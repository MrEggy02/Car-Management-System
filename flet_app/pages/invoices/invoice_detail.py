# pages/invoices/invoice_detail.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable

from i18n import get_text


class InvoiceDetailContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, invoice_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.invoice_id = invoice_id
        self.invoice_data = None
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
    
    def build(self):
        header = self._build_header()
        
        # Load data first
        self.load_invoice_data()
        
        if not self.invoice_data:
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
                        on_click=lambda e: self.navigate("invoice_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("invoice_detail"),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("invoice_detail_subtitle"),
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Icon(ft.Icons.RECEIPT, size=28, color=ft.Colors.WHITE),
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
    
    def load_invoice_data(self):
        try:
            if self.invoice_id:
                self.invoice_data = self.client.get_invoice(self.invoice_id)
                self.page.update()
        except Exception as ex:
            print(f"Error loading invoice detail: {ex}")
    
    def _build_content(self):
        data = self.invoice_data
        
        invoice_no = f"INV-{data.get('id', 0):04d}"
        job_no = data.get("job_no", "-")
        customer_name = data.get("customer_name", "-")
        customer_phone = data.get("customer_phone", "-")
        plate_number = data.get("plate_number", "-")
        brand = data.get("brand", "-")
        model = data.get("model", "-")
        total_amount = data.get("total_amount", 0)
        total_discount = data.get("total_discount", 0)
        final_total = data.get("final_total", 0)
        payment_method = data.get("payment_method", "cash")
        payment_status = data.get("payment_status", "pending")
        received_amount = data.get("received_amount", 0)
        change_amount = data.get("change_amount", 0)
        paid_date = data.get("paid_date", "")
        
        if paid_date:
            paid_date = paid_date[:16] if len(paid_date) > 16 else paid_date
        else:
            paid_date = "-"
        
        status_colors = {
            "pending": "#FF9800",
            "paid": "#4CAF50",
            "partial": "#2196F3",
            "refunded": "#F44336"
        }
        status_texts = {
            "pending": get_text("status_pending"),
            "paid": get_text("status_paid"),
            "partial": get_text("status_partial"),
            "refunded": get_text("status_refunded")
        }
        
        method_texts = {
            "cash": get_text("payment_cash"),
            "transfer": get_text("payment_transfer"),
            "qr": get_text("payment_qr")
        }
        
        # Status Badge
        status_badge = ft.Container(
            content=ft.Text(status_texts.get(payment_status, payment_status), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            bgcolor=status_colors.get(payment_status, "#607D8B"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
        )
        
        # Invoice Info Card
        invoice_info_card = ft.Card(
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
                            ft.Text(get_text("invoice_info"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("invoice_no"), size=12, color="#64748B"),
                            ft.Text(invoice_no, size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("status"), size=12, color="#64748B"),
                            status_badge,
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("payment_method"), size=12, color="#64748B"),
                            ft.Text(method_texts.get(payment_method, payment_method), size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("paid_date"), size=12, color="#64748B"),
                            ft.Text(paid_date, size=14),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("received_amount"), size=12, color="#64748B"),
                            ft.Text(f"{int(received_amount):,} KIP", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("change_amount"), size=12, color="#64748B"),
                            ft.Text(f"{int(change_amount):,} KIP", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_700),
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
                            ft.Text(get_text("car_brand_model"), size=12, color="#64748B"),
                            ft.Text(f"{brand} {model}", size=14),
                        ], spacing=2, expand=True),
                    ]),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Amount Card
        amount_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.CALCULATE, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("payment_summary"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Text(get_text("total_amount"), size=14),
                        ft.Container(expand=True),
                        ft.Text(f"{int(total_amount):,} KIP", size=14, weight=ft.FontWeight.W_500),
                    ]),
                    ft.Row([
                        ft.Text(get_text("discount"), size=14),
                        ft.Container(expand=True),
                        ft.Text(f"- {int(total_discount):,} KIP", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.RED_600),
                    ]),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Row([
                        ft.Text(get_text("final_total"), size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Text(f"{int(final_total):,} KIP", size=20, weight=ft.FontWeight.BOLD, color=self.primary_color),
                    ]),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Action Buttons
        print_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("print_invoice"), size=14, color=ft.Colors.WHITE),
            ], spacing=6),
            on_click=lambda e: self.print_invoice(),
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
            on_click=lambda e: self.navigate("invoice_list"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, self.primary_color),
            ),
        )
        
        action_row = ft.Row([back_btn, print_btn], spacing=12, alignment=ft.MainAxisAlignment.END)
        
        return ft.Column([
            invoice_info_card,
            job_info_card,
            amount_card,
            action_row,
        ], spacing=20)
    
    def print_invoice(self):
        """Print invoice - open print dialog"""
        self.show_snack_bar(get_text("print_coming_soon"), is_error=False)
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()