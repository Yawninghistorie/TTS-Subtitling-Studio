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
        # Model selector section
        self.model_section = ft.Container(
            content=ft.Column(
                [
                    ft.Text("🎙️ TTS Model", size=14, weight=ft.FontWeight.BOLD),
                    ft.Container(height=5),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [ft.Icon(icon="folder_open", size=18), ft.Text("Select Model Folder")],
                            spacing=10,
                        ),
                        on_click=self._select_model_folder,
                        expand=True,
                    ),
                    ft.Container(height=10),
                    ft.Text("Model: Not loaded", size=12, color="#9E9E9E", id="model_status"),
                ],
                spacing=5,
            ),
            padding=15,
            border=ft.border.all(2, "#673AB7"),
            border_radius=12,
            bgcolor="#312B36",
        )

        # SRT drop zone
        self.drop_target = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon="upload_file", size=48, color="#B39DDB"),
                    ft.Text("📄 Drop SRT files here", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("or click to browse", size=12, color="#9E9E9E"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=350,
            height=120,
            border=ft.border.all(2, "#673AB7"),
            border_radius=12,
            bgcolor="#312B36",
            on_click=self._on_drop_click,
        )

        self.srt_files_list = ft.ListView(
            expand=True,
            height=80,
            spacing=5,
        )

        self.target_lang = ft.Dropdown(
            label="🌐 Target Language",
            value="vi",
            options=[
                ft.dropdown.Option("vi", "🇻🇳 Vietnamese"),
                ft.dropdown.Option("en", "🇺🇸 English"),
                ft.dropdown.Option("ja", "🇯🇵 Japanese"),
                ft.dropdown.Option("ko", "🇰🇷 Korean"),
                ft.dropdown.Option("zh", "🇨🇳 Chinese"),
                ft.dropdown.Option("fr", "🇫🇷 French"),
                ft.dropdown.Option("de", "🇩🇪 German"),
                ft.dropdown.Option("es", "🇪🇸 Spanish"),
            ],
            width=280,
        )

        self.translate_btn = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(icon="translate", size=18), ft.Text("🔄 Translate with Gemini")],
                spacing=8,
            ),
            on_click=self._on_translate,
            expand=True,
        )

        self.content = ft.Column(
            [
                ft.Text("📂 Load Files", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                self.model_section,
                ft.Container(height=10),
                ft.Text("📝 SRT Subtitle File:", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=self.drop_target,
                    onDragEnter=self._on_drag_enter,
                    onDragLeave=self._on_drag_leave,
                    onDragOver=self._on_drag_over,
                    onDrop=self._on_file_drop,
                ),
                ft.Container(height=5),
                ft.Text("Loaded SRT Files:", size=12, weight=ft.FontWeight.BOLD),
                self.srt_files_list,
                ft.Container(height=15),
                self.target_lang,
                ft.Container(height=10),
                self.translate_btn,
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def _select_model_folder(self, e):
        """Select model folder."""
        def on_result(e: ft.FilePickerResultException):
            if e.path:
                from app.engine.tts_engine import TTSModelLoader
                models = TTSModelLoader.find_models_in_folder(e.path)
                if models:
                    model_info = TTSModelLoader.load_model(models[0])
                    if model_info:
                        self.app.state.tts_model = model_info
                        self._update_model_status(model_info.name)
                        self.app.page.show_snack_bar(
                            ft.SnackBar(content=ft.Text(f"✅ Loaded: {model_info.name}"))
                        )
                else:
                    self.app.page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("⚠️ No .onnx model found"), bgcolor="#FF9800")
                    )
            self.app.page.update()

        picker = ft.FilePicker(on_result=on_result)
        self.app.page.overlay.append(picker)
        picker.get_directory()

    def _update_model_status(self, model_name: str):
        """Update model status text."""
        for control in self.model_section.content.controls:
            if hasattr(control, 'id') and control.id == "model_status":
                control.value = f"✅ Model: {model_name}"
                break

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
            leading=ft.Icon(icon="text_snippet", color="#B39DDB"),
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

    def _on_translate(self, e):
        """Handle translate button click."""
        if not self.app.state.subtitle_file:
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("⚠️ No SRT file loaded"), bgcolor="#FF9800")
            )
            return
        self.app.state.target_lang = self.target_lang.value
        self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("🔄 Starting translation...")))
        self.app.page.update()