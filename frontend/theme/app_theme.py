# app_theme.py
import flet as ft

# ฟอนต์หลักของแอพ
APP_FONT = "Lao Sangam MN"

def apply_theme(page: ft.Page):
    """Apply global theme with custom font to all pages"""
    
    # Register font
    page.fonts = {
        APP_FONT: "fonts/Phetsarath.ttf",
    }
    
    # main color 
    PRIMARY_COLOR = "#0D47A1"
    TEXT_COLOR = "#1A1A1A"  # สีดำ
    
    # Create text theme with custom font and black color
    text_theme = ft.TextTheme(
        display_large=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        display_medium=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        display_small=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        headline_large=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        headline_medium=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        headline_small=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        title_large=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        title_medium=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        title_small=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        body_large=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        body_medium=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        body_small=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        label_large=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        label_medium=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
        label_small=ft.TextStyle(font_family=APP_FONT, color=TEXT_COLOR),
    )
    
    # Apply theme (ลบ color_scheme ที่มี parameter ไม่รองรับ)
    page.theme = ft.Theme(
        font_family=APP_FONT,
        text_theme=text_theme,
    )
    
    # ตั้งค่าสีพื้นหลังของหน้า
    page.bgcolor = ft.Colors.WHITE
    
    # ตั้ง default text style
    page.default_text_style = ft.TextStyle(
        font_family=APP_FONT,
        color=TEXT_COLOR,
    )
    
    page.update()