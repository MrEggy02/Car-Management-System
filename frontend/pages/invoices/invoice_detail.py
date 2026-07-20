# pages/invoices/invoice_detail.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime

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
        self.success_color = "#10B981"
        self.current_snackbar = None
        
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
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F0F2F5",
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
                        icon_size=20,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("invoice_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("invoice_detail"),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("invoice_detail_subtitle"),
                                size=12,
                                color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=24, right=24, top=14, bottom=14),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
    
    def load_invoice_data(self):
        try:
            if self.invoice_id:
                self.invoice_data = self.client.get_invoice(self.invoice_id)
                print(f"DEBUG: Loaded invoice data for {self.invoice_id}")
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
            "paid": "#4CAF50"
        }
        status_texts = {
            "pending": get_text("status_pending"),
            "paid": get_text("status_paid")
        }
        
        method_texts = {
            "cash": get_text("payment_cash"),
            "transfer": get_text("payment_transfer")
        }
        
        # Status Badge
        status_badge = ft.Container(
            content=ft.Text(status_texts.get(payment_status, payment_status), size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            bgcolor=status_colors.get(payment_status, "#607D8B"),
            border_radius=20,
            padding=ft.Padding(left=16, right=16, top=6, bottom=6),
        )
        
        # ========== INVOICE INFO CARD ==========
        invoice_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
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
                            ft.Text(get_text("invoice_no"), size=11, color="#64748B"),
                            ft.Text(invoice_no, size=15, weight=ft.FontWeight.W_700, color=self.primary_color),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("status"), size=11, color="#64748B"),
                            status_badge,
                        ], spacing=4, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Column([
                            ft.Text(get_text("payment_method"), size=11, color="#64748B"),
                            ft.Text(method_texts.get(payment_method, payment_method), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ], spacing=4, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("paid_date"), size=11, color="#64748B"),
                            ft.Text(paid_date, size=13, color="#1E293B"),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("received_amount"), size=11, color="#64748B"),
                            ft.Text(f"{int(received_amount):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.success_color),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text(get_text("change_amount"), size=11, color="#64748B"),
                            ft.Text(f"{int(change_amount):,} KIP", size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ], spacing=4, expand=True),
                    ]),
                ]),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            ),
            elevation=2,
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
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
                                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
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
                            ft.Text(f"{brand} {model}", size=13, color="#1E293B"),
                        ], spacing=4, expand=True),
                    ]),
                ]),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            ),
            elevation=2,
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
        )
        
        # ========== PAYMENT SUMMARY CARD ==========
        amount_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.PAYMENT, size=20, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                            ),
                            ft.Text(get_text("payment_summary"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Text(get_text("total_amount"), size=13, color="#64748B"),
                        ft.Container(expand=True),
                        ft.Text(f"{int(total_amount):,} KIP", size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ]),
                    ft.Row([
                        ft.Text(get_text("discount"), size=13, color="#64748B"),
                        ft.Container(expand=True),
                        ft.Text(f"- {int(total_discount):,} KIP", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.RED_600),
                    ]),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Row([
                        ft.Text(get_text("final_total"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ft.Container(expand=True),
                        ft.Text(f"{int(final_total):,} KIP", size=20, weight=ft.FontWeight.BOLD, color=self.success_color),
                    ]),
                ]),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            ),
            elevation=2,
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
        )
        
        # ========== ACTION BUTTONS ==========
        back_btn = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ARROW_BACK, size=18, color=self.primary_color),
                ft.Text(get_text("back_to_list"), size=14, color=self.primary_color, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=lambda e: self.navigate("invoice_list"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, self.primary_color),
                padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            ),
        )
        
        action_row = ft.Row([back_btn], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
        
        return ft.Column([
            invoice_info_card,
            job_info_card,
            amount_card,
            ft.Container(height=20),
            action_row,
        ], spacing=0)
    
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