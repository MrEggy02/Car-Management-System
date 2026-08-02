# pages/invoices/invoice_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime
import webbrowser
import tempfile
import os
import threading
import time
import asyncio

from i18n import get_text


class InvoiceListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.current_snackbar = None
        self.invoices = []
        self.filtered_invoices = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.search_field = None
        self.current_status_filter = "all"
        self.status_chips = None
        self.table_rows = None
        self.pagination_container = None
        self.current_dialog = None
        self._dialog_stack = []
        self.kpi_container = None
        self.date_from_field = None
        self.date_to_field = None

    def build(self):
        header = self._build_header()
        self.kpi_container = ft.Container(
            content=ft.Row([], spacing=12),
            padding=ft.Padding(left=0, right=0, top=8, bottom=8),
        )
        search_bar = self._build_search_bar()
        table = self._build_table()
        self.pagination_container = ft.Container(padding=ft.Padding(left=20, right=20, top=12, bottom=12))

        content_area = ft.Container(
            content=ft.Column([
                self.kpi_container,
                search_bar,
                table,
                self.pagination_container,
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

        self.load_invoices()

        return main_content

    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("invoice_list"),
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
                            ft.Text(get_text("new_invoice"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.navigate("invoice_create"),
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
            ("paid", "#4CAF50", ft.Icons.CHECK_CIRCLE),
        ]
        status_texts = {
            "pending": get_text("status_pending"),
            "paid": get_text("status_paid"),
        }
        counts = {s: 0 for s, _, __ in statuses}
        for r in self.invoices:
            st = r.get("payment_status", "pending")
            if st in counts:
                counts[st] += 1

        cards = []
        for status, color, icon in statuses:
            count = counts[status]
            label = status_texts.get(status, status)
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

        total = len(self.invoices)
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
        self._load_status_chips()
        self.apply_filters()

    def _load_status_chips(self):
        """Load status filter chips"""
        if not self.status_chips:
            return

        self.status_chips.controls.clear()

        status_list = [
            {"id": "all", "name": get_text("all_status")},
            {"id": "pending", "name": get_text("status_pending")},
            {"id": "paid", "name": get_text("status_paid")},
        ]

        for status in status_list:
            is_active = self.current_status_filter == status["id"]
            chip = ft.Container(
                content=ft.Text(status["name"], size=12, weight=ft.FontWeight.W_500,
                               color=ft.Colors.WHITE if is_active else "#64748B"),
                bgcolor=self.primary_color if is_active else ft.Colors.GREY_200,
                border_radius=20,
                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                ink=True,
                on_click=lambda e, sid=status["id"]: self.filter_by_status(sid),
            )
            self.status_chips.controls.append(chip)

        self.page.update()

    def filter_by_status(self, status_id):
        """Filter by status chip click"""
        self.current_status_filter = status_id
        self._load_status_chips()
        self.apply_filters()

    def _build_search_bar(self):
        # Status Chips
        self.status_chips = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
        self._load_status_chips()

        self.search_field = ft.TextField(
            hint_text=get_text("search_invoice"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        self.search_field.on_change = self.on_search_change

        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_invoices(),
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
                ft.Container(height=8),
                self.status_chips,
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

    def _build_table(self):
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("invoice_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("job_number"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("customer_name"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("plate_number"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("final_total"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=10, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("payment_status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("payment_method"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("actions"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=230,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )

        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # Table container with horizontal scroll
        table_container = ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                self.table_rows,
            ], spacing=0),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12, bottom_left=12, bottom_right=12),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
        )

        # Wrap table in a Row with horizontal scroll
        return ft.Container(
            content=ft.Row([table_container], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
        )

    def load_invoices(self):
        self.table_rows.controls.clear()
        self.page.update()

        try:
            invoices = self.client.get_invoices()
            print(f"DEBUG: Loaded {len(invoices)} invoices")
            self.invoices = invoices
            self.filtered_invoices = invoices.copy()
            self.kpi_container.content = self._build_kpi_cards()
            self.apply_filters()
        except Exception as ex:
            print(f"Error loading invoices: {ex}")
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

    def on_search_change(self, e):
        """Real-time search"""
        self.apply_filters()

    def apply_filters(self):
        """Apply both status and search filters"""
        selected_status = self.current_status_filter if self.current_status_filter else "all"
        keyword = self.search_field.value.lower() if self.search_field.value else ""

        filtered = self.invoices.copy()

        # Apply status filter
        if selected_status and selected_status != "all":
            filtered = [i for i in filtered if i.get("payment_status") == selected_status]

        # Apply search filter
        if keyword:
            filtered = [
                i for i in filtered
                if keyword in f"INV-{i.get('id', 0):04d}".lower()
                or keyword in i.get("job_no", "").lower()
                or keyword in i.get("customer_name", "").lower()
                or keyword in i.get("plate_number", "").lower()
            ]

        # Apply date filter
        self._apply_date_filter(filtered)

        self.filtered_invoices = filtered
        self.current_page = 1
        self.display_invoices()

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
            paid_date = r.get("paid_date", "")
            if not paid_date:
                continue
            try:
                date_obj = datetime.strptime(str(paid_date)[:10], "%Y-%m-%d").date()
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

    def display_invoices(self):
        self.table_rows.controls.clear()

        total_items = len(self.filtered_invoices)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_invoices[start_idx:end_idx]

        if page_items:
            for i, invoice in enumerate(page_items):
                self.table_rows.controls.append(self._create_invoice_row(invoice, start_idx + i))
        else:
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.RECEIPT_OUTLINED, size=48, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_invoices_found"), size=16, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
            )

        self.update_pagination()
        self.page.update()

    def _create_invoice_row(self, invoice: Dict, index: int):
        invoice_id = invoice.get("id")
        invoice_no = f"INV-{invoice_id:04d}"
        job_no = invoice.get("job_no", "-")
        customer_name = invoice.get("customer_name", "-")
        plate_number = invoice.get("plate_number", "-")
        final_total = invoice.get("final_total", 0)
        payment_status = invoice.get("payment_status", "pending")
        payment_method = invoice.get("payment_method", "cash")
        paid_date = invoice.get("paid_date", "")
        if paid_date:
            paid_date = paid_date[:10] if " " in paid_date else paid_date[:10]
        else:
            paid_date = "-"

        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE

        status_colors = {
            "pending": "#FF9800",
            "paid": "#4CAF50"
        }
        status_texts = {
            "pending": get_text("status_pending"),
            "paid": get_text("status_paid")
        }

        method_texts = {
            "cash": get_text("payment_cash"),
            "transfer": get_text("payment_transfer")
        }

        status_badge = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                ft.Text(status_texts.get(payment_status, payment_status), size=11, color=ft.Colors.WHITE),
            ], spacing=4),
            bgcolor=status_colors.get(payment_status, "#607D8B"),
            border_radius=12,
            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        )

        view_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("view"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, iid=invoice_id: self.view_invoice_detail(iid),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )

        print_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT_OUTLINED, size=16, color=self.primary_color),
                ft.Text(get_text("print"), size=12, color=self.primary_color),
            ], spacing=4),
            on_click=lambda e, iid=invoice_id: self.print_invoice(iid),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )

        actions_list = [view_btn, print_btn]
        if payment_status == "pending":
            pay_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PAYMENT, size=16, color=ft.Colors.WHITE),
                    ft.Text(get_text("receive_payment") if get_text("receive_payment") != "receive_payment" else "ຮັບຊຳລະເງິນ", size=12, color=ft.Colors.WHITE),
                ], spacing=4),
                on_click=lambda e, inv=invoice: self._show_payment_dialog(inv),
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                bgcolor=self.success_color,
                border_radius=6,
            )
            actions_list.append(pay_btn)

        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(invoice_no, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=100,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(job_no, size=13, color="#1E293B"),
                    width=100,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(customer_name, size=13, color="#1E293B", max_lines=1),
                    width=130,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(plate_number, size=12, color="#64748B", max_lines=1),
                    width=100,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(f"{int(final_total):,} KIP", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=10, top=0, bottom=0),
                ),
                ft.Container(
                    content=status_badge,
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(method_texts.get(payment_method, payment_method), size=12, color="#64748B"),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(paid_date, size=12, color="#64748B"),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Row(actions_list, spacing=4),
                    width=230,
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

    def update_pagination(self):
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages

        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_invoices)} {get_text('of')} {len(self.invoices)} {get_text('results')}",
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
            self.display_invoices()

    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_invoices()

    def view_invoice_detail(self, invoice_id: int):
        """View invoice detail - show dialog instead of navigate"""
        invoice = next((i for i in self.invoices if i.get("id") == invoice_id), None)
        if not invoice:
            self.show_snack_bar(get_text("invoice_not_found"), "error")
            return

        self._show_invoice_detail_dialog(invoice)

    def print_invoice(self, invoice_id: int):
        """Print invoice using backend PDF generator"""
        try:
            self.show_snack_bar(get_text("preparing_print"), "info")

            pdf_bytes = self.client.get_invoice_pdf(invoice_id)
            if not pdf_bytes:
                self.show_snack_bar(get_text("pdf_export_failed"), "error")
                return

            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)

            invoice_no = f"INV-{invoice_id:04d}"
            pdf_path = os.path.join(output_dir, f"invoice_{invoice_no}.pdf")

            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)

            os.startfile(pdf_path)
            self.show_snack_bar(get_text("pdf_export_success"), "success")

        except Exception as ex:
            print(f"Error printing invoice: {ex}")
            self.show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", "error")

    def print_delivery_note(self, invoice_id: int):
        """Print delivery note using backend PDF generator"""
        try:
            self.show_snack_bar("ກຳລັງກຽມພິມໃບສົ່ງມອບລົດ...", "info")

            pdf_bytes = self.client.get_delivery_note_pdf(invoice_id)
            if not pdf_bytes:
                self.show_snack_bar("ບໍ່ສາມາດພິມໃບສົ່ງມອບລົດໄດ້", "error")
                return

            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)

            invoice_no = f"INV-{invoice_id:04d}"
            pdf_path = os.path.join(output_dir, f"delivery_note_{invoice_no}.pdf")

            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)

            os.startfile(pdf_path)
            self.show_snack_bar("ພິມໃບສົ່ງມອບລົດສຳເລັດແລ້ວ!", "success")

        except Exception as ex:
            print(f"Error printing delivery note: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", "error")

    def show_post_payment_dialog(self, invoice_id: int, invoice_data: Dict = None):
        """Show options to print delivery note or invoice after successful payment"""
        
        def close_only():
            self._close_dialog()
            # Update the invoice status in the local list without reloading
            if invoice_data:
                # Update the invoice in self.invoices
                for inv in self.invoices:
                    if inv.get('id') == invoice_id:
                        inv['payment_status'] = 'paid'
                        inv['payment_method'] = invoice_data.get('payment_method', 'cash')
                        inv['received_amount'] = invoice_data.get('received_amount', 0)
                        inv['change_amount'] = invoice_data.get('change_amount', 0)
                        inv['paid_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        break
                # Also update in filtered_invoices if present                for inv in self.filtered_invoices:
                    if inv.get('id') == invoice_id:
                        inv['payment_status'] = 'paid'
                        inv['payment_method'] = invoice_data.get('payment_method', 'cash')
                        inv['received_amount'] = invoice_data.get('received_amount', 0)
                        inv['change_amount'] = invoice_data.get('change_amount', 0)
                        inv['paid_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        break
                # Refresh the display
                self.display_invoices()

        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=self.success_color, size=28),
                ft.Text("ຊຳລະເງິນສຳເລັດ", size=18, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("ການຊຳລະເງິນສຳເລັດຮຽບຮ້ອຍແລ້ວ. ທ່ານຕ້ອງການພິມເອກະສານໃດ?", size=14, color="#475569"),
                ], tight=True),
                width=350,
                padding=10,
            ),
            actions=[
                ft.ElevatedButton(
                    "ພິມໃບສົ່ງມອບລົດ",
                    icon=ft.Icons.LOCAL_SHIPPING,
                    bgcolor=self.success_color,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: (close_only(), self.print_delivery_note(invoice_id)),
                ),
                ft.ElevatedButton(
                    "ພິມໃບຮັບເງິນ",
                    icon=ft.Icons.PRINT,
                    bgcolor=self.primary_color,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: (close_only(), self.print_invoice(invoice_id)),
                ),
                ft.TextButton(
                    "ປິດ",
                    on_click=lambda e: close_only(),
                    style=ft.ButtonStyle(color="#64748B"),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)

    def _show_invoice_detail_dialog(self, invoice: Dict):
        """Show invoice detail in dialog"""
        invoice_no = f"INV-{invoice.get('id', 0):04d}"
        job_no = invoice.get("job_no", "-")
        customer_name = invoice.get("customer_name", "-")
        customer_phone = invoice.get("customer_phone", "-")
        plate_number = invoice.get("plate_number", "-")
        brand = invoice.get("brand", "-")
        model = invoice.get("model", "-")
        total_amount = invoice.get("total_amount", 0)
        total_discount = invoice.get("total_discount", 0)
        final_total = invoice.get("final_total", 0)
        payment_method = invoice.get("payment_method", "cash")
        payment_status = invoice.get("payment_status", "pending")
        received_amount = invoice.get("received_amount", 0)
        change_amount = invoice.get("change_amount", 0)
        paid_date = invoice.get("paid_date", "")

        if paid_date:
            paid_date = paid_date[:16] if len(paid_date) > 16 else paid_date
        else:
            paid_date = "-"

        status_colors = {
            "pending": "#FF9800",
            "paid": "#4CAF50"
        }
        status_texts = {
            "pending": get_text("status_pending"),
            "paid": get_text("status_paid")
        }

        method_texts = {
            "cash": get_text("payment_cash"),
            "transfer": get_text("payment_transfer")
        }

        dialog_actions = [
            ft.TextButton(
                get_text("close"),
                on_click=lambda e: self._close_dialog(dialog),
                style=ft.ButtonStyle(color="#64748B"),
            ),
            ft.ElevatedButton(
                get_text("print"),
                on_click=lambda e: self.print_invoice(invoice.get('id')),
                style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
            ),
        ]

        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.RECEIPT, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(
                            get_text("invoice_detail"),
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(get_text("invoice_no"), size=12, color="#64748B", width=100),
                                ft.Text(invoice_no, size=13, weight=ft.FontWeight.W_600, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("job_number"), size=12, color="#64748B", width=100),
                                ft.Text(job_no, size=13, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("customer_name"), size=12, color="#64748B", width=100),
                                ft.Text(customer_name, size=13, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("plate_number"), size=12, color="#64748B", width=100),
                                ft.Text(plate_number, size=13, weight=ft.FontWeight.W_600, color=self.primary_color, expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("payment_status"), size=12, color="#64748B", width=100),
                                ft.Container(
                                    content=ft.Text(status_texts.get(payment_status, payment_status), size=12, color=ft.Colors.WHITE),
                                    bgcolor=status_colors.get(payment_status, "#607D8B"),
                                    border_radius=12,
                                    padding=ft.Padding(left=12, right=12, top=4, bottom=4),
                                ),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("payment_method"), size=12, color="#64748B", width=100),
                                ft.Text(method_texts.get(payment_method, payment_method), size=13, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("paid_date"), size=12, color="#64748B", width=100),
                                ft.Text(paid_date, size=13, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Divider(height=1, color=ft.Colors.GREY_200),
                            ft.Row([
                                ft.Text(get_text("total_amount"), size=13, weight=ft.FontWeight.W_500),
                                ft.Container(expand=True),
                                ft.Text(f"{int(total_amount):,} KIP", size=13, color="#64748B"),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("discount"), size=13, weight=ft.FontWeight.W_500),
                                ft.Container(expand=True),
                                ft.Text(f"-{int(total_discount):,} KIP", size=13, color=ft.Colors.RED_600),
                            ], spacing=8),
                            ft.Divider(height=1, color=ft.Colors.GREY_200),
                            ft.Row([
                                ft.Text(get_text("final_total"), size=15, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{int(final_total):,} KIP", size=15, weight=ft.FontWeight.BOLD, color=self.success_color),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("received_amount"), size=13, weight=ft.FontWeight.W_500),
                                ft.Container(expand=True),
                                ft.Text(f"{int(received_amount):,} KIP", size=13, color=self.success_color),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("change_amount"), size=13, weight=ft.FontWeight.W_500),
                                ft.Container(expand=True),
                                ft.Text(f"{int(change_amount):,} KIP", size=13, color="#1E293B"),
                            ], spacing=8),
                        ], spacing=10),
                        padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                    ),
                ]),
                width=450,
            ),
            actions=dialog_actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._open_dialog(dialog)

    def _open_dialog(self, dialog):
        """Open a dialog - closes all previous tracked dialogs first"""
        for d in self._dialog_stack:
            try:
                d.open = False
            except Exception:
                pass
        self.current_dialog = dialog
        self._dialog_stack.append(dialog)
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog=None):
        """Close all tracked dialogs"""
        for d in self._dialog_stack:
            try:
                d.open = False
            except Exception:
                pass
        self._dialog_stack.clear()
        self.current_dialog = None
        self.page.update()

    def show_snack_bar(self, message: str, type: str = "success"):
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

    # ==================== FIXED PAYMENT DIALOG WITH VALIDATION ====================
    def _show_payment_dialog(self, invoice: Dict):
        final_total = invoice.get('final_total', 0)
        invoice_id = invoice.get('id')

        # Error label
        payment_error = ft.Text("", color=ft.Colors.RED_600, size=11, visible=False)

        payment_method_dropdown = ft.Dropdown(
            label=get_text("payment_method"),
            value="cash",
            options=[
                ft.dropdown.Option("cash", get_text("payment_cash")),
                ft.dropdown.Option("transfer", get_text("payment_transfer")),
            ],
            expand=True,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
        )

        received_field = ft.TextField(
            label=get_text("received_amount"),
            value=str(int(final_total)),
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
        )

        change_text = ft.Text("0 KIP", size=16, weight=ft.FontWeight.BOLD, color=self.success_color, text_align=ft.TextAlign.RIGHT)

        def on_received_change(e):
            try:
                raw_value = e.control.value.replace(',', '').strip()
                received = float(raw_value) if raw_value else 0
                change = max(0, received - final_total)
                change_text.value = f"{int(change):,} KIP"
                # Clear error if amount is sufficient
                if received >= final_total:
                    payment_error.visible = False
                    payment_error.update()
                self.page.update()
            except:
                change_text.value = "0 KIP"

        received_field.on_change = on_received_change

        def validate_payment(received):
            """Validate payment amount"""
            if received < final_total:
                payment_error.value = f"ຈຳນວນເງິນທີ່ຮັບ ({int(received):,} KIP) ຕ້ອງຫຼາຍກວ່າ ຫຼື ເທົ່າກັບຍອດລວມ ({int(final_total):,} KIP)"
                payment_error.visible = True
                payment_error.update()
                return False
            else:
                payment_error.visible = False
                payment_error.update()
                return True

        def confirm_payment(e):
            try:
                method = payment_method_dropdown.value
                try:
                    received = float(received_field.value.replace(',', '')) if received_field.value else 0
                except:
                    received = final_total

                # Validate payment amount
                if not validate_payment(received):
                    if dialog:
                        dialog.update()
                    return

                change = max(0, received - final_total)

                self.client.record_invoice_payment(
                    invoice_id=invoice_id,
                    payment_method=method,
                    received_amount=received,
                    change_amount=change
                )
                # Close payment dialog first, then show post-payment dialog
                invoice_data = {
                    'payment_method': method,
                    'received_amount': received,
                    'change_amount': change
                }
                self._close_dialog(dialog)
                self.show_post_payment_dialog(invoice_id, invoice_data)
            except Exception as ex:
                self.show_snack_bar(f"Payment failed: {ex}", "error")

        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Text("ຮັບຊຳລະເງິນ", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"ຍອດລວມ: {int(final_total):,} KIP", size=16, weight=ft.FontWeight.BOLD, color=self.primary_color),
                    ft.Container(height=10),
                    payment_method_dropdown,
                    ft.Container(height=10),
                    received_field,
                    ft.Container(height=10),
                    ft.Row([
                        ft.Text(get_text("change"), size=14),
                        ft.Container(expand=True),
                        change_text,
                    ]),
                    payment_error,
                ], tight=True),
                width=350,
                height=260,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton("ຍືນຍັນຊຳລະ", on_click=confirm_payment, bgcolor=self.success_color, color=ft.Colors.WHITE),
            ],
        )
        self._open_dialog(dialog)