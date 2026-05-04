# main.py
import flet as ft
import sys
import os

# ให้ Python หา path ของ project
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pages.login_page import login_page
from theme.app_theme import apply_theme


def main(page: ft.Page):
    """Main entry point"""

    # Apply global theme
    apply_theme(page)

    # Window settings
    page.title = "JP Auto System"
    page.window_full_screen = True
    page.window_resizable = True

    # กำหนดขั้นต่ำเพื่อกัน layout พัง
    page.window_min_width = 900
    page.window_min_height = 600

    # ถ้าจะให้ background สี
    page.bgcolor = ft.Colors.WHITE

    # Login success callback
    def on_login_success(page: ft.Page, client, user):
        from pages.dashboard_page import dashboard_page
        dashboard_page(page, client, user)

    # Start with login page
    login_page(page, on_login_success)


if __name__ == "__main__":
    ft.app(target=main)