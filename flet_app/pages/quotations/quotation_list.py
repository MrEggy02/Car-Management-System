# pages/quotations/quotation_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import tempfile
import os
from datetime import datetime

from i18n import get_text


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

    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    
                    ft.Column(
                        [
                            ft.Text(
                                get_text("quotation_list"),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("quotation_list_subtitle"),
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
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
                        on_click=lambda e: self.navigate("quotation_create", job_order_id=self.job_order_id),
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
            padding=ft.padding.symmetric(vertical=20, horizontal=32),
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
                    on_click=lambda e: self.navigate("quotation_create", job_order_id=self.job_order_id),
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
        
        return main_content
    
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
        
        # Row background color (alternate)
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
        
        # Status badge with click to change
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
        
        # Action buttons
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
            on_click=lambda e, qid=quote_id: self.print_quotation_pdf(qid),
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
    
    def show_update_status_dialog(self, quotation_id: int, current_status: str):
        """Show dialog to update quotation status"""
        
        status_dropdown = ft.Dropdown(
            label=get_text("select_status"),
            value=current_status,
            options=[
                ft.dropdown.Option("draft", get_text("draft")),
                ft.dropdown.Option("approved", get_text("approved")),
                ft.dropdown.Option("rejected", get_text("rejected")),
            ],
            width=250,
            border_radius=12,
        )
        
        def update_status(e):
            new_status = status_dropdown.value
            if new_status and new_status != current_status:
                try:
                    self.client.update_quotation_status(quotation_id, new_status)
                    self.close_dialog(dialog)
                    self.load_quotations()
                    self.show_snack_bar(f"✅ {get_text('status_updated_to')} {get_text(new_status)}", is_error=False)
                except Exception as ex:
                    self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
            else:
                dialog.open = False
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(
                            get_text("update_quotation_status"),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"{get_text('current_status')}: {get_text(current_status)}", size=14, color="#64748B"),
                    ft.Container(height=16),
                    status_dropdown,
                ]),
                padding=ft.padding.all(24),
                width=350,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("update"), on_click=update_status, style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
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
        
        # Calculate pagination
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
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_quotations()
    
    def next_page(self, e=None):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_quotations()
    
    def delete_quotation(self, quotation_id: int):
        """Delete quotation with confirmation"""
        quote = next((q for q in self.quotations if q.get("id") == quotation_id), None)
        quote_name = f"QT-{quotation_id:04d}" if quote else get_text("this_quotation")
        
        def confirm(e):
            try:
                self.client.delete_quotation(quotation_id)
                self.close_dialog(dialog)
                self.load_quotations()
                self.show_snack_bar(f"✅ {get_text('delete_success')}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, size=28, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.RED_600,
                            border_radius=14,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column(
                            [
                                ft.Text(get_text("confirm"), size=20, weight=ft.FontWeight.BOLD, color="#1E293B"),
                                ft.Text(get_text("delete_warning"), size=13, color="#64748B"),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(ft.Icons.DELETE_OUTLINE, size=56, color=ft.Colors.RED_600),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(height=8),
                    ft.Text(f"ຕ້ອງການລຶບ '{quote_name}' ຫຼືບໍ່?", size=16, weight=ft.FontWeight.W_500, color="#1E293B", text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                padding=ft.padding.all(32),
                width=400,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("delete"), on_click=confirm, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def print_quotation_pdf(self, quotation_id: int):
        """Print quotation as PDF (opens print dialog)"""
        self.loading_indicator.visible = True
        self.page.update()
        
        try:
            quotation = self.client.get_quotation(quotation_id)
            if quotation:
                html_content = self._generate_quotation_html(quotation)
                
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
                temp_file.write(html_content)
                temp_file.close()
                
                import webbrowser
                webbrowser.open(f'file://{temp_file.name}')
                
                self.show_snack_bar(get_text("print_dialog_opened"), is_error=False)
            else:
                self.show_snack_bar(get_text("error_loading_quotation"), is_error=True)
        except Exception as ex:
            print(f"Error printing: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        finally:
            self.loading_indicator.visible = False
            self.page.update()
    
    def _generate_quotation_html(self, quotation: Dict) -> str:
        """Generate HTML for printing"""
        items = quotation.get("items", [])
        
        items_html = ""
        for item in items:
            items_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">
                    {"🛞" if item.get("item_type") == "part" else "🔧"}
                </td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{item.get("name", "-")}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: center;">{item.get("qty", 1)}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;">{int(item.get("unit_price", 0)):,}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;">{int(item.get("discount_amount", 0)):,}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; text-align: right;"><strong>{int(item.get("total", 0)):,}</strong></td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Quotation #{quotation.get('id')}</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Saysettha OT', 'Noto Sans Lao', 'Segoe UI', Arial, sans-serif;
                    padding: 40px;
                    background: #f1f5f9;
                }}
                .invoice {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{ font-size: 28px; margin-bottom: 5px; }}
                .header p {{ opacity: 0.9; font-size: 14px; }}
                .content {{ padding: 30px; }}
                .info-section {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e2e8f0;
                }}
                .info-box {{
                    background: #f8fafc;
                    padding: 15px;
                    border-radius: 12px;
                }}
                .info-box h3 {{ font-size: 13px; color: #64748B; margin-bottom: 8px; }}
                .info-box p {{ font-size: 16px; font-weight: bold; color: #1E293B; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th {{
                    background: #f1f5f9;
                    padding: 12px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: bold;
                    color: #475569;
                    border-bottom: 2px solid #e2e8f0;
                }}
                td {{ vertical-align: top; }}
                .total-section {{
                    text-align: right;
                    padding-top: 20px;
                    border-top: 2px solid #e2e8f0;
                }}
                .total-row {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 10px;
                }}
                .total-amount {{
                    color: #1565C0;
                    font-size: 24px;
                }}
                .footer {{
                    background: #f8fafc;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #64748B;
                    border-top: 1px solid #e2e8f0;
                }}
                .status {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .status-draft {{ background: #FFF3E0; color: #FF9800; }}
                .status-approved {{ background: #E8F5E9; color: #4CAF50; }}
                .status-rejected {{ background: #FFEBEE; color: #F44336; }}
                @media print {{
                    body {{ background: white; padding: 0; }}
                    .invoice {{ box-shadow: none; }}
                    .no-print {{ display: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="invoice">
                <div class="header">
                    <h1>J&P Auto Maxing</h1>
                    <p>ໃບສະເໜີລາຄາ / QUOTATION</p>
                </div>
                <div class="content">
                    <div class="info-section">
                        <div class="info-box">
                            <h3>📄 ເລກທີ່ / NO.</h3>
                            <p>QT-{quotation.get('id', 'N/A'):04d}</p>
                        </div>
                        <div class="info-box">
                            <h3>📅 ວັນທີ / DATE</h3>
                            <p>{datetime.now().strftime('%d/%m/%Y')}</p>
                        </div>
                        <div class="info-box">
                            <h3>🔖 ສະຖານະ / STATUS</h3>
                            <p><span class="status status-{quotation.get('status', 'draft')}">{quotation.get('status', 'draft').upper()}</span></p>
                        </div>
                        <div class="info-box">
                            <h3>👤 ລູກຄ້າ / CUSTOMER</h3>
                            <p>{quotation.get('customer_name', '-')}</p>
                            <p style="font-size: 12px; font-weight: normal;">📞 {quotation.get('customer_phone', '-')}</p>
                        </div>
                        <div class="info-box">
                            <h3>🚗 ລົດ / VEHICLE</h3>
                            <p>{quotation.get('plate_number', '-')}</p>
                            <p style="font-size: 12px; font-weight: normal;">{quotation.get('brand', '')} {quotation.get('model', '')}</p>
                        </div>
                        <div class="info-box">
                            <h3>🔧 ໃບຮັບລົດ / JOB NO.</h3>
                            <p>{quotation.get('job_no', '-')}</p>
                        </div>
                    </div>
                    
                    <table>
                        <thead>
                            <tr>
                                <th></th>
                                <th>ລາຍການ / ITEM</th>
                                <th style="text-align: center;">ຈຳນວນ / QTY</th>
                                <th style="text-align: right;">ລາຄາ / PRICE (KIP)</th>
                                <th style="text-align: right;">ສ່ວນຫຼຸດ / DISCOUNT</th>
                                <th style="text-align: right;">ລວມ / TOTAL (KIP)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html if items_html else '<tr><td colspan="6" style="text-align: center; padding: 40px;">ບໍ່ມີລາຍການ / No items</td></tr>'}
                        </tbody>
                    </table>
                    
                    <div class="total-section">
                        <div class="total-row">
                            ລວມທັງໝົດ / TOTAL: 
                            <span class="total-amount">{int(quotation.get('total_price', 0)):,} KIP</span>
                        </div>
                    </div>
                </div>
                <div class="footer">
                    <p>ຂອບໃຈທີ່ໃຊ້ບໍລິການຂອງພວກເຮົາ</p>
                    <p>J&P Auto Maxing - ສູນບໍລິການລົດ ແລະ ອາໄຫຼ່ຄົບວົງຈອນ</p>
                </div>
            </div>
            <div class="no-print" style="text-align: center; margin-top: 20px;">
                <button onclick="window.print()" style="padding: 10px 30px; background: #1565C0; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer;">🖨️ ພິມ / PRINT</button>
            </div>
            <script>
                window.print();
            </script>
        </body>
        </html>
        """
        return html
    
    def show_quotation_detail(self, quotation_id: int):
        """Show detailed quotation in a scrollable dialog"""
        self.loading_indicator.visible = True
        self.page.update()
        
        try:
            quotation = self.client.get_quotation(quotation_id)
            self.loading_indicator.visible = False
            
            if quotation:
                items = quotation.get("items", [])
                
                items_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
                
                if not items:
                    items_column.controls.append(
                        ft.Container(
                            content=ft.Text(get_text("no_items"), size=14, color="#64748B"),
                            padding=ft.padding.all(20),
                            alignment=Alignment.CENTER,
                        )
                    )
                else:
                    for item in items:
                        item_type = item.get("item_type")
                        name = item.get("name", "-")
                        qty = item.get("qty", 1)
                        unit_price = item.get("unit_price", 0)
                        discount = item.get("discount_amount", 0)
                        item_total = item.get("total", 0)
                        
                        item_row = ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    content=ft.Icon(ft.Icons.INVENTORY if item_type == "part" else ft.Icons.BUILD, 
                                                   size=20, color=self.primary_color),
                                    width=32,
                                ),
                                ft.Column([
                                    ft.Text(name, size=14, weight=ft.FontWeight.W_500),
                                    ft.Text(f"{get_text('qty')}: {qty} x {int(unit_price):,} KIP", size=11, color="#64748B"),
                                    ft.Text(f"{get_text('discount')}: {int(discount):,} KIP", size=11, color=ft.Colors.RED_600) if discount > 0 else ft.Container(),
                                ], spacing=2, expand=True),
                                ft.Text(f"{int(item_total):,} KIP", size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=ft.padding.symmetric(vertical=8, horizontal=12),
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                        )
                        items_column.controls.append(item_row)
                
                scrollable_content = ft.Column(
                    [
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.REQUEST_QUOTE, size=28, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=12,
                                padding=ft.padding.all(10),
                            ),
                            ft.Column([
                                ft.Text(f"{get_text('quotation')} #{quotation.get('id')}", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{get_text('status')}: {quotation.get('status', 'draft')}", size=12, color="#64748B"),
                            ], spacing=2),
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Column([
                                ft.Text(get_text("job_number"), size=12, color="#64748B"),
                                ft.Text(quotation.get("job_no", "-"), size=14, weight=ft.FontWeight.W_500),
                            ], expand=True),
                            ft.Column([
                                ft.Text(get_text("customer_name"), size=12, color="#64748B"),
                                ft.Text(quotation.get("customer_name", "-"), size=14, weight=ft.FontWeight.W_500),
                            ], expand=True),
                        ]),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Column([
                                ft.Text(get_text("plate_number"), size=12, color="#64748B"),
                                ft.Text(quotation.get("plate_number", "-"), size=14, weight=ft.FontWeight.W_500),
                            ], expand=True),
                            ft.Column([
                                ft.Text(get_text("created_date"), size=12, color="#64748B"),
                                ft.Text(quotation.get("created_at", "-")[:10] if quotation.get("created_at") else "-", size=14, weight=ft.FontWeight.W_500),
                            ], expand=True),
                        ]),
                        ft.Container(height=12),
                        ft.Text(get_text("items"), size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(height=8),
                        ft.Container(
                            content=items_column,
                            height=250,
                            border=ft.border.all(1, ft.Colors.GREY_200),
                            border_radius=8,
                            padding=ft.padding.all(8),
                        ),
                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Text(get_text("total"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                            ft.Text(f"{int(quotation.get('total_price', 0)):,} KIP", size=20, weight=ft.FontWeight.BOLD, color=self.primary_color),
                        ]),
                    ],
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
                
                dialog_content = ft.Container(
                    content=scrollable_content,
                    width=600,
                    height=550,
                    padding=ft.padding.all(20),
                )
                
                dialog = ft.AlertDialog(
                    modal=True,
                    shape=ft.RoundedRectangleBorder(radius=20),
                    bgcolor=ft.Colors.WHITE,
                    title=ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.INFO, size=24, color=ft.Colors.WHITE),
                                    bgcolor=self.primary_color,
                                    border_radius=12,
                                    padding=ft.padding.all(8),
                                ),
                                ft.Text(
                                    get_text("quotation_details"),
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1E293B",
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.all(20),
                        border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                    ),
                    content=dialog_content,
                    actions=[
                        ft.TextButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
                                ft.Text(get_text("close"), size=14, color="#64748B"),
                            ], spacing=6),
                            on_click=lambda e: self.close_dialog(dialog),
                        ),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.PRINT, size=18, color=ft.Colors.WHITE),
                                ft.Text(get_text("print"), size=14, color=ft.Colors.WHITE),
                            ], spacing=6),
                            on_click=lambda e, qid=quotation_id: self.print_quotation_pdf(qid),
                            style=ft.ButtonStyle(bgcolor=self.primary_color),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                self.page.overlay.append(dialog)
                dialog.open = True
                self.page.update()
            else:
                self.show_snack_bar(get_text("error_loading_quotation"), is_error=True)
        except Exception as ex:
            self.loading_indicator.visible = False
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
            self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()
    
    def print_quotation(self, quotation_id: int):
        self.print_quotation_pdf(quotation_id)