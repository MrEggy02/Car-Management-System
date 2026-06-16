# pages/repair/repair_detail.py
import asyncio

import flet as ft
from flet import Alignment
from typing import Dict, Callable

from i18n import get_text


class RepairDetailContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, repair_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.repair_id = repair_id
        self.repair_data = None
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.warning_color = "#F59E0B"
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
            padding=ft.padding.all(24),
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
        self.load_repair_data()
        self.load_parts()
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
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
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
            padding=ft.padding.symmetric(vertical=12, horizontal=24),
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
            padding=ft.padding.symmetric(vertical=5),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_50)),
        )
    
    def _build_content(self):
        data = self.repair_data
        
        status_colors = {
            "waiting": "#FF9800",
            "working": "#2196F3",
            "paused": "#9C27B0",
            "completed": "#4CAF50"
        }
        status_texts = {
            "waiting": get_text("waiting"),
            "working": get_text("working"),
            "paused": get_text("paused"),
            "completed": get_text("completed")
        }
        
        repair_no = f"R{data.get('id', 0):04d}"
        status = data.get("status", "waiting")
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
            padding=ft.padding.symmetric(horizontal=14, vertical=5),
        )
        
        # ========== LEFT COLUMN ==========
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
            ], spacing=0),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.margin.only(bottom=12),
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
                    padding=ft.padding.all(10),
                    bgcolor="#F8FAFC",
                    border_radius=8,
                    margin=ft.margin.only(top=4),
                ),
            ], spacing=0),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.margin.only(bottom=12),
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
                
                border_bottom = ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_50)) if idx < len(quotation_items) - 1 else None
                
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Text(f"{idx+1}", size=12, color="#64748B", width=30),
                        ft.Text(name, size=12, color="#1E293B", expand=True, max_lines=2),
                        ft.Text(f"x{qty}", size=12, color="#64748B", width=45, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{int(unit_price):,}", size=12, color="#64748B", width=90, text_align=ft.TextAlign.RIGHT),
                        ft.Text(f"{int(total):,}", size=12, weight=ft.FontWeight.W_600, color=self.success_color, width=110, text_align=ft.TextAlign.RIGHT),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=6, horizontal=0),
                    border=border_bottom,
                )
                quotation_items_list.controls.append(item_row)
            
            total_row = ft.Container(
                content=ft.Row([
                    ft.Container(expand=True),
                    ft.Text(get_text("total") + ":", size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Text(f"{int(quotation_total):,} KIP", size=14, weight=ft.FontWeight.W_700, color=self.success_color),
                ], spacing=12),
                padding=ft.padding.symmetric(vertical=8, horizontal=0),
                bgcolor="#F8FAFC",
                border_radius=8,
                margin=ft.margin.only(top=6),
            )
            quotation_items_list.controls.append(total_row)
        else:
            quotation_items_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.REQUEST_QUOTE, size=32, color="#CBD5E1"),
                        ft.Text(get_text("no_quotation_items"), size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.padding.all(30),
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
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
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
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.margin.only(bottom=12),
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
                
                border_bottom = ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_50)) if idx < len(parts_usage) - 1 else None
                
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
                        ),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=6, horizontal=0),
                    border=border_bottom,
                )
                parts_used_list.controls.append(item_row)
            
            total_row = ft.Container(
                content=ft.Row([
                    ft.Container(expand=True),
                    ft.Text(get_text("total_parts_cost") + ":", size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Text(f"{int(total_cost):,} KIP", size=14, weight=ft.FontWeight.W_700, color=self.success_color),
                ], spacing=12),
                padding=ft.padding.symmetric(vertical=8, horizontal=0),
                bgcolor="#F8FAFC",
                border_radius=8,
                margin=ft.margin.only(top=6),
            )
            parts_used_list.controls.append(total_row)
        else:
            parts_used_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INVENTORY, size=32, color="#CBD5E1"),
                        ft.Text(get_text("no_parts_used"), size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.padding.all(30),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        add_part_btn = None
        if status != "completed":
            add_part_btn = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("add_part"), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                ], spacing=6),
                on_click=self.show_add_part_dialog,
                style=ft.ButtonStyle(
                    bgcolor=self.primary_color,
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                ),
            )
        
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
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
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
                ft.Row([add_part_btn], alignment=ft.MainAxisAlignment.END) if add_part_btn else ft.Container(),
            ], spacing=0),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.margin.only(bottom=12),
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
            padding=ft.padding.all(20),
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
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
            ),
        )
        
        action_row = ft.Row([back_btn], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
        
        return ft.Column([
            main_content,
            ft.Container(height=16),
            action_row,
        ], spacing=0)
    
    def show_add_part_dialog(self, e):
        if not self.parts_list:
            self.show_snack_bar(get_text("no_parts_available"), is_error=True)
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
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
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
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
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
                            padding=ft.padding.all(8),
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
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    part_dropdown,
                    ft.Container(height=12),
                    stock_info,
                    ft.Container(height=8),
                    self.qty_field,
                ], spacing=0),
                padding=ft.padding.all(24),
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
            self.show_snack_bar(get_text("select_part_first"), is_error=True)
            return
        
        part_id = int(part_id_str)
        qty = int(qty_str) if qty_str else 1
        
        if qty <= 0:
            self.show_snack_bar(get_text("invalid_quantity"), is_error=True)
            return
        
        selected_part = None
        for part in self.parts_list:
            if part.get('id') == part_id:
                selected_part = part
                break
        
        if selected_part and qty > selected_part.get('stock_qty', 0):
            self.show_snack_bar(f"{get_text('insufficient_stock')} (ຄົງເຫຼືອ: {selected_part.get('stock_qty', 0)})", is_error=True)
            return
        
        try:
            result = self.client.add_part_usage(self.repair_id, part_id, qty)
            if result:
                dialog.open = False
                self.current_dialog = None
                self.load_repair_data()
                self.load_parts()
                self._refresh_content()
                self.show_snack_bar(f"✅ {get_text('part_withdrawn')}", is_error=False)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
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
                            self.selected_stock.value = f"✅ {get_text('available_stock')}: {stock}"
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
                            padding=ft.padding.all(8),
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
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Text(get_text("return_part_warning"), size=14, color="#64748B"),
                padding=ft.padding.all(24),
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
                dialog.open = False
                self.current_dialog = None
                self.load_repair_data()
                self.load_parts()
                self._refresh_content()
                self.show_snack_bar(f"✅ {get_text('part_returned')}", is_error=False)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def show_update_status_dialog(self, e):
        current_status = self.repair_data.get("status", "waiting")
        
        status_dropdown = ft.Dropdown(
            label=get_text("select_status"),
            value=current_status,
            options=[
                ft.dropdown.Option("waiting", get_text("waiting")),
                ft.dropdown.Option("working", get_text("working")),
                ft.dropdown.Option("paused", get_text("paused")),
                ft.dropdown.Option("completed", get_text("completed")),
            ],
            expand=True,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            get_text("update_repair_status"),
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Text(get_text("current_status") + ":", size=13, color="#64748B"),
                            ft.Container(
                                content=ft.Text(get_text(current_status), size=13, weight=ft.FontWeight.W_600),
                                bgcolor=ft.Colors.GREY_100,
                                border_radius=8,
                                padding=ft.padding.symmetric(horizontal=12, vertical=4),
                            ),
                        ], spacing=8),
                        padding=ft.padding.only(bottom=12),
                    ),
                    status_dropdown,
                ]),
                padding=ft.padding.all(24),
                width=400,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog), style=ft.ButtonStyle(color="#64748B")),
                ft.ElevatedButton(get_text("update"), on_click=lambda e: self._confirm_update_status(status_dropdown.value, dialog), style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def _confirm_update_status(self, new_status, dialog):
        current_status = self.repair_data.get("status", "waiting")
        if new_status and new_status != current_status:
            try:
                self.client.update_repair_status(self.repair_id, new_status)
                dialog.open = False
                self.current_dialog = None
                self.load_repair_data()
                self._refresh_content()
                self.show_snack_bar(f"✅ {get_text('status_updated_to')} {get_text(new_status)}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        else:
            dialog.open = False
            self.page.update()
    
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
    
    def _close_dialog(self, dialog):
        try:
            dialog.open = False
            self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, size=13),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=3000,
        )
        self.page.update()