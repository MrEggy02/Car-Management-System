# pages/purchase/purchase_order_receive.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable, List
from i18n import get_text


class PurchaseOrderReceiveContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, po_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.po_id = po_id
        self.po_data = None
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.items = []
        self.received_items = []
        
    def build(self):
        header = self._build_header()
        
        if not self.po_id:
            error_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.WARNING_AMBER, size=64, color=ft.Colors.ORANGE_600),
                    ft.Text(get_text("no_purchase_order_selected"), size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.ElevatedButton(
                        get_text("back_to_list"),
                        on_click=lambda e: self.navigate("purchase_order_list"),
                        style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
            return ft.Container(
                content=ft.Column([header, error_container]),
                expand=True,
                bgcolor="#F5F7FA",
            )
        
        self.load_purchase_order()
        
        if not self.po_data:
            loading = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=50, height=50),
                    ft.Text(get_text("loading"), size=16, color="#64748B"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
            return ft.Container(
                content=ft.Column([header, loading]),
                expand=True,
                bgcolor="#F5F7FA",
            )
        
        content = self._build_content()
        
        scrollable_content = ft.Column(
            [content],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.padding.all(24),
            bgcolor="#F0F2F5",
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
                                get_text("receive_purchase_order"),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("receive_purchase_order_subtitle"),
                                size=12,
                                color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
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
    
    def load_purchase_order(self):
        try:
            self.po_data = self.client.get_purchase_order(self.po_id)
            print(f"DEBUG: PO data loaded: {self.po_data}")
            
            if self.po_data and self.po_data.get('items'):
                self.items = self.po_data.get('items', [])
                # Initialize received quantities
                self.received_items = []
                for item in self.items:
                    # Check if already received some
                    already_received = item.get('received_qty', 0)
                    ordered_qty = item.get('qty', 0)
                    remaining_qty = ordered_qty - already_received
                    
                    self.received_items.append({
                        'part_id': item.get('part_id'),
                        'part_name': item.get('part_name', '-'),
                        'ordered_qty': ordered_qty,
                        'already_received': already_received,
                        'received_qty': remaining_qty if remaining_qty > 0 else 0,
                        'unit_cost': item.get('unit_cost', 0)
                    })
            
            self.page.update()
        except Exception as ex:
            print(f"Error loading purchase order: {ex}")
            import traceback
            traceback.print_exc()
    
    def _build_content(self):
        po_no = self.po_data.get('po_no', '-')
        supplier_name = self.po_data.get('supplier_name', '-')
        order_date = self.po_data.get('order_date', '')
        if order_date:
            order_date = order_date[:16] if len(order_date) > 16 else order_date
        else:
            order_date = '-'
        status = self.po_data.get('status', 'pending')
        
        # PO Info Card
        po_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.LOCAL_SHIPPING, size=20, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("po_info"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("po_no"), size=11, color="#64748B"),
                            ft.Text(po_no, size=15, weight=ft.FontWeight.W_700, color=self.primary_color),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("supplier"), size=11, color="#64748B"),
                            ft.Text(supplier_name, size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("order_date"), size=11, color="#64748B"),
                            ft.Text(order_date, size=13, color="#1E293B"),
                        ], spacing=4, expand=True),
                    ]),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
        
        # Items List
        items_list = ft.Column(spacing=8)
        total_amount = 0
        
        for idx, item in enumerate(self.received_items):
            part_name = item.get('part_name', '-')
            ordered_qty = item.get('ordered_qty', 0)
            already_received = item.get('already_received', 0)
            unit_cost = item.get('unit_cost', 0)
            total_line = ordered_qty * unit_cost
            total_amount += total_line
            remaining_qty = ordered_qty - already_received
            
            qty_field = ft.TextField(
                value=str(remaining_qty if remaining_qty > 0 else 0),
                width=100,
                text_align=ft.TextAlign.CENTER,
                input_filter=ft.NumbersOnlyInputFilter(),
                border_radius=8,
                bgcolor=ft.Colors.WHITE,
                disabled=remaining_qty <= 0,
            )
            
            # Store reference to update
            def create_qty_handler(idx_item, qty_field_ref, max_qty):
                def handler(e):
                    try:
                        qty = int(qty_field_ref.value) if qty_field_ref.value else 0
                        qty = min(qty, max_qty)  # Cannot receive more than remaining
                        self.received_items[idx_item]['received_qty'] = qty
                        # Update field value if corrected
                        if qty != int(qty_field_ref.value):
                            qty_field_ref.value = str(qty)
                            self.page.update()
                    except:
                        self.received_items[idx_item]['received_qty'] = 0
                return handler
            
            qty_field.on_change = create_qty_handler(idx, qty_field, remaining_qty)
            
            bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
            
            # Show received status badge
            if already_received > 0:
                received_badge = ft.Container(
                    content=ft.Text(f"{get_text('received')}: {already_received}", size=10, color=ft.Colors.GREEN_600),
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                )
            else:
                received_badge = None
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(part_name, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ft.Row([
                            ft.Text(f"{get_text('unit_cost')}: {int(unit_cost):,} KIP", size=11, color="#64748B"),
                            received_badge if received_badge else ft.Container(),
                        ], spacing=8),
                    ], spacing=2, expand=True),
                    ft.Text(f"{ordered_qty}", size=13, color="#64748B", width=60, text_align=ft.TextAlign.CENTER),
                    qty_field,
                    ft.Text(f"{int(total_line):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.primary_color, width=120, text_align=ft.TextAlign.RIGHT),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=10, horizontal=12),
                bgcolor=bg_color,
                border_radius=8,
            )
            items_list.controls.append(item_row)
        
        # Total amount
        total_text = ft.Text(f"{int(total_amount):,} KIP", size=16, weight=ft.FontWeight.BOLD, color=self.primary_color, text_align=ft.TextAlign.RIGHT)
        
        items_card = ft.Card(
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
                            ft.Text(get_text("items_to_receive"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(get_text("total_amount") + ":", size=12, color="#64748B"),
                                    total_text,
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
                    ft.Row([
                        ft.Text(get_text("part_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                        ft.Text(get_text("ordered_qty"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=60, text_align=ft.TextAlign.CENTER),
                        ft.Text(get_text("received_qty"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100, text_align=ft.TextAlign.CENTER),
                        ft.Text(get_text("total"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120, text_align=ft.TextAlign.RIGHT),
                    ], spacing=12),
                    ft.Container(height=8),
                    items_list,
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
        
        # Action Buttons
        confirm_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.INVENTORY_2, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("confirm_receive"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=8),
            on_click=self.confirm_receive,
            style=ft.ButtonStyle(
                bgcolor="#10B981",
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=28, vertical=14),
            ),
        )
        
        back_btn = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ARROW_BACK, size=18, color=self.primary_color),
                ft.Text(get_text("back"), size=14, color=self.primary_color, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=lambda e: self.navigate("purchase_order_list"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, self.primary_color),
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
            ),
        )
        
        action_row = ft.Row([back_btn, confirm_btn], spacing=12, alignment=ft.MainAxisAlignment.END)
        
        return ft.Column([
            po_info_card,
            items_card,
            ft.Container(height=20),
            action_row,
        ], spacing=0)
    
    def confirm_receive(self, e):
        """Confirm receiving items"""
        # Check if any item received
        has_received = any(item.get('received_qty', 0) > 0 for item in self.received_items)
        if not has_received:
            self.show_snack_bar(get_text("no_items_to_receive"), is_error=True)
            return
        
        # Prepare received items list
        received_items_data = []
        for item in self.received_items:
            if item.get('received_qty', 0) > 0:
                received_items_data.append({
                    'part_id': item['part_id'],
                    'received_qty': item['received_qty']
                })
        
        try:
            result = self.client.receive_purchase_order(self.po_id, received_items_data)
            if result:
                # Show success popup then go back to list
                self.show_success_popup()
            else:
                self.show_snack_bar(get_text("receive_failed"), is_error=True)
        except Exception as ex:
            print(f"Error receiving: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def show_success_popup(self):
        def go_to_list(e):
            popup.open = False
            # Navigate back to list and refresh
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
                            bgcolor="#10B981",
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
                        get_text("receive_success"),
                        size=15,
                        weight=ft.FontWeight.W_500,
                        color="#1E293B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        get_text("stock_updated"),
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