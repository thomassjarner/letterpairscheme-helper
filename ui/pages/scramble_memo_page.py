import flet as ft


class ScrambleMemoPage(ft.Column):
    def __init__(self):
        super().__init__(expand=True)
        self.controls = [
            ft.Text("Scramble Memo", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Coming soon. This needs a conventions discussion first "
                "(orientation, cycle breaks, parity, memo grouping) before "
                "it's implemented — see core/tracer.py.",
                italic=True,
            ),
        ]
