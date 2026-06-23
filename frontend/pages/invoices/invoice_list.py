# pages/invoices/invoice_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime
import webbrowser
import tempfile
import os
import threading
import time

from i18n import get_text


class InvoiceListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.invoices = []
        self.filtered_invoices = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.search_field = None
        self.current_status_filter = "all"  # เปลี่ยนจาก dropdown เป็น chip
        self.status_chips = None
        self.table_rows = None
        self.pagination_container = None
        self.current_dialog = None
        
    def build(self):
        header = self._build_header()
        search_bar = self._build_search_bar()
        table = self._build_table()
        self.pagination_container = ft.Container(padding=ft.padding.symmetric(vertical=12, horizontal=20))
        
        content_area = ft.Container(
            content=ft.Column([
                search_bar,
                table,
                self.pagination_container,
            ], expand=True),
            expand=True,
            padding=ft.padding.all(24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.load_invoices()
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("invoice_list"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("new_invoice"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.navigate("invoice_create"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        ),
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=12, horizontal=24),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
    
    def _load_status_chips(self):
        """Load status filter chips"""
        if not self.status_chips:
            return
        
        self.status_chips.controls.clear()
        
        status_list = [
            {"id": "all", "name": get_text("all_status")},
            {"id": "pending", "name": get_text("status_pending")},
            {"id": "paid", "name": get_text("status_paid")},
        ]
        
        for status in status_list:
            is_active = self.current_status_filter == status["id"]
            chip = ft.Container(
                content=ft.Text(status["name"], size=12, weight=ft.FontWeight.W_500,
                               color=ft.Colors.WHITE if is_active else "#64748B"),
                bgcolor=self.primary_color if is_active else ft.Colors.GREY_200,
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                ink=True,
                on_click=lambda e, sid=status["id"]: self.filter_by_status(sid),
            )
            self.status_chips.controls.append(chip)
        
        self.page.update()
    
    def filter_by_status(self, status_id):
        """Filter by status chip click"""
        self.current_status_filter = status_id
        self._load_status_chips()
        self.apply_filters()
    
    def _build_search_bar(self):
        # Status Chips
        self.status_chips = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
        self._load_status_chips()
        
        self.search_field = ft.TextField(
            hint_text=get_text("search_invoice"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        self.search_field.on_change = self.on_search_change
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_invoices(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([self.search_field, refresh_button], spacing=10),
                ft.Container(height=12),
                self.status_chips,
            ], spacing=0),
            margin=ft.margin.only(bottom=16),
        )
    
    def _build_table(self):
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("invoice_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("job_number"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("customer_name"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("plate_number"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("final_total"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("payment_status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("payment_method"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("actions"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=160,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=14, horizontal=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        return ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                self.table_rows,
            ], spacing=0),
            margin=ft.margin.only(left=20, right=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12, bottom_left=12, bottom_right=12),
            border=ft.border.all(1, ft.Colors.GREY_200),
            expand=True,
        )
    
    def load_invoices(self):
        self.table_rows.controls.clear()
        self.page.update()
        
        try:
            invoices = self.client.get_invoices()
            print(f"DEBUG: Loaded {len(invoices)} invoices")
            self.invoices = invoices
            self.filtered_invoices = invoices.copy()
            self.display_invoices()
        except Exception as ex:
            print(f"Error loading invoices: {ex}")
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                        ft.Text(f"Error: {str(ex)}", size=14, color=ft.Colors.RED_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(40),
                )
            )
            self.page.update()
    
    def on_search_change(self, e):
        """Real-time search"""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply both status and search filters"""
        selected_status = self.current_status_filter if self.current_status_filter else "all"
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        
        filtered = self.invoices.copy()
        
        # Apply status filter
        if selected_status and selected_status != "all":
            filtered = [i for i in filtered if i.get("payment_status") == selected_status]
        
        # Apply search filter
        if keyword:
            filtered = [
                i for i in filtered
                if keyword in f"INV-{i.get('id', 0):04d}".lower()
                or keyword in i.get("job_no", "").lower()
                or keyword in i.get("customer_name", "").lower()
                or keyword in i.get("plate_number", "").lower()
            ]
        
        self.filtered_invoices = filtered
        self.current_page = 1
        self.display_invoices()
    
    def display_invoices(self):
        self.table_rows.controls.clear()
        
        total_items = len(self.filtered_invoices)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_invoices[start_idx:end_idx]
        
        if page_items:
            for i, invoice in enumerate(page_items):
                self.table_rows.controls.append(self._create_invoice_row(invoice, start_idx + i))
        else:
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.RECEIPT_OUTLINED, size=48, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_invoices_found"), size=16, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(40),
                )
            )
        
        self.update_pagination()
        self.page.update()
    
    def _create_invoice_row(self, invoice: Dict, index: int):
        invoice_id = invoice.get("id")
        invoice_no = f"INV-{invoice_id:04d}"
        job_no = invoice.get("job_no", "-")
        customer_name = invoice.get("customer_name", "-")
        plate_number = invoice.get("plate_number", "-")
        final_total = invoice.get("final_total", 0)
        payment_status = invoice.get("payment_status", "pending")
        payment_method = invoice.get("payment_method", "cash")
        paid_date = invoice.get("paid_date", "")
        if paid_date:
            paid_date = paid_date[:10] if " " in paid_date else paid_date[:10]
        else:
            paid_date = "-"
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
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
        
        status_badge = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                ft.Text(status_texts.get(payment_status, payment_status), size=11, color=ft.Colors.WHITE),
            ], spacing=4),
            bgcolor=status_colors.get(payment_status, "#607D8B"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )
        
        view_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("view"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, iid=invoice_id: self.view_invoice_detail(iid),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        print_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT_OUTLINED, size=16, color=self.primary_color),
                ft.Text(get_text("print"), size=12, color=self.primary_color),
            ], spacing=4),
            on_click=lambda e, iid=invoice_id: self.print_invoice(iid),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(invoice_no, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=100,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(job_no, size=13, color="#1E293B"),
                    width=100,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(customer_name, size=13, color="#1E293B", max_lines=1),
                    width=130,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(plate_number, size=12, color="#64748B", max_lines=1),
                    width=100,
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(f"{int(final_total):,} KIP", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=status_badge,
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(method_texts.get(payment_method, payment_method), size=12, color="#64748B"),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(paid_date, size=12, color="#64748B"),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Row([view_btn, print_btn], spacing=4),
                    width=160,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=10),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    def update_pagination(self):
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_invoices)} {get_text('of')} {len(self.invoices)} {get_text('results')}",
                    size=12,
                    color="#64748B",
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_LEFT,
                            icon_size=20,
                            on_click=self.prev_page,
                            disabled=prev_disabled,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                        ft.Container(
                            content=ft.Text(f"{self.current_page}/{self.total_pages}", size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                            padding=ft.padding.symmetric(horizontal=15),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_RIGHT,
                            icon_size=20,
                            on_click=self.next_page,
                            disabled=next_disabled,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                    ]),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_invoices()
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_invoices()
    
    def view_invoice_detail(self, invoice_id: int):
        """View invoice detail - show dialog instead of navigate"""
        invoice = next((i for i in self.invoices if i.get("id") == invoice_id), None)
        if not invoice:
            self.show_snack_bar(get_text("invoice_not_found"), is_error=True)
            return
        
        self._show_invoice_detail_dialog(invoice)
    
    def print_invoice(self, invoice_id: int):
        """พิมพ์ใบเก็บเงินโดยใช้ backend PDF generator และเปิดด้วยโปรแกรม PDF ของระบบ"""
        try:
            self.show_snack_bar(get_text("preparing_print"), is_error=False)
            
            pdf_bytes = self.client.get_invoice_pdf(invoice_id)
            if not pdf_bytes:
                self.show_snack_bar(get_text("pdf_export_failed"), is_error=True)
                return
                
            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            invoice_no = f"INV-{invoice_id:04d}"
            pdf_path = os.path.join(output_dir, f"invoice_{invoice_no}.pdf")
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
                
            os.startfile(pdf_path)
            self.show_snack_bar(get_text("pdf_export_success"), is_error=False)
            
        except Exception as ex:
            print(f"Error printing invoice: {ex}")
            self.show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", is_error=True)

    def _show_invoice_detail_dialog(self, invoice: Dict):
        """Show invoice detail in dialog"""
        
        invoice_no = f"INV-{invoice.get('id', 0):04d}"
        job_no = invoice.get("job_no", "-")
        customer_name = invoice.get("customer_name", "-")
        customer_phone = invoice.get("customer_phone", "-")
        plate_number = invoice.get("plate_number", "-")
        brand = invoice.get("brand", "-")
        model = invoice.get("model", "-")
        total_amount = invoice.get("total_amount", 0)
        total_discount = invoice.get("total_discount", 0)
        final_total = invoice.get("final_total", 0)
        payment_method = invoice.get("payment_method", "cash")
        payment_status = invoice.get("payment_status", "pending")
        received_amount = invoice.get("received_amount", 0)
        change_amount = invoice.get("change_amount", 0)
        paid_date = invoice.get("paid_date", "")
        
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
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.RECEIPT, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            get_text("invoice_detail"),
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
                        content=ft.Column([
                            ft.Row([
                                ft.Text(get_text("invoice_no"), size=12, color="#64748B", width=100),
                                ft.Text(invoice_no, size=13, weight=ft.FontWeight.W_600, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("job_number"), size=12, color="#64748B", width=100),
                                ft.Text(job_no, size=13, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("customer_name"), size=12, color="#64748B", width=100),
                                ft.Text(customer_name, size=13, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("plate_number"), size=12, color="#64748B", width=100),
                                ft.Text(plate_number, size=13, weight=ft.FontWeight.W_600, color=self.primary_color, expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("payment_status"), size=12, color="#64748B", width=100),
                                ft.Container(
                                    content=ft.Text(status_texts.get(payment_status, payment_status), size=12, color=ft.Colors.WHITE),
                                    bgcolor=status_colors.get(payment_status, "#607D8B"),
                                    border_radius=12,
                                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                ),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("payment_method"), size=12, color="#64748B", width=100),
                                ft.Text(method_texts.get(payment_method, payment_method), size=13, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("paid_date"), size=12, color="#64748B", width=100),
                                ft.Text(paid_date, size=13, color="#1E293B", expand=True),
                            ], spacing=8),
                            ft.Divider(height=1, color=ft.Colors.GREY_200),
                            ft.Row([
                                ft.Text(get_text("total_amount"), size=13, weight=ft.FontWeight.W_500),
                                ft.Container(expand=True),
                                ft.Text(f"{int(total_amount):,} KIP", size=13, color="#64748B"),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("discount"), size=13, weight=ft.FontWeight.W_500),
                                ft.Container(expand=True),
                                ft.Text(f"-{int(total_discount):,} KIP", size=13, color=ft.Colors.RED_600),
                            ], spacing=8),
                            ft.Divider(height=1, color=ft.Colors.GREY_200),
                            ft.Row([
                                ft.Text(get_text("final_total"), size=15, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{int(final_total):,} KIP", size=15, weight=ft.FontWeight.BOLD, color=self.success_color),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("received_amount"), size=13, weight=ft.FontWeight.W_500),
                                ft.Container(expand=True),
                                ft.Text(f"{int(received_amount):,} KIP", size=13, color=self.success_color),
                            ], spacing=8),
                            ft.Row([
                                ft.Text(get_text("change_amount"), size=13, weight=ft.FontWeight.W_500),
                                ft.Container(expand=True),
                                ft.Text(f"{int(change_amount):,} KIP", size=13, color="#1E293B"),
                            ], spacing=8),
                        ], spacing=10),
                        padding=ft.padding.all(20),
                    ),
                ]),
                width=450,
            ),
            actions=[
                ft.TextButton(
                    get_text("close"),
                    on_click=lambda e: self._close_dialog(dialog),
                    style=ft.ButtonStyle(color="#64748B"),
                ),
                ft.ElevatedButton(
                    get_text("print"),
                    on_click=lambda e: self.print_invoice(invoice.get('id')),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
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