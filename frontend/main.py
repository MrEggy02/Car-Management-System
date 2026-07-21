import flet as ft
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import mock_patch

from pages.login_page import login_page
from theme.app_theme import apply_theme


def main(page: ft.Page):

    apply_theme(page)

    page.title = "JP Auto System"
    
    page.window_resizable = True
    page.bgcolor = ft.Colors.WHITE
    
    page.window_min_width = 900
    page.window_min_height = 600

    page.update()

    page.window_full_screen = True

    page.update()

    def on_login_success(page: ft.Page, client, user):
        from pages.dashboard_page import dashboard_page
        dashboard_page(page, client, user)

    login_page(page, on_login_success)

if __name__ == "__main__":
    ft.run(main)