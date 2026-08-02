# pages/quotations/quotation_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import tempfile
import os
import webbrowser
import threading
import time
from datetime import datetime, timedelta

from i18n import get_text, get_current_language
from pages.quotations.quotation_dialogs import (
    show_quotation_detail_dialog,
    show_delete_quotation_dialog,
    show_update_status_dialog
)

import asyncio

class QuotationListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, job_order_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.job_order_id = job_order_id
        self.quotations = []
        self.filtered_quotations = []
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.current_snackbar = None
        self.selected_quotation = None
        self.detail_dialog = None
        self.search_field = None
        self.date_from_field = None
        self.date_to_field = None
        self.status_filter = "all"
        self.current_date_filter = "all"  # all, today, week, month
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.current_dialog = None
        self.kpi_container = None
        self.parts_list = []
        self.services_list = []

    def build(self):
        # ส่วนหัว
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("quotation_list"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("new_quotation"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.navigate("quotation_create"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=0,
                            padding=ft.Padding(left=20, right=20, top=12, bottom=12),
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
        
        # ส่วน KPI Cards
        self.kpi_container = ft.Container(
            content=ft.Row([], spacing=12),
            padding=ft.Padding(left=0, right=0, top=8, bottom=8),
        )
        
        # ─── Search Bar with Date Filters in one row ───
        self.search_field = ft.TextField(
            hint_text=get_text("search_quotation"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            expand=True,
            on_change=self.filter_quotations,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        # Date from field
        self.date_from_field = ft.TextField(
            hint_text=get_text("date_from"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            suffix=ft.IconButton(icon=ft.Icons.CLOSE, on_click=self._clear_date_from, icon_size=16),
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            width=140,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            read_only=True,
            on_focus=self._pick_date_from,
        )

        # Date to field
        self.date_to_field = ft.TextField(
            hint_text=get_text("date_to"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            suffix=ft.IconButton(icon=ft.Icons.CLOSE, on_click=self._clear_date_to, icon_size=16),
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            width=140,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            read_only=True,
            on_focus=self._pick_date_to,
        )
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_quotations(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        # ─── Filter row (all in one line) ───
        filter_row = ft.Row([
            self.search_field,
            self.date_from_field,
            self.date_to_field,
            refresh_button,
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        # ─── Table ───
        table_header = self._create_table_header()
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        table_content = ft.Column([
            table_header,
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            self.table_rows,
        ], spacing=0, expand=True)

        table_scroll_container = ft.Container(
            content=table_content,
            bgcolor=ft.Colors.WHITE,
            width=1050,
            expand=True,
        )

        table_container = ft.Container(
            content=ft.Row([table_scroll_container], scroll=ft.ScrollMode.AUTO, expand=True),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            border_radius=ft.BorderRadius.only(
                top_left=12, top_right=12, bottom_left=12, bottom_right=12
            ),
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.GREY_200),
                right=ft.BorderSide(1, ft.Colors.GREY_200),
                bottom=ft.BorderSide(1, ft.Colors.GREY_200),
                left=ft.BorderSide(1, ft.Colors.GREY_200)
            ),
            bgcolor=ft.Colors.WHITE,
            expand=True,
            height=600,
        )
        
        # ─── Pagination ───
        self.pagination_container = ft.Container(
            padding=ft.Padding(left=20, right=20, top=12, bottom=12),
            bgcolor="#F5F7FA",
        )
        
        # ─── Loading & Empty State ───
        self.loading_indicator = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=4),
                ft.Container(height=16),
                ft.Text(get_text("loading"), size=14, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=Alignment.CENTER,
            padding=ft.Padding(left=40, right=40, top=40, bottom=40),
            visible=False,
        )
        
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.REQUEST_QUOTE, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=16),
                ft.Text(get_text("no_quotations_found"), size=18, weight=ft.FontWeight.W_500, color="#64748B"),
                ft.Text(get_text("click_add_to_register"), size=13, color="#94A3B8"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text(get_text("new_quotation"), size=14),
                    on_click=lambda e: self.navigate("quotation_create"),
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=Alignment.CENTER,
            padding=ft.Padding(left=60, right=60, top=60, bottom=60),
            visible=False,
        )
        
        # ─── Main Content Area (with vertical scroll) ───
        content_area = ft.Container(
            content=ft.Column([
                self.kpi_container,
                filter_row,  # All filters in one row
                table_container,
                self.pagination_container,
                self.loading_indicator,
                self.empty_state,
            ], expand=True, spacing=12, scroll=ft.ScrollMode.AUTO),  # Enable vertical scroll
            expand=True,
            padding=ft.Padding(left=20, right=20, top=10, bottom=10),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area], expand=True, scroll=ft.ScrollMode.AUTO),  # Enable scroll on main too
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.page.run_task(self._load_data_async)
        
        return main_content

    async def _load_data_async(self):
        await asyncio.sleep(0.1)
        await asyncio.to_thread(self.load_quotations)
    
    # ─────────────────────────────────────────────────────────────
    # DATE PICKER METHODS
    # ─────────────────────────────────────────────────────────────
    def _clear_date_from(self, e):
        self.date_from_field.value = ""
        self.current_date_filter = "all"
        self.page.update()
        self.filter_quotations(None)
        self._update_kpi_cards()

    def _clear_date_to(self, e):
        self.date_to_field.value = ""
        self.current_date_filter = "all"
        self.page.update()
        self.filter_quotations(None)
        self._update_kpi_cards()

    def _pick_date_from(self, e):
        if getattr(self, 'ignore_from_focus', False):
            self.ignore_from_focus = False
            return
            
        def on_date_selected(e):
            self.ignore_from_focus = True
            if e.control.value:
                self.date_from_field.value = e.control.value.strftime("%Y-%m-%d")
                self.current_date_filter = "all"
                self.page.update()
                self.filter_quotations(None)
                self._update_kpi_cards()
                
        def on_dismiss(e):
            self.ignore_from_focus = True
        
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            on_dismiss=on_dismiss,
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
        )
        self.page.overlay.append(date_picker)
        date_picker.open = True
        self.page.update()
        
    def _pick_date_to(self, e):
        if getattr(self, 'ignore_to_focus', False):
            self.ignore_to_focus = False
            return
            
        def on_date_selected(e):
            self.ignore_to_focus = True
            if e.control.value:
                self.date_to_field.value = e.control.value.strftime("%Y-%m-%d")
                self.current_date_filter = "all"
                self.page.update()
                self.filter_quotations(None)
                self._update_kpi_cards()
                
        def on_dismiss(e):
            self.ignore_to_focus = True
        
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            on_dismiss=on_dismiss,
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
        )
        self.page.overlay.append(date_picker)
        date_picker.open = True
        self.page.update()

    def _update_kpi_cards(self):
        """Update KPI cards highlight"""
        if self.kpi_container:
            self.kpi_container.content = self._build_kpi_cards()
            self.page.update()
    
    # ─────────────────────────────────────────────────────────────
    # KPI CARDS
    # ─────────────────────────────────────────────────────────────
    def _build_kpi_cards(self):
        statuses = [
            ("draft",    "#FF9800", ft.Icons.EDIT_DOCUMENT),
            ("approved", "#4CAF50", ft.Icons.CHECK_CIRCLE),
            ("rejected", "#F44336", ft.Icons.CANCEL),
        ]
        status_texts = {
            "draft": get_text("draft"),
            "approved": get_text("approved"),
            "rejected": get_text("rejected"),
        }
        counts = {s: 0 for s, _, __ in statuses}
        for q in self.quotations:
            st = q.get("status", "draft")
            if st in counts:
                counts[st] += 1

        cards = []
        for status, color, icon in statuses:
            count = counts[status]
            label = status_texts.get(status, status)
            is_active = (self.status_filter == status)
            card = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, size=22, color=ft.Colors.WHITE),
                            bgcolor=color,
                            border_radius=10,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Column(
                            [
                                ft.Text(str(count), size=22, weight=ft.FontWeight.BOLD, color="#1E293B"),
                                ft.Text(label, size=11, color="#64748B"),
                            ],
                            spacing=1,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                border=ft.Border(top=ft.BorderSide(2, color), right=ft.BorderSide(2, color), bottom=ft.BorderSide(2, color), left=ft.BorderSide(2, color)) if is_active else ft.Border(top=ft.BorderSide(1, "#E2E8F0"), right=ft.BorderSide(1, "#E2E8F0"), bottom=ft.BorderSide(1, "#E2E8F0"), left=ft.BorderSide(1, "#E2E8F0")),
                expand=True,
                ink=True,
                on_click=lambda e, s=status: self._kpi_filter(s),
                shadow=ft.BoxShadow(
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                ),
            )
            cards.append(card)

        total = len(self.quotations)
        is_all = self.status_filter == "all"
        all_card = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.LIST_ALT, size=22, color=ft.Colors.WHITE),
                        bgcolor="#607D8B",
                        border_radius=10,
                        padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                    ),
                    ft.Column(
                        [
                            ft.Text(str(total), size=22, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Text(get_text("all_status"), size=11, color="#64748B"),
                        ],
                        spacing=1,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(top=ft.BorderSide(2, "#607D8B"), right=ft.BorderSide(2, "#607D8B"), bottom=ft.BorderSide(2, "#607D8B"), left=ft.BorderSide(2, "#607D8B")) if is_all else ft.Border(top=ft.BorderSide(1, "#E2E8F0"), right=ft.BorderSide(1, "#E2E8F0"), bottom=ft.BorderSide(1, "#E2E8F0"), left=ft.BorderSide(1, "#E2E8F0")),
            expand=True,
            ink=True,
            on_click=lambda e: self._kpi_filter("all"),
            shadow=ft.BoxShadow(
                blur_radius=4,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            ),
        )

        return ft.Row([all_card] + cards, spacing=12, expand=True)

    def _kpi_filter(self, status: str):
        self.status_filter = status
        self.current_page = 1
        self.filter_quotations(None)
    
    # ─────────────────────────────────────────────────────────────
    # TABLE
    # ─────────────────────────────────────────────────────────────
    def _create_table_header(self):
        """สร้างส่วนหัวตาราง"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("quotation_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("customer_name"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("plate_number"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("total"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=10, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("actions"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=180,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _create_table_row(self, quote: Dict, index: int):
        """สร้างแถวในตาราง"""
        quote_id = quote.get("id")
        customer_name = quote.get("customer_name", "-")
        plate_number = quote.get("plate_number", "-")
        total_price = quote.get("net_total", quote.get("sub_total", 0))
        status = quote.get("status", "draft")
        created_at = quote.get("created_at", "").split()[0] if quote.get("created_at") else "-"
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        status_colors = {
            "draft": "#FF9800",
            "approved": "#4CAF50",
            "rejected": "#F44336"
        }
        status_texts = {
            "draft": get_text("draft"),
            "approved": get_text("approved"),
            "rejected": get_text("rejected")
        }
        
        # Clickable badge for draft/rejected, static for approved
        is_approved = status == "approved"
        
        if is_approved:
            # Approved - ไม่สามารถคลิกเปลี่ยนสถานะได้ (static)
            status_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                    ft.Text(status_texts.get(status, status), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=status_colors.get(status, "#607D8B"),
                border_radius=12,
                padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            )
        else:
            # Draft / Rejected - คลิกเปลี่ยนสถานะได้
            status_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                    ft.Text(status_texts.get(status, status), size=11, color=ft.Colors.WHITE),
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=status_colors.get(status, "#607D8B"),
                border_radius=12,
                padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                on_click=lambda e, qid=quote_id, cur_status=status: self.show_update_status_dialog(qid, cur_status),
            )
        
        view_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("view"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, qid=quote_id: self.show_quotation_detail(qid),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        print_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("print"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, qid=quote_id: self.print_quotation(qid),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        # Delete button - disabled for approved status
        if status == "approved":
            delete_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.GREY_400),
                    ft.Text(get_text("delete"), size=12, color=ft.Colors.GREY_400),
                ], spacing=4),
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                border_radius=6,
                tooltip=get_text("cannot_delete_approved_quotation"),
            )
        else:
            delete_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
                    ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
                ], spacing=4),
                on_click=lambda e, qid=quote_id: self.delete_quotation(qid),
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                border_radius=6,
            )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(f"QT-{quote_id:04d}", size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(customer_name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(plate_number, size=12, color="#64748B", max_lines=1),
                    width=120,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(f"{int(total_price):,} KIP", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=10, top=0, bottom=0),
                ),
                ft.Container(
                    content=status_badge,
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(created_at, size=12, color="#64748B"),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Row([view_btn, print_btn, delete_btn], spacing=4),
                    width=180,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    # ─────────────────────────────────────────────────────────────
    # DATA LOADING & FILTERING
    # ─────────────────────────────────────────────────────────────
    def load_quotations(self):
        """โหลดข้อมูลใบเสนอราคาจาก API"""
        self.loading_indicator.visible = True
        self.empty_state.visible = False
        self.table_rows.controls.clear()
        self.page.update()
        
        try:
            quotations = self.client.get_quotations(job_order_id=self.job_order_id)
            self.quotations = quotations
            self.filtered_quotations = quotations.copy()
            self.kpi_container.content = self._build_kpi_cards()
            self.filter_quotations(None)
        except Exception as ex:
            print(f"Error loading quotations: {ex}")
            self.loading_indicator.visible = False
            self.page.update()
    
    def _get_quote_date(self, quote: Dict) -> datetime.date:
        """Extract date from quotation"""
        created_at = quote.get("created_at", "")
        if not created_at:
            return datetime.now().date()
        try:
            return datetime.strptime(str(created_at)[:10], "%Y-%m-%d").date()
        except:
            return datetime.now().date()
    
    def filter_quotations(self, e):
        """กรองใบเสนอราคาตามคำค้นหา สถานะ และวันที่"""
        keyword = self.search_field.value.lower() if self.search_field and self.search_field.value else ""
        self.current_page = 1
        
        # Start with all quotations
        filtered = self.quotations.copy()
        
        # Apply status filter
        if self.status_filter and self.status_filter != "all":
            filtered = [q for q in filtered if q.get("status") == self.status_filter]
        
        # Apply KPI date filter (if any)
        if self.current_date_filter == "today":
            today = datetime.now().date()
            filtered = [q for q in filtered if self._get_quote_date(q) == today]
        elif self.current_date_filter == "week":
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            filtered = [q for q in filtered if week_start <= self._get_quote_date(q) <= today]
        elif self.current_date_filter == "month":
            today = datetime.now().date()
            month_start = today.replace(day=1)
            filtered = [q for q in filtered if month_start <= self._get_quote_date(q) <= today]
        
        # Apply search filter
        if keyword:
            filtered = [
                q for q in filtered
                if keyword in f"QT-{q.get('id', 0):04d}".lower()
                or keyword in q.get("customer_name", "").lower()
                or keyword in q.get("plate_number", "").lower()
                or keyword in (q.get("job_no") or "").lower()
            ]
        
        # Apply date range filter
        date_from_str = self.date_from_field.value.strip() if self.date_from_field and self.date_from_field.value else ""
        date_to_str = self.date_to_field.value.strip() if self.date_to_field and self.date_to_field.value else ""
        
        try:
            date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date() if date_from_str else None
        except ValueError:
            date_from = None
        
        try:
            date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date() if date_to_str else None
        except ValueError:
            date_to = None
        
        if date_from or date_to:
            result = []
            for q in filtered:
                quote_date = self._get_quote_date(q)
                if date_from and quote_date < date_from:
                    continue
                if date_to and quote_date > date_to:
                    continue
                result.append(q)
            filtered = result
        
        self.filtered_quotations = filtered
        self.display_quotations()
    
    def display_quotations(self):
        """แสดงใบเสนอราคาพร้อมการแบ่งหน้า"""
        self.table_rows.controls.clear()
        
        total_items = len(self.filtered_quotations)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_quotations[start_idx:end_idx]
        
        if page_items and len(page_items) > 0:
            self.loading_indicator.visible = False
            self.empty_state.visible = False
            for i, quote in enumerate(page_items):
                self.table_rows.controls.append(self._create_table_row(quote, start_idx + i))
        else:
            self.loading_indicator.visible = False
            self.empty_state.visible = True
        
        self.update_pagination_controls()
        self.page.update()
    
    def update_pagination_controls(self):
        """อัปเดตตัวควบคุมการแบ่งหน้า"""
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_quotations)} {get_text('of')} {len(self.quotations)} {get_text('results')}",
                    size=12,
                    color="#64748B",
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_LEFT,
                            icon_size=20,
                            on_click=self.prev_page,
                            disabled=prev_disabled,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                        ft.Container(
                            content=ft.Text(f"{self.current_page}/{self.total_pages}", size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                            padding=ft.Padding(left=15, right=15, top=0, bottom=0),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_RIGHT,
                            icon_size=20,
                            on_click=self.next_page,
                            disabled=next_disabled,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                    ]),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_quotations()
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_quotations()
    
    # ─────────────────────────────────────────────────────────────
    # ACTIONS
    # ─────────────────────────────────────────────────────────────
    def show_quotation_detail(self, quotation_id: int):
        """แสดงรายละเอียดใบเสนอราคาใน dialog"""
        self.loading_indicator.visible = True
        self.page.update()
        
        try:
            quotation = self.client.get_quotation(quotation_id)
            self.loading_indicator.visible = False
            
            if quotation:
                def on_print(qid):
                    self.print_quotation(qid)
                
                dialog = show_quotation_detail_dialog(
                    quotation,
                    self.primary_color,
                    on_print,
                    self._close_dialog
                )
                self._open_dialog(dialog)
            else:
                self.show_snack_bar(get_text("error_loading_quotation"), "error")
        except Exception as ex:
            self.loading_indicator.visible = False
            self.show_snack_bar(f"Error: {str(ex)}", "error")
            self.page.update()
    
    def show_update_status_dialog(self, quotation_id: int, current_status: str):
        """แสดง dialog สำหรับอัปเดตสถานะใบเสนอราคา"""
        
        # ไม่อนุญาตให้เปลี่ยนสถานะถ้าอนุมัติแล้ว
        if current_status == "approved":
            self.show_snack_bar(get_text("cannot_change_approved_quotation"), "error")
            return
        
        def on_update(qid, new_status):
            try:
                self.client.update_quotation_status(qid, new_status)
                self._close_dialog()
                self.load_quotations()
                self.show_snack_bar(f"{get_text('status_updated_to')} {get_text(new_status)}", "success")
            except Exception as ex:
                print(f"DEBUG: Error in update: {ex}")
                self.show_snack_bar(f"Error: {str(ex)}", "error")
        
        dialog = show_update_status_dialog(
            quotation_id,
            current_status,
            self.primary_color,
            on_update,
            self._close_dialog
        )
        self._open_dialog(dialog)
    
    def delete_quotation(self, quotation_id: int):
        """ลบใบเสนอราคาพร้อมยืนยัน"""
        quote = next((q for q in self.quotations if q.get("id") == quotation_id), None)
        quote_name = f"QT-{quotation_id:04d}" if quote else get_text("this_quotation")
        
        # ห้ามลบใบเสนอราคาที่อนุมัติแล้ว
        if quote and quote.get("status") == "approved":
            self.show_snack_bar(get_text("cannot_delete_approved_quotation"), "error")
            return
        
        def on_confirm():
            try:
                self.client.delete_quotation(quotation_id)
                self._close_dialog()
                self.load_quotations()
                self.show_snack_bar(f"{get_text('delete_success')}", "success")
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", "error")
        
        dialog = show_delete_quotation_dialog(
            quote_name,
            on_confirm,
            self._close_dialog
        )
        self._open_dialog(dialog)
    
    def print_quotation(self, quotation_id: int):
        """พิมพ์ใบเสนอราคาโดยใช้ backend PDF generator และเปิดด้วยโปรแกรม PDF ของระบบ"""
        try:
            self.show_snack_bar(get_text("preparing_print"), "info")
            
            pdf_bytes = self.client.get_quotation_pdf(quotation_id)
            if not pdf_bytes:
                self.show_snack_bar(get_text("pdf_export_failed"), "error")
                return
                
            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            quote = next((q for q in self.quotations if q.get("id") == quotation_id), None)
            quote_no = f"QT-{quotation_id:04d}"
            pdf_path = os.path.join(output_dir, f"quotation_{quote_no}.pdf")
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
                
            os.startfile(pdf_path)
            self.show_snack_bar(get_text("pdf_export_success"), "success")
            
        except Exception as ex:
            print(f"Error printing quotation: {ex}")
            self.show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", "error")

    # ─────────────────────────────────────────────────────────────
    # DIALOG HELPERS
    # ─────────────────────────────────────────────────────────────
    def _open_dialog(self, dialog):
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                if self.current_dialog in self.page.overlay:
                    self.page.overlay.remove(self.current_dialog)
            self.current_dialog = dialog
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        except Exception as e:
            print(f"DEBUG: Error opening dialog: {e}")
    
    def _close_dialog(self, dialog=None):
        try:
            if dialog:
                dialog.open = False
            elif self.current_dialog:
                self.current_dialog.open = False
            self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
    # ─────────────────────────────────────────────────────────────
    # SNACK BAR
    # ─────────────────────────────────────────────────────────────
    def show_snack_bar(self, message: str, type="success"):
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