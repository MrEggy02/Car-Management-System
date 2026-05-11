# pages/job_orders/job_order_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime

from i18n import get_text


class JobOrderListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.job_orders = []
        self.filtered_orders = []
        self.expanded_order_id = None
        self.status_filter = None
        self.search_field = None
        
        # Status colors
        self.status_colors = {
            "pending": "#FF9800",
            "quoting": "#2196F3",
            "repairing": "#9C27B0",
            "finished": "#4CAF50",
            "closed": "#607D8B",
            "cancelled": "#F44336"
        }
        
        self.status_icons = {
            "pending": ft.Icons.HOURGLASS_EMPTY,
            "quoting": ft.Icons.CALCULATE,
            "repairing": ft.Icons.BUILD,
            "finished": ft.Icons.CHECK_CIRCLE,
            "closed": ft.Icons.LOCK,
            "cancelled": ft.Icons.CANCEL
        }

    def build(self):
        # Beautiful gradient header
        header = ft.Container(
            content=ft.Row(
                [
                    
                    ft.Column(
                        [
                            ft.Text(
                                get_text("job_order_list"),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("job_order_list_subtitle"),
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("new_job_order"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.navigate("job_order_create"),
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
            padding=ft.padding.symmetric(vertical=20, horizontal=32),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
        
        # Filter section
        self.status_filter = ft.Dropdown(
            hint_text=get_text("filter_by_status"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option("all", get_text("all_status")),
                ft.dropdown.Option("pending", get_text("pending")),
                ft.dropdown.Option("quoting", get_text("quoting")),
                ft.dropdown.Option("repairing", get_text("repairing")),
                ft.dropdown.Option("finished", get_text("finished")),
                ft.dropdown.Option("cancelled", get_text("cancelled")),
            ],
            value="all",
            expand=True,
        )
        
        self.search_field = ft.TextField(
            hint_text=get_text("search_job_order"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        # CRITICAL: Set on_change handlers for real-time filtering
        self.status_filter.on_change = self.apply_filters_from_event
        self.search_field.on_change = self.apply_filters_from_event
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_orders(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        filter_row = ft.Container(
            content=ft.Row([self.status_filter, self.search_field, refresh_button], spacing=10),
            margin=ft.margin.only(bottom=16),
        )
        
        # Stats row
        self.stats_container = ft.Container(
            content=ft.Row(
                [
                    self._create_stat_card(get_text("total_orders"), "0", ft.Icons.RECEIPT, "#1565C0"),
                    self._create_stat_card(get_text("pending_orders"), "0", ft.Icons.HOURGLASS_EMPTY, "#FF9800"),
                    self._create_stat_card(get_text("repairing_orders"), "0", ft.Icons.BUILD, "#9C27B0"),
                    self._create_stat_card(get_text("completed_orders"), "0", ft.Icons.CHECK_CIRCLE, "#4CAF50"),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            margin=ft.margin.only(bottom=20),
        )
        
        # Orders list
        self.orders_list = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Loading indicator
        self.loading_indicator = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=4),
                ft.Container(height=16),
                ft.Text(get_text("loading"), size=14, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=Alignment.CENTER,
            padding=ft.padding.all(40),
        )
        
        # Empty state
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.RECEIPT_OUTLINED, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=16),
                ft.Text(get_text("no_orders_found"), size=18, weight=ft.FontWeight.W_500, color="#64748B"),
                ft.Text(get_text("click_add_to_register"), size=13, color="#94A3B8"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text(get_text("new_job_order"), color=ft.Colors.WHITE, size=14),
                    on_click=lambda e: self.navigate("job_order_create"),
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=Alignment.CENTER,
            padding=ft.padding.all(60),
            visible=False,
        )
        
        # Scrollable content
        scrollable_content = ft.Column(
            [
                filter_row,
                self.stats_container,
                self.orders_list,
                self.loading_indicator,
                self.empty_state,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.padding.all(24),
            bgcolor="#F5F7FA",
        )
        
        # Main layout
        main_content = ft.Container(
            content=ft.Column([
                header,
                content_area,
            ]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Load orders
        self.load_orders()
        
        return main_content
    
    def _create_stat_card(self, title: str, value: str, icon, color: str):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                    bgcolor=color,
                    border_radius=8,
                    padding=ft.padding.all(8),
                ),
                ft.Column([
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Text(title, size=11, color="#64748B"),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_100),
            expand=True,
        )
    
    def load_orders(self):
        """Load job orders from API"""
        self.loading_indicator.visible = True
        self.empty_state.visible = False
        self.orders_list.controls.clear()
        self.page.update()
        
        try:
            orders = self.client.get_job_orders()
            print(f"DEBUG: Loaded orders from API: {len(orders) if orders else 0}")
            
            if orders:
                self.job_orders = orders
            else:
                self.job_orders = []
            
            # Update stats
            self._update_stats()
            
            # Apply filters and display immediately
            self.apply_filters()
            self.loading_indicator.visible = False
            self.page.update()
            
        except Exception as ex:
            print(f"Error loading orders: {ex}")
            self.loading_indicator.visible = False
            self.orders_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                        ft.Text(f"Error: {str(ex)}", size=14, color=ft.Colors.RED_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(40),
                )
            )
            self.page.update()
    
    def _update_stats(self):
        """Update statistics cards"""
        total = len(self.job_orders)
        pending = sum(1 for o in self.job_orders if o.get("status") == "pending")
        repairing = sum(1 for o in self.job_orders if o.get("status") == "repairing")
        completed = sum(1 for o in self.job_orders if o.get("status") in ["finished", "closed"])
        
        if len(self.stats_container.content.controls) >= 4:
            self.stats_container.content.controls[0].content.controls[1].controls[0].value = str(total)
            self.stats_container.content.controls[1].content.controls[1].controls[0].value = str(pending)
            self.stats_container.content.controls[2].content.controls[1].controls[0].value = str(repairing)
            self.stats_container.content.controls[3].content.controls[1].controls[0].value = str(completed)
        self.page.update()
    
    def apply_filters_from_event(self, e):
        """Called when dropdown or search changes - instantly update display"""
        print(f"DEBUG: Filter changed - status: {self.status_filter.value}, search: {self.search_field.value}")
        self.apply_filters()
        self.page.update()
    
    def apply_filters(self):
        """Apply both status filter and search filter - instantly update UI"""
        selected_status = self.status_filter.value
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        
        # Start with all orders
        filtered = self.job_orders.copy()
        
        # Apply status filter
        if selected_status and selected_status != "all":
            filtered = [o for o in filtered if o.get("status") == selected_status]
        
        # Apply search filter
        if keyword:
            filtered = [
                o for o in filtered
                if keyword in o.get("job_no", "").lower()
                or keyword in o.get("customer_name", "").lower()
                or keyword in o.get("plate_number", "").lower()
            ]
        
        self.filtered_orders = filtered
        
        # Clear and rebuild the list
        self.orders_list.controls.clear()
        
        if self.filtered_orders and len(self.filtered_orders) > 0:
            for order in self.filtered_orders:
                self.orders_list.controls.append(
                    self._create_order_card(order)
                )
            self.empty_state.visible = False
        else:
            # Show appropriate "no data" message
            if selected_status != "all" and keyword:
                status_names = {
                    "pending": get_text("pending"),
                    "quoting": get_text("quoting"),
                    "repairing": get_text("repairing"),
                    "finished": get_text("finished"),
                    "cancelled": get_text("cancelled")
                }
                status_name = status_names.get(selected_status, selected_status)
                message = get_text("no_orders_for_status_and_search").format(
                    status=status_name,
                    search=keyword
                )
            elif selected_status != "all":
                status_names = {
                    "pending": get_text("pending"),
                    "quoting": get_text("quoting"),
                    "repairing": get_text("repairing"),
                    "finished": get_text("finished"),
                    "cancelled": get_text("cancelled")
                }
                status_name = status_names.get(selected_status, selected_status)
                message = get_text("no_orders_for_status").format(status=status_name)
            elif keyword:
                message = get_text("no_orders_for_search").format(search=keyword)
            else:
                message = get_text("no_orders_found")
            
            self.empty_state.content.controls[1].value = message
            self.empty_state.visible = True
        
        self.page.update()
    
    def _create_order_card(self, order: Dict):
        """Create an order card"""
        order_id = order.get("id")
        job_no = order.get("job_no", "N/A")
        customer_name = order.get("customer_name", "-")
        plate_number = order.get("plate_number", "-")
        status = order.get("status", "pending")
        receive_date = order.get("receive_date", "")
        if receive_date:
            try:
                receive_date = receive_date.split()[0] if " " in receive_date else receive_date
            except:
                receive_date = "-"
        else:
            receive_date = "-"
        problem = order.get("problem_description", "-")
        is_expanded = self.expanded_order_id == order_id
        
        status_color = self.status_colors.get(status, "#607D8B")
        status_icon = self.status_icons.get(status, ft.Icons.INFO)
        status_text = get_text(status)
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.RECEIPT, size=24, color=self.primary_color),
                    width=40,
                ),
                ft.Column([
                    ft.Text(job_no, size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Text(f"{customer_name} - {plate_number}", size=12, color="#64748B"),
                ], spacing=2, expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(status_icon, size=16, color=ft.Colors.WHITE),
                        ft.Text(status_text, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                    ], spacing=4),
                    bgcolor=status_color,
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                ),
                ft.IconButton(
                    icon=ft.Icons.KEYBOARD_ARROW_DOWN if not is_expanded else ft.Icons.KEYBOARD_ARROW_UP,
                    icon_size=20,
                    on_click=lambda e, oid=order_id: self.toggle_details(oid),
                ),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )
        
        # Details section
        details_section = ft.Container(
            content=ft.Column([
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=8),
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color="#64748B"),
                    ft.Text(f"{get_text('receive_date')}: {receive_date}", size=12, color="#64748B", expand=True),
                ], spacing=8),
                ft.Row([
                    ft.Icon(ft.Icons.DESCRIPTION, size=16, color="#64748B"),
                    ft.Text(f"{get_text('problem')}: {problem[:100]}{'...' if len(problem) > 100 else ''}", size=12, color="#64748B", expand=True),
                ], spacing=8),
                ft.Row([
                    ft.Icon(ft.Icons.SPEED, size=16, color="#64748B"),
                    ft.Text(f"{get_text('mileage')}: {order.get('mileage', 0)} km", size=12, color="#64748B"),
                ], spacing=8),
                ft.Row([
                    ft.Icon(ft.Icons.LOCAL_GAS_STATION, size=16, color="#64748B"),
                    ft.Text(f"{get_text('fuel_level')}: {order.get('fuel_level', '-')}", size=12, color="#64748B"),
                ], spacing=8),
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=16, color="#64748B"),
                    ft.Text(f"{get_text('service_advisor')}: {order.get('created_by_name', '-')}", size=12, color="#64748B"),
                ], spacing=8),
                ft.Container(height=8),
                ft.Row([
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PRINT, size=16, color=self.primary_color),
                            ft.Text(get_text("print"), size=12, color=self.primary_color),
                        ], spacing=4),
                        on_click=lambda e, oid=order_id: self.print_order(oid),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            side=ft.BorderSide(1, self.primary_color),
                        ),
                    ),
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.EDIT, size=16, color="#64748B"),
                            ft.Text(get_text("update_status"), size=12, color="#64748B"),
                        ], spacing=4),
                        on_click=lambda e, oid=order_id: self.show_status_dialog(oid),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            side=ft.BorderSide(1, ft.Colors.GREY_300),
                        ),
                    ),
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.RECEIPT, size=16, color=ft.Colors.GREEN_600),
                            ft.Text(get_text("create_invoice"), size=12, color=ft.Colors.GREEN_600),
                        ], spacing=4),
                        on_click=lambda e, oid=order_id: self.create_invoice(oid),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            side=ft.BorderSide(1, ft.Colors.GREEN_600),
                        ),
                    ),
                ], alignment=ft.MainAxisAlignment.END, spacing=10),
            ]),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            visible=is_expanded,
        )
        
        card_content = ft.Column([header, details_section], spacing=0)
        
        return ft.Card(
            content=card_content,
            elevation=2,
            margin=ft.margin.only(bottom=8),
        )
    
    def toggle_details(self, order_id: int):
        """Toggle order details visibility"""
        if self.expanded_order_id == order_id:
            self.expanded_order_id = None
        else:
            self.expanded_order_id = order_id
        self.display_orders()
    
    def print_order(self, order_id: int):
        """Navigate to print page"""
        self.navigate("job_order_print", order_id=order_id)
    
    def show_status_dialog(self, order_id: int):
        """Show dialog to update order status"""
        order = next((o for o in self.job_orders if o.get("id") == order_id), None)
        if not order:
            return
        
        current_status = order.get("status", "pending")
        
        status_dropdown = ft.Dropdown(
            label=get_text("new_status"),
            value=current_status,
            options=[
                ft.dropdown.Option("pending", get_text("pending")),
                ft.dropdown.Option("quoting", get_text("quoting")),
                ft.dropdown.Option("repairing", get_text("repairing")),
                ft.dropdown.Option("finished", get_text("finished")),
                ft.dropdown.Option("closed", get_text("closed")),
                ft.dropdown.Option("cancelled", get_text("cancelled")),
            ],
            width=300,
        )
        
        def update_status(e):
            try:
                self.client.update_job_order(order_id, status=status_dropdown.value)
                dialog.open = False
                self.load_orders()
                self.show_snack_bar(get_text("status_updated"), is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = ft.AlertDialog(
            title=ft.Text(get_text("update_order_status")),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"{get_text('job_number')}: {order.get('job_no')}", size=14),
                    ft.Container(height=10),
                    status_dropdown,
                ]),
                padding=ft.padding.all(20),
                width=350,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("update"), on_click=update_status),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def create_invoice(self, job_order_id: int):
        """Create invoice for this job order"""
        self.navigate("invoice_create", job_order_id=job_order_id)
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()