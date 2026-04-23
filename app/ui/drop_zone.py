"""
Drop Zone - Drag & drop file handling
"""

import flet as ft
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
                    ft.Icon(ft.icons.UPLOAD_FILE, size=48, color=ft.colors.DEEP_PURPLE_200),
                    ft.Text("Drop SRT files here", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("or .onnx model files", size=12, color=ft.colors.GREY_400),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=350,
            height=180,
            border=ft.border.all(2, ft.colors.DEEP_PURPLE if True else ft.colors.OUTLINE),
            border_radius=ft.border_radius.all(12),
            bgcolor=ft.colors.SURFACE_CONTAINER_HIGHEST,
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
            prefix_icon=ft.icons.FOLDER_OPEN,
            on_suffix_click=self._select_model_folder,
        )

        self.target_lang = ft.Dropdown(
            label="Target Language",
            value="vi",
            options=[
                ft.dropdown.Option("vi", "Tiếng Việt"),
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("ja", "日本語"),
                ft.dropdown.Option("ko", "한국어"),
                ft.dropdown.Option("zh", "中文"),
                ft.dropdown.Option("fr", "Français"),
                ft.dropdown.Option("de", "Deutsch"),
                ft.dropdown.Option("es", "Español"),
            ],
            width=200,
        )

        self.translate_btn = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.icons.TRANSLATE, size=18), ft.Text("Translate")],
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
        picker.pick_files(
            allow_multiple=True,
            allowed_extensions=["srt", "SRT"],
        )

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

        # Check if already added
        for item in self.srt_files_list.controls:
            if hasattr(item, "data") and item.data == file_path:
                return

        item = ft.ListTile(
            title=ft.Text(file_name, size=14),
            subtitle=ft.Text(file_path, size=10, color=ft.colors.GREY_400),
            leading=ft.Icon(ft.icons.SUBSCRIPT, color=ft.colors.DEEP_PURPLE_200),
            trailing=ft.IconButton(
                icon=ft.icons.CLOSE,
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
        self.drop_target.border = ft.border.all(3, ft.colors.DEEP_PURPLE_200)
        self.drop_target.bgcolor = ft.colors.DEEP_PURPLE.with_alpha(30)
        self.app.page.update()

    def _on_drag_leave(self, e):
        """Handle drag leave."""
        self.drop_target.border = ft.border.all(2, ft.colors.OUTLINE)
        self.drop_target.bgcolor = ft.colors.SURFACE_CONTAINER_HIGHEST
        self.app.page.update()

    def _on_drag_over(self, e):
        """Handle drag over."""
        e.accept()

    def _on_file_drop(self, e: ft.DropEvent):
        """Handle file drop."""
        self.drop_target.border = ft.border.all(2, ft.colors.OUTLINE)
        self.drop_target.bgcolor = ft.colors.SURFACE_CONTAINER_HIGHEST

        if e.files:
            for file_path in e.files:
                path_str = file_path.path if hasattr(file_path, "path") else str(file_path)
                ext = os.path.splitext(path_str)[1].lower()

                if ext == ".srt":
                    self._add_srt_file(path_str)
                elif ext == ".onnx":
                    self._load_onnx_model(path_str)
                elif ext == ".onnx.json":
                    # Load associated onnx file
                    onnx_path = path_str.replace(".onnx.json", ".onnx")
                    if os.path.exists(onnx_path):
                        self._load_onnx_model(onnx_path)

        self.app.page.update()

    def _load_onnx_model(self, model_path: str):
        """Load ONNX TTS model."""
        from app.engine.tts_engine import TTSModelLoader

        model_info = TTSModelLoader.load_model(model_path)
        if model_info:
            self.app.state.tts_model = model_info
            self.model_path.value = model_path
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Loaded model: {model_info.name}"))
            )
        else:
            self.app.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Failed to load model"),
                    bgcolor=ft.colors.ERROR,
                )
            )

    def _select_model_folder(self, e):
        """Select model folder."""
        picker = ft.FilePicker(on_result=self._on_model_folder_selected)
        self.app.page.overlay.append(picker)
        picker.get_directory()

    def _on_model_folder_selected(self, e: ft.FilePickerResultException):
        """Handle model folder selection."""
        if e.path:
            from app.engine.tts_engine import TTSModelLoader

            models = TTSModelLoader.find_models_in_folder(e.path)
            if models:
                self._load_onnx_model(models[0])
                self.model_path.value = models[0]
            else:
                self.app.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("No TTS models found in folder"),
                        bgcolor=ft.colors.WARNING,
                    )
                )

        self.app.page.update()

    def _on_translate(self, e):
        """Handle translate button click."""
        if not self.app.state.subtitle_file:
            self.app.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("No SRT file loaded"),
                    bgcolor=ft.colors.WARNING,
                )
            )
            return

        self.app.state.target_lang = self.target_lang.value
        self.app.page.show_snack_bar(
            ft.SnackBar(content=ft.Text("Starting translation..."))
        )
        self.app.page.update()

        # TODO: Implement translation