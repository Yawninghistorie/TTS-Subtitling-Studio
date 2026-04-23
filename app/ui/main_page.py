"""
Main Page UI - TTS Subtitling Studio
Compatible with Flet 0.84.0
"""

import flet as ft


class AppState:
    """Global application state."""

    def __init__(self):
        self.subtitle_file = None
        self.tts_model = None
        self.translator = None
        self.audio_engine = None
        self.target_lang = "vi"
        self.theme = "dark"


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
                            ft.Icon(icon="PLAY_CIRCLE_FILLED", size=32, color="#B39DDB"),
                            ft.Text("TTS Subtitling Studio", size=22, weight=ft.FontWeight.BOLD),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.IconButton(icon="DARK_MODE", on_click=self._toggle_theme),
                            ft.IconButton(icon="INFO_OUTLINED", on_click=self._show_about),
                        ]
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
            bgcolor="#1C1B1F",
        )

    def _build_body(self):
        """Build main body content."""
        self.left_panel = ft.Container(
            content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=15),
            width=400,
            padding=15,
        )
        self._build_left_panel()

        self.center_panel = ft.Container(
            content=ft.Column(spacing=10),
            expand=True,
            padding=15,
        )
        self._build_center_panel()

        self.body = ft.Container(
            content=ft.Row([self.left_panel, ft.VerticalDivider(), self.center_panel]),
            expand=True,
        )

    def _build_left_panel(self):
        """Build left panel with model and file selection."""
        self.model_btn = ft.ElevatedButton(
            content="Select TTS Model",
            icon="FOLDER_OPEN",
            on_click=self._select_model,
        )
        self.model_label = ft.Text("Model: Not loaded", size=12, color="#9E9E9E")

        self.srt_btn = ft.ElevatedButton(
            content="Load SRT File",
            icon="UPLOAD_FILE",
            on_click=self._select_srt,
        )
        self.srt_label = ft.Text("No SRT file loaded", size=12, color="#9E9E9E")

        self.lang_dropdown = ft.Dropdown(
            label="Target Language",
            value="vi",
            options=[
                ft.dropdown.Option("vi", "Vietnamese"),
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("ja", "Japanese"),
                ft.dropdown.Option("ko", "Korean"),
                ft.dropdown.Option("zh", "Chinese"),
            ],
            width=300,
        )

        self.translate_btn = ft.ElevatedButton(
            content="Translate with Gemini",
            icon="TRANSLATE",
            on_click=self._translate,
        )

        self.left_panel.content.controls.extend([
            ft.Text("Load Model", size=16, weight=ft.FontWeight.BOLD),
            self.model_btn,
            self.model_label,
            ft.Divider(),
            ft.Text("Load Subtitle", size=16, weight=ft.FontWeight.BOLD),
            self.srt_btn,
            self.srt_label,
            ft.Divider(),
            self.lang_dropdown,
            ft.Container(height=10),
            self.translate_btn,
        ])

    def _build_center_panel(self):
        """Build center panel with subtitle list and controls."""
        self.subtitle_list = ft.ListView(expand=True, spacing=5)
        self.play_btn = ft.IconButton(icon="PLAY_ARROW", icon_size=32, on_click=self._play)
        self.stop_btn = ft.IconButton(icon="STOP", icon_size=32, on_click=self._stop)

        self.center_panel.content.controls.extend([
            ft.Text("Subtitles", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(content=self.subtitle_list, border=ft.border.all(1, "#49454F"), expand=True),
            ft.Row([self.play_btn, self.stop_btn]),
        ])

    def _build_footer(self):
        """Build footer with generate button."""
        self.generate_btn = ft.ElevatedButton(
            content="Generate Audio",
            icon="PLAY_CIRCLE_FILLED",
            on_click=self._generate,
            expand=True,
        )
        self.export_btn = ft.ElevatedButton(
            content="Export",
            icon="SAVE",
            on_click=self._export,
            expand=True,
        )

        self.footer = ft.Container(
            content=ft.Row([self.generate_btn, self.export_btn], spacing=10),
            padding=15,
            bgcolor="#1C1B1F",
        )

    def _select_model(self, e):
        """Select TTS model."""
        def on_result(e: ft.FilePickerResultException):
            if e.path:
                self.model_label.value = f"Model: {e.path}"
                self.page.update()
        picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(picker)
        picker.get_directory()

    def _select_srt(self, e):
        """Select SRT file."""
        def on_result(e: ft.FilePickerResultException):
            if e.files:
                self.srt_label.value = e.files[0].name
                self.state.subtitle_file = e.files[0].path
                self._update_subtitle_list()
                self.page.update()
        picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(picker)
        picker.pick_files(allowed_extensions=["srt"])

    def _update_subtitle_list(self):
        """Update subtitle list display."""
        self.subtitle_list.controls.clear()
        if self.state.subtitle_file:
            self.subtitle_list.controls.append(
                ft.ListTile(title=ft.Text(self.state.subtitle_file))
            )
        else:
            self.subtitle_list.controls.append(
                ft.ListTile(title=ft.Text("No subtitles loaded"))
            )

    def _translate(self, e):
        """Translate subtitles."""
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Translation started...")))

    def _play(self, e):
        """Play audio."""
        pass

    def _stop(self, e):
        """Stop audio."""
        pass

    def _generate(self, e):
        """Generate audio."""
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Generating audio...")))

    def _export(self, e):
        """Export audio."""
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Exporting...")))

    def _toggle_theme(self, e):
        """Toggle theme."""
        self.page.theme_mode = ft.ThemeMode.LIGHT if self.page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        self.page.update()

    def _show_about(self, e):
        """Show about dialog."""
        dialog = ft.AlertDialog(
            title=ft.Text("About"),
            content=ft.Text("TTS Subtitling Studio v1.0\nSRT to Audio with Gemini translation"),
            actions=[ft.TextButton(content="OK", on_click=lambda e: self._close_dialog())],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self):
        """Close dialog."""
        self.page.dialog.open = False
        self.page.update()