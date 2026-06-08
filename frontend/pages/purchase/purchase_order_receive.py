# pages/purchase/purchase_order_create.py - 修复版本

import flet as ft
from typing import Dict, Callable, List
from i18n import get_text


class PurchaseOrderCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.selected_supplier = None
        self.items = []  # List of {part_id, part_name, qty, unit_cost}
        self.parts_list = []
        self.suppliers_list = []
        
    def build(self):
        # Load data
        self.load_suppliers()
        self.load_parts()
        
        header = self._build_header()
        content = self._build_content()
        
        main_content = ft.Container(
            content=ft.Column([header, content], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=24,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("purchase_order_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("create_purchase_order"),
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
    
    def load_suppliers(self):
        try:
            self.suppliers_list = self.client.get_suppliers()
            print(f"Loaded {len(self.suppliers_list)} suppliers")
        except Exception as ex:
            print(f"Error loading suppliers: {ex}")
            self.suppliers_list = []
    
    def load_parts(self):
        try:
            self.parts_list = self.client.get_parts()
            print(f"Loaded {len(self.parts_list)} parts")
        except Exception as ex:
            print(f"Error loading parts: {ex}")
            self.parts_list = []
    
    def _build_content(self):
        # Supplier Dropdown
        supplier_options = [
            ft.dropdown.Option(str(s.get('id')), s.get('name', '-'))
            for s in self.suppliers_list
        ]
        
        self.supplier_dropdown = ft.Dropdown(
            label=get_text("supplier"),
            options=supplier_options,
            width=400,
            border_radius=12,
            on_change=self.on_supplier_change,
        )
        
        # Part Selection
        part_options = [
            ft.dropdown.Option(str(p.get('id')), f"{p.get('name', '-')} - {p.get('sell_price', 0):,.0f} KIP")
            for p in self.parts_list
        ]
        
        self.part_dropdown = ft.Dropdown(
            label=get_text("select_part"),
            options=part_options,
            width=300,
            border_radius=12,
        )
        
        self.qty_field = ft.TextField(
            label=get_text("quantity"),
            value="1",
            width=120,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=12,
        )
        
        self.unit_cost_field = ft.TextField(
            label=get_text("unit_cost"),
            value="0",
            width=150,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=12,
        )
        
        def add_item(e):
            if not self.part_dropdown.value:
                self.show_snack_bar(get_text("select_part_first"), is_error=True)
                return
            
            part_id = int(self.part_dropdown.value)
            selected_part = next((p for p in self.parts_list if p.get('id') == part_id), None)
            
            if not selected_part:
                return
            
            qty = int(self.qty_field.value) if self.qty_field.value else 1
            unit_cost = float(self.unit_cost_field.value) if self.unit_cost_field.value else selected_part.get('sell_price', 0)
            
            # Check if part already added
            existing = next((i for i in self.items if i['part_id'] == part_id), None)
            if existing:
                existing['qty'] += qty
                existing['total'] = existing['qty'] * existing['unit_cost']
            else:
                self.items.append({
                    'part_id': part_id,
                    'part_name': selected_part.get('name', '-'),
                    'qty': qty,
                    'unit_cost': unit_cost,
                    'total': qty * unit_cost
                })
            
            # Clear fields
            self.part_dropdown.value = None
            self.qty_field.value = "1"
            self.unit_cost_field.value = "0"
            
            self.update_items_list()
            self.update_total()
        
        add_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, size=18),
                ft.Text(get_text("add_item")),
            ], spacing=6),
            on_click=add_item,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )
        
        # Items List
        self.items_list_view = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=300)
        
        # Total amount
        self.total_text = ft.Text("0 KIP", size=18, weight=ft.FontWeight.BOLD, color=self.primary_color)
        
        # Create button
        create_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("create"), size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ], spacing=6),
            on_click=self.create_purchase_order,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            height=50,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(get_text("basic_info"), size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            self.supplier_dropdown,
                        ]),
                        padding=20,
                    ),
                    elevation=2,
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(get_text("items"), size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Row([self.part_dropdown, self.qty_field, self.unit_cost_field, add_button]),
                            ft.Container(height=20),
                            ft.Text(get_text("item_list"), size=14, weight=ft.FontWeight.W_500),
                            self.items_list_view,
                            ft.Divider(),
                            ft.Row([
                                ft.Text(get_text("total_amount"), size=16, weight=ft.FontWeight.W_500),
                                ft.Container(expand=True),
                                self.total_text,
                            ]),
                        ]),
                        padding=20,
                    ),
                    elevation=2,
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Row([create_button], alignment=ft.MainAxisAlignment.END),
            ], spacing=20),
            padding=ft.padding.all(32),
            expand=True,
        )
    
    def on_supplier_change(self, e):
        if self.supplier_dropdown.value:
            self.selected_supplier = int(self.supplier_dropdown.value)
    
    def update_items_list(self):
        self.items_list_view.controls.clear()
        
        if not self.items:
            self.items_list_view.controls.append(
                ft.Text(get_text("no_items_added"), size=13, color="#64748B")
            )
            self.page.update()
            return
        
        for i, item in enumerate(self.items):
            def delete_item(e, idx=i):
                self.items.pop(idx)
                self.update_items_list()
                self.update_total()
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Text(item['part_name'], expand=True, size=13),
                    ft.Text(f"x{item['qty']}", size=13, color="#64748B"),
                    ft.Text(f"{item['unit_cost']:,.0f}", size=13, color="#64748B"),
                    ft.Text(f"{item['total']:,.0f} KIP", size=13, weight=ft.FontWeight.W_500, color=self.primary_color),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=18,
                        icon_color=ft.Colors.RED_400,
                        on_click=delete_item,
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=8, horizontal=10),
                bgcolor=ft.Colors.GREY_50,
                border_radius=8,
            )
            self.items_list_view.controls.append(item_row)
        
        self.page.update()
    
    def update_total(self):
        total = sum(item['total'] for item in self.items)
        self.total_text.value = f"{total:,.0f} KIP"
        self.page.update()
    
    def create_purchase_order(self, e):
        if not self.selected_supplier:
            self.show_snack_bar(get_text("select_supplier"), is_error=True)
            return
        
        if not self.items:
            self.show_snack_bar(get_text("add_items_first"), is_error=True)
            return
        
        # Prepare items for API
        items_data = []
        for item in self.items:
            items_data.append({
                'part_id': item['part_id'],
                'qty': item['qty'],
                'unit_cost': item['unit_cost']
            })
        
        print(f"DEBUG: Creating PO with supplier_id: {self.selected_supplier}")
        print(f"DEBUG: Items: {items_data}")
        
        try:
            result = self.client.create_purchase_order(self.selected_supplier, items_data)
            print(f"DEBUG: Create PO result: {result}")
            
            if result and result.get('id'):
                self.show_success_popup(result.get('po_no'))
            else:
                self.show_snack_bar(get_text("create_failed"), is_error=True)
        except Exception as ex:
            print(f"Error creating PO: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
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
                            f"{get_text('po_no')}: {po_no}",
                            size=14,
                            color="#64748B",
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
                    on_click=lambda e, popup=popup: self.go_to_list(popup),
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
        self.page.update()
        self.navigate("purchase_order_list")
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()