"""
Main Page UI - TTS Subtitling Studio
"""

import flet as ft
from flet import colors, icons
import os
from typing import List, Dict, Optional, Callable
from app.ui.drop_zone import DropZone
from app.ui.model_panel import ModelPanel
from app.ui.subtitle_editor import SubtitleEditor
from app.ui.audio_controls import AudioControls
from app.ui.waveform_display import WaveformDisplay


class AppState:
    """Global application state."""

    def __init__(self):
        self.subtitle_file = None
        self.tts_model = None
        self.translator = None
        self.audio_engine = None
        self.target_lang = "vi"
        self.theme = "dark"
        self.undo_stack: List[str] = []
        self.redo_stack: List[str] = []

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0


class MainPage:
    """Main application page."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.state = AppState()
        self._setup_page()

    def _setup_page(self):
        """Setup page properties."""
        self.page.title = "TTS Subtitling Studio"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.window_min_width = 1200
        self.page.window_min_height = 700

        # Load theme
        self.page.theme = ft.Theme(
            color_scheme_seed=colors.DEEP_PURPLE,
            brightness=ft.ThemeMode.DARK,
        )

    def build(self):
        """Build the main UI."""
        self._build_header()
        self._build_body()
        self._build_footer()

        self.page.add(self.header, self.body, self.footer)
        self.page.update()

    def _build_header(self):
        """Build header with logo and actions."""
        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(icons.PLAY_CIRCLE_FILL, size=32, color=colors.DEEP_PURPLE_200),
                            ft.Text(
                                "TTS Subtitling Studio",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=colors.WHITE,
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=icons.DARK_MODE,
                                tooltip="Toggle Theme",
                                on_click=self._toggle_theme,
                            ),
                            ft.IconButton(
                                icon=icons.SETTINGS,
                                tooltip="Settings",
                                on_click=self._show_settings,
                            ),
                            ft.IconButton(
                                icon=icons.INFO_OUTLINE,
                                tooltip="About",
                                on_click=self._show_about,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True,
            ),
            padding=ft.padding.all(15),
            bgcolor=colors.SURFACE_CONTAINER_HIGH,
            border=ft.border.only(bottom=ft.border.BorderSide(1, colors.OUTLINE_VARIANT)),
        )

    def _build_body(self):
        """Build main body content."""
        self.left_panel = ft.Container(
            content=ft.Column(
                [
                    DropZone(self),
                    ModelPanel(self),
                ],
                spacing=20,
            ),
            width=400,
            padding=ft.padding.all(15),
        )

        self.center_panel = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text("Preview", size=16, weight=ft.FontWeight.BOLD),
                        padding=ft.padding.only(bottom=5),
                    ),
                    WaveformDisplay(self),
                    ft.Container(height=20),
                    SubtitleEditor(self),
                ],
                spacing=10,
            ),
            expand=True,
            padding=ft.padding.all(15),
        )

        self.body = ft.Container(
            content=ft.Row(
                [self.left_panel, ft.VerticalDivider(), self.center_panel],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )

    def _build_footer(self):
        """Build footer with audio controls."""
        self.audio_controls = AudioControls(self)

        self.progress_bar = ft.ProgressBar(
            value=0,
            bar_height=8,
            expand=True,
            visible=False,
        )

        self.footer = ft.Container(
            content=ft.Column(
                [
                    self.audio_controls.build(),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [ft.Icon(icons.PLAY_ARROW, size=18), ft.Text("Generate Audio")],
                                    spacing=5,
                                ),
                                on_click=self._on_generate,
                                expand=True,
                            ),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [ft.Icon(icons.SAVE, size=18), ft.Text("Export")],
                                    spacing=5,
                                ),
                                on_click=self._on_export,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    self.progress_bar,
                ],
                spacing=10,
            ),
            padding=ft.padding.all(15),
            bgcolor=colors.SURFACE_CONTAINER_HIGH,
            border=ft.border.only(top=ft.border.BorderSide(1, colors.OUTLINE_VARIANT)),
        )

    def _toggle_theme(self, e):
        """Toggle dark/light theme."""
        self.page.theme_mode = (
            ft.ThemeMode.LIGHT
            if self.page.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        self.state.theme = "light" if self.page.theme_mode == ft.ThemeMode.LIGHT else "dark"
        self.page.update()

    def _show_settings(self, e):
        """Show settings dialog."""
        dialog = ft.AlertDialog(
            title=ft.Text("Settings"),
            content=ft.Column(
                [
                    ft.TextField(
                        label="Gemini API Key",
                        hint_text="Enter your API key",
                        password=True,
                        on_change=self._on_api_key_change,
                    ),
                    ft.TextField(
                        label="Output Directory",
                        hint_text="/path/to/output",
                        on_change=self._on_output_dir_change,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._close_dialog),
                ft.TextButton("Save", on_click=self._save_settings),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _show_about(self, e):
        """Show about dialog."""
        dialog = ft.AlertDialog(
            title=ft.Text("About TTS Subtitling Studio"),
            content=ft.Column(
                [
                    ft.Text("Version 1.0.0"),
                    ft.Text("Desktop app for SRT → Translate → TTS → Audio"),
                    ft.Container(height=10),
                    ft.Text("Features:", weight=ft.FontWeight.BOLD),
                    ft.Text("• Drag & drop SRT files"),
                    ft.Text("• Gemini translation with context"),
                    ft.Text("• ONNX TTS model support"),
                    ft.Text("• Live subtitle editing"),
                    ft.Text("• Audio post-processing"),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("Close", on_click=self._close_dialog),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self, e):
        """Close dialog."""
        self.page.dialog.open = False
        self.page.update()

    def _on_api_key_change(self, e):
        """Handle API key change."""
        pass

    def _on_output_dir_change(self, e):
        """Handle output dir change."""
        pass

    def _save_settings(self, e):
        """Save settings."""
        self._close_dialog(e)

    def _on_generate(self, e):
        """Generate audio."""
        if not self.state.subtitle_file:
            self._show_error("No subtitle file loaded")
            return

        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.page.update()

        # TODO: Implement generate logic
        self._show_info("Audio generation started...")

    def _on_export(self, e):
        """Export audio."""
        if not self.state.subtitle_file:
            self._show_error("No audio generated")
            return

        self._show_info("Select output path to save...")

    def _show_error(self, message: str):
        """Show error snackbar."""
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(message), bgcolor=colors.ERROR))

    def _show_info(self, message: str):
        """Show info snackbar."""
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(message)))
        self.page.update()