"""
Waveform Display - Audio waveform visualization
"""

import flet as ft
from flet import colors, icons
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
        self.canvas = ft.Container(
            content=ft.Stack(
                [
                    # Background
                    ft.Container(
                        width=800,
                        height=150,
                        bgcolor=colors.SURFACE_CONTAINER_HIGHEST,
                        border_radius=8,
                    ),
                    # Waveform will be drawn here
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(
                                    icons.GRAPHIC_EQ,
                                    size=48,
                                    color=colors.DEEP_PURPLE.with_alpha(100),
                                ),
                                ft.Text(
                                    "Waveform preview will appear here",
                                    size=14,
                                    color=colors.GREY_500,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            expand=True,
                        ),
                        width=800,
                        height=150,
                        alignment=ft.alignment.center,
                    ),
                ],
                width=800,
                height=150,
            ),
            width=800,
            height=150,
            border=ft.border.all(1, colors.OUTLINE),
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        self.play_btn = ft.IconButton(
            icon=icons.PLAY_ARROW,
            icon_size=32,
            tooltip="Play Preview",
            on_click=self._on_play,
        )

        self.stop_btn = ft.IconButton(
            icon=icons.STOP,
            icon_size=32,
            tooltip="Stop",
            on_click=self._on_stop,
        )

        self.progress_slider = ft.Slider(
            min=0,
            max=100,
            divisions=100,
            label="{value}%",
            on_change=self._on_seek,
            expand=True,
        )

        self.time_label = ft.Text("00:00:00 / 00:00:00", size=12)

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.play_btn, self.stop_btn, self.progress_slider, self.time_label],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self.canvas,
                ],
                spacing=10,
            ),
            padding=ft.padding.all(10),
            border=ft.border.all(1, colors.OUTLINE_VARIANT),
            border_radius=12,
            bgcolor=colors.SURFACE_CONTAINER_LOW,
        )

    def update_waveform(self, waveform: List[float]):
        """Update waveform display."""
        self.waveform_data = waveform

        # Draw waveform on canvas
        # For now, draw a simple representation
        if waveform:
            # Draw simplified waveform using shapes
            self._draw_waveform()

        self.app.page.update()

    def _draw_waveform(self):
        """Draw waveform visualization."""
        # This is a simplified version
        # In production, you'd use CustomPainter or canvas
        self.canvas.content = ft.Stack(
            [
                ft.Container(
                    width=800,
                    height=150,
                    bgcolor=colors.SURFACE_CONTAINER_HIGHEST,
                    border_radius=8,
                ),
                ft.Container(
                    content=ft.Text(
                        f"Waveform: {len(self.waveform_data)} samples",
                        size=14,
                        color=colors.GREEN_200,
                    ),
                    width=800,
                    height=150,
                    alignment=ft.alignment.center,
                ),
            ],
            width=800,
            height=150,
        )

    def _on_play(self, e):
        """Handle play button."""
        if not self.waveform_data:
            self.app.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Generate audio first"))
            )
            return

        self.play_btn.icon = icons.PAUSE
        self.app.page.update()

    def _on_stop(self, e):
        """Handle stop button."""
        self.play_btn.icon = icons.PLAY_ARROW
        self.progress_slider.value = 0
        self.app.page.update()

    def _on_seek(self, e):
        """Handle seek slider."""
        # TODO: Implement audio seeking
        pass