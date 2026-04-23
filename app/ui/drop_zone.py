"""
Drop Zone - Drag & drop file handling
Fixed for Flet 0.84+
"""

import flet as ft
from typing import TYPE_CHECKING
from pathlib import Path
import os

if TYPE_CHECKING:
    from app.ui.main_page import MainPage


class DropZone(ft.Column):
    """Drop zone for files."""

    def __init__(self, app: "MainPage"):
        super().__init__()
        self.app = app
        self._build()

    def _build(self):
        """Build drop zone UI."""
        self.drop_target = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(name="upload_file", size=48, color="#B39DDB"),
                    ft.Text("Drop SRT files here", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("or .onnx model files", size=12, color="#9E9E9E"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=350,
            height=180,
            border=ft.border.all(2, "#673AB7"),
            border_radius=ft.border_radius.all(12),
            bgcolor="#312B36",
            on_click=self._on_drop_click,
        )

        self.srt_files_list = ft.ListView(
            expand=True,
            height=100,
            spacing=5,
        )

        self.model_path = ft.TextField(
            label="Model Path",
            hint_text="Select TTS model folder",
            read_only=True,
            prefix_icon="folder_open",
            on_suffix_click=self._select_model_folder,
        )

        self.target_lang = ft.Dropdown(
            label="Target Language",
            value="vi",
            options=[
                ft.dropdown.Option("vi", "Vietnamese"),
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("ja", "Japanese"),
                ft.dropdown.Option("ko", "Korean"),
                ft.dropdown.Option("zh", "Chinese"),
                ft.dropdown.Option("fr", "French"),
                ft.dropdown.Option("de", "German"),
                ft.dropdown.Option("es", "Spanish"),
            ],
            width=200,
        )

        self.translate_btn = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(name="translate", size=18), ft.Text("Translate")],
                spacing=5,
            ),
            on_click=self._on_translate,
            expand=True,
        )

        self.content = ft.Column(
            [
                ft.Container(
                    content=self.drop_target,
                    onDragEnter=self._on_drag_enter,
                    onDragLeave=self._on_drag_leave,
                    onDragOver=self._on_drag_over,
                    onDrop=self._on_file_drop,
                ),
                ft.Container(height=10),
                ft.Text("Loaded SRT Files:", size=14, weight=ft.FontWeight.BOLD),
                self.srt_files_list,
                ft.Container(height=15),
                self.model_path,
                ft.Container(height=10),
                ft.Text("Translation Settings:", size=14, weight=ft.FontWeight.BOLD),
                self.target_lang,
                ft.Container(height=10),
                self.translate_btn,
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def _on_drop_click(self, e):
        """Handle click to open file picker."""
        picker = ft.FilePicker(on_result=self._on_file_picked)
        self.app.page.overlay.append(picker)
        picker.pick_files(allow_multiple=True, allowed_extensions=["srt", "SRT"])

    def _on_file_picked(self, e: ft.FilePickerResultException):
        """Handle picked files."""
        if not e.files:
            return
        for file in e.files:
            self._add_srt_file(file.path)
        self.app.page.update()

    def _add_srt_file(self, file_path: str):
        """Add SRT file to list."""
        file_name = os.path.basename(file_path)
        for item in self.srt_files_list.controls:
            if hasattr(item, "data") and item.data == file_path:
                return

        item = ft.ListTile(
            title=ft.Text(file_name, size=14),
            subtitle=ft.Text(file_path, size=10, color="#9E9E9E"),
            leading=ft.Icon(name="text_snippet", color="#B39DDB"),
            trailing=ft.IconButton(
                icon="close",
                icon_size=16,
                on_click=lambda e, p=file_path: self._remove_srt_file(p),
            ),
            data=file_path,
        )
        self.srt_files_list.controls.append(item)

    def _remove_srt_file(self, file_path: str):
        """Remove SRT file from list."""
        for item in self.srt_files_list.controls:
            if hasattr(item, "data") and item.data == file_path:
                self.srt_files_list.controls.remove(item)
                break
        self.app.page.update()

    def _on_drag_enter(self, e):
        """Handle drag enter."""
        self.drop_target.border = ft.border.all(3, "#B39DDB")
        self.app.page.update()

    def _on_drag_leave(self, e):
        """Handle drag leave."""
        self.drop_target.border = ft.border.all(2, "#673AB7")
        self.app.page.update()

    def _on_drag_over(self, e):
        """Handle drag over."""
        e.accept()

    def _on_file_drop(self, e: ft.DropEvent):
        """Handle file drop."""
        self.drop_target.border = ft.border.all(2, "#673AB7")
        if e.files:
            for file_path in e.files:
                path_str = file_path.path if hasattr(file_path, "path") else str(file_path)
                ext = os.path.splitext(path_str)[1].lower()
                if ext == ".srt":
                    self._add_srt_file(path_str)
        self.app.page.update()

    def _select_model_folder(self, e):
        """Select model folder."""
        picker = ft.FilePicker(on_result=self._on_model_folder_selected)
        self.app.page.overlay.append(picker)
        picker.get_directory()

    def _on_model_folder_selected(self, e: ft.FilePickerResultException):
        """Handle model folder selection."""
        self.app.page.update()

    def _on_translate(self, e):
        """Handle translate button click."""
        if not self.app.state.subtitle_file:
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("No SRT file loaded"), bgcolor="#FF9800")
            )
            return
        self.app.state.target_lang = self.target_lang.value
        self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Starting translation...")))
        self.app.page.update()