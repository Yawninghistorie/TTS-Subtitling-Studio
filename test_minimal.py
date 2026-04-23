#!/usr/bin/env python3
"""Minimal test app for TTS Subtitling Studio"""

import flet as ft


def main(page: ft.Page):
    page.title = "TTS Subtitling Studio"
    page.theme_mode = ft.ThemeMode.DARK
    
    # Simple test UI
    page.add(
        ft.Text("TTS Subtitling Studio", size=30, weight=ft.FontWeight.BOLD),
        ft.Text("Loading...", size=20),
        ft.ElevatedButton(content="Test Button", on_click=lambda e: print("Clicked!")),
    )


if __name__ == "__main__":
    ft.app(target=main)