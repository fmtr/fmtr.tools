import pydantic_ai
from pydantic_ai import RunContext
from pydantic_ai.agent import AgentRunResult, Agent
from pydantic_ai.messages import ModelRequest, RetryPromptPart
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from fmtr.tools import environment_tools as env
from fmtr.tools.config import ToolsConfig

pydantic_ai.Agent.instrument_all()

class Task:
    """

    Linear task definition, as Agent configuration and typing, plus state history.

    """

    PROVIDER = OpenAIProvider(api_key=env.get(ToolsConfig.FMTR_OPENAI_API_KEY_KEY))

    API_HOST_FMTR = env.get(ToolsConfig.FMTR_AI_HOST_KEY, ToolsConfig.FMTR_AI_HOST_DEFAULT)
    API_URL_FMTR = f'https://{API_HOST_FMTR}/v1'
    PROVIDER_FMTR = OpenAIProvider(base_url=API_URL_FMTR)

    MODEL_ID = 'gpt-4o'
    SYSTEM_PROMPT = None
    DEPS_TYPE = str
    RESULT_TYPE = str
    RESULT_RETRIES = 5

    def __init__(self, *args, **kwargs):
        """

        Configure Agent

        """

        self.model = OpenAIModel(self.MODEL_ID, provider=self.PROVIDER)
        self.agent = Agent(
            *args,
            model=self.model,
            system_prompt=self.SYSTEM_PROMPT or [],
            deps_type=self.DEPS_TYPE,
            result_type=self.RESULT_TYPE,
            result_retries=self.RESULT_RETRIES,
            **kwargs
        )

        self.agent.output_validator(self.validate)
        self.history = []

    async def run(self, *args, **kwargs) -> AgentRunResult[RESULT_TYPE]:
        """

        Run Agent storing history

        """

        result = await self.agent.run(*args, message_history=self.history, **kwargs)
        self.history = result.all_messages()
        return result

    async def revert(self, msg, deps):
        """

        Post-hoc, user-initiated tool retry.

        """
        msg_final = self.history.pop(-1)
        tool_return_part = msg_final.parts[0]

        retry_prompt = RetryPromptPart(content=msg, tool_name=tool_return_part.tool_name, tool_call_id=tool_return_part.tool_call_id, timestamp=tool_return_part.timestamp, part_kind='retry-prompt')
        retry_request = ModelRequest(parts=[retry_prompt], instructions=msg_final.instructions, kind='request')

        self.history.append(retry_request)

        result = await Task.run(self, deps=deps)
        return result

    async def validate(self, ctx: RunContext[DEPS_TYPE], output: RESULT_TYPE) -> RESULT_TYPE:
        """

        Dummy validator

        """
        return output


class TaskTest(Task):
    PROVIDER = Task.PROVIDER_FMTR
    MODEL_ID = 'mixtral:8x7b'


if __name__ == '__main__':
    import asyncio

    task = TaskTest()
    result = asyncio.run(task.run('Hello! What is your name?'))
    result
