# pages/Management/master_data/master_data_page.py
import flet as ft
import asyncio
import traceback
from i18n import get_text
from pages.Management.master_data.master_data_dialogs import MasterDataDialogs


class MasterDataContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
        # Data storage
        self.brands_data = []
        self.units_data = []
        self.categories_data = []
        
        # Filtered data
        self.filtered_brands = []
        self.filtered_units = []
        self.filtered_categories = []
        
        # Search fields
        self.brand_search = None
        self.unit_search = None
        self.category_search = None
        
        # Dialogs helper
        self.dialogs = MasterDataDialogs(self)
        
        # Table row containers
        self.brands_table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.units_table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.categories_table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        
        self.is_loading = False
        self.loading_overlay = None

    def build(self):
        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("master_data_title"),
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
                            ft.Icon(ft.Icons.REFRESH, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("refresh_all"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.load_all_data(),
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
        
        # Create 3 cards horizontally scrollable
        master_cards = ft.Row(
            [
                self._create_brands_card(),
                self._create_units_card(),
                self._create_categories_card(),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
        
        content_area = ft.Container(
            content=master_cards,
            expand=True,
            padding=ft.padding.all(20),
            bgcolor="#F5F7FA",
        )
        
        # Loading overlay
        self.loading_overlay = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=4, color=self.primary_color),
                ft.Container(height=16),
                ft.Text(get_text("loading"), size=14, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
            visible=False,
        )
        
        main_content = ft.Container(
            content=ft.Stack([content_area, self.loading_overlay]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.page.run_task(self._delayed_load)
        return ft.Column([header, main_content], expand=True, spacing=0)
    
    def _create_brands_card(self):
        """Create brands management card"""
        # Title row
        title_row = ft.Row(
            [
                ft.Text(get_text("brands_title"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD, size=16, color=ft.Colors.WHITE),
                        ft.Text(get_text("add_brand"), size=12, color=ft.Colors.WHITE),
                    ], spacing=4),
                    on_click=lambda e: self.dialogs.show_add_dialog("brands"),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, elevation=0, padding=ft.padding.symmetric(horizontal=12, vertical=6)),
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Search field - reduced height and proper alignment
        self.brand_search = ft.TextField(
            hint_text=get_text("search_brands"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            suffix=ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_size=14,
                icon_color=ft.Colors.GREY_500,
                on_click=lambda e: self._clear_brand_search(),
            ),
            on_change=self.filter_brands,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_color=ft.Colors.GREY_200,
            text_size=12,
            height=38,
        )
        
        # Table header
        table_header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(content=ft.Text("#", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=40, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(get_text("brand_name"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=160, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=8)),
                    ft.Container(content=ft.Text(get_text("status"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=70, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(get_text("action"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(0, 0)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=8, horizontal=8),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=8, top_right=8),
        )
        
        # Table body
        table_body = ft.Container(
            content=self.brands_table_rows,
            height=450,
        )
        
        table_container = ft.Container(
            content=ft.Column([table_header, ft.Divider(height=1, color=ft.Colors.GREY_200), table_body], spacing=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )
        
        return ft.Container(
            content=ft.Column([
                title_row,
                ft.Container(height=6),
                self.brand_search,
                ft.Container(height=8),
                table_container,
            ]),
            width=400,
            padding=ft.padding.all(8),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        )
    
    def _create_units_card(self):
        """Create units management card"""
        title_row = ft.Row(
            [
                ft.Text(get_text("units_title"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD, size=16, color=ft.Colors.WHITE),
                        ft.Text(get_text("add_unit"), size=12, color=ft.Colors.WHITE),
                    ], spacing=4),
                    on_click=lambda e: self.dialogs.show_add_dialog("units"),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, elevation=0, padding=ft.padding.symmetric(horizontal=12, vertical=6)),
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        self.unit_search = ft.TextField(
            hint_text=get_text("search_units"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            suffix=ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_size=14,
                icon_color=ft.Colors.GREY_500,
                on_click=lambda e: self._clear_unit_search(),
            ),
            on_change=self.filter_units,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_color=ft.Colors.GREY_200,
            text_size=12,
            height=38,
        )
        
        table_header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(content=ft.Text("#", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=40, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(get_text("unit_name"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=160, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=8)),
                    ft.Container(content=ft.Text(get_text("status"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=70, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(get_text("action"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(0, 0)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=8, horizontal=8),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=8, top_right=8),
        )
        
        table_body = ft.Container(content=self.units_table_rows, height=450)
        table_container = ft.Container(
            content=ft.Column([table_header, ft.Divider(height=1, color=ft.Colors.GREY_200), table_body], spacing=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )
        
        return ft.Container(
            content=ft.Column([title_row, ft.Container(height=6), self.unit_search, ft.Container(height=8), table_container]),
            width=400,
            padding=ft.padding.all(8),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        )
    
    def _create_categories_card(self):
        """Create part categories management card"""
        title_row = ft.Row(
            [
                ft.Text(get_text("part_categories_title"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD, size=16, color=ft.Colors.WHITE),
                        ft.Text(get_text("add_category"), size=12, color=ft.Colors.WHITE),
                    ], spacing=4),
                    on_click=lambda e: self.dialogs.show_add_dialog("categories"),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, elevation=0, padding=ft.padding.symmetric(horizontal=12, vertical=6)),
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        self.category_search = ft.TextField(
            hint_text=get_text("search_categories"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            suffix=ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_size=14,
                icon_color=ft.Colors.GREY_500,
                on_click=lambda e: self._clear_category_search(),
            ),
            on_change=self.filter_categories,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_color=ft.Colors.GREY_200,
            text_size=12,
            height=38,
        )
        
        table_header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(content=ft.Text("#", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=40, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(get_text("category_name"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=160, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=8)),
                    ft.Container(content=ft.Text(get_text("status"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=70, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(get_text("action"), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(0, 0)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=8, horizontal=8),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=8, top_right=8),
        )
        
        table_body = ft.Container(content=self.categories_table_rows, height=450)
        table_container = ft.Container(
            content=ft.Column([table_header, ft.Divider(height=1, color=ft.Colors.GREY_200), table_body], spacing=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_200),
        )
        
        return ft.Container(
            content=ft.Column([title_row, ft.Container(height=6), self.category_search, ft.Container(height=8), table_container]),
            width=400,
            padding=ft.padding.all(8),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        )
    
    def _clear_brand_search(self):
        self.brand_search.value = ""
        self.filter_brands()
    
    def _clear_unit_search(self):
        self.unit_search.value = ""
        self.filter_units()
    
    def _clear_category_search(self):
        self.category_search.value = ""
        self.filter_categories()
    
    def _create_table_row(self, item, index, row_number, on_edit, on_delete):
        """Create a table row for any item type"""
        name = item.get("name", "-")
        status = item.get("status", "active")
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        status_badge = self.dialogs.create_status_badge(status)
        
        edit_btn = ft.IconButton(
            icon=ft.Icons.EDIT_OUTLINED,
            icon_size=16,
            icon_color=self.primary_color,
            on_click=lambda e: on_edit(item.get("id")),
            tooltip=get_text("edit"),
            style=ft.ButtonStyle(padding=ft.padding.all(4)),
        )
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_size=16,
            icon_color=ft.Colors.RED_600,
            on_click=lambda e: on_delete(item.get("id")),
            tooltip=get_text("delete"),
            style=ft.ButtonStyle(padding=ft.padding.all(4)),
        )
        
        row = ft.Container(
            content=ft.Row(
                [
                    ft.Container(content=ft.Text(str(row_number), size=12, weight=ft.FontWeight.W_500, color=self.primary_color), width=40, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(name, size=12, color="#1E293B", max_lines=1), width=160, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=8), tooltip=name if len(name) > 20 else None),
                    ft.Container(content=status_badge, width=70, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Row([edit_btn, delete_btn], spacing=0), width=100, alignment=ft.Alignment(0, 0)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=8, horizontal=8),
            bgcolor=row_bg,
        )
        return ft.Column([row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0)
    
    def show_loading(self):
        if self.loading_overlay:
            self.loading_overlay.visible = True
            self.page.update()
    
    def hide_loading(self):
        if self.loading_overlay:
            self.loading_overlay.visible = False
            self.page.update()
    
    async def _delayed_load(self):
        await asyncio.sleep(0.2)
        self.load_all_data()
    
    def load_all_data(self):
        """Load all master data"""
        if self.is_loading:
            return
        self.is_loading = True
        self.show_loading()
        
        try:
            self.brands_data = self.client.get_brands()
            self.filtered_brands = self.brands_data.copy()
            self.display_brands()
            
            self.units_data = self.client.get_units()
            self.filtered_units = self.units_data.copy()
            self.display_units()
            
            self.categories_data = self.client.get_part_categories()
            self.filtered_categories = self.categories_data.copy()
            self.display_categories()
            
        except Exception as e:
            print(f"Error loading master data: {e}")
            traceback.print_exc()
        finally:
            self.is_loading = False
            self.hide_loading()
    
    def display_brands(self):
        self.brands_table_rows.controls.clear()
        if not self.filtered_brands:
            self._show_empty_state(self.brands_table_rows, get_text("no_brands"))
        else:
            for i, brand in enumerate(self.filtered_brands):
                row = self._create_table_row(brand, i, i+1, self.dialogs.edit_brand, self.dialogs.delete_brand)
                self.brands_table_rows.controls.append(row)
        self.page.update()
    
    def display_units(self):
        self.units_table_rows.controls.clear()
        if not self.filtered_units:
            self._show_empty_state(self.units_table_rows, get_text("no_units"))
        else:
            for i, unit in enumerate(self.filtered_units):
                row = self._create_table_row(unit, i, i+1, self.dialogs.edit_unit, self.dialogs.delete_unit)
                self.units_table_rows.controls.append(row)
        self.page.update()
    
    def display_categories(self):
        self.categories_table_rows.controls.clear()
        if not self.filtered_categories:
            self._show_empty_state(self.categories_table_rows, get_text("no_categories"))
        else:
            for i, cat in enumerate(self.filtered_categories):
                row = self._create_table_row(cat, i, i+1, self.dialogs.edit_category, self.dialogs.delete_category)
                self.categories_table_rows.controls.append(row)
        self.page.update()
    
    def _show_empty_state(self, container, message):
        container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX, size=40, color=ft.Colors.GREY_300),
                    ft.Text(message, size=12, color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.all(30),
            )
        )
    
    def filter_brands(self, e=None):
        query = self.brand_search.value.lower() if self.brand_search.value else ""
        if not query:
            self.filtered_brands = self.brands_data.copy()
        else:
            self.filtered_brands = [b for b in self.brands_data if query in b.get('name', '').lower()]
        self.display_brands()
    
    def filter_units(self, e=None):
        query = self.unit_search.value.lower() if self.unit_search.value else ""
        if not query:
            self.filtered_units = self.units_data.copy()
        else:
            self.filtered_units = [u for u in self.units_data if query in u.get('name', '').lower()]
        self.display_units()
    
    def filter_categories(self, e=None):
        query = self.category_search.value.lower() if self.category_search.value else ""
        if not query:
            self.filtered_categories = self.categories_data.copy()
        else:
            self.filtered_categories = [c for c in self.categories_data if query in c.get('name', '').lower()]
        self.display_categories()
    
    def show_snackbar(self, message):
        snack = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.GREY_800, duration=3000)
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()