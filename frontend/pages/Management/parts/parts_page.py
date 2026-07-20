# Management/parts/parts_page.py
import flet as ft
import sys
import os
import asyncio
import traceback
from datetime import datetime

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
        self.current_snackbar = None
        self.parts_data = []
        self.filtered_parts = []
        self.search_input = None
        self.category_chips = None
        self.current_category_id = None
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
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    # Stock History Button
                    ft.IconButton(
                        icon=ft.Icons.HISTORY,
                        icon_size=22,
                        icon_color=ft.Colors.WHITE,
                        tooltip=get_text("stock_history") or "ປະຫວັດການເຄື່ອນໄຫວສາງ",
                        on_click=lambda e: self.navigate("stock_history"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
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
                            padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                        ),
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=24, right=24, top=12, bottom=12),
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
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )

        # Category Chips (without icons)
        self.category_chips = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)

        # Control bar with search
        control_bar = ft.Container(
            content=ft.Column([
                self.search_input,
                ft.Container(height=12),
                self.category_chips,
            ], spacing=0),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor="#F5F7FA",
        )

        # Table Header
        table_header = self._create_table_header()

        # Table body - contains rows
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # Table content with header and rows
        table_content = ft.Column([
            table_header,
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            self.table_rows,
        ], spacing=0, expand=True)

        # Table scroll container - allows horizontal scroll
        table_scroll_container = ft.Container(
            content=table_content,
            bgcolor=ft.Colors.WHITE,
            width=1100,  # Fixed width to enable horizontal scroll
            expand=True,
        )

        # Table Container with both horizontal and vertical scroll
        table_container = ft.Container(
            content=ft.Row([table_scroll_container], scroll=ft.ScrollMode.AUTO, expand=True),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            border_radius=ft.BorderRadius.only(
                top_left=12, top_right=12, bottom_left=12, bottom_right=12
            ),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            bgcolor=ft.Colors.WHITE,
            expand=True,
            height=500,  # Fixed height to enable vertical scroll
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

    # ==================== DIALOG MANAGEMENT ====================
    def _open_dialog(self, dialog):
        try:
            # ปิด dialog เก่าก่อน
            if self.current_dialog:
                self._close_dialog()
            self.current_dialog = dialog
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        except Exception as e:
            print(f"DEBUG: Error opening dialog: {e}")

    def _close_dialog(self, dialog=None):
        try:
            if dialog is None:
                dialog = self.current_dialog
            if dialog:
                # ลบออกจาก overlay ก่อน
                if dialog in self.page.overlay:
                    self.page.overlay.remove(dialog)
                dialog.open = False
                if self.current_dialog == dialog:
                    self.current_dialog = None
                self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")

    # ==================== END DIALOG MANAGEMENT ====================

    def _create_table_header(self):
        """Create table header row with adjusted widths for full price display"""
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=40, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('parts_name'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=160, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text('category'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=90, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text('qty'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=60, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('unit'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=50, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('cost_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=130, alignment=ft.Alignment(1, 0), padding=ft.Padding(left=0, right=8, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text('sell_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=130, alignment=ft.Alignment(1, 0), padding=ft.Padding(left=0, right=8, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text('supplier'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text('status'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=70, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('actions'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=90, alignment=ft.Alignment(0, 0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )

    def _get_unit_name(self, unit_id):
        if not unit_id:
            return "-"
        for unit in self.units:
            if unit.get('id') == unit_id:
                return unit.get('name', '-')
        return "-"

    def _get_category_name(self, category_id):
        if not category_id:
            return "-"
        for cat in self.categories:
            if cat.get('id') == category_id:
                return cat.get('name', '-')
        return "-"

    def _format_price(self, price):
        try:
            price = int(price)
            return f"{price:,} KIP"
        except:
            return "0 KIP"

    def _format_stock(self, stock_qty):
        return str(stock_qty)

    def _create_table_row(self, part, index, row_number):
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

        # Stock status badge
        if is_low_stock:
            stock_badge = ft.Container(
                content=ft.Text(formatted_stock, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.RED_500,
                border_radius=10,
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                alignment=ft.Alignment(0, 0),
            )
        elif stock_qty == 0:
            stock_badge = ft.Container(
                content=ft.Text(formatted_stock, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.GREY_600,
                border_radius=10,
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                alignment=ft.Alignment(0, 0),
            )
        else:
            stock_badge = ft.Container(
                content=ft.Text(formatted_stock, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=10,
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                alignment=ft.Alignment(0, 0),
            )

        # Status badge
        if is_low_stock:
            status_badge = ft.Container(
                content=ft.Text(get_text("low_stock"), size=10, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.ORANGE_600,
                border_radius=8,
                padding=ft.Padding(left=5, right=5, top=2, bottom=2),
            )
        else:
            status_badge = ft.Container(
                content=ft.Text(get_text("normal"), size=10, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=8,
                padding=ft.Padding(left=5, right=5, top=2, bottom=2),
            )

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

        display_name = name[:22] + "..." if len(name) > 22 else name
        display_supplier = supplier_name[:10] + "..." if len(supplier_name) > 10 else supplier_name
        display_category = category_name[:12] + "..." if len(category_name) > 12 else category_name
        display_unit = unit_name[:5] + "..." if len(unit_name) > 5 else unit_name

        row = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(str(row_number), size=12, weight=ft.FontWeight.W_500, color=self.primary_color), width=40, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(display_name, size=12, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1), width=160, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0), tooltip=name),
                ft.Container(content=ft.Text(display_category, size=11, color="#64748B", max_lines=1), width=90, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0), tooltip=category_name),
                ft.Container(content=stock_badge, width=60, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(display_unit, size=11, color="#64748B"), width=50, alignment=ft.Alignment(0, 0), tooltip=unit_name),
                ft.Container(content=ft.Text(self._format_price(cost_price), size=11, color="#64748B"), width=130, alignment=ft.Alignment(1, 0), padding=ft.Padding(left=0, right=8, top=0, bottom=0)),
                ft.Container(content=ft.Text(self._format_price(sell_price), size=12, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN_700), width=130, alignment=ft.Alignment(1, 0), padding=ft.Padding(left=0, right=8, top=0, bottom=0)),
                ft.Container(content=ft.Text(display_supplier, size=11, color="#64748B", max_lines=1), width=100, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0), tooltip=supplier_name),
                ft.Container(content=status_badge, width=70, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Row([edit_btn, delete_btn], spacing=4), width=90, alignment=ft.Alignment(0, 0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
            bgcolor=row_bg,
        )
        return ft.Column([row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0)

    def _create_empty_state(self):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PRECISION_MANUFACTURING, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_data"), size=16, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add"), size=13, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=40, right=40, top=40, bottom=40),
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
                        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_size=20, on_click=self.prev_page, disabled=prev_disabled, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                        ft.Container(content=ft.Text(f"{self.current_page}/{self.total_pages}", size=13, weight=ft.FontWeight.W_500, color="#1E293B"), padding=ft.Padding(left=15, right=15, top=0, bottom=0)),
                        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_size=20, on_click=self.next_page, disabled=next_disabled, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                    ]),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=20, right=20, top=16, bottom=16),
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
        filtered = self.parts_data.copy()
        if query:
            filtered = [part for part in filtered if query in part.get('name', '').lower() or (part.get('supplier_name') and query in part.get('supplier_name', '').lower())]
        if self.current_category_id:
            filtered = [part for part in filtered if part.get('category_id') == self.current_category_id]
        self.filtered_parts = filtered
        self.display_parts(self.filtered_parts)

    def filter_by_category(self, category_id):
        self.current_category_id = category_id
        self.load_category_chips()
        self.filter_parts()

    def load_category_chips(self):
        self.category_chips.controls.clear()
        all_chip = ft.Container(
            content=ft.Text(get_text("all_items"), size=12, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE if self.current_category_id is None else "#64748B"),
            bgcolor=self.primary_color if self.current_category_id is None else ft.Colors.GREY_200,
            border_radius=20,
            padding=ft.Padding(left=14, right=14, top=6, bottom=6),
            ink=True,
            on_click=lambda e: self.filter_by_category(None),
        )
        self.category_chips.controls.append(all_chip)
        for cat in self.categories:
            if cat.get('status') == 'active':
                is_active = self.current_category_id == cat.get('id')
                chip = ft.Container(
                    content=ft.Text(cat.get('name', '-'), size=12, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE if is_active else "#64748B"),
                    bgcolor=self.primary_color if is_active else ft.Colors.GREY_200,
                    border_radius=20,
                    padding=ft.Padding(left=14, right=14, top=6, bottom=6),
                    ink=True,
                    on_click=lambda e, cid=cat.get('id'): self.filter_by_category(cid),
                )
                self.category_chips.controls.append(chip)
        self.page.update()

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
        await asyncio.to_thread(self.load_data)

    def load_data(self, force=False):
        if self.is_loading and not force:
            return
        self.is_loading = True
        try:
            self.units = self.client.get_units() or []
            self.categories = self.client.get_part_categories() or []
            self.suppliers = self.client.get_suppliers() or []
            print(f"DEBUG: Loaded {len(self.units)} units, {len(self.categories)} categories, {len(self.suppliers)} suppliers")
            self.load_category_chips()
            self.parts_data = self.client.get_parts() or []
            self.filtered_parts = self.parts_data.copy()
            print(f"DEBUG: Loaded {len(self.parts_data)} parts")
            self.display_parts(self.filtered_parts)
        except Exception as e:
            print(f"DEBUG: Error loading parts: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
        finally:
            self.is_loading = False

    def _safe_edit(self, part_id, event):
        try:
            self.edit_part(part_id)
        except Exception as e:
            print(f"DEBUG: Error in edit: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")

    def _safe_delete(self, part_id, event):
        try:
            self.delete_part(part_id)
        except Exception as e:
            print(f"DEBUG: Error in delete: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")

    def show_add_dialog(self):
        active_units = [u for u in self.units if u.get('status') == 'active']
        active_categories = [c for c in self.categories if c.get('status') == 'active']
        self.dialogs.show_add_dialog(active_units, active_categories, self.suppliers)

    def edit_part(self, part_id):
        part = None
        for p in self.parts_data:
            if p.get('id') == part_id:
                part = p
                break
        if not part:
            self.show_snackbar(get_text("error"), "error")
            return
        self.dialogs.show_edit_dialog(part, self.units, self.categories, self.suppliers)

    def delete_part(self, part_id):
        part = None
        for p in self.parts_data:
            if p.get('id') == part_id:
                part = p
                break
        part_name = part.get('name', get_text('this_part')) if part else get_text('this_part')
        self.dialogs.show_delete_dialog(part_name, part_id)

    def show_snackbar(self, message, type="success"):
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
        snack_content = ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=ft.Colors.WHITE, size=16),
                ft.Text(message, color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.W_500),
            ], spacing=8, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=14, right=14, top=8, bottom=8),
            bgcolor=bgcolor,
            border_radius=8,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK)),
        )
        snackbar = ft.Container(
            content=snack_content,
            margin=ft.Margin(left=30, right=30, top=0, bottom=20),
            alignment=ft.Alignment(0, 1),
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            opacity=0,
        )
        self.page.overlay.append(snackbar)
        self.current_snackbar = snackbar
        snackbar.opacity = 1
        self.page.update()
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
        self.page.run_task(dismiss_after_delay)