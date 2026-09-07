from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from pydantic import ConfigDict, validate_call
from pydantic_ai import RunContext
from pydantic_ai.toolsets import ApprovalRequiredToolset, FunctionToolset
from pydantic_ai.tools import ToolDefinition

from corio import strings
from corio.ai.agentic import tool
from corio.iterator import IndexList
from corio.strings import get_docstring, join_natural




class Base(FunctionToolset):
    """

    Class-based ACP toolset scaffold.

    """

    DESCRIPTION: str | None = None

    def __init__(self):
        super().__init__()
        for tool in self.tool_instances:
            tool.register()

    @property
    def id(self) -> str:
        """

        Return the toolset identifier used by pydantic-ai.

        """
        return self.name

    @property
    def name(self) -> str:
        """

        Return the concrete toolset class name.

        """
        return type(self).__name__


    @property
    def description(self) -> str | None:
        """

        Toolset description from an override or the class docstring.

        """
        if self.DESCRIPTION is not None:
            return self.DESCRIPTION
        return get_docstring(self.__class__)

    @cached_property
    def TOOLS(self) -> list[type[tool.Base]]:
        """

        Tool classes registered on this toolset.

        """
        return []

    @cached_property
    def tool_instances(self) -> IndexList[tool.Base]:
        """

        Instantiated tool objects for this toolset.

        """
        return IndexList[tool.Base](tool_cls(self) for tool_cls in self.TOOLS)

    async def get_instructions(self, ctx: RunContext[Any]) -> list[str]:
        """

        Tool instructions derived from the registered toolset.

        """
        names = self.tool_instances.name.keys()
        names = join_natural(names, mask='`{}`')
        return [
            strings.trim(
                f"""
                ## {self.description}

                You have access to {self.description} like {names}.
                """
            )
        ]

    # ACP-related:

    if TYPE_CHECKING:
        from corio.ai.agentic.acp import options


    def approve(
            self,
            ctx: RunContext[Any],
            tool_def: ToolDefinition,
            tool_args: dict[str, Any],
    ) -> bool:
        """

        Decide whether a tool call requires user approval.

        """

        if not self.option.approval:
            return False

        tool = self.tool_instances.name[tool_def.name]
        if isinstance(tool.approve, bool):
            return tool.approve
        tool_approve = validate_call(
            tool.approve,
            config=ConfigDict(arbitrary_types_allowed=True),
        )
        return bool(tool_approve(ctx, **tool_args))

    @cached_property
    def wrapper(self) -> ApprovalRequiredToolset:
        """

        Return the approval-enforcing view of this toolset.

        """
        return ApprovalRequiredToolset(self, self.approve)

    @cached_property
    def option(self) -> options.Policy:
        """

        Return the default full-access policy for this toolset.

        """
        from corio.ai.agentic.acp import options
        return options.Policy.from_value(
            name=self.name,
            value=options.FULL,
            description=self.description,
        )
