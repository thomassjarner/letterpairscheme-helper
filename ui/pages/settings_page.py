import shutil
from pathlib import Path

import flet as ft

from data.paths import get_data_file


class SettingsPage(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=12)
        self.page = page
        self.status_text = ft.Text("")
        data_file = get_data_file()
        self.controls = [
            ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Your data is stored outside the app folder, so app updates never touch it:"),
            ft.Container(
                content=ft.Text(str(data_file), selectable=True, font_family="monospace"),
                padding=10,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                border_radius=6,
            ),
            ft.Row(
                [
                    ft.ElevatedButton("Export backup...", icon=ft.Icons.DOWNLOAD, on_click=self._export_backup),
                ]
            ),
            self.status_text,
        ]

    def _export_backup(self, e):
        data_file = get_data_file()
        if not data_file.exists():
            self.status_text.value = "No data file yet — create a scheme first."
            self.update()
            return
        backup_path = data_file.with_name("data.backup.json")
        shutil.copy2(data_file, backup_path)
        self.status_text.value = f"Backup written to {backup_path}"
        self.update()
