# pages/reports/parts_usage_report.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime, timedelta
import webbrowser
import tempfile
import os
import threading
import time

from i18n import get_text, get_current_language


class PartsUsageReportContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
        # Data
        self.report_data = {}
        self.start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.end_date = datetime.now().strftime("%Y-%m-%d")
        
        # UI Components
        self.start_date_picker = None
        self.end_date_picker = None
        
    def build(self):
        header = self._build_header()
        filter_section = self._build_filter_section()
        
        self.content_area = ft.Column(
            [
                filter_section,
                ft.Container(height=20),
                self._build_stock_value_card(),
                ft.Container(height=20),
                self._build_top_parts_table(),
                ft.Container(height=20),
                self._build_low_stock_table(),
                ft.Container(height=20),
                self._build_stock_movement_summary(),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.load_report()
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("parts_usage_report"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.PRINT,
                        icon_size=22,
                        icon_color=ft.Colors.WHITE,
                        tooltip=get_text("print"),
                        on_click=self.print_report,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
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
    
    def _build_filter_section(self):
        self.start_date_picker = ft.TextField(
            label=get_text("start_date"),
            value=self.start_date,
            read_only=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            on_focus=self._pick_start_date,
            width=200,
            border_radius=12,
        )
        
        self.end_date_picker = ft.TextField(
            label=get_text("end_date"),
            value=self.end_date,
            read_only=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            on_focus=self._pick_end_date,
            width=200,
            border_radius=12,
        )
        
        search_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SEARCH, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("search"), size=14, color=ft.Colors.WHITE),
            ], spacing=6),
            on_click=self.load_report,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
        )
        
        refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_report(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(get_text("filter_period"), size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                ]),
                ft.Container(height=12),
                ft.Row([
                    self.start_date_picker,
                    ft.Text(get_text("to"), size=14, color="#64748B"),
                    self.end_date_picker,
                    search_btn,
                    refresh_btn,
                ], spacing=12),
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.symmetric(horizontal=24, vertical=10),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _pick_start_date(self, e):
        def on_date_selected(e):
            self.start_date = e.control.value.strftime("%Y-%m-%d")
            self.start_date_picker.value = self.start_date
            self.page.update()
        
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
        )
        self.page.overlay.append(date_picker)
        date_picker.open = True
        self.page.update()
    
    def _pick_end_date(self, e):
        def on_date_selected(e):
            self.end_date = e.control.value.strftime("%Y-%m-%d")
            self.end_date_picker.value = self.end_date
            self.page.update()
        
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
        )
        self.page.overlay.append(date_picker)
        date_picker.open = True
        self.page.update()
    
    def load_report(self, e=None):
        try:
            self.content_area.controls = [self._build_loading()]
            self.page.update()
            
            self.report_data = self.client.get_parts_usage_report(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            self.content_area.controls = [
                self._build_filter_section(),
                ft.Container(height=20),
                self._build_stock_value_card(),
                ft.Container(height=20),
                self._build_top_parts_table(),
                ft.Container(height=20),
                self._build_low_stock_table(),
                ft.Container(height=20),
                self._build_stock_movement_summary(),
            ]
            self.page.update()
        except Exception as ex:
            print(f"Error loading parts usage report: {ex}")
            self._show_error(str(ex))
    
    def _build_loading(self):
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            height=400,
        )
    
    def _show_error(self, message):
        self.content_area.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                    ft.Text(f"{get_text('error')}: {message}", size=14, color=ft.Colors.RED_600),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("retry")),
                        on_click=self.load_report,
                        style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment(0, 0),
                expand=True,
                height=400,
            )
        ]
        self.page.update()
    
    def _build_stock_value_card(self):
        stock_value = self.report_data.get('stock_value', {})
        
        total_value = stock_value.get('total_stock_value', 0)
        total_parts = stock_value.get('total_parts', 0)
        
        return ft.Container(
            content=ft.Row([
                self._build_info_card(
                    title=get_text("total_stock_value"),
                    value=self._format_currency(total_value),
                    icon=ft.Icons.INVENTORY,
                    color="#10B981",
                ),
                self._build_info_card(
                    title=get_text("total_parts"),
                    value=str(total_parts),
                    icon=ft.Icons.CATEGORY,
                    color="#3B82F6",
                ),
            ], spacing=20, expand=True),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.symmetric(horizontal=24),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _build_info_card(self, title, value, icon, color):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=24, color=ft.Colors.WHITE),
                    bgcolor=color,
                    border_radius=12,
                    padding=ft.padding.all(12),
                ),
                ft.Column([
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Text(title, size=12, color="#64748B"),
                ], spacing=2, expand=True),
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
            expand=True,
        )
    
    def _build_top_parts_table(self):
        top_parts = self.report_data.get('top_parts', [])
        
        if not top_parts:
            return ft.Container()
        
        # Table header
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("part_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("brand"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("quantity_used"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("total_cost"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
                ft.Text(get_text("current_stock"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, part in enumerate(top_parts[:20]):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            name = part.get('part_name', '-')
            brand = part.get('brand', '-')
            total_used = part.get('total_used', 0)
            total_cost = part.get('total_cost', 0)
            current_stock = part.get('current_stock', 0)
            
            # Stock level indicator
            stock_color = "#10B981" if current_stock > 10 else "#F59E0B" if current_stock > 0 else "#EF4444"
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(brand, size=12, color="#64748B", width=100),
                        ft.Text(str(total_used), size=13, color="#1E293B", width=100),
                        ft.Text(self._format_currency(total_cost), size=13, color="#1E293B", width=120),
                        ft.Text(str(current_stock), size=13, color=stock_color, width=100),
                    ]),
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("top_parts_usage"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                header,
                table_body,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.symmetric(horizontal=24),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _build_low_stock_table(self):
        low_stock_parts = self.report_data.get('low_stock_parts', [])
        
        if not low_stock_parts:
            return ft.Container(
                content=ft.Column([
                    ft.Text(get_text("low_stock_alert"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=20, color="#10B981"),
                            ft.Text(get_text("no_low_stock"), size=14, color="#64748B"),
                        ], spacing=8),
                        padding=ft.padding.all(20),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=12,
                    ),
                ]),
                padding=ft.padding.all(20),
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                margin=ft.margin.symmetric(horizontal=24),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )
        
        # Table header
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("part_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("current_stock"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("min_stock"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=80),
                ft.Text(get_text("status"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, part in enumerate(low_stock_parts):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            name = part.get('name', '-')
            stock_qty = part.get('stock_qty', 0)
            min_stock = part.get('min_stock', 5)
            
            if stock_qty <= 0:
                status = get_text("out_of_stock")
                status_color = "#EF4444"
            elif stock_qty <= min_stock / 2:
                status = get_text("critical")
                status_color = "#F59E0B"
            else:
                status = get_text("low")
                status_color = "#FF9800"
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(str(stock_qty), size=13, color="#EF4444", width=100),
                        ft.Text(str(min_stock), size=13, color="#64748B", width=80),
                        ft.Container(
                            content=ft.Text(status, size=11, color=status_color),
                            bgcolor=ft.Colors.with_opacity(0.1, status_color),
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            width=100,
                        ),
                    ]),
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("low_stock_alert"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                header,
                table_body,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.symmetric(horizontal=24),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _build_stock_movement_summary(self):
        stock_movements = self.report_data.get('stock_movements', [])
        
        if not stock_movements:
            return ft.Container()
        
        movement_row = ft.Row(spacing=20, expand=True)
        
        for movement in stock_movements:
            movement_type = movement.get('type', '')
            total_qty = movement.get('total_qty', 0)
            count = movement.get('movement_count', 0)
            
            if movement_type == 'IN':
                icon = ft.Icons.ARROW_DOWNWARD
                color = "#10B981"
                title = get_text("stock_in")
            else:
                icon = ft.Icons.ARROW_UPWARD
                color = "#EF4444"
                title = get_text("stock_out")
            
            movement_row.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                                bgcolor=color,
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Container(expand=True),
                            ft.Text(str(total_qty), size=20, weight=ft.FontWeight.BOLD, color=color),
                        ], spacing=12),
                        ft.Container(height=4),
                        ft.Text(title, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ft.Text(f"{count} {get_text('movements')}", size=11, color="#64748B"),
                    ]),
                    padding=ft.padding.all(16),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_100),
                    expand=True,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("stock_movement_summary"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                movement_row,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.symmetric(horizontal=24, bottom=24),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _format_currency(self, amount):
        try:
            return f"{int(amount or 0):,} KIP"
        except:
            return "0 KIP"
    
    def print_report(self, e):
        """Print report using browser print dialog"""
        try:
            # Show loading indicator
            self._show_snack_bar(get_text("preparing_print"), is_error=False)
            
            # Generate HTML for printing in a separate thread
            def generate_and_print():
                html_content = self._generate_print_html()
                
                # Create temporary HTML file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                    f.write(html_content)
                    temp_path = f.name
                
                # Small delay to ensure file is written
                time.sleep(0.5)
                
                # Open in browser
                webbrowser.open(f'file://{temp_path}')
                
                # Schedule cleanup after a delay (30 seconds)
                def cleanup():
                    time.sleep(30)
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except:
                        pass
                
                threading.Thread(target=cleanup, daemon=True).start()
            
            # Run in background thread to not block UI
            threading.Thread(target=generate_and_print, daemon=True).start()
            
        except Exception as ex:
            print(f"Error printing: {ex}")
            self._show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
    
    def _generate_print_html(self):
        """Generate HTML for printing with Lao/English text"""
        stock_value = self.report_data.get('stock_value', {})
        top_parts = self.report_data.get('top_parts', [])
        low_stock_parts = self.report_data.get('low_stock_parts', [])
        stock_movements = self.report_data.get('stock_movements', [])
        
        # Get shop info
        shop_info = {}
        try:
            shop_info = self.client.get_shop()
        except:
            pass
        
        shop_name = shop_info.get('name', 'JP Auto Shop')
        shop_address = shop_info.get('address', '')
        shop_phone = shop_info.get('phone', '')
        
        # Get current language
        current_lang = 'lo'
        try:
            from i18n import get_current_language
            current_lang = get_current_language()
        except:
            pass
        
        # Set titles based on language
        if current_lang == 'lo':
            report_title = "ລາຍງານການໃຊ້ອາໄຫຼ່"
            summary_title = "ສະຫຼຸບມູນຄ່າສະຕ໋ອກ"
            top_parts_title = "ອາໄຫຼ່ທີ່ໃຊ້ຫຼາຍທີ່ສຸດ"
            low_stock_title = "ອາໄຫຼ່ສະຕ໋ອກໃກ້ໝົດ"
            movement_title = "ສະຫຼຸບການເຄື່ອນໄຫວສະຕ໋ອກ"
            part_name_text = "ຊື່ອາໄຫຼ່"
            brand_text = "ຍີ່ຫໍ້"
            quantity_used_text = "ຈຳນວນທີ່ໃຊ້"
            total_cost_text = "ມູນຄ່າທັງໝົດ"
            current_stock_text = "ສະຕ໋ອກປະຈຸບັນ"
            min_stock_text = "ສະຕ໋ອກຕ່ຳສຸດ"
            status_text = "ສະຖານະ"
            type_text = "ປະເພດ"
            total_qty_text = "ຈຳນວນທັງໝົດ"
            count_text = "ຈຳນວນຄັ້ງ"
            stock_in_text = "ເຂົ້າ"
            stock_out_text = "ອອກ"
            total_stock_value_text = "ມູນຄ່າສະຕ໋ອກທັງໝົດ"
            total_parts_text = "ຈຳນວນອາໄຫຼ່ທັງໝົດ"
            out_of_stock_text = "ໝົດສະຕ໋ອກ"
            critical_text = "ວິກິດ"
            low_text = "ໃກ້ໝົດ"
            period_text = "ວັນທີ"
            to_text = "ຫາ"
            printed_text = "ພິມເມື່ອ"
            phone_text = "ໂທ"
        else:
            report_title = "Parts Usage Report"
            summary_title = "Stock Value Summary"
            top_parts_title = "Top Used Parts"
            low_stock_title = "Low Stock Alert"
            movement_title = "Stock Movement Summary"
            part_name_text = "Part Name"
            brand_text = "Brand"
            quantity_used_text = "Quantity Used"
            total_cost_text = "Total Cost"
            current_stock_text = "Current Stock"
            min_stock_text = "Min Stock"
            status_text = "Status"
            type_text = "Type"
            total_qty_text = "Total Quantity"
            count_text = "Count"
            stock_in_text = "Stock In"
            stock_out_text = "Stock Out"
            total_stock_value_text = "Total Stock Value"
            total_parts_text = "Total Parts"
            out_of_stock_text = "Out of Stock"
            critical_text = "Critical"
            low_text = "Low"
            period_text = "Period"
            to_text = "to"
            printed_text = "Printed on"
            phone_text = "Tel"
        
        # Build top parts table HTML
        top_parts_html = ""
        for part in top_parts[:20]:
            name = part.get('part_name', '-')
            brand = part.get('brand', '-')
            total_used = part.get('total_used', 0)
            total_cost = part.get('total_cost', 0)
            current_stock = part.get('current_stock', 0)
            stock_class = "stock-positive" if current_stock > 10 else "stock-warning" if current_stock > 0 else "stock-danger"
            top_parts_html += f"""
            <tr>
                <td>{name}</td>
                <td>{brand}</td>
                <td class="text-right">{total_used}</td>
                <td class="text-right">{self._format_currency(total_cost)}</td>
                <td class="text-right {stock_class}">{current_stock}</td>
            </tr>
            """
        
        # Build low stock table HTML
        low_stock_html = ""
        for part in low_stock_parts:
            name = part.get('name', '-')
            stock_qty = part.get('stock_qty', 0)
            min_stock = part.get('min_stock', 5)
            
            if stock_qty <= 0:
                status = out_of_stock_text
                status_class = "badge-out"
            elif stock_qty <= min_stock / 2:
                status = critical_text
                status_class = "badge-critical"
            else:
                status = low_text
                status_class = "badge-low"
            
            low_stock_html += f"""
            <tr>
                <td>{name}</td>
                <td class="text-right">{stock_qty}</td>
                <td class="text-right">{min_stock}</td>
                <td><span class="badge {status_class}">{status}</span></td>
            </tr>
            """
        
        # Build stock movement HTML
        movement_html = ""
        for movement in stock_movements:
            movement_type = movement.get('type', '')
            total_qty = movement.get('total_qty', 0)
            count = movement.get('movement_count', 0)
            type_display = stock_in_text if movement_type == 'IN' else stock_out_text
            movement_html += f"""
            <tr>
                <td>{type_display}</td>
                <td class="text-right">{total_qty}</td>
                <td class="text-right">{count}</td>
            </tr>
            """
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report_title}</title>
    <style>
        @media print {{
            body {{ margin: 0; padding: 15px; }}
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
            color: #333;
            background: white;
        }}
        .print-container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 25px;
            border-bottom: 2px solid #1565C0;
            padding-bottom: 15px;
        }}
        .shop-name {{
            font-size: 22px;
            font-weight: bold;
            color: #1565C0;
            margin-bottom: 5px;
        }}
        .shop-address {{
            font-size: 11px;
            color: #666;
        }}
        .shop-phone {{
            font-size: 11px;
            color: #666;
        }}
        .report-title {{
            font-size: 18px;
            font-weight: bold;
            margin-top: 12px;
            color: #1E293B;
        }}
        .period {{
            font-size: 11px;
            color: #64748B;
            margin-top: 5px;
        }}
        .print-date {{
            font-size: 10px;
            color: #94A3B8;
            margin-top: 3px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 14px;
            font-weight: bold;
            background-color: #F1F5F9;
            padding: 8px 12px;
            margin-bottom: 12px;
            border-left: 4px solid #1565C0;
        }}
        .cards-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .card {{
            flex: 1;
            min-width: 200px;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        .card-value {{
            font-size: 18px;
            font-weight: bold;
            color: #1565C0;
        }}
        .card-label {{
            font-size: 11px;
            color: #64748B;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        th {{
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            padding: 8px 10px;
            text-align: left;
            font-weight: bold;
            font-size: 11px;
        }}
        td {{
            border: 1px solid #E2E8F0;
            padding: 6px 10px;
            font-size: 11px;
        }}
        .text-right {{
            text-align: right;
        }}
        .text-center {{
            text-align: center;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
        }}
        .badge-critical {{ background-color: #FEE2E2; color: #DC2626; }}
        .badge-low {{ background-color: #FEF3C7; color: #D97706; }}
        .badge-out {{ background-color: #FEE2E2; color: #DC2626; }}
        .stock-positive {{ color: #10B981; font-weight: bold; }}
        .stock-warning {{ color: #F59E0B; font-weight: bold; }}
        .stock-danger {{ color: #EF4444; font-weight: bold; }}
        .footer {{
            margin-top: 25px;
            text-align: center;
            font-size: 9px;
            color: #94A3B8;
            border-top: 1px solid #E2E8F0;
            padding-top: 12px;
        }}
    </style>
</head>
<body>
    <div class="print-container">
        <div class="header">
            <div class="shop-name">{shop_name}</div>
            <div class="shop-address">{shop_address}</div>
            <div class="shop-phone">{phone_text}: {shop_phone}</div>
            <div class="report-title">{report_title}</div>
            <div class="period">{period_text}: {self.start_date} {to_text} {self.end_date}</div>
            <div class="print-date">{printed_text}: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        </div>
        
        <div class="section">
            <div class="section-title">{summary_title}</div>
            <div class="cards-grid">
                <div class="card">
                    <div class="card-value">{self._format_currency(stock_value.get('total_stock_value', 0))}</div>
                    <div class="card-label">{total_stock_value_text}</div>
                </div>
                <div class="card">
                    <div class="card-value">{stock_value.get('total_parts', 0)}</div>
                    <div class="card-label">{total_parts_text}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">{top_parts_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{part_name_text}</th>
                        <th>{brand_text}</th>
                        <th class="text-right">{quantity_used_text}</th>
                        <th class="text-right">{total_cost_text}</th>
                        <th class="text-right">{current_stock_text}</th>
                    </tr>
                </thead>
                <tbody>
                    {top_parts_html if top_parts_html else '<tr><td colspan="5" class="text-center">-</td></tr>'}
                </tbody>
            能有
        </div>
        
        <div class="section">
            <div class="section-title">{low_stock_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{part_name_text}</th>
                        <th class="text-right">{current_stock_text}</th>
                        <th class="text-right">{min_stock_text}</th>
                        <th>{status_text}</th>
                    </tr>
                </thead>
                <tbody>
                    {low_stock_html if low_stock_html else '<tr><td colspan="4" class="text-center">-</td></tr>'}
                </tbody>
            能有
        </div>
        
        <div class="section">
            <div class="section-title">{movement_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{type_text}</th>
                        <th class="text-right">{total_qty_text}</th>
                        <th class="text-right">{count_text}</th>
                    </tr>
                </thead>
                <tbody>
                    {movement_html if movement_html else '<tr><td colspan="3" class="text-center">-</td></tr>'}
                </tbody>
            能有
        </div>
        
        <div class="footer">
            {shop_name}<br>
            {shop_address} | {phone_text}: {shop_phone}
        </div>
    </div>
    
    <script>
        window.onload = function() {{
            setTimeout(function() {{
                window.print();
            }}, 100);
        }}
    </script>
</body>
</html>"""
        
        return html_content
    
    def _show_snack_bar(self, message, is_error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=2000,
        )
        self.page.update()