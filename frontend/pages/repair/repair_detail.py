# pages/repair/repair_detail.py
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
        self.parts_list = []
        self.selected_part_id = None
        self.qty_field = None
        self.selected_stock = None
        
    def build(self):
        header = self._build_header()
        
        # Load data first
        self.load_repair_data()
        self.load_parts()
        
        if not self.repair_data:
            loading = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=50, height=50),
                    ft.Container(height=20),
                    ft.Text(get_text("loading"), size=16, color="#64748B"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
            return ft.Container(
                content=ft.Column([header, loading]),
                expand=True,
                bgcolor="#F5F7FA",
            )
        
        content = self._build_content()
        
        scrollable_content = ft.Column(
            [content],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.padding.all(24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=24,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("repair_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
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
                    
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=14, horizontal=26),
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
                self.page.update()
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
            content=ft.Text(status_texts.get(status, status), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=status_colors.get(status, "#607D8B"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
        )
        
        # Repair Info Card
        repair_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.INFO, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
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
                            ft.Text(get_text("repair_no"), size=12, color="#64748B"),
                            ft.Text(repair_no, size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("status"), size=12, color="#64748B"),
                            status_badge,
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("mechanic"), size=12, color="#64748B"),
                            ft.Text(mechanic_name, size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("start_date"), size=12, color="#64748B"),
                            ft.Text(start_date, size=14),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("end_date"), size=12, color="#64748B"),
                            ft.Text(end_date, size=14),
                        ], spacing=2, expand=True),
                    ]),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Job Order Info Card
        job_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
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
                            ft.Text(get_text("job_number"), size=12, color="#64748B"),
                            ft.Text(job_no, size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("customer_name"), size=12, color="#64748B"),
                            ft.Text(customer_name, size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("customer_phone"), size=12, color="#64748B"),
                            ft.Text(customer_phone, size=14),
                        ], spacing=2, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("plate_number"), size=12, color="#64748B"),
                            ft.Text(plate_number, size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("car_brand"), size=12, color="#64748B"),
                            ft.Text(f"{brand} {model} {f'({year})' if year else ''}", size=14),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("car_color"), size=12, color="#64748B"),
                            ft.Text(color, size=14),
                        ], spacing=2, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Text(get_text("problem_description"), size=12, color="#64748B"),
                    ft.Text(problem, size=13, color="#1E293B"),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Parts Used Card (With Add Part Button)
        parts_list = ft.Column(spacing=8)
        total_cost = 0
        
        if parts_usage:
            for part in parts_usage:
                usage_id = part.get("id")
                part_name = part.get("part_name", "-")
                qty = part.get("qty", 0)
                cost_price = part.get("cost_price", 0)
                total = qty * cost_price
                total_cost += total
                
                item = ft.Container(
                    content=ft.Row([
                        ft.Text(f"{qty}x", size=13, weight=ft.FontWeight.W_500, color=self.primary_color, width=40),
                        ft.Text(part_name, size=13, expand=True),
                        ft.Text(f"{int(cost_price):,} KIP", size=12, color="#64748B"),
                        ft.Text(f"{int(total):,} KIP", size=13, weight=ft.FontWeight.BOLD, color="#1E293B", width=120),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            tooltip=get_text("return_part"),
                            on_click=lambda e, uid=usage_id: self.return_part(uid),
                        ),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=6, horizontal=10),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=6,
                )
                parts_list.controls.append(item)
        else:
            parts_list.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_parts_used"), size=13, color="#64748B"),
                    padding=ft.padding.all(20),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        # Add Part Button (only show if status is not completed)
        add_part_btn = None
        if status != "completed":
            add_part_btn = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                    ft.Text(get_text("add_part"), size=14, color=ft.Colors.WHITE),
                ], spacing=6),
                on_click=self.show_add_part_dialog,
                style=ft.ButtonStyle(
                    bgcolor=self.primary_color,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            )
        else:
            add_part_btn = ft.Container()
        
        parts_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.INVENTORY, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("parts_used"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                            ft.Text(f"{get_text('total_parts_cost')}: {int(total_cost):,} KIP", size=14, weight=ft.FontWeight.BOLD, color=self.primary_color),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=8),
                    parts_list,
                    ft.Container(height=8),
                    ft.Row([add_part_btn], alignment=ft.MainAxisAlignment.END),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Action Buttons
        update_status_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("update_status"), size=14, color=ft.Colors.WHITE),
            ], spacing=6),
            on_click=self.show_update_status_dialog,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )
        
        back_btn = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ARROW_BACK, size=18, color=self.primary_color),
                ft.Text(get_text("back_to_list"), size=14, color=self.primary_color),
            ], spacing=6),
            on_click=lambda e: self.navigate("repair_list"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, self.primary_color),
            ),
        )
        
        action_row = ft.Row([back_btn, update_status_btn], spacing=12, alignment=ft.MainAxisAlignment.END)
        
        return ft.Column([
            repair_info_card,
            job_info_card,
            parts_card,
            action_row,
        ], spacing=20)
    
    def show_add_part_dialog(self, e):
        """Show dialog to add part to repair"""
        # Create part dropdown with stock info
        part_options = []
        part_options.append(ft.dropdown.Option("", get_text("select_part")))
        
        for part in self.parts_list:
            part_name = part.get("name", "-")
            part_code = part.get("part_code", "")
            stock_qty = part.get("stock_qty", 0)
            part_options.append(
                ft.dropdown.Option(
                    str(part.get('id')),
                    f"{part_code} - {part_name} (ຄົງເຫຼືອ: {stock_qty})"
                )
            )
        
        part_dropdown = ft.Dropdown(
            label=get_text("select_part"),
            hint_text=get_text("select_part_hint"),
            options=part_options,
            width=300,
            border_radius=12,
        )
        
        # Add on_change after creation (Flet 0.84.0 compatibility)
        part_dropdown.on_change = self.on_part_select
        
        self.qty_field = ft.TextField(
            label=get_text("quantity"),
            value="1",
            width=150,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=12,
        )
        
        self.selected_stock = ft.Text("", size=12, color="#64748B", visible=False)
        
        def confirm_add_part(e):
            if not part_dropdown.value or part_dropdown.value == "":
                self.show_snack_bar(get_text("select_part_first"), is_error=True)
                return
            
            part_id = int(part_dropdown.value)
            qty = int(self.qty_field.value) if self.qty_field.value else 1
            
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
                    # Reload data
                    self.load_repair_data()
                    self.load_parts()
                    # Refresh content
                    new_content = self._build_content()
                    parent = self.page.controls[0]
                    if parent:
                        content_area = parent.content.controls[1]
                        content_area.content = ft.Column([new_content], scroll=ft.ScrollMode.AUTO, expand=True)
                        content_area.update()
                    self.show_snack_bar(f"✅ {get_text('part_withdrawn')}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
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
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    part_dropdown,
                    ft.Container(height=12),
                    self.qty_field,
                ]),
                padding=ft.padding.all(24),
                width=400,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton(get_text("withdraw"), on_click=confirm_add_part, style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def on_part_select(self, e):
        """When part is selected, show stock info"""
        if e.control.value and e.control.value != "":
            part_id = int(e.control.value)
            for part in self.parts_list:
                if part.get('id') == part_id:
                    stock = part.get('stock_qty', 0)
                    # Update the stock text in dialog if exists
                    if hasattr(self, 'selected_stock') and self.selected_stock:
                        self.selected_stock.value = f"{get_text('available_stock')}: {stock}"
                        self.selected_stock.visible = True
                        self.page.update()
                    break
    
    def return_part(self, usage_id):
        """Return part to stock"""
        def confirm_return(e):
            try:
                result = self.client.delete_part_usage(self.repair_id, usage_id)
                if result:
                    dialog.open = False
                    # Reload data
                    self.load_repair_data()
                    self.load_parts()
                    # Refresh content
                    new_content = self._build_content()
                    parent = self.page.controls[0]
                    if parent:
                        content_area = parent.content.controls[1]
                        content_area.content = ft.Column([new_content], scroll=ft.ScrollMode.AUTO, expand=True)
                        content_area.update()
                    self.show_snack_bar(f"✅ {get_text('part_returned')}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, size=24, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.ORANGE_600,
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            get_text("confirm_return"),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Text(get_text("return_part_warning"), size=14, color="#64748B"),
                padding=ft.padding.all(24),
                width=350,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton(get_text("return"), on_click=confirm_return, style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_600, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
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
            width=250,
            border_radius=12,
        )
        
        def update_status(e):
            new_status = status_dropdown.value
            if new_status and new_status != current_status:
                try:
                    self.client.update_repair_status(self.repair_id, new_status)
                    self._close_dialog(dialog)
                    self.load_repair_data()
                    # Refresh content
                    new_content = self._build_content()
                    parent = self.page.controls[0]
                    if parent:
                        content_area = parent.content.controls[1]
                        content_area.content = ft.Column([new_content], scroll=ft.ScrollMode.AUTO, expand=True)
                        content_area.update()
                    self.show_snack_bar(f"✅ {get_text('status_updated_to')} {get_text(new_status)}", is_error=False)
                except Exception as ex:
                    self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
            else:
                dialog.open = False
                self.page.update()
        
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
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"{get_text('current_status')}: {get_text(current_status)}", size=14, color="#64748B"),
                    ft.Container(height=16),
                    status_dropdown,
                ]),
                padding=ft.padding.all(24),
                width=350,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton(get_text("update"), on_click=update_status, style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()