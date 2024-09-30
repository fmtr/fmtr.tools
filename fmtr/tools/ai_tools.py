import torch
from datetime import datetime
from peft import PeftConfig, PeftModel
from statistics import mean, stdev
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List

from fmtr.tools import logger
from fmtr.tools.hfh_tools import get_hf_cache_path

CPU = 'cpu'
GPU = 'cuda'


class DynamicBatcher:
    """

    Helper to simplify dynamic batching.

    """

    def __init__(self, prompts, threshold_stable_reset=None, factor_reduction=None):

        self.prompts = prompts
        self.size_total = len(self)
        self.threshold_stable_reset = threshold_stable_reset or 50
        self.factor_reduction = factor_reduction or 0.9
        self.size = self.count_stable = None
        self.started = datetime.now()

        self.reset()

    def reset(self):
        """

        Reset inferred, stable batch size. Useful if outlier outputs force the batch size below what's optimal

        """
        self.size = len(self)
        self.count_stable = 0

    def batch_complete(self):
        """

        When a batch completes, remove it. If the number of stable batches reaches the threshold, trigger reset.

        """

        self.prompts = self.prompts[self.size:]

        self.count_stable += 1

        percent = 100 - ((len(self) / self.size_total) * 100)

        msg = (
            f"Marking batch (size {self.size}) complete. {len(self)} of {self.size_total} prompts remaining. "
        )
        logger.info(msg)
        msg = (
            f"Stable for {self.count_stable} batch(es) (threshold: {self.threshold_stable_reset}). "
            f"{percent:.2f}% complete. "
            f"Elapsed: {datetime.now() - self.started}. "
            f"Estimated: {self.calculate_eta()}."
        )
        logger.info(msg)

        if self.count_stable >= self.threshold_stable_reset:
            msg = (f"Stable count reached threshold of {self.threshold_stable_reset}. Resetting batch size.")
            logger.info(msg)
            self.reset()

    def __len__(self):
        """

        Length is number of remaining prompts

        """
        return len(self.prompts)

    def get(self):
        """

        Fetch a batch of current size

        """
        logger.info(f"Processing batch of {self.size} prompts...")
        return self.prompts[:self.size]

    def reduce(self):
        """

        If OOM occurs, reduce batch size by specified factor, or by at least 1.

        """

        self.count_stable = 0

        size_new = round(self.size * self.factor_reduction)

        if size_new == self.size:
            self.size -= 1
            logger.info(f"Batch size reduced to {self.size} prompts")
        else:
            self.size = size_new
            logger.info(f"Batch size reduced by factor {self.factor_reduction} to {self.size} prompts")

        if self.size == 0:
            if len(self) < self.size_total:
                msg = f"Batch size 1 caused OOM, despite previous batches succeeding. Will retry. Try freeing resources."
                logger.warning(msg)
                self.size = 1
            else:
                raise ValueError('Size of first batch reached 0. Prompt(s) are likely extremely long.')

    def calculate_eta(self):
        """

        Calculate bulk-job ETA.

        """
        time_spent = datetime.now() - self.started

        completed = self.size_total - len(self)
        if completed <= 0:
            return "Unknown"

        average_time_per_task = time_spent / completed
        remaining_time = average_time_per_task * len(self)
        eta = datetime.now() + remaining_time

        return eta


class BulkInferenceManager:
    """

    Perform bulk LLM inference using the specified configuration and dynamic batching.

    """

    LOCAL_ONLY = False
    PRECISION_FLOAT = torch.float16

    REPO_ID = 'mistralai/Mistral-7B-Instruct-v0.3'
    REPO_ID_ADAPTER = None
    REPO_TAG_ADAPTER = 'main'

    DEVICE_ACTIVE = GPU
    DEVICE_INACTIVE = CPU

    BATCH_STABLE_RESET = None
    BATCH_FACTOR_REDUCTION = None

    def __init__(self):
        """

        Load a base model plus optional adapter in the specified precision, then deactivate until first use.

        """

        args = dict(local_files_only=self.LOCAL_ONLY, torch_dtype=self.PRECISION_FLOAT)

        logger.info(f"Loading base model from {self.REPO_ID}")
        base_model = AutoModelForCausalLM.from_pretrained(self.REPO_ID, **args)
        self.tokenizer = AutoTokenizer.from_pretrained(self.REPO_ID, **args)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        if self.REPO_ID_ADAPTER:
            logger.info(f"Loading adapter model from {self.REPO_ID_ADAPTER} [{self.REPO_TAG_ADAPTER}]")
            if self.LOCAL_ONLY:
                path_adapter = get_hf_cache_path(self.REPO_ID_ADAPTER, tag=self.REPO_TAG_ADAPTER)
            else:
                path_adapter = self.REPO_ID_ADAPTER
            self.adapter_config = PeftConfig.from_pretrained(path_adapter, revision=self.REPO_TAG_ADAPTER, **args)
            self.model = PeftModel.from_pretrained(base_model, path_adapter, revision=self.REPO_TAG_ADAPTER, **args)
            self.model_adapter = self.model
        else:
            self.model = base_model
            self.adapter_config = self.model_adapter = None

        self.deactivate()

    def activate(self):
        """

        Move the model to the specified active device.

        """
        if self.model.device != self.DEVICE_ACTIVE:
            logger.info(f'Activating model {self.REPO_ID_ADAPTER or self.REPO_ID} to device {self.DEVICE_ACTIVE}')
            self.model = self.model.to(self.DEVICE_ACTIVE)

    def deactivate(self):
        """

        Move the model to the specified active inactive.

        """
        if self.model.device != self.DEVICE_INACTIVE:
            logger.info(f'Deactivating model {self.REPO_ID_ADAPTER or self.REPO_ID} to device {self.DEVICE_INACTIVE}')
            self.model = self.model.to(self.DEVICE_INACTIVE)

    def encode(self, prompts: List[str]):
        """

        Encode/tokenize a list of text prompts to a batch of tokens, including appropriate templates, etc.

        """

        messages = [[{"role": "user", "content": prompt}] for prompt in prompts]

        ids_input = self.tokenizer.apply_chat_template(
            messages,
            return_tensors="pt",
            padding=True,
            return_attention_mask=True,
            return_dict=True
        )

        return ids_input

    def generate(self, prompts, **params):
        """

        Generate outputs for all batches, using dynamic batching, backoff in case off OOM errors, etc.

        """
        logger.info(f'Starting generation...')
        logger.debug(f'Generation parameters: {params}')

        batcher = DynamicBatcher(
            prompts,
            factor_reduction=self.BATCH_FACTOR_REDUCTION,
            threshold_stable_reset=self.BATCH_STABLE_RESET
        )

        self.activate()

        while len(batcher):
            try:

                prompts = batcher.get()

                batch_encoding = self.encode(prompts).to(self.model.device)

                ids_output = self.model.generate(
                    pad_token_id=self.tokenizer.eos_token_id,
                    **batch_encoding,
                    **params
                )
                ids_output = ids_output.to(self.DEVICE_INACTIVE)

                batcher.batch_complete()
                yield prompts, ids_output

            except RuntimeError as exception:
                if "CUDA out of memory" in str(exception):
                    logger.warning(f"Ran out of memory. Reducing batch size: {repr(exception)}")
                    batcher.reduce()
                else:
                    raise

        self.deactivate()

    def decode(self, prompts, ids_output):
        """

        Decode outputs to text

        """
        texts_prompts = self.tokenizer.batch_decode(ids_output, skip_special_tokens=True)
        texts = [text_prompt.removeprefix(prompt).strip() for prompt, text_prompt in zip(prompts, texts_prompts)]
        return texts

    def get_outputs(self, prompts: List[str], **params):
        """

        Generate a batch of outputs from a batch of prompts

        """

        params = params or dict(do_sample=False)

        for prompts_batch, ids_output in self.generate(prompts, **params):
            texts = self.decode(prompts_batch, ids_output)

            lengths = [len(text) // 5 for text in texts]
            msg = f'Text statistics: {min(lengths)=} {max(lengths)=} {mean(lengths)=} {stdev(lengths)=}.'
            logger.info(msg)

            yield from texts

    def get_output(self, prompt, **params):
        """

        Get a singleton output

        """
        outputs = self.get_outputs([prompt], **params)
        output = next(iter(outputs))
        return output


def tst():
    """

    Test with a large number of small input/outputs.

    """
    mask = 'Write out the following number as words: {}. Just the text please, no explanation or alternatives'
    prompts = [mask.format(i) for i in range(10_000)]
    manager = BulkInferenceManager()
    texts = manager.get_outputs(prompts, max_new_tokens=20, do_sample=True, temperature=1.2, top_p=0.5, top_k=50)

    data = {}
    for prompt, text in zip(prompts, texts):
        data[prompt] = text
    return data


if __name__ == '__main__':
    texts = tst()
    texts
