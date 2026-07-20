# pages/repair/repair_detail.py
import asyncio

import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime, date

from i18n import get_text


class RepairDetailContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, repair_id: int = None, read_only: bool = False):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.repair_id = repair_id
        self.read_only = read_only
        self.repair_data = None
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.warning_color = "#F59E0B"
        self.current_snackbar = None
        self.parts_list = []
        self.selected_part_id = None
        self.qty_field = None
        self.selected_stock = None
        self.current_dialog = None
        self.content_area = None
        
    def build(self):
        header = self._build_header()
        
        self.content_area = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Container(height=20),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F8FAFC",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area], expand=True),
            expand=True,
            bgcolor="#F1F5F9",
        )
        
        self.page.run_task(self._load_data)
        
        return main_content
    
    async def _load_data(self):
        await asyncio.sleep(0.1)
        await asyncio.to_thread(self.load_repair_data)
        await asyncio.to_thread(self.load_parts)
        self._refresh_content()
    
    def _refresh_content(self):
        if not self.repair_data:
            self.content_area.content = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED_400),
                ft.Container(height=16),
                ft.Text(get_text("error_loading_data"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16)
            self.content_area.update()
            return
        
        new_content = self._build_content()
        self.content_area.content = ft.Column([new_content], scroll=ft.ScrollMode.AUTO, expand=True)
        self.content_area.update()
    
    def _build_header(self):
        update_status_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("update_status"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=6),
            on_click=self.show_update_status_dialog,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=0,
                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
            ),
            visible=not getattr(self, 'read_only', False)
        )
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=20,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("repair_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("repair_detail"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    update_status_btn,
                ],
                spacing=12,
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
    
    def load_repair_data(self):
        try:
            if self.repair_id:
                self.repair_data = self.client.get_repair_order(self.repair_id)
                print(f"DEBUG: Loaded repair data for {self.repair_id}")
                
                if self.repair_data and self.repair_data.get('job_order_id'):
                    self.load_quotation_items(self.repair_data.get('job_order_id'))
        except Exception as ex:
            print(f"Error loading repair detail: {ex}")
    
    def load_quotation_items(self, job_order_id: int):
        try:
            quotations = self.client.get_quotations(job_order_id=job_order_id) or []
            approved_quotation = None
            for q in quotations:
                if q.get('status') == 'approved':
                    approved_quotation = q
                    break
            
            if approved_quotation:
                items = self.client.get_quotation_items(approved_quotation.get('id')) or []
                self.quotation_items = []
                for item in items:
                    self.quotation_items.append({
                        'item_type': item.get('item_type'),
                        'name': item.get('name', '-'),
                        'qty': item.get('qty', 1),
                        'unit_price': item.get('unit_price', 0),
                        'total': item.get('total', 0)
                    })
                self.repair_data['quotation_items'] = self.quotation_items
        except Exception as ex:
            print(f"Error loading quotation items: {ex}")
    
    def load_parts(self):
        try:
            self.parts_list = self.client.get_parts()
        except Exception as ex:
            print(f"Error loading parts: {ex}")
            self.parts_list = []
    
    def _create_info_row(self, label, value):
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=12, color="#64748B", width=110),
                ft.Text(value, size=13, color="#1E293B", weight=ft.FontWeight.W_500 if "R" in value or any(c.isdigit() for c in value) else ft.FontWeight.W_400, expand=True),
            ], spacing=12),
            padding=ft.Padding(left=0, right=0, top=5, bottom=5),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)),
        )
    
    def _build_content(self):
        data = self.repair_data
        
        status_colors = {
            "working": "#2196F3",
            "completed": "#4CAF50"
        }
        status_texts = {
            "working": get_text("working"),
            "completed": get_text("completed")
        }
        
        repair_no = f"R{data.get('id', 0):04d}"
        status = data.get("status", "working")
        job_no = data.get("job_no", "-")
        customer_name = data.get("customer_name", "-")
        customer_phone = data.get("customer_phone", "-")
        plate_number = data.get("plate_number", "-")
        brand = data.get("brand", "-")
        model = data.get("model", "-")
        year = data.get("year", "")
        color = data.get("color", "-")
        problem = data.get("problem_description", "-")
        mechanic_name = data.get("mechanic_name", "-")
        start_date = data.get("start_date", "")
        end_date = data.get("end_date", "")
        parts_usage = data.get("parts_usage", [])
        quotation_items = data.get("quotation_items", [])
        
        if start_date:
            start_date = start_date[:16] if len(start_date) > 16 else start_date
        else:
            start_date = "-"
        if end_date:
            end_date = end_date[:16] if len(end_date) > 16 else end_date
        else:
            end_date = "-"
        
        status_badge = ft.Container(
            content=ft.Text(status_texts.get(status, status), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            bgcolor=status_colors.get(status, "#607D8B"),
            border_radius=20,
            padding=ft.Padding(left=14, right=14, top=5, bottom=5),
        )
        
        # ========== LEFT COLUMN ==========
        # Build elapsed-time duration display
        duration_ctrl = self._build_duration_display(
            data.get("start_date", ""), data.get("end_date", ""), status
        )

        # Repair Info Card
        repair_info_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CONSTRUCTION, size=18, color=self.primary_color),
                    ft.Text(get_text("repair_info"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Container(expand=True),
                    status_badge,
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=4),
                self._create_info_row(get_text("repair_no"), repair_no),
                self._create_info_row(get_text("mechanic"), mechanic_name),
                ft.Row([
                    ft.Container(self._create_info_row(get_text("start_date"), start_date), expand=True),
                    ft.Container(self._create_info_row(get_text("end_date"), end_date), expand=True),
                ], spacing=20),
                ft.Container(
                    content=ft.Row([
                        ft.Text(get_text("duration_label"), size=12, color="#64748B", width=110),
                        duration_ctrl,
                    ], spacing=12),
                    padding=ft.Padding(left=0, right=0, top=5, bottom=5),
                    border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)),
                ),
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.Margin(left=0, right=0, top=0, bottom=12),
        )
        
        # Job Info Card
        job_info_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                    ft.Text(get_text("job_order_info"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=4),
                self._create_info_row(get_text("job_number"), job_no),
                self._create_info_row(get_text("customer_name"), customer_name),
                self._create_info_row(get_text("customer_phone"), customer_phone),
                self._create_info_row(get_text("plate_number"), plate_number),
                self._create_info_row(get_text("car_brand_model"), f"{brand} {model} {f'({year})' if year else ''}"),
                self._create_info_row(get_text("car_color"), color),
                ft.Container(height=4),
                ft.Text(get_text("problem_description"), size=12, color="#64748B"),
                ft.Container(
                    content=ft.Text(problem, size=13, color="#1E293B"),
                    padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                    bgcolor="#F8FAFC",
                    border_radius=8,
                    margin=ft.Margin(left=0, right=0, top=4, bottom=0),
                ),
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.Margin(left=0, right=0, top=0, bottom=12),
        )
        
        left_column = ft.Container(
            content=ft.Column([repair_info_card, job_info_card], spacing=0),
            width=450,
            expand=True,
        )
        
        # ========== RIGHT COLUMN ==========
        # Quotation Items Card
        quotation_items_list = ft.Column(spacing=0)
        quotation_total = 0
        
        if quotation_items and len(quotation_items) > 0:
            for idx, item in enumerate(quotation_items):
                name = item.get('name', '-')
                qty = item.get('qty', 1)
                unit_price = item.get('unit_price', 0)
                total = item.get('total', 0)
                quotation_total += total
                
                border_bottom = ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)) if idx < len(quotation_items) - 1 else None
                
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Text(f"{idx+1}", size=12, color="#64748B", width=30),
                        ft.Text(name, size=12, color="#1E293B", expand=True, max_lines=2),
                        ft.Text(f"x{qty}", size=12, color="#64748B", width=45, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{int(unit_price):,}", size=12, color="#64748B", width=90, text_align=ft.TextAlign.RIGHT),
                        ft.Text(f"{int(total):,}", size=12, weight=ft.FontWeight.W_600, color=self.success_color, width=110, text_align=ft.TextAlign.RIGHT),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=0, right=0, top=6, bottom=6),
                    border=border_bottom,
                )
                quotation_items_list.controls.append(item_row)
            
            total_row = ft.Container(
                content=ft.Row([
                    ft.Container(expand=True),
                    ft.Text(get_text("total") + ":", size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Text(f"{int(quotation_total):,} KIP", size=14, weight=ft.FontWeight.W_700, color=self.success_color),
                ], spacing=12),
                padding=ft.Padding(left=0, right=0, top=8, bottom=8),
                bgcolor="#F8FAFC",
                border_radius=8,
                margin=ft.Margin(left=0, right=0, top=6, bottom=0),
            )
            quotation_items_list.controls.append(total_row)
        else:
            quotation_items_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.REQUEST_QUOTE, size=32, color="#CBD5E1"),
                        ft.Text(get_text("no_quotation_items"), size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.Padding(left=30, right=30, top=30, bottom=30),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        quotation_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.REQUEST_QUOTE, size=18, color=self.primary_color),
                    ft.Text(get_text("quotation_items"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PRICE_CHANGE, size=14, color=self.success_color),
                            ft.Text(f"{int(quotation_total):,} KIP", size=14, weight=ft.FontWeight.W_700, color=self.success_color),
                        ], spacing=4),
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                        bgcolor=ft.Colors.with_opacity(0.1, self.success_color),
                        border_radius=16,
                    ),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=4),
                ft.Row([
                    ft.Text("#", size=10, weight=ft.FontWeight.W_600, color="#64748B", width=30),
                    ft.Text(get_text("item_name"), size=10, weight=ft.FontWeight.W_600, color="#64748B", expand=True),
                    ft.Text(get_text("qty"), size=10, weight=ft.FontWeight.W_600, color="#64748B", width=45, text_align=ft.TextAlign.CENTER),
                    ft.Text(get_text("price"), size=10, weight=ft.FontWeight.W_600, color="#64748B", width=90, text_align=ft.TextAlign.RIGHT),
                    ft.Text(get_text("total"), size=10, weight=ft.FontWeight.W_600, color="#64748B", width=110, text_align=ft.TextAlign.RIGHT),
                ], spacing=6),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                quotation_items_list,
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.Margin(left=0, right=0, top=0, bottom=12),
        )
        
        # Parts Used Card
        parts_used_list = ft.Column(spacing=0)
        total_cost = 0
        
        if parts_usage and len(parts_usage) > 0:
            for idx, part in enumerate(parts_usage):
                usage_id = part.get("id")
                part_name = part.get("part_name", "-")
                qty = part.get("qty", 0)
                cost_price = part.get("cost_price", 0)
                total = qty * cost_price
                total_cost += total
                
                border_bottom = ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)) if idx < len(parts_usage) - 1 else None
                
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Text(f"{idx+1}", size=12, color="#64748B", width=30),
                        ft.Text(part_name, size=12, color="#1E293B", expand=True, max_lines=2),
                        ft.Text(f"x{qty}", size=12, color="#64748B", width=45, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{int(cost_price):,}", size=12, color="#64748B", width=90, text_align=ft.TextAlign.RIGHT),
                        ft.Text(f"{int(total):,}", size=12, weight=ft.FontWeight.W_600, color=self.success_color, width=110, text_align=ft.TextAlign.RIGHT),
                        ft.IconButton(
                            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            tooltip=get_text("return_part"),
                            on_click=lambda e, uid=usage_id: self.return_part(uid),
                            padding=0,
                            visible=not getattr(self, 'read_only', False),
                        ),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=0, right=0, top=6, bottom=6),
                    border=border_bottom,
                )
                parts_used_list.controls.append(item_row)
            
            total_row = ft.Container(
                content=ft.Row([
                    ft.Container(expand=True),
                    ft.Text(get_text("total_parts_cost") + ":", size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Text(f"{int(total_cost):,} KIP", size=14, weight=ft.FontWeight.W_700, color=self.success_color),
                ], spacing=12),
                padding=ft.Padding(left=0, right=0, top=8, bottom=8),
                bgcolor="#F8FAFC",
                border_radius=8,
                margin=ft.Margin(left=0, right=0, top=6, bottom=0),
            )
            parts_used_list.controls.append(total_row)
        else:
            parts_used_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INVENTORY, size=32, color="#CBD5E1"),
                        ft.Text(get_text("no_parts_used"), size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.Padding(left=30, right=30, top=30, bottom=30),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        add_part_btn = None
        if status != "completed" and not getattr(self, 'read_only', False):
            add_part_btn = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("add_part"), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                ], spacing=6),
                on_click=self.show_add_part_dialog,
                style=ft.ButtonStyle(
                    bgcolor=self.primary_color,
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                ),
            )

        pull_parts_btn = None
        quotation_parts_count = int(data.get("quotation_parts_count") or 0)
        has_quotation_parts = quotation_parts_count > 0 or any(
            item.get('item_type') == 'part' for item in quotation_items
        )
        if status != "completed" and has_quotation_parts and not getattr(self, 'read_only', False):
            pull_parts_btn = ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DOWNLOAD, size=14, color=ft.Colors.WHITE),
                        ft.Text(get_text("pull_quotation_parts"), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                    ], spacing=6),
                    on_click=self.confirm_pull_quotation_parts,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_600,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                    ),
                )

        action_buttons = []
        if pull_parts_btn:
            action_buttons.append(pull_parts_btn)
        if add_part_btn:
            action_buttons.append(add_part_btn)
        
        parts_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INVENTORY_2, size=18, color=self.primary_color),
                    ft.Text(get_text("more_part"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ATTACH_MONEY, size=14, color=self.success_color),
                            ft.Text(f"{int(total_cost):,} KIP", size=14, weight=ft.FontWeight.W_700, color=self.success_color),
                        ], spacing=4),
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                        bgcolor=ft.Colors.with_opacity(0.1, self.success_color),
                        border_radius=16,
                    ),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=4),
                ft.Row([
                    ft.Text("#", size=10, weight=ft.FontWeight.W_600, color="#64748B", width=30),
                    ft.Text(get_text("part_name"), size=10, weight=ft.FontWeight.W_600, color="#64748B", expand=True),
                    ft.Text(get_text("qty"), size=10, weight=ft.FontWeight.W_600, color="#64748B", width=45, text_align=ft.TextAlign.CENTER),
                    ft.Text(get_text("cost_price"), size=10, weight=ft.FontWeight.W_600, color="#64748B", width=90, text_align=ft.TextAlign.RIGHT),
                    ft.Text(get_text("total"), size=10, weight=ft.FontWeight.W_600, color="#64748B", width=110, text_align=ft.TextAlign.RIGHT),
                    ft.Text("", size=10, width=30),
                ], spacing=6),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                parts_used_list,
                ft.Container(height=6),
                ft.Row(action_buttons, alignment=ft.MainAxisAlignment.END, spacing=10) if action_buttons else ft.Container(),
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.Margin(left=0, right=0, top=0, bottom=12),
        )
        
        right_column = ft.Container(
            content=ft.Column([quotation_card, parts_card], spacing=0),
            width=550,
            expand=True,
        )
        
        # ========== TWO COLUMN LAYOUT with Horizontal Scroll ==========
        two_columns = ft.Row(
            [left_column, ft.VerticalDivider(width=1, color=ft.Colors.GREY_300), right_column],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.AUTO,  # Enable horizontal scroll
        )
        
        main_content = ft.Container(
            content=two_columns,
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            expand=True,
        )
        
        # Action Buttons
        back_btn = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ARROW_BACK, size=18, color=self.primary_color),
                ft.Text(get_text("back_to_list"), size=14, color=self.primary_color, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=lambda e: self.navigate("repair_list"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, self.primary_color),
                padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            ),
        )
        
        export_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("export_work_order"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=6),
            on_click=self.export_repair_pdf,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            ),
        )
        
        action_row = ft.Row([back_btn, export_btn], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
        
        return ft.Column([
            main_content,
            ft.Container(height=16),
            action_row,
        ], spacing=0)

    def export_repair_pdf(self, e):
        self.show_snack_bar(get_text("loading"), "info")
        try:
            import os
            
            pdf_bytes = self.client.get_repair_order_pdf(self.repair_id)
            if not pdf_bytes:
                self.show_snack_bar(get_text("pdf_export_failed"), "error")
                return
                
            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            ro_no = f"R{self.repair_id:04d}"
            pdf_path = os.path.join(output_dir, f"repair_work_order_{ro_no}.pdf")
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
                
            os.startfile(pdf_path)
            self.show_snack_bar(get_text("pdf_export_success"), "success")
            
        except Exception as ex:
            print(f"Error exporting PDF: {ex}")
            self.show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", "error")
    
    def show_add_part_dialog(self, e):
        if not self.parts_list:
            self.show_snack_bar(get_text("no_parts_available"), "error")
            return
        
        part_options = []
        
        for part in self.parts_list:
            part_name = part.get("name", "-")
            stock_qty = part.get("stock_qty", 0)
            part_options.append(
                ft.dropdown.Option(
                    str(part.get('id')),
                    f"{part_name} [{stock_qty}]"
                )
            )
        
        part_dropdown = ft.Dropdown(
            label=get_text("select_part"),
            hint_text=get_text("select_part_hint"),
            options=[ft.dropdown.Option("", f"-- {get_text('select_part')} --")] + part_options,
            expand=True,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        )
        part_dropdown.on_change = self.on_part_select
        
        self.qty_field = ft.TextField(
            label=get_text("quantity"),
            value="1",
            width=150,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        )
        
        stock_info = ft.Text("", size=12, color="#64748B", visible=False)
        self.selected_stock = stock_info
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.INVENTORY, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(
                            get_text("withdraw_part"),
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
                    part_dropdown,
                    ft.Container(height=12),
                    stock_info,
                    ft.Container(height=8),
                    self.qty_field,
                ], spacing=0),
                padding=ft.Padding(left=24, right=24, top=24, bottom=24),
                width=450,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog), style=ft.ButtonStyle(color="#64748B")),
                ft.ElevatedButton(get_text("withdraw"), on_click=lambda e: self._confirm_add_part(part_dropdown.value, self.qty_field.value, dialog), style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def _confirm_add_part(self, part_id_str, qty_str, dialog):
        if not part_id_str or part_id_str == "":
            self.show_snack_bar(get_text("select_part_first"), "error")
            return
        
        part_id = int(part_id_str)
        qty = int(qty_str) if qty_str else 1
        
        if qty <= 0:
            self.show_snack_bar(get_text("invalid_quantity"), "error")
            return
        
        selected_part = None
        for part in self.parts_list:
            if part.get('id') == part_id:
                selected_part = part
                break
        
        if selected_part and qty > selected_part.get('stock_qty', 0):
            self.show_snack_bar(f"{get_text('insufficient_stock')} (ຄົງເຫຼືອ: {selected_part.get('stock_qty', 0)})", "error")
            return
        
        try:
            result = self.client.add_part_usage(self.repair_id, part_id, qty)
            if result:
                self._close_dialog(dialog)
                self.load_repair_data()
                self.load_parts()
                self._refresh_content()
                self.show_snack_bar(f"{get_text('part_withdrawn')}", "success")
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", "error")
    
    def on_part_select(self, e):
        if e.control.value and e.control.value != "":
            part_id = int(e.control.value)
            for part in self.parts_list:
                if part.get('id') == part_id:
                    stock = part.get('stock_qty', 0)
                    if self.selected_stock:
                        if stock <= 0:
                            self.selected_stock.value = f"⚠️ {get_text('out_of_stock')}"
                            self.selected_stock.color = "#EF4444"
                        elif stock <= 5:
                            self.selected_stock.value = f"⚠️ {get_text('low_stock')}: {stock}"
                            self.selected_stock.color = "#F59E0B"
                        else:
                            self.selected_stock.value = f"{get_text('available_stock')}: {stock}"
                            self.selected_stock.color = "#10B981"
                        self.selected_stock.visible = True
                        self.page.update()
                    break
    
    def return_part(self, usage_id):
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.warning_color,
                            border_radius=12,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(
                            get_text("confirm_return"),
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
                content=ft.Text(get_text("return_part_warning"), size=14, color="#64748B"),
                padding=ft.Padding(left=24, right=24, top=24, bottom=24),
                width=380,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog), style=ft.ButtonStyle(color="#64748B")),
                ft.ElevatedButton(get_text("return"), on_click=lambda e: self._confirm_return_part(usage_id, dialog), style=ft.ButtonStyle(bgcolor=self.warning_color, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def _confirm_return_part(self, usage_id, dialog):
        try:
            result = self.client.delete_part_usage(self.repair_id, usage_id)
            if result:
                self._close_dialog(dialog)
                self.load_repair_data()
                self.load_parts()
                self._refresh_content()
                self.show_snack_bar(f"{get_text('part_returned')}", "success")
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", "error")
    
    def _build_duration_display(self, start_date_str: str, end_date_str: str, status: str) -> ft.Control:
        """Build a colored duration indicator for the detail info card."""
        try:
            if not start_date_str:
                return ft.Text("-", size=13, color="#94A3B8")

            start_d = datetime.strptime(str(start_date_str)[:10], "%Y-%m-%d").date()

            if status == "completed" and end_date_str:
                end_d = datetime.strptime(str(end_date_str)[:10], "%Y-%m-%d").date()
                days = (end_d - start_d).days
                return ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color="#4CAF50"),
                    ft.Text(
                        get_text("duration_completed").format(days),
                        size=13, color="#4CAF50", weight=ft.FontWeight.W_600,
                    ),
                ], spacing=4)

            days = (date.today() - start_d).days
            if days < 3:
                color, icon = "#10B981", ft.Icons.TIMER
            elif days < 7:
                color, icon = "#F59E0B", ft.Icons.TIMER
            else:
                color, icon = "#EF4444", ft.Icons.TIMER_OFF

            return ft.Row([
                ft.Icon(icon, size=14, color=color),
                ft.Text(
                    get_text("days_running").format(days),
                    size=13, color=color, weight=ft.FontWeight.W_600,
                ),
            ], spacing=4)
        except Exception:
            return ft.Text("-", size=13, color="#94A3B8")

    def _quotation_requires_parts(self) -> bool:
        if self.repair_data and int(self.repair_data.get("quotation_parts_count") or 0) > 0:
            return True
        items = self.repair_data.get("quotation_items", []) if self.repair_data else []
        return any(item.get("item_type") == "part" for item in items)

    def _has_parts_usage(self) -> bool:
        usage = self.repair_data.get("parts_usage", []) if self.repair_data else []
        return len(usage) > 0

    def show_update_status_dialog(self, e):
        current_status = self.repair_data.get("status", "working")

        if current_status == "completed":
            self.show_snack_bar(get_text("cannot_update_completed_status"), "error")
            return

        steps = [
            ("working",   get_text("working"),   "#2196F3", ft.Icons.BUILD),
            ("completed", get_text("completed"), "#4CAF50", ft.Icons.CHECK_CIRCLE),
        ]

        # Mutable state via dict — Flet 0.84 compatible (no ft.Ref generics)
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
                    ft.Colors.with_opacity(0.12, color) if is_selected
                    else ft.Colors.WHITE
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
                self._close_dialog(dialog)
                return

            if new_status == "completed":
                if self._quotation_requires_parts() and not self._has_parts_usage():
                    self.show_snack_bar(get_text("must_withdraw_parts_before_complete"), "error")
                    return
                confirm_dialog = ft.AlertDialog(
                    modal=True,
                    shape=ft.RoundedRectangleBorder(radius=16),
                    bgcolor=ft.Colors.WHITE,
                    title=ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.WARNING, size=22, color=ft.Colors.WHITE),
                                bgcolor="#F59E0B", border_radius=10, padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                            ),
                            ft.Text(get_text("confirm_complete_repair"), size=18,
                                    weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ], spacing=10),
                        padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                        border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                    ),
                    content=ft.Container(
                        content=ft.Text(get_text("confirm_complete_repair_msg"), size=14, color="#64748B"),
                        padding=ft.Padding(left=20, right=20, top=20, bottom=20), width=360,
                    ),
                    actions=[
                        ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(confirm_dialog),
                                      style=ft.ButtonStyle(color="#64748B")),
                        ft.ElevatedButton(get_text("confirm"),
                            on_click=lambda e: self._do_update_status(new_status, dialog, confirm_dialog),
                            style=ft.ButtonStyle(bgcolor="#4CAF50", color=ft.Colors.WHITE,
                                                 shape=ft.RoundedRectangleBorder(radius=8))),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                self._open_dialog(confirm_dialog)
            else:
                self._do_update_status(new_status, dialog)

        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=22, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color, border_radius=10, padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(get_text("update_repair_status"), size=18,
                                weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(get_text("select_new_status"), size=13, color="#64748B"),
                    ft.Container(height=10),
                    step_row,
                ], spacing=0),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20), width=420,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog),
                              style=ft.ButtonStyle(color="#64748B")),
                ft.ElevatedButton(get_text("update"), on_click=confirm_update,
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE,
                                         shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._open_dialog(dialog)

    def _do_update_status(self, new_status: str, *dialogs):
        try:
            self.client.update_repair_status(self.repair_id, new_status)
            for d in dialogs:
                if d:
                    d.open = False
            self.current_dialog = None
            self.page.update()
            self.load_repair_data()
            self.load_parts()
            self._refresh_content()
            self.show_snack_bar(
                f"{get_text('status_updated_to')} {get_text(new_status)}",
                "success",
            )
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", "error")
    
    def _open_dialog(self, dialog):
        try:
            self.current_dialog = dialog
            self.page.show_dialog(dialog)
        except Exception as e:
            print(f"DEBUG: Error opening dialog: {e}")
    
    def _close_dialog(self, dialog):
        try:
            self.page.pop_dialog()
            if self.current_dialog is dialog:
                self.current_dialog = None
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
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

    def confirm_pull_quotation_parts(self, e):
        confirm_dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.DOWNLOAD, size=22, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.GREEN_600, border_radius=10, padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(get_text("confirm_pull_parts"), size=18,
                                weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Text(get_text("confirm_pull_parts_msg"), size=13, color="#64748B"),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20), width=420,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(confirm_dialog),
                              style=ft.ButtonStyle(color="#64748B")),
                ft.ElevatedButton(get_text("confirm"),
                    on_click=lambda e: self.page.run_task(self._pull_quotation_parts_async, confirm_dialog),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE,
                                         shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(confirm_dialog)

    async def _pull_quotation_parts_async(self, dialog):
        self._close_dialog(dialog)
        try:
            result = await asyncio.to_thread(self.client.pull_quotation_parts, self.repair_id)
            if result:
                await asyncio.to_thread(self.load_repair_data)
                await asyncio.to_thread(self.load_parts)
                self._refresh_content()
                self.show_snack_bar(f"{get_text('pull_parts_success')}", "success")
        except Exception as ex:
            error_msg = str(ex)
            lower = error_msg.lower()
            if "already been pulled" in lower or "no parts are listed" in lower:
                self.show_snack_bar(get_text("no_new_parts_to_pull"), "error")
            elif "insufficient stock" in lower:
                self.show_snack_bar(error_msg, "error")
            else:
                self.show_snack_bar(f"Error: {error_msg}", "error")