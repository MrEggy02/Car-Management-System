import flet as ft
from i18n import get_text


class BrandsDialogs:
    def __init__(self, parent):
        self.parent = parent
        self.current_dialog = None
    
    def create_status_badge(self, status):
        """Create status badge widget"""
        if status == "active":
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color="#2E7D32"),
                    ft.Text(get_text("status_active"), size=10, color="#2E7D32"),
                ], spacing=4),
                bgcolor="#E8F5E9",
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
            )
        else:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color="#DC2626"),
                    ft.Text(get_text("status_inactive"), size=10, color="#DC2626"),
                ], spacing=4),
                bgcolor="#FFEEEE",
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
            )
    
    def show_add_dialog(self):
        """Show add brand dialog"""
        name_field = ft.TextField(
            label=get_text("brand_name"),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
        )
        
        status_dropdown = ft.Dropdown(
            label=get_text("status"),
            value="active",
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            options=[
                ft.dropdown.Option("active", get_text("status_active")),
                ft.dropdown.Option("inactive", get_text("status_inactive")),
            ],
        )
        
        def save(e):
            if name_field.value:
                try:
                    self.parent.client.add_brand(name_field.value, status_dropdown.value)
                    self._close_dialog()
                    self.parent.load_brands()
                    self.parent.show_snackbar(f"✅ {get_text('add_success')}")
                except Exception as err:
                    self.parent.show_snackbar(f"{get_text('error')}: {err}", is_error=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=14),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.ADD, size=22, color=ft.Colors.WHITE),
                            bgcolor=self.parent.primary_color,
                            border_radius=10,
                            padding=ft.padding.all(6),
                        ),
                        ft.Text(get_text("add_brand"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.symmetric(horizontal=18, vertical=14),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    name_field,
                    ft.Container(height=8),
                    status_dropdown,
                ], spacing=0),
                padding=ft.padding.all(18),
                width=400,
                height=180,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B"),
                            on_click=self._close_dialog,
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), color=ft.Colors.WHITE),
                            on_click=save,
                            style=ft.ButtonStyle(bgcolor=self.parent.primary_color, elevation=0),
                        ),
                    ], spacing=10, alignment=ft.MainAxisAlignment.END),
                    padding=ft.padding.symmetric(horizontal=18, vertical=12),
                    border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)
    
    def show_edit_dialog(self, brand_id):
        """Show edit brand dialog"""
        brand = next((b for b in self.parent.brands_data if b.get('id') == brand_id), None)
        if not brand:
            return
        
        name_field = ft.TextField(
            label=get_text("brand_name"),
            value=brand.get("name"),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
        )
        
        status_dropdown = ft.Dropdown(
            label=get_text("status"),
            value=brand.get("status", "active"),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            options=[
                ft.dropdown.Option("active", get_text("status_active")),
                ft.dropdown.Option("inactive", get_text("status_inactive")),
            ],
        )
        
        def save(e):
            if name_field.value:
                try:
                    self.parent.client.update_brand(brand_id, name_field.value, status_dropdown.value)
                    self._close_dialog()
                    self.parent.load_brands()
                    self.parent.show_snackbar(f"✅ {get_text('edit_success')}")
                except Exception as err:
                    self.parent.show_snackbar(f"{get_text('error')}: {err}", is_error=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=14),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=22, color=ft.Colors.WHITE),
                            bgcolor=self.parent.primary_color,
                            border_radius=10,
                            padding=ft.padding.all(6),
                        ),
                        ft.Text(get_text("edit_brand"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.symmetric(horizontal=18, vertical=14),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    name_field,
                    ft.Container(height=8),
                    status_dropdown,
                ], spacing=0),
                padding=ft.padding.all(18),
                width=400,
                height=180,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B"),
                            on_click=self._close_dialog,
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), color=ft.Colors.WHITE),
                            on_click=save,
                            style=ft.ButtonStyle(bgcolor=self.parent.primary_color, elevation=0),
                        ),
                    ], spacing=10, alignment=ft.MainAxisAlignment.END),
                    padding=ft.padding.symmetric(horizontal=18, vertical=12),
                    border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)
    
    def show_delete_dialog(self, brand_id):
        """Show delete confirmation dialog"""
        brand = next((b for b in self.parent.brands_data if b.get('id') == brand_id), None)
        if not brand:
            return
        
        brand_name = brand.get('name', get_text('this_brand'))
        
        def on_confirm(e):
            try:
                self.parent.client.delete_brand(brand_id)
                self._close_dialog()
                self.parent.load_brands()
                self.parent.show_snackbar(f"✅ {get_text('delete_success')}")
            except Exception as err:
                self.parent.show_snackbar(f"{get_text('error')}: {err}", is_error=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=14),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, size=22, color=ft.Colors.WHITE),
                            bgcolor="#DC2626",
                            border_radius=10,
                            padding=ft.padding.all(6),
                        ),
                        ft.Text(get_text("confirm_delete"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=10,
                ),
                padding=ft.padding.symmetric(horizontal=18, vertical=14),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=40, color="#DC2626"),
                    ft.Container(height=8),
                    ft.Text(
                        f"ຕ້ອງການລຶບ '{brand_name}' ຫຼື ບໍ່?",
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color="#1E293B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        get_text("delete_warning"),
                        size=12,
                        color="#64748B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=ft.padding.all(20),
                width=320,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B"),
                            on_click=self._close_dialog,
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("delete"), color=ft.Colors.WHITE),
                            on_click=on_confirm,
                            style=ft.ButtonStyle(bgcolor="#DC2626", elevation=0),
                        ),
                    ], spacing=10, alignment=ft.MainAxisAlignment.END),
                    padding=ft.padding.symmetric(horizontal=18, vertical=12),
                    border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)
    
    def _open_dialog(self, dialog):
        """Open dialog"""
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                if self.current_dialog in self.parent.page.overlay:
                    self.parent.page.overlay.remove(self.current_dialog)
            self.current_dialog = dialog
            self.parent.page.overlay.append(dialog)
            dialog.open = True
            self.parent.page.update()
        except Exception as e:
            print(f"DEBUG: Error opening dialog: {e}")
    
    def _close_dialog(self, e=None):
        """Close dialog"""
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                self.parent.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")