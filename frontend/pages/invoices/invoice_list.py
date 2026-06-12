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
        self.status_filter = None
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
    
    def _build_search_bar(self):
        self.status_filter = ft.Dropdown(
            hint_text=get_text("filter_by_status"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option("all", get_text("all_status")),
                ft.dropdown.Option("pending", get_text("status_pending")),
                ft.dropdown.Option("paid", get_text("status_paid")),
                ft.dropdown.Option("partial", get_text("status_partial")),
                ft.dropdown.Option("refunded", get_text("status_refunded")),
            ],
            value="all",
            expand=True,
        )
        
        self.status_filter.on_change = self.filter_invoices
        
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
        self.search_field.on_change = self.search_invoices
        
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
            content=ft.Row([self.status_filter, self.search_field, refresh_button], spacing=10),
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
    
    def filter_invoices(self, e):
        status = self.status_filter.value
        print(f"DEBUG: Filtering by status: {status}")
        
        if status and status != "all":
            self.filtered_invoices = [i for i in self.invoices if i.get("payment_status") == status]
        else:
            self.filtered_invoices = self.invoices.copy()
        
        print(f"DEBUG: Filtered {len(self.filtered_invoices)} invoices")
        self.current_page = 1
        self.display_invoices()
    
    def search_invoices(self, e):
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        print(f"DEBUG: Searching with keyword: {keyword}")
        
        if keyword:
            self.filtered_invoices = [
                i for i in self.invoices
                if keyword in f"INV-{i.get('id', 0):04d}".lower()
                or keyword in i.get("job_no", "").lower()
                or keyword in i.get("customer_name", "").lower()
                or keyword in i.get("plate_number", "").lower()
            ]
        else:
            self.filtered_invoices = self.invoices.copy()
        
        if self.status_filter.value != "all":
            self.filtered_invoices = [i for i in self.filtered_invoices if i.get("payment_status") == self.status_filter.value]
        
        print(f"DEBUG: Search found {len(self.filtered_invoices)} invoices")
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
        """Print invoice"""
        try:
            self.show_snack_bar(get_text("preparing_print"), is_error=False)
            
            invoice = next((i for i in self.invoices if i.get("id") == invoice_id), None)
            if not invoice:
                self.show_snack_bar(get_text("invoice_not_found"), is_error=True)
                return
            
            def generate_and_print():
                html_content = self._generate_print_html(invoice)
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                    f.write(html_content)
                    temp_path = f.name
                
                time.sleep(0.5)
                webbrowser.open(f'file://{temp_path}')
                
                def cleanup():
                    time.sleep(30)
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except:
                        pass
                
                threading.Thread(target=cleanup, daemon=True).start()
            
            threading.Thread(target=generate_and_print, daemon=True).start()
            
        except Exception as ex:
            print(f"Error printing: {ex}")
            self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
    
    def _generate_print_html(self, invoice: Dict) -> str:
        """Generate HTML for invoice printing"""
        
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
            try:
                dt = datetime.strptime(str(paid_date), "%Y-%m-%d %H:%M:%S")
                paid_date = dt.strftime("%d/%m/%Y %H:%M")
            except:
                paid_date = str(paid_date)[:10]
        else:
            paid_date = "-"
        
        method_texts = {
            "cash": "ເງິນສົດ",
            "transfer": "ໂອນເງິນ",
            "qr": "QR Code"
        }
        
        status_texts = {
            "pending": "ລໍຖ້າຊຳລະ",
            "paid": "ຊຳລະແລ້ວ",
            "partial": "ຊຳລະບາງສ່ວນ",
            "refunded": "ຄືນເງິນ"
        }
        
        shop_info = {}
        try:
            shop_info = self.client.get_shop()
        except:
            pass
        
        shop_name = shop_info.get('name', 'J&P Auto Maxing')
        shop_address = shop_info.get('address', 'Vientiane, Lao PDR')
        shop_phone = shop_info.get('phone', '020 92431434')
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invoice - {invoice_no}</title>
    <style>
        @media print {{
            body {{ margin: 0; padding: 0; }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans', 'DejaVu Sans', 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            padding: 20px;
            background: #e2e8f0;
        }}
        
        .invoice {{
            max-width: 400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .invoice-content {{
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            padding: 20px 20px 15px 20px;
            background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
            color: white;
        }}
        
        .shop-name {{
            font-size: 20px;
            font-weight: bold;
        }}
        
        .shop-address {{
            font-size: 10px;
            opacity: 0.9;
            margin-top: 4px;
        }}
        
        .shop-phone {{
            font-size: 11px;
            font-weight: bold;
            margin-top: 6px;
        }}
        
        .title {{
            font-size: 14px;
            font-weight: bold;
            margin-top: 10px;
            padding-top: 6px;
            border-top: 1px dashed rgba(255,255,255,0.3);
            display: inline-block;
        }}
        
        .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 11px;
            padding-bottom: 4px;
            border-bottom: 1px dotted #e2e8f0;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #475569;
            width: 110px;
        }}
        
        .info-value {{
            color: #1e293b;
            font-weight: 500;
            flex: 1;
            text-align: right;
        }}
        
        .divider {{
            height: 1px;
            background: repeating-linear-gradient(90deg, #cbd5e1, #cbd5e1 5px, transparent 5px, transparent 10px);
            margin: 10px 0;
        }}
        
        .total-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
        }}
        
        .total-label {{
            font-weight: bold;
        }}
        
        .total-amount {{
            font-weight: bold;
        }}
        
        .grand-total {{
            font-size: 16px;
            font-weight: bold;
            color: #1565C0;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #cbd5e1;
        }}
        
        .footer {{
            text-align: center;
            padding-top: 15px;
            margin-top: 15px;
            border-top: 1px dashed #cbd5e1;
            font-size: 9px;
            color: #94a3b8;
        }}
        
        .thankyou {{
            font-size: 11px;
            font-weight: bold;
            color: #1565C0;
            margin-bottom: 6px;
        }}
        
        .stamp {{
            margin-top: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 9px;
            color: #64748b;
        }}
        
        .signature {{
            border-top: 1px dotted #94a3b8;
            width: 120px;
            padding-top: 4px;
            text-align: center;
        }}
        
        .badge {{
            background: #f1f5f9;
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 8px;
            font-weight: bold;
            margin-bottom: 6px;
        }}
        
        .highlight {{
            font-weight: bold;
            color: #1565C0;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 9px;
            font-weight: bold;
            color: white;
        }}
        
        .status-paid {{
            background: #10B981;
        }}
        
        .status-pending {{
            background: #F59E0B;
        }}
    </style>
</head>
<body>
    <div class="invoice">
        <div class="header">
            <div class="shop-name">{shop_name}</div>
            <div class="shop-address">{shop_address}</div>
            <div class="shop-phone">📞 {shop_phone}</div>
            <div class="title">ໃບຮັບເງິນ / INVOICE</div>
        </div>
        
        <div class="invoice-content">
            <div style="text-align: center; margin-bottom: 12px;">
                <span class="badge">ເລກທີໃບຮັບເງິນ</span>
                <div style="font-size: 18px; font-weight: bold; color: #1565C0; margin-top: 4px;">{invoice_no}</div>
            </div>
            
            <div class="info-row">
                <span class="info-label">ວັນທີ</span>
                <span class="info-value">{paid_date}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">ເລກທີໃບຮັບລົດ</span>
                <span class="info-value">{job_no}</span>
            </div>
            
            <div class="divider"></div>
            
            <div class="info-row">
                <span class="info-label">ຊື່ລູກຄ້າ</span>
                <span class="info-value">{customer_name}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">ເບີໂທ</span>
                <span class="info-value">{customer_phone}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">ທະບຽນລົດ</span>
                <span class="info-value"><span class="highlight">{plate_number}</span></span>
            </div>
            
            <div class="info-row">
                <span class="info-label">ຍີ່ຫໍ້/ລຸ້ນ</span>
                <span class="info-value">{brand} {model}</span>
            </div>
            
            <div class="divider"></div>
            
            <div class="total-row">
                <span class="total-label">ລວມຍ່ອຍ</span>
                <span class="total-amount">{int(total_amount):,} KIP</span>
            </div>
            
            <div class="total-row">
                <span class="total-label">ສ່ວນຫຼຸດ</span>
                <span class="total-amount" style="color: #EF4444;">-{int(total_discount):,} KIP</span>
            </div>
            
            <div class="divider"></div>
            
            <div class="total-row grand-total">
                <span class="total-label">ລວມທັງໝົດ</span>
                <span class="total-amount">{int(final_total):,} KIP</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">ວິທີຈ່າຍ</span>
                <span class="info-value">{method_texts.get(payment_method, payment_method)}</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">ຮັບເງິນ</span>
                <span class="info-value">{int(received_amount):,} KIP</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">ເງິນທອນ</span>
                <span class="info-value">{int(change_amount):,} KIP</span>
            </div>
            
            <div class="info-row">
                <span class="info-label">ສະຖານະ</span>
                <span class="info-value">
                    <span class="status-badge {'status-paid' if payment_status == 'paid' else 'status-pending'}">
                        {status_texts.get(payment_status, payment_status)}
                    </span>
                </span>
            </div>
            
            <div class="stamp">
                <div class="signature">ລາຍເຊັນລູກຄ້າ</div>
                <div class="signature">ລາຍເຊັນຮ້ານ</div>
            </div>
            
            <div class="footer">
                <div class="thankyou">ຂອບໃຈທີ່ໄວ້ໃຈບໍລິການຂອງພວກເຮົາ</div>
                <div>ສອບຖາມເພີ່ມເຕີມ: {shop_phone}</div>
                <div class="date-text">ພິມເມື່ອ: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
            </div>
        </div>
    </div>
    
    <script>
        window.onload = function() {{
            setTimeout(function() {{
                window.print();
            }}, 300);
        }}
    </script>
</body>
</html>"""
        
        return html_content
    
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