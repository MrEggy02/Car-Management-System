# pages/purchase/purchase_order_create.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable, List
import asyncio

from i18n import get_text


class PurchaseOrderCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable,
                 content_container: ft.Container = None, part_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.content_container = content_container
        self.part_id = part_id
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.current_snackbar = None
        self.suppliers = []
        self.parts = []
        self.categories = []
        self.selected_supplier_id = None
        self.selected_category_id = None
        self.items = []
        self.items_list = None
        self.parts_search = None
        self.parts_results = None
        self.supplier_dropdown = None
        self.category_dropdown = None
        self.total_text = None
        self.content_area = None
        self.create_btn = None
        self.selected_items_container = None

    def build(self):
        # Header
        self.create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("save_purchase_order"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=8),
            on_click=self.create_purchase_order,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=0,
                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
            ),
        )
        
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=20,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("purchase_order_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("purchase_order_create_title"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    self.create_btn,
                ],
                spacing=12,
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
        
        # Content area with loading
        self.content_area = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.load_data()
        
        return main_content
    
    def load_data(self):
        try:
            self.suppliers = self.client.get_suppliers()
            self.parts = self.client.get_parts()
            try:
                self.categories = self.client.get_active_part_categories()
            except:
                self.categories = []
            self._build_form()
        except Exception as ex:
            print(f"Error loading data: {ex}")
            self._show_error(str(ex))
    
    def _show_error(self, message):
        error_content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                ft.Text(f"{get_text('error')}: {message}", size=14, color=ft.Colors.RED_600),
                ft.Container(height=16),
                ft.ElevatedButton(
                    content=ft.Text(get_text("retry")),
                    on_click=lambda e: self.load_data(),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=ft.Padding(left=30, right=30, top=30, bottom=30),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
        )
        self.content_area.content = error_content
        self.page.update()
    
    def _build_form(self):
        # ==================== LEFT COLUMN: SUPPLIER ====================
        supplier_options = [
            ft.dropdown.Option("", f"-- {get_text('select_supplier')} --")
        ]
        for supplier in self.suppliers:
            supplier_options.append(
                ft.dropdown.Option(
                    str(supplier.get('id')),
                    supplier.get('name', '')
                )
            )
        
        self.supplier_dropdown = ft.Dropdown(
            label=get_text("supplier"),
            options=supplier_options,
            expand=True,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        )
        
        apply_supplier_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SEARCH, size=16, color=ft.Colors.WHITE),
                ft.Text(get_text("select") if get_text("select") != "select" else "ບັນທຶກ", size=13, color=ft.Colors.WHITE),
            ], spacing=6, tight=True),
            on_click=self.apply_supplier_filter,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=0,
                padding=ft.Padding(left=14, right=14, top=12, bottom=12),
            ),
        )
        
        supplier_section = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.BUSINESS, size=16, color=self.primary_color), ft.Text(get_text("supplier_info"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B")], spacing=6),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=8),
                ft.Row([self.supplier_dropdown, apply_supplier_btn], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=0),
            padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            expand=True,
        )
        
        left_column = ft.Container(
            content=supplier_section,
            width=350,
            expand=True,
        )
        
        # ==================== RIGHT COLUMN: SEARCH PARTS ====================
        self.parts_search = ft.TextField(
            hint_text=get_text("search_part_to_order"),
            border_radius=20,
            bgcolor=ft.Colors.GREY_100,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.TRANSPARENT,
            content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            on_change=self.search_parts,
        )
        
        self.category_chips_row = ft.Row(wrap=True, spacing=6, run_spacing=6)
        self._build_category_chips()
        
        search_row = ft.Row([
            self.parts_search,
        ], spacing=8)
        
        self.parts_results = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=300)
        
        search_section = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.SHOPPING_CART, size=16, color=self.primary_color), ft.Text(get_text("select_parts"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B")], spacing=6),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=8),
                search_row,
                ft.Container(height=6),
                self.category_chips_row,
                ft.Container(height=8),
                ft.Container(
                    content=self.parts_results,
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                    border_radius=10,
                    padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                    bgcolor=ft.Colors.GREY_50,
                    expand=True,
                ),
            ], spacing=0, expand=True),
            padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            expand=True,
        )
        
        right_column = ft.Container(
            content=search_section,
            width=420,
            expand=True,
        )
        
        # ==================== BOTTOM: SELECTED ITEMS ====================
        self.items_list = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, height=180)
        self.total_text = ft.Text("0 KIP", size=15, weight=ft.FontWeight.BOLD, color=self.success_color)
        
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("#", size=11, weight=ft.FontWeight.BOLD, color="#64748B"), width=35, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("item_name"), size=11, weight=ft.FontWeight.BOLD, color="#64748B"), expand=True, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=6, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text("qty"), size=11, weight=ft.FontWeight.BOLD, color="#64748B"), width=60, alignment=ft.Alignment(0, 0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=8, bottom=8),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=6, top_right=6),
        )
        
        selected_items_section = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.LIST_ALT, size=16, color=self.primary_color), ft.Text(get_text("selected_items"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"), ft.Container(expand=True),
                    ft.Container(content=ft.Row([ft.Text(get_text("total_amount") + ":", size=12, color="#64748B"), self.total_text], spacing=6), padding=ft.Padding(left=8, right=8, top=4, bottom=4), bgcolor=ft.Colors.GREY_50, border_radius=16)],
                    spacing=6),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=6),
                ft.Container(
                    content=ft.Column([table_header, ft.Divider(height=1, color=ft.Colors.GREY_200), self.items_list]),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                    border_radius=6,
                ),
            ], spacing=0),
            padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.Margin(left=0, right=0, top=12, bottom=0),
        )
        
        # ==================== TWO COLUMNS ROW ====================
        two_columns_row = ft.Row(
            [left_column, ft.VerticalDivider(width=1, color=ft.Colors.GREY_300), right_column],
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )
        
        big_card = ft.Container(
            content=ft.Column([
                two_columns_row,
                selected_items_section,
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            expand=True,
        )
        
        scrollable_content = ft.Column([big_card], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
        content_area = ft.Container(content=scrollable_content, expand=True, padding=ft.Padding(left=12, right=12, top=12, bottom=12), bgcolor="#F0F2F5")
        
        self.content_area.content = content_area
        
        # Initialize items display
        self.update_items_display()
        # Show all parts initially (no supplier selected yet)
        self.search_parts(None)
        self.page.update()

    def apply_supplier_filter(self, e):
        val = self.supplier_dropdown.value if self.supplier_dropdown else ""
        new_supplier_id = int(val) if val and val != "" else None
        # If items already exist, block manual supplier change
        if self.items and new_supplier_id != self.selected_supplier_id:
            if self.supplier_dropdown:
                self.supplier_dropdown.value = str(self.selected_supplier_id) if self.selected_supplier_id else ""
            self.show_snack_bar(
                "ບໍ່ສາມາດປ່ຽນຜູ້ສະໜອງໄດ້ ກະລຸນາລຶບອາໄຫລ່ທີ່ເລືອກໄວ້ກ່ອນ",
                is_error=True
            )
            self.page.update()
            return
        if new_supplier_id != self.selected_supplier_id:
            self.items = []
            self.update_items_display()
        self.selected_supplier_id = new_supplier_id
        if self.parts_search:
            self.parts_search.value = ""
        self.search_parts(None)
        self.page.update()

    def on_supplier_change(self, e):
        pass  # Replaced by apply_supplier_filter button

    def _build_category_chips(self):
        self.category_chips_row.controls.clear()
        # "All" chip
        all_selected = self.selected_category_id is None
        all_chip = ft.Container(
            content=ft.Text(f"ທັງໝົດ", size=11, color=ft.Colors.WHITE if all_selected else "#1E293B", weight=ft.FontWeight.W_600 if all_selected else ft.FontWeight.NORMAL),
            bgcolor=self.primary_color if all_selected else ft.Colors.GREY_200,
            border_radius=20,
            padding=ft.Padding(left=12, right=12, top=4, bottom=4),
            on_click=lambda e: self.select_category(None),
            ink=True,
        )
        self.category_chips_row.controls.append(all_chip)
        for cat in self.categories:
            cat_id = cat.get('id')
            cat_name = cat.get('name', '')
            selected = self.selected_category_id == cat_id
            chip = ft.Container(
                content=ft.Text(cat_name, size=11, color=ft.Colors.WHITE if selected else "#1E293B", weight=ft.FontWeight.W_600 if selected else ft.FontWeight.NORMAL),
                bgcolor=self.primary_color if selected else ft.Colors.GREY_200,
                border_radius=20,
                padding=ft.Padding(left=12, right=12, top=4, bottom=4),
                on_click=lambda e, cid=cat_id: self.select_category(cid),
                ink=True,
            )
            self.category_chips_row.controls.append(chip)

    def select_category(self, category_id):
        self.selected_category_id = category_id
        self._build_category_chips()
        self.search_parts(None)
        self.page.update()

    def on_category_change(self, e):
        val = e.control.value
        if val and val != "":
            try:
                self.selected_category_id = int(val)
            except (ValueError, TypeError):
                self.selected_category_id = None
        else:
            self.selected_category_id = None
        self.search_parts(None)
        self.page.update()

    def search_parts(self, e):
        keyword = ""
        if self.parts_search and self.parts_search.value:
            keyword = self.parts_search.value.lower().strip()
        self.parts_results.controls.clear()
        
        # If supplier already selected, show only that supplier's parts
        if self.selected_supplier_id:
            results = [p for p in self.parts if p.get("supplier_id") == self.selected_supplier_id]
        else:
            # No supplier yet — show all parts
            results = list(self.parts)
            
        # Filter by category if selected
        if self.selected_category_id is not None:
            results = [p for p in results if int(p.get("category_id") or 0) == self.selected_category_id]
        
        # Further filter by keyword if provided
        if keyword:
            results = [p for p in results if keyword in p.get("name", "").lower()]
        
        if results:
            for part in results[:50]:
                part_id = part.get('id')
                part_name = part.get('name', '')
                category_name = part.get('category_name') or "ບໍ່ລະບຸປະເພດ"
                supplier_name = part.get('supplier_name') or "ບໍ່ລະບຸຜູ້ສະໜອງ"
                current_stock = part.get('stock_qty', 0)
                min_stock = part.get('min_stock', 5)
                
                already_added = any(item['part_id'] == part_id for item in self.items)
                
                if current_stock <= min_stock:
                    stock_color = "#EF4444"
                    stock_bg = "#FEE2E2"
                    stock_text = f"⚠️ {get_text('low_stock')}: {current_stock}"
                else:
                    stock_color = "#10B981"
                    stock_bg = "#D1FAE5"
                    stock_text = f"{get_text('stock')}: {current_stock}"
                
                add_btn = ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    icon_size=24,
                    icon_color=self.primary_color if not already_added else ft.Colors.GREY_400,
                    on_click=lambda e, pid=part_id, pname=part_name: self.show_add_item_dialog(pid, pname),
                    disabled=already_added,
                )
                
                item_card = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.INVENTORY_2, size=24, color=self.primary_color),
                            bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                            border_radius=10,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Column([
                            ft.Text(part_name, size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                            ft.Text(f"{get_text('category')}: {category_name} | {get_text('supplier')}: {supplier_name}", size=11, color="#64748B"),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(stock_text, size=10, color=stock_color),
                                    bgcolor=stock_bg,
                                    border_radius=10,
                                    padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                                ),
                            ], spacing=6),
                        ], expand=True, spacing=3),
                        add_btn,
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                )
                self.parts_results.controls.append(item_card)
        else:
            empty_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX, size=40, color="#CBD5E1"),
                    ft.Text(get_text("no_parts_found"), size=13, color="#94A3B8"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                alignment=ft.Alignment(0, 0),
                padding=ft.Padding(left=30, right=30, top=30, bottom=30),
            )
            self.parts_results.controls.append(empty_container)
        
        self.page.update()
    
    def show_add_item_dialog(self, part_id, part_name):
        qty_field = ft.TextField(
            label=get_text("order_qty"),
            value="1",
            width=200,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            expand=True,
        )
        
        def confirm_add(e):
            qty = int(qty_field.value) if qty_field.value else 1
            
            if qty <= 0:
                self.show_snack_bar(get_text("quantity_must_be_positive"), is_error=True)
                return
            
            # Check if part already in list
            for i, item in enumerate(self.items):
                if item['part_id'] == part_id:
                    self.items[i]['qty'] = qty
                    dialog.open = False
                    self.update_items_display()
                    self.show_snack_bar(get_text("part_updated_success"), is_error=False)
                    return
            
            self.items.append({
                'part_id': part_id,
                'part_name': part_name,
                'qty': qty,
            })
            dialog.open = False
            self.update_items_display()
            
            # Auto-select supplier from the added part (if not already set)
            if not self.selected_supplier_id:
                selected_part = next((p for p in self.parts if p.get('id') == part_id), None)
                if selected_part:
                    auto_supplier_id = selected_part.get('supplier_id')
                    if auto_supplier_id:
                        self.selected_supplier_id = auto_supplier_id
                        if self.supplier_dropdown:
                            self.supplier_dropdown.value = str(auto_supplier_id)
                        if self.parts_search:
                            self.parts_search.value = ""
                        self.search_parts(None)
            
            # Lock supplier dropdown while items exist
            if self.supplier_dropdown and self.items:
                self.supplier_dropdown.disabled = True
            
            self.show_snack_bar(f"{get_text('added')}: {part_name}", is_error=False)
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=14),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.INVENTORY, size=22, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=10,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(
                            get_text("add_to_order"),
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(part_name, size=13, weight=ft.FontWeight.W_500, color=self.primary_color),
                    ft.Container(height=10),
                    ft.Row([qty_field], expand=True),
                ]),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                width=320,
                height=140,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self._close_dialog(dialog), style=ft.ButtonStyle(color="#64748B")),
                ft.ElevatedButton(get_text("add"), on_click=confirm_add, style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=6))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def _open_dialog(self, dialog):
        self.page.show_dialog(dialog)
    
    def _close_dialog(self, dialog):
        self.page.pop_dialog()
    
    def update_items_display(self):
        self.items_list.controls.clear()
        total = 0
        
        if not self.items:
            empty_row = ft.Container(
                content=ft.Text(get_text("no_items_added"), size=13, color="#94A3B8"),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                alignment=ft.Alignment(0, 0),
            )
            self.items_list.controls.append(empty_row)
            self.total_text.value = "0 KIP"
            self.page.update()
            return
        
        for idx, item in enumerate(self.items):
            bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
            
            row = ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Text(str(idx + 1), size=12, color="#64748B"), width=35, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(item.get('part_name', '-'), size=12, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1), expand=True, padding=ft.Padding(left=6, right=0, top=0, bottom=0)),
                    ft.Container(content=ft.Text(f"x{item.get('qty', 1)}", size=12, color="#1E293B"), width=60, alignment=ft.Alignment(0, 0)),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color="#EF4444",
                        on_click=lambda e, idx_i=idx: self.remove_item(idx_i),
                        padding=0,
                    ),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=10, right=10, top=6, bottom=6),
                bgcolor=bg_color,
            )
            self.items_list.controls.append(row)
            total += item.get('qty', 0)
        
        subtotal_row = ft.Container(
            content=ft.Row([
                ft.Container(expand=True),
                ft.Text(get_text("total_qty") + ":", size=12, weight=ft.FontWeight.W_500, color="#64748B"),
                ft.Text(f"{total} {get_text('items')}", size=12, weight=ft.FontWeight.W_600, color="#1E293B"),
            ], spacing=6),
            padding=ft.Padding(left=10, right=10, top=5, bottom=5),
            bgcolor=ft.Colors.GREY_100,
        )
        self.items_list.controls.append(subtotal_row)
        
        self.total_text.value = f"{total} {get_text('items')}"
        self.page.update()
    
    def remove_item(self, index):
        if 0 <= index < len(self.items):
            removed = self.items.pop(index)
            # If no items left, unlock supplier dropdown and reset supplier
            if not self.items:
                self.selected_supplier_id = None
                if self.supplier_dropdown:
                    self.supplier_dropdown.disabled = False
                    self.supplier_dropdown.value = ""
                if self.parts_search:
                    self.parts_search.value = ""
                self.search_parts(None)
            self.update_items_display()
            self.show_snack_bar(f"{get_text('part_removed')}: {removed['part_name']}", is_error=False)
    
    def create_purchase_order(self, e):
        if self.create_btn:
            self.create_btn.disabled = True
        
        if not self.supplier_dropdown.value or self.supplier_dropdown.value == "":
            self.show_snack_bar(get_text("please_select_supplier_first"), is_error=True)
            if self.create_btn:
                self.create_btn.disabled = False
            return
        
        if not self.items:
            self.show_snack_bar(get_text("please_add_at_least_one_item"), is_error=True)
            if self.create_btn:
                self.create_btn.disabled = False
            return
        
        items_data = []
        for item in self.items:
            items_data.append({
                "part_id": item['part_id'],
                "qty": item['qty'],
                "unit_cost": 0  # ສົ່ງ 0 ເພາະບໍ່ມີການປ້ອນລາຄາ
            })
        
        try:
            result = self.client.create_purchase_order(
                supplier_id=int(self.supplier_dropdown.value),
                items=items_data
            )
            if result and result.get('id'):
                self.show_success_popup(result.get('po_no'))
            else:
                self.show_snack_bar(get_text("create_failed"), is_error=True)
                if self.create_btn:
                    self.create_btn.disabled = False
        except Exception as ex:
            print(f"Error creating PO: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
            if self.create_btn:
                self.create_btn.disabled = False
        
        self.page.update()
    
    def show_success_popup(self, po_no):
        def go_to_list(e):
            popup.open = False
            self.navigate("purchase_order_list")
            if self.create_btn:
                self.create_btn.disabled = False
        
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=14),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.success_color,
                            border_radius=10,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(
                            get_text("success"),
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(height=6),
                    ft.Text(
                        get_text("po_created_success"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color="#1E293B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=6),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOCAL_SHIPPING, size=14, color=self.primary_color),
                            ft.Text(
                                f"{get_text('po_number')}: {po_no}",
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=self.primary_color,
                            ),
                        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                        border_radius=8,
                    ),
                    ft.Container(height=6),
                    ft.Text(
                        get_text("go_to_list_message"),
                        size=12,
                        color="#64748B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                width=360,
                height=180,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            get_text("go_to_list"),
                            on_click=go_to_list,
                            style=ft.ButtonStyle(
                                bgcolor=self.primary_color,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=6),
                                padding=ft.Padding(left=20, right=20, top=8, bottom=8),
                            ),
                        ),
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        """Show snackbar notification - Bottom center with auto width"""
        
        # Remove existing snackbar if any
        if self.current_snackbar:
            try:
                self.page.overlay.remove(self.current_snackbar)
            except:
                pass
            self.current_snackbar = None
        
        if not is_error:
            bgcolor = ft.Colors.GREEN_600
            icon = ft.Icons.CHECK_CIRCLE
        else:
            bgcolor = ft.Colors.RED_600
            icon = ft.Icons.ERROR
        
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