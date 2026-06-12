# pages/purchase/purchase_order_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable

from i18n import get_text


class PurchaseOrderListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.purchase_orders = []
        self.filtered_orders = []
        self.low_stock_parts = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.search_field = None
        self.status_filter = None
        self.table_rows = None
        self.pagination_container = None
        self.low_stock_container = None
        self.low_stock_visible = True

    def build(self):
        header = self._build_header()
        
        # Low Stock Alert Section (Process 7.1)
        self.low_stock_container = ft.Container(
            content=self._build_low_stock_alert(),
            margin=ft.margin.only(bottom=16),
            visible=True,
        )
        
        search_bar = self._build_search_bar()
        table = self._build_table()
        self.pagination_container = ft.Container(padding=ft.padding.symmetric(vertical=12, horizontal=20))
        
        # Main scrollable content area
        content_area = ft.Container(
            content=ft.Column([
                self.low_stock_container,
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
    
    def _build_header(self):
        return ft.Container(
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
    
    def _build_low_stock_alert(self):
        """Build low stock alert section (Process 7.1) with scrollable list"""
        
        # Header with toggle button (using KEYBOARD_ARROW_UP/DOWN instead of ARROW_UP/DOWN)
        header_row = ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.WARNING, size=20, color=ft.Colors.WHITE),
                bgcolor="#F59E0B",
                border_radius=8,
                padding=ft.padding.all(6),
            ),
            ft.Text(get_text("low_stock_alert"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.KEYBOARD_ARROW_UP if self.low_stock_visible else ft.Icons.KEYBOARD_ARROW_DOWN,
                icon_size=18,
                icon_color="#64748B",
                tooltip=get_text("collapse"),
                on_click=self._toggle_low_stock_alert,
            ),
        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Low stock list with max height and scroll
        low_stock_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=250)
        
        def create_low_stock_card(part):
            part_id = part.get('id')
            part_name = part.get('name', '-')
            stock_qty = part.get('stock_qty', 0)
            min_stock = part.get('min_stock', 5)
            supplier_name = part.get('supplier_name', '-')
            supplier_phone = part.get('supplier_phone', '-')
            
            # Calculate percentage
            percentage = (stock_qty / min_stock * 100) if min_stock > 0 else 0
            
            # Determine urgency color
            if percentage <= 25:
                urgency_color = "#EF4444"
                urgency_text = get_text("critical_stock")
            elif percentage <= 50:
                urgency_color = "#F59E0B"
                urgency_text = get_text("warning_stock")
            else:
                urgency_color = "#10B981"
                urgency_text = get_text("low_stock")
            
            return ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.WARNING_AMBER, size=20, color=urgency_color),
                        bgcolor=ft.Colors.with_opacity(0.1, urgency_color),
                        border_radius=10,
                        padding=ft.padding.all(8),
                    ),
                    ft.Column([
                        ft.Text(part_name, size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ft.Text(f"{get_text('supplier')}: {supplier_name} | {get_text('phone')}: {supplier_phone}", size=11, color="#64748B"),
                    ], spacing=2, expand=True),
                    ft.Column([
                        ft.Container(
                            content=ft.Text(f"{stock_qty} / {min_stock}", size=13, weight=ft.FontWeight.W_700, color=urgency_color),
                            bgcolor=ft.Colors.with_opacity(0.1, urgency_color),
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        ),
                        ft.Text(urgency_text, size=10, color=urgency_color),
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SHOPPING_CART, size=14, color=ft.Colors.WHITE),
                            ft.Text(get_text("order_now"), size=12, color=ft.Colors.WHITE),
                        ], spacing=4),
                        on_click=lambda e, pid=part_id: self.navigate("purchase_order_create", part_id=pid),
                        style=ft.ButtonStyle(
                            bgcolor=self.primary_color,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        ),
                    ),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(12),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.GREY_200),
            )
        
        if self.low_stock_parts:
            for part in self.low_stock_parts[:10]:  # Show max 10 items
                low_stock_list.controls.append(create_low_stock_card(part))
            
            # Show more indicator if more than 10
            if len(self.low_stock_parts) > 10:
                low_stock_list.controls.append(
                    ft.Container(
                        content=ft.Text(f"... {get_text('and_more')} {len(self.low_stock_parts) - 10} {get_text('items')}", size=11, color="#64748B"),
                        padding=ft.padding.all(8),
                        alignment=ft.Alignment(0, 0),
                    )
                )
        else:
            low_stock_list.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_low_stock_parts"), size=13, color="#94A3B8"),
                    padding=ft.padding.all(30),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        info_text = ft.Text(
            f"{get_text('parts_need_reorder')}: {len(self.low_stock_parts)} {get_text('items')}",
            size=12,
            color="#64748B",
        )
        
        content_column = ft.Column([
            header_row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            ft.Container(height=8),
            info_text,
            ft.Container(height=8),
            low_stock_list,
        ], spacing=0)
        
        # Make the low stock card collapsible
        if not self.low_stock_visible:
            content_column = ft.Column([
                header_row,
                ft.Divider(height=1, color=ft.Colors.GREY_200),
            ], spacing=0)
        
        return ft.Card(
            content=ft.Container(
                content=content_column,
                padding=ft.padding.all(16),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
    
    def _toggle_low_stock_alert(self, e):
        """Toggle low stock alert visibility"""
        self.low_stock_visible = not self.low_stock_visible
        self.low_stock_container.content = self._build_low_stock_alert()
        self.low_stock_container.update()
    
    def _build_search_bar(self):
        self.status_filter = ft.Dropdown(
            hint_text=get_text("filter_by_status"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option("all", get_text("all_status")),
                ft.dropdown.Option("pending", get_text("pending")),
                ft.dropdown.Option("ordered", get_text("ordered")),
                ft.dropdown.Option("received", get_text("received")),
                ft.dropdown.Option("cancelled", get_text("cancelled")),
            ],
            value="all",
            expand=True,
        )
        self.status_filter.on_change = self.on_filter_change
        
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
            content=ft.Row([self.status_filter, self.search_field, refresh_button], spacing=10),
            margin=ft.margin.only(bottom=16),
        )
    
    def _build_table(self):
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("po_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("supplier"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=160,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("order_date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("total_amount"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=140,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("created_by"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("actions"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=140,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=14, horizontal=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Add horizontal scroll for table
        table_content = ft.Column([
            table_header,
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            self.table_rows,
        ], spacing=0)
        
        table_scroll = ft.Container(
            content=table_content,
            width=1000,
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
        """Refresh both low stock and purchase orders"""
        self.load_low_stock_parts()
        self.load_purchase_orders()
    
    def load_low_stock_parts(self):
        """Load low stock parts for alert (Process 7.1)"""
        try:
            parts = self.client.get_low_stock_parts()
            self.low_stock_parts = parts
            
            self.low_stock_container.content = self._build_low_stock_alert()
            self.low_stock_container.update()
        except Exception as ex:
            print(f"Error loading low stock parts: {ex}")
    
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
    
    def on_filter_change(self, e):
        """Real-time filter by status"""
        self.apply_filters()
    
    def on_search_change(self, e):
        """Real-time search"""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply both status and search filters"""
        selected_status = self.status_filter.value
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        
        filtered = self.purchase_orders.copy()
        
        # Apply status filter
        if selected_status and selected_status != "all":
            filtered = [o for o in filtered if o.get("status") == selected_status]
        
        # Apply search filter
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
            "pending": "#FF9800",
            "ordered": "#2196F3",
            "received": "#4CAF50",
            "cancelled": "#F44336"
        }
        status_texts = {
            "pending": get_text("pending"),
            "ordered": get_text("ordered"),
            "received": get_text("received"),
            "cancelled": get_text("cancelled")
        }
        
        # Clickable status badge to update status
        status_badge = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                ft.Text(status_texts.get(status, status), size=11, color=ft.Colors.WHITE),
                ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=ft.Colors.WHITE),
            ], spacing=4),
            bgcolor=status_colors.get(status, "#607D8B"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            on_click=lambda e, pid=po_id, cur_status=status: self.show_update_status_dialog(pid, cur_status),
        )
        
        view_btn = ft.IconButton(
            icon=ft.Icons.VISIBILITY_OUTLINED,
            icon_size=18,
            tooltip=get_text("view_detail"),
            on_click=lambda e, pid=po_id: self.view_detail(pid),
        )
        
        # Show receive button only if status is 'ordered' (ready to receive)
        receive_btn = None
        if status == "ordered":
            receive_btn = ft.IconButton(
                icon=ft.Icons.INVENTORY_2_OUTLINED,
                icon_size=18,
                tooltip=get_text("receive"),
                icon_color=ft.Colors.GREEN_600,
                on_click=lambda e, pid=po_id: self.receive_order(pid),
            )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(po_no, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=120,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(supplier_name, size=13, color="#1E293B", max_lines=1),
                    width=160,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(order_date, size=12, color="#64748B"),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(f"{int(total_amount):,}", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=140,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=status_badge,
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(created_by, size=12, color="#64748B", max_lines=1),
                    width=130,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Row([view_btn, receive_btn] if receive_btn else [view_btn], spacing=4),
                    width=140,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=10),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    def show_update_status_dialog(self, po_id: int, current_status: str):
        """Show dialog to update purchase order status"""
        status_options = []
        if current_status == "pending":
            status_options = ["ordered", "cancelled"]
        elif current_status == "ordered":
            status_options = ["received", "cancelled"]
        elif current_status == "received":
            status_options = []
        else:
            status_options = []
        
        if not status_options:
            self.show_snack_bar(get_text("cannot_update_status"), is_error=True)
            return
        
        status_dropdown = ft.Dropdown(
            label=get_text("select_status"),
            value=status_options[0] if status_options else current_status,
            options=[
                ft.dropdown.Option("ordered", get_text("ordered")),
                ft.dropdown.Option("received", get_text("received")),
                ft.dropdown.Option("cancelled", get_text("cancelled")),
            ],
            width=250,
            border_radius=12,
        )
        
        def update_status(e):
            new_status = status_dropdown.value
            if new_status and new_status != current_status:
                try:
                    self.client.update_purchase_order_status(po_id, new_status)
                    dialog.open = False
                    self.load_purchase_orders()
                    self.show_snack_bar(f"✅ {get_text('status_updated_to')} {get_text(new_status)}", is_error=False)
                except Exception as ex:
                    self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
            else:
                dialog.open = False
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            get_text("update_purchase_order_status"),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"{get_text('current_status')}: {get_text(current_status)}", size=14, color="#64748B"),
                    ft.Container(height=16),
                    status_dropdown,
                ]),
                padding=ft.padding.all(24),
                width=350,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("update"), on_click=update_status, style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
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
    
    def receive_order(self, po_id: int):
        self.navigate("purchase_order_receive", po_id=po_id)
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, size=13),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=3000,
        )
        self.page.update()