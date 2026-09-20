import flet as ft


class PracticePage(ft.Column):
    def __init__(self):
        super().__init__(expand=True)
        self.controls = [
            ft.Text("Practice", size=20, weight=ft.FontWeight.BOLD),
            ft.Text(
                "Coming soon: random pair quizzes, word\u2194pair quizzes, "
                "timed memo practice, scramble tracing practice, weak-pair "
                "statistics, and MBLD practice.",
                italic=True,
            ),
        ]
