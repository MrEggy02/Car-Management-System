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
        self.items_per_page = 25
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
                    content=ft.Text(get_text('parts_name'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=200,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('parts_stock'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('cost_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=140,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('sell_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=140,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('profit'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('supplier'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
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
    
    def _create_table_row(self, part, index, row_number):
        """Create a single table row"""
        part_id = part.get('id')
        name = part.get('name', '-')
        stock_qty = part.get('stock_qty', 0)
        min_stock = part.get('min_stock', 5)
        cost_price = part.get('cost_price', 0)
        sell_price = part.get('sell_price', 0)
        unit = part.get('unit', get_text('unit'))
        supplier_name = part.get('supplier_name', '-')
        
        is_low_stock = stock_qty <= min_stock
        profit = sell_price - cost_price
        profit_margin = (profit / sell_price * 100) if sell_price > 0 else 0
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        # Stock status badge
        if is_low_stock:
            stock_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.WARNING, size=14, color=ft.Colors.WHITE),
                    ft.Text(f"{stock_qty} {unit}", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                ], spacing=4),
                bgcolor=ft.Colors.RED_500,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        elif stock_qty == 0:
            stock_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CANCEL, size=14, color=ft.Colors.WHITE),
                    ft.Text(f"{stock_qty} {unit}", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                ], spacing=4),
                bgcolor=ft.Colors.GREY_600,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        else:
            stock_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color=ft.Colors.WHITE),
                    ft.Text(f"{stock_qty} {unit}", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                ], spacing=4),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        
        # Profit badge
        if profit > 0:
            profit_color = ft.Colors.GREEN_700
            profit_bg = "#E8F5E9"
        elif profit < 0:
            profit_color = ft.Colors.RED_600
            profit_bg = "#FFEBEE"
        else:
            profit_color = ft.Colors.GREY_600
            profit_bg = "#F5F5F5"
        
        profit_badge = ft.Container(
            content=ft.Column([
                ft.Text(f"+{int(profit):,} KIP", size=12, weight=ft.FontWeight.W_600, color=profit_color),
                ft.Text(f"({profit_margin:.1f}%)", size=9, color=profit_color),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
            bgcolor=profit_bg,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
        )
        
        # Status badge
        if is_low_stock:
            status_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.WARNING, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("low_stock"), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=ft.Colors.ORANGE_600,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        else:
            status_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("normal"), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        
        # Action buttons
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
                    content=ft.Text(name, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
                    width=200,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                    tooltip=name,
                ),
                # Stock
                ft.Container(
                    content=stock_badge,
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
                # Cost Price
                ft.Container(
                    content=ft.Text(f"{int(cost_price):,} KIP", size=12, color=ft.Colors.GREY_600),
                    width=140,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                # Sell Price
                ft.Container(
                    content=ft.Text(f"{int(sell_price):,} KIP", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700),
                    width=140,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                # Profit
                ft.Container(
                    content=profit_badge,
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                # Supplier
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(supplier_name, size=11, color="#64748B", max_lines=1),
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=4,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    ),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                # Status
                ft.Container(
                    content=status_badge,
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                # Actions
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
    
    def update_pagination_controls(self):
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
        """Show add part dialog"""
        
        # Load suppliers for dropdown
        suppliers = []
        try:
            suppliers = self.client.get_suppliers()
        except Exception as err:
            print(f"Error loading suppliers: {err}")
        
        supplier_options = [
            ft.dropdown.Option("", f"-- {get_text('select_supplier')} --")
        ]
        for sup in suppliers:
            supplier_options.append(
                ft.dropdown.Option(str(sup.get('id')), sup.get('name', 'Unknown'))
            )
        
        name = ft.TextField(
            label=f"{get_text('parts_name')} *",
            hint_text="ເຊັ່ນ: ນ້ຳມັນເຄື່ອງ 10w-40",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            autofocus=True,
            prefix_icon=ft.Icons.CATEGORY,
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
            expand=True,
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
            expand=True,
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
            expand=True,
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
            expand=True,
        )
        
        unit = ft.TextField(
            label=get_text("unit"),
            hint_text="ຊິ້ນ, ກະປ໋ອງ, ລິດ",
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
            if name.value and sell_price.value:
                try:
                    supplier_id_val = int(supplier_dropdown.value) if supplier_dropdown.value and supplier_dropdown.value.strip() else None
                    
                    self.client.add_part(
                        name=name.value,
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
                                ft.Text(get_text('parts_add'), size=20, weight=ft.FontWeight.BOLD, color="#1E293B"),
                                ft.Text("ເພີ່ມອາໄຫຼ່ໃໝ່", size=13, color="#64748B"),
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
                width=550,
                height=480,
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
    
    def edit_part(self, part_id):
        """Edit part dialog"""
        
        part = None
        for p in self.parts_data:
            if p.get('id') == part_id:
                part = p
                break
        
        if not part:
            self.show_snackbar(f"❌ {get_text('error')}")
            return
        
        # Load suppliers
        suppliers = []
        try:
            suppliers = self.client.get_suppliers()
        except Exception as err:
            print(f"Error loading suppliers: {err}")
        
        supplier_options = [
            ft.dropdown.Option("", f"-- {get_text('select_supplier')} --")
        ]
        for sup in suppliers:
            supplier_options.append(
                ft.dropdown.Option(str(sup.get('id')), sup.get('name', 'Unknown'))
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
            expand=True,
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
            expand=True,
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
            expand=True,
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
            expand=True,
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
                    'name': name.value,
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
                        ft.Container(content=ft.Icon(ft.Icons.EDIT, size=28, color=ft.Colors.WHITE), bgcolor=self.primary_color, border_radius=14, padding=ft.padding.all(8)),
                        ft.Column([ft.Text(get_text('parts_edit'), size=20, weight=ft.FontWeight.BOLD, color="#1E293B"), ft.Text("ແກ້ໄຂຂໍ້ມູນອາໄຫຼ່", size=13, color="#64748B")], spacing=2),
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
                width=550,
                height=500,
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
                        ft.Text(f"ທ່ານຕ້ອງການລຶບ '{part_name}' ແທ້ບໍ?", size=16, weight=ft.FontWeight.W_500, color="#1E293B", text_align=ft.TextAlign.CENTER),
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
    
    def show_snackbar(self, message):
        snack = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.GREY_800, duration=3000)
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()