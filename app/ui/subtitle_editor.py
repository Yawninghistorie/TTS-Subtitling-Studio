"""
Subtitle Editor - Live editing of subtitles
Fixed for Flet 0.84+
"""

import flet as ft
from typing import TYPE_CHECKING, Optional
from datetime import timedelta

if TYPE_CHECKING:
    from app.ui.main_page import MainPage


class SubtitleEditor(ft.Container):
    """Subtitle editor with live editing capabilities."""

    def __init__(self, app: "MainPage"):
        super().__init__()
        self.app = app
        self.selected_index: Optional[int] = None
        self._build()

    def _build(self):
        """Build subtitle editor UI."""
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Start", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("End", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Text", size=12, weight=ft.FontWeight.BOLD, expand=True)),
                ft.DataColumn(ft.Text("Actions", size=12, weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            heading_row_color="#1C1B1F",
            border=ft.border.all(1, "#79747E"),
            expand=True,
        )

        self.toolbar = ft.Row(
            [
                ft.IconButton(icon="add", tooltip="Insert Entry", on_click=self._insert_entry),
                ft.IconButton(icon="delete", tooltip="Delete Selected", on_click=self._delete_selected),
                ft.Container(width=10),
                ft.IconButton(icon="undo", tooltip="Undo", on_click=self._undo),
                ft.IconButton(icon="redo", tooltip="Redo", on_click=self._redo),
                ft.Container(width=10),
                ft.IconButton(icon="search", tooltip="Search", on_click=self._show_search),
                ft.Container(expand=True),
                ft.Text("Entries: 0", size=12, color="#9E9E9E"),
            ],
            spacing=5,
        )

        self.content = ft.Column(
            [
                ft.Container(
                    content=ft.Text("Subtitle Editor", size=16, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.only(bottom=5),
                ),
                ft.Container(
                    content=ft.ListView([self.table], expand=True, height=300),
                    border=ft.border.all(1, "#79747E"),
                    border_radius=8,
                ),
                self.toolbar,
            ],
            spacing=10,
        )

    def update_subtitles(self):
        """Update subtitle table from SubtitleFile."""
        sub_file = self.app.state.subtitle_file
        self.table.rows.clear()

        if not sub_file or not sub_file.entries:
            self.toolbar.controls[-1] = ft.Text("Entries: 0", size=12, color="#9E9E9E")
            self.app.page.update()
            return

        for entry in sub_file.entries:
            dur = entry.duration_seconds
            dur_text = f"{dur:.1f}s"
            text_display = entry.display_text[:60] + "..." if len(entry.display_text) > 60 else entry.display_text

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(entry.index), size=11)),
                    ft.DataCell(ft.Text(self._format_time(entry.start_time), size=11, color="#80DEEA")),
                    ft.DataCell(ft.Text(self._format_time(entry.end_time), size=11, color="#80DEEA")),
                    ft.DataCell(ft.Text(text_display, size=11, max_lines=2)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(icon="play_arrow", icon_size=16, tooltip="Preview"),
                                ft.IconButton(icon="edit", icon_size=16, tooltip="Edit"),
                            ],
                            spacing=2,
                        )
                    ),
                ],
                on_select_changed=lambda e, idx=entry.index: self._select_row(idx),
                selected=False,
            )
            self.table.rows.append(row)

        count = len(sub_file.entries)
        self.toolbar.controls[-1] = ft.Text(f"Entries: {count}", size=12, color="#9E9E9E")
        self.app.page.update()

    @staticmethod
    def _format_time(td: timedelta) -> str:
        """Format timedelta to display string."""
        total_ms = int(td.total_seconds() * 1000)
        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        seconds = (total_ms % 60000) // 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _select_row(self, index: int):
        """Select a row."""
        self.selected_index = index

    def _insert_entry(self, e):
        """Insert new entry."""
        sub_file = self.app.state.subtitle_file
        if not sub_file:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Load SRT file first"), bgcolor="#FF9800"))
            return
        self.app.page.update()

    def _delete_selected(self, e):
        """Delete selected entry."""
        if self.selected_index is None:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Select an entry first"), bgcolor="#FF9800"))
            return
        self.app.page.update()

    def _undo(self, e):
        """Undo last action."""
        pass

    def _redo(self, e):
        """Redo last action."""
        pass

    def _show_search(self, e):
        """Toggle search field."""
        self.app.page.update()