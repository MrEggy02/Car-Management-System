# pages/promotions_page.py
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
    
    def build(self):
        """Build promotions management content with table layout"""
        
        # Beautiful gradient header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("promotions_title"), 
                                size=24, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.WHITE
                            ),
                            ft.Text(
                                get_text("promotion_sub"),
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
            padding=ft.padding.symmetric(vertical=20, horizontal=32),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
           
        )
        
        # Search Bar with beautiful design
        self.search_input = ft.TextField(
            hint_text=f"🔍 {get_text('search')} {get_text('promotions_title')}...",
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
        
        # Control bar
        control_bar = ft.Container(
            content=search_container,
            padding=ft.padding.all(20),
            bgcolor="#F5F7FA",
        )
        
        # Table Header
        table_header = self._create_table_header()
        
        # Table scroll container
        table_scroll_container = ft.Container(
            content=self.table_rows,
            expand=True,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            bgcolor=ft.Colors.WHITE,
        )
        
        # Table Container
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
        
        # Pagination container (will be updated by update_pagination)
        self.pagination_container = ft.Container(
            padding=ft.padding.symmetric(vertical=16, horizontal=20),
            bgcolor="#F5F7FA",
        )
        
        # Main content area
        main_content = ft.Container(
            content=ft.Column([
                table_container,
                self.pagination_container,
            ], spacing=0),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Main container
        main_container = ft.Container(
            content=main_content,
            expand=True,
        )
        
        # Load data after UI is built
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
                ft.Container(
                    content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=50,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('promo_code'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('promo_name'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('discount_type'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('start_date'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('end_date'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('status'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('actions'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=14, horizontal=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _create_table_row(self, promo, index, row_number):
        """Create a single table row"""
        promo_id = promo.get('id')
        promo_name = promo.get('promo_name', '-')
        promo_code = promo.get('promo_code', '-')
        discount_type = promo.get('discount_type', 'percentage')
        discount_value = promo.get('discount_value', 0)
        start_date = promo.get('start_date', '-')
        end_date = promo.get('end_date', '-')
        is_active = promo.get('is_active', True)
        
        # Calculate days remaining
        days_remaining = None
        if end_date != '-':
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                today = datetime.now().date()
                days_remaining = (end - today).days
            except:
                pass
        
        # Determine if expiring soon
        is_expiring_soon = days_remaining is not None and 0 <= days_remaining <= 7
        is_expired = days_remaining is not None and days_remaining < 0
        
        # Row background color (alternate)
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        # Discount display
        discount_symbol = "%" if discount_type == "percentage" else " KIP"
        discount_display = f"{int(discount_value)}{discount_symbol}"
        discount_label = get_text("percentage") if discount_type == "percentage" else get_text("fixed")
        
        # Status badge
        if is_active and not is_expired:
            if is_expiring_soon:
                status_badge = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING, size=14, color=ft.Colors.WHITE),
                        ft.Text(get_text("expiring_soon"), size=11, color=ft.Colors.WHITE),
                    ], spacing=4),
                    bgcolor=ft.Colors.ORANGE_600,
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                )
            else:
                status_badge = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color=ft.Colors.WHITE),
                        ft.Text(get_text("active"), size=11, color=ft.Colors.WHITE),
                    ], spacing=4),
                    bgcolor=ft.Colors.GREEN_600,
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                )
        else:
            status_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CANCEL, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("inactive"), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=ft.Colors.RED_500,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
            )
        
        # Days remaining text
        if days_remaining is not None:
            if days_remaining >= 0:
                days_text = f"{days_remaining} {get_text('days_left')}"
                days_color = ft.Colors.RED_600 if is_expiring_soon else ft.Colors.GREY_600
            else:
                days_text = get_text("expired")
                days_color = ft.Colors.RED_600
        else:
            days_text = "-"
            days_color = ft.Colors.GREY_400
        
        # Action buttons
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
        
        # Format dates for display (shorter)
        start_display = start_date if start_date != '-' else '-'
        end_display = end_date if end_date != '-' else '-'
        
        row = ft.Container(
            content=ft.Row([
                # Row number column with badge styling
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
                # Promo Code column
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(promo_code, size=12, color=ft.Colors.GREY_700, weight=ft.FontWeight.W_500, max_lines=1),
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=4,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    ),
                    width=110,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                # Promo Name column
                ft.Container(
                    content=ft.Text(promo_name, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                # Discount column
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{discount_label}: {discount_display}", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ORANGE_700, max_lines=1),
                        ft.Text(days_text, size=10, color=days_color),
                    ], spacing=1),
                    width=110,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                # Start Date column
                ft.Container(
                    content=ft.Text(start_display, size=12, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                # End Date column
                ft.Container(
                    content=ft.Text(end_display, size=12, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                # Status column
                ft.Container(
                    content=status_badge,
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                # Actions column
                ft.Container(
                    content=ft.Row([edit_btn, delete_btn], spacing=4),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=10),
            bgcolor=row_bg,
        )
        
        # Add divider at bottom
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    def _create_empty_state(self):
        """Create empty state when no data"""
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
    
    def update_pagination(self):
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
        
        self.pagination_container.content = ft.Row([
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
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.update()
    
    def prev_page(self, e=None):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_promotions(self.filtered_promotions)
    
    def next_page(self, e=None):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_promotions(self.filtered_promotions)
    
    def filter_promotions(self, e=None):
        """Filter promotions based on search query"""
        query = self.search_input.value.lower() if self.search_input.value else ""
        
        self.current_page = 1
        
        if not query:
            self.filtered_promotions = self.promotions_data.copy()
        else:
            self.filtered_promotions = [
                promo for promo in self.promotions_data
                if query in promo.get('promo_name', '').lower()
                or query in promo.get('promo_code', '').lower()
            ]
        
        self.display_promotions(self.filtered_promotions)
    
    def display_promotions(self, promotions):
        """Display promotions in table format"""
        self.table_rows.controls.clear()
        
        if not promotions:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_promotions = promotions[start_idx:end_idx]
            
            # Calculate global row number
            global_start = start_idx + 1
            
            for i, promo in enumerate(page_promotions):
                row_number = global_start + i
                row = self._create_table_row(promo, start_idx + i, row_number)
                self.table_rows.controls.append(row)
        
        self.update_pagination()
        self.page.update()
    
    async def _delayed_load(self):
        """Async delayed load"""
        await asyncio.sleep(0.2)
        self.load_data()
    
    def load_data(self):
        """Load promotions from API"""
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
        """Safe wrapper for edit button"""
        try:
            self.edit_promotion(promo_id)
        except Exception as e:
            print(f"DEBUG: Error in edit: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
    
    def _safe_delete(self, promo_id, event):
        """Safe wrapper for delete button"""
        try:
            self.delete_promotion(promo_id)
        except Exception as e:
            print(f"DEBUG: Error in delete: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
    
    def _open_dialog(self, dialog):
        """Centralized dialog opening method"""
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
        """Centralized dialog closing method"""
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
    def show_add_dialog(self, e=None):
        """Show add promotion dialog with modern UI"""
        print("DEBUG: show_add_dialog called")
        
        promo_code = ft.TextField(
            label=f"{get_text('promo_code')} *",
            hint_text="เช่น SUMMER2024",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            autofocus=True,
            prefix_icon=ft.Icons.LOCAL_OFFER,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        promo_name = ft.TextField(
            label=f"{get_text('promo_name')} *",
            hint_text="เช่น ส่วนลดหน้าร้อน",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.TAG,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        discount_type = ft.Dropdown(
            label=f"{get_text('discount_type')} *",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.PERCENT,
            options=[
                ft.dropdown.Option("percentage", f"% {get_text('percentage')}"),
                ft.dropdown.Option("fixed", f"KIP {get_text('fixed')}"),
            ]
        )
        
        discount_value = ft.TextField(
            label=f"{get_text('discount_value')} *",
            hint_text="เช่น 10 หรือ 50000",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        start_date = ft.TextField(
            label=f"{get_text('start_date')} *",
            hint_text="2024-01-01",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        end_date = ft.TextField(
            label=f"{get_text('end_date')} *",
            hint_text="2024-12-31",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_MONTH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        def save(e):
            if promo_code.value and promo_name.value and discount_type.value and discount_value.value:
                try:
                    self.client.add_promotion(
                        promo_code.value,
                        promo_name.value,
                        discount_type.value,
                        float(discount_value.value),
                        start_date.value,
                        end_date.value,
                        True
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
                                ft.Text(
                                    get_text('promotions_add'),
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    "เพิ่มโปรโมชั่นใหม่เข้าสู่ระบบ",
                                    size=13,
                                    color="#64748B",
                                ),
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
                        promo_code,
                        ft.Container(height=12),
                        promo_name,
                        ft.Container(height=12),
                        discount_type,
                        ft.Container(height=12),
                        discount_value,
                        ft.Container(height=12),
                        ft.Row([start_date, end_date], spacing=12),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(24),
                width=520,
                height=500,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
                                        ft.Text(get_text("cancel"), size=14, color="#64748B"),
                                    ],
                                    spacing=6,
                                ),
                                on_click=self._close_dialog,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.GREY_400),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                                        ft.Text(get_text("save"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    ],
                                    spacing=6,
                                ),
                                on_click=save,
                                style=ft.ButtonStyle(
                                    bgcolor=self.primary_color,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=2,
                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                ),
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
        """Edit promotion dialog with modern UI"""
        
        # Find promotion from stored data
        promo = None
        for p in self.promotions_data:
            if p.get('id') == promo_id:
                promo = p
                break
        
        if not promo:
            self.show_snackbar(f"❌ {get_text('error')}")
            return
        
        promo_code = ft.TextField(
            label=f"{get_text('promo_code')} *",
            value=promo.get('promo_code', ''),
            read_only=True,
            border_radius=12,
            bgcolor=ft.Colors.GREY_100,
            filled=True,
            prefix_icon=ft.Icons.LOCAL_OFFER,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )
        
        promo_name = ft.TextField(
            label=f"{get_text('promo_name')} *",
            value=promo.get('promo_name', ''),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.TAG,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        discount_type = ft.Dropdown(
            label=f"{get_text('discount_type')} *",
            value=promo.get('discount_type', 'percentage'),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.PERCENT,
            options=[
                ft.dropdown.Option("percentage", f"% {get_text('percentage')}"),
                ft.dropdown.Option("fixed", f"KIP {get_text('fixed')}"),
            ]
        )
        
        discount_value = ft.TextField(
            label=f"{get_text('discount_value')} *",
            value=str(int(promo.get('discount_value', 0))),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        start_date = ft.TextField(
            label=f"{get_text('start_date')} *",
            value=promo.get('start_date', ''),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        end_date = ft.TextField(
            label=f"{get_text('end_date')} *",
            value=promo.get('end_date', ''),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_MONTH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        is_active = promo.get('is_active', True)
        
        active_toggle = ft.Switch(
            label=get_text("active"),
            value=is_active,
            active_color=self.primary_color,
        )
        
        def save_edit(e):
            try:
                if not promo_name.value or not discount_type.value or not discount_value.value:
                    self.show_snackbar(get_text("fill_all_fields"))
                    return
                
                self.client.update_promotion(promo_id, {
                    'promo_code': promo_code.value,
                    'promo_name': promo_name.value,
                    'discount_type': discount_type.value,
                    'discount_value': float(discount_value.value) if discount_value.value else 0,
                    'start_date': start_date.value,
                    'end_date': end_date.value,
                    'is_active': active_toggle.value,
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
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=28, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=14,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    get_text('promotions_edit'),
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    "แก้ไขข้อมูลโปรโมชั่น",
                                    size=13,
                                    color="#64748B",
                                ),
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
                        promo_code,
                        ft.Container(height=12),
                        promo_name,
                        ft.Container(height=12),
                        discount_type,
                        ft.Container(height=12),
                        discount_value,
                        ft.Container(height=12),
                        ft.Row([start_date, end_date], spacing=12),
                        ft.Container(height=12),
                        active_toggle,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(24),
                width=520,
                height=550,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
                                        ft.Text(get_text("cancel"), size=14, color="#64748B"),
                                    ],
                                    spacing=6,
                                ),
                                on_click=self._close_dialog,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.GREY_400),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                                        ft.Text(get_text("save"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    ],
                                    spacing=6,
                                ),
                                on_click=save_edit,
                                style=ft.ButtonStyle(
                                    bgcolor=self.primary_color,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=2,
                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                ),
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
    
    def delete_promotion(self, promo_id):
        """Delete promotion with confirmation dialog"""
        
        # Find promotion from stored data
        promo = None
        for p in self.promotions_data:
            if p.get('id') == promo_id:
                promo = p
                break
        
        promo_name = promo.get('promo_name', get_text('this_promotion')) if promo else get_text('this_promotion')
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
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, size=28, color=ft.Colors.WHITE),
                            bgcolor=WARNING_COLOR,
                            border_radius=14,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    get_text("confirm"),
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    "กรุณายืนยันการลบข้อมูล",
                                    size=13,
                                    color="#64748B",
                                ),
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
                        ft.Container(
                            content=ft.Icon(ft.Icons.DELETE_OUTLINE, size=56, color=WARNING_COLOR),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            f"คุณต้องการลบ '{promo_name}' หรือไม่?",
                            size=16,
                            weight=ft.FontWeight.W_500,
                            color="#1E293B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=4),
                        ft.Text(
                            get_text("delete_warning"),
                            size=13,
                            color="#64748B",
                            text_align=ft.TextAlign.CENTER,
                        ),
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
                            ft.TextButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
                                        ft.Text(get_text("cancel"), size=14, color="#64748B"),
                                    ],
                                    spacing=6,
                                ),
                                on_click=self._close_dialog,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.GREY_400),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.DELETE, size=18, color=ft.Colors.WHITE),
                                        ft.Text(get_text("delete"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    ],
                                    spacing=6,
                                ),
                                on_click=confirm,
                                style=ft.ButtonStyle(
                                    bgcolor=WARNING_COLOR,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=2,
                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                ),
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
    
    def show_snackbar(self, message):
        """Show snackbar message"""
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.GREY_800,
            duration=3000,
        )
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()