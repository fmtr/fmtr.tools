from typing import ClassVar

from acp.schema import SessionConfigOptionSelect, SessionConfigSelectOption



DISABLED = "disabled"
APPROVAL = "approval"
FULL = "full"


class Select(SessionConfigOptionSelect):
    """

    ACP session option with a string value selected from named choices.

    """

    @property
    def value(self) -> str:
        """

        Return the currently selected option value.

        """
        return self.current_value

    @property
    def approval(self) -> bool:
        """

        Return whether this option requires tool approval.

        """
        return self.current_value != FULL

    @classmethod
    def from_values(
        cls,
        name: str,
        values: list[str],
        value: str,
        description: str | None,
        category: str,
    ):
        """

        Build an ACP select option from its available values.

        """
        return cls(
            id=name,
            name=name,
            description=description,
            category=category,
            type="select",
            currentValue=value,
            options=[
                SessionConfigSelectOption(value=item, name=item)
                for item in values
            ],
        )


class Policy(Select):
    """

    ACP tool access option supporting disabled, approval, and full access.

    """

    VALUES: ClassVar[list[str]] = [DISABLED, APPROVAL, FULL]

    @classmethod
    def from_value(
        cls,
        name: str,
        value: str = APPROVAL,
        description: str | None = "Tool access policy.",
    ):
        """

        Build the standard tool access policy option.

        """
        return cls.from_values(
            name=name,
            values=cls.VALUES,
            value=value,
            description=description,
            category="tools",
        )
