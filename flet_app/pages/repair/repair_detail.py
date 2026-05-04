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
    
    def build(self):
        self.load_repair_data()
        
        header = self._build_header()
        
        if not self.repair_data:
            loading = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=50, height=50),
                    ft.Container(height=20),
                    ft.Text(get_text("loading"), size=16, color="#64748B"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=Alignment.CENTER,
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
            padding=ft.padding.all(32),
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
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("repair_detail_subtitle"),
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Icon(ft.Icons.CONSTRUCTION, size=28, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                        border_radius=15,
                        padding=ft.padding.all(8),
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=20, horizontal=32),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            ),
        )
    
    def load_repair_data(self):
        try:
            if self.repair_id:
                self.repair_data = self.client.get_repair_order(self.repair_id)
                self.page.update()
        except Exception as ex:
            print(f"Error loading repair detail: {ex}")
    
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
        
        # Parts Used Card
        parts_list = ft.Column(spacing=8)
        total_cost = 0
        
        if parts_usage:
            for part in parts_usage:
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
                    alignment=Alignment.CENTER,
                )
            )
        
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
                    dialog.open = False
                    self.page.update()
                    self.load_repair_data()
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
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("update"), on_click=update_status, style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()