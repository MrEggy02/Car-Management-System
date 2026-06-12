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
        self.success_color = "#10B981"
        self.suppliers = []
        self.parts = []
        self.selected_supplier_id = None
        self.items = []
        self.items_list = None
        self.parts_search = None
        self.parts_results = None
        self.supplier_dropdown = None
        self.total_text = None
        self.content_area = None
        
    def build(self):
        # Header with Create Button in right side
        create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("save_purchase_order"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=8),
            on_click=self.create_purchase_order,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=0,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
        )
        
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=20,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("purchase_order_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("purchase_order_create_title"),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("purchase_order_create_subtitle"),
                                size=12,
                                color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    create_btn,
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=14, horizontal=24),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
        
        # Content area with loading
        self.content_area = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.padding.all(40),
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Load data
        self.load_data()
        
        return main_content
    
    def load_data(self):
        try:
            self.suppliers = self.client.get_suppliers()
            self.parts = self.client.get_parts()
            self._build_form()
        except Exception as ex:
            print(f"Error loading data: {ex}")
            self._show_error(str(ex))
    
    def _show_error(self, message):
        error_content = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                    ft.Text(f"{get_text('error')}: {message}", size=14, color=ft.Colors.RED_600),
                    ft.Container(height=16),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("retry")),
                        on_click=lambda e: self.load_data(),
                        style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                padding=ft.padding.all(40),
            ),
            elevation=2,
        )
        self.content_area.content = error_content
        self.content_area.update()
    
    def _build_form(self):
        # Supplier Dropdown
        supplier_options = [
            ft.dropdown.Option("", f"-- {get_text('select_supplier')} --")
        ]
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
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        )
        self.supplier_dropdown.on_change = self.on_supplier_change
        
        # Parts Search
        self.parts_search = ft.TextField(
            hint_text=get_text("search_part_to_order"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
        )
        self.parts_search.on_change = self.search_parts
        
        self.parts_results = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=250)
        
        # Items List
        self.items_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=200)
        
        # Total Display
        self.total_text = ft.Text("0 KIP", size=16, weight=ft.FontWeight.BOLD, color=self.success_color)
        
        # Supplier Card
        supplier_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.BUSINESS, size=18, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("supplier_info"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=12),
                    self.supplier_dropdown,
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
        
        # Parts Section Card
        parts_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.INVENTORY, size=18, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("add_parts"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
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
            margin=ft.margin.only(bottom=16),
        )
        
        # Items Section Card
        items_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.LIST_ALT, size=18, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("items_to_order"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(get_text("total_amount") + ":", size=12, color="#64748B"),
                                    self.total_text,
                                ], spacing=6),
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                bgcolor=ft.Colors.GREY_50,
                                border_radius=16,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=8),
                    self.items_list,
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
        
        # Update content area
        scrollable_content = ft.Column([
            supplier_card,
            parts_section,
            items_section,
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        self.content_area.content = scrollable_content
        self.content_area.update()
    
    def on_supplier_change(self, e):
        self.selected_supplier_id = int(e.control.value) if e.control.value else None
        self.search_parts(None)
        self.page.update()
    
    def search_parts(self, e):
        keyword = self.parts_search.value.lower() if self.parts_search.value else ""
        self.parts_results.controls.clear()
        
        results = self.parts
        if keyword:
            results = [p for p in results if keyword in p.get("name", "").lower()]
        
        for part in results[:20]:
            part_id = part.get('id')
            part_name = part.get('name', '')
            current_stock = part.get('stock_qty', 0)
            min_stock = part.get('min_stock', 5)
            
            add_btn = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("add"), size=12, color=ft.Colors.WHITE),
                ], spacing=4),
                on_click=lambda e, pid=part_id, pname=part_name: self.show_add_item_dialog(pid, pname),
                style=ft.ButtonStyle(
                    bgcolor=self.primary_color,
                    shape=ft.RoundedRectangleBorder(radius=6),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                ),
            )
            
            # Stock status color
            if current_stock <= min_stock:
                stock_color = "#EF4444"
                stock_text = f"⚠️ {get_text('low_stock')}"
            else:
                stock_color = "#10B981"
                stock_text = f"✓ {get_text('stock')}: {current_stock}"
            
            item = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.INVENTORY_2, size=20, color=self.primary_color),
                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                        border_radius=8,
                        padding=ft.padding.all(8),
                    ),
                    ft.Column([
                        ft.Text(part_name, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ft.Row([
                            ft.Text(stock_text, size=10, color=stock_color),
                        ], spacing=8),
                    ], spacing=2, expand=True),
                    add_btn,
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.GREY_200),
            )
            self.parts_results.controls.append(item)
        
        if not results:
            self.parts_results.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=40, color="#CBD5E1"),
                        ft.Text(get_text("no_parts_found"), size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.padding.all(40),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        self.page.update()
    
    def show_add_item_dialog(self, part_id, part_name):
        qty_field = ft.TextField(
            label=get_text("order_qty"),
            value="1",
            width=200,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )
        
        # Find current sell price as default
        selected_part = next((p for p in self.parts if p.get('id') == part_id), None)
        default_cost = selected_part.get('sell_price', 0) if selected_part else 0
        
        cost_field = ft.TextField(
            label=get_text("unit_cost"),
            value=str(default_cost),
            width=200,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
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
                'part_name': part_name,
                'qty': qty,
                'unit_cost': unit_cost,
                'total': qty * unit_cost
            })
            dialog.open = False
            self.update_items_display()
            self.show_snack_bar(f"✓ {get_text('added')}: {part_name}", is_error=False)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.INVENTORY, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            get_text("add_to_order"),
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(part_name, size=14, weight=ft.FontWeight.W_500, color=self.primary_color),
                    ft.Container(height=12),
                    qty_field,
                    ft.Container(height=12),
                    cost_field,
                ]),
                padding=ft.padding.all(24),
                width=350,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog), style=ft.ButtonStyle(color="#64748B")),
                ft.ElevatedButton(get_text("add"), on_click=confirm_add, style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def _open_dialog(self, dialog):
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def update_items_display(self):
        self.items_list.controls.clear()
        total = 0
        
        if not self.items:
            empty_row = ft.Container(
                content=ft.Text(get_text("no_items_added"), size=13, color="#94A3B8"),
                padding=ft.padding.all(30),
                alignment=ft.Alignment(0, 0),
            )
            self.items_list.controls.append(empty_row)
            self.total_text.value = "0 KIP"
            self.page.update()
            return
        
        for idx, item in enumerate(self.items):
            total += item['total']
            bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(f"{item['qty']}x", size=14, weight=ft.FontWeight.W_700, color=self.primary_color),
                        width=50,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column([
                        ft.Text(item['part_name'], size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ft.Text(f"{get_text('unit_cost')}: {int(item['unit_cost']):,} KIP", size=11, color="#64748B"),
                    ], spacing=2, expand=True),
                    ft.Text(f"{int(item['total']):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.success_color, width=120, text_align=ft.TextAlign.RIGHT),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=18,
                        icon_color=ft.Colors.RED_400,
                        tooltip=get_text("remove"),
                        on_click=lambda e, idx_i=idx: self.remove_item(idx_i),
                        padding=0,
                    ),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=10, horizontal=12),
                bgcolor=bg_color,
                border_radius=8,
            )
            self.items_list.controls.append(item_row)
        
        # Subtotal row
        subtotal_row = ft.Container(
            content=ft.Row([
                ft.Container(expand=True),
                ft.Text(get_text("subtotal") + ":", size=12, weight=ft.FontWeight.W_500, color="#64748B"),
                ft.Text(f"{int(total):,} KIP", size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
            ], spacing=8),
            padding=ft.padding.symmetric(vertical=8, horizontal=12),
            bgcolor=ft.Colors.GREY_100,
        )
        self.items_list.controls.append(subtotal_row)
        
        self.total_text.value = f"{int(total):,} KIP"
        self.page.update()
    
    def remove_item(self, index):
        removed = self.items.pop(index)
        self.update_items_display()
        self.show_snack_bar(f"{get_text('part_removed')}: {removed['part_name']}", is_error=False)
    
    def create_purchase_order(self, e):
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
            if result and result.get('id'):
                self.show_success_popup(result.get('po_no'))
            else:
                self.show_snack_bar(get_text("create_failed"), is_error=True)
        except Exception as ex:
            print(f"Error creating PO: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def show_success_popup(self, po_no):
        def go_to_list(e):
            popup.open = False
            self.navigate("purchase_order_list")
        
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=28, color=ft.Colors.WHITE),
                            bgcolor=self.success_color,
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            get_text("success"),
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(height=8),
                    ft.Text(
                        get_text("po_created_success"),
                        size=15,
                        weight=ft.FontWeight.W_500,
                        color="#1E293B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOCAL_SHIPPING, size=16, color=self.primary_color),
                            ft.Text(
                                f"{get_text('po_number')}: {po_no}",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=self.primary_color,
                            ),
                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.padding.all(12),
                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                        border_radius=10,
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        get_text("go_to_list_message"),
                        size=12,
                        color="#64748B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                padding=ft.padding.all(24),
                width=380,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            get_text("go_to_list"),
                            on_click=go_to_list,
                            style=ft.ButtonStyle(
                                bgcolor=self.primary_color,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=24, vertical=10),
                            ),
                        ),
                    ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, size=13),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=3000,
        )
        self.page.update()