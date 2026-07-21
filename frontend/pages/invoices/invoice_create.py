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
        self.current_snackbar = None
        
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
                ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("save_invoice") if get_text("save_invoice") != "save_invoice" else "ບັນທຶກໃບຮັບເງິນ", size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=8),
            on_click=self.confirm_payment,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=0,
                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
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
                           
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    self.create_btn,
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
        
        # Create main content area with loading
        self.content_area = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.Padding(left=40, right=40, top=40, bottom=40),
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
        await asyncio.sleep(0.2)
        self.load_pending_jobs()
    
    def load_pending_jobs(self):
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
        # Search field
        self.job_search_field = ft.TextField(
            label=get_text("search_job_order"),
            hint_text=get_text("search_by_job_no_customer_plate"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
            on_change=self.on_search_job,
            border_color=ft.Colors.GREY_200,
        )
        
        self.job_clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=18,
            icon_color=ft.Colors.GREY_500,
            on_click=lambda e: self.clear_search(),
            visible=False,
        )
        
        search_row = ft.Row([self.job_search_field, self.job_clear_button], spacing=8)
        
        self.job_results_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=200)
        self.job_results_container = ft.Container(
            content=self.job_results_list,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            border_radius=12,
            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
            bgcolor=ft.Colors.WHITE,
            visible=False,
        )
        
        self.selected_job_label = ft.Text("", size=13, weight=ft.FontWeight.W_500, color="#1E293B")
        
        self.selected_job_card = ft.Container(
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
                padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
            visible=False,
        )
        
        no_jobs_card = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=ft.Colors.GREY_400),
                ft.Text(get_text("no_jobs_ready_for_invoice"), size=16, color="#64748B", text_align=ft.TextAlign.CENTER),
                ft.Text(get_text("complete_repair_first"), size=12, color="#94A3B8", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            padding=ft.Padding(left=40, right=40, top=40, bottom=40),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
        )
        
        if not self.pending_jobs:
            self.content_area.content = no_jobs_card
            self.page.update()
            return
        
        # ✅ Show pending jobs immediately without search
        self._display_pending_jobs()
        
        selection_card = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                        ft.Text(get_text("select_job_order"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=8),
                search_row,
                ft.Container(height=8),
                self.job_results_container,
                self.selected_job_card,
            ]),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        self.content_area.content = selection_card
        self.page.update()
    
    def _display_pending_jobs(self):
        """Display all pending jobs in the results list (without search)"""
        self.job_results_list.controls.clear()
        
        if not self.pending_jobs:
            self.job_results_list.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_orders_found"), size=13, color="#94A3B8"),
                    padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                    alignment=ft.Alignment(0, 0),
                )
            )
            self.job_results_container.visible = True
            return
        
        # Show up to 10 pending jobs
        for job in self.pending_jobs[:10]:
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
                        padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                    ),
                    ft.Column([
                        ft.Text(job_no, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ft.Text(f"{customer_name} | {plate_number}", size=11, color="#64748B"),
                    ], spacing=2, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color="#94A3B8"),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                ink=True,
                on_click=lambda e, jid=job_id: self.select_job(jid),
            )
            self.job_results_list.controls.append(result_item)
        
        self.job_results_container.visible = True
        self.page.update()
    
    def on_search_job(self, e):
        query = self.job_search_field.value.lower() if self.job_search_field.value else ""
        self.job_clear_button.visible = bool(query)
        
        if not query:
            # If search is cleared, show all pending jobs again
            self._display_pending_jobs()
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
                    padding=ft.Padding(left=20, right=20, top=20, bottom=20),
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
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Column([
                            ft.Text(job_no, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                            ft.Text(f"{customer_name} | {plate_number}", size=11, color="#64748B"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color="#94A3B8"),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                    ink=True,
                    on_click=lambda e, jid=job_id: self.select_job(jid),
                )
                self.job_results_list.controls.append(result_item)
        
        self.job_results_container.visible = True
        self.page.update()
    
    def clear_search(self):
        self.job_search_field.value = ""
        self.job_clear_button.visible = False
        self._display_pending_jobs()
        self.page.update()
    
    def clear_selected_job(self):
        self.selected_job_id = None
        self.selected_job_data = None
        self.selected_job_card.visible = False
        self.job_search_field.value = ""
        self._display_pending_jobs()
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
        if not self.selected_job_id:
            return
        
        self.content_area.content = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.Padding(left=40, right=40, top=40, bottom=40),
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
        error_content = ft.Container(
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
            padding=ft.Padding(left=40, right=40, top=40, bottom=40),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
        )
        self.content_area.content = error_content
        self.page.update()
    
    def _create_info_row(self, label, value):
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=12, color="#64748B", width=110),
                ft.Text(value, size=13, color="#1E293B", weight=ft.FontWeight.W_500, expand=True),
            ], spacing=12),
            padding=ft.Padding(left=0, right=0, top=5, bottom=5),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)),
        )
    
    def _build_invoice_form(self):
        # Job Info Card (Clean Card)
        job_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                    ft.Text(get_text("job_order_info"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=4),
                self._create_info_row(get_text("job_number"), self.selected_job_data.get('job_no', '-')),
                self._create_info_row(get_text("customer_name"), self.selected_job_data.get('customer_name', '-')),
                self._create_info_row(get_text("customer_phone"), self.selected_job_data.get('customer_phone', '-')),
                self._create_info_row(get_text("plate_number"), self.selected_job_data.get('plate_number', '-')),
                self._create_info_row(get_text("car_brand_model"), f"{self.selected_job_data.get('brand', '')} {self.selected_job_data.get('model', '')}"),
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
        )
        
        # Items List (Clean Card)
        items_list = ft.Column(spacing=0)
        total_amount = 0
        
        # Add services
        for idx, service in enumerate(self.services):
            name = service.get('name', '-')
            qty = service.get('qty', 1)
            unit_price = service.get('unit_price', 0)
            total = service.get('total', qty * unit_price)
            total_amount += total
            
            border_bottom = ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)) if idx < len(self.services) - 1 else None
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.BUILD, size=14, color=self.primary_color, width=25),
                    ft.Text(name, size=13, color="#1E293B", expand=True, max_lines=2),
                    ft.Text(f"x{qty}", size=12, color="#64748B", width=50, text_align=ft.TextAlign.CENTER),
                    ft.Text(self._format_currency(unit_price), size=12, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                    ft.Text(self._format_currency(total), size=13, weight=ft.FontWeight.W_600, color=self.primary_color, width=120, text_align=ft.TextAlign.RIGHT),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=0, right=0, top=8, bottom=8),
                border=border_bottom,
            )
            items_list.controls.append(item_row)
        
        # Add parts
        for idx, part in enumerate(self.parts):
            name = part.get('name', '-')
            qty = part.get('qty', 1)
            unit_price = part.get('unit_price', 0)
            total = part.get('total', qty * unit_price)
            total_amount += total
            
            border_bottom = ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)) if idx < len(self.parts) - 1 else None
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INVENTORY, size=14, color=self.primary_color, width=25),
                    ft.Text(name, size=13, color="#1E293B", expand=True, max_lines=2),
                    ft.Text(f"x{qty}", size=12, color="#64748B", width=50, text_align=ft.TextAlign.CENTER),
                    ft.Text(self._format_currency(unit_price), size=12, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                    ft.Text(self._format_currency(total), size=13, weight=ft.FontWeight.W_600, color=self.primary_color, width=120, text_align=ft.TextAlign.RIGHT),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=0, right=0, top=8, bottom=8),
                border=border_bottom,
            )
            items_list.controls.append(item_row)
        
        # Subtotal row
        subtotal_row = ft.Container(
            content=ft.Row([
                ft.Container(expand=True),
                ft.Text(get_text("subtotal") + ":", size=13, weight=ft.FontWeight.W_600, color="#64748B"),
                ft.Text(self._format_currency(total_amount), size=14, weight=ft.FontWeight.W_700, color=self.primary_color),
            ], spacing=12),
            padding=ft.Padding(left=0, right=0, top=10, bottom=10),
            bgcolor="#F8FAFC",
            border_radius=8,
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
        )
        items_list.controls.append(subtotal_row)
        
        # Discount row
        if self.discount_amount > 0:
            discount_row = ft.Container(
                content=ft.Row([
                    ft.Container(expand=True),
                    ft.Text(get_text("discount") + ":", size=13, weight=ft.FontWeight.W_600, color="#64748B"),
                    ft.Text(f"-{self._format_currency(self.discount_amount)}", size=14, weight=ft.FontWeight.W_700, color=ft.Colors.RED_600),
                ], spacing=12),
                padding=ft.Padding(left=0, right=0, top=8, bottom=8),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED_600),
                border_radius=8,
                margin=ft.Margin(left=0, right=0, top=4, bottom=0),
            )
            items_list.controls.append(discount_row)
            total_amount -= self.discount_amount
        
        # Final total row
        final_total_row = ft.Container(
            content=ft.Row([
                ft.Container(expand=True),
                ft.Text(get_text("final_total") + ":", size=15, weight=ft.FontWeight.W_700, color="#1E293B"),
                ft.Text(self._format_currency(total_amount), size=18, weight=ft.FontWeight.W_800, color=self.success_color),
            ], spacing=12),
            padding=ft.Padding(left=0, right=0, top=12, bottom=12),
            bgcolor=ft.Colors.with_opacity(0.1, self.success_color),
            border_radius=8,
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
        )
        items_list.controls.append(final_total_row)
        
        items_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LIST_ALT, size=18, color=self.primary_color),
                    ft.Text(get_text("items_list"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ATTACH_MONEY, size=14, color=self.success_color),
                            ft.Text(self._format_currency(total_amount), size=14, weight=ft.FontWeight.W_700, color=self.success_color),
                        ], spacing=4),
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                        bgcolor=ft.Colors.with_opacity(0.1, self.success_color),
                        border_radius=16,
                    ),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=8),
                ft.Row([
                    ft.Text("#", size=11, weight=ft.FontWeight.W_600, color="#64748B", width=25),
                    ft.Text(get_text("item_name"), size=11, weight=ft.FontWeight.W_600, color="#64748B", expand=True),
                    ft.Text(get_text("qty"), size=11, weight=ft.FontWeight.W_600, color="#64748B", width=50, text_align=ft.TextAlign.CENTER),
                    ft.Text(get_text("price"), size=11, weight=ft.FontWeight.W_600, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                    ft.Text(get_text("total"), size=11, weight=ft.FontWeight.W_600, color="#64748B", width=120, text_align=ft.TextAlign.RIGHT),
                ], spacing=8),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=4),
                items_list,
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
        )
        
        # Summary Section (Clean Card)
        payment_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.RECEIPT_LONG, size=18, color=self.primary_color),
                    ft.Text(get_text("invoice_summary") if get_text("invoice_summary") != "invoice_summary" else "ສະຫຼຸບໃບເກັບເງິນ", size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=8),
                self._create_info_row(get_text("final_total"), self._format_currency(self.final_total)),
                ft.Container(height=16),
                ft.Text("ໃບເກັບເງິນນີ້ຈະຖືກບັນທຶກໃນສະຖານະ 'ໜີ້ຕ້ອງຮັບ' (Pending) ແລະ ສາມາດກົດຮັບຊຳລະເງິນໄດ້ໃນໜ້າລາຍການໃບຮັບເງິນ.", size=12, color="#64748B"),
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        # Two column layout
        left_column = ft.Container(
            content=ft.Column([job_card, items_card], spacing=0),
            width=650,
            expand=True,
        )
        
        right_column = ft.Container(
            content=ft.Column([payment_card], spacing=0),
            width=400,
            expand=True,
        )
        
        two_columns = ft.Row(
            [left_column, ft.VerticalDivider(width=1, color=ft.Colors.GREY_300), right_column],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        main_card = ft.Container(
            content=two_columns,
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            expand=True,
        )
        
        # Update content area
        self.content_area.content = ft.Column([main_card], expand=True, scroll=ft.ScrollMode.AUTO)
        self.page.update()
    
    def confirm_payment(self, e):
        if self.is_processing:
            return
        
        self.is_processing = True
        if self.create_btn:
            self.create_btn.disabled = True
        self.page.update()
        
        try:
            result = self.client.create_invoice(
                job_order_id=self.selected_job_id,
                total_amount=self.total_amount,
                total_discount=self.discount_amount,
                final_total=self.final_total,
                payment_method="cash",
                payment_status="pending",
                received_amount=0,
                change_amount=0
            )
            
            if result and result.get('id'):
                self.show_success_popup(result.get('id'))
            else:
                self.show_snack_bar(get_text("create_invoice_failed"), "error")
                self.is_processing = False
                if self.create_btn:
                    self.create_btn.disabled = False
                self.page.update()
        except Exception as ex:
            print(f"Exception: {ex}")
            self.show_snack_bar(f"{get_text('error')}: {str(ex)}", "error")
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
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
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
                padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(height=8),
                    ft.Text(
                        "ບັນທຶກໃບເກັບເງິນສຳເລັດແລ້ວ!",
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
                        padding=ft.Padding(left=12, right=12, top=12, bottom=12),
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
                padding=ft.Padding(left=24, right=24, top=24, bottom=24),
                width=360,
                height=160,
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
                                padding=ft.Padding(left=20, right=20, top=10, bottom=10),
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