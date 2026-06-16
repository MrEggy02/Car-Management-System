# pages/reports/service_items_report.py
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


class ServiceItemsReportContent:
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
        self.content_container = None
        
    def build(self):
        header = self._build_header()
        filter_section = self._build_filter_section()
        
        # Main content container
        self.content_container = ft.Column(
            [
                filter_section,
                ft.Container(height=20),
                self._build_loading(),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_container]),
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
                                get_text("service_items_report"),
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
            margin=ft.margin.only(left=24, right=24, top=10, bottom=10),
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
    
    def load_report(self, e=None):
        try:
            self.content_container.controls = [
                self._build_filter_section(),
                ft.Container(height=20),
                self._build_loading(),
            ]
            self.page.update()
            
            self.report_data = self.client.get_service_items_report(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            print("=" * 50)
            print("SERVICE ITEMS DATA:")
            print(f"top_services count: {len(self.report_data.get('top_services', []))}")
            print(f"service_by_brand count: {len(self.report_data.get('service_by_brand', []))}")
            print("=" * 50)
            
            self._build_report_ui()
            
        except Exception as ex:
            print(f"Error loading service items report: {ex}")
            import traceback
            traceback.print_exc()
            self._show_error(str(ex))
    
    def _build_report_ui(self):
        """Build the complete report UI"""
        content_list = [
            self._build_filter_section(),
            ft.Container(height=20),
        ]
        
        # 1. Top Services Table
        content_list.append(self._build_top_services_table())
        content_list.append(ft.Container(height=20))
        
        # 2. Services by Brand Table
        content_list.append(self._build_service_by_brand_table())
        
        self.content_container.controls = content_list
        self.page.update()
    
    def _show_error(self, message):
        self.content_container.controls = [
            self._build_filter_section(),
            ft.Container(height=20),
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
    
    def _build_top_services_table(self):
        top_services = self.report_data.get('top_services', [])
        
        if not top_services:
            return ft.Container(
                content=ft.Column([
                    ft.Text(get_text("top_services"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
                margin=ft.margin.only(left=24, right=24, top=0, bottom=0),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )
        
        # Table header
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("service_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("unit_price"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
                ft.Text(get_text("usage_count"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("quoted_amount"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=140),
                ft.Text(get_text("actual_revenue"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=140),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, service in enumerate(top_services):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            name = service.get('service_name', '-')
            unit_price = service.get('unit_price', 0)
            usage_count = service.get('usage_count', 0)
            quoted_amount = service.get('quoted_amount', 0)
            actual_revenue = service.get('actual_revenue', 0)
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(self._format_currency(unit_price), size=12, color="#64748B", width=120),
                        ft.Text(str(usage_count), size=13, color="#3B82F6", weight=ft.FontWeight.W_500, width=100),
                        ft.Text(self._format_currency(quoted_amount), size=12, color="#64748B", width=140),
                        ft.Text(self._format_currency(actual_revenue), size=13, weight=ft.FontWeight.W_500, color="#10B981", width=140),
                    ]),
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("top_services"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                header,
                table_body,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.only(left=24, right=24, top=0, bottom=0),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _build_service_by_brand_table(self):
        service_by_brand = self.report_data.get('service_by_brand', [])
        
        if not service_by_brand:
            return ft.Container()
        
        # Group by brand
        brand_data = {}
        for item in service_by_brand:
            brand = item.get('brand', 'Other')
            service_name = item.get('service_name', '-')
            service_count = item.get('service_count', 0)
            
            if brand not in brand_data:
                brand_data[brand] = []
            brand_data[brand].append({'name': service_name, 'count': service_count})
        
        # Table header
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("brand"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=150),
                ft.Text(get_text("service_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("service_count"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        row_index = 0
        for brand, services in brand_data.items():
            for service in services[:10]:
                bg = ft.Colors.GREY_50 if row_index % 2 == 0 else ft.Colors.WHITE
                
                table_body.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(brand if row_index == 0 or services.index(service) == 0 else "", 
                                   size=13, weight=ft.FontWeight.W_500, color="#1E293B", width=150),
                            ft.Text(service['name'], size=13, color="#1E293B", expand=True),
                            ft.Text(str(service['count']), size=13, color="#3B82F6", weight=ft.FontWeight.W_500, width=120),
                        ]),
                        padding=ft.padding.symmetric(vertical=12, horizontal=16),
                        bgcolor=bg,
                    )
                )
                row_index += 1
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("services_by_vehicle_brand"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                header,
                table_body,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.only(left=24, right=24, top=0, bottom=24),
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
            self._show_snack_bar(get_text("preparing_print"), is_error=False)
            
            def generate_and_print():
                html_content = self._generate_print_html()
                
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
            self._show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
    
    def _generate_print_html(self):
        """Generate HTML for printing with Lao/English text"""
        top_services = self.report_data.get('top_services', [])
        service_by_brand = self.report_data.get('service_by_brand', [])
        
        shop_info = {}
        try:
            shop_info = self.client.get_shop()
        except:
            pass
        
        shop_name = shop_info.get('name', 'JP Auto Shop')
        shop_address = shop_info.get('address', '')
        shop_phone = shop_info.get('phone', '')
        
        current_lang = 'lo'
        try:
            from i18n import get_current_language
            current_lang = get_current_language()
        except:
            pass
        
        if current_lang == 'lo':
            report_title = "ລາຍງານບໍລິການ"
            top_services_title = "ບໍລິການທີ່ຖືກໃຊ້ຫຼາຍທີ່ສຸດ"
            by_brand_title = "ບໍລິການແບ່ງຕາມຍີ່ຫໍ້ລົດ"
            service_name_text = "ຊື່ບໍລິການ"
            unit_price_text = "ລາຄາຕໍ່ໜ່ວຍ"
            usage_count_text = "ຈຳນວນຄັ້ງທີ່ໃຊ້"
            quoted_amount_text = "ຍອດທີ່ກຳນົດ"
            actual_revenue_text = "ລາຍຮັບຈິງ"
            period_text = "ວັນທີ"
            to_text = "ຫາ"
            printed_text = "ພິມເມື່ອ"
            phone_text = "ໂທ"
            brand_text = "ຍີ່ຫໍ້"
            service_count_text = "ຈຳນວນ"
        else:
            report_title = "Service Items Report"
            top_services_title = "Top Services"
            by_brand_title = "Services by Vehicle Brand"
            service_name_text = "Service Name"
            unit_price_text = "Unit Price"
            usage_count_text = "Usage Count"
            quoted_amount_text = "Quoted Amount"
            actual_revenue_text = "Actual Revenue"
            period_text = "Period"
            to_text = "to"
            printed_text = "Printed on"
            phone_text = "Tel"
            brand_text = "Brand"
            service_count_text = "Count"
        
        # Build top services table HTML
        top_services_html = ""
        for service in top_services:
            top_services_html += f"""
            <tr>
                <td>{service.get('service_name', '-')}</td>
                <td class="text-right">{self._format_currency(service.get('unit_price', 0))}</td>
                <td class="text-right">{service.get('usage_count', 0)}</td>
                <td class="text-right">{self._format_currency(service.get('quoted_amount', 0))}</td>
                <td class="text-right">{self._format_currency(service.get('actual_revenue', 0))}</td>
            </tr>
            """
        
        # Build service by brand HTML
        brand_data = {}
        for item in service_by_brand:
            brand = item.get('brand', 'Other')
            service_name = item.get('service_name', '-')
            service_count = item.get('service_count', 0)
            
            if brand not in brand_data:
                brand_data[brand] = []
            brand_data[brand].append({'name': service_name, 'count': service_count})
        
        brand_html = ""
        for brand, services in brand_data.items():
            for service in services[:15]:
                brand_html += f"""
                <tr>
                    <td>{brand}</td>
                    <td>{service['name']}</td>
                    <td class="text-right">{service['count']}</td>
                </tr>
                """
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report_title}</title>
    <style>
        @media print {{ body {{ margin: 0; padding: 15px; }} }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans', 'DejaVu Sans', 'Segoe UI', Arial, sans-serif;
            font-size: 12px; padding: 20px; color: #333; background: white;
        }}
        .print-container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center; margin-bottom: 25px;
            border-bottom: 2px solid #1565C0; padding-bottom: 15px;
        }}
        .shop-name {{ font-size: 22px; font-weight: bold; color: #1565C0; }}
        .shop-address {{ font-size: 11px; color: #666; }}
        .shop-phone {{ font-size: 11px; color: #666; }}
        .report-title {{ font-size: 18px; font-weight: bold; margin-top: 12px; color: #1E293B; }}
        .period {{ font-size: 11px; color: #64748B; margin-top: 5px; }}
        .print-date {{ font-size: 10px; color: #94A3B8; margin-top: 3px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{
            font-size: 14px; font-weight: bold;
            background-color: #F1F5F9; padding: 8px 12px;
            margin-bottom: 12px; border-left: 4px solid #1565C0;
        }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; }}
        th {{
            background-color: #F8FAFC; border: 1px solid #E2E8F0;
            padding: 6px 8px; text-align: left; font-weight: bold; font-size: 10px;
        }}
        td {{
            border: 1px solid #E2E8F0; padding: 5px 8px; font-size: 10px;
        }}
        .text-right {{ text-align: right; }}
        .text-center {{ text-align: center; }}
        .footer {{
            margin-top: 25px; text-align: center; font-size: 9px;
            color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 12px;
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
            <div class="section-title">{top_services_title}</div>
            <table>
                <thead><tr><th>{service_name_text}</th><th class="text-right">{unit_price_text}</th><th class="text-right">{usage_count_text}</th><th class="text-right">{quoted_amount_text}</th><th class="text-right">{actual_revenue_text}</th></tr></thead>
                <tbody>{top_services_html if top_services_html else '<tr><td colspan="5" class="text-center">-</td></tr>'}</tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">{by_brand_title}</div>
            <table>
                <thead><tr><th>{brand_text}</th><th>{service_name_text}</th><th class="text-right">{service_count_text}</th></tr></thead>
                <tbody>{brand_html if brand_html else '<tr><td colspan="3" class="text-center">-</td></tr>'}</tbody>
            </table>
        </div>
        
        <div class="footer">{shop_name}<br>{shop_address} | {phone_text}: {shop_phone}</div>
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
            content=ft.Text(message, size=13),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=2000,
        )
        self.page.update()