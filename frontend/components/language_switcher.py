# components/language_switcher.py
import flet as ft
from i18n import (
    set_language,
    get_language_name,
    get_current_language,
    get_font,
)

def create_language_switcher(on_change=None):
    """Create language dropdown for switching languages"""

    def on_language_change(e):
        set_language(e.control.value)

        # refresh font if language changed
        if on_change:
            on_change(e)

    return ft.Dropdown(
        value=get_current_language(),
        options=[
            ft.dropdown.Option("lo", "🇱🇦 ພາສາລາວ"),
            ft.dropdown.Option("en", "EN English"),
        ],
        on_change=on_language_change,
        width=150,
        height=40,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        text_style=ft.TextStyle(
            font_family=get_font(),
            size=14,
        ),
    )