# pages/purchase/stock_movement.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import asyncio  # เพิ่ม import asyncio

from i18n import get_text


class StockMovementContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.current_snackbar = None
        self.movements = []
        self.filtered_movements = []
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.search_field = None
        self.type_filter = None
        self.table_rows = None
        self.pagination_container = None

    def build(self):
        header = self._build_header()
        search_bar = self._build_search_bar()
        table = self._build_table()
        self.pagination_container = ft.Container(padding=ft.Padding(left=20, right=20, top=12, bottom=12))
        
        content_area = ft.Container(
            content=ft.Column([
                search_bar,
                table,
                self.pagination_container,
            ], expand=True),
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.page.run_task(self._load_data_async)
        
        return main_content

    async def _load_data_async(self):
        await asyncio.sleep(0.1)
        await asyncio.to_thread(self.load_movements)
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=24,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("dashboard"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("stock_movement_title"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    
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
    
    def _build_search_bar(self):
        self.type_filter = ft.Dropdown(
            hint_text=get_text("filter_by_type"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option("all", get_text("all_type")),
                ft.dropdown.Option("IN", get_text("stock_in")),
                ft.dropdown.Option("OUT", get_text("stock_out")),
            ],
            value="all",
            expand=True,
        )
        self.type_filter.on_change = self.filter_movements
        
        self.search_field = ft.TextField(
            hint_text=get_text("search_stock_movement"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
        )
        self.search_field.on_change = self.search_movements
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_movements(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        return ft.Container(
            content=ft.Row([self.type_filter, self.search_field, refresh_button], spacing=10),
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
        )
    
    def _build_table(self):
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("part_id"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=80,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("part_name"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=180,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("type"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=90,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("quantity"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=10, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("reference"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=150,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Wrap table in a Row with horizontal scroll
        table_container = ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                self.table_rows,
            ], spacing=0),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
        )
        
        return ft.Container(
            content=ft.Row([table_container], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
        )
    
    def load_movements(self):
        self.table_rows.controls.clear()
        self.page.update()
        
        try:
            movements = self.client.get_stock_movements(limit=200)
            print(f"DEBUG: Loaded {len(movements)} movements")
            self.movements = movements
            self.filtered_movements = movements.copy()
            self.display_movements()
        except Exception as ex:
            print(f"Error loading movements: {ex}")
            import traceback
            traceback.print_exc()
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                        ft.Text(f"Error: {str(ex)}", size=14, color=ft.Colors.RED_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
            )
            self.page.update()
    
    def filter_movements(self, e):
        movement_type = self.type_filter.value
        if movement_type and movement_type != "all":
            self.filtered_movements = [m for m in self.movements if m.get("type") == movement_type]
        else:
            self.filtered_movements = self.movements.copy()
        self.current_page = 1
        self.display_movements()
    
    def search_movements(self, e):
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        if keyword:
            self.filtered_movements = [
                m for m in self.movements
                if keyword in str(m.get("part_id", "")).lower()
                or keyword in m.get("part_name", "").lower()
            ]
        else:
            self.filtered_movements = self.movements.copy()
        
        if self.type_filter.value != "all":
            self.filtered_movements = [m for m in self.filtered_movements if m.get("type") == self.type_filter.value]
        
        self.current_page = 1
        self.display_movements()
    
    def display_movements(self):
        self.table_rows.controls.clear()
        
        total_items = len(self.filtered_movements)
        
        if total_items == 0:
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.HISTORY, size=48, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_stock_movements"), size=16, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
            )
            self.update_pagination()
            self.page.update()
            return
        
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_movements[start_idx:end_idx]
        
        for i, movement in enumerate(page_items):
            self.table_rows.controls.append(self._create_movement_row(movement, start_idx + i))
        
        self.update_pagination()
        self.page.update()
    
    def _create_movement_row(self, movement: Dict, index: int):
        date = movement.get("date", "")
        if date:
            date = date[:16] if len(date) > 16 else date
        else:
            date = "-"
        
        part_id = movement.get("part_id", "")
        part_id_display = f"#{part_id}" if part_id else "-"
        
        part_name = movement.get("part_name", "-")
        movement_type = movement.get("type", "IN")
        qty = movement.get("qty", 0)
        ref_type = movement.get("ref_type", "-")
        ref_id = movement.get("ref_id", "")
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        if movement_type == "IN":
            type_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARROW_DOWNWARD, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("stock_in"), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=ft.Colors.GREEN_600,
                border_radius=12,
                padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            )
            qty_color = ft.Colors.GREEN_700
            qty_prefix = "+"
        else:
            type_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARROW_UPWARD, size=14, color=ft.Colors.WHITE),
                    ft.Text(get_text("stock_out"), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=ft.Colors.RED_600,
                border_radius=12,
                padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            )
            qty_color = ft.Colors.RED_700
            qty_prefix = "-"
        
        # Reference display
        if ref_type == "purchase":
            ref_text = f"{get_text('purchase_order')} #{ref_id}"
        elif ref_type == "repair":
            ref_text = f"{get_text('repair')} #{ref_id}"
        else:
            ref_text = ref_type
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(date, size=12, color="#64748B"),
                    width=130,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(part_id_display, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=80,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(part_name, size=13, color="#1E293B", max_lines=1),
                    width=180,
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=type_badge,
                    width=90,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(f"{qty_prefix}{qty}", size=13, weight=ft.FontWeight.BOLD, color=qty_color),
                    width=100,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=10, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(ref_text, size=12, color="#64748B"),
                    width=150,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
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
                    f"{get_text('showing')} {len(self.filtered_movements)} {get_text('of')} {len(self.movements)} {get_text('results')}",
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
                            padding=ft.Padding(left=15, right=15, top=0, bottom=0),
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
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_movements()
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_movements()
    
    def show_snack_bar(self, message: str, type="success"):
        """Show snackbar notification - Bottom center with auto width"""
        
        # Remove existing snackbar if any
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
        
        # Create snackbar content with auto width
        snack_content = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=ft.Colors.WHITE, size=16),
                    ft.Text(message, color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.W_500),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=8, bottom=8),
            bgcolor=bgcolor,
            border_radius=8,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            ),
        )
        
        # Create overlay container - positioned at bottom center
        snackbar = ft.Container(
            content=snack_content,
            margin=ft.Margin(left=30, right=30, top=0, bottom=20),
            alignment=ft.Alignment(0, 1),  # Bottom Center
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            opacity=0,
        )
        
        # Add to overlay
        self.page.overlay.append(snackbar)
        self.current_snackbar = snackbar
        
        # Animate in
        snackbar.opacity = 1
        self.page.update()
        
        # Auto dismiss after 3 seconds using asyncio
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
        
        # Run the dismiss task
        self.page.run_task(dismiss_after_delay)