#!/usr/bin/env python3
"""
TTS Subtitling Studio
Desktop App: SRT → Gemini Translate → ONNX TTS → Audio

Entry Point
"""

import flet as ft
from app.ui.main_page import MainPage


def main(page: ft.Page):
    """Main entry point for Flet app."""
    app = MainPage(page)
    app.build()


if __name__ == "__main__":
    ft.app(target=main)