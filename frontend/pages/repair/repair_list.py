# pages/repair/repair_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime, date
import os
import asyncio

from i18n import get_text


class RepairListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.current_snackbar = None
        self.repair_orders = []
        self.filtered_orders = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.search_field = None
        self.status_filter = "all"
        self.date_from_field = None
        self.date_to_field = None
        self.table_rows = None
        self.pagination_container = None
        self.kpi_container = None
        self._mechanics_cache = None
        self.current_dialog = None
        self.payment_dialog = None
        self.table_container = None

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
                [header, content_area], scroll=ft.ScrollMode.AUTO
            ),
            expand=True,
            bgcolor="#F5F7FA",
        )

        self.page.run_task(self._load_data_async)

        return main_content

    async def _load_data_async(self):
        await asyncio.sleep(0.1)
        await asyncio.to_thread(self.load_repair_orders)

    # ─────────────────────────── HEADER ───────────────────────────
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("repair_list_title"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                                ft.Text(
                                    get_text("new_repair"),
                                    size=14,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ],
                            spacing=6,
                        ),
                        on_click=lambda e: self.navigate("repair_create"),
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
            ("working",   "#2196F3", ft.Icons.BUILD),
            ("completed", "#4CAF50", ft.Icons.CHECK_CIRCLE),
        ]
        status_texts = {
            "working":   get_text("working"),
            "completed": get_text("completed"),
        }
        counts = {s: 0 for s, _, __ in statuses}
        for r in self.repair_orders:
            st = r.get("status", "working")
            if st in counts:
                counts[st] += 1

        cards = []
        for status, color, icon in statuses:
            count = counts[status]
            label = status_texts[status]
            is_active = (
                self.status_filter == status
            )
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

        total = len(self.repair_orders)
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
        self.filter_repairs(None)

    # ─────────────────────────── SEARCH BAR ───────────────────────────
    def _build_search_bar(self):
        self.search_field = ft.TextField(
            hint_text=get_text("search_repair"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        self.search_field.on_change = self.search_repairs

        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_repair_orders(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )

        def clear_date_from(e):
            self.date_from_field.value = ""
            self.page.update()
            self.search_repairs(None)

        def clear_date_to(e):
            self.date_to_field.value = ""
            self.page.update()
            self.search_repairs(None)

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
            content=ft.Column(
                [
                    ft.Row([self.search_field, refresh_button], spacing=10),
                    ft.Row([self.date_from_field, self.date_to_field], spacing=10),
                ],
                spacing=8,
            ),
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
                self.search_repairs(None)
                
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
                self.search_repairs(None)
                
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
        def _header_cell(text, width, align=-1):
            return ft.Container(
                content=ft.Text(text, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                width=width,
                alignment=ft.Alignment(align, 0),
                padding=ft.Padding(left=10, right=0, top=0, bottom=0) if align == -1 else None,
            )

        table_header = ft.Container(
            content=ft.Row(
                [
                    _header_cell(get_text("repair_no"), 100),
                    _header_cell(get_text("job_number"), 100),
                    _header_cell(get_text("customer_name"), 140),
                    _header_cell(get_text("plate_number"), 100),
                    _header_cell(get_text("vehicle"), 120),
                    _header_cell(get_text("mechanic"), 130),
                    # NEW: Parts Withdrawn Status Column
                    _header_cell("ອາໄຫຼ່", 80, 0),
                    _header_cell(get_text("status"), 110, 0),
                    _header_cell(get_text("days_open"), 100, 0),
                    _header_cell(get_text("actions"), 200, 0),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )

        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        table_content = ft.Column(
            [table_header, ft.Divider(height=1, color=ft.Colors.GREY_300), self.table_rows],
            spacing=0,
        )

        table_scroll = ft.Container(
            content=table_content,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            width=1250,  # เพิ่มความกว้างให้พอดีกับคอลัมน์ใหม่
        )

        # Wrap table in scrollable row
        self.table_container = ft.Container(
            content=ft.Row([table_scroll], scroll=ft.ScrollMode.AUTO, expand=True),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            expand=True,
        )
        
        return self.table_container

    # ─────────────────────────── DATA LOADING ───────────────────────────
    def load_repair_orders(self):
        self.table_rows.controls.clear()
        self.page.update()
        try:
            repair_orders = self.client.get_repair_orders()
            self.repair_orders = repair_orders
            self.filtered_orders = repair_orders.copy()
            self.kpi_container.content = self._build_kpi_cards()
            self.display_repairs()
        except Exception as ex:
            print(f"Error loading repair orders: {ex}")
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                            ft.Text(f"Error: {str(ex)}", size=14, color=ft.Colors.RED_600),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
            )
            self.page.update()

    # ─────────────────────────── FILTERING ───────────────────────────
    def filter_repairs(self, e):
        status = self.status_filter
        if status and status != "all":
            self.filtered_orders = [r for r in self.repair_orders if r.get("status") == status]
        else:
            self.filtered_orders = self.repair_orders.copy()

        keyword = (
            self.search_field.value.lower()
            if self.search_field and self.search_field.value
            else ""
        )
        if keyword:
            self.filtered_orders = [r for r in self.filtered_orders if self._matches_keyword(r, keyword)]

        self._apply_date_filter()
        self.current_page = 1
        self.kpi_container.content = self._build_kpi_cards()
        self.display_repairs()

    def search_repairs(self, e):
        keyword = (
            self.search_field.value.lower()
            if self.search_field and self.search_field.value
            else ""
        )
        status = self.status_filter

        self.filtered_orders = [r for r in self.repair_orders if self._matches_keyword(r, keyword)]
        if status and status != "all":
            self.filtered_orders = [r for r in self.filtered_orders if r.get("status") == status]

        self._apply_date_filter()
        self.current_page = 1
        self.display_repairs()

    def _matches_keyword(self, r: dict, keyword: str) -> bool:
        if not keyword:
            return True
        repair_id = r.get("id", 0)
        repair_no = f"R{repair_id:04d}" if isinstance(repair_id, int) else f"R{str(repair_id)}"
        return (
            keyword in repair_no.lower()
            or keyword in r.get("job_no", "").lower()
            or keyword in r.get("customer_name", "").lower()
            or keyword in r.get("plate_number", "").lower()
            or keyword in r.get("mechanic_name", "").lower()
            or keyword in (r.get("brand") or "").lower()
            or keyword in (r.get("model") or "").lower()
        )

    def _apply_date_filter(self):
        date_from_str = self.date_from_field.value.strip() if self.date_from_field and self.date_from_field.value else ""
        date_to_str   = self.date_to_field.value.strip()   if self.date_to_field   and self.date_to_field.value   else ""
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
        result = []
        for r in self.filtered_orders:
            sd_str = r.get("start_date", "")
            if not sd_str:
                continue
            try:
                sd = datetime.strptime(str(sd_str)[:10], "%Y-%m-%d").date()
            except ValueError:
                continue
            if date_from and sd < date_from:
                continue
            if date_to and sd > date_to:
                continue
            result.append(r)
        self.filtered_orders = result

    # ─────────────────────────── DISPLAY ───────────────────────────
    def display_repairs(self):
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

        if page_items:
            for i, order in enumerate(page_items):
                self.table_rows.controls.append(self._create_repair_row(order, start_idx + i))
        else:
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.CONSTRUCTION, size=48, color=ft.Colors.GREY_400),
                            ft.Text(get_text("no_repair_orders"), size=16, color=ft.Colors.GREY_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
            )

        self.update_pagination()
        self.page.update()

    # ─────────────────────────── ROW BUILDER ───────────────────────────
    def _create_repair_row(self, order: Dict, index: int):
        repair_id     = order.get("id")
        repair_no     = f"R{repair_id:04d}" if isinstance(repair_id, int) else f"R{str(repair_id)}"
        job_no        = order.get("job_no", "-")
        customer_name = order.get("customer_name", "-")
        plate_number  = order.get("plate_number", "-")
        brand         = order.get("brand") or ""
        model         = order.get("model") or ""
        vehicle_text  = f"{brand} {model}".strip() or "-"
        mechanic_name = order.get("mechanic_name") or ""
        status        = order.get("status", "working")
        start_date_str = order.get("start_date", "")
        end_date_str   = order.get("end_date", "")
        parts_usage_count = order.get("parts_usage_count", 0)
        quotation_parts_count = order.get("quotation_parts_count", 0)

        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE

        status_colors = {
            "working":   "#2196F3",
            "completed": "#4CAF50",
        }
        status_texts = {
            "working":   get_text("working"),
            "completed": get_text("completed"),
        }

        is_completed = status == "completed"
        badge_children = [
            ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
            ft.Text(status_texts.get(status, status), size=11, color=ft.Colors.WHITE),
        ]
        if not is_completed:
            badge_children.append(ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=ft.Colors.WHITE))

        status_badge = ft.Container(
            content=ft.Row(badge_children, spacing=4),
            bgcolor=status_colors.get(status, "#607D8B"),
            border_radius=12,
            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            on_click=(
                None if is_completed
                else lambda e, rid=repair_id, cur=status, used=parts_usage_count, quoted=quotation_parts_count: self.show_update_status_dialog(rid, cur, used, quoted)
            ),
        )

        duration_badge = self._build_duration_badge(start_date_str, end_date_str, status)
        mechanic_cell  = self._build_mechanic_cell(mechanic_name, repair_id)

        # ─── NEW: Parts Withdrawn Status Badge ───
        if parts_usage_count > 0:
            parts_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=12, color="#10B981"),
                    ft.Text("ເບີກແລ້ວ", size=10, color="#10B981", weight=ft.FontWeight.W_500),
                ], spacing=4),
                bgcolor=ft.Colors.with_opacity(0.1, "#10B981"),
                border_radius=10,
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                tooltip=f"ເບີກອາໄຫຼ່ທັງໝົດ {parts_usage_count} ລາຍການ",
            )
        else:
            parts_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.REMOVE_CIRCLE_OUTLINE, size=12, color="#94A3B8"),
                    ft.Text("ຍັງບໍ່ເບີກ", size=10, color="#94A3B8"),
                ], spacing=4),
                bgcolor=ft.Colors.GREY_100,
                border_radius=10,
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            )

        view_btn = ft.IconButton(
            icon=ft.Icons.VISIBILITY_OUTLINED,
            icon_size=20,
            icon_color=self.primary_color,
            tooltip=get_text("view"),
            on_click=lambda e, rid=repair_id: self.view_repair_detail(rid, read_only=True),
        )

        if is_completed:
            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_size=20,
                icon_color=ft.Colors.GREY_400,
                tooltip=get_text("cannot_delete_completed_repair"),
                disabled=True,
            )
        else:
            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_size=20,
                icon_color=ft.Colors.RED_600,
                tooltip=get_text("delete"),
                on_click=lambda e, rid=repair_id, rno=repair_no: self.confirm_delete(rid, rno),
            )
            
        print_btn = ft.IconButton(
            icon=ft.Icons.PRINT_OUTLINED,
            icon_size=20,
            icon_color=self.primary_color,
            tooltip=get_text("print"),
            on_click=lambda e, rid=repair_id: self.print_repair(rid),
        )
        
        add_part_btn = ft.IconButton(
            icon=ft.Icons.ADD_SHOPPING_CART,
            icon_size=20,
            icon_color=ft.Colors.ORANGE_600,
            tooltip="ເບິກອາໄຫຼ່",
            on_click=lambda e, rid=repair_id: self.view_repair_detail(rid, read_only=False),
            visible=not is_completed,
        )

        def _cell(content, width, align=-1, left_pad=True):
            return ft.Container(
                content=content,
                width=width,
                alignment=ft.Alignment(align, 0),
                padding=ft.Padding(left=10, right=0, top=0, bottom=0) if (left_pad and align == -1) else None,
            )

        row = ft.Container(
            content=ft.Row(
                [
                    _cell(ft.Text(repair_no, size=13, weight=ft.FontWeight.W_500, color="#1E293B"), 100),
                    _cell(ft.Text(job_no, size=13, color="#1E293B"), 100),
                    _cell(ft.Container(content=ft.Text(customer_name, size=13, color="#1E293B", max_lines=1), tooltip=customer_name), 140),
                    _cell(ft.Text(plate_number, size=12, color="#64748B", max_lines=1), 100),
                    _cell(ft.Container(content=ft.Text(vehicle_text, size=12, color="#64748B", max_lines=1), tooltip=vehicle_text), 120),
                    _cell(mechanic_cell, 130),
                    _cell(parts_badge, 80, 0, False),
                    _cell(status_badge, 110, 0, False),
                    _cell(duration_badge, 100, 0, False),
                    _cell(ft.Row([add_part_btn, view_btn, print_btn, delete_btn], spacing=0), 200, 0, False),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            bgcolor=row_bg,
        )

        return ft.Column([row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0)

    # ── Duration badge ──
    def _build_duration_badge(self, start_date_str: str, end_date_str: str, status: str) -> ft.Control:
        try:
            if not start_date_str:
                return ft.Text("-", size=10, color="#94A3B8")
            start_d = datetime.strptime(str(start_date_str)[:10], "%Y-%m-%d").date()

            if status == "completed" and end_date_str:
                end_d = datetime.strptime(str(end_date_str)[:10], "%Y-%m-%d").date()
                days = (end_d - start_d).days
                return ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=10, color="#4CAF50"),
                            ft.Text(f"{days}d", size=10, color="#4CAF50", weight=ft.FontWeight.W_600),
                        ],
                        spacing=2,
                    ),
                    tooltip=get_text("duration_completed").format(days),
                )

            days = (date.today() - start_d).days
            color = "#10B981" if days < 3 else "#F59E0B" if days < 7 else "#EF4444"
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.TIMER, size=10, color=color),
                        ft.Text(f"{days}d", size=10, color=color, weight=ft.FontWeight.W_600),
                    ],
                    spacing=2,
                ),
                tooltip=get_text("days_running").format(days),
            )
        except Exception:
            return ft.Text("-", size=10, color="#94A3B8")

    # ── Mechanic cell ──
    def _build_mechanic_cell(self, mechanic_name: str, repair_id: int) -> ft.Control:
        if mechanic_name and mechanic_name != "-":
            return ft.Text(mechanic_name, size=12, color="#64748B", max_lines=1)

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.WARNING, size=13, color="#F59E0B"),
                        ft.Text(get_text("no_mechanic_assigned"), size=10, color="#F59E0B"),
                    ],
                    spacing=2,
                ),
                ft.Container(
                    content=ft.Text(
                        get_text("assign"),
                        size=10,
                        color=self.primary_color,
                        weight=ft.FontWeight.W_600,
                    ),
                    on_click=lambda e, rid=repair_id: self.show_assign_mechanic_dialog(rid),
                    border_radius=4,
                    padding=ft.Padding(left=4, right=4, top=2, bottom=2),
                    border=ft.Border(top=ft.BorderSide(1, self.primary_color), right=ft.BorderSide(1, self.primary_color), bottom=ft.BorderSide(1, self.primary_color), left=ft.BorderSide(1, self.primary_color)),
                    ink=True,
                ),
            ],
            spacing=2,
        )

    # ─────────────────────────── PAGINATION ───────────────────────────
    def update_pagination(self):
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages

        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_orders)} "
                    f"{get_text('of')} {len(self.repair_orders)} "
                    f"{get_text('results')}",
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
                                on_click=self.prev_page,
                                disabled=prev_disabled,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    f"{self.current_page}/{self.total_pages}",
                                    size=13,
                                    weight=ft.FontWeight.W_500,
                                    color="#1E293B",
                                ),
                                padding=ft.Padding(left=15, right=15, top=0, bottom=0),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_RIGHT,
                                icon_size=20,
                                on_click=self.next_page,
                                disabled=next_disabled,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
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

    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_repairs()

    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_repairs()

    # ─────────────────────────── NAVIGATION ───────────────────────────
    def view_repair_detail(self, repair_id: int, read_only: bool = False):
        self.page.overlay.clear()
        self.navigate("repair_detail", repair_id=repair_id, read_only=read_only)

    # ─────────────────────────── STATUS STEPPER DIALOG ───────────────────────────
    def show_update_status_dialog(self, repair_id: int, current_status: str, parts_usage_count: int = 0, quotation_parts_count: int = 0):
        if current_status == "completed":
            self.show_snack_bar(get_text("cannot_update_completed_status"), "error")
            return

        steps = [
            ("working",   get_text("working"),   "#2196F3", ft.Icons.BUILD),
            ("completed", get_text("completed"), "#4CAF50", ft.Icons.CHECK_CIRCLE),
        ]

        state = {"selected": current_status}
        step_row = ft.Row(spacing=8)

        def _make_step_btn(key, label, color, icon, is_selected):
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                            bgcolor=color,
                            border_radius=10,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(
                            label, size=11, color="#1E293B",
                            weight=ft.FontWeight.W_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                border_radius=12,
                bgcolor=(
                    ft.Colors.with_opacity(0.12, color) if is_selected else ft.Colors.WHITE
                ),
                border=(
                    ft.Border(top=ft.BorderSide(2, color), right=ft.BorderSide(2, color), bottom=ft.BorderSide(2, color), left=ft.BorderSide(2, color)) if is_selected
                    else ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200))
                ),
                ink=True,
                on_click=lambda e, k=key, c=color: _on_step_click(k, c),
                width=90,
                alignment=ft.Alignment(0, 0),
            )

        def _rebuild_steps(selected_key):
            step_row.controls.clear()
            for k, lbl, col, ico in steps:
                step_row.controls.append(_make_step_btn(k, lbl, col, ico, k == selected_key))

        def _on_step_click(k, c):
            state["selected"] = k
            _rebuild_steps(k)
            self.page.update()

        _rebuild_steps(current_status)

        def confirm_update(e):
            new_status = state["selected"]
            if new_status == current_status:
                self.close_dialog(dialog)
                return
            if new_status == "completed":
                if quotation_parts_count > 0 and parts_usage_count == 0:
                    self.show_snack_bar(get_text("must_withdraw_parts_before_complete"), "error")
                    return
                confirm_dialog = ft.AlertDialog(
                    modal=True,
                    shape=ft.RoundedRectangleBorder(radius=16),
                    bgcolor=ft.Colors.WHITE,
                    title=ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.WARNING, size=22, color=ft.Colors.WHITE),
                                    bgcolor="#F59E0B",
                                    border_radius=10,
                                    padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                                ),
                                ft.Text(get_text("confirm_complete_repair"), size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ],
                            spacing=10,
                        ),
                        padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                        border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                    ),
                    content=ft.Container(
                        content=ft.Text(get_text("confirm_complete_repair_msg"), size=14, color="#64748B"),
                        padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                        width=360,
                    ),
                    actions=[
                        ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(confirm_dialog)),
                        ft.ElevatedButton(
                            get_text("confirm"),
                            on_click=lambda e: self._do_update_status(repair_id, new_status, dialog, confirm_dialog),
                            style=ft.ButtonStyle(bgcolor="#4CAF50", color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                self.page.overlay.append(confirm_dialog)
                confirm_dialog.open = True
                self.page.update()
            else:
                self._do_update_status(repair_id, new_status, dialog)

        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=22, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=10,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(get_text("update_repair_status"), size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(get_text("select_new_status"), size=13, color="#64748B"),
                        ft.Container(height=10),
                        step_row,
                    ],
                    spacing=0,
                ),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                width=300,
                height=140,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(
                    get_text("update"),
                    on_click=confirm_update,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _do_update_status(self, repair_id, new_status, *dialogs):
        try:
            self.client.update_repair_status(repair_id, new_status)
            for d in dialogs:
                if d:
                    d.open = False
            self.page.update()
            self.load_repair_orders()
            self.show_snack_bar(
                f"{get_text('status_updated_to')} {get_text(new_status)}", "success"
            )
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", "error")

    # ─────────────────────────── ASSIGN MECHANIC DIALOG ───────────────────────────
    def show_assign_mechanic_dialog(self, repair_id: int):
        if self._mechanics_cache is None:
            try:
                self._mechanics_cache = self.client.get_mechanics() or []
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", "error")
                return

        if not self._mechanics_cache:
            self.show_snack_bar(get_text("no_mechanic_assigned"), "error")
            return

        state = {"mechanic_id": None}
        mech_cards = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=240)

        def build_mechanic_list(selected_id=None):
            mech_cards.controls.clear()
            for m in self._mechanics_cache:
                mid   = m.get("id")
                name  = m.get("fullname", m.get("name", "-"))
                phone = m.get("phone", "-")
                is_sel = mid == selected_id

                def on_select(e, _id=mid):
                    state["mechanic_id"] = _id
                    build_mechanic_list(_id)
                    self.page.update()

                card = ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.PERSON, size=20,
                                    color=self.primary_color if is_sel else "#64748B",
                                ),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color) if is_sel else ft.Colors.GREY_100,
                                border_radius=10,
                                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                            ),
                            ft.Column(
                                [
                                    ft.Text(name, size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                                    ft.Text(phone, size=11, color="#64748B"),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE if is_sel else ft.Icons.CIRCLE,
                                size=20,
                                color=self.success_color if is_sel else "#CBD5E1",
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                    bgcolor=ft.Colors.with_opacity(0.05, self.primary_color) if is_sel else ft.Colors.WHITE,
                    border_radius=10,
                    border=ft.Border(top=ft.BorderSide(1, self.primary_color if is_sel else ft.Colors.GREY_200), right=ft.BorderSide(1, self.primary_color if is_sel else ft.Colors.GREY_200), bottom=ft.BorderSide(1, self.primary_color if is_sel else ft.Colors.GREY_200), left=ft.BorderSide(1, self.primary_color if is_sel else ft.Colors.GREY_200)),
                    ink=True,
                    on_click=on_select,
                )
                mech_cards.controls.append(card)

        build_mechanic_list()

        def confirm_assign(e):
            mid = state["mechanic_id"]
            if not mid:
                self.show_snack_bar(get_text("please_select_mechanic"), "error")
                return
            try:
                self.client.assign_mechanic(repair_id, mid)
                self.close_dialog(dialog)
                self.load_repair_orders()
                self.show_snack_bar(f"{get_text('mechanic_assigned')}", "success")
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", "error")

        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON_ADD, size=22, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=10,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(get_text("assign_mechanic"), size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(content=mech_cards, padding=ft.Padding(left=20, right=20, top=20, bottom=20), width=380),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(
                    get_text("assign"),
                    on_click=confirm_assign,
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def confirm_delete(self, repair_id: int, repair_no: str):
        def do_delete(e):
            self.close_dialog(dialog)
            try:
                self.client.delete_repair_order(repair_id)
                self.load_repair_orders()
                self.show_snack_bar(f"{get_text('delete_success')}", "success")
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", "error")

        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_600, size=24),
                ft.Text(get_text("confirm_delete"), size=16, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            content=ft.Text(
                f"{get_text('delete_confirmation')}\n{repair_no}",
                size=14,
                color="#475569",
            ),
            actions=[
                ft.TextButton(
                    get_text("cancel"),
                    on_click=lambda e: self.close_dialog(dialog),
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
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    # ─────────────────────────── UTILITIES ───────────────────────────
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def show_snack_bar(self, message: str, type="success"):
        """Show snackbar notification - Bottom center with auto width"""
        
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
        
        snackbar = ft.Container(
            content=snack_content,
            margin=ft.Margin(left=30, right=30, top=0, bottom=20),
            alignment=ft.Alignment(0, 1),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            opacity=0,
        )
        
        self.page.overlay.append(snackbar)
        self.current_snackbar = snackbar
        
        snackbar.opacity = 1
        self.page.update()
        
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
        
        self.page.run_task(dismiss_after_delay)

    def print_repair(self, repair_id: int):
        try:
            self.show_snack_bar(get_text("preparing_print"), "info")
            pdf_bytes = self.client.get_repair_order_pdf(repair_id)
            if not pdf_bytes:
                self.show_snack_bar(get_text("pdf_export_failed"), "error")
                return
                
            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            file_path = os.path.join(output_dir, f"repair_work_order_{repair_id}.pdf")
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)
                
            os.startfile(file_path)
            self.show_snack_bar(get_text("pdf_export_success"), "success")
        except Exception as ex:
            print(f"Error printing repair order: {ex}")
            self.show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", "error")