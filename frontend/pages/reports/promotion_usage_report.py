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

from i18n import get_text, get_current_language


class PromotionUsageReportContent:
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
        
        self.load_report()
        
        return main_content
    
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
    
    def _build_stat_card(self, title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                        bgcolor=color,
                        border_radius=10,
                        padding=ft.padding.all(8),
                    ),
                    ft.Container(expand=True),
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color="#1E293B", text_align=ft.TextAlign.RIGHT),
                ], spacing=12),
                ft.Container(height=4),
                ft.Text(title, size=12, color="#64748B"),
            ]),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_100),
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
                        padding=ft.padding.all(40),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=12,
                        alignment=ft.Alignment(0, 0),
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
                ft.Text(get_text("promotion_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("discount_type"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("usage_count"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("total_discount"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=140),
                ft.Text(get_text("total_revenue"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=140),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
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
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
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
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
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
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
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
        summary = self.report_data.get('summary', {})
        promotion_usage = self.report_data.get('promotion_usage', [])
        promotion_quoted = self.report_data.get('promotion_quoted', [])
        
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
            report_title = "ລາຍງານການໃຊ້ໂປຣໂມຊັນ"
            summary_title = "ສະຫຼຸບໂປຣໂມຊັນ"
            usage_title = "ລາຍລະອຽດການໃຊ້ໂປຣໂມຊັນ"
            quoted_title = "ລາຍລະອຽດການກຳນົດໂປຣໂມຊັນ"
            total_used_text = "ຈຳນວນທີ່ໃຊ້ທັງໝົດ"
            total_discount_text = "ສ່ວນຫຼຸດທັງໝົດ"
            total_invoices_text = "ໃບບິນທີ່ໃຊ້ໂປຣໂມຊັນ"
            promotion_name_text = "ຊື່ໂປຣໂມຊັນ"
            discount_type_text = "ປະເພດສ່ວນຫຼຸດ"
            usage_count_text = "ຈຳນວນຄັ້ງທີ່ໃຊ້"
            total_discount_col_text = "ສ່ວນຫຼຸດທັງໝົດ"
            total_revenue_text = "ລາຍຮັບທັງໝົດ"
            quoted_count_text = "ຈຳນວນທີ່ກຳນົດ"
            quoted_discount_text = "ສ່ວນຫຼຸດທີ່ກຳນົດ"
            period_text = "ວັນທີ"
            to_text = "ຫາ"
            printed_text = "ພິມເມື່ອ"
            phone_text = "ໂທ"
        else:
            report_title = "Promotion Usage Report"
            summary_title = "Promotion Summary"
            usage_title = "Promotion Usage Details"
            quoted_title = "Promotion Usage at Quotation Stage"
            total_used_text = "Total Promotions Used"
            total_discount_text = "Total Discount Given"
            total_invoices_text = "Invoices with Promotion"
            promotion_name_text = "Promotion Name"
            discount_type_text = "Discount Type"
            usage_count_text = "Usage Count"
            total_discount_col_text = "Total Discount"
            total_revenue_text = "Total Revenue"
            quoted_count_text = "Quoted Count"
            quoted_discount_text = "Quoted Discount"
            period_text = "Period"
            to_text = "to"
            printed_text = "Printed on"
            phone_text = "Tel"
        
        # Build promotion usage table HTML
        usage_html = ""
        for promo in promotion_usage:
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
            
            usage_html += f"""
            <tr>
                <td>{name}</td>
                <td>{discount_text}</td>
                <td class="text-right">{usage_count}</td>
                <td class="text-right">{self._format_currency(total_discount)}</td>
                <td class="text-right">{self._format_currency(total_revenue)}</td>
            </tr>
            """
        
        # Build promotion quoted table HTML
        quoted_html = ""
        for promo in promotion_quoted:
            name = promo.get('promotion_name', '-')
            quoted_count = promo.get('quoted_count', 0)
            quoted_discount = promo.get('quoted_discount', 0)
            quoted_html += f"""
            <tr>
                <td>{name}</td>
                <td class="text-right">{quoted_count}</td>
                <td class="text-right">{self._format_currency(quoted_discount)}</td>
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
            min-width: 180px;
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
                    <div class="card-value">{summary.get('total_promotions_used', 0)}</div>
                    <div class="card-label">{total_used_text}</div>
                </div>
                <div class="card">
                    <div class="card-value">{self._format_currency(summary.get('total_discount_given', 0))}</div>
                    <div class="card-label">{total_discount_text}</div>
                </div>
                <div class="card">
                    <div class="card-value">{summary.get('total_invoices_with_promotion', 0)}</div>
                    <div class="card-label">{total_invoices_text}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">{usage_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{promotion_name_text}</th>
                        <th>{discount_type_text}</th>
                        <th class="text-right">{usage_count_text}</th>
                        <th class="text-right">{total_discount_col_text}</th>
                        <th class="text-right">{total_revenue_text}</th>
                    </tr>
                </thead>
                <tbody>
                    {usage_html if usage_html else '<tr><td colspan="5" class="text-center">-</td></tr>'}
                </tbody>
            能有
        </div>
        
        <div class="section">
            <div class="section-title">{quoted_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{promotion_name_text}</th>
                        <th class="text-right">{quoted_count_text}</th>
                        <th class="text-right">{quoted_discount_text}</th>
                    </tr>
                </thead>
                <tbody>
                    {quoted_html if quoted_html else '<tr><td colspan="3" class="text-center">-</td></tr>'}
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