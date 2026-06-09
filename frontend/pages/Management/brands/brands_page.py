import flet as ft
from flet import Alignment
from typing import Dict, Callable
from i18n import get_text
from Management.brands.brands_dialogs import BrandsDialogs


class BrandsPageContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
        # Data storage
        self.brands_data = []
        self.filtered_brands = []
        
        # Search field
        self.search_input = None
        
        # Table row container
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Pagination
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.pagination_container = ft.Container()
        
        # Dialogs helper
        self.dialogs = BrandsDialogs(self)
        
        self.current_dialog = None
        self.is_loading = False

    def build(self):
        # Header with gradient
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("brands_title"),
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
                            ft.Text(get_text("add_brand"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.dialogs.show_add_dialog(),
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
        
        # Search Bar - same as services page
        self.search_input = ft.TextField(
            hint_text=f" {get_text('search_brands')}",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            on_change=self.filter_brands,
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
        
        # Table header
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
        
        self.load_brands()
        
        return ft.Column([
            header,
            control_bar,
            main_content,
        ], expand=True, spacing=0)
    
    def _create_table_header(self):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=60,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("brand_name"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=300,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("actions"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=150,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=14, horizontal=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _create_table_row(self, brand: Dict, index: int, row_number: int):
        name = brand.get("name", "-")
        status = brand.get("status", "active")
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        status_badge = self._create_status_badge(status)
        
        edit_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=self.primary_color), ft.Text(get_text("edit"), size=12, color=self.primary_color)], spacing=4),
            on_click=lambda e, bid=brand.get("id"): self.dialogs.show_edit_dialog(bid),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        delete_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600), ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600)], spacing=4),
            on_click=lambda e, bid=brand.get("id"): self.dialogs.show_delete_dialog(bid),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(str(row_number), size=13, weight=ft.FontWeight.W_500, color=self.primary_color),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=6,
                        alignment=ft.Alignment(0, 0),
                    ),
                    width=60,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(name, size=13, color="#1E293B", max_lines=1),
                    width=300,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                    tooltip=name,
                ),
                ft.Container(
                    content=status_badge,
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Row([edit_btn, delete_btn], spacing=8),
                    width=150,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=10),
            bgcolor=row_bg,
        )
        
        return ft.Column([row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0)
    
    def _create_status_badge(self, status):
        if status == "active":
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color="#2E7D32"),
                    ft.Text(get_text("status_active"), size=11, color="#2E7D32"),
                ], spacing=4),
                bgcolor="#E8F5E9",
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        else:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color="#DC2626"),
                    ft.Text(get_text("status_inactive"), size=11, color="#DC2626"),
                ], spacing=4),
                bgcolor="#FFEEEE",
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
    
    def _create_empty_state(self):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.BRANDING_WATERMARK, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_brands_found"), size=16, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add_to_register"), size=13, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(40),
            expand=True,
        )
    
    def update_pagination_controls(self):
        if not self.filtered_brands:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (len(self.filtered_brands) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Container(
            content=ft.Row([
                ft.Text(f"{get_text('showing')} {len(self.filtered_brands)} {get_text('of')} {len(self.brands_data)} {get_text('results')}", size=12, color="#64748B"),
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
            self.display_brands()
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_brands()
    
    def filter_brands(self, e=None):
        query = self.search_input.value.lower() if self.search_input.value else ""
        self.current_page = 1
        
        if not query:
            self.filtered_brands = self.brands_data.copy()
        else:
            self.filtered_brands = [b for b in self.brands_data if query in b.get('name', '').lower()]
        
        self.display_brands()
    
    def display_brands(self):
        self.table_rows.controls.clear()
        
        if not self.filtered_brands:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_brands = self.filtered_brands[start_idx:end_idx]
            
            global_start = start_idx + 1
            
            for i, brand in enumerate(page_brands):
                row_number = global_start + i
                row = self._create_table_row(brand, start_idx + i, row_number)
                self.table_rows.controls.append(row)
        
        self.update_pagination_controls()
        self.page.update()
    
    def load_brands(self):
        try:
            self.brands_data = self.client.get_brands() or []
            self.filtered_brands = self.brands_data.copy()
            self.display_brands()
        except Exception as ex:
            print(f"Error loading brands: {ex}")
            self.table_rows.controls.clear()
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
    
    def show_snackbar(self, message, is_error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=3000,
        )
        self.page.update()