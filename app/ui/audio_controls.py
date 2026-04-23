"""
Audio Controls - Volume, speed, pitch adjustments
"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.ui.main_page import MainPage


class AudioControls:
    """Audio post-processing controls."""

    def __init__(self, app: "MainPage"):
        self.app = app
        self.volume = 1.0
        self.speed = 1.0
        self.pitch = 0.0
        self.fade_in = 0.1
        self.fade_out = 0.2
        self.normalize = True
        self.peak_db = -3.0

    def build(self) -> ft.Container:
        """Build audio controls UI."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Audio Settings", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Volume", size=12),
                                        ft.Slider(
                                            min=0,
                                            max=2,
                                            divisions=20,
                                            value=1.0,
                                            on_change=self._on_volume_change,
                                            width=150,
                                        ),
                                        ft.Text(f"{self.volume * 100:.0f}%", size=10),
                                    ],
                                    spacing=2,
                                ),
                                padding=10,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=8,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Speed", size=12),
                                        ft.Slider(
                                            min=0.5,
                                            max=2,
                                            divisions=15,
                                            value=1.0,
                                            on_change=self._on_speed_change,
                                            width=150,
                                        ),
                                        ft.Text(f"{self.speed:.1f}x", size=10),
                                    ],
                                    spacing=2,
                                ),
                                padding=10,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=8,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Pitch", size=12),
                                        ft.Slider(
                                            min=-12,
                                            max=12,
                                            divisions=24,
                                            value=0,
                                            on_change=self._on_pitch_change,
                                            width=150,
                                        ),
                                        ft.Text(f"{self.pitch:+.0f} semitones", size=10),
                                    ],
                                    spacing=2,
                                ),
                                padding=10,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=8,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Fade In", size=12),
                                        ft.Slider(
                                            min=0,
                                            max=2,
                                            divisions=20,
                                            value=0.1,
                                            on_change=self._on_fade_in_change,
                                            width=150,
                                        ),
                                        ft.Text(f"{self.fade_in:.1f}s", size=10),
                                    ],
                                    spacing=2,
                                ),
                                padding=10,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=8,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Fade Out", size=12),
                                        ft.Slider(
                                            min=0,
                                            max=2,
                                            divisions=20,
                                            value=0.2,
                                            on_change=self._on_fade_out_change,
                                            width=150,
                                        ),
                                        ft.Text(f"{self.fade_out:.1f}s", size=10),
                                    ],
                                    spacing=2,
                                ),
                                padding=10,
                                border=ft.border.all(1, ft.colors.OUTLINE),
                                border_radius=8,
                            ),
                        ],
                        spacing=15,
                        wrap=True,
                    ),
                    ft.Row(
                        [
                            ft.Switch(
                                label="Normalize Volume",
                                value=True,
                                on_change=self._on_normalize_change,
                            ),
                            ft.Text("Peak: ", size=12),
                            ft.Dropdown(
                                value="-3",
                                options=[
                                    ft.dropdown.Option("-1", "-1 dB (Loud)"),
                                    ft.dropdown.Option("-3", "-3 dB (Standard)"),
                                    ft.dropdown.Option("-6", "-6 dB (Conservative)"),
                                    ft.dropdown.Option("-12", "-12 dB (Quiet)"),
                                ],
                                width=180,
                                on_change=self._on_peak_change,
                            ),
                        ],
                        spacing=20,
                    ),
                ],
                spacing=15,
            ),
            padding=ft.padding.all(15),
            border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
            border_radius=12,
            bgcolor=ft.colors.SURFACE_CONTAINER_LOW,
        )

    def _on_volume_change(self, e):
        """Handle volume change."""
        self.volume = e.control.value
        self.app.page.update()

    def _on_speed_change(self, e):
        """Handle speed change."""
        self.speed = e.control.value
        self.app.page.update()

    def _on_pitch_change(self, e):
        """Handle pitch change."""
        self.pitch = e.control.value
        self.app.page.update()

    def _on_fade_in_change(self, e):
        """Handle fade in change."""
        self.fade_in = e.control.value
        self.app.page.update()

    def _on_fade_out_change(self, e):
        """Handle fade out change."""
        self.fade_out = e.control.value
        self.app.page.update()

    def _on_normalize_change(self, e):
        """Handle normalize toggle."""
        self.normalize = e.control.value
        self.app.page.update()

    def _on_peak_change(self, e):
        """Handle peak level change."""
        try:
            self.peak_db = float(e.control.value)
        except:
            pass
        self.app.page.update()