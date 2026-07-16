# Management/units/units_dialogs.py
import flet as ft
from i18n import get_text


class UnitsDialogs:
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
                padding=ft.Padding(left=8, right=8, top=2, bottom=2),
            )
        else:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color="#DC2626"),
                    ft.Text(get_text("status_inactive"), size=10, color="#DC2626"),
                ], spacing=4),
                bgcolor="#FFEEEE",
                border_radius=12,
                padding=ft.Padding(left=8, right=8, top=2, bottom=2),
            )
    
    def show_add_dialog(self):
        """Show add unit dialog with validation"""
        
        # Error label
        name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        
        name_field = ft.TextField(
            label=get_text("unit_name"),
            hint_text="ເຊັ່ນ: ຊິ້ນ, ກິໂລ, ລິດ",
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            height=38,
            text_size=12,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        )
        
        status_dropdown = ft.Dropdown(
            label=get_text("status"),
            value="active",
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            height=38,
            options=[
                ft.dropdown.Option("active", get_text("status_active")),
                ft.dropdown.Option("inactive", get_text("status_inactive")),
            ],
        )
        
        def validate_fields():
            is_valid = True
            
            if not name_field.value or not name_field.value.strip():
                name_error.value = get_text("please_enter_name")
                name_error.visible = True
                is_valid = False
            else:
                name_error.visible = False
            
            name_field.update()
            name_error.update()
            
            return is_valid
        
        def save(e):
            if not validate_fields():
                return
            
            try:
                self.parent.client.add_unit(name_field.value.strip(), status_dropdown.value)
                self._close_dialog()
                self.parent.load_units()
                self.parent.show_snackbar(get_text("add_success"), "success")
            except Exception as err:
                self.parent.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                            bgcolor=self.parent.primary_color,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text("add_unit"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Column([
                        name_field,
                        name_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    status_dropdown,
                ], spacing=0),
                padding=ft.Padding(left=14, right=14, top=12, bottom=8),
                width=360,
                height=150,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                            on_click=self._close_dialog,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), size=13, color=ft.Colors.WHITE),
                            on_click=save,
                            style=ft.ButtonStyle(
                                bgcolor=self.parent.primary_color,
                                elevation=0,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                            ),
                        ),
                    ], spacing=6, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)
    
    def show_edit_dialog(self, unit_id):
        """Show edit unit dialog with validation"""
        unit = next((u for u in self.parent.units_data if u.get('id') == unit_id), None)
        if not unit:
            return
        
        # Error label
        name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        
        name_field = ft.TextField(
            label=get_text("unit_name"),
            value=unit.get("name"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            height=38,
            text_size=12,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        )
        
        status_dropdown = ft.Dropdown(
            label=get_text("status"),
            value=unit.get("status", "active"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            height=38,
            options=[
                ft.dropdown.Option("active", get_text("status_active")),
                ft.dropdown.Option("inactive", get_text("status_inactive")),
            ],
        )
        
        def validate_fields():
            is_valid = True
            
            if not name_field.value or not name_field.value.strip():
                name_error.value = get_text("please_enter_name")
                name_error.visible = True
                is_valid = False
            else:
                name_error.visible = False
            
            name_field.update()
            name_error.update()
            
            return is_valid
        
        def save(e):
            if not validate_fields():
                return
            
            try:
                self.parent.client.update_unit(unit_id, name_field.value.strip(), status_dropdown.value)
                self._close_dialog()
                self.parent.load_units()
                self.parent.show_snackbar(get_text("edit_success"), "success")
            except Exception as err:
                self.parent.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=18, color=ft.Colors.WHITE),
                            bgcolor=self.parent.primary_color,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text("edit_unit"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Column([
                        name_field,
                        name_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    status_dropdown,
                ], spacing=0),
                padding=ft.Padding(left=14, right=14, top=12, bottom=8),
                width=360,
                height=150,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                            on_click=self._close_dialog,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), size=13, color=ft.Colors.WHITE),
                            on_click=save,
                            style=ft.ButtonStyle(
                                bgcolor=self.parent.primary_color,
                                elevation=0,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                            ),
                        ),
                    ], spacing=6, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)
    
    def show_delete_dialog(self, unit_id):
        """Show delete confirmation dialog"""
        unit = next((u for u in self.parent.units_data if u.get('id') == unit_id), None)
        if not unit:
            return
        
        unit_name = unit.get('name', get_text('this_unit'))
        
        def on_confirm(e):
            try:
                self.parent.client.delete_unit(unit_id)
                self._close_dialog()
                self.parent.load_units()
                self.parent.show_snackbar(get_text("delete_success"), "success")
            except Exception as err:
                self.parent.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, size=18, color=ft.Colors.WHITE),
                            bgcolor="#DC2626",
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text("confirm_delete"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=32, color="#DC2626"),
                    ft.Container(height=4),
                    ft.Text(
                        f"ຕ້ອງການລຶບ '{unit_name}' ຫຼື ບໍ່?",
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
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                width=280,
                height=150,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                            on_click=self._close_dialog,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("delete"), size=13, color=ft.Colors.WHITE),
                            on_click=on_confirm,
                            style=ft.ButtonStyle(
                                bgcolor="#DC2626",
                                elevation=0,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                            ),
                        ),
                    ], spacing=6, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
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