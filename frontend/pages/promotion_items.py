# pages/promotion_items.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable

from i18n import get_text


class PromotionItemsContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, 
                 promotion_id: int = None, promotion_name: str = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.promotion_id = promotion_id
        self.promotion_name = promotion_name
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.primary_light = "#E3F2FD"
        self.items = []
        self.current_tab = "parts"
        self.items_list = None
        
    def build(self):
        header = self._build_header()
        
        # Tab buttons - Fixed for Flet 0.84 (no 'color' parameter in Container)
        parts_btn = ft.Container(
            content=ft.Text(get_text("parts"), size=16, weight=ft.FontWeight.W_500, 
                          color=ft.Colors.WHITE if self.current_tab == "parts" else "#64748B"),
            padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            bgcolor=self.primary_color if self.current_tab == "parts" else ft.Colors.TRANSPARENT,
            border_radius=30,
            on_click=lambda e: self.switch_tab("parts"),
        )
        
        services_btn = ft.Container(
            content=ft.Text(get_text("services"), size=16, weight=ft.FontWeight.W_500,
                          color=ft.Colors.WHITE if self.current_tab == "services" else "#64748B"),
            padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            bgcolor=self.primary_color if self.current_tab == "services" else ft.Colors.TRANSPARENT,
            border_radius=30,
            on_click=lambda e: self.switch_tab("services"),
        )
        
        tabs_row = ft.Row([parts_btn, services_btn], spacing=10)
        
        # Add button
        add_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("add"), size=14, color=ft.Colors.WHITE),
            ], spacing=6),
            on_click=self.show_add_dialog,
            style=ft.ButtonStyle(bgcolor=self.primary_color, shape=ft.RoundedRectangleBorder(radius=10)),
        )
        
        # Search field
        self.search_field = ft.TextField(
            hint_text=f"🔍 {get_text('search')}...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.search_items,
        )
        
        # Items list
        self.items_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Content
        content = ft.Column([
            ft.Row([tabs_row, add_btn], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=16),
            self.search_field,
            ft.Container(height=16),
            self.items_list,
        ], expand=True)
        
        content_area = ft.Container(
            content=content,
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.load_data()
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=24,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("promotions"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                f"ຈັດການລາຍການ: {self.promotion_name}",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                "ເພີ່ມ/ລຶບ ສິນຄ້າ ແລະ ບໍລິການ",
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Icon(ft.Icons.LIST_ALT, size=28, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                        border_radius=15,
                        padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=32, right=32, top=20, bottom=20),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
    
    def load_data(self):
        """Load items for this promotion"""
        try:
            self.items = self.client.get_promotion_items(self.promotion_id)
            self.display_items()
        except Exception as ex:
            print(f"Error loading items: {ex}")
            self.show_snackbar(f"Error: {ex}", is_error=True)
    
    def display_items(self, search: str = ""):
        """Display items based on current tab and search"""
        if not self.items_list:
            return
            
        self.items_list.controls.clear()
        
        filtered = [i for i in self.items if i.get('item_type') == self.current_tab]
        
        if search:
            filtered = [i for i in filtered if search.lower() in i.get('item_name', '').lower()]
        
        if not filtered:
            self.items_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=48, color=ft.Colors.GREY_400),
                        ft.Text(f"ບໍ່ມີ {self.current_tab} ໃນໂປຣໂມຊັນນີ້", size=14, color="#64748B"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
            )
        else:
            for item in filtered:
                self.items_list.controls.append(self._create_item_row(item))
        
        self.page.update()
    
    def _create_item_row(self, item: dict):
        """Create a row for an item"""
        item_name = item.get('item_name', '-')
        item_price = item.get('item_price', 0)
        item_id = item.get('id')
        
        def delete_item(e):
            self.delete_item(item_id, item_name)
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(item_name, size=14, weight=ft.FontWeight.W_500),
                    ft.Text(f"{int(item_price):,} KIP", size=11, color="#64748B"),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_600,
                    icon_size=20,
                    on_click=delete_item,
                    tooltip=get_text("delete"),
                ),
            ]),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100), right=ft.BorderSide(1, ft.Colors.GREY_100), bottom=ft.BorderSide(1, ft.Colors.GREY_100), left=ft.BorderSide(1, ft.Colors.GREY_100)),
        )
    
    def delete_item(self, item_id: int, item_name: str):
        """Delete item with confirmation"""
        def confirm(e):
            try:
                self.client.delete_promotion_item(self.promotion_id, item_id)
                self.load_data()
                self.show_snackbar(f"ລຶບ {item_name} ສຳເລັດ", is_error=False)
                dialog.open = False
            except Exception as ex:
                self.show_snackbar(f"Error: {ex}", is_error=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            title=ft.Text(get_text("confirm_delete")),
            content=ft.Text(f"ທ່ານຕ້ອງການລຶບ '{item_name}' ແທ້ບໍ?"),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("delete"), on_click=confirm, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def search_items(self, e):
        self.display_items(e.control.value)
    
    def switch_tab(self, tab):
        self.current_tab = tab
        self.display_items()
    
    def show_add_dialog(self, e):
        """Show dialog to add item"""
        
        self.available_items = []
        
        search_field = ft.TextField(
            hint_text=f"ຄົ້ນຫາ...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
        )
        
        items_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=350)
        
        def load_items(search: str = ""):
            try:
                if self.current_tab == "parts":
                    items = self.client.get_available_parts_for_promotion(self.promotion_id, search)
                else:
                    items = self.client.get_available_services_for_promotion(self.promotion_id, search)
                
                items_list.controls.clear()
                self.available_items = items
                
                if not items:
                    items_list.controls.append(
                        ft.Container(
                            content=ft.Text(f"ບໍ່ພົບຂໍ້ມູນ", size=13, color="#64748B"),
                            alignment=ft.Alignment(0, 0),
                            padding=40,
                        )
                    )
                else:
                    for item in items:
                        price = item.get('sell_price') if self.current_tab == "parts" else item.get('price')
                        items_list.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Column([
                                        ft.Text(item['name'], size=14, weight=ft.FontWeight.W_500),
                                        ft.Text(f"{int(price):,} KIP", size=12, color="#64748B"),
                                    ], spacing=2, expand=True),
                                    ft.ElevatedButton(
                                        get_text("add"),
                                        bgcolor=self.primary_color,
                                        color=ft.Colors.WHITE,
                                        on_click=lambda e, iid=item['id'], iname=item['name']: add_item(iid, iname),
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                    ),
                                ]),
                                padding=10,
                                bgcolor=ft.Colors.GREY_50,
                                border_radius=10,
                            )
                        )
                
                self.page.update()
            except Exception as ex:
                print(f"Error loading available items: {ex}")
                self.show_snackbar(f"Error: {ex}", is_error=True)
        
        def add_item(item_id: int, item_name: str):
            try:
                self.client.add_promotion_item(self.promotion_id, self.current_tab, item_id)
                add_dialog.open = False
                self.load_data()
                self.show_snackbar(f"ເພີ່ມ {item_name} ສຳເລັດ", is_error=False)
            except Exception as ex:
                self.show_snackbar(f"Error: {ex}", is_error=True)
        
        search_field.on_change = lambda e: load_items(e.control.value)
        
        load_items()
        
        add_dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            title=ft.Text(f"ເພີ່ມ {get_text('parts') if self.current_tab == 'parts' else get_text('services')}", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    search_field,
                    ft.Container(height=10),
                    items_list,
                ], spacing=0),
                width=450,
                height=450,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(add_dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(add_dialog)
        add_dialog.open = True
        self.page.update()
    
    def show_snackbar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()