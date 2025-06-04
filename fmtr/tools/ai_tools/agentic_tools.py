import pydantic_ai
from pydantic_ai import RunContext, ModelRetry
from pydantic_ai.agent import AgentRunResult, Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import List, Optional, Any

from fmtr.tools import environment_tools as env
from fmtr.tools.constants import Constants
from fmtr.tools.logging_tools import logger
from fmtr.tools.string_tools import truncate_mid

pydantic_ai.Agent.instrument_all()


class Validator:
    """

    Subclassable validator

    """

    async def validate(self, ctx: RunContext[Any], output: Any) -> List[str]:
        raise NotImplementedError()




class Task:
    """

    Linear task definition, as Agent configuration and typing, plus state history.

    """

    PROVIDER = OpenAIProvider(api_key=env.get(Constants.FMTR_OPENAI_API_KEY_KEY))

    API_HOST_FMTR = env.get(Constants.FMTR_AI_HOST_KEY, Constants.FMTR_AI_HOST_DEFAULT)
    API_URL_FMTR = f'https://{API_HOST_FMTR}/v1'
    PROVIDER_FMTR = OpenAIProvider(base_url=API_URL_FMTR)

    MODEL_ID = 'gpt-4o'
    MODEL_ID_FMTR = 'qwen2.5-coder:14b'
    SYSTEM_PROMPT_STATIC = None
    DEPS_TYPE = str
    RESULT_TYPE = str
    RESULT_RETRIES = 5
    VALIDATORS: List[Validator] = []

    def __init__(self, *args, **kwargs):
        """

        Configure Agent

        """

        self.model = OpenAIModel(self.MODEL_ID, provider=self.PROVIDER)
        self.agent = Agent(
            *args,
            model=self.model,
            system_prompt=self.SYSTEM_PROMPT_STATIC or [],
            deps_type=self.DEPS_TYPE,
            result_type=self.RESULT_TYPE,
            result_retries=self.RESULT_RETRIES,
            **kwargs
        )

        self.agent.output_validator(self.validate)
        self.agent.system_prompt(self.add_system_prompt)
        self.history = []

    @property
    def sync_runner(self):
        """

        Convenience/debug function to run without async.

        """
        import asyncio
        return asyncio.run

    async def run(self, *args, deps=None, **kwargs) -> AgentRunResult[RESULT_TYPE]:
        """

        Run Agent with deps-relative user prompt and while storing history

        """
        result = await self.agent.run(*args, user_prompt=self.get_prompt(deps), deps=deps, message_history=self.history, **kwargs)
        self.history = result.all_messages()
        return result

    async def validate(self, ctx: RunContext[DEPS_TYPE], output: RESULT_TYPE) -> RESULT_TYPE:
        """

        Aggregate any validation failures and combine them into a single ModelRetry exception

        """
        msgs = []
        for validator in self.VALIDATORS:
            msgs += validator.validate(ctx, output)

        if msgs:
            msg = '. '.join(msgs)
            logger.warning(msg)
            raise ModelRetry(msg)

        return output

    def get_prompt(self, deps: Optional[DEPS_TYPE]) -> Optional[str]:
        """

        Dummy prompt generator

        """
        return None

    def add_system_prompt(self, ctx: RunContext[DEPS_TYPE]) -> str | List[str]:
        """

        Dummy system prompt append

        """

        return []

    def __repr__(self):
        """

        String representation of the object

        """
        return f'{self.__class__.__name__}({repr(truncate_mid(self.SYSTEM_PROMPT_STATIC, 100))})'

if __name__ == '__main__':
    import asyncio
    from fmtr.tools import dm


    class TestOutput(dm.Base):
        text: str


    class TestDeps(dm.Base):
        lang: str
        subject: str


    class TaskTest(Task):
        # PROVIDER = Task.PROVIDER_FMTR
        # MODEL_ID = 'qwen2.5-coder:14b'
        RESULT_TYPE = TestOutput
        SYSTEM_PROMPT_STATIC = 'Tell the user jokes.'

        def add_system_prompt(self, ctx: RunContext[TestDeps]) -> str:
            return f'The jokes must be in the {ctx.deps.lang} language.'

        def get_prompt(self, deps: Optional[TestDeps]) -> str:
            return f'Tell me one about {deps.subject}.'

    task = TaskTest()
    deps = TestDeps(lang='English', subject='eggs')
    result1 = task.sync_runner(task.run(deps=deps))
    result1

    deps = TestDeps(lang='German', subject='sausages')
    result2 = task.sync_runner(task.run(deps=deps))
    result2
