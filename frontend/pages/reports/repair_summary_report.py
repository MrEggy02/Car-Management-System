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
import asyncio  # เพิ่ม import asyncio

from i18n import get_text, get_current_language


class RepairSummaryReportContent:
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
            
            self.report_data = self.client.get_repair_summary_report(
                start_date=self.start_date,
                end_date=self.end_date
            )
            # Build the report UI
            self._build_report_ui()
            
        except Exception as ex:
            print(f"Error loading repair summary: {ex}")
            import traceback
            traceback.print_exc()
            self._show_error(str(ex))
    
    def _build_report_ui(self):
        """Build the complete report UI"""
        content_list = [
            self._build_filter_section(),
            ft.Container(height=20),
        ]
        
        # 1. Status Summary Cards
        content_list.append(self._build_status_summary_cards())
        content_list.append(ft.Container(height=20))
        
        # 2. Repair Statistics
        content_list.append(self._build_repair_stats_card())
        content_list.append(ft.Container(height=20))
        
        # 3. Vehicle Stats Table
        content_list.append(self._build_vehicle_table())
        content_list.append(ft.Container(height=20))
        
        # 4. Mechanic Stats Table
        content_list.append(self._build_mechanic_table())
        content_list.append(ft.Container(height=20))
        
        # 5. Daily Repairs Table
        content_list.append(self._build_daily_table())
        
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
    
    def _build_status_summary_cards(self):
        """Build status summary cards"""
        status_summary = self.report_data.get('status_summary', [])
        
        status_colors = {
            'pending': "#FF9800",
            'working': "#2196F3",
            'completed': "#4CAF50",
            'cancelled': "#F44336"
        }
        status_texts = {
            'pending': get_text("pending"),
            'working': get_text("working"),
            'completed': get_text("completed"),
            'cancelled': get_text("cancelled")
        }
        
        if not status_summary:
            status_summary = [
                {"status": "pending", "count": 0, "percentage": 0},
                {"status": "working", "count": 0, "percentage": 0},
                {"status": "completed", "count": 0, "percentage": 0}
            ]
        
        cards_row = ft.Row(spacing=16, expand=True)
        
        for status in status_summary:
            status_name = status.get('status', '')
            count = status.get('count', 0)
            percentage = status.get('percentage', 0)
            color = status_colors.get(status_name, "#64748B")
            
            cards_row.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(count), size=28, weight=ft.FontWeight.BOLD, color=color),
                        ft.Text(status_texts.get(status_name, status_name), size=13, color="#64748B"),
                        ft.Text(f"{percentage:.1f}%", size=11, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                    expand=True,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("repair_status_summary"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                cards_row,
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
    
    def _build_repair_stats_card(self):
        """Build repair statistics card"""
        repair_stats = self.report_data.get('repair_stats', {})
        
        total = repair_stats.get('total_repairs') or 0
        completed = repair_stats.get('completed_repairs') or 0
        working = repair_stats.get('working_repairs') or 0
        completion_rate = repair_stats.get('completion_rate') or 0
        avg_hours = repair_stats.get('avg_repair_hours') or 0
        
        # Stats row
        stats_row = ft.Row(spacing=16, expand=True)
        
        stat_items = [
            (get_text("total_repairs"), str(total), ft.Icons.CONSTRUCTION, "#3B82F6"),
            (get_text("completed_repairs"), str(completed), ft.Icons.CHECK_CIRCLE, "#10B981"),
            (get_text("completion_rate"), f"{completion_rate:.1f}%", ft.Icons.TRENDING_UP, "#8B5CF6"),
            (get_text("avg_repair_hours"), f"{avg_hours:.1f}h", ft.Icons.SCHEDULE, "#F59E0B"),
        ]
        
        for label, value, icon, color in stat_items:
            stats_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                            bgcolor=color,
                            border_radius=10,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Column([
                            ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Text(label, size=12, color="#64748B"),
                        ], spacing=2, expand=True),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100), right=ft.BorderSide(1, ft.Colors.GREY_100), bottom=ft.BorderSide(1, ft.Colors.GREY_100), left=ft.BorderSide(1, ft.Colors.GREY_100)),
                    expand=True,
                )
            )
        
        # Progress bar
        progress_value = (completed / total * 100) if total > 0 else 0
        progress_bar = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(get_text("progress"), size=12, color="#64748B"),
                    ft.Text(f"{progress_value:.1f}%", size=12, weight=ft.FontWeight.BOLD, color="#10B981"),
                ]),
                ft.Container(height=4),
                ft.ProgressBar(
                    value=progress_value / 100,
                    color="#10B981",
                    bgcolor=ft.Colors.GREY_200,
                    height=6,
                    border_radius=3,
                ),
                ft.Row([
                    ft.Text(f"{get_text('working')}: {working}", size=11, color="#64748B"),
                ], spacing=16),
            ]),
            padding=ft.Padding(left=14, right=14, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
            margin=ft.Margin(left=0, right=0, top=10, bottom=0),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("repair_statistics"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(height=12),
                stats_row,
                ft.Container(height=16),
                progress_bar,
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
    
    def _build_vehicle_table(self):
        """Build vehicle statistics table"""
        vehicle_stats = self.report_data.get('vehicle_stats', [])
        
        if not vehicle_stats:
            return ft.Container(
                content=ft.Column([
                    ft.Text(get_text("top_vehicles_by_brand"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
                ft.Text(get_text("brand"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("repair_count"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("completed"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("avg_hours"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
            ]),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, vehicle in enumerate(vehicle_stats):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(vehicle.get('brand') or '-', size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(str(vehicle.get('repair_count') or 0), size=13, color="#3B82F6", width=100),
                        ft.Text(str(vehicle.get('completed_count') or 0), size=13, color="#10B981", width=100),
                        ft.Text(f"{(vehicle.get('avg_hours') or 0):.1f}h", size=13, color="#64748B", width=100),
                    ]),
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("top_vehicles_by_brand"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
    
    def _build_mechanic_table(self):
        """Build mechanic performance table"""
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
                ft.Text(get_text("mechanic"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                ft.Text(get_text("repair_count"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("completed"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("avg_hours_per_repair"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
            ]),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, mechanic in enumerate(mechanic_stats):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            name = mechanic.get('mechanic_name') or '-'
            repair_count = mechanic.get('repair_count') or 0
            completed_count = mechanic.get('completed_count') or 0
            avg_hours = mechanic.get('avg_hours_per_repair') or 0
            completion_rate = (completed_count / repair_count * 100) if repair_count > 0 else 0
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(str(repair_count), size=13, color="#3B82F6", width=100),
                        ft.Text(str(completed_count), size=13, color="#10B981", width=100),
                        ft.Text(f"{avg_hours:.1f}h ({completion_rate:.0f}%)", size=13, color="#64748B", width=120),
                    ]),
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
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
    
    def _build_daily_table(self):
        """Build daily repairs table"""
        daily_repairs = self.report_data.get('daily_repairs', [])
        
        if not daily_repairs:
            return ft.Container()
        
        # Table header
        header = ft.Container(
            content=ft.Row([
                ft.Text(get_text("date"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
                ft.Text(get_text("daily_repairs"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("completed"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
                ft.Text(get_text("in_progress"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100),
            ]),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_body = ft.Column(spacing=0)
        
        for i, day in enumerate(daily_repairs):
            bg = ft.Colors.GREY_50 if i % 2 == 0 else ft.Colors.WHITE
            
            date = day.get('date') or '-'
            daily_repair = day.get('daily_repairs') or 0
            daily_completed = day.get('daily_completed') or 0
            daily_in_progress = day.get('daily_in_progress') or 0
            
            completed_color = "#10B981" if daily_completed > 0 else "#94A3B8"
            progress_color = "#3B82F6" if daily_in_progress > 0 else "#94A3B8"
            
            table_body.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(date, size=13, color="#1E293B", width=120),
                        ft.Text(str(daily_repair), size=13, color="#1E293B", width=100),
                        ft.Text(str(daily_completed), size=13, color=completed_color, width=100),
                        ft.Text(str(daily_in_progress), size=13, color=progress_color, width=100),
                    ]),
                    padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                    bgcolor=bg,
                )
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(get_text("daily_repair_trend"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
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
            pdf_bytes = self.client.get_repair_summary_report_pdf(
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
                
            file_name = f"repair_summary_report_{self.start_date}_to_{self.end_date}.pdf"
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