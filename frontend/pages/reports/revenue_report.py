# pages/reports/revenue_report.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime, timedelta
import webbrowser
import tempfile
import os
import threading
import time

from i18n import get_text


class RevenueReportContent:
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
                self._build_summary_cards(),
                ft.Container(height=20),
                self._build_revenue_chart(),
                ft.Container(height=20),
                self._build_payment_methods_table(),
                ft.Container(height=20),
                self._build_daily_revenue_table(),
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
                                get_text("revenue_report"),
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
        
        today_btn = ft.OutlinedButton(
            content=ft.Text(get_text("today"), size=13),
            on_click=lambda e: self._set_quick_filter("today"),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )
        this_week_btn = ft.OutlinedButton(
            content=ft.Text(get_text("this_week"), size=13),
            on_click=lambda e: self._set_quick_filter("week"),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )
        this_month_btn = ft.OutlinedButton(
            content=ft.Text(get_text("this_month"), size=13),
            on_click=lambda e: self._set_quick_filter("month"),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(get_text("filter_period"), size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                    ft.Container(expand=True),
                    today_btn,
                    this_week_btn,
                    this_month_btn,
                ], spacing=12),
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
    
    def _set_quick_filter(self, period):
        today = datetime.now()
        if period == "today":
            self.start_date = today.strftime("%Y-%m-%d")
            self.end_date = today.strftime("%Y-%m-%d")
        elif period == "week":
            start = today - timedelta(days=today.weekday())
            self.start_date = start.strftime("%Y-%m-%d")
            self.end_date = today.strftime("%Y-%m-%d")
        elif period == "month":
            self.start_date = today.replace(day=1).strftime("%Y-%m-%d")
            self.end_date = today.strftime("%Y-%m-%d")
        
        self.start_date_picker.value = self.start_date
        self.end_date_picker.value = self.end_date
        self.load_report()
    
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
            
            self.report_data = self.client.get_revenue_report(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            self.content_area.controls = [
                self._build_filter_section(),
                ft.Container(height=20),
                self._build_summary_cards(),
                ft.Container(height=20),
                self._build_revenue_chart(),
                ft.Container(height=20),
                self._build_payment_methods_table(),
                ft.Container(height=20),
                self._build_daily_revenue_table(),
            ]
            self.page.update()
        except Exception as ex:
            print(f"Error loading revenue report: {ex}")
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
    
    def _build_summary_cards(self):
        summary = self.report_data.get('summary', {})
        
        cards = ft.Row([
            self._build_stat_card(
                title=get_text("total_revenue"),
                value=self._format_currency(summary.get('total_revenue', 0)),
                icon=ft.Icons.MONEY,
                color="#10B981",
                subtitle=f"{summary.get('invoice_count', 0)} {get_text('invoices')}",
            ),
            self._build_stat_card(
                title=get_text("total_discount"),
                value=self._format_currency(summary.get('total_discount', 0)),
                icon=ft.Icons.LOCAL_OFFER,
                color="#F59E0B",
                subtitle=f"{get_text('given')}",
            ),
            self._build_stat_card(
                title=get_text("total_received"),
                value=self._format_currency(summary.get('total_received', 0)),
                icon=ft.Icons.PAYMENT,
                color="#3B82F6",
                subtitle=f"{get_text('collected')}",
            ),
            self._build_stat_card(
                title=get_text("net_profit"),
                value=self._format_currency(summary.get('net_profit', 0)),
                icon=ft.Icons.TRENDING_UP,
                color="#8B5CF6",
                subtitle=f"{get_text('profit')}",
            ),
        ], spacing=20, expand=True)
        
        cost_row = ft.Row([
            self._build_stat_card(
                title=get_text("parts_cost"),
                value=self._format_currency(summary.get('total_parts_cost', 0)),
                icon=ft.Icons.INVENTORY,
                color="#EF4444",
                subtitle=f"{get_text('parts_used')}",
                small=True,
            ),
            self._build_stat_card(
                title=get_text("purchase_cost"),
                value=self._format_currency(summary.get('total_purchase_cost', 0)),
                icon=ft.Icons.LOCAL_SHIPPING,
                color="#EC4899",
                subtitle=f"{get_text('purchases')}",
                small=True,
            ),
        ], spacing=20, expand=True)
        
        return ft.Column([
            cards,
            ft.Container(height=16),
            cost_row,
        ])
    
    def _build_stat_card(self, title, value, icon, color, subtitle="", small=False):
        padding_value = 16 if not small else 12
        padding = ft.padding.all(padding_value)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=20 if small else 24, color=ft.Colors.WHITE),
                        bgcolor=color,
                        border_radius=10,
                        padding=ft.padding.all(8),
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        value,
                        size=14 if small else 18,
                        weight=ft.FontWeight.BOLD,
                        color="#1E293B",
                        text_align=ft.TextAlign.RIGHT,
                    ),
                ], spacing=12),
                ft.Container(height=4),
                ft.Text(title, size=12 if small else 13, color="#64748B"),
                ft.Text(subtitle, size=10, color="#94A3B8") if subtitle else ft.Container(),
            ], spacing=0),
            padding=padding,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_100),
            expand=True,
        )
    
    def _build_revenue_chart(self):
        daily_revenue = self.report_data.get('daily_revenue', [])
        
        if not daily_revenue:
            return ft.Container(
                content=ft.Text(get_text("no_data"), size=14, color="#64748B"),
                padding=ft.padding.all(40),
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                alignment=ft.Alignment(0, 0),
            )
        
        max_revenue = max([d.get('daily_revenue', 0) for d in daily_revenue]) or 1
        
        chart_bars = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO, height=300)
        
        for day in daily_revenue[:30]:
            date = day.get('date', '')
            revenue = day.get('daily_revenue', 0)
            count = day.get('daily_count', 0)
            
            height_percentage = (revenue / max_revenue) * 200
            bar_color = self.primary_color if revenue > 0 else ft.Colors.GREY_300
            
            chart_bars.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            height=height_percentage,
                            width=40,
                            bgcolor=bar_color,
                            border_radius=ft.BorderRadius.only(top_left=8, top_right=8),
                        ),
                        ft.Container(height=4),
                        ft.Text(date[-5:], size=10, color="#64748B"),
                        ft.Text(self._format_currency_short(revenue), size=10, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ft.Text(f"({count})", size=9, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    alignment=ft.Alignment(0, 1),
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(get_text("daily_revenue_trend"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Container(expand=True),
                    ft.Text(f"{get_text('period')}: {self.start_date} - {self.end_date}", size=11, color="#64748B"),
                ]),
                ft.Container(height=16),
                ft.Container(
                    content=chart_bars,
                    padding=ft.padding.all(20),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                ),
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.symmetric(horizontal=24, vertical=0),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _build_payment_methods_table(self):
        payment_methods = self.report_data.get('payment_methods', [])
        
        if not payment_methods:
            return ft.Container()
        
        table_rows = ft.Column(spacing=8)
        
        for method in payment_methods:
            method_name = method.get('payment_method', '-')
            amount = method.get('amount', 0)
            count = method.get('count', 0)
            
            icon = ft.Icons.MONEY if method_name == 'cash' else ft.Icons.CREDIT_CARD
            
            table_rows.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, size=20, color=self.primary_color),
                            bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                            border_radius=10,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(method_name.capitalize(), size=14, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(f"{count} {get_text('invoices')}", size=12, color="#64748B"),
                        ft.Text(self._format_currency(amount), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=10,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("payment_methods"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                table_rows,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.symmetric(horizontal=24, vertical=0),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _build_daily_revenue_table(self):
        daily_revenue = self.report_data.get('daily_revenue', [])
        
        if not daily_revenue:
            return ft.Container()
        
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("date"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
                ft.Text(get_text("revenue"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("invoices"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, day in enumerate(daily_revenue):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(day.get('date', '-'), size=13, color="#1E293B", width=120),
                        ft.Text(self._format_currency(day.get('daily_revenue', 0)), size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(str(day.get('daily_count', 0)), size=13, color="#64748B", width=100),
                    ]),
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("daily_breakdown"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                header,
                table_body,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.symmetric(horizontal=24, vertical=0),
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
    
    def _format_currency_short(self, amount):
        try:
            amount = int(amount or 0)
            if amount >= 1_000_000:
                return f"{amount/1_000_000:.1f}M"
            elif amount >= 1_000:
                return f"{amount/1_000:.0f}K"
            return str(amount)
        except:
            return "0"
    
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
                
                # Open in browser with a small delay and close the file path notification
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
        summary = self.report_data.get('summary', {})
        payment_methods = self.report_data.get('payment_methods', [])
        daily_revenue = self.report_data.get('daily_revenue', [])
        
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
        current_lang = get_current_language() if hasattr(__builtins__, 'get_current_language') else 'lo'
        
        # Set titles based on language
        if current_lang == 'lo':
            report_title = "ລາຍງານລາຍຮັບ"
            summary_title = "ສະຫຼຸບລາຍຮັບ"
            cost_title = "ຕົ້ນທຶນ"
            payment_title = "ວິທີການຊຳລະ"
            daily_title = "ລາຍຮັບລາຍວັນ"
            total_revenue_text = "ລາຍຮັບທັງໝົດ"
            total_discount_text = "ສ່ວນຫຼຸດທັງໝົດ"
            total_received_text = "ເງິນທີ່ຮັບແລ້ວ"
            net_profit_text = "ກຳໄລສຸດທິ"
            parts_cost_text = "ຕົ້ນທຶນອາໄຫຼ່"
            purchase_cost_text = "ຕົ້ນທຶນສັ່ງຊື້"
            payment_method_text = "ວິທີການຊຳລະ"
            invoices_text = "ຈຳນວນໃບບິນ"
            amount_text = "ຍອດເງິນ"
            date_text = "ວັນທີ"
            revenue_text = "ຍອດລາຍຮັບ"
            period_text = "ວັນທີ"
            to_text = "ຫາ"
            printed_text = "ພິມເມື່ອ"
            phone_text = "ໂທ"
        else:
            report_title = "Revenue Report"
            summary_title = "Summary"
            cost_title = "Cost"
            payment_title = "Payment Methods"
            daily_title = "Daily Revenue"
            total_revenue_text = "Total Revenue"
            total_discount_text = "Total Discount"
            total_received_text = "Total Received"
            net_profit_text = "Net Profit"
            parts_cost_text = "Parts Cost"
            purchase_cost_text = "Purchase Cost"
            payment_method_text = "Payment Method"
            invoices_text = "Invoices"
            amount_text = "Amount"
            date_text = "Date"
            revenue_text = "Revenue"
            period_text = "Period"
            to_text = "to"
            printed_text = "Printed on"
            phone_text = "Tel"
        
        # Build payment methods table HTML
        payment_html = ""
        for method in payment_methods:
            method_name = method.get('payment_method', '-')
            amount = method.get('amount', 0)
            count = method.get('count', 0)
            display_name = "ເງິນສົດ" if method_name == 'cash' else "ເຄຣດິດກາດ" if method_name == 'credit' else method_name.capitalize()
            payment_html += f"""
            <tr>
                <td>{display_name}</td>
                <td class="text-right">{count}</td>
                <td class="text-right">{self._format_currency(amount)}</td>
            </tr>
            """
        
        # Build daily revenue table HTML
        daily_html = ""
        for day in daily_revenue:
            daily_html += f"""
            <tr>
                <td>{day.get('date', '-')}</td>
                <td class="text-right">{self._format_currency(day.get('daily_revenue', 0))}</td>
                <td class="text-right">{day.get('daily_count', 0)}</td>
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
            .no-break {{ page-break-inside: avoid; }}
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
            margin-bottom: 20px;
        }}
        .section-title {{
            font-size: 14px;
            font-weight: bold;
            background-color: #F1F5F9;
            padding: 6px 12px;
            margin-bottom: 10px;
            border-left: 4px solid #1565C0;
        }}
        .cards-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 15px;
        }}
        .card {{
            flex: 1;
            min-width: 180px;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        }}
        .card-value {{
            font-size: 18px;
            font-weight: bold;
            color: #1565C0;
        }}
        .card-label {{
            font-size: 10px;
            color: #64748B;
            margin-top: 3px;
        }}
        .card-sub {{
            font-size: 9px;
            color: #94A3B8;
            margin-top: 2px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 12px;
        }}
        th {{
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            padding: 6px 8px;
            text-align: left;
            font-weight: bold;
            font-size: 10px;
        }}
        td {{
            border: 1px solid #E2E8F0;
            padding: 5px 8px;
            font-size: 10px;
        }}
        .text-right {{
            text-align: right;
        }}
        .text-center {{
            text-align: center;
        }}
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
                    <div class="card-value">{self._format_currency(summary.get('total_revenue', 0))}</div>
                    <div class="card-label">{total_revenue_text}</div>
                    <div class="card-sub">{summary.get('invoice_count', 0)} {get_text('invoices')}</div>
                </div>
                <div class="card">
                    <div class="card-value">{self._format_currency(summary.get('total_discount', 0))}</div>
                    <div class="card-label">{total_discount_text}</div>
                </div>
                <div class="card">
                    <div class="card-value">{self._format_currency(summary.get('total_received', 0))}</div>
                    <div class="card-label">{total_received_text}</div>
                </div>
                <div class="card">
                    <div class="card-value">{self._format_currency(summary.get('net_profit', 0))}</div>
                    <div class="card-label">{net_profit_text}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">{cost_title}</div>
            <div class="cards-grid">
                <div class="card">
                    <div class="card-value">{self._format_currency(summary.get('total_parts_cost', 0))}</div>
                    <div class="card-label">{parts_cost_text}</div>
                </div>
                <div class="card">
                    <div class="card-value">{self._format_currency(summary.get('total_purchase_cost', 0))}</div>
                    <div class="card-label">{purchase_cost_text}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">{payment_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{payment_method_text}</th>
                        <th class="text-right">{invoices_text}</th>
                        <th class="text-right">{amount_text}</th>
                    </tr>
                </thead>
                <tbody>
                    {payment_html if payment_html else '<tr><td colspan="3" class="text-center">-</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">{daily_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{date_text}</th>
                        <th class="text-right">{revenue_text}</th>
                        <th class="text-right">{get_text('invoices')}</th>
                    </tr>
                </thead>
                <tbody>
                    {daily_html if daily_html else '<tr><td colspan="3" class="text-center">-</td></tr>'}</tbody>
            
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