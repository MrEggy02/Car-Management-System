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
        
        # Language switcher
        current_lang = get_current_language()
        lang_display = "LA" if current_lang == "lo" else "EN"
        
        language_switcher = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Text("🇱🇦", size=16),
                            ft.Text(get_text("lao_language"), size=14, color=ft.Colors.GREY_800),
                        ],
                        spacing=10,
                    ),
                    on_click=lambda e: change_language_to("lo"),
                ),
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Text("🇬🇧", size=16),
                            ft.Text(get_text("english_language"), size=14, color=ft.Colors.GREY_800),
                        ],
                        spacing=10,
                    ),
                    on_click=lambda e: change_language_to("en"),
                ),
            ],
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.TRANSLATE_OUTLINED, size=18, color=ft.Colors.WHITE),
                        ft.Text(
                            lang_display,
                            size=13,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=18, color=ft.Colors.WHITE),
                    ],
                    spacing=4,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border_radius=20,
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            ),
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
        
        # User profile
        self.user_profile_name = ft.Text(
            self.parent.user.get("fullname", self.parent.user.get("username", "User")),
            color=ft.Colors.WHITE,
            size=14,
            weight=ft.FontWeight.BOLD,
        )
        
        self.user_profile_role = ft.Container(
            content=ft.Text(
                self._get_role_text(self.parent.user.get("role", "user")),
                color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
                size=11,
            ),
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
        )
        
        user_profile = ft.Row(
            [
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.ACCOUNT_CIRCLE,
                        color=ft.Colors.WHITE,
                        size=40,
                    ),
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                    border_radius=25,
                    padding=2,
                ),
                ft.Column(
                    [
                        self.user_profile_name,
                        self.user_profile_role,
                    ],
                    spacing=2,
                ),
            ],
            spacing=10,
        )
        
        # App name
        self.app_name_text = ft.Text(
            get_text("app_name"),
            size=16,
            weight=ft.FontWeight.W_700,
            color=ft.Colors.WHITE,
        )
        
        # Right section
        right_section = ft.Row(
            [
                language_switcher,
                user_profile,
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.END,
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
                        padding=ft.padding.only(left=175),
                    ),
                    right_section,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(left=15, right=20, top=12, bottom=12),
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
    
    def _get_role_text(self, role):
        """แปลง role เป็นข้อความที่แสดง"""
        roles = {
            "admin": get_text("role_admin"),
            "technician": get_text("role_technician"),
            "reception": get_text("role_reception"),
            "manager": get_text("role_manager"),
            "user": get_text("role_user"),
        }
        return roles.get(role, role)
    
    def update_user_info(self):
        """อัพเดทข้อมูลผู้ใช้ที่แสดง"""
        if self.user_profile_name:
            self.user_profile_name.value = self.parent.user.get("fullname", self.parent.user.get("username", "User"))
            self.user_profile_name.update()
        
        if self.user_profile_role and self.user_profile_role.content:
            self.user_profile_role.content.value = self._get_role_text(self.parent.user.get("role", "user"))
            self.user_profile_role.update()