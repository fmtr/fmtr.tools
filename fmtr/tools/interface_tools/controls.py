import flet as ft

class SliderSteps(ft.Slider):
    """

    Slider control using step instead of divisions

    """

    def __init__(self, *args, min=10, max=100, step=10, **kwargs):
        self.step = step
        divisions = (max - min) // step
        super().__init__(*args, min=min, max=max, divisions=divisions, **kwargs)
