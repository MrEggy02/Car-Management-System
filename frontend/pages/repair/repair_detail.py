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
        self.content_area = None  # Store reference to content area
        
    def build(self):
        header = self._build_header()
        
        # Create content area with loading state
        self.content_area = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Container(height=20),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.padding.all(24),
            bgcolor="#F0F2F5",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Load data after build
        self.page.run_task(self._load_data)
        
        return main_content
    
    async def _load_data(self):
        """Load all data asynchronously"""
        await asyncio.sleep(0.1)
        self.load_repair_data()
        self.load_parts()
        self._refresh_content()
    
    def _refresh_content(self):
        """Refresh the content area"""
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
        # Action Buttons in Header
        update_status_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("update_status"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
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
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("repair_detail_subtitle"),
                                size=12,
                                color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
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
            padding=ft.padding.symmetric(vertical=14, horizontal=24),
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
        except Exception as ex:
            print(f"Error loading repair detail: {ex}")
    
    def load_parts(self):
        try:
            self.parts_list = self.client.get_parts()
        except Exception as ex:
            print(f"Error loading parts: {ex}")
            self.parts_list = []
    
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
        
        if start_date:
            start_date = start_date[:16] if len(start_date) > 16 else start_date
        else:
            start_date = "-"
        if end_date:
            end_date = end_date[:16] if len(end_date) > 16 else end_date
        else:
            end_date = "-"
        
        # Status Badge
        status_badge = ft.Container(
            content=ft.Text(status_texts.get(status, status), size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            bgcolor=status_colors.get(status, "#607D8B"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=16, vertical=6),
        )
        
        # ========== REPAIR INFO CARD ==========
        repair_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.CONSTRUCTION, size=20, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("repair_info"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("repair_no"), size=11, color="#64748B"),
                            ft.Text(repair_no, size=15, weight=ft.FontWeight.W_700, color=self.primary_color),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("status"), size=11, color="#64748B"),
                            status_badge,
                        ], spacing=4, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([
                            ft.Text(get_text("mechanic"), size=11, color="#64748B"),
                            ft.Text(mechanic_name, size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ], spacing=4, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("start_date"), size=11, color="#64748B"),
                            ft.Text(start_date, size=13, color="#1E293B"),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("end_date"), size=11, color="#64748B"),
                            ft.Text(end_date, size=13, color="#1E293B"),
                        ], spacing=4, expand=True),
                    ]),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
        
        # ========== JOB ORDER INFO CARD ==========
        job_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("job_order_info"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("job_number"), size=11, color="#64748B"),
                            ft.Text(job_no, size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("customer_name"), size=11, color="#64748B"),
                            ft.Text(customer_name, size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("customer_phone"), size=11, color="#64748B"),
                            ft.Text(customer_phone, size=13, color="#1E293B"),
                        ], spacing=4, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("plate_number"), size=11, color="#64748B"),
                            ft.Text(plate_number, size=14, weight=ft.FontWeight.W_700, color=self.primary_color),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("car_brand_model"), size=11, color="#64748B"),
                            ft.Text(f"{brand} {model} {f'({year})' if year else ''}", size=13, color="#1E293B"),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("car_color"), size=11, color="#64748B"),
                            ft.Text(color, size=13, color="#1E293B"),
                        ], spacing=4, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Text(get_text("problem_description"), size=11, color="#64748B"),
                    ft.Container(
                        content=ft.Text(problem, size=13, color="#1E293B"),
                        padding=ft.padding.all(12),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=8,
                        margin=ft.margin.only(top=4),
                    ),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
        
        # ========== PARTS USED CARD ==========
        parts_list = ft.Column(spacing=6)
        total_cost = 0
        
        if parts_usage and len(parts_usage) > 0:
            for idx, part in enumerate(parts_usage):
                usage_id = part.get("id")
                part_name = part.get("part_name", "-")
                qty = part.get("qty", 0)
                cost_price = part.get("cost_price", 0)
                total = qty * cost_price
                total_cost += total
                
                bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
                
                item = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(f"{qty}", size=14, weight=ft.FontWeight.W_700, color=self.primary_color),
                            width=50,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column([
                            ft.Text(part_name, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                            ft.Text(f"{int(cost_price):,} KIP", size=11, color="#64748B"),
                        ], spacing=2, expand=True),
                        ft.Text(f"{int(total):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.success_color, width=120, text_align=ft.TextAlign.RIGHT),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=18,
                            icon_color=ft.Colors.RED_400,
                            tooltip=get_text("return_part"),
                            on_click=lambda e, uid=usage_id: self.return_part(uid),
                            padding=0,
                        ),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=10, horizontal=12),
                    bgcolor=bg_color,
                    border_radius=8,
                )
                parts_list.controls.append(item)
        else:
            parts_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INVENTORY, size=40, color="#CBD5E1"),
                        ft.Text(get_text("no_parts_used"), size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.padding.all(30),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        # Add Part Button (only show if status is not completed)
        add_part_btn = None
        if status != "completed":
            add_part_btn = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                    ft.Text(get_text("add_part"), size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                ], spacing=6),
                on_click=self.show_add_part_dialog,
                style=ft.ButtonStyle(
                    bgcolor=self.primary_color,
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                ),
            )
        
        parts_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.INVENTORY_2, size=20, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("parts_used"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(get_text("total_parts_cost") + ":", size=12, color="#64748B"),
                                    ft.Text(f"{int(total_cost):,} KIP", size=15, weight=ft.FontWeight.BOLD, color=self.success_color),
                                ], spacing=6),
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                bgcolor=ft.Colors.GREY_50,
                                border_radius=16,
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=8),
                    parts_list,
                    ft.Container(height=8),
                    ft.Row([add_part_btn], alignment=ft.MainAxisAlignment.END) if add_part_btn else ft.Container(),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
        
        # ========== ACTION BUTTONS ==========
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
            repair_info_card,
            job_info_card,
            parts_card,
            ft.Container(height=20),
            action_row,
        ], spacing=0)
    
    def show_add_part_dialog(self, e):
        """Show dialog to add part to repair"""
        if not self.parts_list:
            self.show_snack_bar(get_text("no_parts_available"), is_error=True)
            return
        
        part_options = []
        
        for part in self.parts_list:
            part_name = part.get("name", "-")
            stock_qty = part.get("stock_qty", 0)
            status_text = "✓" if stock_qty > 5 else "⚠️" if stock_qty > 0 else "❌"
            part_options.append(
                ft.dropdown.Option(
                    str(part.get('id')),
                    f"{part_name} [{stock_qty}] {status_text}"
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
        """Confirm add part"""
        if not part_id_str or part_id_str == "":
            self.show_snack_bar(get_text("select_part_first"), is_error=True)
            return
        
        part_id = int(part_id_str)
        qty = int(qty_str) if qty_str else 1
        
        if qty <= 0:
            self.show_snack_bar(get_text("invalid_quantity"), is_error=True)
            return
        
        # Find selected part to check stock
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
                # Reload data
                self.load_repair_data()
                self.load_parts()
                # Refresh UI
                self._refresh_content()
                self.show_snack_bar(f"✅ {get_text('part_withdrawn')}", is_error=False)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def on_part_select(self, e):
        """When part is selected, show stock info"""
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
        """Return part to stock"""
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
        """Confirm return part"""
        try:
            result = self.client.delete_part_usage(self.repair_id, usage_id)
            if result:
                dialog.open = False
                self.current_dialog = None
                # Reload data
                self.load_repair_data()
                self.load_parts()
                # Refresh UI
                self._refresh_content()
                self.show_snack_bar(f"✅ {get_text('part_returned')}", is_error=False)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def show_update_status_dialog(self, e):
        """Show dialog to update repair status"""
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
        """Confirm update status"""
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