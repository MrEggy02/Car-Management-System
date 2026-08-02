# pages/invoices/delivery_note_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import os
import asyncio
from datetime import datetime, timedelta

from i18n import get_text


class DeliveryNoteListContent:
    """ໜ້າລາຍຊື່ໃບສົ່ງມອບລົດ — ສະແດງສະເພາະ invoices ທີ່ paid ແລ້ວ"""

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
        self.current_page_num = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.search_field = None
        self.date_from_field = None
        self.date_to_field = None
        self.table_rows = None
        self.pagination_container = None
        self.current_dialog = None
        self.kpi_container = None
        self.current_date_filter = "all"  # all, today, week, month

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

        content_area = ft.Container(
            content=ft.Column(
                [
                    self.kpi_container,
                    search_bar,
                    table,
                    self.pagination_container,
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F5F7FA",
        )

        main_content = ft.Container(
            content=ft.Column(
                [header, content_area],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            bgcolor="#F5F7FA",
        )

        self.load_invoices()
        return main_content

    # ─────────────────────────────────────────────────────────────
    # Header
    # ─────────────────────────────────────────────────────────────
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.LOCAL_SHIPPING,
                                        size=22,
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.Text(
                                        "ໃບສົ່ງມອບລົດ",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Text(
                                "ລາຍຊື່ໃບສົ່ງມອບລົດທີ່ຊຳລະເງິນສຳເລັດແລ້ວ",
                                size=13,
                                color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=24, right=24, top=16, bottom=16),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )

    # ─────────────────────────────────────────────────────────────
    # KPI Cards
    # ─────────────────────────────────────────────────────────────
    def _build_kpi_cards(self):
        """Build KPI cards showing count of delivery notes"""
        total = len(self.invoices)
        
        # Calculate today's deliveries
        today = datetime.now().date()
        today_count = sum(1 for inv in self.invoices if self._get_paid_date(inv) == today)
        
        # Calculate this week's deliveries
        week_start = today - timedelta(days=today.weekday())
        week_count = sum(1 for inv in self.invoices 
                        if week_start <= self._get_paid_date(inv) <= today)
        
        # Calculate this month's deliveries
        month_start = today.replace(day=1)
        month_count = sum(1 for inv in self.invoices 
                         if month_start <= self._get_paid_date(inv) <= today)
        
        cards = [
            {
                "label": "ທັງໝົດ",
                "count": total,
                "icon": ft.Icons.LIST_ALT,
                "color": "#607D8B",
                "filter": "all"
            },
            {
                "label": "ມື້ນີ້",
                "count": today_count,
                "icon": ft.Icons.TODAY,
                "color": "#2196F3",
                "filter": "today"
            },
            {
                "label": "ອາທິດນີ້",
                "count": week_count,
                "icon": ft.Icons.CALENDAR_VIEW_WEEK,
                "color": "#4CAF50",
                "filter": "week"
            },
            {
                "label": "ເດືອນນີ້",
                "count": month_count,
                "icon": ft.Icons.CALENDAR_MONTH,
                "color": "#FF9800",
                "filter": "month"
            },
        ]
        
        kpi_cards = []
        for card in cards:
            is_active = self.current_date_filter == card["filter"]
            kpi_cards.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(card["icon"], size=22, color=ft.Colors.WHITE),
                                bgcolor=card["color"],
                                border_radius=10,
                                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                            ),
                            ft.Column(
                                [
                                    ft.Text(str(card["count"]), size=22, weight=ft.FontWeight.BOLD, color="#1E293B"),
                                    ft.Text(card["label"], size=11, color="#64748B"),
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
                    border=ft.Border(
                        top=ft.BorderSide(2 if is_active else 1, card["color"] if is_active else "#E2E8F0"),
                        right=ft.BorderSide(2 if is_active else 1, card["color"] if is_active else "#E2E8F0"),
                        bottom=ft.BorderSide(2 if is_active else 1, card["color"] if is_active else "#E2E8F0"),
                        left=ft.BorderSide(2 if is_active else 1, card["color"] if is_active else "#E2E8F0"),
                    ),
                    expand=True,
                    ink=True,
                    on_click=lambda e, f=card["filter"]: self._kpi_filter(f),
                    shadow=ft.BoxShadow(
                        blur_radius=4,
                        color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                    ),
                )
            )
        
        return ft.Row(kpi_cards, spacing=12, expand=True)
    
    def _get_paid_date(self, invoice: Dict) -> datetime.date:
        """Extract paid date from invoice"""
        paid_date = invoice.get("paid_date", "")
        if not paid_date:
            return datetime.now().date()
        try:
            return datetime.strptime(str(paid_date)[:10], "%Y-%m-%d").date()
        except:
            return datetime.now().date()
    
    def _kpi_filter(self, filter_type: str):
        """Filter invoices by date range from KPI cards"""
        self.current_date_filter = filter_type
        self.current_page_num = 1
        self._update_kpi_cards()
        self.apply_filters()
    
    def _update_kpi_cards(self):
        """Update KPI cards highlight"""
        if self.kpi_container:
            self.kpi_container.content = self._build_kpi_cards()
            self.page.update()

    # ─────────────────────────────────────────────────────────────
    # Search bar
    # ─────────────────────────────────────────────────────────────
    def _build_search_bar(self):
        self.search_field = ft.TextField(
            hint_text="ຄົ້ນຫາດ້ວຍເລກໃບບິນ, ຊື່ລູກຄ້າ ຫຼື ທະບຽນລົດ...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        self.search_field.on_change = lambda e: self.apply_filters()

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
            self.current_date_filter = "all"
            self.page.update()
            self.apply_filters()
            self._update_kpi_cards()

        def clear_date_to(e):
            self.date_to_field.value = ""
            self.current_date_filter = "all"
            self.page.update()
            self.apply_filters()
            self._update_kpi_cards()

        self.date_from_field = ft.TextField(
            hint_text=get_text("date_from"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            suffix=ft.IconButton(icon=ft.Icons.CLOSE, on_click=clear_date_from, icon_size=16),
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            width=140,
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
            content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            width=140,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            read_only=True,
            on_focus=self._pick_date_to,
        )

        return ft.Container(
            content=ft.Row([
                self.search_field,
                self.date_from_field,
                self.date_to_field,
                refresh_button,
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
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
                self.current_date_filter = "all"
                self.page.update()
                self.apply_filters()
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
                self.apply_filters()
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

    # ─────────────────────────────────────────────────────────────
    # Table
    # ─────────────────────────────────────────────────────────────
    def _build_table(self):
        table_header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            get_text("invoice_no"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            get_text("job_number"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            get_text("customer_name"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=150,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            get_text("plate_number"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            "ຍີ່ຫໍ້ / ລຸ້ນ",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=150,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            "ວັນທີຊຳລະ",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=120,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            get_text("actions"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=160,
                        alignment=ft.Alignment(0, 0),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )

        self.table_rows = ft.Column(
            spacing=0, scroll=ft.ScrollMode.AUTO, expand=True
        )

        # Wrap table in a Row with horizontal scroll
        table_container = ft.Container(
            content=ft.Column(
                [
                    table_header,
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    self.table_rows,
                ],
                spacing=0,
            ),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.GREY_200),
                right=ft.BorderSide(1, ft.Colors.GREY_200),
                bottom=ft.BorderSide(1, ft.Colors.GREY_200),
                left=ft.BorderSide(1, ft.Colors.GREY_200),
            ),
            expand=True,
        )

        return ft.Container(
            content=ft.Row([table_container], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
        )

    # ─────────────────────────────────────────────────────────────
    # Data loading
    # ─────────────────────────────────────────────────────────────
    def load_invoices(self):
        self.table_rows.controls.clear()
        self.page.update()

        try:
            all_invoices = self.client.get_invoices()
            # Filter only paid invoices
            self.invoices = [
                inv for inv in all_invoices if inv.get("payment_status") == "paid"
            ]
            self.filtered_invoices = self.invoices.copy()
            self.kpi_container.content = self._build_kpi_cards()
            self.apply_filters()
        except Exception as ex:
            print(f"Error loading invoices: {ex}")
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.ERROR_OUTLINE,
                                size=48,
                                color=ft.Colors.RED_400,
                            ),
                            ft.Text(
                                f"Error: {str(ex)}", size=14, color=ft.Colors.RED_600
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
            )
            self.page.update()

    def apply_filters(self):
        keyword = (
            self.search_field.value.lower() if self.search_field.value else ""
        )
        
        filtered = self.invoices.copy()
        
        # Apply KPI date filter
        if self.current_date_filter == "today":
            today = datetime.now().date()
            filtered = [inv for inv in filtered if self._get_paid_date(inv) == today]
        elif self.current_date_filter == "week":
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            filtered = [inv for inv in filtered if week_start <= self._get_paid_date(inv) <= today]
        elif self.current_date_filter == "month":
            today = datetime.now().date()
            month_start = today.replace(day=1)
            filtered = [inv for inv in filtered if month_start <= self._get_paid_date(inv) <= today]
        
        # Apply search filter
        if keyword:
            filtered = [
                inv
                for inv in filtered
                if keyword in f"INV-{inv.get('id', 0):04d}".lower()
                or keyword in inv.get("customer_name", "").lower()
                or keyword in inv.get("plate_number", "").lower()
                or keyword in inv.get("job_no", "").lower()
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
            for inv in filtered:
                paid_date = self._get_paid_date(inv)
                if date_from and paid_date < date_from:
                    continue
                if date_to and paid_date > date_to:
                    continue
                result.append(inv)
            filtered = result
        
        self.filtered_invoices = filtered
        self.current_page_num = 1
        self.display_invoices()

    def display_invoices(self):
        self.table_rows.controls.clear()

        total_items = len(self.filtered_invoices)
        self.total_pages = max(
            1, (total_items + self.items_per_page - 1) // self.items_per_page
        )
        if self.current_page_num > self.total_pages:
            self.current_page_num = self.total_pages
        if self.current_page_num < 1:
            self.current_page_num = 1

        start_idx = (self.current_page_num - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_invoices[start_idx:end_idx]

        if page_items:
            for i, invoice in enumerate(page_items):
                self.table_rows.controls.append(
                    self._create_row(invoice, start_idx + i)
                )
        else:
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.LOCAL_SHIPPING,
                                size=64,
                                color=ft.Colors.GREY_300,
                            ),
                            ft.Text(
                                "ຍັງບໍ່ມີໃບສົ່ງມອບລົດ",
                                size=16,
                                color=ft.Colors.GREY_500,
                            ),
                            ft.Text(
                                "ໃບສົ່ງມອບຈະປາກົດຂຶ້ນເມື່ອໃບບິນຖືກຊຳລະສຳເລັດ",
                                size=13,
                                color=ft.Colors.GREY_400,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=ft.Padding(left=40, right=40, top=60, bottom=60),
                    alignment=ft.Alignment(0, 0),
                )
            )

        self._update_pagination()
        self.page.update()

    # ─────────────────────────────────────────────────────────────
    # Row builder
    # ─────────────────────────────────────────────────────────────
    def _create_row(self, invoice: Dict, index: int):
        invoice_id = invoice.get("id")
        invoice_no = f"INV-{invoice_id:04d}"
        job_no = invoice.get("job_no", "-")
        customer_name = invoice.get("customer_name", "-")
        plate_number = invoice.get("plate_number", "-")
        brand = invoice.get("brand", "")
        model = invoice.get("model", "")
        brand_model = f"{brand} {model}".strip() or "-"
        paid_date = invoice.get("paid_date", "")
        if paid_date:
            paid_date = paid_date[:10]
        else:
            paid_date = "-"

        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE

        print_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.LOCAL_SHIPPING, size=16, color=self.success_color
                    ),
                    ft.Text("ພິມໃບສົ່ງມອບ", size=12, color=self.success_color),
                ],
                spacing=4,
            ),
            on_click=lambda e, iid=invoice_id: self.print_delivery_note(iid),
            padding=ft.Padding(left=8, right=8, top=5, bottom=5),
            border_radius=6,
            border=ft.Border(
                top=ft.BorderSide(1, self.success_color),
                right=ft.BorderSide(1, self.success_color),
                bottom=ft.BorderSide(1, self.success_color),
                left=ft.BorderSide(1, self.success_color),
            ),
            ink=True,
        )

        view_btn = ft.Container(
            content=ft.Icon(
                ft.Icons.RECEIPT_OUTLINED, size=18, color=ft.Colors.GREY_500
            ),
            tooltip="ດູໃບບິນ",
            on_click=lambda e, iid=invoice_id: self.navigate(
                "invoice_list"
            ),
            padding=ft.Padding(left=6, right=6, top=4, bottom=4),
            border_radius=6,
            ink=True,
        )

        row = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            invoice_no,
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color="#1E293B",
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(job_no, size=13, color="#1E293B"),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            customer_name, size=13, color="#1E293B", max_lines=1
                        ),
                        width=150,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            plate_number,
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color="#1E293B",
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            brand_model, size=12, color="#64748B", max_lines=1
                        ),
                        width=150,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(paid_date, size=12, color="#64748B"),
                        width=120,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(
                        content=ft.Row([print_btn, view_btn], spacing=6),
                        width=160,
                        alignment=ft.Alignment(0, 0),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            bgcolor=row_bg,
        )

        return ft.Column(
            [row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0
        )

    # ─────────────────────────────────────────────────────────────
    # Print delivery note PDF
    # ─────────────────────────────────────────────────────────────
    def print_delivery_note(self, invoice_id: int):
        try:
            self._show_snack("ກຳລັງກຽມພິມໃບສົ່ງມອບລົດ...", "info")

            pdf_bytes = self.client.get_delivery_note_pdf(invoice_id)
            if not pdf_bytes:
                self._show_snack("ບໍ່ສາມາດສ້າງ PDF ໄດ້", "error")
                return

            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(
                os.path.join(base_dir, "..", "..", "..")
            )
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)

            invoice_no = f"INV-{invoice_id:04d}"
            pdf_path = os.path.join(
                output_dir, f"delivery_note_{invoice_no}.pdf"
            )
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)

            os.startfile(pdf_path)
            self._show_snack("ພິມໃບສົ່ງມອບລົດສຳເລັດ!", "success")

        except Exception as ex:
            print(f"Error printing delivery note: {ex}")
            self._show_snack(f"Error: {str(ex)}", "error")

    # ─────────────────────────────────────────────────────────────
    # Pagination
    # ─────────────────────────────────────────────────────────────
    def _update_pagination(self):
        prev_disabled = self.current_page_num <= 1
        next_disabled = self.current_page_num >= self.total_pages

        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_invoices)} {get_text('of')} {len(self.invoices)} {get_text('results')}",
                    size=12,
                    color="#64748B",
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_LEFT,
                                icon_size=20,
                                on_click=self._prev_page,
                                disabled=prev_disabled,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    f"{self.current_page_num}/{self.total_pages}",
                                    size=13,
                                    weight=ft.FontWeight.W_500,
                                    color="#1E293B",
                                ),
                                padding=ft.Padding(
                                    left=15, right=15, top=0, bottom=0
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_RIGHT,
                                icon_size=20,
                                on_click=self._next_page,
                                disabled=next_disabled,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                            ),
                        ]
                    ),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()

    def _prev_page(self, e=None):
        if self.current_page_num > 1:
            self.current_page_num -= 1
            self.display_invoices()

    def _next_page(self, e=None):
        if self.current_page_num < self.total_pages:
            self.current_page_num += 1
            self.display_invoices()

    # ─────────────────────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────────────────────
    def _show_snack(self, message: str, type="success"):
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