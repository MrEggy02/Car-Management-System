# pages/invoices/invoice_create.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable

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
        self.job_info = None
        self.parts_usage = []
        self.services = []
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.promo_code_field = None
        self.discount_amount = 0
        self.promotion = None
        self.final_total = 0
        self.total_amount_text = None
        self.discount_text = None
        self.final_total_text = None
        self.promo_message = None
        self.create_btn = None
        self.is_processing = False
        
    def build(self):
        header = self._build_header()
        
        if not self.job_order_id:
            error_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.WARNING_AMBER, size=64, color=ft.Colors.ORANGE_600),
                    ft.Text(get_text("select_job_order_first"), 
                           size=18, weight=ft.FontWeight.BOLD, color="#1E293B", text_align=ft.TextAlign.CENTER),
                    ft.Text(get_text("go_back_and_select_job"), 
                           size=14, color="#64748B", text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton(
                        get_text("back"),
                        on_click=lambda e: self.navigate("job_order_list"),
                        style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
            main_content = ft.Container(
                content=ft.Column([header, error_container]),
                expand=True,
                bgcolor="#F5F7FA",
            )
            return main_content
        
        self.load_invoice_info()
        
        if not self.job_info:
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
                    
                    ft.Column(
                        [
                            ft.Text(
                                get_text("create_invoice"),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("create_invoice_subtitle"),
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
    
    def load_invoice_info(self):
        """Load invoice information for the job order"""
        print(f"DEBUG: job_order_id = {self.job_order_id}")
        
        if not self.job_order_id:
            print("DEBUG: No job_order_id provided!")
            return
        
        try:
            result = self.client.get_invoice_info_by_job_order(self.job_order_id)
            print(f"DEBUG: Result from API = {result}")
            
            self.job_info = result.get('job_info')
            self.parts_usage = result.get('parts_usage', [])
            self.services = result.get('services', [])
            
            if self.job_info:
                self.final_total = self.job_info.get('quotation_total', 0)
                self.discount_amount = 0
                print(f"DEBUG: Total amount = {self.final_total}")
            
            self.page.update()
        except Exception as ex:
            print(f"Error loading invoice info: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
    
    def update_total_display(self):
        """Update total display after discount"""
        if self.total_amount_text:
            total_amount = self.job_info.get('quotation_total', 0) if self.job_info else 0
            self.total_amount_text.value = f"{int(total_amount):,} KIP"
        if self.discount_text:
            self.discount_text.value = f"{int(self.discount_amount):,} KIP"
        if self.final_total_text:
            self.final_total_text.value = f"{int(self.final_total):,} KIP"
        self.page.update()
    
    def _build_content(self):
        job = self.job_info
        total_amount = job.get('quotation_total', 0) if job else 0
        
        # Job Info Card
        job_card = ft.Card(
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
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("job_number"), size=12, color="#64748B"),
                            ft.Text(job.get('job_no', '-') if job else '-', size=14, weight=ft.FontWeight.W_500),
                        ], expand=True),
                        ft.Column([
                            ft.Text(get_text("customer_name"), size=12, color="#64748B"),
                            ft.Text(job.get('customer_name', '-') if job else '-', size=14, weight=ft.FontWeight.W_500),
                        ], expand=True),
                        ft.Column([
                            ft.Text(get_text("customer_phone"), size=12, color="#64748B"),
                            ft.Text(job.get('customer_phone', '-') if job else '-', size=14),
                        ], expand=True),
                    ]),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("plate_number"), size=12, color="#64748B"),
                            ft.Text(job.get('plate_number', '-') if job else '-', size=14, weight=ft.FontWeight.W_500),
                        ], expand=True),
                        ft.Column([
                            ft.Text(get_text("car_brand_model"), size=12, color="#64748B"),
                            ft.Text(f"{job.get('brand', '') if job else ''} {job.get('model', '') if job else ''}", size=14),
                        ], expand=True),
                    ]),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Items List Card
        items_list = ft.Column(spacing=8)
        
        # Add services
        for service in self.services:
            name = service.get('name', '-')
            qty = service.get('qty', 1)
            unit_price = service.get('unit_price', 0)
            total = qty * unit_price
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.BUILD, size=16, color=self.primary_color),
                        width=30,
                    ),
                    ft.Text(name, size=13, expand=True),
                    ft.Text(f"x{qty}", size=12, color="#64748B", width=50),
                    ft.Text(f"{int(unit_price):,}", size=12, color="#64748B", width=100),
                    ft.Text(f"{int(total):,} KIP", size=13, weight=ft.FontWeight.W_500, color="#1E293B", width=130),
                ]),
                padding=ft.padding.symmetric(vertical=6, horizontal=10),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
            )
            items_list.controls.append(item_row)
        
        # Add parts
        for part in self.parts_usage:
            name = part.get('part_name', '-')
            qty = part.get('qty', 1)
            unit_price = part.get('sell_price', 0)
            total = qty * unit_price
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.INVENTORY, size=16, color=self.primary_color),
                        width=30,
                    ),
                    ft.Text(name, size=13, expand=True),
                    ft.Text(f"x{qty}", size=12, color="#64748B", width=50),
                    ft.Text(f"{int(unit_price):,}", size=12, color="#64748B", width=100),
                    ft.Text(f"{int(total):,} KIP", size=13, weight=ft.FontWeight.W_500, color="#1E293B", width=130),
                ]),
                padding=ft.padding.symmetric(vertical=6, horizontal=10),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
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
                            ft.Text(get_text("items_list"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=8),
                    items_list,
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Create UI elements first
        self.total_amount_text = ft.Text(f"{int(total_amount):,} KIP", size=18, weight=ft.FontWeight.BOLD, color="#1E293B")
        self.discount_text = ft.Text("0 KIP", size=14, color=ft.Colors.RED_600)
        self.final_total_text = ft.Text(f"{int(total_amount):,} KIP", size=20, weight=ft.FontWeight.BOLD, color=self.primary_color)
        
        # Promotion Section
        self.promo_code_field = ft.TextField(
            hint_text=get_text("enter_promo_code"),
            width=250,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        )
        
        apply_promo_btn = ft.ElevatedButton(
            get_text("apply_promo"),
            on_click=self.apply_promotion,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK),
            height=40,
        )
        
        self.promo_message = ft.Text("", size=11, visible=False)
        
        # Payment Section
        payment_method_dropdown = ft.Dropdown(
            label=get_text("payment_method"),
            value="cash",
            options=[
                ft.dropdown.Option("cash", get_text("payment_cash")),
                ft.dropdown.Option("transfer", get_text("payment_transfer")),
                ft.dropdown.Option("qr", get_text("payment_qr")),
            ],
            width=200,
            border_radius=8,
        )
        
        received_field = ft.TextField(
            label=get_text("received_amount"),
            value="0",
            width=200,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=8,
        )
        
        self.change_text = ft.Text("0 KIP", size=14, color=ft.Colors.GREEN_600)
        
        def on_received_change(e):
            received = float(e.control.value) if e.control.value else 0
            change = max(0, received - self.final_total)
            self.change_text.value = f"{int(change):,} KIP"
            self.page.update()
        
        received_field.on_change = on_received_change
        
        # Store total_amount for closure
        current_total_amount = total_amount
        
        def confirm_payment(e):
            if self.is_processing:
                return
            
            self.is_processing = True
            if self.create_btn:
                self.create_btn.disabled = True
                self.create_btn.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
            self.page.update()
            
            print("=" * 50)
            print("DEBUG: confirm_payment ຖືກເອີ້ນ")
            
            payment_method = payment_method_dropdown.value
            received_amount = float(received_field.value) if received_field.value else 0
            change_amount = max(0, received_amount - self.final_total)
            
            print(f"DEBUG: job_order_id = {self.job_order_id}")
            print(f"DEBUG: payment_method = {payment_method}")
            print(f"DEBUG: total_amount = {current_total_amount}")
            print(f"DEBUG: total_discount = {self.discount_amount}")
            print(f"DEBUG: final_total = {self.final_total}")
            print(f"DEBUG: received_amount = {received_amount}")
            print(f"DEBUG: change_amount = {change_amount}")
            
            try:
                result = self.client.create_invoice(
                    job_order_id=self.job_order_id,
                    total_amount=current_total_amount,
                    total_discount=self.discount_amount,
                    final_total=self.final_total,
                    payment_method=payment_method,
                    payment_status='paid',
                    received_amount=received_amount,
                    change_amount=change_amount
                )
                print(f"DEBUG: API result = {result}")
                
                if result and result.get('id'):
                    invoice_id = result.get('id')
                    print(f"DEBUG: Invoice ID = {invoice_id}")
                    self.show_success_popup(invoice_id)
                else:
                    print("DEBUG: result ບໍ່ມີ id ຫຼື result ເປັນ None")
                    self.show_snack_bar(get_text("create_invoice_failed"), is_error=True)
                    self.is_processing = False
                    if self.create_btn:
                        self.create_btn.disabled = False
                        self.create_btn.content.controls[0].name = ft.Icons.PAYMENT
                    self.page.update()
            except Exception as ex:
                print(f"DEBUG: Exception = {ex}")
                import traceback
                traceback.print_exc()
                self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
                self.is_processing = False
                if self.create_btn:
                    self.create_btn.disabled = False
                    self.create_btn.content.controls[0].name = ft.Icons.PAYMENT
                self.page.update()
            
            print("=" * 50)
        
        self.create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PAYMENT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("confirm_payment"), size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ], spacing=6),
            on_click=confirm_payment,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, shape=ft.RoundedRectangleBorder(radius=10)),
            height=50,
        )
        
        total_card = ft.Card(
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
                    ft.Row([
                        ft.Text(get_text("total_amount"), size=14),
                        ft.Container(expand=True),
                        self.total_amount_text,
                    ]),
                    ft.Row([
                        ft.Text(get_text("discount"), size=14),
                        ft.Container(expand=True),
                        self.discount_text,
                    ]),
                    ft.Row([
                        ft.Row([
                            self.promo_code_field,
                            apply_promo_btn,
                        ], spacing=8),
                    ]),
                    self.promo_message,
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Row([
                        ft.Text(get_text("final_total"), size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        self.final_total_text,
                    ]),
                    ft.Container(height=16),
                    ft.Row([
                        payment_method_dropdown,
                        received_field,
                    ], spacing=16),
                    ft.Row([
                        ft.Text(get_text("change_amount"), size=14),
                        ft.Container(expand=True),
                        self.change_text,
                    ]),
                    ft.Container(height=16),
                    self.create_btn,
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(top=20),
        )
        
        return ft.Column([
            job_card,
            items_card,
            total_card,
        ], spacing=20)
    
    def apply_promotion(self, e):
        promo_code = self.promo_code_field.value
        if not promo_code:
            self.promo_message.value = get_text("enter_promo_code")
            self.promo_message.color = ft.Colors.RED_600
            self.promo_message.visible = True
            self.page.update()
            return
        
        try:
            total_amount = self.job_info.get('quotation_total', 0) if self.job_info else 0
            result = self.client.validate_promotion(promo_code, total_amount)
            
            if result.get('valid'):
                self.promotion = result.get('promotion')
                self.discount_amount = result.get('discount_amount', 0)
                self.final_total = result.get('final_total', total_amount)
                
                self.discount_text.value = f"{int(self.discount_amount):,} KIP"
                self.final_total_text.value = f"{int(self.final_total):,} KIP"
                self.promo_message.value = f"✅ {get_text('promo_applied')}: {self.promotion.get('promo_name')}"
                self.promo_message.color = ft.Colors.GREEN_600
                self.promo_message.visible = True
                self.promo_code_field.disabled = True
                self.update_total_display()
            else:
                self.promo_message.value = result.get('message', get_text('promo_code_invalid'))
                self.promo_message.color = ft.Colors.RED_600
                self.promo_message.visible = True
        except Exception as ex:
            self.promo_message.value = f"{get_text('error')}: {str(ex)}"
            self.promo_message.color = ft.Colors.RED_600
            self.promo_message.visible = True
        
        self.page.update()
    
    def show_success_popup(self, invoice_id):
        """Show success popup when invoice created successfully"""
        print(f"DEBUG: show_success_popup ຖືກເອີ້ນ, invoice_id = {invoice_id}")
        
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.Colors.WHITE,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN_600),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            get_text("payment_success"),
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            f"{get_text('invoice_no')}: INV-{invoice_id:04d}",
                            size=14,
                            color="#64748B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            get_text("view_invoice_detail_message"),
                            size=12,
                            color="#94A3B8",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                width=380,
                padding=ft.padding.all(24),
            ),
            actions=[
                ft.ElevatedButton(
                    get_text("go_to_invoice_list"),
                    on_click=lambda e: self.go_to_invoice_list(popup),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
        print("DEBUG: Popup ຖືກສະແດງແລ້ວ")
        
        # Reset processing flag
        self.is_processing = False
    
    def go_to_invoice_list(self, popup):
        print("DEBUG: ໄປທີ່ invoice_list")
        popup.open = False
        self.navigate("invoice_list")
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()