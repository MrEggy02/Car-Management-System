# pages/Management/master_data/master_data_dialogs.py
import flet as ft
from i18n import get_text


class MasterDataDialogs:
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
    
    def show_add_dialog(self, table_type):
        """Show add dialog for brands, units, or categories"""
        if table_type == "brands":
            title = get_text("add_brand")
            label = get_text("brand_name")
            save_method = self.parent.client.add_brand
        elif table_type == "units":
            title = get_text("add_unit")
            label = get_text("unit_name")
            save_method = self.parent.client.add_unit
        else:
            title = get_text("add_category")
            label = get_text("category_name")
            save_method = self.parent.client.add_part_category
        
        name_field = ft.TextField(
            label=label,
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
                    save_method(name_field.value, status_dropdown.value)
                    self._close_dialog()
                    self.parent.load_all_data()
                    self.parent.show_snackbar(f"✅ {get_text('add_success')}")
                except Exception as err:
                    self.parent.show_snackbar(f"{get_text('error')}: {err}")
        
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
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
    
    def edit_brand(self, brand_id):
        brand = next((b for b in self.parent.brands_data if b.get('id') == brand_id), None)
        if brand:
            self._show_edit_dialog("brands", brand_id, brand.get("name"), brand.get("status"))
    
    def edit_unit(self, unit_id):
        unit = next((u for u in self.parent.units_data if u.get('id') == unit_id), None)
        if unit:
            self._show_edit_dialog("units", unit_id, unit.get("name"), unit.get("status"))
    
    def edit_category(self, category_id):
        category = next((c for c in self.parent.categories_data if c.get('id') == category_id), None)
        if category:
            self._show_edit_dialog("categories", category_id, category.get("name"), category.get("status"))
    
    def _show_edit_dialog(self, table_type, item_id, current_name, current_status):
        """Show edit dialog for any table type"""
        if table_type == "brands":
            title = get_text("edit_brand")
            label = get_text("brand_name")
            update_method = self.parent.client.update_brand
        elif table_type == "units":
            title = get_text("edit_unit")
            label = get_text("unit_name")
            update_method = self.parent.client.update_unit
        else:
            title = get_text("edit_category")
            label = get_text("category_name")
            update_method = self.parent.client.update_part_category
        
        name_field = ft.TextField(
            label=label,
            value=current_name,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
        )
        
        status_dropdown = ft.Dropdown(
            label=get_text("status"),
            value=current_status,
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
                    update_method(item_id, name_field.value, status_dropdown.value)
                    self._close_dialog()
                    self.parent.load_all_data()
                    self.parent.show_snackbar(f"✅ {get_text('edit_success')}")
                except Exception as err:
                    self.parent.show_snackbar(f"{get_text('error')}: {err}")
        
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
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
    
    def delete_brand(self, brand_id):
        self._show_delete_dialog("brands", brand_id)
    
    def delete_unit(self, unit_id):
        self._show_delete_dialog("units", unit_id)
    
    def delete_category(self, category_id):
        self._show_delete_dialog("categories", category_id)
    
    def _show_delete_dialog(self, table_type, item_id):
        """Show delete confirmation dialog"""
        if table_type == "brands":
            item_name = next((b.get('name') for b in self.parent.brands_data if b.get('id') == item_id), get_text('this_brand'))
            delete_method = self.parent.client.delete_brand
        elif table_type == "units":
            item_name = next((u.get('name') for u in self.parent.units_data if u.get('id') == item_id), get_text('this_unit'))
            delete_method = self.parent.client.delete_unit
        else:
            item_name = next((c.get('name') for c in self.parent.categories_data if c.get('id') == item_id), get_text('this_category'))
            delete_method = self.parent.client.delete_part_category
        
        def on_confirm(e):
            try:
                delete_method(item_id)
                self._close_dialog()
                self.parent.load_all_data()
                self.parent.show_snackbar(f"✅ {get_text('delete_success')}")
            except Exception as err:
                self.parent.show_snackbar(f"{get_text('error')}: {err}")
        
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
                        f"ຕ້ອງການລຶບ '{item_name}' ຫຼື ບໍ່?",
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
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                self.parent.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")