# pages/purchase/goods_receipt_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import asyncio
from datetime import datetime, timedelta

from i18n import get_text


class ReceivingManagementContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.current_snackbar = None
        self.receipts = []
        self.filtered_receipts = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.search_field = None
        self.date_from_field = None
        self.date_to_field = None
        self.table_rows = None
        self.pagination_container = None
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
        self.pagination_container = ft.Container(padding=ft.Padding(left=20, right=20, top=12, bottom=12))
        
        content_area = ft.Container(
            content=ft.Column([
                self.kpi_container,
                search_bar,
                table,
                self.pagination_container,
            ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.load_receipts()
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                "ຂໍ້ມູນການນຳເຂົ້າ",
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
                            ft.Text("ສ້າງໃບນຳເຂົ້າ", size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.navigate("receiving_po_list"),
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
        """Build KPI cards for receipt statistics"""
        total = len(self.receipts)
        
        # Calculate today's receipts
        today = datetime.now().date()
        today_count = sum(1 for r in self.receipts if self._get_receipt_date(r) == today)
        
        # Calculate this week's receipts
        week_start = today - timedelta(days=today.weekday())
        week_count = sum(1 for r in self.receipts 
                        if week_start <= self._get_receipt_date(r) <= today)
        
        # Calculate this month's receipts
        month_start = today.replace(day=1)
        month_count = sum(1 for r in self.receipts 
                         if month_start <= self._get_receipt_date(r) <= today)
        
        cards = [
            {
                "label": get_text("total") if get_text("total") else "ທັງໝົດ",
                "count": total,
                "icon": ft.Icons.LIST_ALT,
                "color": "#607D8B",
                "filter": "all"
            },
            {
                "label": get_text("today") if get_text("today") else "ມື້ນີ້",
                "count": today_count,
                "icon": ft.Icons.TODAY,
                "color": "#2196F3",
                "filter": "today"
            },
            {
                "label": get_text("this_week") if get_text("this_week") else "ອາທິດນີ້",
                "count": week_count,
                "icon": ft.Icons.CALENDAR_VIEW_WEEK,
                "color": "#4CAF50",
                "filter": "week"
            },
            {
                "label": get_text("this_month") if get_text("this_month") else "ເດືອນນີ້",
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
    
    def _get_receipt_date(self, receipt: Dict) -> datetime.date:
        """Extract date from receipt"""
        receipt_date = receipt.get("receipt_date", "")
        if not receipt_date:
            return datetime.now().date()
        try:
            return datetime.strptime(str(receipt_date)[:10], "%Y-%m-%d").date()
        except:
            return datetime.now().date()
    
    def _kpi_filter(self, filter_type: str):
        """Filter receipts by date range from KPI cards"""
        self.current_date_filter = filter_type
        self.current_page = 1
        self._update_kpi_cards()
        self.apply_filters()
    
    def _update_kpi_cards(self):
        """Update KPI cards highlight"""
        if self.kpi_container:
            self.kpi_container.content = self._build_kpi_cards()
            self.page.update()
    
    # ─────────────────────────── SEARCH BAR ───────────────────────────
    def _build_search_bar(self):
        self.search_field = ft.TextField(
            hint_text=get_text("search_purchase_order") + " / " + get_text("goods_receipt_no"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            expand=True,
        )
        self.search_field.on_change = self.on_search_change
        
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
            on_click=lambda e: self.load_receipts(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.search_field,
                    self.date_from_field,
                    self.date_to_field,
                    refresh_button,
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=0),
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
        )
    
    # ─────────────────────────── DATE PICKER METHODS ───────────────────────────
    def _clear_date_from(self, e):
        self.date_from_field.value = ""
        self.current_date_filter = "all"
        self.page.update()
        self.apply_filters()
        self._update_kpi_cards()

    def _clear_date_to(self, e):
        self.date_to_field.value = ""
        self.current_date_filter = "all"
        self.page.update()
        self.apply_filters()
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
    
    # ─────────────────────────── TABLE ───────────────────────────
    def _build_table(self):
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("goods_receipt_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("po_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("supplier"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=180,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("receipt_date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=140,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("total_amount"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=8, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("received_by"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("action"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=80,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        table_content = ft.Column([
            table_header,
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            self.table_rows,
        ], spacing=0)
        
        table_scroll = ft.Container(
            content=table_content,
            width=950,
        )
        
        return ft.Container(
            content=ft.Row([table_scroll], scroll=ft.ScrollMode.AUTO),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
        )
    
    # ─────────────────────────── LOAD & FILTER DATA ───────────────────────────
    def load_receipts(self):
        self.table_rows.controls.clear()
        self.page.update()
        
        try:
            receipts = self.client.get_goods_receipts()
            self.receipts = receipts
            self.filtered_receipts = receipts.copy()
            self.kpi_container.content = self._build_kpi_cards()
            self.display_receipts()
        except Exception as ex:
            print(f"Error loading goods receipts: {ex}")
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
    
    def apply_filters(self):
        """Apply all filters (search, date range, KPI date filter)"""
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        
        # Start with all receipts
        filtered = self.receipts.copy()
        
        # Apply KPI date filter
        if self.current_date_filter == "today":
            today = datetime.now().date()
            filtered = [r for r in filtered if self._get_receipt_date(r) == today]
        elif self.current_date_filter == "week":
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            filtered = [r for r in filtered if week_start <= self._get_receipt_date(r) <= today]
        elif self.current_date_filter == "month":
            today = datetime.now().date()
            month_start = today.replace(day=1)
            filtered = [r for r in filtered if month_start <= self._get_receipt_date(r) <= today]
        
        # Apply search filter
        if keyword:
            filtered = [
                r for r in filtered
                if keyword in r.get("receipt_no", "").lower()
                or keyword in r.get("po_no", "").lower()
                or keyword in r.get("supplier_name", "").lower()
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
            for r in filtered:
                receipt_date = self._get_receipt_date(r)
                if date_from and receipt_date < date_from:
                    continue
                if date_to and receipt_date > date_to:
                    continue
                result.append(r)
            filtered = result
        
        self.filtered_receipts = filtered
        self.current_page = 1
        self.display_receipts()
            
    def on_search_change(self, e):
        self.apply_filters()
    
    # ─────────────────────────── DISPLAY ───────────────────────────
    def display_receipts(self):
        self.table_rows.controls.clear()
        total_items = len(self.filtered_receipts)
        
        if total_items == 0:
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=48, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_goods_receipts"), size=16, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
            )
            self.update_pagination()
            self.page.update()
            return
            
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
            
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_receipts[start_idx:end_idx]
        
        for i, receipt in enumerate(page_items):
            self.table_rows.controls.append(self._create_receipt_row(receipt, start_idx + i))
            
        self.update_pagination()
        self.page.update()
        
    def _create_receipt_row(self, receipt: Dict, index: int):
        receipt_id = receipt.get("id")
        receipt_no = receipt.get("receipt_no", "-")
        po_no = receipt.get("po_no", "-")
        supplier_name = receipt.get("supplier_name", "-")
        receipt_date = receipt.get("receipt_date", "")
        if receipt_date:
            receipt_date = receipt_date[:16]
        else:
            receipt_date = "-"
        total_amount = receipt.get("total_amount", 0)
        received_by_name = receipt.get("received_by_name", "-")
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        view_btn = ft.IconButton(
            icon=ft.Icons.VISIBILITY_OUTLINED,
            icon_size=18,
            tooltip=get_text("view_receipt_detail"),
            on_click=lambda e: self.show_receipt_detail_dialog(receipt_id),
        )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(receipt_no, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=130,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(po_no, size=13, color="#1E293B"),
                    width=120,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(supplier_name, size=13, color="#1E293B", max_lines=1),
                    width=180,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(receipt_date, size=12, color="#64748B"),
                    width=140,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(f"{int(total_amount):,}", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=8, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(received_by_name, size=12, color="#64748B", max_lines=1),
                    width=130,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=view_btn,
                    width=80,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=10, bottom=10),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    # ─────────────────────────── DIALOG ───────────────────────────
    def show_receipt_detail_dialog(self, receipt_id: int):
        try:
            detail = self.client.get_goods_receipt(receipt_id)
            if not detail:
                self.show_snack_bar("Goods receipt details not found", "error")
                return
                
            items = detail.get("items", [])
            items_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=250)
            
            for idx, item in enumerate(items):
                bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
                
                qty = item.get("qty_received", 0)
                cost = item.get("cost_price", 0)
                line_total = item.get("total_price", 0)
                
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Text(f"#{item.get('part_id')}", size=12, color="#64748B", width=60),
                        ft.Text(item.get("part_name", "-"), size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(f"{qty}", size=13, color="#1E293B", width=60, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{int(cost):,}", size=13, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                        ft.Text(f"{int(line_total):,}", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700, width=110, text_align=ft.TextAlign.RIGHT),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    bgcolor=bg_color,
                    border_radius=8,
                )
                items_list.controls.append(item_row)
                
            dialog = ft.AlertDialog(
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=16),
                bgcolor=ft.Colors.WHITE,
                title=ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.INVENTORY, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(
                            f"{get_text('view_receipt_detail')}: {detail.get('receipt_no', '-')}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                    border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"{get_text('po_no')}: {detail.get('po_no', '-')}", size=13, color="#64748B"),
                            ft.Container(expand=True),
                            ft.Text(f"{get_text('receipt_date')}: {detail.get('receipt_date', '')[:16]}", size=13, color="#64748B"),
                        ]),
                        ft.Row([
                            ft.Text(f"{get_text('supplier')}: {detail.get('supplier_name', '-')}", size=13, color="#64748B"),
                            ft.Container(expand=True),
                            ft.Text(f"{get_text('received_by')}: {detail.get('received_by_name', '-')}", size=13, color="#64748B"),
                        ]),
                        ft.Container(height=12),
                        ft.Row([
                            ft.Text(get_text("part_id"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", width=60),
                            ft.Text(get_text("part_name"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                            ft.Text(get_text("qty"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", width=60, text_align=ft.TextAlign.CENTER),
                            ft.Text(get_text("unit_cost"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                            ft.Text(get_text("total"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", width=110, text_align=ft.TextAlign.RIGHT),
                        ], spacing=10),
                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                        items_list,
                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                        ft.Row([
                            ft.Text(get_text("total_amount"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                            ft.Text(f"{int(detail.get('total_amount', 0)):,} KIP", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ], spacing=10),
                    padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                    width=650,
                    height=450,
                ),
                actions=[
                    ft.TextButton(
                        get_text("close"),
                        on_click=lambda e: self._close_dialog(dialog),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self._open_dialog(dialog)
        except Exception as ex:
            print(f"Error displaying receipt details: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", "error")
            
    def _open_dialog(self, dialog):
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
        
    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    # ─────────────────────────── PAGINATION ───────────────────────────
    def update_pagination(self):
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_receipts)} {get_text('of')} {len(self.receipts)} {get_text('results')}",
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
            self.display_receipts()
            
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_receipts()
    
    # ─────────────────────────── SNACK BAR ───────────────────────────
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