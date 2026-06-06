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
        
    def build(self):
        header = self._build_header()
        filter_section = self._build_filter_section()
        
        self.content_area = ft.Column(
            [
                filter_section,
                ft.Container(height=20),
                self._build_top_services_table(),
                ft.Container(height=20),
                self._build_service_by_brand_table(),
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
            padding=ft.padding.symmetric(vertical=14, horizontal=26),
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
            
            self.report_data = self.client.get_service_items_report(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            self.content_area.controls = [
                self._build_filter_section(),
                ft.Container(height=20),
                self._build_top_services_table(),
                ft.Container(height=20),
                self._build_service_by_brand_table(),
            ]
            self.page.update()
        except Exception as ex:
            print(f"Error loading service items report: {ex}")
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
            margin=ft.margin.symmetric(horizontal=24),
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
        
        # Create accordion for each brand
        accordion_items = []
        
        for brand, services in brand_data.items():
            services_list = ft.Column(spacing=4)
            for service in services[:10]:  # Top 10 per brand
                services_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(service['name'], size=12, color="#1E293B", expand=True),
                            ft.Text(str(service['count']), size=12, color="#3B82F6", weight=ft.FontWeight.W_500),
                        ]),
                        padding=ft.padding.symmetric(vertical=4, horizontal=12),
                    )
                )
            
            accordion_items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Text(brand, size=14, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                                ft.Text(f"{len(services)} {get_text('services')}", size=11, color="#64748B"),
                            ]),
                            padding=ft.padding.all(12),
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=8,
                        ),
                        services_list,
                    ]),
                    margin=ft.margin.only(bottom=8),
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("services_by_vehicle_brand"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Column(accordion_items, spacing=8),
                    padding=ft.padding.all(16),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_100),
                ),
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
        top_services = self.report_data.get('top_services', [])
        service_by_brand = self.report_data.get('service_by_brand', [])
        
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
        current_lang = 'lo'  # default
        try:
            from i18n import get_current_language
            current_lang = get_current_language()
        except:
            pass
        
        # Set titles based on language
        if current_lang == 'lo':
            report_title = "ລາຍງານບໍລິການ"
            summary_title = "ສະຫຼຸບບໍລິການ"
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
            services_text = "ບໍລິການ"
        else:
            report_title = "Service Items Report"
            summary_title = "Service Summary"
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
            services_text = "Services"
        
        # Build top services table HTML
        top_services_html = ""
        for service in top_services:
            name = service.get('service_name', '-')
            unit_price = service.get('unit_price', 0)
            usage_count = service.get('usage_count', 0)
            quoted_amount = service.get('quoted_amount', 0)
            actual_revenue = service.get('actual_revenue', 0)
            top_services_html += f"""
            <tr>
                <td>{name}</td>
                <td class="text-right">{self._format_currency(unit_price)}</td>
                <td class="text-right">{usage_count}</td>
                <td class="text-right">{self._format_currency(quoted_amount)}</td>
                <td class="text-right">{self._format_currency(actual_revenue)}</td>
            </tr>
            """
        
        # Build service by brand HTML
        brand_html = ""
        brand_data = {}
        for item in service_by_brand:
            brand = item.get('brand', 'Other')
            service_name = item.get('service_name', '-')
            service_count = item.get('service_count', 0)
            
            if brand not in brand_data:
                brand_data[brand] = []
            brand_data[brand].append({'name': service_name, 'count': service_count})
        
        for brand, services in brand_data.items():
            brand_html += f"""
            <div class="brand-section">
                <div class="brand-header">
                    <span class="brand-name">{brand}</span>
                    <span class="brand-count">{len(services)} {services_text}</span>
                </div>
                <table class="brand-table">
            """
            for service in services[:15]:
                brand_html += f"""
                    <tr>
                        <td>{service['name']}</td>
                        <td class="text-right">{service['count']}</td>
                    </tr>
                """
            brand_html += """
                </table>
            </div>
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
        .brand-section {{
            margin-bottom: 15px;
            page-break-inside: avoid;
        }}
        .brand-header {{
            background-color: #F1F5F9;
            padding: 8px 12px;
            margin-bottom: 8px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .brand-name {{
            font-size: 13px;
            font-weight: bold;
            color: #1565C0;
        }}
        .brand-count {{
            font-size: 11px;
            color: #64748B;
        }}
        .brand-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 10px;
        }}
        .brand-table td {{
            border: none;
            border-bottom: 1px solid #E2E8F0;
            padding: 6px 8px;
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
            <div class="section-title">{top_services_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{service_name_text}</th>
                        <th class="text-right">{unit_price_text}</th>
                        <th class="text-right">{usage_count_text}</th>
                        <th class="text-right">{quoted_amount_text}</th>
                        <th class="text-right">{actual_revenue_text}</th>
                    </tr>
                </thead>
                <tbody>
                    {top_services_html if top_services_html else '<tr><td colspan="5" class="text-center">-</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">{by_brand_title}</div>
            {brand_html if brand_html else '<div class="text-center" style="padding: 20px;">-</div>'}
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