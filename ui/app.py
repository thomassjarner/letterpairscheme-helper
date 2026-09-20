import flet as ft

from data.json_repository import JsonAppDataRepository
from ui.pages.letter_pairs_page import LetterPairsPage
from ui.pages.letter_schemes_page import LetterSchemesPage
from ui.pages.practice_page import PracticePage
from ui.pages.scramble_memo_page import ScrambleMemoPage
from ui.pages.settings_page import SettingsPage
from ui.state import AppState

DESTINATIONS = [
    ("Letter Schemes", ft.Icons.GRID_VIEW),
    ("Letter Pairs", ft.Icons.TABLE_CHART),
    ("Scramble Memo", ft.Icons.SHUFFLE),
    ("Practice", ft.Icons.FITNESS_CENTER),
    ("Settings", ft.Icons.SETTINGS),
]


def main(page: ft.Page):
    page.title = "BLD Letter Memo"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0

    repository = JsonAppDataRepository()
    state = AppState(repository)

    schemes_page = LetterSchemesPage(state)
    pairs_page = LetterPairsPage(state)
    scramble_page = ScrambleMemoPage()
    practice_page = PracticePage()
    settings_page = SettingsPage(page)

    pages = [schemes_page, pairs_page, scramble_page, practice_page, settings_page]
    content_area = ft.Container(content=pages[0], expand=True, padding=16)

    def on_nav_change(e):
        index = e.control.selected_index
        content_area.content = pages[index]
        if pages[index] is pairs_page:
            pairs_page.refresh()
        if pages[index] is schemes_page:
            schemes_page.refresh()
        page.update()

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=180,
        destinations=[
            ft.NavigationRailDestination(icon=icon, label=label) for label, icon in DESTINATIONS
        ],
        on_change=on_nav_change,
    )

    # Letter Schemes changes (buffer/letters) affect which pairs are
    # active, so refresh the Letter Pairs page whenever underlying data
    # changes and it happens to be visible.
    state.on_change(lambda: pairs_page.refresh() if content_area.content is pairs_page else None)

    page.add(
        ft.Row(
            [nav_rail, ft.VerticalDivider(width=1), content_area],
            expand=True,
        )
    )


def run():
    ft.app(target=main)


if __name__ == "__main__":
    run()
