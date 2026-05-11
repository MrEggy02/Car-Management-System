import flet as ft
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pages.login_page import login_page
from theme.app_theme import apply_theme


def main(page: ft.Page):

    apply_theme(page)

    page.title = "JP Auto System"

    # ตั้งค่าเบื้องต้น
    page.window_resizable = True
    page.bgcolor = ft.Colors.WHITE

    # ขนาดขั้นต่ำ
    page.window_min_width = 900
    page.window_min_height = 600

    # update ก่อน
    page.update()

    # ค่อย fullscreen
    page.window_full_screen = True

    page.update()

    def on_login_success(page: ft.Page, client, user):
        from pages.dashboard_page import dashboard_page
        dashboard_page(page, client, user)

    login_page(page, on_login_success)


if __name__ == "__main__":
    ft.app(target=main)