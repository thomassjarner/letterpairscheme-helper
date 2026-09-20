import flet as ft

from core.pairs import get_active_pairs
from ui.state import AppState


class LetterPairsPage(ft.Column):
    def __init__(self, state: AppState):
        super().__init__(expand=True, spacing=12)
        self.state = state
        self.search_field = ft.TextField(
            hint_text="Search pair or word...",
            width=280,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
        )
        self.status_filter = ft.Dropdown(
            width=160,
            value="all",
            options=[
                ft.dropdown.Option("all", "All"),
                ft.dropdown.Option("active", "Active only"),
                ft.dropdown.Option("inactive", "Inactive only"),
            ],
            on_change=self._on_search_change,
        )
        self.count_text = ft.Text(size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        self.rows_view = ft.ListView(expand=True, spacing=2)
        self._word_fields: list[ft.TextField] = []

        self.controls = [
            ft.Row([self.search_field, self.status_filter, self.count_text]),
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(ft.Text("Pair", weight=ft.FontWeight.BOLD), width=70),
                        ft.Container(ft.Text("Word", weight=ft.FontWeight.BOLD), expand=True),
                        ft.Container(ft.Text("Status", weight=ft.FontWeight.BOLD), width=90),
                        ft.Container(ft.Text("Active in", weight=ft.FontWeight.BOLD), width=220),
                    ]
                ),
                padding=ft.padding.symmetric(horizontal=8),
            ),
            ft.Divider(height=1),
            self.rows_view,
        ]
        self.refresh()

    def refresh(self):
        active_pairs = get_active_pairs(self.state.data.schemes)  # pair -> [labels]
        all_pairs = set(active_pairs) | set(self.state.data.global_words.keys())

        query = (self.search_field.value or "").strip().upper()
        status = self.status_filter.value

        rows = []
        self._word_fields = []
        for pair in sorted(all_pairs):
            is_active = pair in active_pairs
            word = self.state.get_word(pair)

            if status == "active" and not is_active:
                continue
            if status == "inactive" and is_active:
                continue
            if query and query not in pair and query.lower() not in word.lower():
                continue

            rows.append((pair, word, is_active, active_pairs.get(pair, [])))

        self.count_text.value = f"{len(rows)} pair(s)"
        self.rows_view.controls = [
            self._build_row(pair, word, is_active, sources) for pair, word, is_active, sources in rows
        ]

    def _build_row(self, pair: str, word: str, is_active: bool, sources: list[str]) -> ft.Control:
        field = ft.TextField(
            value=word,
            dense=True,
            border=ft.InputBorder.UNDERLINE,
            expand=True,
            on_submit=self._focus_next,
            on_change=lambda e, p=pair: self.state.set_word(p, e.control.value),
        )
        self._word_fields.append(field)

        status_chip = ft.Container(
            content=ft.Text("Active" if is_active else "Inactive", size=12, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_600 if is_active else ft.Colors.GREY_500,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            border_radius=12,
        )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(ft.Text(pair, weight=ft.FontWeight.BOLD), width=70),
                    ft.Container(field, expand=True),
                    ft.Container(status_chip, width=90),
                    ft.Container(
                        ft.Text(", ".join(sources), size=11, color=ft.Colors.ON_SURFACE_VARIANT, no_wrap=False),
                        width=220,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            bgcolor=None if is_active else ft.Colors.SURFACE_CONTAINER_LOWEST,
            opacity=1.0 if is_active else 0.75,
        )

    def _focus_next(self, e):
        try:
            idx = self._word_fields.index(e.control)
        except ValueError:
            return
        if idx + 1 < len(self._word_fields):
            self._word_fields[idx + 1].focus()
            self.update()

    def _on_search_change(self, e):
        self.refresh()
        self.update()
