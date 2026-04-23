"""
Subtitle Editor - Live editing of subtitles
"""

import flet as ft
from typing import TYPE_CHECKING, List, Dict, Optional
from datetime import timedelta

if TYPE_CHECKING:
    from app.ui.main_page import MainPage


class SubtitleEditor(ft.Container):
    """Subtitle editor with live editing capabilities."""

    def __init__(self, app: "MainPage"):
        super().__init__()
        self.app = app
        self.selected_index: Optional[int] = None
        self.editing_cell: Optional[str] = None
        self._build()

    def _build(self):
        """Build subtitle editor UI."""
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Start", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("End", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Text", size=12, weight=ft.FontWeight.BOLD, expand=True)),
                ft.DataColumn(ft.Text("Duration", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", size=12, weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            heading_row_color=ft.colors.SURFACE_CONTAINER_HIGH,
            border=ft.border.all(1, ft.colors.OUTLINE),
            expand=True,
        )

        self.toolbar = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.ADD,
                    tooltip="Insert Entry (Ctrl+N)",
                    on_click=self._insert_entry,
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE,
                    tooltip="Delete Selected",
                    on_click=self._delete_selected,
                ),
                ft.Container(width=10),
                ft.IconButton(
                    icon=ft.icons.UNDO,
                    tooltip="Undo (Ctrl+Z)",
                    on_click=self._undo,
                ),
                ft.IconButton(
                    icon=ft.icons.REDO,
                    tooltip="Redo (Ctrl+Y)",
                    on_click=self._redo,
                ),
                ft.Container(width=10),
                ft.IconButton(
                    icon=ft.icons.SEARCH,
                    tooltip="Search (Ctrl+F)",
                    on_click=self._show_search,
                ),
                ft.Container(expand=True),
                ft.Text("Entries: 0", size=12, color=ft.colors.GREY_400),
            ],
            spacing=5,
        )

        self.search_field = ft.TextField(
            hint_text="Search text...",
            prefix_icon=ft.icons.SEARCH,
            visible=False,
            on_submit=self._on_search,
            expand=True,
        )

        self.content = ft.Column(
            [
                ft.Container(
                    content=ft.Text("Subtitle Editor", size=16, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.only(bottom=5),
                ),
                ft.Container(content=self.search_field, visible=False),
                ft.Container(
                    content=ft.ListView(
                        [self.table],
                        expand=True,
                        height=300,
                    ),
                    border=ft.border.all(1, ft.colors.OUTLINE),
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
            self.toolbar.controls[-1] = ft.Text("Entries: 0", size=12, color=ft.colors.GREY_400)
            self.app.page.update()
            return

        for entry in sub_file.entries:
            # Format duration
            dur = entry.duration_seconds
            dur_text = f"{dur:.1f}s"

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(entry.index), size=11)),
                    ft.DataCell(
                        ft.Text(
                            self._format_time(entry.start_time),
                            size=11,
                            color=ft.colors.CYAN_200,
                        )
                    ),
                    ft.DataCell(
                        ft.Text(
                            self._format_time(entry.end_time),
                            size=11,
                            color=ft.colors.CYAN_200,
                        )
                    ),
                    ft.DataCell(
                        ft.Text(
                            entry.display_text[:80] + "..." if len(entry.display_text) > 80 else entry.display_text,
                            size=11,
                            max_lines=2,
                        )
                    ),
                    ft.DataCell(ft.Text(dur_text, size=11, color=ft.colors.YELLOW_200)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.PLAY_ARROW,
                                    icon_size=16,
                                    tooltip="Preview",
                                    on_click=lambda e, idx=entry.index: self._preview_entry(idx),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    icon_size=16,
                                    tooltip="Edit",
                                    on_click=lambda e, idx=entry.index: self._edit_entry(idx),
                                ),
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
        self.toolbar.controls[-1] = ft.Text(f"Entries: {count}", size=12, color=ft.colors.GREY_400)
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

    def _preview_entry(self, index: int):
        """Preview single entry."""
        self.app.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(f"Previewing entry #{index}"))
        )
        self.app.page.update()

    def _edit_entry(self, index: int):
        """Edit single entry."""
        sub_file = self.app.state.subtitle_file
        if not sub_file:
            return

        entry = next((e for e in sub_file.entries if e.index == index), None)
        if not entry:
            return

        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Entry #{index}"),
            content=ft.Column(
                [
                    ft.TextField(
                        label="Start Time",
                        value=self._format_time(entry.start_time),
                        on_change=lambda e: self._parse_time_change(entry, "start", e.control.value),
                    ),
                    ft.TextField(
                        label="End Time",
                        value=self._format_time(entry.end_time),
                        on_change=lambda e: self._parse_time_change(entry, "end", e.control.value),
                    ),
                    ft.TextField(
                        label="Text",
                        value=entry.text,
                        multiline=True,
                        min_lines=2,
                        on_change=lambda e: self._update_entry_text(entry, e.control.value),
                    ),
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog()),
                ft.TextButton("Save", on_click=lambda e: self._save_entry(entry)),
            ],
        )
        self.app.page.dialog = dialog
        dialog.open = True
        self.app.page.update()

    def _parse_time_change(self, entry, field, value):
        """Parse time change."""
        try:
            parts = value.split(":")
            if len(parts) == 3:
                h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
                td = timedelta(hours=h, minutes=m, seconds=s)
                if field == "start":
                    entry.start_time = td
                else:
                    entry.end_time = td
        except:
            pass

    def _update_entry_text(self, entry, text):
        """Update entry text."""
        entry.text = text

    def _save_entry(self, entry):
        """Save entry changes."""
        self._close_dialog()
        self.update_subtitles()

    def _close_dialog(self):
        """Close dialog."""
        self.app.page.dialog.open = False
        self.app.page.update()

    def _insert_entry(self, e):
        """Insert new entry."""
        sub_file = self.app.state.subtitle_file
        if not sub_file:
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Load SRT file first"), bgcolor=ft.colors.WARNING)
            )
            return

        from app.models.subtitle import SubtitleEntry

        # Insert after selected or at end
        new_index = len(sub_file.entries) + 1
        last_entry = sub_file.entries[-1] if sub_file.entries else None
        start = last_entry.end_time if last_entry else timedelta(0)
        end = start + timedelta(seconds=3)

        new_entry = SubtitleEntry(
            index=new_index,
            start_time=start,
            end_time=end,
            text="New subtitle text",
        )
        sub_file.entries.append(new_entry)

        # Re-index
        for i, entry in enumerate(sub_file.entries):
            entry.index = i + 1

        self.update_subtitles()

    def _delete_selected(self, e):
        """Delete selected entry."""
        if self.selected_index is None:
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Select an entry first"), bgcolor=ft.colors.WARNING)
            )
            return

        sub_file = self.app.state.subtitle_file
        if not sub_file:
            return

        sub_file.entries = [e for e in sub_file.entries if e.index != self.selected_index]

        # Re-index
        for i, entry in enumerate(sub_file.entries):
            entry.index = i + 1

        self.selected_index = None
        self.update_subtitles()

    def _undo(self, e):
        """Undo last action."""
        pass

    def _redo(self, e):
        """Redo last action."""
        pass

    def _show_search(self, e):
        """Toggle search field."""
        self.search_field.visible = not self.search_field.visible
        self.app.page.update()

    def _on_search(self, e):
        """Handle search."""
        query = e.control.value.lower()
        # TODO: Implement search highlighting
        self.app.page.update()