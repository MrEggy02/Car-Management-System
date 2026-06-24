import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime

from i18n import get_text


class PersonalPageContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.primary_light = "#E3F2FD"
        
        # Edit mode
        self.is_editing = False
        
    def build(self):
        # Header with gradient
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=24,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("dashboard"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("personal_page"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON, size=28, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                        border_radius=15,
                        padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=26, right=26, top=14, bottom=14),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
            
        )
        
        # Main content
        content = self._build_content()
        
        # Scrollable content
        scrollable_content = ft.Column(
            [content],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.Padding(left=32, right=32, top=32, bottom=32),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        return main_content
    
    def _build_content(self):
        # User avatar with gradient circle
        name = self.user.get('fullname', self.user.get('username', 'User'))
        first_char = name[0].upper() if name else "U"
        
        avatar = ft.Container(
            content=ft.Text(
                first_char,
                size=48,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            width=100,
            height=100,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=50,
            alignment=ft.Alignment(0, 0),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color=ft.Colors.with_opacity(0.3, self.primary_color),
            ),
        )
        
        # User info card
        if not self.is_editing:
            info_card = self._build_info_display()
        else:
            info_card = self._build_info_edit()
        
        # Action buttons
        action_buttons = self._build_action_buttons()
        
        # System info card
        system_card = self._build_system_info()
        
        return ft.Column([
            ft.Container(height=20),
            ft.Row(
                [
                    ft.Container(expand=True),
                    ft.Column(
                        [
                            avatar,
                            ft.Container(height=16),
                            ft.Text(
                                name,
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                            ft.Text(
                                self._get_role_text(self.user.get('role', 'user')),
                                size=13,
                                color="#64748B",
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(expand=True),
                ],
            ),
            ft.Container(height=32),
            info_card,
            ft.Container(height=20),
            action_buttons,
            ft.Container(height=20),
            system_card,
        ], spacing=0)
    
    def _build_info_display(self):
        """Build display mode for user info"""
        username = self.user.get('username', '-')
        fullname = self.user.get('fullname', '-')
        role = self.user.get('role', 'user')
        role_text = self._get_role_text(role)
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.INFO, size=20, color=self.primary_color),
                                bgcolor=self.primary_light,
                                border_radius=10,
                                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                            ),
                            ft.Text(
                                get_text("personal_information"),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    # Username
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON_OUTLINE, size=18, color="#64748B"),
                            width=32,
                        ),
                        ft.Column([
                            ft.Text(get_text("username"), size=11, color="#94A3B8"),
                            ft.Text(username, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ], spacing=2, expand=True),
                    ], spacing=8),
                    ft.Container(height=12),
                    # Full name
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.BADGE, size=18, color="#64748B"),
                            width=32,
                        ),
                        ft.Column([
                            ft.Text(get_text("fullname"), size=11, color="#94A3B8"),
                            ft.Text(fullname, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ], spacing=2, expand=True),
                    ], spacing=8),
                    ft.Container(height=12),
                    # Role
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.WORK, size=18, color="#64748B"),
                            width=32,
                        ),
                        ft.Column([
                            ft.Text(get_text("role"), size=11, color="#94A3B8"),
                            ft.Container(
                                content=ft.Text(role_text, size=12, color=ft.Colors.WHITE),
                                bgcolor=self.primary_color,
                                border_radius=12,
                                padding=ft.Padding(left=12, right=12, top=4, bottom=4),
                            ),
                        ], spacing=2, expand=True),
                    ], spacing=8),
                ]),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            ),
            elevation=2,
        )
    
    def _build_info_edit(self):
        """Build edit mode for user info"""
        username = self.user.get('username', '-')
        fullname = self.user.get('fullname', '-')
        
        # Fields for editing (only fullname can be edited)
        self.fullname_field = ft.TextField(
            label=get_text("fullname"),
            value=fullname,
            border_radius=12,
            prefix_icon=ft.Icons.BADGE,
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.EDIT, size=20, color=self.primary_color),
                                bgcolor=self.primary_light,
                                border_radius=10,
                                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                            ),
                            ft.Text(
                                get_text("edit_information"),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    # Username (readonly)
                    ft.TextField(
                        label=get_text("username"),
                        value=username,
                        border_radius=12,
                        prefix_icon=ft.Icons.PERSON_OUTLINE,
                        read_only=True,
                        border_color=ft.Colors.GREY_300,
                        content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                    ),
                    ft.Container(height=12),
                    # Fullname (editable)
                    self.fullname_field,
                    ft.Container(height=12),
                    # Role (readonly)
                    ft.TextField(
                        label=get_text("role"),
                        value=self._get_role_text(self.user.get('role', 'user')),
                        border_radius=12,
                        prefix_icon=ft.Icons.WORK,
                        read_only=True,
                        border_color=ft.Colors.GREY_300,
                        content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                    ),
                ]),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            ),
            elevation=2,
        )
    
    def _build_action_buttons(self):
        if not self.is_editing:
            return ft.Row(
                [
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOCK_RESET, size=18, color=self.primary_color),
                            ft.Text(get_text("change_password"), size=14, color=self.primary_color),
                        ], spacing=6),
                        on_click=self.show_change_password_dialog,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            side=ft.BorderSide(1, self.primary_color),
                        ),
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.EDIT, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("edit_profile"), size=14, color=ft.Colors.WHITE),
                        ], spacing=6),
                        on_click=self.toggle_edit_mode,
                        style=ft.ButtonStyle(
                            bgcolor=self.primary_color,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        expand=True,
                    ),
                ],
                spacing=16,
            )
        else:
            return ft.Row(
                [
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
                            ft.Text(get_text("cancel"), size=14, color="#64748B"),
                        ], spacing=6),
                        on_click=self.toggle_edit_mode,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            side=ft.BorderSide(1, ft.Colors.GREY_300),
                        ),
                        expand=True,
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("save_changes"), size=14, color=ft.Colors.WHITE),
                        ], spacing=6),
                        on_click=self.save_profile,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN_600,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        expand=True,
                    ),
                ],
                spacing=16,
            )
    
    def _build_system_info(self):
        """Build system information card"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.COMPUTER, size=20, color="#64748B"),
                                bgcolor=ft.Colors.GREY_100,
                                border_radius=10,
                                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                            ),
                            ft.Text(
                                get_text("system_information"),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.STORE, size=18, color="#64748B"),
                            width=32,
                        ),
                        ft.Column([
                            ft.Text(get_text("app_name"), size=11, color="#94A3B8"),
                            ft.Text("JP Auto Repair System", size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ], spacing=2, expand=True),
                    ], spacing=8),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color="#64748B"),  # Changed from VERSION
                            width=32,
                        ),
                        ft.Column([
                            ft.Text(get_text("version"), size=11, color="#94A3B8"),
                            ft.Text("2.0.0", size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ], spacing=2, expand=True),
                    ], spacing=8),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.CALENDAR_TODAY, size=18, color="#64748B"),
                            width=32,
                        ),
                        ft.Column([
                            ft.Text(get_text("login_date"), size=11, color="#94A3B8"),
                            ft.Text(datetime.now().strftime("%d/%m/%Y %H:%M"), size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ], spacing=2, expand=True),
                    ], spacing=8),
                ]),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            ),
            elevation=2,
        )
    
    def toggle_edit_mode(self, e):
        """Toggle edit mode"""
        self.is_editing = not self.is_editing
        # Rebuild the page
        self.page.clean()
        self.page.add(self.build())
        self.page.update()
    
    def save_profile(self, e):
        """Save user profile changes"""
        new_fullname = self.fullname_field.value.strip()
        
        if not new_fullname:
            self.show_snack_bar(get_text("please_enter_fullname"), is_error=True)
            return
        
        try:
            # Update user profile via API
            result = self.client.update_user_profile({
                "fullname": new_fullname
            })
            
            if result:
                # Update local user data
                self.user['fullname'] = new_fullname
                self.show_snack_bar(get_text("profile_updated_success"), is_error=False)
                self.is_editing = False
                self.page.clean()
                self.page.add(self.build())
                self.page.update()
            else:
                self.show_snack_bar(get_text("update_failed"), is_error=True)
        except Exception as ex:
            print(f"Error saving profile: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def show_change_password_dialog(self, e):
        """Show change password dialog"""
        # Password fields
        current_password_field = ft.TextField(
            label=get_text("current_password"),
            password=True,
            can_reveal_password=True,
            border_radius=12,
            prefix_icon=ft.Icons.LOCK,
        )
        
        new_password_field = ft.TextField(
            label=get_text("new_password"),
            password=True,
            can_reveal_password=True,
            border_radius=12,
            prefix_icon=ft.Icons.LOCK_OPEN,
        )
        
        confirm_password_field = ft.TextField(
            label=get_text("confirm_password"),
            password=True,
            can_reveal_password=True,
            border_radius=12,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
        )
        
        def change_password(e):
            current_pw = current_password_field.value
            new_pw = new_password_field.value
            confirm_pw = confirm_password_field.value
            
            if not current_pw or not new_pw or not confirm_pw:
                self.show_snack_bar(get_text("please_fill_all_fields"), is_error=True)
                return
            
            if new_pw != confirm_pw:
                self.show_snack_bar(get_text("passwords_do_not_match"), is_error=True)
                return
            
            if len(new_pw) < 4:
                self.show_snack_bar(get_text("password_too_short"), is_error=True)
                return
            
            try:
                result = self.client.change_password({
                    "current_password": current_pw,
                    "new_password": new_pw
                })
                
                if result:
                    dialog.open = False
                    self.show_snack_bar(get_text("password_changed_success"), is_error=False)
                else:
                    self.show_snack_bar(get_text("current_password_incorrect"), is_error=True)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.Colors.WHITE,
            title=ft.Text(
                get_text("change_password"),
                size=20,
                weight=ft.FontWeight.BOLD,
                color="#1E293B",
            ),
            content=ft.Container(
                content=ft.Column([
                    current_password_field,
                    ft.Container(height=8),
                    new_password_field,
                    ft.Container(height=8),
                    confirm_password_field,
                ]),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                width=400,
            ),
            actions=[
                ft.TextButton(
                    get_text("cancel"),
                    on_click=lambda e: self.close_dialog(dialog),
                    style=ft.ButtonStyle(color="#64748B"),
                ),
                ft.ElevatedButton(
                    get_text("change"),
                    on_click=change_password,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()
    
    def _get_role_text(self, role):
        """Convert role to display text"""
        roles = {
            "admin": get_text("role_admin"),
            "manager": get_text("role_manager"),
            "technician": get_text("role_technician"),
            "reception": get_text("role_reception"),
            "mechanic": get_text("role_mechanic"),
            "user": get_text("role_user"),
        }
        return roles.get(role, role.capitalize())