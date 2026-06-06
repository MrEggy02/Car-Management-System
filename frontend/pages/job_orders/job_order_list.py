# pages/job_orders/job_order_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime
import webbrowser
import tempfile
import os
import threading
import time

from i18n import get_text, get_current_language
from pages.job_orders.job_order_dialogs import (
    show_create_job_order_dialog,
    show_job_order_detail_dialog,
    show_status_update_dialog
)


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
        self.current_dialog = None
        self.search_field = None
        self.status_filter = None
        self.customers = []
        self.vehicles_by_customer = {}
        
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
        
        # Container for orders list - using GridView
        self.orders_grid = ft.GridView(
            expand=True,
            runs_count=2,
            max_extent=400,
            child_aspect_ratio=0.9,
            spacing=12,
            run_spacing=12,
            padding=ft.padding.only(top=0, left=0, right=0, bottom=0),
        )

    def build(self):
        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("job_order_list"),
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
                            ft.Text(get_text("new_job_order"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.show_create_dialog(),
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
            padding=ft.padding.symmetric(vertical=14, horizontal=26),
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
        
        # Stats row - smaller
        self.stats_container = ft.Container(
            content=ft.Row(
                [
                    self._create_stat_card(get_text("total_orders"), "0", ft.Icons.RECEIPT, "#1565C0"),
                    self._create_stat_card(get_text("pending_orders"), "0", ft.Icons.HOURGLASS_EMPTY, "#FF9800"),
                    self._create_stat_card(get_text("repairing_orders"), "0", ft.Icons.BUILD, "#9C27B0"),
                    self._create_stat_card(get_text("completed_orders"), "0", ft.Icons.CHECK_CIRCLE, "#4CAF50"),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            margin=ft.margin.only(bottom=16),
        )
        
        # Loading indicator
        self.loading_indicator = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=4),
                ft.Container(height=16),
                ft.Text(get_text("loading"), size=14, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=Alignment.CENTER,
            padding=ft.padding.all(40),
            visible=True,
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
                    on_click=lambda e: self.show_create_dialog(),
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
        
        # Main content
        scrollable_content = ft.Column(
            [
                filter_row,
                self.stats_container,
                ft.Container(
                    content=self.orders_grid,
                    expand=True,
                ),
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
            padding=ft.padding.all(20),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.load_orders()
        self.load_customers_and_vehicles()
        
        return main_content
    
    def _create_stat_card(self, title: str, value: str, icon, color: str):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=18, color=ft.Colors.WHITE),
                    bgcolor=color,
                    border_radius=8,
                    padding=ft.padding.all(6),
                ),
                ft.Column([
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Text(title, size=10, color="#64748B"),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(10),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_100),
            expand=True,
        )
    
    def load_customers_and_vehicles(self):
        """Load all customers and their vehicles for dialog"""
        try:
            self.customers = self.client.get_customers() or []
            for customer in self.customers:
                vehicles = self.client.get_vehicles(customer_id=customer.get("id")) or []
                self.vehicles_by_customer[customer.get("id")] = vehicles
        except Exception as ex:
            print(f"Error loading customers: {ex}")
    
    def load_orders(self):
        self.loading_indicator.visible = True
        self.empty_state.visible = False
        self.orders_grid.controls.clear()
        self.page.update()
        
        try:
            orders = self.client.get_job_orders()
            print(f"DEBUG: Loaded orders from API: {len(orders) if orders else 0}")
            
            if orders:
                self.job_orders = orders
            else:
                self.job_orders = []
            
            self._update_stats()
            self.apply_filters()
            self.loading_indicator.visible = False
            self.page.update()
            
        except Exception as ex:
            print(f"Error loading orders: {ex}")
            self.loading_indicator.visible = False
            self.orders_grid.controls.append(
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
        self.apply_filters()
        self.page.update()
    
    def apply_filters(self):
        selected_status = self.status_filter.value if self.status_filter else "all"
        keyword = self.search_field.value.lower() if self.search_field and self.search_field.value else ""
        
        filtered = self.job_orders.copy()
        
        if selected_status and selected_status != "all":
            filtered = [o for o in filtered if o.get("status") == selected_status]
        
        if keyword:
            filtered = [
                o for o in filtered
                if keyword in o.get("job_no", "").lower()
                or keyword in o.get("customer_name", "").lower()
                or keyword in o.get("plate_number", "").lower()
            ]
        
        self.filtered_orders = filtered
        self.orders_grid.controls.clear()
        
        if self.filtered_orders and len(self.filtered_orders) > 0:
            for order in self.filtered_orders:
                self.orders_grid.controls.append(self._create_order_card(order))
            self.empty_state.visible = False
        else:
            self.empty_state.visible = True
        
        self.page.update()
    
    def _create_order_card(self, order: Dict):
        """Create a compact order card"""
        order_id = order.get("id")
        job_no = order.get("job_no", "N/A")
        customer_name = order.get("customer_name", "-")
        plate_number = order.get("plate_number", "-")
        status = order.get("status", "pending")
        receive_date = order.get("receive_date", "")
        
        if receive_date:
            try:
                receive_date = receive_date.split()[0] if " " in receive_date else receive_date[:10]
            except:
                receive_date = "-"
        else:
            receive_date = "-"
        
        status_color = self.status_colors.get(status, "#607D8B")
        status_icon = self.status_icons.get(status, ft.Icons.INFO)
        status_text = get_text(status)
        
        # Compact card
        card = ft.Container(
            content=ft.Column([
                # Header with job number and status
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                        ),
                        ft.Text(job_no, size=14, weight=ft.FontWeight.BOLD, color="#1E293B", expand=True),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(status_icon, size=10, color=ft.Colors.WHITE),
                                ft.Text(status_text, size=9, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                            ], spacing=3),
                            bgcolor=status_color,
                            border_radius=16,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        ),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                ),
                
                # Divider
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                
                # Customer info
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PERSON, size=12, color="#64748B"),
                            ft.Text(customer_name, size=11, color="#1E293B", weight=ft.FontWeight.W_500, expand=True),
                        ], spacing=6),
                        ft.Row([
                            ft.Icon(ft.Icons.DIRECTIONS_CAR, size=12, color="#64748B"),
                            ft.Text(plate_number, size=11, color="#64748B", expand=True),
                        ], spacing=6),
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY, size=12, color="#64748B"),
                            ft.Text(f"{get_text('receive_date')}: {receive_date}", size=10, color="#64748B", expand=True),
                        ], spacing=6),
                    ], spacing=6),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                ),
                
                # Divider
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                
                # Action buttons - horizontal row
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.VISIBILITY,
                            icon_size=16,
                            tooltip=get_text("view_detail"),
                            icon_color=self.primary_color,
                            on_click=lambda e, oid=order_id: self.show_detail_dialog(oid),
                            style=ft.ButtonStyle(padding=ft.padding.all(6)),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.PRINT,
                            icon_size=16,
                            tooltip=get_text("print"),
                            icon_color=self.primary_color,
                            on_click=lambda e, oid=order_id: self.print_job_order(oid),
                            style=ft.ButtonStyle(padding=ft.padding.all(6)),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.UPDATE,
                            icon_size=16,
                            tooltip=get_text("update_status"),
                            icon_color="#64748B",
                            on_click=lambda e, oid=order_id: self.show_status_dialog(oid),
                            style=ft.ButtonStyle(padding=ft.padding.all(6)),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.RECEIPT,
                            icon_size=16,
                            tooltip=get_text("create_invoice"),
                            icon_color=ft.Colors.GREEN_600,
                            on_click=lambda e, oid=order_id: self.create_invoice(oid),
                            style=ft.ButtonStyle(padding=ft.padding.all(6)),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, spacing=0),
                    padding=ft.padding.symmetric(vertical=8),
                ),
            ], spacing=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
            shadow=ft.BoxShadow(
                blur_radius=4,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 1),
            ),
        )
        
        return card
    
    def show_create_dialog(self):
        def on_save(data):
            try:
                result = self.client.create_job_order(
                    customer_id=data["customer_id"],
                    vehicle_id=data["vehicle_id"],
                    problem_description=data["problem_description"],
                    mileage=data["mileage"],
                    fuel_level=data["fuel_level"],
                )
                if result:
                    self._close_dialog()
                    self.load_orders()
                    self.show_success_popup(result.get("job_no", "N/A"))
            except Exception as err:
                self.show_snack_bar(f"{get_text('error')}: {err}", is_error=True)
        
        dialog = show_create_job_order_dialog(
            self.primary_color,
            self.customers,
            self.vehicles_by_customer,
            on_save,
            self._close_dialog
        )
        self._open_dialog(dialog)
    
    def show_detail_dialog(self, order_id):
        order = next((o for o in self.job_orders if o.get("id") == order_id), None)
        if not order:
            return
        
        dialog = show_job_order_detail_dialog(
            order, 
            self.primary_color, 
            self._close_dialog,
            on_print=lambda oid: self.print_job_order(oid)
        )
        self._open_dialog(dialog)
    
    def show_status_dialog(self, order_id):
        order = next((o for o in self.job_orders if o.get("id") == order_id), None)
        if not order:
            return
        
        def on_update(status):
            try:
                self.client.update_job_order(order_id, status=status)
                self._close_dialog()
                self.load_orders()
                self.show_snack_bar(get_text("status_updated"), is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = show_status_update_dialog(
            order,
            self.primary_color,
            on_update,
            self._close_dialog
        )
        self._open_dialog(dialog)
    
    def create_invoice(self, job_order_id):
        self.navigate("invoice_create", job_order_id=job_order_id)
    
    def print_job_order(self, order_id):
        """Print job order using browser print dialog"""
        try:
            self.show_snack_bar(get_text("preparing_print"), is_error=False)
            
            order = next((o for o in self.job_orders if o.get("id") == order_id), None)
            if not order:
                self.show_snack_bar(get_text("order_not_found"), is_error=True)
                return
            
            def generate_and_print():
                html_content = self._generate_print_html(order)
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                    f.write(html_content)
                    temp_path = f.name
                
                time.sleep(0.5)
                webbrowser.open(f'file://{temp_path}')
                
                def cleanup():
                    time.sleep(30)
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except:
                        pass
                
                threading.Thread(target=cleanup, daemon=True).start()
            
            threading.Thread(target=generate_and_print, daemon=True).start()
            
        except Exception as ex:
            print(f"Error printing: {ex}")
            self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
    
    def _generate_print_html(self, order):
        """Generate HTML for printing"""
        job_no = order.get("job_no", "N/A")
        customer_name = order.get("customer_name", "-")
        customer_phone = order.get("customer_phone", "-")
        customer_address = order.get("address", "-")
        plate_number = order.get("plate_number", "-")
        brand = order.get("brand", "-")
        model = order.get("model", "-")
        year = order.get("year", "")
        color = order.get("color", "-")
        receive_date = order.get("receive_date", "")
        problem = order.get("problem_description", "-")
        mileage = order.get("mileage", 0)
        fuel_level = order.get("fuel_level", "-")
        created_by = order.get("created_by_name", self.user.get("fullname", "-"))
        
        if receive_date:
            try:
                dt = datetime.strptime(str(receive_date), "%Y-%m-%d %H:%M:%S")
                receive_date = dt.strftime("%d/%m/%Y %H:%M")
            except:
                try:
                    dt = datetime.strptime(str(receive_date), "%Y-%m-%d")
                    receive_date = dt.strftime("%d/%m/%Y")
                except:
                    pass
        
        shop_info = {}
        try:
            shop_info = self.client.get_shop()
        except:
            pass
        
        shop_name = shop_info.get('name', 'J&P Auto Maxing')
        shop_address = shop_info.get('address', 'Vientiane, Lao PDR')
        shop_phone = shop_info.get('phone', '020 92431434')
        
        receipt_no = f"RCP-{order.get('id', 0):06d}"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Job Order Receipt - {job_no}</title>
    <style>
        @media print {{
            body {{ margin: 0; padding: 0; }}
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Noto Sans', 'DejaVu Sans', 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            padding: 20px;
            background: #e2e8f0;
        }}
        .receipt {{
            max-width: 350px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .receipt-content {{
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 20px 20px 15px 20px;
            background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
            color: white;
        }}
        .shop-name {{
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        .shop-address {{
            font-size: 9px;
            opacity: 0.9;
            margin-top: 4px;
        }}
        .shop-phone {{
            font-size: 10px;
            font-weight: bold;
            margin-top: 6px;
        }}
        .receipt-title {{
            font-size: 11px;
            letter-spacing: 2px;
            margin-top: 8px;
            padding-top: 6px;
            border-top: 1px dashed rgba(255,255,255,0.3);
            display: inline-block;
        }}
        .info-section {{
            margin-bottom: 16px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 10px;
            padding-bottom: 4px;
            border-bottom: 1px dotted #e2e8f0;
        }}
        .info-label {{
            font-weight: 600;
            color: #475569;
            width: 85px;
        }}
        .info-value {{
            color: #1e293b;
            font-weight: 500;
            flex: 1;
            text-align: right;
        }}
        .divider {{
            height: 1px;
            background: repeating-linear-gradient(90deg, #cbd5e1, #cbd5e1 5px, transparent 5px, transparent 10px);
            margin: 12px 0;
        }}
        .divider-dashed {{
            height: 1px;
            background: repeating-linear-gradient(90deg, #94a3b8, #94a3b8 4px, transparent 4px, transparent 8px);
            margin: 10px 0;
        }}
        .section-title {{
            font-size: 11px;
            font-weight: bold;
            color: #1565C0;
            margin-bottom: 8px;
            padding-bottom: 4px;
            border-bottom: 2px solid #1565C0;
            display: inline-block;
        }}
        .problem-box {{
            background: #f8fafc;
            padding: 10px;
            border-radius: 8px;
            margin-top: 6px;
            font-size: 10px;
            line-height: 1.4;
            color: #334155;
            border-left: 3px solid #1565C0;
        }}
        .barcode {{
            height: 20px;
            background: repeating-linear-gradient(90deg, #000, #000 2px, transparent 2px, transparent 6px);
            margin: 12px 0;
        }}
        .footer {{
            text-align: center;
            padding-top: 12px;
            margin-top: 8px;
            border-top: 1px dashed #cbd5e1;
            font-size: 8px;
            color: #94a3b8;
        }}
        .thankyou {{
            font-size: 11px;
            font-weight: bold;
            color: #1565C0;
            margin-bottom: 6px;
        }}
        .stamp {{
            margin-top: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 9px;
            color: #64748b;
        }}
        .signature {{
            border-top: 1px dotted #94a3b8;
            width: 100px;
            padding-top: 4px;
            text-align: center;
        }}
        .receipt-no {{
            font-size: 9px;
            color: #64748b;
            text-align: center;
            margin-top: 4px;
            font-family: monospace;
        }}
        .badge {{
            background: #f1f5f9;
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 8px;
            font-weight: bold;
            margin-bottom: 6px;
        }}
    </style>
</head>
<body>
    <div class="receipt">
        <div class="header">
            <div class="shop-name">{shop_name}</div>
            <div class="shop-address">{shop_address}</div>
            <div class="shop-phone">📞 {shop_phone}</div>
            <div class="receipt-title">ສຳເນົາໃບຮັບລົດ</div>
        </div>
        
        <div class="receipt-content">
            <div class="receipt-no">{receipt_no}</div>
            
            <div style="text-align: center; margin: 8px 0;">
                <span class="badge">ເລກທີໃບຮັບ</span>
                <div style="font-size: 20px; font-weight: bold; color: #1565C0; letter-spacing: 1px; margin-top: 2px;">{job_no}</div>
            </div>
            
            <div class="divider-dashed"></div>
            
            <div class="info-row">
                <span class="info-label">📅 ວັນທີຮັບ</span>
                <span class="info-value">{receive_date}</span>
            </div>
            
            <div class="divider"></div>
            
            <div class="info-section">
                <div class="section-title">👤 ຂໍ້ມູນລູກຄ້າ</div>
                <div class="info-row">
                    <span class="info-label">ຊື່</span>
                    <span class="info-value">{customer_name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ເບີໂທ</span>
                    <span class="info-value">{customer_phone}</span>
                </div>
                {f'<div class="info-row"><span class="info-label">ທີ່ຢູ່</span><span class="info-value">{customer_address[:30]}</span></div>' if customer_address and customer_address != "-" else ''}
            </div>
            
            <div class="divider-dashed"></div>
            
            <div class="info-section">
                <div class="section-title">🚗 ຂໍ້ມູນລົດ</div>
                <div class="info-row">
                    <span class="info-label">ທະບຽນລົດ</span>
                    <span class="info-value">{plate_number}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ຍີ່ຫໍ້/ລຸ້ນ</span>
                    <span class="info-value">{brand} {model}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ສີ/ປີ</span>
                    <span class="info-value">{color if color != "-" else "-"} {f'({year})' if year else ''}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ເລກໄມ</span>
                    <span class="info-value">{mileage:,} km</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ນ້ຳມັນ</span>
                    <span class="info-value">{fuel_level}</span>
                </div>
            </div>
            
            <div class="divider-dashed"></div>
            
            <div class="info-section">
                <div class="section-title">🔧 ບັນຫາທີ່ພົບ</div>
                <div class="problem-box">{problem}</div>
            </div>
            
            <div class="divider-dashed"></div>
            
            <div class="info-row">
                <span class="info-label">🧑‍🔧 ພະນັກງານຮັບ</span>
                <span class="info-value">{created_by}</span>
            </div>
            
            <div class="barcode"></div>
            
            <div class="stamp">
                <div class="signature">ລາຍເຊັນລູກຄ້າ</div>
                <div>📅 {datetime.now().strftime('%d/%m/%Y')}</div>
            </div>
            
            <div class="footer">
                <div class="thankyou">ຂອບໃຈທີ່ໃຊ້ບໍລິການ</div>
                <div>ສອບຖາມເພີ່ມເຕີມ: {shop_phone}</div>
                <div style="margin-top: 6px;">ພິມເມື່ອ: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
            </div>
        </div>
    </div>
    
    <script>
        window.onload = function() {{
            setTimeout(function() {{
                window.print();
            }}, 200);
        }}
    </script>
</body>
</html>"""
        
        return html_content
    
    def show_success_popup(self, job_no):
        def go_to_list(e):
            popup.open = False
            self._close_dialog()
        
        def print_now(e):
            popup.open = False
            order = next((o for o in self.job_orders if o.get("job_no") == job_no), None)
            if order:
                self.print_job_order(order.get("id"))
            self._close_dialog()
        
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.Colors.WHITE,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN_600),
                            alignment=Alignment.CENTER,
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            get_text("job_order_created"),
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            f"{get_text('job_number')}: {job_no}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=self.primary_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            get_text("print_receipt_question"),
                            size=13,
                            color="#64748B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                width=400,
                padding=ft.padding.all(24),
            ),
            actions=[
                ft.TextButton(get_text("later"), on_click=go_to_list),
                ft.ElevatedButton(
                    get_text("print_now"),
                    on_click=print_now,
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def _open_dialog(self, dialog):
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                if self.current_dialog in self.page.overlay:
                    self.page.overlay.remove(self.current_dialog)
            self.current_dialog = dialog
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        except Exception as e:
            print(f"DEBUG: Error opening dialog: {e}")
    
    def _close_dialog(self, e=None):
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=2000,
        )
        self.page.update()