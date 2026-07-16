import flet as ft
import sys
import os
import base64

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# ฟังก์ชัน resource_path (แก้ไขให้ถูกต้อง)
# ============================================
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        # กำลังรันในโหมด development (ไม่ใช่ .exe)
        base_path = os.path.abspath(".")
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ============================================

# import mock_patch (ถ้าไม่ใช้ให้ลบออก)
# import mock_patch

from pages.login_page import login_page
from theme.app_theme import apply_theme


def main(page: ft.Page):

    apply_theme(page)

    page.title = "JP Auto System"
    
    # ============================================
    # ตั้งค่า Window Icon
    # ============================================
    def set_window_icon():
        try:
            # ลองใช้หลายรูปแบบ
            icon_paths = [
                resource_path("assets/logo.ico"),
                resource_path("assets/car_logo.ico"),
                resource_path("assets/car_logo.png"),
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    # ใช้ Base64 สำหรับ .png
                    if icon_path.endswith('.png'):
                        with open(icon_path, "rb") as f:
                            icon_data = base64.b64encode(f.read()).decode()
                        page.window_icon = f"data:image/png;base64,{icon_data}"  # type: ignore
                    else:
                        page.window_icon = icon_path  # type: ignore
                    
                    page.update()
                    print(f"✅ Window icon set: {icon_path}")
                    return True
            
            print("⚠️ No icon file found!")
            return False
            
        except Exception as e:
            print(f"⚠️ Error setting window icon: {e}")
            return False
    
    # เรียกตั้งค่า icon
    set_window_icon()
    # ============================================
    
    page.window_resizable = True  # type: ignore
    page.bgcolor = ft.Colors.WHITE
    
    page.window_min_width = 900  # type: ignore
    page.window_min_height = 600  # type: ignore

    page.update()

    page.window_full_screen = True  # type: ignore

    page.update()

    def on_login_success(page: ft.Page, client, user):
        from pages.dashboard_page import dashboard_page
        dashboard_page(page, client, user)

    login_page(page, on_login_success)


if __name__ == "__main__":
    ft.run(main)