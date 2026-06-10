import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime
import asyncio

from i18n import get_text


class InvoiceCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, 
                 job_order_id: int = None, content_container: ft.Container = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.job_order_id = job_order_id
        self.content_container = content_container
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
        # Data storage
        self.pending_jobs = []
        self.selected_job_id = None
        self.selected_job_data = None
        self.parts = []
        self.services = []
        self.summary = {}
        
        # UI references
        self.job_dropdown = None
        self.job_info_container = None
        self.job_info_text = None
        self.content_area = None
        self.total_amount_text = None
        self.discount_text = None
        self.final_total_text = None
        self.promo_code_field = None
        self.promo_message = None
        self.create_btn = None
        self.is_processing = False
        
    def build(self):
        header = self._build_header()
        
        # Create main content area with loading
        self.content_area = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Load data
        self.page.run_task(self._load_data)
        
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
                                get_text("create_invoice"),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                "ສ້າງໃບຮັບເງິນ / Create Invoice",
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
            padding=ft.padding.symmetric(vertical=14, horizontal=24),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
    
    async def _load_data(self):
        """Load pending jobs (approved quotations or finished repairs)"""
        await asyncio.sleep(0.2)
        self.load_pending_jobs()
    
    def load_pending_jobs(self):
        """Load job orders that are ready for invoicing"""
        try:
            # Get all job orders
            all_orders = self.client.get_job_orders() or []
            
            # Filter job orders that need invoice (status = 'approved' or 'finished' or 'closed')
            # And check if invoice doesn't exist
            self.pending_jobs = []
            
            for order in all_orders:
                status = order.get('status', '')
                # Only show jobs that are approved, finished, or closed
                if status in ['approved', 'finished', 'closed']:
                    # Check if invoice already exists
                    try:
                        invoices = self.client.get_invoices(job_order_id=order.get('id'))
                        if not invoices:
                            self.pending_jobs.append(order)
                    except:
                        self.pending_jobs.append(order)
            
            if self.job_order_id:
                # If specific job ID provided, select it
                for job in self.pending_jobs:
                    if job.get('id') == self.job_order_id:
                        self.selected_job_id = self.job_order_id
                        self.selected_job_data = job
                        self.load_invoice_info()
                        return
            
            # Build the selection UI
            self._build_selection_ui()
            
        except Exception as ex:
            print(f"Error loading pending jobs: {ex}")
            self._show_error(str(ex))
    
    def _build_selection_ui(self):
        """Build UI for selecting job order"""
        
        # Job dropdown
        self.job_dropdown = ft.Dropdown(
            label=get_text("select_job_order"),
            hint_text=get_text("select_job_order_for_invoice"),
            border_radius=12,
            bgcolor=ft.Colors.GREY_100,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            options=[],
            expand=True,
        )
        self.job_dropdown.on_change = self.on_job_select
        
        # Populate dropdown
        for job in self.pending_jobs:
            self.job_dropdown.options.append(
                ft.dropdown.Option(
                    str(job.get('id')),
                    f"{job.get('job_no')} - {job.get('customer_name')} - {job.get('plate_number')}"
                )
            )
        
        # Job info container
        self.job_info_text = ft.Text("", size=13, color="#1E293B")
        self.job_info_container = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=self.primary_color),
                        ft.Text(get_text("selected_job"), size=12, weight=ft.FontWeight.W_500, color="#64748B"),
                    ],
                    spacing=4,
                ),
                ft.Container(height=4),
                self.job_info_text,
            ]),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            visible=False,
        )
        
        # Selection card
        selection_card = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color),
                        ft.Text("ເລືອກໃບຮັບລົດ", size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=12),
                self.job_dropdown,
                ft.Container(height=10),
                self.job_info_container,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        # No jobs message
        if not self.pending_jobs:
            no_jobs_card = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=ft.Colors.GREY_400),
                    ft.Text("ບໍ່ມີໃບຮັບລົດທີ່ພ້ອມອອກໃບຮັບເງິນ", size=16, color="#64748B", text_align=ft.TextAlign.CENTER),
                    ft.Text("ກະລຸນາອະນຸມັດໃບສະເໜີລາຄາ ຫຼື ສຳເລັດການສ້ອມແປງກ່ອນ", size=12, color="#94A3B8", text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                padding=ft.padding.all(40),
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            )
            self.content_area.content = no_jobs_card
            self.page.update()
            return
        
        # Update content area
        self.content_area.content = selection_card
        self.page.update()
    
    def on_job_select(self, e):
        """Handle job selection"""
        if self.job_dropdown.value:
            self.selected_job_id = int(self.job_dropdown.value)
            for job in self.pending_jobs:
                if job.get('id') == self.selected_job_id:
                    self.selected_job_data = job
                    self.job_info_text.value = f"{job.get('job_no')} - {job.get('customer_name')} - {job.get('plate_number')}"
                    self.job_info_container.visible = True
                    break
            
            # Load invoice info
            self.load_invoice_info()
        else:
            self.selected_job_id = None
            self.job_info_container.visible = False
        self.page.update()
    
    def load_invoice_info(self):
        """Load invoice information for the selected job order"""
        if not self.selected_job_id:
            return
        
        # Show loading
        self.content_area.content = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )
        self.page.update()
        
        try:
            result = self.client.get_invoice_info_by_job_order(self.selected_job_id)
            
            self.selected_job_data = result.get('job_order', {})
            self.parts = result.get('parts', [])
            self.services = result.get('services', [])
            self.summary = result.get('summary', {})
            
            # Build invoice form
            self._build_invoice_form()
            
        except Exception as ex:
            print(f"Error loading invoice info: {ex}")
            import traceback
            traceback.print_exc()
            self._show_error(str(ex))
    
    def _show_error(self, message):
        """Show error message"""
        error_content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                ft.Text(f"{get_text('error')}: {message}", size=14, color=ft.Colors.RED_600),
                ft.ElevatedButton(
                    content=ft.Text(get_text("retry")),
                    on_click=lambda e: self.load_invoice_info(),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )
        self.content_area.content = error_content
        self.page.update()
    
    def _build_invoice_form(self):
        """Build the invoice form with loaded data"""
        
        total_amount = self.summary.get('total_amount', 0)
        self.discount_amount = self.summary.get('total_discount', 0)
        self.final_total = self.summary.get('final_total', total_amount)
        
        # Job Info Card
        job_card = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                        ft.Text(get_text("job_order_info"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=12),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("job_number"), size=11, color="#64748B"),
                        ft.Text(self.selected_job_data.get('job_no', '-'), size=13, weight=ft.FontWeight.W_500),
                    ], expand=True),
                    ft.Column([
                        ft.Text(get_text("customer_name"), size=11, color="#64748B"),
                        ft.Text(self.selected_job_data.get('customer_name', '-'), size=13, weight=ft.FontWeight.W_500),
                    ], expand=True),
                    ft.Column([
                        ft.Text(get_text("customer_phone"), size=11, color="#64748B"),
                        ft.Text(self.selected_job_data.get('customer_phone', '-'), size=13),
                    ], expand=True),
                ]),
                ft.Container(height=8),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("plate_number"), size=11, color="#64748B"),
                        ft.Text(self.selected_job_data.get('plate_number', '-'), size=13, weight=ft.FontWeight.W_500),
                    ], expand=True),
                    ft.Column([
                        ft.Text(get_text("car_brand_model"), size=11, color="#64748B"),
                        ft.Text(f"{self.selected_job_data.get('brand', '')} {self.selected_job_data.get('model', '')}", size=13),
                    ], expand=True),
                ]),
            ]),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        # Items List
        items_list = ft.Column(spacing=6)
        
        # Add services
        for service in self.services:
            name = service.get('name', '-')
            qty = service.get('qty', 1)
            unit_price = service.get('unit_price', 0)
            total = service.get('total', qty * unit_price)
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.BUILD, size=16, color=self.primary_color),
                        width=28,
                    ),
                    ft.Text(name, size=12, expand=True),
                    ft.Text(f"x{qty}", size=11, color="#64748B", width=35),
                    ft.Text(self._format_currency(unit_price), size=11, color="#64748B", width=90),
                    ft.Text(self._format_currency(total), size=12, weight=ft.FontWeight.W_500, color="#1E293B", width=110),
                ]),
                padding=ft.padding.symmetric(vertical=6, horizontal=10),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
            )
            items_list.controls.append(item_row)
        
        # Add parts
        for part in self.parts:
            name = part.get('name', '-')
            qty = part.get('qty', 1)
            unit_price = part.get('unit_price', 0)
            total = part.get('total', qty * unit_price)
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.INVENTORY, size=16, color=self.primary_color),
                        width=28,
                    ),
                    ft.Text(name, size=12, expand=True),
                    ft.Text(f"x{qty}", size=11, color="#64748B", width=35),
                    ft.Text(self._format_currency(unit_price), size=11, color="#64748B", width=90),
                    ft.Text(self._format_currency(total), size=12, weight=ft.FontWeight.W_500, color="#1E293B", width=110),
                ]),
                padding=ft.padding.symmetric(vertical=6, horizontal=10),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
            )
            items_list.controls.append(item_row)
        
        items_card = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LIST_ALT, size=18, color=self.primary_color),
                        ft.Text(get_text("items_list"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=8),
                items_list,
            ]),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        # UI elements
        self.total_amount_text = ft.Text(self._format_currency(total_amount), size=16, weight=ft.FontWeight.BOLD, color="#1E293B")
        self.discount_text = ft.Text(self._format_currency(self.discount_amount), size=13, color=ft.Colors.RED_600)
        self.final_total_text = ft.Text(self._format_currency(self.final_total), size=22, weight=ft.FontWeight.BOLD, color=self.primary_color)
        
        # Payment section
        payment_method_dropdown = ft.Dropdown(
            label=get_text("payment_method"),
            value="cash",
            options=[
                ft.dropdown.Option("cash", get_text("payment_cash")),
                ft.dropdown.Option("transfer", get_text("payment_transfer")),
                ft.dropdown.Option("qr", get_text("payment_qr")),
            ],
            width=180,
            border_radius=10,
        )
        
        received_field = ft.TextField(
            label=get_text("received_amount"),
            value=str(self.final_total),
            width=180,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=10,
            text_size=13,
        )
        
        change_text = ft.Text("0 KIP", size=14, weight=ft.FontWeight.W_500, color="#10B981")
        
        def on_received_change(e):
            try:
                received = float(e.control.value) if e.control.value else 0
                change = max(0, received - self.final_total)
                change_text.value = self._format_currency(change)
                self.page.update()
            except:
                change_text.value = "0 KIP"
        
        received_field.on_change = on_received_change
        
        # Create button
        self.create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PAYMENT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("confirm_payment"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=8),
            on_click=self.confirm_payment,
            style=ft.ButtonStyle(
                bgcolor="#10B981",
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
            ),
        )
        
        # Total Card
        total_card = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CALCULATE, size=18, color=self.primary_color),
                        ft.Text(get_text("payment_summary"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ft.Container(expand=True),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=10),
                ft.Row([
                    ft.Text(get_text("total_amount"), size=13),
                    ft.Container(expand=True),
                    self.total_amount_text,
                ]),
                ft.Row([
                    ft.Text(get_text("discount"), size=13),
                    ft.Container(expand=True),
                    self.discount_text,
                ]),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Row([
                    ft.Text(get_text("final_total"), size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    self.final_total_text,
                ]),
                ft.Container(height=16),
                ft.Row([
                    payment_method_dropdown,
                    received_field,
                    ft.Column([
                        ft.Text(get_text("change"), size=11, color="#64748B"),
                        change_text,
                    ], spacing=2),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.END),
                ft.Container(height=16),
                self.create_btn,
            ]),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        # Scrollable content
        scrollable_content = ft.Column([
            job_card,
            ft.Container(height=16),
            items_card,
            ft.Container(height=16),
            total_card,
            ft.Container(height=16),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Update content area
        self.content_area.content = scrollable_content
        self.page.update()
    
    def confirm_payment(self, e):
        """Confirm payment and create invoice"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.create_btn.disabled = True
        self.create_btn.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
        self.page.update()
        
        try:
            # Get values from form (need to find them in the scrollable content)
            # For simplicity, we'll recreate them or store as instance vars
            payment_method = "cash"
            received_amount = self.final_total
            change_amount = 0
            
            # Find payment method and received amount from the card
            for control in self.content_area.content.controls:
                if isinstance(control, ft.Container) and control.content:
                    for child in control.content.controls:
                        if isinstance(child, ft.Row) and len(child.controls) >= 3:
                            for field in child.controls:
                                if isinstance(field, ft.Dropdown):
                                    payment_method = field.value
                                elif isinstance(field, ft.TextField) and field.label == get_text("received_amount"):
                                    try:
                                        received_amount = float(field.value) if field.value else 0
                                        change_amount = max(0, received_amount - self.final_total)
                                    except:
                                        received_amount = self.final_total
                                        change_amount = 0
                        break
                    break
            
            result = self.client.create_invoice(
                job_order_id=self.selected_job_id,
                total_amount=self.summary.get('total_amount', 0),
                total_discount=self.discount_amount,
                final_total=self.final_total,
                payment_method=payment_method,
                payment_status='paid' if received_amount >= self.final_total else 'pending',
                received_amount=received_amount,
                change_amount=change_amount
            )
            
            if result and result.get('id'):
                self.show_success_popup(result.get('id'))
            else:
                self.show_snack_bar(get_text("create_invoice_failed"), is_error=True)
                self.is_processing = False
                self.create_btn.disabled = False
                self.create_btn.content.controls[0].name = ft.Icons.PAYMENT
                self.page.update()
        except Exception as ex:
            print(f"Exception: {ex}")
            self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
            self.is_processing = False
            self.create_btn.disabled = False
            self.create_btn.content.controls[0].name = ft.Icons.PAYMENT
            self.page.update()
    
    def show_success_popup(self, invoice_id):
        """Show success popup when invoice created successfully"""
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=28, color=ft.Colors.WHITE),
                            bgcolor="#10B981",
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            get_text("success"),
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
                    ft.Container(height=8),
                    ft.Text(
                        get_text("payment_success"),
                        size=15,
                        weight=ft.FontWeight.W_500,
                        color="#1E293B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.RECEIPT, size=16, color=self.primary_color),
                            ft.Text(
                                f"{get_text('invoice_no')}: INV-{invoice_id:04d}",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=self.primary_color,
                            ),
                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.padding.all(12),
                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                        border_radius=10,
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        get_text("view_invoice_detail_message"),
                        size=12,
                        color="#64748B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                padding=ft.padding.all(24),
                width=360,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            get_text("go_to_invoice_list"),
                            on_click=lambda e: self._close_popup_and_go(popup),
                            style=ft.ButtonStyle(
                                bgcolor=self.primary_color,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=24, vertical=10),
                            ),
                        ),
                        ft.Container(expand=True),
                    ]),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def _close_popup_and_go(self, popup):
        popup.open = False
        self.navigate("invoice_list")
    
    def _format_currency(self, amount):
        try:
            return f"{int(amount or 0):,} KIP"
        except:
            return "0 KIP"
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, size=13),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=3000,
        )
        self.page.update()