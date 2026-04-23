"""
Waveform Display - Audio waveform visualization
Fixed for Flet 0.84+
"""

import flet as ft
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.ui.main_page import MainPage


class WaveformDisplay(ft.Container):
    """Waveform visualization display."""

    def __init__(self, app: "MainPage"):
        super().__init__()
        self.app = app
        self.waveform_data: List[float] = []
        self._build()

    def _build(self):
        """Build waveform display UI."""
        self.play_btn = ft.IconButton(
            icon="play_arrow",
            icon_size=32,
            tooltip="Play Preview",
            on_click=self._on_play,
        )

        self.stop_btn = ft.IconButton(
            icon="stop",
            icon_size=32,
            tooltip="Stop",
            on_click=self._on_stop,
        )

        self.progress_slider = ft.Slider(
            min=0,
            max=100,
            divisions=100,
            label="{value}%",
            expand=True,
        )

        self.time_label = ft.Text("00:00:00 / 00:00:00", size=12)

        self.waveform_placeholder = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(name="graphic_eq", size=48, color="#673AB7"),
                    ft.Text("Waveform preview will appear here", size=14, color="#9E9E9E"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
            width=800,
            height=150,
            alignment=ft.alignment.center,
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.play_btn, self.stop_btn, self.progress_slider, self.time_label],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(
                        content=self.waveform_placeholder,
                        border=ft.border.all(1, "#79747E"),
                        border_radius=8,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(10),
            border=ft.border.all(1, "#49454F"),
            border_radius=12,
            bgcolor="#1D1B20",
        )

    def update_waveform(self, waveform: List[float]):
        """Update waveform display."""
        self.waveform_data = waveform
        self.app.page.update()

    def _on_play(self, e):
        """Handle play button."""
        if not self.waveform_data:
            self.app.page.show_snack_bar(ft.SnackBar(content=ft.Text("Generate audio first")))
            return
        self.play_btn.icon = "pause"
        self.app.page.update()

    def _on_stop(self, e):
        """Handle stop button."""
        self.play_btn.icon = "play_arrow"
        self.progress_slider.value = 0
        self.app.page.update()