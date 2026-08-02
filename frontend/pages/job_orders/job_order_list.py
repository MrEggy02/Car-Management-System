# pages/job_orders/job_order_list.py
import flet as ft
import asyncio
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime
import webbrowser
import tempfile
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog

from i18n import get_text, get_current_language
from pages.job_orders.job_order_dialogs import (
    show_job_order_detail_dialog,
)


class JobOrderListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.current_snackbar = None
        self.job_orders = []
        self.filtered_orders = []
        self.current_dialog = None
        self.search_field = None
        self.current_status_filter = "all"
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.date_from_field = None
        self.date_to_field = None
        self.kpi_container = None
        self.table_rows = None
        self.pagination_container = None
        self.loading_indicator = None
        self.empty_state = None
        
        self.current_upload_order_id = None
        
        # Status colors
        self.status_colors = {
            "pending": "#FF9800",
            "quoting": "#2196F3",
            "repairing": "#9C27B0",
            "finished": "#4CAF50",
            "closed": "#607D8B",
            "cancelled": "#F44336"
        }
        
        self.status_icons = {
            "pending": ft.Icons.HOURGLASS_EMPTY,
            "quoting": ft.Icons.CALCULATE,
            "repairing": ft.Icons.BUILD,
            "finished": ft.Icons.CHECK_CIRCLE,
            "closed": ft.Icons.LOCK,
            "cancelled": ft.Icons.CANCEL
        }
        
        self.status_texts = {
            "pending": get_text("pending"),
            "quoting": get_text("quoting"),
            "repairing": get_text("repairing"),
            "finished": get_text("finished"),
            "closed": get_text("closed"),
            "cancelled": get_text("cancelled")
        }

    async def trigger_upload(self, order_id):
        self.current_upload_order_id = order_id
        
        def on_file_selected(file_path):
            if not file_path:
                self.current_upload_order_id = None
                return
            
            try:
                self.client.upload_job_order_receipt(self.current_upload_order_id, file_path)
                self.show_snack_bar("ອັບໂຫຼດສຳເລັດ", "success")
                self.load_orders()
            except Exception as ex:
                self.show_snack_bar(f"Error: {ex}", "error")
            self.current_upload_order_id = None
            
        def run_picker():
            root = tk.Tk()
            root.attributes("-alpha", 0.0)
            root.attributes("-topmost", True)
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="ເລືອກຮູບພາບໃບສັນຍາ (Select Receipt Image)",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
            )
            root.destroy()
            on_file_selected(file_path)
            
        threading.Thread(target=run_picker, daemon=True).start()
        
    def view_receipt_image(self, order_id):
        url = self.client.get_job_order_receipt_url(order_id)
        dialog = ft.AlertDialog(
            title=ft.Text("ໃບສັນຍາ (Receipt Image)"),
            content=ft.Image(src=url, fit="contain", width=600, height=600),
            actions=[
                ft.TextButton(get_text("close") if get_text("close") != "close" else "ປິດ", on_click=self._close_dialog)
            ]
        )
        self._open_dialog(dialog)

    def _open_dialog(self, dialog):
        self.current_dialog = dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self, e=None):
        if self.current_dialog:
            self.current_dialog.open = False
            self.page.update()

    def show_snack_bar(self, msg, type="success"):
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
                    ft.Text(msg, color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.W_500),
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

    def build(self):

        header = self._build_header()
        self.kpi_container = ft.Container(
            content=ft.Row([], spacing=12),
            padding=ft.Padding(left=0, right=0, top=8, bottom=8),
        )
        search_bar = self._build_search_bar()
        table = self._build_table()
        self.pagination_container = ft.Container(
            padding=ft.Padding(left=20, right=20, top=12, bottom=12)
        )
        
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
                ft.Icon(ft.Icons.RECEIPT_OUTLINED, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=16),
                ft.Text(get_text("no_orders_found"), size=18, weight=ft.FontWeight.W_500, color="#64748B"),
                ft.Text(get_text("click_add_to_register"), size=13, color="#94A3B8"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text(get_text("new_job_order"), color=ft.Colors.WHITE, size=14),
                    on_click=lambda e: self.navigate("job_order_create"),
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
        
        content_area = ft.Container(
            content=ft.Column([
                self.kpi_container,
                search_bar,
                table,
                self.pagination_container,
                self.loading_indicator,
                self.empty_state,
            ], expand=True, scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area], expand=True, scroll=ft.ScrollMode.AUTO),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Load orders using new fast API
        self.page.run_task(self._load_data_async)
        
        return main_content

    async def _load_data_async(self):
        await asyncio.sleep(0.1)
        await asyncio.to_thread(self.load_orders)
    
    # ─────────────────────────── HEADER ───────────────────────────
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("job_order_list"),
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
                            ft.Text(get_text("new_job_order"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.navigate("job_order_create"),
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
    
    # ─────────────────────────── KPI CARDS ───────────────────────────
    def _build_kpi_cards(self):
        statuses = [
            ("pending", "#FF9800", ft.Icons.HOURGLASS_EMPTY),
            ("quoting", "#2196F3", ft.Icons.CALCULATE),
            ("repairing", "#9C27B0", ft.Icons.BUILD),
            ("finished", "#4CAF50", ft.Icons.CHECK_CIRCLE),
            ("closed", "#607D8B", ft.Icons.LOCK),
            ("cancelled", "#F44336", ft.Icons.CANCEL),
        ]
        counts = {s: 0 for s, _, __ in statuses}
        for r in self.job_orders:
            st = r.get("status", "pending")
            if st in counts:
                counts[st] += 1

        cards = []
        for status, color, icon in statuses:
            count = counts[status]
            label = self.status_texts.get(status, status)
            is_active = self.current_status_filter == status
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

        total = len(self.job_orders)
        is_all = self.current_status_filter == "all"
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
        self.current_status_filter = status
        self.current_page = 1
        self.apply_filters()

    # ─────────────────────────── SEARCH BAR ───────────────────────────
    def _build_search_bar(self):
        self.search_field = ft.TextField(
            hint_text=get_text("search_job_order"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
            on_change=self.apply_filters_from_event,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_orders(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )

        def clear_date_from(e):
            self.date_from_field.value = ""
            self.page.update()
            self.apply_filters()

        def clear_date_to(e):
            self.date_to_field.value = ""
            self.page.update()
            self.apply_filters()

        self.date_from_field = ft.TextField(
            hint_text=get_text("date_from"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            suffix=ft.IconButton(icon=ft.Icons.CLOSE, on_click=clear_date_from, icon_size=16),
            content_padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            read_only=True,
            on_focus=self._pick_date_from,
        )

        self.date_to_field = ft.TextField(
            hint_text=get_text("date_to"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            suffix=ft.IconButton(icon=ft.Icons.CLOSE, on_click=clear_date_to, icon_size=16),
            content_padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            read_only=True,
            on_focus=self._pick_date_to,
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([self.search_field, refresh_button], spacing=10),
                ft.Container(height=8),
                ft.Row([self.date_from_field, self.date_to_field], spacing=10),
            ], spacing=0),
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
        )
    
    def _pick_date_from(self, e):
        if getattr(self, 'ignore_from_focus', False):
            self.ignore_from_focus = False
            return
            
        def on_date_selected(e):
            self.ignore_from_focus = True
            if e.control.value:
                self.date_from_field.value = e.control.value.strftime("%Y-%m-%d")
                self.page.update()
                self.apply_filters()
                
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
                self.page.update()
                self.apply_filters()
                
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

    # ─────────────────────────── TABLE ───────────────────────────
    def _build_table(self):
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(get_text("job_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=140, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=10, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text("customer_name"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=200, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=10, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text("plate_number"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=130, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=10, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text("receive_date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=120, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("actions"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), expand=True, alignment=ft.Alignment(0, 0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        table_scroll_container = ft.Container(
            content=self.table_rows,
            expand=True,
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            bgcolor=ft.Colors.WHITE,
        )
        
        table_container = ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                table_scroll_container,
            ], spacing=0),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12, bottom_left=12, bottom_right=12),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
        )
        
        return ft.Container(
            content=ft.Row([table_container], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
        )
    
    def _create_table_row(self, order: Dict, index: int):
        order_id = order.get("id")
        job_no = order.get("job_no", "N/A")
        customer_name = order.get("customer_name", "-")
        plate_number = order.get("plate_number", "-")
        receive_date = order.get("receive_date", "")
        status = order.get("status", "pending")
        
        if receive_date:
            try:
                receive_date = receive_date.split()[0] if " " in receive_date else receive_date[:10]
            except:
                receive_date = "-"
        else:
            receive_date = "-"
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        # Status badge
        status_color = self.status_colors.get(status, "#607D8B")
        status_text = self.status_texts.get(status, status)
        status_badge = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                ft.Text(status_text, size=11, color=ft.Colors.WHITE),
            ], spacing=4),
            bgcolor=status_color,
            border_radius=12,
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
        )
        
        view_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=16, color=self.primary_color), ft.Text(get_text("view"), size=12, color=self.primary_color)], spacing=4),
            on_click=lambda e, oid=order_id: self.show_detail_dialog(oid),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        print_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.PRINT_OUTLINED, size=16, color=self.primary_color), ft.Text(get_text("print"), size=12, color=self.primary_color)], spacing=4),
            on_click=lambda e, oid=order_id: self.print_job_order(oid),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        delete_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600), ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600)], spacing=4),
            on_click=lambda e, oid=order_id, jno=job_no: self.confirm_delete(oid, jno),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        async def on_upload_click(e):
            await self.trigger_upload(order_id)
            
        upload_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.UPLOAD_FILE, size=16, color="#0284C7"), ft.Text("ອັບຮູບ", size=12, color="#0284C7")], spacing=4),
            on_click=on_upload_click,
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        has_image = order.get("signed_receipt_image") is not None
        view_image_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.IMAGE, size=16, color="#059669"), ft.Text("ເບິ່ງຮູບ", size=12, color="#059669")], spacing=4),
            on_click=lambda e, oid=order_id: self.view_receipt_image(oid),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
            visible=has_image,
        )
        
        actions_row = ft.Row(
            [view_btn, print_btn, upload_btn, view_image_btn, delete_btn] if has_image else [view_btn, print_btn, upload_btn, delete_btn], 
            spacing=4,
            wrap=False,
            scroll=ft.ScrollMode.AUTO
        )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(job_no, size=13, weight=ft.FontWeight.W_500, color="#1E293B"), width=140, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=10, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(customer_name, size=13, color="#1E293B", max_lines=1), width=200, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=10, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(plate_number, size=12, color="#64748B", max_lines=1), width=130, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=10, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(receive_date, size=12, color="#64748B"), width=120, alignment=ft.Alignment(0, 0)),
                ft.Container(content=status_badge, width=100, alignment=ft.Alignment(0, 0)),
                ft.Container(content=actions_row, expand=True, alignment=ft.Alignment(-1, 0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            bgcolor=row_bg,
        )
        
        return ft.Column([row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0)
    
    def load_orders(self):
        """Load orders using fast API that returns all data in one call"""
        self.loading_indicator.visible = True
        self.empty_state.visible = False
        self.table_rows.controls.clear()
        self.page.update()
        
        try:
            # Use new fast API that returns everything in one query
            orders = self.client.get_job_orders_with_details()
            print(f"DEBUG: Loaded {len(orders) if orders else 0} orders from fast API")
            
            if orders:
                self.job_orders = orders
            else:
                self.job_orders = []
            
            self.filtered_orders = self.job_orders.copy()
            self.kpi_container.content = self._build_kpi_cards()
            self.apply_filters()
            
        except Exception as ex:
            print(f"Error loading orders via fast API: {ex}")
            # Fallback to old method
            try:
                orders = self.client.get_job_orders()
                self.job_orders = orders or []
                self.filtered_orders = self.job_orders.copy()
                self.kpi_container.content = self._build_kpi_cards()
                self.apply_filters()
            except Exception as ex2:
                print(f"Error loading orders via fallback: {ex2}")
                self.loading_indicator.visible = False
                self.table_rows.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                            ft.Text(f"Error: {str(ex)}", size=14, color=ft.Colors.RED_600),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                    )
                )
                self.page.update()
    
    def display_orders(self):
        self.table_rows.controls.clear()
        
        total_items = len(self.filtered_orders)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_orders[start_idx:end_idx]
        
        if page_items and len(page_items) > 0:
            self.loading_indicator.visible = False
            self.empty_state.visible = False
            for i, order in enumerate(page_items):
                self.table_rows.controls.append(self._create_table_row(order, start_idx + i))
        else:
            self.loading_indicator.visible = False
            self.empty_state.visible = True
        
        self.update_pagination_controls()
        self.page.update()
    
    def update_pagination_controls(self):
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Container(
            content=ft.Row([
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_orders)} {get_text('of')} {len(self.job_orders)} {get_text('results')}",
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
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=20, right=20, top=16, bottom=16),
            bgcolor="#F5F7FA",
        )
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_orders()
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_orders()
    
    def apply_filters_from_event(self, e):
        self.apply_filters()
        self.page.update()
    
    def apply_filters(self):
        keyword = self.search_field.value.lower() if self.search_field and self.search_field.value else ""
        selected_status = self.current_status_filter if self.current_status_filter else "all"
        
        filtered = self.job_orders.copy()
        
        # Apply status filter
        if selected_status and selected_status != "all":
            filtered = [o for o in filtered if o.get("status") == selected_status]
        
        # Apply search filter
        if keyword:
            filtered = [
                o for o in filtered
                if keyword in o.get("job_no", "").lower()
                or keyword in o.get("customer_name", "").lower()
                or keyword in o.get("plate_number", "").lower()
            ]
        
        # Apply date filter
        self._apply_date_filter(filtered)
        
        self.filtered_orders = filtered
        self.current_page = 1
        self.display_orders()
    
    def _apply_date_filter(self, filtered_list):
        """Apply date range filter to the filtered list"""
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
        
        if not date_from and not date_to:
            return
        
        # Filter in-place
        result = []
        for r in filtered_list:
            date_str = r.get("receive_date", "")
            if not date_str:
                continue
            try:
                date_obj = datetime.strptime(str(date_str)[:10], "%Y-%m-%d").date()
                if date_from and date_obj < date_from:
                    continue
                if date_to and date_obj > date_to:
                    continue
                result.append(r)
            except ValueError:
                continue
        
        # Replace the list content
        filtered_list.clear()
        filtered_list.extend(result)
    
    def show_detail_dialog(self, order_id):
        order = next((o for o in self.job_orders if o.get("id") == order_id), None)
        if not order:
            return
        
        has_image = order.get("signed_receipt_image") is not None
        receipt_url = self.client.get_job_order_receipt_url(order_id) if has_image else None
        
        dialog = show_job_order_detail_dialog(
            order, 
            self.primary_color, 
            self._close_dialog,
            on_print=lambda oid: self.print_job_order(oid),
            receipt_url=receipt_url
        )
        self._open_dialog(dialog)
    
    def confirm_delete(self, order_id, job_no):
        """Show confirmation dialog before deleting a job order."""
        def do_delete(e):
            self._close_dialog()
            try:
                self.client.delete_job_order(order_id)
                self.load_orders()
                self.show_snack_bar(f"{get_text('deleted_successfully')} ({job_no})", "success")
            except Exception as ex:
                self.show_snack_bar(f"{get_text('error')}: {str(ex)}", "error")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_600, size=24),
                ft.Text(get_text("confirm_delete"), size=16, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            content=ft.Text(
                f"{get_text('delete_job_order_confirm')} {job_no}?",
                size=14,
                color="#475569",
            ),
            actions=[
                ft.TextButton(
                    get_text("cancel"),
                    on_click=self._close_dialog,
                    style=ft.ButtonStyle(color="#64748B"),
                ),
                ft.ElevatedButton(
                    get_text("delete"),
                    on_click=do_delete,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.RED_600,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)
    
    def print_job_order(self, order_id):
        try:
            self.show_snack_bar(get_text("preparing_print"), "info")
            
            pdf_bytes = self.client.get_job_order_pdf(order_id)
            if not pdf_bytes:
                self.show_snack_bar(get_text("pdf_export_failed"), "error")
                return
                
            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            order = next((o for o in self.job_orders if o.get("id") == order_id), None)
            job_no = order.get("job_no", f"JOB_{order_id}") if order else f"JOB_{order_id}"
            pdf_path = os.path.join(output_dir, f"job_order_{job_no}.pdf")
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
                
            os.startfile(pdf_path)
            self.show_snack_bar(get_text("pdf_export_success"), "success")
            
        except Exception as ex:
            print(f"Error printing job order: {ex}")
            self.show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", "error")
    
    def _generate_print_html(self, order):
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets/fonts/Phetsarath.ttf")
        
        job_no = order.get("job_no", "N/A")
        customer_name = order.get("customer_name", "-")
        customer_phone = order.get("customer_phone", "-")
        customer_address = order.get("address", "-")
        plate_number = order.get("plate_number", "-")
        brand = order.get("brand", "-")
        model = order.get("model", "-")
        year = order.get("year", "")
        color = order.get("color", "-")
        receive_date = order.get("receive_date", "")
        problem = order.get("problem_description", "-")
        mileage = order.get("mileage", 0)
        fuel_level = order.get("fuel_level", "-")
        created_by = order.get("created_by_name", self.user.get("fullname", "-"))
        
        if receive_date:
            try:
                dt = datetime.strptime(str(receive_date), "%Y-%m-%d %H:%M:%S")
                receive_date = dt.strftime("%d/%m/%Y %H:%M")
            except:
                try:
                    dt = datetime.strptime(str(receive_date), "%Y-%m-%d")
                    receive_date = dt.strftime("%d/%m/%Y")
                except:
                    pass
        
        shop_info = {}
        try:
            shop_info = self.client.get_shop()
        except:
            pass
        
        shop_name = shop_info.get('name', 'J&P Auto Maxing')
        shop_address = shop_info.get('address', 'Vientiane, Lao PDR')
        shop_phone = shop_info.get('phone', '020 92431434')
        
        receipt_no = f"RCP-{order.get('id', 0):06d}"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Job Order Receipt - {job_no}</title>
    <style>
        @font-face {{
            font-family: 'Phetsarath';
            src: url('file:///{font_path}') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}
        
        @media print {{
            body {{ margin: 0; padding: 0; }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Phetsarath', 'Noto Sans', 'DejaVu Sans', 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            padding: 20px;
            background: #e2e8f0;
        }}
        
        .receipt {{
            max-width: 380px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .receipt-content {{
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 20px 20px 15px 20px;
            background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
            color: white;
        }}
        
        .shop-name {{
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        
        .shop-address {{
            font-size: 10px;
            opacity: 0.9;
            margin-top: 4px;
        }}
        
        .shop-phone {{
            font-size: 11px;
            font-weight: bold;
            margin-top: 6px;
        }}
        
        .receipt-title {{
            font-size: 11px;
            letter-spacing: 2px;
            margin-top: 8px;
            padding-top: 6px;
            border-top: 1px dashed rgba(255,255,255,0.3);
            display: inline-block;
        }}
        
        .info-section {{
            margin-bottom: 14px;
        }}
        
        .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 11px;
            padding-bottom: 4px;
            border-bottom: 1px dotted #e2e8f0;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #475569;
            width: 90px;
        }}
        
        .info-value {{
            color: #1e293b;
            font-weight: 500;
            flex: 1;
            text-align: right;
        }}
        
        .divider {{
            height: 1px;
            background: repeating-linear-gradient(90deg, #cbd5e1, #cbd5e1 5px, transparent 5px, transparent 10px);
            margin: 10px 0;
        }}
        
        .divider-dashed {{
            height: 1px;
            background: repeating-linear-gradient(90deg, #94a3b8, #94a3b8 4px, transparent 4px, transparent 8px);
            margin: 8px 0;
        }}
        
        .section-title {{
            font-size: 11px;
            font-weight: bold;
            color: #1565C0;
            margin-bottom: 6px;
            padding-bottom: 3px;
            border-bottom: 2px solid #1565C0;
            display: inline-block;
        }}
        
        .problem-box {{
            background: #f8fafc;
            padding: 10px;
            border-radius: 8px;
            margin-top: 6px;
            font-size: 11px;
            line-height: 1.4;
            color: #334155;
            border-left: 3px solid #1565C0;
        }}
        
        .barcode {{
            height: 20px;
            background: repeating-linear-gradient(90deg, #000, #000 2px, transparent 2px, transparent 6px);
            margin: 12px 0;
        }}
        
        .footer {{
            text-align: center;
            padding-top: 12px;
            margin-top: 8px;
            border-top: 1px dashed #cbd5e1;
            font-size: 9px;
            color: #94a3b8;
        }}
        
        .thankyou {{
            font-size: 12px;
            font-weight: bold;
            color: #1565C0;
            margin-bottom: 6px;
        }}
        
        .stamp {{
            margin-top: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 9px;
            color: #64748b;
        }}
        
        .signature {{
            border-top: 1px dotted #94a3b8;
            width: 120px;
            padding-top: 4px;
            text-align: center;
        }}
        
        .receipt-no {{
            font-size: 9px;
            color: #64748b;
            text-align: center;
            margin-top: 4px;
            font-family: monospace;
        }}
        
        .badge {{
            background: #f1f5f9;
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 8px;
            font-weight: bold;
            margin-bottom: 6px;
        }}
        
        .highlight {{
            font-weight: bold;
            color: #1565C0;
        }}
        
        .date-text {{
            font-size: 10px;
        }}
    </style>
</head>
<body>
    <div class="receipt">
        <div class="header">
            <div class="shop-name">{shop_name}</div>
            <div class="shop-address">{shop_address}</div>
            <div class="shop-phone">📞 {shop_phone}</div>
            <div class="receipt-title">ສຳເນົາໃບຮັບລົດ</div>
        </div>
        
        <div class="receipt-content">
            <div class="receipt-no">{receipt_no}</div>
            
            <div style="text-align: center; margin: 8px 0;">
                <span class="badge">ເລກທີໃບຮັບ</span>
                <div style="font-size: 22px; font-weight: bold; color: #1565C0; letter-spacing: 1px; margin-top: 2px;">{job_no}</div>
            </div>
            
            <div class="divider-dashed"></div>
            
            <div class="info-row">
                <span class="info-label">📅 ວັນທີຮັບ</span>
                <span class="info-value">{receive_date}</span>
            </div>
            
            <div class="divider"></div>
            
            <div class="info-section">
                <div class="section-title">👤 ຂໍ້ມູນລູກຄ້າ</div>
                <div class="info-row">
                    <span class="info-label">ຊື່</span>
                    <span class="info-value">{customer_name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ເບີໂທ</span>
                    <span class="info-value">{customer_phone}</span>
                </div>
                {f'<div class="info-row"><span class="info-label">ທີ່ຢູ່</span><span class="info-value">{customer_address[:35]}</span></div>' if customer_address and customer_address != "-" else ''}
            </div>
            
            <div class="divider-dashed"></div>
            
            <div class="info-section">
                <div class="section-title">🚗 ຂໍ້ມູນລົດ</div>
                <div class="info-row">
                    <span class="info-label">ທະບຽນລົດ</span>
                    <span class="info-value"><span class="highlight">{plate_number}</span></span>
                </div>
                <div class="info-row">
                    <span class="info-label">ຍີ່ຫໍ້/ລຸ້ນ</span>
                    <span class="info-value">{brand} {model}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ສີ/ປີ</span>
                    <span class="info-value">{color if color != "-" else "-"} {f'({year})' if year else ''}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ເລກໄມ</span>
                    <span class="info-value">{int(mileage):,} km</span>
                </div>
                <div class="info-row">
                    <span class="info-label">ນ້ຳມັນ</span>
                    <span class="info-value">{fuel_level}</span>
                </div>
            </div>
            
            <div class="divider-dashed"></div>
            
            <div class="info-section">
                <div class="section-title">🔧 ບັນຫາທີ່ພົບ</div>
                <div class="problem-box">{problem}</div>
            </div>
            
            <div class="divider-dashed"></div>
            
            <div class="info-row">
                <span class="info-label">🧑‍🔧 ພະນັກງານຮັບ</span>
                <span class="info-value">{created_by}</span>
            </div>
            
            <div class="barcode"></div>
            
            <div class="stamp">
                <div class="signature">ລາຍເຊັນລູກຄ້າ</div>
                <div class="signature">ລາຍເຊັນຊ່າງ</div>
            </div>
            
            <div class="footer">
                <div class="thankyou">ຂອບໃຈທີ່ໄວ້ໃຈບໍລິການຂອງພວກເຮົາ</div>
                <div>ສອບຖາມເພີ່ມເຕີມ: {shop_phone}</div>
                <div class="date-text">ພິມເມື່ອ: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
            </div>
        </div>
    </div>
    
    <script>
        window.onload = function() {{
            setTimeout(function() {{
                window.print();
            }}, 300);
        }}
    </script>
</body>
</html>"""
        
        return html_content
    
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
            import traceback
            traceback.print_exc()
    
    def _close_dialog(self, e=None):
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")