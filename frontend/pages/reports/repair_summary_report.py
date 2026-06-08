# pages/reports/repair_summary_report.py
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


class RepairSummaryReportContent:
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
                self._build_status_summary(),
                ft.Container(height=20),
                self._build_repair_stats(),
                ft.Container(height=20),
                self._build_vehicle_stats(),
                ft.Container(height=20),
                self._build_mechanic_stats(),
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
                                get_text("repair_summary_report"),
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
            
            self.report_data = self.client.get_repair_summary_report(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # Debug output
            print("=" * 50)
            print("REPAIR SUMMARY REPORT DATA:")
            print(f"report_data: {self.report_data}")
            if self.report_data:
                print(f"status_summary: {self.report_data.get('status_summary', [])}")
                print(f"repair_stats: {self.report_data.get('repair_stats', {})}")
                print(f"vehicle_stats: {self.report_data.get('vehicle_stats', [])}")
                print(f"mechanic_stats: {self.report_data.get('mechanic_stats', [])}")
            print("=" * 50)
            
            self.content_area.controls = [
                self._build_filter_section(),
                ft.Container(height=20),
                self._build_status_summary(),
                ft.Container(height=20),
                self._build_repair_stats(),
                ft.Container(height=20),
                self._build_vehicle_stats(),
                ft.Container(height=20),
                self._build_mechanic_stats(),
            ]
            self.page.update()
        except Exception as ex:
            print(f"Error loading repair summary: {ex}")
            import traceback
            traceback.print_exc()
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
            self._build_filter_section(),
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
    
    def _build_status_summary(self):
        status_summary = self.report_data.get('status_summary', [])
        
        # If no data from API, show message
        if not status_summary:
            return ft.Container(
                content=ft.Column([
                    ft.Text(get_text("repair_status_summary"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
                margin=ft.margin.symmetric(horizontal=24, vertical=0),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )
        
        status_colors = {
            'pending': "#FF9800",
            'working': "#2196F3",
            'paused': "#9C27B0",
            'completed': "#4CAF50",
            'cancelled': "#F44336"
        }
        
        status_texts = {
            'pending': get_text("pending"),
            'working': get_text("working"),
            'paused': get_text("paused"),
            'completed': get_text("completed"),
            'cancelled': get_text("cancelled")
        }
        
        cards = ft.Row(spacing=20, expand=True, wrap=True)
        
        for status in status_summary:
            status_name = status.get('status', '')
            count = status.get('count', 0)
            color = status_colors.get(status_name, "#64748B")
            
            cards.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(count), size=28, weight=ft.FontWeight.BOLD, color=color),
                        ft.Text(status_texts.get(status_name, status_name), size=12, color="#64748B"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    padding=ft.padding.all(16),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_100),
                    expand=True,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("repair_status_summary"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                cards,
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
    
    def _build_repair_stats(self):
        repair_stats = self.report_data.get('repair_stats', {})
        
        total = repair_stats.get('total_repairs', 0)
        completed = repair_stats.get('completed_repairs', 0)
        completion_rate = (completed / total * 100) if total > 0 else 0
        avg_hours = repair_stats.get('avg_repair_hours', 0)
        
        stats_row = ft.Row([
            self._build_stat_card(
                title=get_text("total_repairs"),
                value=str(total),
                icon=ft.Icons.CONSTRUCTION,
                color="#3B82F6",
            ),
            self._build_stat_card(
                title=get_text("completed_repairs"),
                value=str(completed),
                icon=ft.Icons.CHECK_CIRCLE,
                color="#10B981",
            ),
            self._build_stat_card(
                title=get_text("completion_rate"),
                value=f"{completion_rate:.1f}%",
                icon=ft.Icons.TRENDING_UP,
                color="#8B5CF6",
            ),
            self._build_stat_card(
                title=get_text("avg_repair_hours"),
                value=f"{avg_hours:.1f}",
                icon=ft.Icons.SCHEDULE,
                color="#F59E0B",
            ),
        ], spacing=20, expand=True)
        
        # Progress bar for completion rate
        progress = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(get_text("progress"), size=12, color="#64748B"),
                    ft.Text(f"{completion_rate:.1f}%", size=12, weight=ft.FontWeight.BOLD, color="#10B981"),
                ]),
                ft.ProgressBar(
                    value=completion_rate / 100 if completion_rate > 0 else 0,
                    color="#10B981",
                    bgcolor=ft.Colors.GREY_200,
                    height=8,
                    border_radius=4,
                ),
            ]),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("repair_statistics"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                stats_row,
                ft.Container(height=16),
                progress,
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
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
    
    def _build_vehicle_stats(self):
        vehicle_stats = self.report_data.get('vehicle_stats', [])
        
        if not vehicle_stats:
            return ft.Container(
                content=ft.Column([
                    ft.Text(get_text("top_vehicles"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
                margin=ft.margin.symmetric(horizontal=24, vertical=0),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )
        
        # Table header
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("vehicle"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("brand_model"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=150),
                ft.Text(get_text("repair_count"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
                ft.Text(get_text("completed"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, vehicle in enumerate(vehicle_stats):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            license_plate = vehicle.get('license_plate', '-')
            model = vehicle.get('model', '-')
            brand = vehicle.get('brand', '-')
            repair_count = vehicle.get('repair_count', 0)
            completed_count = vehicle.get('completed_count', 0)
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(license_plate, size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(f"{brand} {model}", size=12, color="#64748B", width=150),
                        ft.Text(str(repair_count), size=13, color="#1E293B", width=120),
                        ft.Text(str(completed_count), size=13, color="#10B981", width=100),
                    ]),
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("top_vehicles"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
    
    def _build_mechanic_stats(self):
        mechanic_stats = self.report_data.get('mechanic_stats', [])
        
        if not mechanic_stats:
            return ft.Container(
                content=ft.Column([
                    ft.Text(get_text("mechanic_performance"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
                margin=ft.margin.symmetric(horizontal=24, vertical=0),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )
        
        # Table header
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("mechanic"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("repair_count"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
                ft.Text(get_text("completed"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("completion_rate"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, mechanic in enumerate(mechanic_stats):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            name = mechanic.get('mechanic_name', '-')
            repair_count = mechanic.get('repair_count', 0)
            completed_count = mechanic.get('completed_count', 0)
            completion_rate = (completed_count / repair_count * 100) if repair_count > 0 else 0
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(str(repair_count), size=13, color="#1E293B", width=120),
                        ft.Text(str(completed_count), size=13, color="#10B981", width=100),
                        ft.Text(f"{completion_rate:.0f}%", size=13, color="#3B82F6", width=100),
                    ]),
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("mechanic_performance"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
        status_summary = self.report_data.get('status_summary', [])
        repair_stats = self.report_data.get('repair_stats', {})
        vehicle_stats = self.report_data.get('vehicle_stats', [])
        mechanic_stats = self.report_data.get('mechanic_stats', [])
        
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
            report_title = "ລາຍງານສະຫຼຸບການສ້ອມແປງ"
            status_title = "ສະຫຼຸບສະຖານະການສ້ອມແປງ"
            stats_title = "ສະຖິຕິການສ້ອມແປງ"
            vehicles_title = "ລົດທີ່ມາສ້ອມແປງຫຼາຍທີ່ສຸດ"
            mechanics_title = "ຜົນງານຊ່າງຈັກ"
            total_repairs_text = "ຈຳນວນການສ້ອມແປງທັງໝົດ"
            completed_repairs_text = "ສ້ອມແປງສຳເລັດ"
            completion_rate_text = "ອັດຕາສຳເລັດ"
            avg_hours_text = "ເວລາສະເລ່ຍ (ຊົ່ວໂມງ)"
            progress_text = "ຄວາມຄືບໜ້າ"
            vehicle_text = "ທະບຽນລົດ"
            brand_model_text = "ຍີ່ຫໍ້/ລຸ້ນ"
            repair_count_text = "ຈຳນວນຄັ້ງ"
            completed_text = "ສຳເລັດ"
            mechanic_text = "ຊ່າງຈັກ"
            period_text = "ວັນທີ"
            to_text = "ຫາ"
            printed_text = "ພິມເມື່ອ"
            phone_text = "ໂທ"
            
            status_texts = {
                'pending': "ລໍຖ້າ",
                'working': "ກຳລັງສ້ອມແປງ",
                'paused': "ຢຸດຊົ່ວຄາວ",
                'completed': "ສຳເລັດ",
                'cancelled': "ຍົກເລີກ"
            }
        else:
            report_title = "Repair Summary Report"
            status_title = "Repair Status Summary"
            stats_title = "Repair Statistics"
            vehicles_title = "Top Vehicles by Repair Count"
            mechanics_title = "Mechanic Performance"
            total_repairs_text = "Total Repairs"
            completed_repairs_text = "Completed Repairs"
            completion_rate_text = "Completion Rate"
            avg_hours_text = "Avg Repair Hours"
            progress_text = "Progress"
            vehicle_text = "License Plate"
            brand_model_text = "Brand/Model"
            repair_count_text = "Repair Count"
            completed_text = "Completed"
            mechanic_text = "Mechanic"
            period_text = "Period"
            to_text = "to"
            printed_text = "Printed on"
            phone_text = "Tel"
            
            status_texts = {
                'pending': "Pending",
                'working': "Working",
                'paused': "Paused",
                'completed': "Completed",
                'cancelled': "Cancelled"
            }
        
        # Build status summary cards HTML
        status_cards_html = ""
        for status in status_summary:
            status_name = status.get('status', '')
            count = status.get('count', 0)
            status_display = status_texts.get(status_name, status_name)
            
            if status_name == 'pending':
                color = "#FF9800"
            elif status_name == 'working':
                color = "#2196F3"
            elif status_name == 'paused':
                color = "#9C27B0"
            elif status_name == 'completed':
                color = "#4CAF50"
            elif status_name == 'cancelled':
                color = "#F44336"
            else:
                color = "#64748B"
            
            status_cards_html += f"""
            <div class="status-card">
                <div class="status-count" style="color: {color}">{count}</div>
                <div class="status-label">{status_display}</div>
            </div>
            """
        
        # Build vehicle stats table HTML
        vehicle_html = ""
        for vehicle in vehicle_stats:
            license_plate = vehicle.get('license_plate', '-')
            model = vehicle.get('model', '-')
            brand = vehicle.get('brand', '-')
            repair_count = vehicle.get('repair_count', 0)
            completed_count = vehicle.get('completed_count', 0)
            vehicle_html += f"""
            <tr>
                <td>{license_plate}</td>
                <td>{brand} {model}</td>
                <td class="text-right">{repair_count}</td>
                <td class="text-right">{completed_count}</td>
            </tr>
            """
        
        # Build mechanic stats table HTML
        mechanic_html = ""
        for mechanic in mechanic_stats:
            name = mechanic.get('mechanic_name', '-')
            repair_count = mechanic.get('repair_count', 0)
            completed_count = mechanic.get('completed_count', 0)
            completion_rate = (completed_count / repair_count * 100) if repair_count > 0 else 0
            mechanic_html += f"""
            <tr>
                <td>{name}</td>
                <td class="text-right">{repair_count}</td>
                <td class="text-right">{completed_count}</td>
                <td class="text-right">{completion_rate:.0f}%</td>
            </tr>
            """
        
        total = repair_stats.get('total_repairs', 0)
        completed = repair_stats.get('completed_repairs', 0)
        completion_rate = (completed / total * 100) if total > 0 else 0
        avg_hours = repair_stats.get('avg_repair_hours', 0)
        
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
        .status-cards {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .status-card {{
            flex: 1;
            min-width: 100px;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        .status-count {{
            font-size: 28px;
            font-weight: bold;
        }}
        .status-label {{
            font-size: 11px;
            color: #64748B;
            margin-top: 4px;
        }}
        .stats-cards {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .stat-card {{
            flex: 1;
            min-width: 150px;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 18px;
            font-weight: bold;
            color: #1565C0;
        }}
        .stat-label {{
            font-size: 11px;
            color: #64748B;
            margin-top: 4px;
        }}
        .progress-container {{
            margin-top: 15px;
            padding: 12px;
            background-color: #F8FAFC;
            border-radius: 8px;
        }}
        .progress-bar {{
            height: 8px;
            background-color: #E2E8F0;
            border-radius: 4px;
            margin-top: 8px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background-color: #10B981;
            border-radius: 4px;
            width: {completion_rate}%;
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
            <div class="section-title">{status_title}</div>
            <div class="status-cards">
                {status_cards_html if status_cards_html else '<div class="text-center">-</div>'}
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">{stats_title}</div>
            <div class="stats-cards">
                <div class="stat-card">
                    <div class="stat-value">{total}</div>
                    <div class="stat-label">{total_repairs_text}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{completed}</div>
                    <div class="stat-label">{completed_repairs_text}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{completion_rate:.1f}%</div>
                    <div class="stat-label">{completion_rate_text}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{avg_hours:.1f}</div>
                    <div class="stat-label">{avg_hours_text}</div>
                </div>
            </div>
            <div class="progress-container">
                <div style="display: flex; justify-content: space-between;">
                    <span>{progress_text}</span>
                    <span>{completion_rate:.1f}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">{vehicles_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{vehicle_text}</th>
                        <th>{brand_model_text}</th>
                        <th class="text-right">{repair_count_text}</th>
                        <th class="text-right">{completed_text}</th>
                    </tr>
                </thead>
                <tbody>
                    {vehicle_html if vehicle_html else '<tr><td colspan="4" class="text-center">-</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">{mechanics_title}</div>
            <table>
                <thead>
                    <tr>
                        <th>{mechanic_text}</th>
                        <th class="text-right">{repair_count_text}</th>
                        <th class="text-right">{completed_text}</th>
                        <th class="text-right">{completion_rate_text}</th>
                    </tr>
                </thead>
                <tbody>
                    {mechanic_html if mechanic_html else '<tr><td colspan="4" class="text-center">-</td></tr>'}
                </tbody>
            </table>
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