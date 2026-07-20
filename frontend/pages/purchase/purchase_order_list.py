# pages/purchase/purchase_order_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import asyncio  # เพิ่ม import asyncio

from i18n import get_text


class PurchaseOrderListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.current_snackbar = None
        self.purchase_orders = []
        self.filtered_orders = []
        self.low_stock_parts = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.search_field = None
        self.current_status_filter = "all"
        self.status_chips = None
        self.table_rows = None
        self.pagination_container = None
        self.notification_button = None
        self.header_container = None
        self.current_dialog = None

    def build(self):
        header = self._build_header()
        
        search_bar = self._build_search_bar()
        table = self._build_table()
        self.pagination_container = ft.Container(padding=ft.padding.symmetric(vertical=12, horizontal=20))
        
        content_area = ft.Container(
            content=ft.Column([
                search_bar,
                table,
                self.pagination_container,
            ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
            padding=ft.padding.all(24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.load_low_stock_parts()
        self.load_purchase_orders()
        
        return main_content
    
    def _build_notification_button(self):
        """Build notification button with badge"""
        count = len(self.low_stock_parts)
        has_notification = count > 0
        
        return ft.Container(
            content=ft.Row([
                ft.Text("⚠️", size=16),
                ft.Text(
                    get_text("low_stock"),
                    size=13,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Container(
                    content=ft.Text(
                        str(count),
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor="#EF4444" if has_notification else ft.Colors.TRANSPARENT,
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    visible=has_notification,
                ),
            ], spacing=4),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            border_radius=10,
            on_click=self.show_low_stock_dialog,
            ink=True,
        )
    
    def _build_header(self):
        self.notification_button = self._build_notification_button()
        
        self.header_container = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("purchase_order_list_title"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Row([
                        self.notification_button,
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.HISTORY, size=18, color=ft.Colors.WHITE),
                                ft.Text(get_text("goods_receipt_history_title"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                            ], spacing=6),
                            on_click=lambda e: self.navigate("goods_receipt_list"),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                                shape=ft.RoundedRectangleBorder(radius=10),
                                elevation=0,
                                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                            ),
                        ),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                                ft.Text(get_text("create_purchase_order"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                            ], spacing=6),
                            on_click=lambda e: self.navigate("purchase_order_create"),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                                shape=ft.RoundedRectangleBorder(radius=10),
                                elevation=0,
                                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                            ),
                        ),
                    ], spacing=8),
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
        return self.header_container
    
    def _update_header(self):
        """Update header when low stock count changes"""
        if self.header_container:
            self.notification_button = self._build_notification_button()
            self.header_container.content = ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("purchase_order_list_title"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Row([
                        self.notification_button,
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.HISTORY, size=18, color=ft.Colors.WHITE),
                                ft.Text(get_text("goods_receipt_history_title"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                            ], spacing=6),
                            on_click=lambda e: self.navigate("goods_receipt_list"),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                                shape=ft.RoundedRectangleBorder(radius=10),
                                elevation=0,
                                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                            ),
                        ),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                                ft.Text(get_text("create_purchase_order"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                            ], spacing=6),
                            on_click=lambda e: self.navigate("purchase_order_create"),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                                shape=ft.RoundedRectangleBorder(radius=10),
                                elevation=0,
                                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                            ),
                        ),
                    ], spacing=8),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            self.page.update()
    
    def _load_status_chips(self):
        """Load status filter chips"""
        if not self.status_chips:
            return
        
        self.status_chips.controls.clear()
        
        status_list = [
            {"id": "all", "name": get_text("all_status")},
            {"id": "ordering", "name": get_text("ordering") if get_text("ordering") else "Ordering"},
            {"id": "partial", "name": get_text("partial") if get_text("partial") else "Partial"},
            {"id": "completed", "name": get_text("completed") if get_text("completed") else "Completed"},
            {"id": "cancelled", "name": get_text("cancelled") if get_text("cancelled") else "Cancelled"},
        ]
        
        for status in status_list:
            is_active = self.current_status_filter == status["id"]
            chip = ft.Container(
                content=ft.Text(status["name"], size=12, weight=ft.FontWeight.W_500,
                               color=ft.Colors.WHITE if is_active else "#64748B"),
                bgcolor=self.primary_color if is_active else ft.Colors.GREY_200,
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                ink=True,
                on_click=lambda e, sid=status["id"]: self.filter_by_status(sid),
            )
            self.status_chips.controls.append(chip)
        
        self.page.update()
    
    def filter_by_status(self, status_id):
        self.current_status_filter = status_id
        self._load_status_chips()
        self.apply_filters()
    
    def _build_search_bar(self):
        self.status_chips = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
        self._load_status_chips()
        
        self.search_field = ft.TextField(
            hint_text=get_text("search_purchase_order"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
        )
        self.search_field.on_change = self.on_search_change
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.refresh_all(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([self.search_field, refresh_button], spacing=10),
                ft.Container(height=12),
                self.status_chips,
            ], spacing=0),
            margin=ft.margin.only(bottom=16),
        )
    
    def _build_table(self):
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("po_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    padding=ft.padding.only(left=8),
                ),
                ft.Container(
                    content=ft.Text(get_text("supplier"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=140,
                    padding=ft.padding.only(left=8),
                ),
                ft.Container(
                    content=ft.Text(get_text("order_date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=95,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("total_amount"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=8),
                ),
                ft.Container(
                    content=ft.Text(get_text("status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=85,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("created_by"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    padding=ft.padding.only(left=8),
                ),
                ft.Container(
                    content=ft.Text(get_text("actions"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=8),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        table_content = ft.Column([
            table_header,
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            self.table_rows,
        ], spacing=0)
        
        table_scroll = ft.Container(
            content=table_content,
            width=950,
        )
        
        return ft.Container(
            content=ft.Row([table_scroll], scroll=ft.ScrollMode.AUTO),
            margin=ft.margin.only(left=20, right=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
            expand=True,
        )
    
    def refresh_all(self):
        self.load_low_stock_parts()
        self.load_purchase_orders()
    
    def load_low_stock_parts(self):
        try:
            self.low_stock_parts = self.client.get_low_stock_parts()
            self._update_header()
        except Exception as ex:
            print(f"Error loading low stock parts: {ex}")
            self.low_stock_parts = []
            self._update_header()
    
    def show_low_stock_dialog(self, e):
        if not self.low_stock_parts:
            dialog = ft.AlertDialog(
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=16),
                bgcolor=ft.Colors.WHITE,
                title=ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=24, color=ft.Colors.WHITE),
                                bgcolor="#10B981",
                                border_radius=12,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                get_text("low_stock"),
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
                        ft.Icon(ft.Icons.INBOX, size=48, color="#CBD5E1"),
                        ft.Text(get_text("no_low_stock_parts"), size=14, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                    padding=ft.padding.all(40),
                    width=400,
                ),
                actions=[
                    ft.TextButton(get_text("close"), on_click=lambda e: self._close_dialog(dialog)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self._open_dialog(dialog)
            return
        
        parts_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=350)
        
        for part in self.low_stock_parts[:30]:
            name = part.get('name', '-')
            stock_qty = part.get('stock_qty', 0)
            min_stock = part.get('min_stock', 5)
            supplier_name = part.get('supplier_name', '-')
            
            if stock_qty <= 0:
                color = "#EF4444"
                status = get_text("out_of_stock")
            elif stock_qty <= min_stock / 2:
                color = "#F59E0B"
                status = get_text("critical")
            else:
                color = "#10B981"
                status = get_text("low")
            
            part_row = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ft.Text(f"{get_text('supplier')}: {supplier_name}", size=11, color="#64748B"),
                    ], spacing=2, expand=True),
                    ft.Column([
                        ft.Text(f"{stock_qty} / {min_stock}", size=13, weight=ft.FontWeight.W_700, color=color),
                        ft.Text(status, size=10, color=color),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                bgcolor=ft.Colors.GREY_50,
                border_radius=8,
            )
            parts_list.controls.append(part_row)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING, size=24, color=ft.Colors.WHITE),
                            bgcolor="#F59E0B",
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            f"{get_text('low_stock')} ({len(self.low_stock_parts)})",
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
                    ft.Text(get_text("parts_need_reorder"), size=12, color="#64748B"),
                    ft.Container(height=8),
                    parts_list,
                ]),
                padding=ft.padding.all(20),
                width=450,
                height=450,
            ),
            actions=[
                ft.TextButton(get_text("close"), on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton(
                    get_text("create_purchase_order"),
                    on_click=lambda e: (self._close_dialog(dialog), self.navigate("purchase_order_create")),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    # ==================== RECEIVE DIALOG (Process 7.3) ====================
    
    def show_receive_dialog(self, po_id: int):
        """Show dialog to receive purchase order items (Process 7.3)"""
        try:
            print(f"🔍 DEBUG: show_receive_dialog called with po_id={po_id}")
            
            po_data = self.client.get_purchase_order(po_id)
            print(f"🔍 DEBUG: po_data = {po_data}")
            
            if not po_data:
                self.show_snack_bar(get_text("purchase_order_not_found"), is_error=True)
                return
            
            current_status = po_data.get('status')
            print(f"🔍 DEBUG: Current status = {current_status}")
            
            if current_status not in ['ordering', 'partial']:
                self.show_snack_bar(get_text("only_ordering_po_can_be_received"), is_error=True)
                return
            
            items = po_data.get('items', [])
            print(f"🔍 DEBUG: items count = {len(items)}")
            
            if not items:
                self.show_snack_bar(get_text("no_items_in_order"), is_error=True)
                return
            
            receive_items = []
            qty_fields = {}
            cost_fields = {}
            
            for item in items:
                part_id = item.get('part_id')
                part_name = item.get('part_name', '-')
                qty = item.get('qty', 0)
                already_received = item.get('received_qty', 0)
                remaining = qty - already_received
                
                if remaining <= 0:
                    continue
                
                receive_items.append({
                    'part_id': part_id,
                    'part_name': part_name,
                    'qty': qty,
                    'already_received': already_received,
                    'remaining': remaining,
                    'unit_cost': item.get('unit_cost', 0)
                })
            
            if not receive_items:
                self.show_snack_bar(get_text("all_items_already_received"), is_error=True)
                return
            
            items_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=300)
            
            for idx, item in enumerate(receive_items):
                qty_field = ft.TextField(
                    value=str(item['remaining']),
                    width=80,
                    text_align=ft.TextAlign.CENTER,
                    input_filter=ft.NumbersOnlyInputFilter(),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    content_padding=ft.padding.symmetric(horizontal=8, vertical=6),
                )
                qty_fields[idx] = qty_field
                
                cost_field = ft.TextField(
                    value=str(int(item['unit_cost'])),
                    width=100,
                    text_align=ft.TextAlign.RIGHT,
                    input_filter=ft.NumbersOnlyInputFilter(),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    content_padding=ft.padding.symmetric(horizontal=8, vertical=6),
                )
                cost_fields[idx] = cost_field
                
                def create_qty_handler(idx_item, qty_field_ref, max_qty):
                    def handler(e):
                        try:
                            qty = int(qty_field_ref.value) if qty_field_ref.value else 0
                            if qty > max_qty:
                                qty_field_ref.value = str(max_qty)
                                self.page.update()
                            elif qty < 0:
                                qty_field_ref.value = "0"
                                self.page.update()
                        except:
                            qty_field_ref.value = "0"
                            self.page.update()
                    return handler
                
                qty_field.on_change = create_qty_handler(idx, qty_field, item['remaining'])
                
                bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
                
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(item['part_name'], size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ], spacing=2, expand=True),
                        ft.Text(f"{item['qty']}", size=13, color="#64748B", width=50, text_align=ft.TextAlign.CENTER),
                        cost_field,
                        qty_field,
                        ft.Text(f"{get_text('remaining')}: {item['remaining']}", size=11, color="#F59E0B", width=80),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    bgcolor=bg_color,
                    border_radius=8,
                )
                items_column.controls.append(item_row)
            
            po_no = po_data.get('po_no', '-')
            supplier_name = po_data.get('supplier_name', '-')
            
            dialog = ft.AlertDialog(
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=16),
                bgcolor=ft.Colors.WHITE,
                title=ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.INVENTORY_2, size=24, color=ft.Colors.WHITE),
                                bgcolor="#10B981",
                                border_radius=12,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                f"{get_text('receive')}: {po_no}",
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
                        ft.Text(f"{get_text('supplier')}: {supplier_name}", size=13, color="#64748B"),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Text(get_text("item"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                            ft.Text(get_text("ordered"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=50, text_align=ft.TextAlign.CENTER),
                            ft.Text(get_text("unit_cost"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100, text_align=ft.TextAlign.CENTER),
                            ft.Text(get_text("receive_qty"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=80, text_align=ft.TextAlign.CENTER),
                            ft.Text(get_text("remaining"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=80, text_align=ft.TextAlign.CENTER),
                        ], spacing=12),
                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                        items_column,
                    ]),
                    padding=ft.padding.all(20),
                    width=650,
                    height=450,
                ),
                actions=[
                    ft.TextButton(
                        get_text("cancel"),
                        on_click=lambda e: self._close_dialog(dialog),
                    ),
                    ft.ElevatedButton(
                        get_text("confirm_receive"),
                        on_click=lambda e: self.confirm_receive(dialog, po_id, receive_items, qty_fields, cost_fields),
                        style=ft.ButtonStyle(
                            bgcolor="#10B981",
                            color=ft.Colors.WHITE,
                        ),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self._open_dialog(dialog)
            
        except Exception as ex:
            print(f"❌ Error showing receive dialog: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def confirm_receive(self, dialog, po_id, receive_items, qty_fields, cost_fields):
        """Confirm receiving items"""
        received_items_data = []
        has_received = False
        
        for idx, item in enumerate(receive_items):
            qty_field = qty_fields.get(idx)
            cost_field = cost_fields.get(idx)
            if qty_field and cost_field:
                try:
                    qty = int(qty_field.value) if qty_field.value else 0
                except:
                    qty = 0
                
                try:
                    cost_price = float(cost_field.value) if cost_field.value else 0.0
                except:
                    cost_price = 0.0
                
                if qty > item['remaining']:
                    qty = item['remaining']
                    qty_field.value = str(qty)
                
                if qty > 0:
                    has_received = True
                    received_items_data.append({
                        'part_id': item['part_id'],
                        'received_qty': qty,
                        'cost_price': cost_price
                    })
        
        if not has_received:
            self.show_snack_bar(get_text("no_items_to_receive"), is_error=True)
            return
        
        try:
            result = self.client.receive_purchase_order(po_id, received_items_data)
            if result:
                self._close_dialog(dialog)
                self.load_purchase_orders()
                self.show_snack_bar(get_text("receive_success"), is_error=False)
            else:
                self.show_snack_bar(get_text("receive_failed"), is_error=True)
        except Exception as ex:
            print(f"Error receiving: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def show_cancel_dialog(self, po_id: int, po_no: str):
        """Show cancel confirmation dialog"""
        def confirm_cancel(e):
            try:
                self.client.update_purchase_order_status(po_id, 'cancelled')
                self._close_dialog(dialog)
                self.load_purchase_orders()
                self.show_snack_bar(f"{get_text('cancelled_success')}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING, size=24, color=ft.Colors.WHITE),
                            bgcolor="#EF4444",
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            get_text("confirm_cancel"),
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
                    ft.Text(
                        f"{get_text('cancel_po_confirm')}: {po_no}?",
                        size=14,
                        color="#1E293B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        get_text("cancel_warning"),
                        size=12,
                        color="#64748B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                padding=ft.padding.all(24),
                width=380,
            ),
            actions=[
                ft.TextButton(
                    get_text("no"),
                    on_click=lambda e: self._close_dialog(dialog),
                ),
                ft.ElevatedButton(
                    get_text("yes_cancel"),
                    on_click=confirm_cancel,
                    style=ft.ButtonStyle(
                        bgcolor="#EF4444",
                        color=ft.Colors.WHITE,
                    ),
                ),
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
    
    def load_purchase_orders(self):
        self.table_rows.controls.clear()
        self.page.update()
        
        try:
            orders = self.client.get_purchase_orders()
            self.purchase_orders = orders
            self.filtered_orders = orders.copy()
            self.display_orders()
        except Exception as ex:
            print(f"Error loading purchase orders: {ex}")
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                        ft.Text(f"Error: {str(ex)}", size=14, color=ft.Colors.RED_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(40),
                )
            )
            self.page.update()
    
    def on_search_change(self, e):
        self.apply_filters()
    
    def apply_filters(self):
        selected_status = self.current_status_filter if self.current_status_filter else "all"
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        
        filtered = self.purchase_orders.copy()
        
        if selected_status and selected_status != "all":
            filtered = [o for o in filtered if o.get("status") == selected_status]
        
        if keyword:
            filtered = [
                o for o in filtered
                if keyword in o.get("po_no", "").lower()
                or keyword in o.get("supplier_name", "").lower()
            ]
        
        self.filtered_orders = filtered
        self.current_page = 1
        self.display_orders()
    
    def display_orders(self):
        self.table_rows.controls.clear()
        
        total_items = len(self.filtered_orders)
        
        if total_items == 0:
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.LOCAL_SHIPPING, size=48, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_purchase_orders"), size=16, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(40),
                )
            )
            self.update_pagination()
            self.page.update()
            return
        
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_orders[start_idx:end_idx]
        
        for i, order in enumerate(page_items):
            self.table_rows.controls.append(self._create_order_row(order, start_idx + i))
        
        self.update_pagination()
        self.page.update()
    
    def _create_order_row(self, order: Dict, index: int):
        po_id = order.get("id")
        po_no = order.get("po_no", "-")
        supplier_name = order.get("supplier_name", "-")
        order_date = order.get("order_date", "")
        if order_date:
            order_date = order_date[:10] if " " in order_date else order_date[:10]
        else:
            order_date = "-"
        total_amount = order.get("total_amount", 0)
        status = order.get("status", "pending")
        created_by = order.get("created_by_name", "-")
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        status_colors = {
            "ordering": "#2196F3",
            "partial": "#FF9800",
            "completed": "#4CAF50",
            "cancelled": "#F44336"
        }
        status_texts = {
            "ordering": get_text("ordering") if get_text("ordering") else "Ordering",
            "partial": get_text("partial") if get_text("partial") else "Partial",
            "completed": get_text("completed") if get_text("completed") else "Completed",
            "cancelled": get_text("cancelled") if get_text("cancelled") else "Cancelled"
        }
        
        # Status badge
        status_badge = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                ft.Text(status_texts.get(status, status), size=11, color=ft.Colors.WHITE),
            ], spacing=4),
            bgcolor=status_colors.get(status, "#607D8B"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
        )
        
        # View button
        view_btn = ft.IconButton(
            icon=ft.Icons.VISIBILITY_OUTLINED,
            icon_size=18,
            tooltip=get_text("view_detail"),
            on_click=lambda e, pid=po_id: self.view_detail(pid),
        )
        
        # Receive button
        receive_btn = None
        if status in ["ordering", "partial"]:
            receive_btn = ft.IconButton(
                icon=ft.Icons.INVENTORY_2_OUTLINED,
                icon_size=18,
                tooltip=get_text("receive"),
                icon_color=ft.Colors.GREEN_600,
                on_click=lambda e, pid=po_id: self.show_receive_dialog(pid),
            )
        
        # Cancel button
        cancel_btn = None
        if status in ["ordering", "partial"]:
            cancel_btn = ft.IconButton(
                icon=ft.Icons.CANCEL_OUTLINED,
                icon_size=18,
                tooltip=get_text("cancel"),
                icon_color=ft.Colors.RED_600,
                on_click=lambda e, pid=po_id, pno=po_no: self.show_cancel_dialog(pid, pno),
            )
        
        actions = [view_btn]
        if receive_btn:
            actions.append(receive_btn)
        if cancel_btn:
            actions.append(cancel_btn)
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(po_no, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=110,
                    padding=ft.padding.only(left=8),
                ),
                ft.Container(
                    content=ft.Text(supplier_name, size=13, color="#1E293B", max_lines=1),
                    width=140,
                    padding=ft.padding.only(left=8),
                ),
                ft.Container(
                    content=ft.Text(order_date, size=12, color="#64748B"),
                    width=95,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(f"{int(total_amount):,}", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=100,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=8),
                ),
                ft.Container(
                    content=status_badge,
                    width=85,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(created_by, size=12, color="#64748B", max_lines=1),
                    width=100,
                    padding=ft.padding.only(left=8),
                ),
                ft.Container(
                    content=ft.Row(actions, spacing=2),
                    width=130,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=10, horizontal=8),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    def update_pagination(self):
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_orders)} {get_text('of')} {len(self.purchase_orders)} {get_text('results')}",
                    size=12,
                    color="#64748B",
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_LEFT,
                            icon_size=20,
                            on_click=self.prev_page,
                            disabled=prev_disabled,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                        ft.Container(
                            content=ft.Text(f"{self.current_page}/{self.total_pages}", size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                            padding=ft.padding.symmetric(horizontal=15),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_RIGHT,
                            icon_size=20,
                            on_click=self.next_page,
                            disabled=next_disabled,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                    ]),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_orders()
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_orders()
    
    def view_detail(self, po_id: int):
        self.navigate("purchase_order_detail", po_id=po_id)
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        """Show snackbar notification - Bottom center with auto width"""
        
        # Remove existing snackbar if any
        if self.current_snackbar:
            try:
                self.page.overlay.remove(self.current_snackbar)
            except:
                pass
            self.current_snackbar = None
        
        if not is_error:
            bgcolor = ft.Colors.GREEN_600
            icon = ft.Icons.CHECK_CIRCLE
        else:
            bgcolor = ft.Colors.RED_600
            icon = ft.Icons.ERROR
        
        # Create snackbar content with auto width
        snack_content = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=ft.Colors.WHITE, size=16),
                    ft.Text(message, color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.W_500),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=8, bottom=8),
            bgcolor=bgcolor,
            border_radius=8,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            ),
        )
        
        # Create overlay container - positioned at bottom center
        snackbar = ft.Container(
            content=snack_content,
            margin=ft.Margin(left=30, right=30, top=0, bottom=20),
            alignment=ft.Alignment(0, 1),  # Bottom Center
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            opacity=0,
        )
        
        # Add to overlay
        self.page.overlay.append(snackbar)
        self.current_snackbar = snackbar
        
        # Animate in
        snackbar.opacity = 1
        self.page.update()
        
        # Auto dismiss after 3 seconds using asyncio
        async def dismiss_after_delay():
            await asyncio.sleep(2.0)
            if snackbar in self.page.overlay:
                snackbar.opacity = 0
                self.page.update()
                await asyncio.sleep(0.3)
                if snackbar in self.page.overlay:
                    self.page.overlay.remove(snackbar)
                    if self.current_snackbar == snackbar:
                        self.current_snackbar = None
                    self.page.update()
        
        # Run the dismiss task
        self.page.run_task(dismiss_after_delay)