# pages/invoices/invoice_create.py
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
        self.success_color = "#10B981"
        
        # Data storage
        self.pending_jobs = []
        self.selected_job_id = None
        self.selected_job_data = None
        self.parts = []
        self.services = []
        self.summary = {}
        self.discount_amount = 0
        self.final_total = 0
        self.total_amount = 0
        
        # UI references
        self.job_search_field = None
        self.job_clear_button = None
        self.job_results_container = None
        self.job_results_list = None
        self.selected_job_card = None
        self.selected_job_label = None
        self.content_area = None
        self.total_amount_text = None
        self.discount_text = None
        self.final_total_text = None
        self.payment_method_dropdown = None
        self.received_field = None
        self.change_text = None
        self.create_btn = None
        self.is_processing = False
        
    def build(self):
        # Header with Create Button in right side
        self.create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PAYMENT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("confirm_payment"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=8),
            on_click=self.confirm_payment,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=0,
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
        )
        
        header = ft.Container(
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
                    self.create_btn,
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
        
        # Create main content area with loading
        self.content_area = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.padding.all(40),
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Load data
        self.page.run_task(self._load_data)
        
        return main_content
    
    async def _load_data(self):
        """Load pending jobs"""
        await asyncio.sleep(0.2)
        self.load_pending_jobs()
    
    def load_pending_jobs(self):
        """Load job orders that are ready for invoicing"""
        try:
            all_orders = self.client.get_job_orders() or []
            
            self.pending_jobs = []
            for order in all_orders:
                status = order.get('status', '')
                if status in ['finished', 'closed']:
                    try:
                        invoices = self.client.get_invoices(job_order_id=order.get('id'))
                        if not invoices:
                            self.pending_jobs.append(order)
                    except:
                        self.pending_jobs.append(order)
            
            if self.job_order_id:
                for job in self.pending_jobs:
                    if job.get('id') == self.job_order_id:
                        self.selected_job_id = self.job_order_id
                        self.selected_job_data = job
                        self.load_invoice_info()
                        return
            
            self._build_search_ui()
            
        except Exception as ex:
            print(f"Error loading pending jobs: {ex}")
            self._show_error(str(ex))
    
    def _build_search_ui(self):
        """Build search UI for finding job orders"""
        
        # Search field
        self.job_search_field = ft.TextField(
            label=get_text("search_job_order"),
            hint_text=get_text("search_by_job_no_customer_plate"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            on_change=self.on_search_job,
            border_color=ft.Colors.GREY_200,
        )
        
        # Clear button
        self.job_clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=18,
            icon_color=ft.Colors.GREY_500,
            on_click=lambda e: self.clear_search(),
            visible=False,
        )
        
        search_row = ft.Row([self.job_search_field, self.job_clear_button], spacing=8)
        
        # Search results container
        self.job_results_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=200)
        self.job_results_container = ft.Container(
            content=self.job_results_list,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=12,
            padding=ft.padding.all(8),
            bgcolor=ft.Colors.WHITE,
            visible=False,
        )
        
        # Selected job card
        self.selected_job_label = ft.Text("", size=13, weight=ft.FontWeight.W_500, color="#1E293B")
        
        self.selected_job_card = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=self.success_color),
                        ft.Column([
                            ft.Text(get_text("selected_job"), size=11, color="#64748B"),
                            self.selected_job_label,
                        ], spacing=2, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color="#64748B",
                            on_click=lambda e: self.clear_selected_job(),
                            tooltip=get_text("clear_selection"),
                        ),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                ),
                elevation=0,
            ),
            margin=ft.margin.only(top=8),
            visible=False,
        )
        
        # No jobs message
        no_jobs_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=ft.Colors.GREY_400),
                    ft.Text("ບໍ່ມີໃບຮັບລົດທີ່ພ້ອມອອກໃບຮັບເງິນ", size=16, color="#64748B", text_align=ft.TextAlign.CENTER),
                    ft.Text("ກະລຸນາສໍາເລັດການສ້ອມແປງກ່ອນ", size=12, color="#94A3B8", text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                padding=ft.padding.all(40),
            ),
            elevation=2,
        )
        
        if not self.pending_jobs:
            self.content_area.content = no_jobs_card
            self.page.update()
            return
        
        # Selection card
        selection_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                            ft.Text(get_text("select_job_order"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=12),
                    search_row,
                    ft.Container(height=8),
                    self.job_results_container,
                    self.selected_job_card,
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
        )
        
        self.content_area.content = selection_card
        self.page.update()
    
    def on_search_job(self, e):
        query = self.job_search_field.value.lower() if self.job_search_field.value else ""
        self.job_clear_button.visible = bool(query)
        
        if not query:
            self.job_results_container.visible = False
            self.page.update()
            return
        
        filtered = [
            job for job in self.pending_jobs
            if query in job.get('job_no', '').lower()
            or query in job.get('customer_name', '').lower()
            or query in job.get('plate_number', '').lower()
        ]
        
        self.job_results_list.controls.clear()
        
        if not filtered:
            self.job_results_list.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_orders_found"), size=13, color="#94A3B8"),
                    padding=ft.padding.all(20),
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for job in filtered[:10]:
                job_id = job.get('id')
                job_no = job.get('job_no', '-')
                customer_name = job.get('customer_name', '-')
                plate_number = job.get('plate_number', '-')
                
                result_item = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color),
                            bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                            border_radius=10,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column([
                            ft.Text(job_no, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                            ft.Text(f"{customer_name} | {plate_number}", size=11, color="#64748B"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color="#94A3B8"),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    ink=True,
                    on_click=lambda e, jid=job_id: self.select_job(jid),
                )
                self.job_results_list.controls.append(result_item)
        
        self.job_results_container.visible = True
        self.page.update()
    
    def clear_search(self):
        self.job_search_field.value = ""
        self.job_clear_button.visible = False
        self.job_results_container.visible = False
        self.page.update()
    
    def clear_selected_job(self):
        self.selected_job_id = None
        self.selected_job_data = None
        self.selected_job_card.visible = False
        self.job_search_field.value = ""
        self._build_search_ui()
        self.page.update()
    
    def select_job(self, job_id):
        self.selected_job_id = job_id
        for job in self.pending_jobs:
            if job.get('id') == job_id:
                self.selected_job_data = job
                break
        
        if self.selected_job_data:
            job_no = self.selected_job_data.get('job_no', '-')
            customer_name = self.selected_job_data.get('customer_name', '-')
            plate_number = self.selected_job_data.get('plate_number', '-')
            self.selected_job_label.value = f"{job_no} - {customer_name} - {plate_number}"
            self.job_search_field.value = job_no
            self.job_results_container.visible = False
            self.selected_job_card.visible = True
            self.load_invoice_info()
    
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
            padding=ft.padding.all(40),
        )
        self.page.update()
        
        try:
            result = self.client.get_invoice_info_by_job_order(self.selected_job_id)
            
            self.selected_job_data = result.get('job_order', {})
            self.parts = result.get('parts', [])
            self.services = result.get('services', [])
            self.summary = result.get('summary', {})
            self.total_amount = self.summary.get('total_amount', 0)
            self.discount_amount = self.summary.get('total_discount', 0)
            self.final_total = self.summary.get('final_total', self.total_amount)
            
            self._build_invoice_form()
            
        except Exception as ex:
            print(f"Error loading invoice info: {ex}")
            self._show_error(str(ex))
    
    def _show_error(self, message):
        error_content = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                    ft.Text(f"{get_text('error')}: {message}", size=14, color=ft.Colors.RED_600),
                    ft.Container(height=16),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("retry")),
                        on_click=lambda e: self.load_invoice_info(),
                        style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                padding=ft.padding.all(40),
            ),
            elevation=2,
        )
        self.content_area.content = error_content
        self.page.update()
    
    def _build_invoice_form(self):
        """Build the invoice form with loaded data"""
        
        # Job Info Card
        job_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("job_order_info"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("job_number"), size=11, color="#64748B"),
                            ft.Text(self.selected_job_data.get('job_no', '-'), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ], spacing=3, expand=True),
                        ft.Column([
                            ft.Text(get_text("customer_name"), size=11, color="#64748B"),
                            ft.Text(self.selected_job_data.get('customer_name', '-'), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ], spacing=3, expand=True),
                        ft.Column([
                            ft.Text(get_text("customer_phone"), size=11, color="#64748B"),
                            ft.Text(self.selected_job_data.get('customer_phone', '-'), size=13, color="#1E293B"),
                        ], spacing=3, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("plate_number"), size=11, color="#64748B"),
                            ft.Text(self.selected_job_data.get('plate_number', '-'), size=14, weight=ft.FontWeight.W_700, color=self.primary_color),
                        ], spacing=3, expand=True),
                        ft.Column([
                            ft.Text(get_text("car_brand_model"), size=11, color="#64748B"),
                            ft.Text(f"{self.selected_job_data.get('brand', '')} {self.selected_job_data.get('model', '')}", size=13, color="#1E293B"),
                        ], spacing=3, expand=True),
                    ]),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
        
        # Items List
        items_list = ft.Column(spacing=6)
        
        # Add services
        for idx, service in enumerate(self.services):
            name = service.get('name', '-')
            qty = service.get('qty', 1)
            unit_price = service.get('unit_price', 0)
            total = service.get('total', qty * unit_price)
            bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.BUILD, size=16, color=self.primary_color),
                        width=30,
                    ),
                    ft.Text(name, size=13, expand=True, max_lines=2),
                    ft.Text(f"x{qty}", size=12, color="#64748B", width=50, text_align=ft.TextAlign.CENTER),
                    ft.Text(self._format_currency(unit_price), size=12, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                    ft.Text(self._format_currency(total), size=13, weight=ft.FontWeight.W_600, color=self.primary_color, width=120, text_align=ft.TextAlign.RIGHT),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                bgcolor=bg_color,
                border_radius=8,
            )
            items_list.controls.append(item_row)
        
        # Add parts
        for idx, part in enumerate(self.parts):
            name = part.get('name', '-')
            qty = part.get('qty', 1)
            unit_price = part.get('unit_price', 0)
            total = part.get('total', qty * unit_price)
            bg_color = ft.Colors.GREY_50 if (idx + len(self.services)) % 2 == 0 else ft.Colors.WHITE
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.INVENTORY, size=16, color=self.primary_color),
                        width=30,
                    ),
                    ft.Text(name, size=13, expand=True, max_lines=2),
                    ft.Text(f"x{qty}", size=12, color="#64748B", width=50, text_align=ft.TextAlign.CENTER),
                    ft.Text(self._format_currency(unit_price), size=12, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                    ft.Text(self._format_currency(total), size=13, weight=ft.FontWeight.W_600, color=self.primary_color, width=120, text_align=ft.TextAlign.RIGHT),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                bgcolor=bg_color,
                border_radius=8,
            )
            items_list.controls.append(item_row)
        
        items_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.LIST_ALT, size=18, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("items_list"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(get_text("total") + ":", size=11, color="#64748B"),
                                    ft.Text(self._format_currency(self.total_amount), size=13, weight=ft.FontWeight.W_600, color=self.primary_color),
                                ], spacing=6),
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                bgcolor=ft.Colors.GREY_50,
                                border_radius=16,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=8),
                    items_list if items_list.controls else ft.Container(
                        content=ft.Text(get_text("no_items"), size=13, color="#94A3B8"),
                        padding=ft.padding.all(30),
                        alignment=ft.Alignment(0, 0),
                    ),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=16),
        )
        
        # Payment Section
        self.total_amount_text = ft.Text(self._format_currency(self.total_amount), size=16, weight=ft.FontWeight.W_600, color="#1E293B", text_align=ft.TextAlign.RIGHT)
        self.discount_text = ft.Text(self._format_currency(self.discount_amount), size=14, weight=ft.FontWeight.W_600, color=ft.Colors.RED_600, text_align=ft.TextAlign.RIGHT)
        self.final_total_text = ft.Text(self._format_currency(self.final_total), size=22, weight=ft.FontWeight.BOLD, color=self.success_color, text_align=ft.TextAlign.RIGHT)
        
        self.payment_method_dropdown = ft.Dropdown(
            label=get_text("payment_method"),
            value="cash",
            options=[
                ft.dropdown.Option("cash", get_text("payment_cash")),
                ft.dropdown.Option("transfer", get_text("payment_transfer")),
                ft.dropdown.Option("qr", get_text("payment_qr")),
            ],
            expand=True,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )
        
        self.received_field = ft.TextField(
            label=get_text("received_amount"),
            value=str(self.final_total),
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )
        
        self.change_text = ft.Text("0 KIP", size=16, weight=ft.FontWeight.BOLD, color=self.success_color, text_align=ft.TextAlign.RIGHT)
        
        def on_received_change(e):
            try:
                received = float(e.control.value) if e.control.value else 0
                change = max(0, received - self.final_total)
                self.change_text.value = self._format_currency(change)
                self.page.update()
            except:
                self.change_text.value = "0 KIP"
        
        self.received_field.on_change = on_received_change
        
        # Total Card
        total_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.PAYMENT, size=18, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(get_text("payment_summary"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("total_amount"), size=12, color="#64748B"),
                            self.total_amount_text,
                        ], spacing=4, expand=True, horizontal_alignment=ft.CrossAxisAlignment.START),
                        ft.Column([
                            ft.Text(get_text("discount"), size=12, color="#64748B"),
                            self.discount_text,
                        ], spacing=4, expand=True, horizontal_alignment=ft.CrossAxisAlignment.START),
                    ]),
                    ft.Container(height=8),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("final_total"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            self.final_total_text,
                        ], spacing=4, expand=True),
                    ]),
                    ft.Container(height=16),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=12),
                    ft.Row([
                        self.payment_method_dropdown,
                        self.received_field,
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.END),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Text(get_text("change"), size=12, color="#64748B", width=100),
                        ft.Container(expand=True),
                        self.change_text,
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
        )
        
        # Create Button (bottom)
        bottom_create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PAYMENT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("confirm_payment"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=8),
            on_click=self.confirm_payment,
            style=ft.ButtonStyle(
                bgcolor=self.success_color,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=32, vertical=14),
            ),
        )
        
        # Scrollable content
        scrollable_content = ft.Column([
            job_card,
            items_card,
            total_card,
            ft.Container(height=24),
            ft.Row([bottom_create_btn], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
        ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Update content area
        self.content_area.content = scrollable_content
        self.page.update()
    
    def confirm_payment(self, e):
        """Confirm payment and create invoice"""
        if self.is_processing:
            return
        
        self.is_processing = True
        if self.create_btn:
            self.create_btn.disabled = True
        self.page.update()
        
        try:
            payment_method = self.payment_method_dropdown.value if self.payment_method_dropdown else "cash"
            
            try:
                received_amount = float(self.received_field.value) if self.received_field.value else 0
            except:
                received_amount = self.final_total
            
            change_amount = max(0, received_amount - self.final_total)
            payment_status = 'paid' if received_amount >= self.final_total else 'pending'
            
            result = self.client.create_invoice(
                job_order_id=self.selected_job_id,
                total_amount=self.total_amount,
                total_discount=self.discount_amount,
                final_total=self.final_total,
                payment_method=payment_method,
                payment_status=payment_status,
                received_amount=received_amount,
                change_amount=change_amount
            )
            
            if result and result.get('id'):
                self.show_success_popup(result.get('id'))
            else:
                self.show_snack_bar(get_text("create_invoice_failed"), is_error=True)
                self.is_processing = False
                if self.create_btn:
                    self.create_btn.disabled = False
                self.page.update()
        except Exception as ex:
            print(f"Exception: {ex}")
            self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
            self.is_processing = False
            if self.create_btn:
                self.create_btn.disabled = False
            self.page.update()
    
    def show_success_popup(self, invoice_id):
        def go_to_list(e):
            popup.open = False
            self.navigate("invoice_list")
        
        def go_to_detail(e):
            popup.open = False
            # Use lambda to capture invoice_id properly
            self.navigate("invoice_detail", invoice_id=invoice_id)
        
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=28, color=ft.Colors.WHITE),
                            bgcolor=self.success_color,
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
                width=380,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.OutlinedButton(
                            get_text("back_to_list"),
                            on_click=go_to_list,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, self.primary_color),
                            ),
                        ),
                        ft.ElevatedButton(
                            get_text("view_invoice"),
                            on_click=go_to_detail,
                            style=ft.ButtonStyle(
                                bgcolor=self.primary_color,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                            ),
                        ),
                    ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
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