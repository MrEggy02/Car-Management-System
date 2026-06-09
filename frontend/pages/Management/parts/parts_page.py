import flet as ft
import sys
import os
import asyncio
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import get_text
from Management.parts.parts_dialogs import PartsDialogs


class PartsContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.is_loading = False
        self.current_dialog = None
        self.parts_data = []
        self.filtered_parts = []
        self.search_input = None
        self.current_page = 1
        self.items_per_page = 25
        self.total_pages = 1
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
        # Cache for units, categories, suppliers
        self.units = []
        self.categories = []
        self.suppliers = []
        
        # Dialogs helper
        self.dialogs = PartsDialogs(self)
        
        # Table data rows container
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.pagination_container = ft.Container()
        
    def build(self):
        """Build parts management content with table layout"""
        
        # Beautiful gradient header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("parts_title"), 
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
                        on_click=lambda e: self.show_add_dialog(),
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
        
        # Search Bar
        self.search_input = ft.TextField(
            hint_text=f" {get_text('search')} {get_text('parts_title')}...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            on_change=self.filter_parts,
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
        
        # Pagination container
        self.update_pagination_controls()
        
        # Main content area
        main_content = ft.Container(
            content=ft.Column([
                table_container,
                self.pagination_container,
            ], spacing=0),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.page.run_task(self._delayed_load)
        
        return ft.Column([
            header,
            control_bar,
            main_content,
        ], expand=True, spacing=0)
    
    def _create_table_header(self):
        """Create table header row with reduced widths"""
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=40, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('parts_name'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=160, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=8)),
                ft.Container(content=ft.Text(get_text('category'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=90, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=8)),
                ft.Container(content=ft.Text(get_text('parts_stock'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=60, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('unit'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=50, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('cost_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=90, alignment=ft.Alignment(1, 0), padding=ft.padding.only(right=8)),
                ft.Container(content=ft.Text(get_text('sell_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=90, alignment=ft.Alignment(1, 0), padding=ft.padding.only(right=8)),
                ft.Container(content=ft.Text(get_text('supplier'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=8)),
                ft.Container(content=ft.Text(get_text('status'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=70, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('actions'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=90, alignment=ft.Alignment(0, 0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=8),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _get_unit_name(self, unit_id):
        """Get unit name by ID"""
        if not unit_id:
            return "-"
        for unit in self.units:
            if unit.get('id') == unit_id:
                return unit.get('name', '-')
        return "-"
    
    def _get_category_name(self, category_id):
        """Get category name by ID"""
        if not category_id:
            return "-"
        for cat in self.categories:
            if cat.get('id') == category_id:
                return cat.get('name', '-')
        return "-"
    
    def _format_price(self, price):
        """Format price to short string"""
        if price >= 1000000:
            return f"{price/1000000:.1f}M"
        elif price >= 1000:
            return f"{int(price/1000)}K"
        else:
            return str(int(price))
    
    def _format_stock(self, stock_qty):
        """Format stock quantity - if over 999, show as K"""
        if stock_qty >= 10000:
            return f"{stock_qty/1000:.0f}K"
        else:
            return str(stock_qty)
    
    def _create_table_row(self, part, index, row_number):
        """Create a single table row with reduced widths"""
        part_id = part.get('id')
        name = part.get('name', '-')
        stock_qty = part.get('stock_qty', 0)
        min_stock = part.get('min_stock', 5)
        cost_price = part.get('cost_price', 0)
        sell_price = part.get('sell_price', 0)
        unit_id = part.get('unit_id')
        category_id = part.get('category_id')
        supplier_name = part.get('supplier_name', '-')
        
        unit_name = self._get_unit_name(unit_id)
        category_name = self._get_category_name(category_id)
        
        is_low_stock = stock_qty <= min_stock
        formatted_stock = self._format_stock(stock_qty)
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        # Stock status badge - simplified and smaller
        if is_low_stock:
            stock_badge = ft.Container(
                content=ft.Text(formatted_stock, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.RED_500,
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                alignment=ft.Alignment(0, 0),
            )
        elif stock_qty == 0:
            stock_badge = ft.Container(
                content=ft.Text(formatted_stock, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.GREY_600,
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                alignment=ft.Alignment(0, 0),
            )
        else:
            stock_badge = ft.Container(
                content=ft.Text(formatted_stock, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                alignment=ft.Alignment(0, 0),
            )
        
        # Status badge - simplified
        if is_low_stock:
            status_badge = ft.Container(
                content=ft.Text(get_text("low_stock"), size=10, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.ORANGE_600,
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=5, vertical=2),
            )
        else:
            status_badge = ft.Container(
                content=ft.Text(get_text("normal"), size=10, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=5, vertical=2),
            )
        
        # Action buttons - smaller
        edit_btn = ft.IconButton(
            icon=ft.Icons.EDIT_OUTLINED,
            icon_size=18,
            icon_color=self.primary_color,
            on_click=lambda e, pid=part_id: self._safe_edit(pid, e),
            tooltip=get_text("edit"),
            padding=0,
        )
        
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_size=18,
            icon_color=ft.Colors.RED_600,
            on_click=lambda e, pid=part_id: self._safe_delete(pid, e),
            tooltip=get_text("delete"),
            padding=0,
        )
        
        # Truncate long names
        display_name = name[:22] + "..." if len(name) > 22 else name
        display_supplier = supplier_name[:10] + "..." if len(supplier_name) > 10 else supplier_name
        display_category = category_name[:12] + "..." if len(category_name) > 12 else category_name
        display_unit = unit_name[:5] + "..." if len(unit_name) > 5 else unit_name
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(str(row_number), size=12, weight=ft.FontWeight.W_500, color=self.primary_color),
                    width=40,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(display_name, size=12, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1),
                    width=160,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=8),
                    tooltip=name,
                ),
                ft.Container(
                    content=ft.Text(display_category, size=11, color="#64748B", max_lines=1),
                    width=90,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=8),
                    tooltip=category_name,
                ),
                ft.Container(
                    content=stock_badge,
                    width=60,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(display_unit, size=11, color="#64748B"),
                    width=50,
                    alignment=ft.Alignment(0, 0),
                    tooltip=unit_name,
                ),
                ft.Container(
                    content=ft.Text(self._format_price(cost_price), size=11, color="#64748B"),
                    width=90,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=8),
                ),
                ft.Container(
                    content=ft.Text(self._format_price(sell_price), size=12, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700),
                    width=90,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=8),
                ),
                ft.Container(
                    content=ft.Text(display_supplier, size=11, color="#64748B", max_lines=1),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=8),
                    tooltip=supplier_name,
                ),
                ft.Container(
                    content=status_badge,
                    width=70,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Row([edit_btn, delete_btn], spacing=4),
                    width=90,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=8, horizontal=8),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    def _create_empty_state(self):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PRECISION_MANUFACTURING, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_data"), size=16, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add"), size=13, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(40),
            expand=True,
        )
    
    def update_pagination_controls(self):
        if not self.filtered_parts:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (len(self.filtered_parts) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Container(
            content=ft.Row([
                ft.Text(f"{get_text('showing')} {len(self.filtered_parts)} {get_text('of')} {len(self.parts_data)} {get_text('results')}", size=12, color="#64748B"),
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
            self.display_parts(self.filtered_parts)
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_parts(self.filtered_parts)
    
    def filter_parts(self, e=None):
        query = self.search_input.value.lower() if self.search_input.value else ""
        self.current_page = 1
        
        if not query:
            self.filtered_parts = self.parts_data.copy()
        else:
            self.filtered_parts = [
                part for part in self.parts_data
                if query in part.get('name', '').lower()
                or (part.get('supplier_name') and query in part.get('supplier_name', '').lower())
            ]
        
        self.display_parts(self.filtered_parts)
    
    def display_parts(self, parts):
        self.table_rows.controls.clear()
        
        if not parts:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_parts = parts[start_idx:end_idx]
            global_start = start_idx + 1
            
            for i, part in enumerate(page_parts):
                row_number = global_start + i
                row = self._create_table_row(part, start_idx + i, row_number)
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
            # Load units, categories, suppliers
            self.units = self.client.get_units() or []
            self.categories = self.client.get_part_categories() or []
            self.suppliers = self.client.get_suppliers() or []
            
            print(f"DEBUG: Loaded {len(self.units)} units, {len(self.categories)} categories, {len(self.suppliers)} suppliers")
            
            # Load parts
            self.parts_data = self.client.get_parts()
            self.filtered_parts = self.parts_data.copy()
            print(f"DEBUG: Loaded {len(self.parts_data)} parts")
            
            self.display_parts(self.filtered_parts)
        except Exception as e:
            print(f"DEBUG: Error loading parts: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
        finally:
            self.is_loading = False
    
    def _safe_edit(self, part_id, event):
        try:
            self.edit_part(part_id)
        except Exception as e:
            print(f"DEBUG: Error in edit: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
    
    def _safe_delete(self, part_id, event):
        try:
            self.delete_part(part_id)
        except Exception as e:
            print(f"DEBUG: Error in delete: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
    
    def show_add_dialog(self):
        """Show add part dialog using dialogs class"""
        active_units = [u for u in self.units if u.get('status') == 'active']
        active_categories = [c for c in self.categories if c.get('status') == 'active']
        self.dialogs.show_add_dialog(active_units, active_categories, self.suppliers)
    
    def edit_part(self, part_id):
        """Edit part dialog using dialogs class"""
        part = None
        for p in self.parts_data:
            if p.get('id') == part_id:
                part = p
                break
        
        if not part:
            self.show_snackbar(f"❌ {get_text('error')}")
            return
        
        active_units = [u for u in self.units]
        active_categories = [c for c in self.categories]
        self.dialogs.show_edit_dialog(part, active_units, active_categories, self.suppliers)
    
    def delete_part(self, part_id):
        """Delete part with confirmation dialog"""
        part = None
        for p in self.parts_data:
            if p.get('id') == part_id:
                part = p
                break
        
        part_name = part.get('name', get_text('this_part')) if part else get_text('this_part')
        self.dialogs.show_delete_dialog(part_name, part_id)
    
    def show_snackbar(self, message, is_error=False):
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=3000,
        )
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()