import flet as ft
from flet import Alignment
from i18n import get_text, set_language, get_current_language


class TopNavBarManager:
    def __init__(self, parent):
        self.parent = parent
        self.top_nav_bar = None
        self.user_profile_name = None
        self.user_profile_role = None
        self.app_name_text = None
        
    def build(self):
        """สร้าง Top Navigation Bar"""
        
        def change_language_to(lang):
            set_language(lang)
            self.parent._rebuild_all()
        
        # Current language
        current_lang = get_current_language()
        
        # Create menu items for PopupMenuButton
        menu_items = [
            # Personal Page
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.PERSON_OUTLINE, size=18, color="#1565C0"),
                        ft.Text(get_text("personal_page"), size=14, color="#1E293B"),
                    ],
                    spacing=10,
                ),
                on_click=lambda e: self.parent.navigate_to("personal_page"),
            ),
            ft.PopupMenuItem(),  # divider
            # Language section header
            ft.PopupMenuItem(
                content=ft.Text(get_text("language"), size=12, color="#64748B", weight=ft.FontWeight.W_500),
                disabled=True,
            ),
            # Lao
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE if current_lang == "lo" else ft.Icons.CIRCLE_OUTLINED, 
                               size=16, color="#1565C0" if current_lang == "lo" else "#94A3B8"),
                        ft.Text("LA", size=16),
                        ft.Text(get_text("lao_language"), size=14, color="#1E293B"),
                    ],
                    spacing=10,
                ),
                on_click=lambda e: change_language_to("lo"),
            ),
            # English
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE if current_lang == "en" else ft.Icons.CIRCLE_OUTLINED, 
                               size=16, color="#1565C0" if current_lang == "en" else "#94A3B8"),
                        ft.Text("EN", size=16),
                        ft.Text(get_text("english_language"), size=14, color="#1E293B"),
                    ],
                    spacing=10,
                ),
                on_click=lambda e: change_language_to("en"),
            ),
            ft.PopupMenuItem(),  # divider
            # Logout - Direct logout without confirmation dialog
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOGOUT, size=18, color="#EF4444"),
                        ft.Text(get_text("logout"), size=14, color="#EF4444"),
                    ],
                    spacing=10,
                ),
                on_click=lambda e: self._direct_logout(),  # Direct logout
            ),
        ]
        
        # User profile with PopupMenuButton
        user_profile = ft.PopupMenuButton(
            items=menu_items,
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.ACCOUNT_CIRCLE,
                                color=ft.Colors.WHITE,
                                size=36,
                            ),
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            border_radius=25,
                            padding=2,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    self.parent.user.get("fullname", self.parent.user.get("username", "User")),
                                    color=ft.Colors.WHITE,
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        self._get_role_text(self.parent.user.get("role", "user")),
                                        color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
                                        size=10,
                                    ),
                                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                                    border_radius=10,
                                    padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                                ),
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=8, right=8, top=6, bottom=6),
                border_radius=30,
            ),
        )
        
        # App name
        self.app_name_text = ft.Text(
            get_text("app_name"),
            size=16,
            weight=ft.FontWeight.W_700,
            color=ft.Colors.WHITE,
        )
        
        # Logo
        logo_circle = ft.Container(
            content=ft.Image(
                src="assets/car_logo.png",
                width=30,
                height=30,
                fit="cover",
            ),
            width=30,
            height=30,
            border_radius=25,
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            alignment=Alignment.CENTER,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
        
        # Top navigation bar
        self.top_nav_bar = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=ft.Colors.WHITE,
                        icon_size=24,
                        on_click=lambda e: self.parent.toggle_sidebar(),
                        tooltip=get_text("menu"),
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                logo_circle,
                                self.app_name_text,
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        expand=True,
                        alignment=Alignment.CENTER,
                        padding=ft.Padding(left=175, right=0, top=0, bottom=0),
                    ),
                    ft.Row(
                        [
                            user_profile,
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=15, right=20, top=12, bottom=12),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=["#1565C0", "#0D47A1"],
            ),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            ),
        )
        
        return self.top_nav_bar

    def _direct_logout(self):
        """Direct logout without confirmation dialog"""
        print("DEBUG: Direct logout called")
        
        # Navigate to login page directly
        from pages.login_page import login_page

        def on_login_success(p, c, u):
            from pages.dashboard_page import dashboard_page
            dashboard_page(p, c, u)

        login_page(self.parent.page, on_login_success)
    
    def _get_role_text(self, role):
        """แปลง role เป็นข้อความที่แสดง"""
        roles = {
            "admin": get_text("role_admin"),
            "technician": get_text("role_technician"),
            "reception": get_text("role_reception"),
            "manager": get_text("role_manager"),
            "user": get_text("role_user"),
            "mechanic": get_text("role_mechanic"),
        }
        return roles.get(role, role)
    
    def update_user_info(self):
        """อัพเดทข้อมูลผู้ใช้ที่แสดง"""
        pass
    
    @property
    def page(self):
        """Get parent page"""
        return self.parent.page