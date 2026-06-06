# pages/quotations/quotation_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import tempfile
import os
import webbrowser
import threading
import time
from datetime import datetime

from i18n import get_text, get_current_language
from pages.quotations.quotation_dialogs import (
    show_create_quotation_dialog,
    show_quotation_detail_dialog,
    show_update_status_dialog,
    show_delete_quotation_dialog
)


class QuotationListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, job_order_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.job_order_id = job_order_id
        self.quotations = []
        self.filtered_quotations = []
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.selected_quotation = None
        self.detail_dialog = None
        self.search_field = None
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.current_dialog = None
        self.parts_list = []
        self.services_list = []

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("quotation_list"),
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
                            ft.Text(get_text("new_quotation"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.show_create_quotation_dialog(),
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
            padding=ft.padding.symmetric(vertical=14, horizontal=26),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
        
        # Search bar
        self.search_field = ft.TextField(
            hint_text=get_text("search_quotation"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            on_change=self.filter_quotations,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_quotations(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        # Create table header
        table_header = self._create_table_header()
        
        # Table rows container (scrollable)
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Table container
        table_container = ft.Container(
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
        
        # Pagination container
        self.pagination_container = ft.Container(
            padding=ft.padding.symmetric(vertical=12, horizontal=20),
            bgcolor="#F5F7FA",
        )
        
        # Loading indicator
        self.loading_indicator = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=4),
                ft.Container(height=16),
                ft.Text(get_text("loading"), size=14, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=Alignment.CENTER,
            padding=ft.padding.all(40),
            visible=False,
        )
        
        # Empty state
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.REQUEST_QUOTE, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=16),
                ft.Text(get_text("no_quotations_found"), size=18, weight=ft.FontWeight.W_500, color="#64748B"),
                ft.Text(get_text("click_add_to_register"), size=13, color="#94A3B8"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text(get_text("new_quotation"), size=14),
                    on_click=lambda e: self.show_create_quotation_dialog(),
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=Alignment.CENTER,
            padding=ft.padding.all(60),
            visible=False,
        )
        
        # Main content area
        content_area = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([self.search_field, refresh_button], spacing=10),
                    margin=ft.margin.only(bottom=16),
                ),
                table_container,
                self.pagination_container,
                self.loading_indicator,
                self.empty_state,
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
        
        self.load_quotations()
        self.load_parts_and_services()
        
        return main_content
    
    def load_parts_and_services(self):
        """Load parts and services for quotation creation"""
        try:
            self.parts_list = self.client.get_parts()
            self.services_list = self.client.get_services()
        except Exception as ex:
            print(f"Error loading parts/services: {ex}")
            self.parts_list = []
            self.services_list = []
    
    def _create_table_header(self):
        """Create table header row"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("quotation_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("customer_name"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("plate_number"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("total"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("actions"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=180,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=14, horizontal=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _create_table_row(self, quote: Dict, index: int):
        """Create a table row"""
        quote_id = quote.get("id")
        customer_name = quote.get("customer_name", "-")
        plate_number = quote.get("plate_number", "-")
        total_price = quote.get("total_price", 0)
        status = quote.get("status", "draft")
        created_at = quote.get("created_at", "").split()[0] if quote.get("created_at") else "-"
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        status_colors = {
            "draft": "#FF9800",
            "approved": "#4CAF50",
            "rejected": "#F44336"
        }
        status_texts = {
            "draft": get_text("draft"),
            "approved": get_text("approved"),
            "rejected": get_text("rejected")
        }
        
        status_badge = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                ft.Text(status_texts.get(status, status), size=11, color=ft.Colors.WHITE),
                ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=ft.Colors.WHITE),
            ], spacing=4),
            bgcolor=status_colors.get(status, "#607D8B"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            on_click=lambda e, qid=quote_id, cur_status=status: self.show_update_status_dialog(qid, cur_status),
        )
        
        view_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("view"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, qid=quote_id: self.show_quotation_detail(qid),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        print_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("print"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, qid=quote_id: self.print_quotation(qid),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        delete_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
                ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
            ], spacing=4),
            on_click=lambda e, qid=quote_id: self.delete_quotation(qid),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(f"QT-{quote_id:04d}", size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(customer_name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(plate_number, size=12, color="#64748B", max_lines=1),
                    width=120,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(f"{int(total_price):,} KIP", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=status_badge,
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(created_at, size=12, color="#64748B"),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Row([view_btn, print_btn, delete_btn], spacing=4),
                    width=180,
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
    
    def load_quotations(self):
        """Load quotations from API"""
        self.loading_indicator.visible = True
        self.empty_state.visible = False
        self.table_rows.controls.clear()
        self.page.update()
        
        try:
            quotations = self.client.get_quotations(job_order_id=self.job_order_id)
            self.quotations = quotations
            self.filtered_quotations = quotations.copy()
            self.display_quotations()
        except Exception as ex:
            print(f"Error loading quotations: {ex}")
            self.loading_indicator.visible = False
            self.page.update()
    
    def filter_quotations(self, e):
        """Filter quotations by search keyword"""
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        self.current_page = 1
        
        if not keyword:
            self.filtered_quotations = self.quotations.copy()
        else:
            self.filtered_quotations = [
                q for q in self.quotations
                if keyword in f"QT-{q.get('id', 0):04d}".lower()
                or keyword in q.get("customer_name", "").lower()
                or keyword in q.get("plate_number", "").lower()
                or keyword in q.get("job_no", "").lower()
            ]
        
        self.display_quotations()
    
    def display_quotations(self):
        """Display quotations with pagination"""
        self.table_rows.controls.clear()
        
        total_items = len(self.filtered_quotations)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_quotations[start_idx:end_idx]
        
        if page_items and len(page_items) > 0:
            self.loading_indicator.visible = False
            self.empty_state.visible = False
            for i, quote in enumerate(page_items):
                self.table_rows.controls.append(self._create_table_row(quote, start_idx + i))
        else:
            self.loading_indicator.visible = False
            self.empty_state.visible = True
        
        self.update_pagination_controls()
        self.page.update()
    
    def update_pagination_controls(self):
        """Update pagination controls"""
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_quotations)} {get_text('of')} {len(self.quotations)} {get_text('results')}",
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
            self.display_quotations()
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_quotations()
    
    def show_create_quotation_dialog(self, e=None):
        """Show dialog to create new quotation"""
        
        # Load job orders
        try:
            all_orders = self.client.get_job_orders()
            pending_orders = [o for o in all_orders if o.get('status') in ['pending', 'quoting']]
        except Exception as ex:
            print(f"Error loading job orders: {ex}")
            pending_orders = []
        
        if not pending_orders:
            self.show_snack_bar(get_text("no_pending_job_orders"), is_error=True)
            return
        
        def on_save(job_order_id, items):
            try:
                result = self.client.create_quotation(job_order_id)
                if result:
                    quotation_id = result.get("id")
                    for item in items:
                        self.client.add_quotation_item(
                            quotation_id, 
                            item["item_type"], 
                            item["ref_id"], 
                            item["qty"]
                        )
                    self.client.calculate_quotation_total(quotation_id)
                    self._close_dialog()
                    self.load_quotations()
                    self.show_snack_bar(f"✅ {get_text('quotation_created_successfully')}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
        
        def on_approve(job_order_id, items):
            try:
                result = self.client.create_quotation(job_order_id)
                if result:
                    quotation_id = result.get("id")
                    for item in items:
                        self.client.add_quotation_item(
                            quotation_id, 
                            item["item_type"], 
                            item["ref_id"], 
                            item["qty"]
                        )
                    self.client.calculate_quotation_total(quotation_id)
                    self.client.update_quotation_status(quotation_id, "approved")
                    self._close_dialog()
                    self.load_quotations()
                    self.show_snack_bar(f"✅ {get_text('quotation_approved_successfully')}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
        
        dialog = show_create_quotation_dialog(
            self.primary_color,
            self.parts_list,
            self.services_list,
            pending_orders,
            on_save,
            on_approve,
            self._close_dialog
        )
        self._open_dialog(dialog)
    
    def show_quotation_detail(self, quotation_id: int):
        """Show detailed quotation in a scrollable dialog"""
        self.loading_indicator.visible = True
        self.page.update()
        
        try:
            quotation = self.client.get_quotation(quotation_id)
            self.loading_indicator.visible = False
            
            if quotation:
                def on_print(qid):
                    self.print_quotation(qid)
                
                dialog = show_quotation_detail_dialog(
                    quotation,
                    self.primary_color,
                    on_print,
                    self._close_dialog
                )
                self._open_dialog(dialog)
            else:
                self.show_snack_bar(get_text("error_loading_quotation"), is_error=True)
        except Exception as ex:
            self.loading_indicator.visible = False
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
            self.page.update()
    
    def show_update_status_dialog(self, quotation_id: int, current_status: str):
        """Show dialog to update quotation status"""
        
        def on_update(qid, new_status):
            try:
                self.client.update_quotation_status(qid, new_status)
                self._close_dialog()
                self.load_quotations()
                self.show_snack_bar(f"✅ {get_text('status_updated_to')} {get_text(new_status)}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = show_update_status_dialog(
            quotation_id,
            current_status,
            self.primary_color,
            on_update,
            self._close_dialog
        )
        self._open_dialog(dialog)
    
    def delete_quotation(self, quotation_id: int):
        """Delete quotation with confirmation"""
        quote = next((q for q in self.quotations if q.get("id") == quotation_id), None)
        quote_name = f"QT-{quotation_id:04d}" if quote else get_text("this_quotation")
        
        def on_confirm():
            try:
                self.client.delete_quotation(quotation_id)
                self._close_dialog()
                self.load_quotations()
                self.show_snack_bar(f"✅ {get_text('delete_success')}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = show_delete_quotation_dialog(
            quote_name,
            on_confirm,
            self._close_dialog
        )
        self._open_dialog(dialog)
    
    def print_quotation(self, quotation_id: int):
        """Print quotation using browser print dialog"""
        try:
            self.show_snack_bar(get_text("preparing_print"), is_error=False)
            
            def generate_and_print():
                quotation = self.client.get_quotation(quotation_id)
                if quotation:
                    html_content = self._generate_print_html(quotation)
                    
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
                else:
                    self.show_snack_bar(get_text("error_loading_quotation"), is_error=True)
            
            threading.Thread(target=generate_and_print, daemon=True).start()
            
        except Exception as ex:
            print(f"Error printing: {ex}")
            self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
    
    def _generate_print_html(self, quotation: Dict) -> str:
        """Generate professional quotation HTML for printing"""
        
        items = quotation.get("items", [])
        shop_info = {}
        try:
            shop_info = self.client.get_shop()
        except:
            pass
        
        shop_name = shop_info.get('name', 'J&P Auto Maxing')
        shop_address = shop_info.get('address', 'Vientiane, Lao PDR')
        shop_phone = shop_info.get('phone', '020 92431434')
        
        quotation_no = f"QT-{quotation.get('id', 0):04d}"
        created_date = quotation.get("created_at", "")
        if created_date:
            try:
                dt = datetime.strptime(str(created_date), "%Y-%m-%d %H:%M:%S")
                created_date = dt.strftime("%d/%m/%Y")
            except:
                created_date = str(created_date)[:10]
        else:
            created_date = datetime.now().strftime("%d/%m/%Y")
        
        items_html = ""
        for item in items:
            item_type = item.get("item_type", "part")
            name = item.get("name", "-")
            qty = item.get("qty", 1)
            unit_price = item.get("unit_price", 0)
            discount = item.get("discount_amount", 0)
            total = item.get("total", qty * unit_price)
            
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: center;">
                    {"🛞" if item_type == "part" else "🔧"}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{name}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: center;">{qty}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right;">{int(unit_price):,}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right;">{int(discount):,}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right;"><strong>{int(total):,}</strong></td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Quotation - {quotation_no}</title>
            <style>
                @media print {{ body {{ margin: 0; padding: 0; }} }}
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Noto Sans', 'DejaVu Sans', 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                    padding: 30px;
                    background: #f1f5f9;
                }}
                .quotation {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
                    color: white;
                    padding: 25px 30px;
                    text-align: center;
                }}
                .shop-name {{ font-size: 24px; font-weight: bold; letter-spacing: 1px; }}
                .shop-address {{ font-size: 11px; opacity: 0.9; margin-top: 5px; }}
                .shop-phone {{ font-size: 12px; font-weight: bold; margin-top: 5px; }}
                .quotation-title {{
                    font-size: 14px;
                    letter-spacing: 3px;
                    margin-top: 12px;
                    padding-top: 8px;
                    border-top: 1px dashed rgba(255,255,255,0.3);
                    display: inline-block;
                }}
                .content {{ padding: 30px; }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 15px;
                    margin-bottom: 25px;
                }}
                .info-box {{
                    background: #f8fafc;
                    padding: 12px 15px;
                    border-radius: 10px;
                }}
                .info-label {{ font-size: 10px; color: #64748B; text-transform: uppercase; margin-bottom: 4px; }}
                .info-value {{ font-size: 14px; font-weight: bold; color: #1E293B; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{
                    background: #f1f5f9;
                    padding: 12px;
                    text-align: left;
                    font-size: 11px;
                    font-weight: bold;
                    color: #475569;
                    border-bottom: 2px solid #e2e8f0;
                }}
                td {{ vertical-align: top; }}
                .total-section {{ text-align: right; margin-top: 20px; padding-top: 15px; border-top: 2px solid #e2e8f0; }}
                .total-row {{ font-size: 16px; font-weight: bold; margin-bottom: 5px; }}
                .grand-total {{ font-size: 22px; font-weight: bold; color: #1565C0; }}
                .footer {{
                    background: #f8fafc;
                    padding: 15px;
                    text-align: center;
                    font-size: 10px;
                    color: #64748B;
                    border-top: 1px solid #e2e8f0;
                }}
                .stamp {{ margin-top: 20px; display: flex; justify-content: space-between; padding: 0 20px; }}
                .signature {{
                    border-top: 1px solid #cbd5e1;
                    width: 150px;
                    padding-top: 5px;
                    text-align: center;
                    font-size: 9px;
                    color: #64748B;
                }}
                .barcode {{
                    height: 25px;
                    background: repeating-linear-gradient(90deg, #000, #000 2px, transparent 2px, transparent 8px);
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="quotation">
                <div class="header">
                    <div class="shop-name">{shop_name}</div>
                    <div class="shop-address">{shop_address}</div>
                    <div class="shop-phone">📞 {shop_phone}</div>
                    <div class="quotation-title">ໃບສະເໜີລາຄາ / QUOTATION</div>
                </div>
                
                <div class="content">
                    <div class="info-grid">
                        <div class="info-box"><div class="info-label">📄 ເລກທີ່ / NO.</div><div class="info-value">{quotation_no}</div></div>
                        <div class="info-box"><div class="info-label">📅 ວັນທີ / DATE</div><div class="info-value">{created_date}</div></div>
                        <div class="info-box"><div class="info-label">🔖 ສະຖານະ / STATUS</div><div class="info-value">{quotation.get('status', 'DRAFT').upper()}</div></div>
                        <div class="info-box"><div class="info-label">👤 ລູກຄ້າ / CUSTOMER</div><div class="info-value">{quotation.get('customer_name', '-')}</div><div style="font-size: 11px;">📞 {quotation.get('customer_phone', '-')}</div></div>
                        <div class="info-box"><div class="info-label">🚗 ລົດ / VEHICLE</div><div class="info-value">{quotation.get('plate_number', '-')}</div><div style="font-size: 11px;">{quotation.get('brand', '')} {quotation.get('model', '')}</div></div>
                        <div class="info-box"><div class="info-label">🔧 ໃບຮັບລົດ / JOB NO.</div><div class="info-value">{quotation.get('job_no', '-')}</div></div>
                    </div>
                    
                    <div class="barcode"></div>
                    
                    <table>
                        <thead><tr><th style="width: 40px;">#</th><th>ລາຍການ / ITEM</th><th style="width: 60px; text-align: center;">ຈຳນວນ</th><th style="width: 100px; text-align: right;">ລາຄາ (KIP)</th><th style="width: 100px; text-align: right;">ສ່ວນຫຼຸດ</th><th style="width: 110px; text-align: right;">ລວມ (KIP)</th></tr></thead>
                        <tbody>{items_html if items_html else '<tr><td colspan="6" style="text-align: center; padding: 40px;">ບໍ່ມີລາຍການ / No items</td></tr>'}</tbody>
                    能有
                    
                    <div class="total-section"><div class="total-row">ລວມທັງໝົດ / TOTAL: <span class="grand-total">{int(quotation.get('total_price', 0)):,} KIP</span></div></div>
                    
                    <div class="stamp"><div class="signature">ລາຍເຊັນລູກຄ້າ</div><div class="signature">ລາຍເຊັນຜູ້ຂາຍ</div></div>
                </div>
                
                <div class="footer">
                    <p>ຂອບໃຈທີ່ໄວ້ໃຈບໍລິການຂອງພວກເຮົາ</p>
                    <p>J&P Auto Maxing - ສູນບໍລິການລົດ ແລະ ອາໄຫຼ່ຄົບວົງຈອນ</p>
                    <p style="margin-top: 8px;">{shop_phone} | {shop_address}</p>
                </div>
            </div>
            <script>window.onload = function() {{ setTimeout(function() {{ window.print(); }}, 200); }}</script>
        </body>
        </html>
        """
        return html
    
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
    
    def _close_dialog(self, dialog=None):
        try:
            if dialog:
                dialog.open = False
            elif self.current_dialog:
                self.current_dialog.open = False
            self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=2000,
        )
        self.page.update()