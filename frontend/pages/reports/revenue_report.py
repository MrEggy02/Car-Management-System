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
import asyncio

from i18n import get_text


class RevenueReportContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.current_snackbar = None
        
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
        
        # Wrap content_area in a Container with proper padding
        content_container = ft.Container(
            content=self.content_area,
            padding=ft.Padding(left=10, right=10, top=0, bottom=0),
            expand=True,
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_container]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.page.run_task(self._load_data_async)
        
        return main_content

    async def _load_data_async(self):
        await asyncio.sleep(0.1)
        await asyncio.to_thread(self.load_report)
    
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
            padding=ft.Padding(left=24, right=24, top=12, bottom=12),
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
                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
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
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=10, right=10, top=10, bottom=10),
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
        if getattr(self, 'ignore_start_focus', False):
            self.ignore_start_focus = False
            return
            
        def on_date_selected(e):
            self.ignore_start_focus = True
            if e.control.value:
                self.start_date = e.control.value.strftime("%Y-%m-%d")
                self.start_date_picker.value = self.start_date
                self.page.update()
                
        def on_dismiss(e):
            self.ignore_start_focus = True
            
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            on_dismiss=on_dismiss,
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
        )
        self.page.overlay.append(date_picker)
        date_picker.open = True
        self.page.update()
    
    def _pick_end_date(self, e):
        if getattr(self, 'ignore_end_focus', False):
            self.ignore_end_focus = False
            return
            
        def on_date_selected(e):
            self.ignore_end_focus = True
            if e.control.value:
                self.end_date = e.control.value.strftime("%Y-%m-%d")
                self.end_date_picker.value = self.end_date
                self.page.update()
                
        def on_dismiss(e):
            self.ignore_end_focus = True
            
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            on_dismiss=on_dismiss,
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
        
        # Main 4 cards - ใช้ Row ที่มี expand=True และ spacing ที่เหมาะสม
        cards = ft.Row(
            [
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
            ],
            spacing=16,
            expand=True,
        )
        
        # Cost row - 2 cards
        cost_row = ft.Row(
            [
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
            ],
            spacing=16,
            expand=True,
        )
        
        # Wrap with Container that has proper padding
        return ft.Container(
            content=ft.Column([
                cards,
                ft.Container(height=16),
                cost_row,
            ]),
            padding=ft.Padding(left=10, right=10, top=0, bottom=0),
        )
    
    def _build_stat_card(self, title, value, icon, color, subtitle="", small=False):
        padding_value = 16 if not small else 14
        icon_size = 20 if not small else 18
        value_size = 18 if not small else 15
        title_size = 13 if not small else 12
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=icon_size, color=ft.Colors.WHITE),
                        bgcolor=color,
                        border_radius=10,
                        padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        value,
                        size=value_size,
                        weight=ft.FontWeight.BOLD,
                        color="#1E293B",
                        text_align=ft.TextAlign.RIGHT,
                    ),
                ], spacing=12),
                ft.Container(height=4),
                ft.Text(title, size=title_size, color="#64748B"),
                ft.Text(subtitle, size=10, color="#94A3B8") if subtitle else ft.Container(),
            ], spacing=0),
            padding=ft.Padding(left=padding_value, right=padding_value, top=padding_value, bottom=padding_value),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=4,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 1),
            ),
        )
    
    def _build_revenue_chart(self):
        daily_revenue = self.report_data.get('daily_revenue', [])
        
        if not daily_revenue:
            return ft.Container(
                content=ft.Text(get_text("no_data"), size=14, color="#64748B"),
                padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                margin=ft.Margin(left=10, right=10, top=0, bottom=0),
                alignment=ft.Alignment(0, 0),
            )
        
        max_revenue = max([d.get('daily_revenue', 0) for d in daily_revenue]) or 1
        
        chart_bars = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO, height=300)
        
        for day in daily_revenue[:30]:
            date = day.get('date', '')
            revenue = day.get('daily_revenue', 0)
            count = day.get('daily_invoice_count', 0)
            
            height_percentage = (revenue / max_revenue) * 200
            bar_color = self.primary_color if revenue > 0 else ft.Colors.GREY_300
            
            chart_bars.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            height=max(height_percentage, 4),
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
                    padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                ),
            ]),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=10, right=10, top=0, bottom=0),
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
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(method_name.capitalize(), size=14, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(f"{count} {get_text('invoices')}", size=12, color="#64748B"),
                        ft.Text(self._format_currency(amount), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
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
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=10, right=10, top=0, bottom=0),
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
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
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
                        ft.Text(str(day.get('daily_invoice_count', 0)), size=13, color="#64748B", width=100),
                    ]),
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
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
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=10, right=10, top=0, bottom=0),
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
        """Export report as A4 PDF and open it"""
        try:
            self._show_snack_bar(get_text("preparing_print"), "info")
            
            pdf_bytes = self.client.get_revenue_report_pdf(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            if not pdf_bytes:
                self._show_snack_bar(get_text("pdf_export_failed"), "error")
                return
            
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            file_name = f"revenue_report_{self.start_date}_to_{self.end_date}.pdf"
            file_path = os.path.join(output_dir, file_name)
            
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)
                
            os.startfile(file_path)
            self._show_snack_bar(get_text("pdf_export_success"), "success")
            
        except Exception as ex:
            print(f"Error printing PDF: {ex}")
            self._show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", "error")
    
    def _show_snack_bar(self, message, type="success"):
        """Show snackbar notification - Bottom center with auto width"""
        
        if self.current_snackbar:
            try:
                self.page.overlay.remove(self.current_snackbar)
            except:
                pass
            self.current_snackbar = None
        
        if type == "success":
            bgcolor = ft.Colors.GREEN_600
            icon = ft.Icons.CHECK_CIRCLE
        elif type == "error":
            bgcolor = ft.Colors.RED_600
            icon = ft.Icons.ERROR
        else:
            bgcolor = ft.Colors.GREY_800
            icon = ft.Icons.INFO
        
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
        
        snackbar = ft.Container(
            content=snack_content,
            margin=ft.Margin(left=30, right=30, top=0, bottom=20),
            alignment=ft.Alignment(0, 1),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            opacity=0,
        )
        
        self.page.overlay.append(snackbar)
        self.current_snackbar = snackbar
        
        snackbar.opacity = 1
        self.page.update()
        
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
        
        self.page.run_task(dismiss_after_delay)