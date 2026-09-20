import flet as ft

from core.cube_definitions import CATEGORY_PIECES


def build_buffer_picker(category: str, current_buffer: str | None, on_change) -> ft.Control:
    """
    on_change(new_piece_name: str) -> None
    """
    piece_names = sorted(CATEGORY_PIECES[category].keys())
    return ft.Dropdown(
        label=f"{category.capitalize()} buffer",
        width=180,
        value=current_buffer,
        options=[ft.dropdown.Option(p) for p in piece_names],
        on_change=lambda e: on_change(e.control.value),
    )
