# pages/reports/promotion_usage_report.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime, timedelta
import webbrowser
import tempfile
import os
import threading
import time
import asyncio  # เพิ่ม import asyncio

from i18n import get_text, get_current_language


class PromotionUsageReportContent:
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
                self._build_promotion_usage_table(),
                ft.Container(height=20),
                self._build_promotion_quoted_table(),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area]),
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
                                get_text("promotion_usage_report"),
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
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=24, right=24, top=10, bottom=10),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
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
            
            self.report_data = self.client.get_promotion_usage_report(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            self.content_area.controls = [
                self._build_filter_section(),
                ft.Container(height=20),
                self._build_summary_cards(),
                ft.Container(height=20),
                self._build_promotion_usage_table(),
                ft.Container(height=20),
                self._build_promotion_quoted_table(),
            ]
            self.page.update()
        except Exception as ex:
            print(f"Error loading promotion usage report: {ex}")
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
        
        total_used = summary.get('total_promotions_used', 0)
        total_discount = summary.get('total_discount_given', 0)
        total_invoices = summary.get('total_invoices_with_promotion', 0)
        
        cards = ft.Row([
            self._build_stat_card(
                title=get_text("total_promotions_used"),
                value=str(total_used),
                icon=ft.Icons.LOCAL_OFFER,
                color="#8B5CF6",
            ),
            self._build_stat_card(
                title=get_text("total_discount_given"),
                value=self._format_currency(total_discount),
                icon=ft.Icons.DISCOUNT,
                color="#10B981",
            ),
            self._build_stat_card(
                title=get_text("invoices_with_promotion"),
                value=str(total_invoices),
                icon=ft.Icons.RECEIPT,
                color="#3B82F6",
            ),
        ], spacing=20, expand=True)
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("promotion_summary"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                cards,
            ]),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=24, right=24, top=0, bottom=0),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _build_stat_card(self, title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                        bgcolor=color,
                        border_radius=10,
                        padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                    ),
                    ft.Container(expand=True),
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color="#1E293B", text_align=ft.TextAlign.RIGHT),
                ], spacing=12),
                ft.Container(height=4),
                ft.Text(title, size=12, color="#64748B"),
            ]),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100), right=ft.BorderSide(1, ft.Colors.GREY_100), bottom=ft.BorderSide(1, ft.Colors.GREY_100), left=ft.BorderSide(1, ft.Colors.GREY_100)),
            expand=True,
        )
    
    def _build_promotion_usage_table(self):
        promotion_usage = self.report_data.get('promotion_usage', [])
        
        if not promotion_usage:
            return ft.Container(
                content=ft.Column([
                    ft.Text(get_text("promotion_usage_details"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Text(get_text("no_data"), size=14, color="#64748B"),
                        padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=12,
                        alignment=ft.Alignment(0, 0),
                    ),
                ]),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                margin=ft.Margin(left=24, right=24, top=0, bottom=0),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )
        
        # Table header
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("promotion_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("discount_type"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("usage_count"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("total_discount"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=140),
                ft.Text(get_text("total_revenue"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=140),
            ]),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, promo in enumerate(promotion_usage):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            name = promo.get('promotion_name', '-')
            discount_type = promo.get('discount_type', '-')
            discount_value = promo.get('discount_value', 0)
            usage_count = promo.get('usage_count', 0)
            total_discount = promo.get('total_discount_given', 0)
            total_revenue = promo.get('total_revenue', 0)
            
            if discount_type == 'percentage':
                discount_text = f"{discount_type}: {int(discount_value)}%"
            else:
                discount_text = f"{discount_type}: {self._format_currency(discount_value)}"
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(discount_text, size=11, color="#64748B", width=100),
                        ft.Text(str(usage_count), size=13, color="#3B82F6", weight=ft.FontWeight.W_500, width=100),
                        ft.Text(self._format_currency(total_discount), size=12, color="#EF4444", width=140),
                        ft.Text(self._format_currency(total_revenue), size=13, weight=ft.FontWeight.W_500, color="#10B981", width=140),
                    ]),
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("promotion_usage_details"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                header,
                table_body,
            ]),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=24, right=24, top=0, bottom=0),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _build_promotion_quoted_table(self):
        promotion_quoted = self.report_data.get('promotion_quoted', [])
        
        if not promotion_quoted:
            return ft.Container()
        
        # Table header
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("promotion_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("quoted_count"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
                ft.Text(get_text("quoted_discount"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=140),
            ]),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, promo in enumerate(promotion_quoted):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            name = promo.get('promotion_name', '-')
            quoted_count = promo.get('quoted_count', 0)
            quoted_discount = promo.get('quoted_discount', 0)
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(str(quoted_count), size=13, color="#3B82F6", weight=ft.FontWeight.W_500, width=120),
                        ft.Text(self._format_currency(quoted_discount), size=13, color="#64748B", width=140),
                    ]),
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("promotion_quoted_details"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                header,
                table_body,
            ]),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=24, right=24, top=0, bottom=24),
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
        """Export report as A4 PDF and open it"""
        try:
            self._show_snack_bar(get_text("preparing_print"), "info")
            
            # Fetch PDF bytes from backend
            pdf_bytes = self.client.get_promotion_usage_report_pdf(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            if not pdf_bytes:
                self._show_snack_bar(get_text("pdf_export_failed"), "error")
                return
            
            # Ensure output directory exists in project root
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            file_name = f"promotion_usage_report_{self.start_date}_to_{self.end_date}.pdf"
            file_path = os.path.join(output_dir, file_name)
            
            # Write PDF bytes
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)
                
            # Open PDF
            os.startfile(file_path)
            self._show_snack_bar(get_text("pdf_export_success"), "success")
            
        except Exception as ex:
            print(f"Error printing PDF: {ex}")
            self._show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", "error")
    
    def _show_snack_bar(self, message, type="success"):
        """Show snackbar notification - Bottom center with auto width"""
        
        # Remove existing snackbar if any
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