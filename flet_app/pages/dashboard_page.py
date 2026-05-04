# pages/dashboard_page.py
import flet as ft
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import APIClient
from pages.app_layout import AppLayout
from theme.app_theme import apply_theme  # เพิ่ม import theme

def dashboard_page(page: ft.Page, client: APIClient, user: dict):
    """หน้า Dashboard หลัก - with persistent NavigationRail"""
    print("DEBUG: dashboard_page called")
    print(f"DEBUG: user = {user}")
    
    # Apply global font theme
    apply_theme(page)
    
    # Clear existing controls
    page.controls.clear()
    
    # Set page properties for dashboard
    page.title = "J&P Auto Maxing - Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.bgcolor = ft.Colors.WHITE
    
    # Set window size for dashboard
    page.window_width = 1200
    page.window_height = 800
    page.window_resizable = True
    
    # Create and build app layout
    try:
        app_layout = AppLayout(page, client, user)
        app_layout.build()
        print("DEBUG: AppLayout built successfully")
    except Exception as e:
        print(f"DEBUG: Error building AppLayout: {e}")
        import traceback
        traceback.print_exc()
    
    page.update()