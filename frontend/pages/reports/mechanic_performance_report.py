# pages/reports/mechanic_performance_report.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime, timedelta
import os
import asyncio  # เพิ่ม import asyncio

from i18n import get_text


class MechanicPerformanceReportContent:
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
        
        row1 = ft.Row([
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
                title="ສະເລ່ຍຊົ່ວໂມງສ້ອມແປງ/ງານ",
                value=f"{summary.get('avg_workshop_hours', 0):.1f} ຊມ",
                icon=ft.Icons.ACCESS_TIME,
                color="#10B981",
                subtitle="ໄລຍະເວລາສ້ອມແປງສະເລ່ຍ",
            ),
        ], spacing=16, expand=True)
        
        row2 = ft.Row([
            self._build_stat_card(
                title="ລາຍຮັບຄ່າແຮງລວມ",
                value=self._format_currency(summary.get('total_labor_revenue', 0)),
                icon=ft.Icons.BUILD,
                color="#0284C7",
                subtitle="ລາຍຮັບຈາກຄ່າແຮງຊ່າງ",
            ),
            self._build_stat_card(
                title="ກຳໄລອາໄຫຼ່ລວມ",
                value=self._format_currency(summary.get('total_parts_profit', 0)),
                icon=ft.Icons.INVENTORY,
                color="#8B5CF6",
                subtitle="ກຳໄລຈາກອາໄຫຼ່ທີ່ໃຊ້",
            ),
            self._build_stat_card(
                title="ກຳໄລລວມທັງໝົດ",
                value=self._format_currency(summary.get('total_profit', 0)),
                icon=ft.Icons.MONETIZATION_ON,
                color="#10B981",
                subtitle="ຄ່າແຮງ + ກຳໄລອາໄຫຼ່",
            ),
        ], spacing=16, expand=True)
        
        return ft.Container(
            content=ft.Column([
                row1,
                ft.Container(height=10),
                row2
            ]),
            margin=ft.Margin(left=24, right=24, top=0, bottom=0),
        )
    
    def _build_stat_card(self, title, value, icon, color, subtitle=""):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                    bgcolor=color,
                    border_radius=10,
                    padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                ),
                ft.Column([
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Text(title, size=12, color="#64748B"),
                    ft.Text(subtitle, size=10, color="#94A3B8") if subtitle else ft.Container(),
                ], spacing=2, expand=True),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100), right=ft.BorderSide(1, ft.Colors.GREY_100), bottom=ft.BorderSide(1, ft.Colors.GREY_100), left=ft.BorderSide(1, ft.Colors.GREY_100)),
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
                        padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=12,
                        alignment=ft.Alignment(0, 0),
                    ),
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
        
        header = ft.Container(
            content=ft.Row([
                ft.Text("ຊື່ຊ່າງສ້ອມແປງ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text("ມອບໝາຍ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=70, text_align=ft.TextAlign.CENTER),
                ft.Text("ສຳເລັດ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=70, text_align=ft.TextAlign.CENTER),
                ft.Text("ສະເລ່ຍຊົ່ວໂມງ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=90, text_align=ft.TextAlign.CENTER),
                ft.Text("ລາຍຮັບຄ່າແຮງ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120, text_align=ft.TextAlign.RIGHT),
                ft.Text("ກຳໄລອາໄຫຼ່", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120, text_align=ft.TextAlign.RIGHT),
                ft.Text("ກຳໄລລວມ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120, text_align=ft.TextAlign.RIGHT),
                ft.Text("ປະສິດທິພາບ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100, text_align=ft.TextAlign.CENTER),
            ]),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, m in enumerate(mechanic_stats):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            avg_hours_val = m.get('avg_hours')
            avg_hours_text = f"{avg_hours_val:.1f} ຊມ" if avg_hours_val is not None else "-"
            
            eff_val = m.get('efficiency', 0)
            eff_color = "#10B981" if eff_val >= 80 else "#F59E0B" if eff_val >= 50 else "#EF4444"
            
            labor_rev = m.get('labor_revenue', 0)
            parts_prof = m.get('parts_profit', 0)
            total_prof = m.get('total_profit', 0)
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(m.get('mechanic_name', '-'), size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(str(m.get('total_assigned', 0)), size=13, color="#1E293B", width=70, text_align=ft.TextAlign.CENTER),
                        ft.Text(str(m.get('completed_count', 0)), size=13, color="#10B981", weight=ft.FontWeight.BOLD, width=70, text_align=ft.TextAlign.CENTER),
                        ft.Text(avg_hours_text, size=13, color="#1E293B", width=90, text_align=ft.TextAlign.CENTER),
                        ft.Text(self._format_currency(labor_rev), size=13, color="#1E293B", width=120, text_align=ft.TextAlign.RIGHT),
                        ft.Text(self._format_currency(parts_prof), size=13, color="#1E293B", width=120, text_align=ft.TextAlign.RIGHT),
                        ft.Text(self._format_currency(total_prof), size=13, weight=ft.FontWeight.BOLD, color="#10B981", width=120, text_align=ft.TextAlign.RIGHT),
                        ft.Container(
                            content=ft.Text(f"{eff_val:.1f}%", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=eff_color,
                            border_radius=12,
                            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                            width=90,
                            alignment=ft.Alignment(0, 0),
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
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
    
    def print_report(self, e):
        """Export report as A4 PDF and open it"""
        try:
            self._show_snack_bar(get_text("preparing_print"), "info")
            
            # Fetch PDF bytes from backend
            pdf_bytes = self.client.get_mechanic_performance_report_pdf(
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
                
            file_name = f"mechanic_performance_report_{self.start_date}_to_{self.end_date}.pdf"
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

    def _format_currency(self, amount):
        try:
            return f"{int(amount or 0):,} KIP"
        except:
            return "0 KIP"