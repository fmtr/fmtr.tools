from typing import Optional

import flet as ft
from flet.core.gesture_detector import TapEvent

from fmtr.tools.logging_tools import logger


class SliderSteps(ft.Slider):
    """

    Slider control using step instead of divisions

    """

    def __init__(self, *args, min=10, max=100, step=10, **kwargs):
        self.step = step
        divisions = (max - min) // step
        super().__init__(*args, min=min, max=max, divisions=divisions, **kwargs)


class Cell(ft.DataCell):
    """

    Context-aware, clickable data cell.

    """

    def __init__(self, series, column):
        """

        Store context

        """
        self.series = series
        self.column = column
        self.value = series[column]

        super().__init__(self.gesture_detector)

    @property
    def text(self):
        """

        Cell contents text

        """

        return ft.Text(str(self.value), color=self.color)

    @property
    def color(self):
        """

        Basic conditional formatting

        """
        if self.value is None:
            return ft.Colors.GREY
        else:
            return None

    @property
    def gesture_detector(self):
        """

        Make arbitrary content clickable

        """
        return ft.GestureDetector(content=self.text, on_tap=self.click_tap)

    async def click_tap(self, event: TapEvent):
        """

        Default cell click behavior — override in subclass if needed

        """
        value = await self.click(event=event)
        event.page.update()
        return value

    async def click(self, event: Optional[TapEvent] = None):
        """

        Default cell click behavior — override in subclass if needed

        """
        logger.info(f"Clicked {self.column=} {self.series.id=} {self.value=}")


class Row(ft.DataRow):
    """

    Instantiate a row from a series

    """

    TypeCell = Cell

    def __init__(self, series):
        self.series = series
        cells = [self.TypeCell(series, col) for col in series.index]
        super().__init__(cells)


class Column(ft.DataColumn):
    """

    Column stub

    """

    def __init__(self, col_name: str):
        """

        Store context

        """

        self.col_name = col_name

        super().__init__(label=self.text)

    @property
    def text(self):
        """

        Cell contents text

        """
        return ft.Text(str(self.col_name), weight=self.weight)

    @property
    def weight(self):
        """

        Default bold headers

        """
        return ft.FontWeight.BOLD


class Table(ft.DataTable):
    """

    Dataframe with clickable cells

    """

    TypeRow = Row
    TypeColumn = Column

    def __init__(self, df):  # todo move to submodule with tabular deps
        """

        Set columns/rows using relevant types

        """
        self.df = df
        columns = [self.TypeColumn(col) for col in df.columns]
        rows = [self.TypeRow(row) for _, row in df.iterrows()]
        super().__init__(columns=columns, rows=rows)
