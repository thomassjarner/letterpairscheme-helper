import flet as ft

from ui.components.buffer_picker import build_buffer_picker
from ui.components.sticker_grid import build_sticker_grid
from ui.state import AppState


class LetterSchemesPage(ft.Column):
    def __init__(self, state: AppState):
        super().__init__(expand=True, spacing=0)
        self.state = state
        self.selected_category = "corners"
        self.new_scheme_field = ft.TextField(hint_text="New scheme name", width=200, on_submit=self._create_scheme)
        self.rename_field = ft.TextField(hint_text="Rename active scheme", width=200, on_submit=self._rename_scheme)
        self.scheme_list_view = ft.ListView(expand=True, spacing=2)
        self.body_area = ft.Container(expand=True, padding=16)
        self.controls = [self._build_layout()]
        self.refresh()

    # ---- layout -------------------------------------------------------------

    def _build_layout(self) -> ft.Control:
        sidebar = ft.Container(
            width=260,
            padding=12,
            border=ft.border.only(right=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
            content=ft.Column(
                [
                    ft.Text("Schemes", weight=ft.FontWeight.BOLD, size=16),
                    ft.Row([self.new_scheme_field, ft.IconButton(ft.Icons.ADD, on_click=self._create_scheme, tooltip="Create scheme")]),
                    ft.Divider(),
                    self.scheme_list_view,
                ],
                expand=True,
            ),
        )
        return ft.Row([sidebar, self.body_area], expand=True)

    # ---- refresh --------------------------------------------------------

    def refresh(self):
        self._refresh_scheme_list()
        self._refresh_body()
        self.update()

    def _refresh_scheme_list(self):
        active = self.state.active_scheme
        self.scheme_list_view.controls = []
        for name in self.state.scheme_names:
            is_active = active is not None and active.name == name
            self.scheme_list_view.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                name,
                                weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                                expand=True,
                            ),
                            ft.IconButton(ft.Icons.CONTENT_COPY, icon_size=16, tooltip="Duplicate",
                                          on_click=lambda e, n=name: self._duplicate_scheme(n)),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=16, tooltip="Delete",
                                          on_click=lambda e, n=name: self._delete_scheme(n)),
                        ],
                        spacing=0,
                    ),
                    padding=8,
                    border_radius=6,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER if is_active else None,
                    on_click=lambda e, n=name: self._switch_scheme(n),
                )
            )

    def _refresh_body(self):
        scheme = self.state.active_scheme
        if scheme is None:
            self.body_area.content = ft.Text("Create a scheme to get started.", italic=True)
            return

        cat = scheme.corners if self.selected_category == "corners" else scheme.edges

        tabs = ft.Tabs(
            selected_index=0 if self.selected_category == "corners" else 1,
            on_change=self._on_tab_change,
            tabs=[ft.Tab(text="Corners"), ft.Tab(text="Edges")],
        )

        buffer_picker = build_buffer_picker(
            self.selected_category, cat.buffer_piece,
            lambda piece: self._set_buffer(piece),
        )

        grid = build_sticker_grid(
            self.selected_category, cat,
            lambda sticker, value: self._set_letter(sticker, value),
        )

        self.body_area.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(scheme.name, size=20, weight=ft.FontWeight.BOLD),
                        self.rename_field,
                        ft.IconButton(ft.Icons.CHECK, tooltip="Rename", on_click=self._rename_scheme),
                    ]
                ),
                tabs,
                ft.Row([buffer_picker]),
                ft.Container(content=grid, padding=ft.padding.only(top=12)),
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ---- event handlers ---------------------------------------------------

    def _create_scheme(self, e):
        name = self.new_scheme_field.value.strip()
        if not name:
            return
        self.state.create_scheme(name)
        self.new_scheme_field.value = ""
        self.refresh()

    def _rename_scheme(self, e):
        scheme = self.state.active_scheme
        new_name = self.rename_field.value.strip()
        if scheme is None or not new_name:
            return
        self.state.rename_scheme(scheme.name, new_name)
        self.rename_field.value = ""
        self.refresh()

    def _duplicate_scheme(self, name: str):
        self.state.duplicate_scheme(name)
        self.refresh()

    def _delete_scheme(self, name: str):
        self.state.delete_scheme(name)
        self.refresh()

    def _switch_scheme(self, name: str):
        self.state.switch_scheme(name)
        self.refresh()

    def _on_tab_change(self, e):
        self.selected_category = "corners" if e.control.selected_index == 0 else "edges"
        self._refresh_body()
        self.update()

    def _set_buffer(self, piece_name: str):
        scheme = self.state.active_scheme
        if scheme is None:
            return
        self.state.set_buffer(scheme, self.selected_category, piece_name)
        self._refresh_body()
        self.update()

    def _set_letter(self, sticker: str, value: str):
        scheme = self.state.active_scheme
        if scheme is None:
            return
        # Deliberately does NOT rebuild the grid here: rebuilding on every
        # keystroke would steal focus from the field the user is typing
        # in, which fights the "fast data entry" requirement. The letter
        # is saved immediately; duplicate-letter warnings and borders are
        # recomputed next time the grid rebuilds (tab switch, scheme
        # switch, or reopening the page).
        self.state.set_sticker_letter(scheme, self.selected_category, sticker, value)
