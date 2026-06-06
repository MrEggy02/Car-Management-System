import flet as ft
import sys
import os
import asyncio
import traceback
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import get_text

class PromotionsContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.is_loading = False
        self.current_dialog = None
        self.promotions_data = []
        self.filtered_promotions = []
        self.search_input = None
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
        # Table data rows container
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.pagination_container = ft.Container()
        
        # Cache for items
        self.promotion_items_cache = {}
    
    def build(self):
        """Build promotions management content"""
        
        # Beautiful gradient header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("promotions_title"), 
                                size=18, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.WHITE
                            ),
                            
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("add"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.show_add_dialog(e),
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
        
        # Search Bar
        self.search_input = ft.TextField(
            hint_text=f" {get_text('search')} {get_text('promotions_title')}...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            on_change=self.filter_promotions,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        search_container = ft.Container(
            content=self.search_input,
            expand=True,
        )
        
        control_bar = ft.Container(
            content=search_container,
            padding=ft.padding.all(20),
            bgcolor="#F5F7FA",
        )
        
        # Table Header
        table_header = self._create_table_header()
        
        table_scroll_container = ft.Container(
            content=self.table_rows,
            expand=True,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            bgcolor=ft.Colors.WHITE,
        )
        
        table_container = ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                table_scroll_container,
            ], spacing=0),
            margin=ft.margin.only(left=20, right=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(
                top_left=12, top_right=12, bottom_left=12, bottom_right=12
            ),
            border=ft.border.all(1, ft.Colors.GREY_200),
            expand=True,
        )
        
        self.update_pagination_controls()
        
        main_content = ft.Container(
            content=ft.Column([
                table_container,
                self.pagination_container,
            ], spacing=0),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        main_container = ft.Container(
            content=main_content,
            expand=True,
        )
        
        self.page.run_task(self._delayed_load)
        
        return ft.Column([
            header,
            control_bar,
            main_container,
        ], expand=True, spacing=0)
    
    def _create_table_header(self):
        """Create table header row"""
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=50, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('promo_name'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=200, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=10)),
                ft.Container(content=ft.Text(get_text('discount_type'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=120, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=10)),
                ft.Container(content=ft.Text(get_text('discount_value'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=130, alignment=ft.Alignment(1, 0), padding=ft.padding.only(right=10)),
                ft.Container(content=ft.Text(get_text('period'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=180, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('status'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('actions'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=180, alignment=ft.Alignment(0, 0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=14, horizontal=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _format_discount(self, discount_type, value):
        """Format discount display"""
        if discount_type == 'percent':
            return f"{int(value)}%"
        else:
            return f"{int(value):,} KIP"
    
    def _format_date(self, date_str):
        """Format date string"""
        if not date_str:
            return "-"
        try:
            if isinstance(date_str, datetime):
                return date_str.strftime('%d/%m/%Y')
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except:
            return str(date_str)[:10]
    
    def _get_status_badge(self, status, start_date, end_date):
        """Get status badge with color"""
        # Check if expired
        try:
            today = datetime.now().date()
            if end_date:
                end = datetime.strptime(str(end_date), '%Y-%m-%d').date()
                if end < today:
                    status = 'inactive'
        except:
            pass
        
        if status == 'active':
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("status_active"), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        else:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CANCEL, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("status_inactive"), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=ft.Colors.RED_500,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
            )
    
    def _create_table_row(self, promo, index, row_number):
        """Create a single table row"""
        promo_id = promo.get('id')
        name = promo.get('name', '-')
        discount_type = promo.get('discount_type', 'percent')
        value = promo.get('value', 0)
        min_qty = promo.get('min_qty', 1)
        min_amount = promo.get('min_amount', 0)
        start_date = promo.get('start_date')
        end_date = promo.get('end_date')
        status = promo.get('status', 'active')
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        discount_display = self._format_discount(discount_type, value)
        discount_type_label = get_text("percentage") if discount_type == "percent" else get_text("fixed_amount")
        
        # Date range display
        start_display = self._format_date(start_date)
        end_display = self._format_date(end_date)
        if start_display == "-" and end_display == "-":
            period_display = "-"
        else:
            period_display = f"{start_display} - {end_display}"
        
        # Check if expired
        is_expired = False
        try:
            today = datetime.now().date()
            if end_date:
                end = datetime.strptime(str(end_date), '%Y-%m-%d').date()
                is_expired = end < today and status == 'active'
        except:
            pass
        
        if is_expired:
            status = 'inactive'
        
        status_badge = self._get_status_badge(status, start_date, end_date)
        
        # Requirements text
        req_text = ""
        if min_qty > 1:
            req_text += f"Min {min_qty} pcs"
        if min_amount > 0:
            if req_text:
                req_text += " / "
            req_text += f"Min {int(min_amount):,} KIP"
        
        # Action buttons
        items_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LIST_ALT, size=16, color="#9C27B0"),
                ft.Text(get_text("items"), size=12, color="#9C27B0"),
            ], spacing=4),
            on_click=lambda e, pid=promo_id, pname=name: self.show_items_dialog(pid, pname),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        edit_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("edit"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, pid=promo_id: self._safe_edit(pid, e),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        delete_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
                ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
            ], spacing=4),
            on_click=lambda e, pid=promo_id: self._safe_delete(pid, e),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        row = ft.Container(
            content=ft.Row([
                # Row number
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(str(row_number), size=13, weight=ft.FontWeight.W_500, color="#1565C0"),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=6,
                        alignment=ft.Alignment(0, 0),
                    ),
                    width=50,
                    alignment=ft.Alignment(0, 0),
                ),
                # Name
                ft.Container(
                    content=ft.Column([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
                        ft.Text(req_text, size=10, color="#64748B") if req_text else ft.Container(),
                    ], spacing=2),
                    width=200,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                    tooltip=name,
                ),
                # Discount Type
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(discount_type_label, size=12, color="#64748B"),
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=4,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    ),
                    width=120,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                # Discount Value
                ft.Container(
                    content=ft.Text(discount_display, size=13, weight=ft.FontWeight.W_600, color=ft.Colors.ORANGE_700),
                    width=130,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                # Period
                ft.Container(
                    content=ft.Text(period_display, size=11, color=ft.Colors.GREY_600, max_lines=1),
                    width=180,
                    alignment=ft.Alignment(0, 0),
                ),
                # Status
                ft.Container(
                    content=status_badge,
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                # Actions
                ft.Container(
                    content=ft.Row([items_btn, edit_btn, delete_btn], spacing=4),
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
    
    def _create_empty_state(self):
        """Create empty state"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOCAL_OFFER, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_data"), size=16, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add"), size=13, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.Alignment(0, 0)),
            padding=ft.padding.all(40),
            expand=True,
        )
    
    def update_pagination_controls(self):
        """Update pagination controls"""
        if not self.filtered_promotions:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (len(self.filtered_promotions) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Container(
            content=ft.Row([
                ft.Text(f"{get_text('showing')} {len(self.filtered_promotions)} {get_text('of')} {len(self.promotions_data)} {get_text('results')}", size=12, color="#64748B"),
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
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=16, horizontal=20),
            bgcolor="#F5F7FA",
        )
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_promotions(self.filtered_promotions)
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_promotions(self.filtered_promotions)
    
    def filter_promotions(self, e=None):
        query = self.search_input.value.lower() if self.search_input.value else ""
        self.current_page = 1
        
        if not query:
            self.filtered_promotions = self.promotions_data.copy()
        else:
            self.filtered_promotions = [
                promo for promo in self.promotions_data
                if query in promo.get('name', '').lower()
            ]
        
        self.display_promotions(self.filtered_promotions)
    
    def display_promotions(self, promotions):
        self.table_rows.controls.clear()
        
        if not promotions:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_promotions = promotions[start_idx:end_idx]
            global_start = start_idx + 1
            
            for i, promo in enumerate(page_promotions):
                row_number = global_start + i
                row = self._create_table_row(promo, start_idx + i, row_number)
                self.table_rows.controls.append(row)
        
        self.update_pagination_controls()
        self.page.update()
    
    async def _delayed_load(self):
        await asyncio.sleep(0.2)
        self.load_data()
    
    def load_data(self):
        if self.is_loading:
            return
        self.is_loading = True
        
        try:
            print("DEBUG: Loading promotions data...")
            self.promotions_data = self.client.get_promotions()
            self.filtered_promotions = self.promotions_data.copy()
            print(f"DEBUG: Loaded {len(self.promotions_data)} promotions")
            self.display_promotions(self.filtered_promotions)
        except Exception as e:
            print(f"DEBUG: Error loading promotions: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
        finally:
            self.is_loading = False
    
    def _safe_edit(self, promo_id, event):
        try:
            self.edit_promotion(promo_id)
        except Exception as e:
            print(f"DEBUG: Error in edit: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
    
    def _safe_delete(self, promo_id, event):
        try:
            self.delete_promotion(promo_id)
        except Exception as e:
            print(f"DEBUG: Error in delete: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
    
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
    
    def _close_dialog(self, e=None):
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
    def show_add_dialog(self, e=None):
        """Show add promotion dialog"""
        
        name = ft.TextField(
            label=f"{get_text('promo_name')} *",
            hint_text="ເຊັ່ນ: Summer Sale 2024",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            autofocus=True,
            prefix_icon=ft.Icons.LOCAL_OFFER,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        discount_type = ft.Dropdown(
            label=f"{get_text('discount_type')} *",
            value="percent",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option("percent", f"% {get_text('percentage')}"),
                ft.dropdown.Option("amount", f"KIP {get_text('fixed_amount')}"),
            ]
        )
        
        value = ft.TextField(
            label=f"{get_text('discount_value')} *",
            hint_text="ເຊັ່ນ: 10 (ສຳລັບເປີເຊັນ) ຫຼື 50000 (ສຳລັບຈຳນວນເງິນ)",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        min_qty = ft.TextField(
            label=get_text("min_qty"),
            hint_text="1",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="1",
            prefix_icon=ft.Icons.SHOPPING_CART,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        min_amount = ft.TextField(
            label=get_text("min_amount"),
            hint_text="0",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="0",
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        start_date = ft.TextField(
            label=get_text("start_date"),
            hint_text="YYYY-MM-DD",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        end_date = ft.TextField(
            label=get_text("end_date"),
            hint_text="YYYY-MM-DD",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_MONTH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        status = ft.Dropdown(
            label=get_text("status"),
            value="active",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option("active", f"✅ {get_text('status_active')}"),
                ft.dropdown.Option("inactive", f"❌ {get_text('status_inactive')}"),
            ]
        )
        
        def save(e):
            if name.value and discount_type.value and value.value:
                try:
                    self.client.add_promotion(
                        name=name.value,
                        discount_type=discount_type.value,
                        value=float(value.value),
                        min_qty=int(min_qty.value) if min_qty.value else 1,
                        min_amount=float(min_amount.value) if min_amount.value else 0,
                        start_date=start_date.value if start_date.value else None,
                        end_date=end_date.value if end_date.value else None,
                        status=status.value
                    )
                    self._close_dialog()
                    self.load_data()
                    self.show_snackbar(f"✅ {get_text('add_success')}")
                except Exception as err:
                    print(f"Error saving: {err}")
                    traceback.print_exc()
                    self.show_snackbar(f"{get_text('error')}: {err}")
            else:
                self.show_snackbar(get_text("fill_all_fields"))
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.LOCAL_OFFER, size=28, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=14,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column(
                            [
                                ft.Text(get_text('promotions_add'), size=20, weight=ft.FontWeight.BOLD, color="#1E293B"),
                                ft.Text("ເພີ່ມໂປຣໂມຊັນໃໝ່", size=13, color="#64748B"),
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
                content=ft.Column(
                    [
                        name,
                        ft.Container(height=12),
                        discount_type,
                        ft.Container(height=12),
                        value,
                        ft.Container(height=12),
                        ft.Row([min_qty, min_amount], spacing=12),
                        ft.Container(height=12),
                        ft.Row([start_date, end_date], spacing=12),
                        ft.Container(height=12),
                        status,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(24),
                width=550,
                height=520,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(
                                content=ft.Row([ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"), ft.Text(get_text("cancel"), size=14, color="#64748B")], spacing=6),
                                on_click=self._close_dialog,
                            ),
                            ft.ElevatedButton(
                                content=ft.Row([ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE), ft.Text(get_text("save"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)], spacing=6),
                                on_click=save,
                                style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10), elevation=2),
                            ),
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.padding.all(20),
                    border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def edit_promotion(self, promo_id):
        """Edit promotion dialog"""
        
        promo = None
        for p in self.promotions_data:
            if p.get('id') == promo_id:
                promo = p
                break
        
        if not promo:
            self.show_snackbar(f"❌ {get_text('error')}")
            return
        
        name = ft.TextField(
            label=f"{get_text('promo_name')} *",
            value=promo.get('name', ''),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.LOCAL_OFFER,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        discount_type = ft.Dropdown(
            label=f"{get_text('discount_type')} *",
            value=promo.get('discount_type', 'percent'),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option("percent", f"% {get_text('percentage')}"),
                ft.dropdown.Option("amount", f"KIP {get_text('fixed_amount')}"),
            ]
        )
        
        value = ft.TextField(
            label=f"{get_text('discount_value')} *",
            value=str(promo.get('value', 0)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        min_qty = ft.TextField(
            label=get_text("min_qty"),
            value=str(promo.get('min_qty', 1)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SHOPPING_CART,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        min_amount = ft.TextField(
            label=get_text("min_amount"),
            value=str(promo.get('min_amount', 0)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        start_date_val = promo.get('start_date')
        start_date = ft.TextField(
            label=get_text("start_date"),
            value=str(start_date_val) if start_date_val else "",
            hint_text="YYYY-MM-DD",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        end_date_val = promo.get('end_date')
        end_date = ft.TextField(
            label=get_text("end_date"),
            value=str(end_date_val) if end_date_val else "",
            hint_text="YYYY-MM-DD",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_MONTH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        status = ft.Dropdown(
            label=get_text("status"),
            value=promo.get('status', 'active'),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option("active", f"✅ {get_text('status_active')}"),
                ft.dropdown.Option("inactive", f"❌ {get_text('status_inactive')}"),
            ]
        )
        
        def save_edit(e):
            try:
                if not name.value or not discount_type.value or not value.value:
                    self.show_snackbar(get_text("fill_all_fields"))
                    return
                
                self.client.update_promotion(promo_id, {
                    'name': name.value,
                    'discount_type': discount_type.value,
                    'value': float(value.value),
                    'min_qty': int(min_qty.value) if min_qty.value else 1,
                    'min_amount': float(min_amount.value) if min_amount.value else 0,
                    'start_date': start_date.value if start_date.value else None,
                    'end_date': end_date.value if end_date.value else None,
                    'status': status.value,
                })
                self._close_dialog()
                self.load_data()
                self.show_snackbar(f"✅ {get_text('edit_success')}")
            except Exception as err:
                print(f"Error in save_edit: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(content=ft.Icon(ft.Icons.EDIT, size=28, color=ft.Colors.WHITE), bgcolor=self.primary_color, border_radius=14, padding=ft.padding.all(8)),
                        ft.Column([ft.Text(get_text('promotions_edit'), size=20, weight=ft.FontWeight.BOLD, color="#1E293B"), ft.Text("ແກ້ໄຂຂໍ້ມູນໂປຣໂມຊັນ", size=13, color="#64748B")], spacing=2),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        name,
                        ft.Container(height=12),
                        discount_type,
                        ft.Container(height=12),
                        value,
                        ft.Container(height=12),
                        ft.Row([min_qty, min_amount], spacing=12),
                        ft.Container(height=12),
                        ft.Row([start_date, end_date], spacing=12),
                        ft.Container(height=12),
                        status,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(24),
                width=550,
                height=550,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"), ft.Text(get_text("cancel"), size=14, color="#64748B")], spacing=6), on_click=self._close_dialog),
                            ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE), ft.Text(get_text("save"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)], spacing=6), on_click=save_edit, style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.padding.all(20),
                    border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def delete_promotion(self, promo_id):
        promo = None
        for p in self.promotions_data:
            if p.get('id') == promo_id:
                promo = p
                break
        
        promo_name = promo.get('name', get_text('this_promotion')) if promo else get_text('this_promotion')
        WARNING_COLOR = "#DC2626"
        
        def confirm(e):
            try:
                self.client.delete_promotion(promo_id)
                self._close_dialog()
                self.load_data()
                self.show_snackbar(f"✅ {get_text('delete_success')}")
            except Exception as err:
                print(f"Error in delete: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(content=ft.Icon(ft.Icons.WARNING_AMBER, size=28, color=ft.Colors.WHITE), bgcolor=WARNING_COLOR, border_radius=14, padding=ft.padding.all(8)),
                        ft.Column([ft.Text(get_text("confirm"), size=20, weight=ft.FontWeight.BOLD, color="#1E293B"), ft.Text("ກະລຸນາຢືນຢັນການລຶບຂໍ້ມູນ", size=13, color="#64748B")], spacing=2),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(content=ft.Icon(ft.Icons.DELETE_OUTLINE, size=56, color=WARNING_COLOR), alignment=ft.Alignment(0, 0)),
                        ft.Container(height=8),
                        ft.Text(f"ທ່ານຕ້ອງການລຶບ '{promo_name}' ແທ້ບໍ?", size=16, weight=ft.FontWeight.W_500, color="#1E293B", text_align=ft.TextAlign.CENTER),
                        ft.Container(height=4),
                        ft.Text(get_text("delete_warning"), size=13, color="#64748B", text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                padding=ft.padding.all(32),
                width=400,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"), ft.Text(get_text("cancel"), size=14, color="#64748B")], spacing=6), on_click=self._close_dialog),
                            ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.DELETE, size=18, color=ft.Colors.WHITE), ft.Text(get_text("delete"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)], spacing=6), on_click=confirm, style=ft.ButtonStyle(bgcolor=WARNING_COLOR, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.padding.all(20),
                    border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    # ========== Promotion Items Management ==========
    
    def show_items_dialog(self, promotion_id: int, promotion_name: str):
        """Navigate to promotion items page"""
        self.navigate("promotion_items", promotion_id=promotion_id, promotion_name=promotion_name)
    
    def _show_add_item_dialog(self, promotion_id: int, item_type: str, on_add_callback):
        """Show dialog to add item to promotion"""
        
        search_field = ft.TextField(
            hint_text=f"ຄົ້ນຫາ {item_type}...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
        )
        search_field.on_change = lambda e: load_items(e.control.value)
        
        items_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=350)
        
        def load_items(search: str = ""):
            try:
                if item_type == 'part':
                    items = self.client.get_available_parts_for_promotion(promotion_id, search)
                else:
                    items = self.client.get_available_services_for_promotion(promotion_id, search)
                
                items_list.controls.clear()
                
                if not items:
                    items_list.controls.append(
                        ft.Container(
                            content=ft.Text(f"ບໍ່ພົບ {item_type} ທີ່ສາມາດເພີ່ມໄດ້", size=13, color="#64748B"),
                            alignment=ft.Alignment(0, 0),
                            padding=40,
                        )
                    )
                else:
                    for item in items:
                        price = item.get('sell_price') if item_type == 'part' else item.get('price')
                        items_list.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Column([
                                        ft.Text(item['name'], size=14, weight=ft.FontWeight.W_500),
                                        ft.Text(f"{int(price):,} KIP", size=12, color="#64748B"),
                                    ], spacing=2, expand=True),
                                    ft.ElevatedButton(
                                        "ເພີ່ມ",
                                        bgcolor=self.primary_color,
                                        color=ft.Colors.WHITE,
                                        on_click=lambda e, iid=item['id'], iname=item['name']: add_item(iid, iname),
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                    ),
                                ]),
                                padding=10,
                                bgcolor=ft.Colors.GREY_50,
                                border_radius=10,
                            )
                        )
                
                self.page.update()
            except Exception as e:
                print(f"Error loading available items: {e}")
                self.show_snackbar(f"{get_text('error')}: {e}")
        
        def add_item(item_id: int, item_name: str):
            try:
                self.client.add_promotion_item(promotion_id, item_type, item_id)
                self._close_dialog()
                on_add_callback()
                self.show_snackbar(f"✅ ເພີ່ມ {item_name} ສຳເລັດ")
            except Exception as e:
                self.show_snackbar(f"{get_text('error')}: {e}")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            title=ft.Text(f"ເພີ່ມ {item_type.upper()}", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    search_field,
                    ft.Container(height=10),
                    items_list,
                ], spacing=0),
                width=450,
                height=450,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=self._close_dialog),
            ],
        )
        
        load_items()
        self._open_dialog(dialog)
    
    def _create_item_row(self, item: dict, promotion_id: int, on_delete_callback):
        """Create a row for an item in the items list"""
        
        def delete_item(e):
            try:
                self.client.delete_promotion_item(promotion_id, item['id'])
                on_delete_callback()
                self.show_snackbar(f"✅ ລຶບລາຍການສຳເລັດ")
            except Exception as err:
                self.show_snackbar(f"{get_text('error')}: {err}")
        
        item_name = item.get('item_name', '-')
        item_price = item.get('item_price', 0)
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(item_name, size=14, weight=ft.FontWeight.W_500),
                    ft.Text(f"{int(item_price):,} KIP", size=11, color="#64748B"),
                ], spacing=2, expand=True),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_600,
                    icon_size=20,
                    on_click=delete_item,
                    tooltip="ລຶບ",
                ),
            ]),
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
        )
    
    def show_snackbar(self, message):
        snack = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.GREY_800, duration=3000)
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()