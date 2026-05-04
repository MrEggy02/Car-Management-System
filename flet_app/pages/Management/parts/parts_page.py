# pages/parts_page.py
import flet as ft
import sys
import os
import asyncio
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import get_text

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
        self.items_per_page = 20
        self.total_pages = 1
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
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
                                size=24, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.WHITE
                            ),
                            ft.Text(
                                get_text("card_parts_sub"),
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
            hint_text=f"🔍 {get_text('search')} {get_text('parts_title')}...",
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
                    content=ft.Text(get_text('parts_code'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('parts_name'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('parts_brand'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('parts_stock'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=80,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('cost_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('sell_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('status'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=90,
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
    
    def _create_table_row(self, part, index, row_number):
        """Create a single table row"""
        part_id = part.get('id')
        part_name = part.get('name', '-')
        part_code = part.get('part_code', '-')
        brand = part.get('brand', '-') or '-'
        stock_qty = part.get('stock_qty', 0)
        min_stock = part.get('min_stock', 5)
        sell_price = part.get('sell_price', 0)
        cost_price = part.get('cost_price', 0)
        unit = part.get('unit', get_text('unit'))
        
        is_low_stock = stock_qty < min_stock
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        if is_low_stock:
            status_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.WARNING, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("stock_warning"), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=ft.Colors.RED_500,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        else:
            status_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("normal_stock"), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        
        edit_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("edit"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, pid=part_id: self._safe_edit(pid, e),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        delete_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
                ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
            ], spacing=4),
            on_click=lambda e, pid=part_id: self._safe_delete(pid, e),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
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
                ft.Container(
                    content=ft.Text(part_code, size=12, color=ft.Colors.GREY_700, max_lines=1),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(part_name, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(brand, size=12, color=ft.Colors.GREY_600, max_lines=1),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(
                        f"{stock_qty} {unit}", 
                        size=13, 
                        weight=ft.FontWeight.W_500, 
                        color=ft.Colors.RED_600 if is_low_stock else ft.Colors.BLACK
                    ),
                    width=80,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(f"{int(cost_price):,}", size=12, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(f"{int(sell_price):,}", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=110,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=status_badge,
                    width=90,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Row([edit_btn, delete_btn], spacing=4),
                    width=120,
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
        """Create empty state when no data"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PRECISION_MANUFACTURING, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_data"), size=16, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add"), size=13, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.Alignment(0, 0)),
            padding=ft.padding.all(40),
            expand=True,
        )
    
    def update_pagination(self):
        """Update pagination controls"""
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
        
        self.pagination_container.content = ft.Row([
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
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.update()
    
    def prev_page(self, e=None):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_parts(self.filtered_parts)
    
    def next_page(self, e=None):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_parts(self.filtered_parts)
    
    def filter_parts(self, e=None):
        """Filter parts based on search query"""
        query = self.search_input.value.lower() if self.search_input.value else ""
        
        self.current_page = 1
        
        if not query:
            self.filtered_parts = self.parts_data.copy()
        else:
            self.filtered_parts = [
                part for part in self.parts_data
                if query in part.get('name', '').lower()
                or query in part.get('part_code', '').lower()
                or query in part.get('brand', '').lower()
            ]
        
        self.display_parts(self.filtered_parts)
    
    def display_parts(self, parts):
        """Display parts in table format"""
        self.table_rows.controls.clear()
        
        if not parts:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_parts = parts[start_idx:end_idx]
            
            # Calculate global row number
            global_start = start_idx + 1
            
            for i, part in enumerate(page_parts):
                row_number = global_start + i
                row = self._create_table_row(part, start_idx + i, row_number)
                self.table_rows.controls.append(row)
        
        self.update_pagination()
        self.page.update()
    
    async def _delayed_load(self):
        """Async delayed load"""
        await asyncio.sleep(0.2)
        self.load_data()
    
    def load_data(self):
        """Load parts from API"""
        if self.is_loading:
            return
        self.is_loading = True
        
        try:
            print("DEBUG: Loading parts data...")
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
        """Safe wrapper for edit button"""
        try:
            self.edit_part(part_id)
        except Exception as e:
            print(f"DEBUG: Error in edit: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
    
    def _safe_delete(self, part_id, event):
        """Safe wrapper for delete button"""
        try:
            self.delete_part(part_id)
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
        """Show add part dialog with modern UI and supplier dropdown"""
        print("DEBUG: show_add_dialog called")
        
        # Load suppliers for dropdown
        suppliers = []
        try:
            suppliers = self.client.get_suppliers()
            print(f"DEBUG: Loaded {len(suppliers)} suppliers for dropdown")
        except Exception as err:
            print(f"DEBUG: Error loading suppliers: {err}")
        
        # Create options for dropdown
        supplier_options = [
            ft.dropdown.Option("", f"-- {get_text('no_supplier')} --")
        ]
        
        for sup in suppliers:
            supplier_id = sup.get('id')
            supplier_name = sup.get('name', 'Unknown')
            supplier_options.append(
                ft.dropdown.Option(str(supplier_id), f"{supplier_name}")
            )
        
        code = ft.TextField(
            label=f"{get_text('parts_code')} *",
            hint_text="เช่น BRK-001",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            autofocus=True,
            prefix_icon=ft.Icons.CODE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        name = ft.TextField(
            label=f"{get_text('parts_name')} *",
            hint_text="เช่น ผ้าเบรคหน้า",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CATEGORY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        brand = ft.TextField(
            label=get_text("parts_brand"),
            hint_text="เช่น Toyota, Honda, Bosch",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.BRANDING_WATERMARK,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        cost_price = ft.TextField(
            label=get_text("cost_price"),
            hint_text="0",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="0",
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        sell_price = ft.TextField(
            label=f"{get_text('sell_price')} *",
            hint_text="0",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="0",
            prefix_icon=ft.Icons.PAYMENT,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        stock_qty = ft.TextField(
            label=get_text("parts_stock"),
            hint_text="0",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="0",
            prefix_icon=ft.Icons.INVENTORY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        min_stock = ft.TextField(
            label=get_text("parts_min_stock"),
            hint_text="5",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="5",
            prefix_icon=ft.Icons.WARNING,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        unit = ft.TextField(
            label=get_text("unit"),
            hint_text="ชิ้น, ลิตร, เส้น",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value=get_text("unit"),
            prefix_icon=ft.Icons.SCALE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        supplier_dropdown = ft.Dropdown(
            label=get_text("supplier"),
            hint_text=f"-- {get_text('select_supplier')} --",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            options=supplier_options,
            value="",
        )
        
        def save(e):
            if code.value and name.value and sell_price.value:
                try:
                    supplier_id_val = int(supplier_dropdown.value) if supplier_dropdown.value and supplier_dropdown.value.strip() else None
                    
                    self.client.add_part(
                        part_code=code.value,
                        name=name.value,
                        brand=brand.value,
                        cost_price=float(cost_price.value) if cost_price.value else 0,
                        sell_price=float(sell_price.value) if sell_price.value else 0,
                        stock_qty=int(stock_qty.value) if stock_qty.value else 0,
                        min_stock=int(min_stock.value) if min_stock.value else 5,
                        unit=unit.value,
                        supplier_id=supplier_id_val
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
                            content=ft.Icon(ft.Icons.ADD_CIRCLE, size=28, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=14,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    get_text('parts_add'),
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    "เพิ่มอะไหล่ใหม่เข้าสู่ระบบ",
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
                        code,
                        ft.Container(height=12),
                        name,
                        ft.Container(height=12),
                        brand,
                        ft.Container(height=12),
                        ft.Row([cost_price, sell_price], spacing=12),
                        ft.Container(height=12),
                        ft.Row([stock_qty, min_stock], spacing=12),
                        ft.Container(height=12),
                        unit,
                        ft.Container(height=12),
                        supplier_dropdown,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(24),
                width=560,
                height=620,
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
    
    def edit_part(self, part_id):
        """Edit part dialog with modern UI and supplier dropdown"""
        
        part = None
        for p in self.parts_data:
            if p.get('id') == part_id:
                part = p
                break
        
        if not part:
            self.show_snackbar(f"❌ {get_text('error')}")
            return
        
        # Load suppliers for dropdown
        suppliers = []
        try:
            suppliers = self.client.get_suppliers()
            print(f"DEBUG: Loaded {len(suppliers)} suppliers for dropdown")
        except Exception as err:
            print(f"DEBUG: Error loading suppliers: {err}")
        
        # Create options for dropdown
        supplier_options = [
            ft.dropdown.Option("", f"-- {get_text('no_supplier')} --")
        ]
        
        for sup in suppliers:
            supplier_id = sup.get('id')
            supplier_name = sup.get('name', 'Unknown')
            supplier_options.append(
                ft.dropdown.Option(str(supplier_id), f"{supplier_name}")
            )
        
        code = ft.TextField(
            label=f"{get_text('parts_code')} *",
            value=part.get('part_code', ''),
            read_only=True,
            border_radius=12,
            bgcolor=ft.Colors.GREY_100,
            filled=True,
            prefix_icon=ft.Icons.CODE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )
        
        name = ft.TextField(
            label=f"{get_text('parts_name')} *",
            value=part.get('name', ''),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CATEGORY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        brand = ft.TextField(
            label=get_text("parts_brand"),
            value=part.get('brand', ''),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.BRANDING_WATERMARK,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        cost_price = ft.TextField(
            label=get_text("cost_price"),
            value=str(part.get('cost_price', 0)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        sell_price = ft.TextField(
            label=f"{get_text('sell_price')} *",
            value=str(part.get('sell_price', 0)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.PAYMENT,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        stock_qty = ft.TextField(
            label=get_text("parts_stock"),
            value=str(part.get('stock_qty', 0)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.INVENTORY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        min_stock = ft.TextField(
            label=get_text("parts_min_stock"),
            value=str(part.get('min_stock', 5)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.WARNING,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        unit = ft.TextField(
            label=get_text("unit"),
            value=part.get('unit', get_text("unit")),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SCALE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        current_supplier_id = str(part.get('supplier_id', '')) if part.get('supplier_id') else ""
        
        supplier_dropdown = ft.Dropdown(
            label=get_text("supplier"),
            hint_text=f"-- {get_text('select_supplier')} --",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
            options=supplier_options,
            value=current_supplier_id,
        )
        
        def save_edit(e):
            try:
                if not name.value or not sell_price.value:
                    self.show_snackbar(get_text("fill_all_fields"))
                    return
                
                supplier_id_val = int(supplier_dropdown.value) if supplier_dropdown.value and supplier_dropdown.value.strip() else None
                
                self.client.update_part(part_id, {
                    'part_code': code.value,
                    'name': name.value,
                    'brand': brand.value,
                    'cost_price': float(cost_price.value) if cost_price.value else 0,
                    'sell_price': float(sell_price.value) if sell_price.value else 0,
                    'stock_qty': int(stock_qty.value) if stock_qty.value else 0,
                    'min_stock': int(min_stock.value) if min_stock.value else 5,
                    'unit': unit.value,
                    'supplier_id': supplier_id_val
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
                                    get_text('parts_edit'),
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    "แก้ไขข้อมูลอะไหล่",
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
                        code,
                        ft.Container(height=12),
                        name,
                        ft.Container(height=12),
                        brand,
                        ft.Container(height=12),
                        ft.Row([cost_price, sell_price], spacing=12),
                        ft.Container(height=12),
                        ft.Row([stock_qty, min_stock], spacing=12),
                        ft.Container(height=12),
                        unit,
                        ft.Container(height=12),
                        supplier_dropdown,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(24),
                width=560,
                height=620,
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
    
    def delete_part(self, part_id):
        """Delete part with confirmation dialog"""
        
        part = None
        for p in self.parts_data:
            if p.get('id') == part_id:
                part = p
                break
        
        part_name = part.get('name', get_text('this_part')) if part else get_text('this_part')
        WARNING_COLOR = "#DC2626"
        
        def confirm(e):
            try:
                self.client.delete_part(part_id)
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
                            f"คุณต้องการลบ '{part_name}' หรือไม่?",
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