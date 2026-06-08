# pages/purchase/purchase_order_create.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable, List

from i18n import get_text


class PurchaseOrderCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable,
                 content_container: ft.Container = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.content_container = content_container
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.suppliers = []
        self.parts = []
        self.selected_supplier_id = None
        self.items = []
        self.items_list = None
        self.parts_search = None
        self.parts_results = None
        self.supplier_dropdown = None
        self.total_text = None
        
    def build(self):
        header = self._build_header()
        self.load_data()
        
        content = self._build_content()
        
        scrollable_content = ft.Column(
            [content],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.padding.all(32),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    
                    ft.Column(
                        [
                            ft.Text(
                                get_text("purchase_order_create_title"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=12, horizontal=24),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
            
        )
    
    def load_data(self):
        try:
            self.suppliers = self.client.get_suppliers()
            self.parts = self.client.get_parts()
            self.page.update()
        except Exception as ex:
            print(f"Error loading data: {ex}")
    
    def _build_content(self):
        # Supplier Dropdown
        supplier_options = []
        supplier_options.append(ft.dropdown.Option("", f"--- {get_text('select_supplier')} ---"))
        for supplier in self.suppliers:
            supplier_options.append(
                ft.dropdown.Option(
                    str(supplier.get('id')),
                    supplier.get('name', '')
                )
            )
        
        self.supplier_dropdown = ft.Dropdown(
            label=get_text("supplier"),
            options=supplier_options,
            expand=True,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
        )
        self.supplier_dropdown.on_change = self.on_supplier_change
        
        # Parts Search
        self.parts_search = ft.TextField(
            hint_text=get_text("search_part_to_order"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
        )
        self.parts_search.on_change = self.search_parts
        
        self.parts_results = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=200)
        
        # Items List
        self.items_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        # Total Display
        self.total_text = ft.Text("0 KIP", size=18, weight=ft.FontWeight.BOLD, color=self.primary_color)
        
        supplier_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.BUSINESS, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("supplier_info"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    self.supplier_dropdown,
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        parts_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.INVENTORY, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("add_parts"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    self.parts_search,
                    ft.Container(height=12),
                    ft.Text(get_text("search_results"), size=12, color="#64748B"),
                    ft.Container(height=8),
                    self.parts_results,
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        items_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.LIST, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("items_to_order"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=8),
                    self.items_list,
                    ft.Container(height=8),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Row([
                        ft.Text(f"{get_text('total_amount')}:", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        self.total_text,
                    ]),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        def create_po(e):
            if not self.supplier_dropdown.value or self.supplier_dropdown.value == "":
                self.show_snack_bar(get_text("please_select_supplier_first"), is_error=True)
                return
            
            if not self.items:
                self.show_snack_bar(get_text("please_add_at_least_one_item"), is_error=True)
                return
            
            items_data = []
            for item in self.items:
                items_data.append({
                    "part_id": item['part_id'],
                    "qty": item['qty'],
                    "unit_cost": item['unit_cost']
                })
            
            try:
                result = self.client.create_purchase_order(
                    supplier_id=int(self.supplier_dropdown.value),
                    items=items_data
                )
                if result:
                    self.show_success_popup(result.get('po_no'))
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("save_purchase_order"), size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ], spacing=6),
            on_click=create_po,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            height=50,
        )
        
        return ft.Column([
            supplier_card,
            parts_section,
            items_section,
            ft.Container(content=create_btn, padding=ft.padding.only(top=20)),
        ], spacing=20)
    
    def on_supplier_change(self, e):
        self.selected_supplier_id = int(e.control.value) if e.control.value else None
        self.search_parts(None)
        self.page.update()
    
    def search_parts(self, e):
        keyword = self.parts_search.value.lower() if self.parts_search.value else ""
        self.parts_results.controls.clear()
        
        results = self.parts
        if keyword:
            results = [p for p in results if keyword in p.get("name", "").lower() or keyword in p.get("part_code", "").lower()]
        
        for part in results[:20]:
            part_id = part.get('id')
            part_code = part.get('part_code', '')
            part_name = part.get('name', '')
            current_stock = part.get('stock_qty', 0)
            min_stock = part.get('min_stock', 5)
            
            add_btn = ft.ElevatedButton(
                get_text("add_to_order"),
                on_click=lambda e, pid=part_id, pcode=part_code, pname=part_name, pstock=current_stock: self.show_add_item_dialog(pid, pcode, pname, pstock),
                style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE, padding=ft.padding.symmetric(horizontal=12, vertical=4)),
            )
            
            item = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(f"{part_code} - {part_name}", weight=ft.FontWeight.W_500, size=13),
                        ft.Text(f"{get_text('current_stock')}: {current_stock} | {get_text('min_stock')}: {min_stock}", size=10, color="#64748B"),
                    ], expand=True),
                    add_btn,
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=6, horizontal=10),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
            )
            self.parts_results.controls.append(item)
        
        self.page.update()
    
    def show_add_item_dialog(self, part_id, part_code, part_name, current_stock):
        qty_field = ft.TextField(
            label=get_text("order_qty"),
            value="1",
            width=200,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        
        cost_field = ft.TextField(
            label=get_text("unit_cost"),
            value="0",
            width=200,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        
        def confirm_add(e):
            qty = int(qty_field.value) if qty_field.value else 1
            unit_cost = float(cost_field.value) if cost_field.value else 0
            
            if qty <= 0:
                self.show_snack_bar(get_text("quantity_must_be_positive"), is_error=True)
                return
            
            if unit_cost <= 0:
                self.show_snack_bar(get_text("please_enter_unit_cost"), is_error=True)
                return
            
            # Check if part already in items
            for i, item in enumerate(self.items):
                if item['part_id'] == part_id:
                    # Update existing
                    self.items[i]['qty'] = qty
                    self.items[i]['unit_cost'] = unit_cost
                    self.items[i]['total'] = qty * unit_cost
                    dialog.open = False
                    self.update_items_display()
                    self.show_snack_bar(get_text("part_updated_success"), is_error=False)
                    return
            
            # Add new item
            self.items.append({
                'part_id': part_id,
                'part_code': part_code,
                'part_name': part_name,
                'qty': qty,
                'unit_cost': unit_cost,
                'total': qty * unit_cost
            })
            dialog.open = False
            self.update_items_display()
            self.show_snack_bar(get_text("part_added_success"), is_error=False)
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"{get_text('order_qty')}: {part_code} - {part_name}"),
            content=ft.Container(
                content=ft.Column([
                    qty_field,
                    cost_field,
                ]),
                padding=ft.padding.all(20),
                width=300,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("add_to_order"), on_click=confirm_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def update_items_display(self):
        self.items_list.controls.clear()
        total = 0
        
        for i, item in enumerate(self.items):
            total += item['total']
            item_row = ft.Container(
                content=ft.Row([
                    ft.Text(f"{item['qty']}x", size=13, weight=ft.FontWeight.W_500, color=self.primary_color, width=50),
                    ft.Text(f"{item['part_code']} - {item['part_name']}", size=13, expand=True),
                    ft.Text(f"{int(item['unit_cost']):,}", size=12, color="#64748B"),
                    ft.Text(f"{int(item['total']):,} KIP", size=13, weight=ft.FontWeight.BOLD, color="#1E293B", width=130),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        tooltip=get_text("delete"),
                        on_click=lambda e, idx=i: self.remove_item(idx),
                    ),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=6, horizontal=10),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
            )
            self.items_list.controls.append(item_row)
        
        self.total_text.value = f"{int(total):,} KIP"
        self.page.update()
    
    def remove_item(self, index):
        removed = self.items.pop(index)
        self.update_items_display()
        self.show_snack_bar(f"{get_text('part_removed')}: {removed['part_name']}", is_error=False)
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_success_popup(self, po_no):
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.Colors.WHITE,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN_600),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Text(
                            get_text("po_created_success"),
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            f"{get_text('po_number')}: {po_no}",
                            size=14,
                            color="#64748B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            get_text("go_to_list_message"),
                            size=12,
                            color="#94A3B8",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(24),
                width=350,
            ),
            actions=[
                ft.ElevatedButton(
                    get_text("go_to_list"),
                    on_click=lambda e: self.go_to_list(popup),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def go_to_list(self, popup):
        popup.open = False
        self.navigate("purchase_order_list")
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()