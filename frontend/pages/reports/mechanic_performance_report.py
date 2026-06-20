# pages/reports/mechanic_performance_report.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime, timedelta
import os

from i18n import get_text


class MechanicPerformanceReportContent:
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
                self._build_mechanic_performance_table(),
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
                                get_text("mechanic_performance_report"),
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
            
            self.report_data = self.client.get_mechanic_performance_report(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            self.content_area.controls = [
                self._build_filter_section(),
                ft.Container(height=20),
                self._build_summary_cards(),
                ft.Container(height=20),
                self._build_mechanic_performance_table(),
            ]
            self.page.update()
        except Exception as ex:
            print(f"Error loading mechanic performance report: {ex}")
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
                title="ຈຳນວນຊ່າງທັງໝົດ",
                value=str(summary.get('total_mechanics', 0)),
                icon=ft.Icons.PEOPLE_OUTLINE,
                color="#3B82F6",
                subtitle="ຊ່າງສ້ອມແປງທີ່ປະຕິບັດງານ",
            ),
            self._build_stat_card(
                title="ງານທີ່ມອບໝາຍທັງໝົດ",
                value=str(summary.get('total_assigned', 0)),
                icon=ft.Icons.ASSIGNMENT,
                color="#F59E0B",
                subtitle=f"ງານສຳເລັດແລ້ວ: {summary.get('total_completed', 0)}",
            ),
            self._build_stat_card(
                title="ສະເລ່ຍຊົ່ວໂມງຊ່ອມ/ງານ",
                value=f"{summary.get('avg_workshop_hours', 0):.1f} ຊມ",
                icon=ft.Icons.ACCESS_TIME,
                color="#10B981",
                subtitle="ໄລຍະເວລາສ້ອມແປງສະເລ່ຍ",
            ),
        ], spacing=16, expand=True)
        
        return ft.Container(
            content=cards,
            margin=ft.margin.symmetric(horizontal=24),
        )
    
    def _build_stat_card(self, title, value, icon, color, subtitle=""):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                    bgcolor=color,
                    border_radius=10,
                    padding=ft.padding.all(8),
                ),
                ft.Column([
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Text(title, size=12, color="#64748B"),
                    ft.Text(subtitle, size=10, color="#94A3B8") if subtitle else ft.Container(),
                ], spacing=2, expand=True),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_100),
            expand=True,
        )
    
    def _build_mechanic_performance_table(self):
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
                margin=ft.margin.only(left=24, right=24, bottom=24),
                shadow=ft.BoxShadow(
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )
        
        header = ft.Container(
            content=ft.Row([
                ft.Text("ຊື່ຊ່າງສ້ອມແປງ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text("ເບີໂທລະສັບ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
                ft.Text("ມອບໝາຍ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=80),
                ft.Text("ສຳເລັດ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=80),
                ft.Text("ກຳລັງເຮັດ / ລໍຖ້າ / ຢຸດ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=150),
                ft.Text("ສະເລ່ຍຊົ່ວໂມງ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text("ປະສິດທິພາບ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
            ]),
            padding=ft.padding.symmetric(vertical=12, horizontal=16),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, m in enumerate(mechanic_stats):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            # Formulate WIP details
            wip_details = f"{m.get('working_count', 0)} / {m.get('waiting_count', 0)} / {m.get('paused_count', 0)}"
            
            avg_hours_val = m.get('avg_hours')
            avg_hours_text = f"{avg_hours_val:.1f} ຊມ" if avg_hours_val is not None else "-"
            
            eff_val = m.get('efficiency', 0)
            eff_color = "#10B981" if eff_val >= 80 else "#F59E0B" if eff_val >= 50 else "#EF4444"
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(m.get('mechanic_name', '-'), size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(m.get('mechanic_phone', '-'), size=12, color="#64748B", width=120),
                        ft.Text(str(m.get('total_assigned', 0)), size=13, color="#1E293B", width=80),
                        ft.Text(str(m.get('completed_count', 0)), size=13, color="#10B981", weight=ft.FontWeight.BOLD, width=80),
                        ft.Text(wip_details, size=13, color="#64748B", width=150),
                        ft.Text(avg_hours_text, size=13, color="#1E293B", width=100),
                        ft.Container(
                            content=ft.Text(f"{eff_val:.1f}%", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=eff_color,
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            width=90,
                            alignment=ft.Alignment(0, 0),
                        ),
                    ]),
                    padding=ft.padding.symmetric(vertical=12, horizontal=16),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("ສະຖິຕິປະສິດທິພາບຂອງຊ່າງແຕ່ລະຄົນ", size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                header,
                table_body,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.margin.only(left=24, right=24, bottom=24),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def print_report(self, e):
        """Export report as A4 PDF and open it"""
        try:
            self._show_snack_bar(get_text("preparing_print"), is_error=False)
            
            # Fetch PDF bytes from backend
            pdf_bytes = self.client.get_mechanic_performance_report_pdf(
                start_date=self.start_date,
                end_date=self.end_date
            )
            
            # Ensure output directory exists in project root
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            file_name = f"mechanic_performance_report_{self.start_date}_to_{self.end_date}.pdf"
            file_path = os.path.join(output_dir, file_name)
            
            # Write PDF bytes
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)
                
            # Open PDF
            os.startfile(file_path)
            self._show_snack_bar(get_text("pdf_export_success"), is_error=False)
            
        except Exception as ex:
            print(f"Error printing PDF: {ex}")
            self._show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", is_error=True)
            
    def _show_snack_bar(self, message, is_error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=2000,
        )
        self.page.update()
