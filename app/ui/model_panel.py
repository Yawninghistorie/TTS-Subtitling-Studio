"""
Model Info Panel - Display TTS model information
"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ui.main_page import MainPage


class ModelPanel(ft.Container):
    """Panel showing TTS model information."""

    def __init__(self, app: "MainPage"):
        super().__init__()
        self.app = app
        self._build()

    def _build(self):
        """Build model info panel UI."""
        self.model_name = ft.Text("No Model Loaded", size=16, weight=ft.FontWeight.BOLD)
        self.sample_rate = ft.Text("Sample Rate: --", size=12)
        self.languages = ft.Text("Languages: --", size=12)
        self.speakers = ft.Text("Speakers: --", size=12)

        self.speaker_dropdown = ft.Dropdown(
            label="Speaker",
            value=None,
            options=[],
            width=200,
            disabled=True,
            on_change=self._on_speaker_change,
        )

        self.preview_text = ft.TextField(
            label="Preview Text",
            value="Hello, this is a test.",
            multiline=False,
            width=280,
        )

        self.preview_btn = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.icons.PLAY_ARROW, size=18), ft.Text("Preview")],
                spacing=5,
            ),
            on_click=self._on_preview,
            disabled=True,
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text("Model Info", size=14, weight=ft.FontWeight.BOLD),
                        padding=ft.padding.only(bottom=10),
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [ft.Icon(ft.icons.MIC, size=16), self.model_name],
                                    spacing=10,
                                ),
                                self.sample_rate,
                                self.languages,
                                self.speakers,
                            ],
                            spacing=5,
                        ),
                        padding=ft.padding.all(10),
                        border=ft.border.all(1, ft.colors.OUTLINE),
                        border_radius=8,
                    ),
                    ft.Container(height=15),
                    self.speaker_dropdown,
                    ft.Container(height=10),
                    self.preview_text,
                    ft.Container(height=10),
                    self.preview_btn,
                ],
                spacing=10,
            ),
            padding=ft.padding.all(15),
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=12,
            bgcolor=ft.colors.SURFACE_CONTAINER_HIGH,
        )

    def update_model_info(self):
        """Update model info display."""
        model = self.app.state.tts_model
        if not model:
            self.model_name.value = "No Model Loaded"
            self.sample_rate.value = "Sample Rate: --"
            self.languages.value = "Languages: --"
            self.speakers.value = "Speakers: --"
            self.speaker_dropdown.disabled = True
            self.preview_btn.disabled = True
        else:
            self.model_name.value = model.name
            self.sample_rate.value = f"Sample Rate: {model.sample_rate} Hz"
            self.languages.value = f"Languages: {', '.join(model.languages)}"
            self.speakers.value = f"Speakers: {len(model.speakers)}"

            # Update speaker dropdown
            self.speaker_dropdown.options = [
                ft.dropdown.Option(str(s["id"]), s["name"])
                for s in model.speakers
            ]
            if model.speakers:
                self.speaker_dropdown.value = str(model.speakers[0]["id"])
            self.speaker_dropdown.disabled = False
            self.preview_btn.disabled = False

        self.app.page.update()

    def _on_speaker_change(self, e):
        """Handle speaker change."""
        # Store selected speaker ID
        pass

    def _on_preview(self, e):
        """Handle preview button click."""
        if not self.app.state.tts_model:
            return

        text = self.preview_text.value
        if not text.strip():
            return

        self.app.page.show_snack_bar(
            ft.SnackBar(content=ft.Text(f"Playing preview: {text[:30]}..."))
        )
        self.app.page.update()

        # TODO: Implement preview playback