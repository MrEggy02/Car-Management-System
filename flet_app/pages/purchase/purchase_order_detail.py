# pages/purchase/purchase_order_detail.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable

from i18n import get_text


class PurchaseOrderDetailContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, po_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.po_id = po_id
        self.po_data = None
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
    def build(self):
        header = self._build_header()
        
        if not self.po_id:
            error_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.WARNING_AMBER, size=64, color=ft.Colors.ORANGE_600),
                    ft.Text("ບໍ່ພົບໃບສັ່ງຊື້", size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.ElevatedButton(
                        get_text("back"),
                        on_click=lambda e: self.navigate("purchase_order_list"),
                        style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
            return ft.Container(
                content=ft.Column([header, error_container]),
                expand=True,
                bgcolor="#F5F7FA",
            )
        
        self.load_purchase_order()
        
        if not self.po_data:
            loading = ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=50, height=50),
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
                        on_click=lambda e: self.navigate("purchase_order_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("purchase_order_detail"),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("purchase_order_detail_subtitle"),
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                  
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
           
        )
    
    def load_purchase_order(self):
        try:
            self.po_data = self.client.get_purchase_order(self.po_id)
            print(f"DEBUG: PO detail loaded: {self.po_data}")
            self.page.update()
        except Exception as ex:
            print(f"Error loading purchase order detail: {ex}")
            import traceback
            traceback.print_exc()
    
    def _build_content(self):
        data = self.po_data
        po_no = data.get('po_no', '-')
        supplier_name = data.get('supplier_name', '-')
        order_date = data.get('order_date', '')
        if order_date:
            order_date = order_date[:16] if len(order_date) > 16 else order_date
        else:
            order_date = '-'
        status = data.get('status', 'pending')
        created_by = data.get('created_by_name', '-')
        received_by = data.get('received_by_name', '-')
        received_at = data.get('received_at', '')
        if received_at:
            received_at = received_at[:16] if len(received_at) > 16 else received_at
        else:
            received_at = '-'
        total_amount = data.get('total_amount', 0)
        items = data.get('items', [])
        
        status_colors = {
            "pending": "#FF9800",
            "ordered": "#2196F3",
            "received": "#4CAF50",
            "cancelled": "#F44336"
        }
        status_texts = {
            "pending": get_text("pending"),
            "ordered": get_text("ordered"),
            "received": get_text("received"),
            "cancelled": get_text("cancelled")
        }
        
        status_badge = ft.Container(
            content=ft.Text(status_texts.get(status, status), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=status_colors.get(status, "#607D8B"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
        )
        
        # PO Info Card
        po_info_card = ft.Card(
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
                            ft.Text(get_text("po_info"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("po_no"), size=12, color="#64748B"),
                            ft.Text(po_no, size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("status"), size=12, color="#64748B"),
                            status_badge,
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("supplier"), size=12, color="#64748B"),
                            ft.Text(supplier_name, size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("order_date"), size=12, color="#64748B"),
                            ft.Text(order_date, size=14),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("created_by"), size=12, color="#64748B"),
                            ft.Text(created_by, size=14),
                        ], spacing=2, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("received_by"), size=12, color="#64748B"),
                            ft.Text(received_by if received_by != '-' else '-', size=14),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("received_date"), size=12, color="#64748B"),
                            ft.Text(received_at, size=14),
                        ], spacing=2, expand=True),
                    ]),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Items List Card
        items_list = ft.Column(spacing=8)
        
        for item in items:
            part_name = item.get('part_name', '-')
            qty = item.get('qty', 0)
            unit_cost = item.get('unit_cost', 0)
            total_line = item.get('total_line', 0)
            received_qty = item.get('received_qty', 0)
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Text(part_name, size=13, expand=True),
                    ft.Text(f"{qty}", size=12, color="#64748B", width=60),
                    ft.Text(f"{int(unit_cost):,}", size=12, color="#64748B", width=120),
                    ft.Text(f"{int(total_line):,} KIP", size=13, weight=ft.FontWeight.W_500, color="#1E293B", width=130),
                    ft.Container(
                        content=ft.Container(
                            content=ft.Text(f"{received_qty}/{qty}", size=11, color=ft.Colors.GREEN_600 if received_qty == qty else ft.Colors.ORANGE_600),
                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN_600 if received_qty == qty else ft.Colors.ORANGE_600),
                            border_radius=10,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        ),
                        width=80,
                        alignment=ft.Alignment(0, 0),
                    ),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                bgcolor=ft.Colors.GREY_50,
                border_radius=8,
            )
            items_list.controls.append(item_row)
        
        items_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.LIST, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("items"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                            ft.Text(f"{get_text('total_amount')}: {int(total_amount):,} KIP", size=14, weight=ft.FontWeight.BOLD, color=self.primary_color),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Text(get_text("part_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                        ft.Text(get_text("qty"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=60),
                        ft.Text(get_text("unit_cost"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=120),
                        ft.Text(get_text("total"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=130),
                        ft.Text(get_text("received"), size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=80),
                    ], spacing=8),
                    ft.Container(height=8),
                    items_list,
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Action Buttons
        back_btn = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ARROW_BACK, size=18, color=self.primary_color),
                ft.Text(get_text("back_to_list"), size=14, color=self.primary_color),
            ], spacing=6),
            on_click=lambda e: self.navigate("purchase_order_list"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, self.primary_color),
            ),
        )
        
        action_row = ft.Row([back_btn], spacing=12, alignment=ft.MainAxisAlignment.END)
        
        return ft.Column([
            po_info_card,
            items_card,
            action_row,
        ], spacing=20)
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()