import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime
import asyncio
import functools

from i18n import get_text


class QuotationCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, job_order_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.job_order_id = job_order_id
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
        # Data storage
        self.parts_list = []
        self.services_list = []
        self.pending_orders = []
        self.temp_items = []
        self.temp_id_counter = 0
        self.selected_job_id = None
        
        # UI references
        self.search_field = None
        self.qty_field = None
        self.results_list = None
        self.items_table_body = None
        self.total_text = ft.Text("0 KIP", size=16, weight=ft.FontWeight.BOLD, color="#10B981")
        self.job_info_text = None
        self.job_info_container = None
        self.job_dropdown = None
        self.parts_tab = None
        self.services_tab = None
        self.category_chips = None
        
        # State
        self.current_tab = "parts"
        self.current_category = "all"
        
    def build(self):
        # --- Header with Back Button on Left ---
        header = ft.Container(
            content=ft.Row(
                [
                    # Back button on the left
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ARROW_BACK, size=18, color=ft.Colors.WHITE),
                                
                            ],
                            spacing=6,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=8, vertical=8),
                        on_click=lambda e: self.navigate("quotation_list"),
                        ink=True,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("create_quotation"),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            
                        ],
                        spacing=4,
                    ),
                    ft.Container(expand=True),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                                        ft.Text(get_text("save_quotation"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                                    ],
                                    spacing=8,
                                ),
                                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                                border_radius=30,
                                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                on_click=self.save_quotation,
                                ink=True,
                            ),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=ft.Colors.WHITE),
                                        ft.Text(get_text("approve_quotation"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                                    ],
                                    spacing=8,
                                ),
                                bgcolor="#10B981",
                                border_radius=30,
                                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                on_click=self.approve_quotation,
                                ink=True,
                            ),
                        ],
                        spacing=12,
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=14, horizontal=24),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
        
        # ==================== SECTION 1: JOB ORDER ====================
        self.job_dropdown = ft.Dropdown(
            label=get_text("select_job_order"),
            hint_text=get_text("select_job_order_for_quotation"),
            border_radius=12,
            bgcolor=ft.Colors.GREY_100,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            options=[],
            expand=True,
        )
        self.job_dropdown.on_change = self.on_job_select
        
        self.job_info_text = ft.Text("", size=13, color="#1E293B")
        self.job_info_container = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=self.primary_color),
                        ft.Text("ໃບຮັບລົດທີ່ເລືອກ", size=12, weight=ft.FontWeight.W_500, color="#64748B"),
                    ],
                    spacing=4,
                ),
                ft.Container(height=4),
                self.job_info_text,
            ]),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            visible=False,
        )
        
        job_section = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                        ft.Text("ຂໍ້ມູນໃບຮັບລົດ", size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=12),
                self.job_dropdown,
                ft.Container(height=10),
                self.job_info_container,
            ],
            spacing=0,
        )
        
        # ==================== SECTION 2: SELECTED ITEMS (Table) ====================
        table_header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=45, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text("ລາຍການ", size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=100, alignment=ft.Alignment(-1, 0)),
                    ft.Container(content=ft.Text("ຈຳນວນ", size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=70, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text("ລາຄາ (KIP)", size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=120, alignment=ft.Alignment(1, 0)),
                    ft.Container(content=ft.Text("ລວມ (KIP)", size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=130, alignment=ft.Alignment(1, 0)),
                    ft.Container(content=ft.Text("", size=12), width=45),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=12, horizontal=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=8,
        )
        
        self.items_table_body = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, height=250)
        
        selected_items_table = ft.Column(
            [
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                self.items_table_body,
            ],
            spacing=0,
        )
        
        selected_section = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LIST_ALT, size=18, color=self.primary_color),
                        ft.Text(get_text("selected_items"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text("ລວມທັງໝົດ:", size=13, weight=ft.FontWeight.W_500, color="#64748B"),
                                    self.total_text,
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=20,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=10),
                selected_items_table,
            ],
            spacing=0,
        )
        
        # ==================== SECTION 3: SELECT ITEMS (Right Side) ====================
        self.parts_tab = ft.Container(
            content=ft.Text(get_text("parts"), size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
            bgcolor=self.primary_color,
            border_radius=25,
            padding=ft.padding.symmetric(horizontal=28, vertical=8),
            expand=True,
        )
        self.parts_tab.on_click = self.on_parts_click
        
        self.services_tab = ft.Container(
            content=ft.Text(get_text("services"), size=14, weight=ft.FontWeight.W_600, color="#64748B"),
            bgcolor=ft.Colors.GREY_200,
            border_radius=25,
            padding=ft.padding.symmetric(horizontal=28, vertical=8),
            expand=True,
        )
        self.services_tab.on_click = self.on_services_click
        
        self.category_chips = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        self.search_field = ft.TextField(
            hint_text=get_text("search_items"),
            border_radius=25,
            bgcolor=ft.Colors.GREY_100,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.TRANSPARENT,
            content_padding=ft.padding.symmetric(horizontal=18, vertical=14),
            expand=True,
        )
        self.search_field.on_change = self.on_search_change
        
        self.qty_field = ft.TextField(
            label=get_text("quantity"),
            value="1",
            width=100,
            border_radius=12,
            bgcolor=ft.Colors.GREY_100,
            filled=True,
            input_filter=ft.NumbersOnlyInputFilter(),
            text_align=ft.TextAlign.CENTER,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=12),
        )
        
        # Results list with initial empty state
        self.results_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=320)
        
        # Add initial welcome message
        welcome_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SEARCH, size=48, color="#CBD5E1"),
                ft.Text("ພິມຄຳສັ່ງເພື່ອຄົ້ນຫາ", size=14, color="#94A3B8"),
                ft.Text("ຄົ້ນຫາອາໄຫຼ່ ຫຼື ບໍລິການ", size=12, color="#CBD5E1"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            alignment=ft.Alignment(0, 0),
            padding=ft.padding.all(40),
        )
        self.results_list.controls.append(welcome_container)
        
        results_container = ft.Container(
            content=self.results_list,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=12,
            padding=ft.padding.all(10),
            bgcolor=ft.Colors.GREY_50,
            expand=True,
        )
        
        select_items_section = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.SHOPPING_CART, size=18, color=self.primary_color),
                        ft.Text("ເລືອກລາຍການ", size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=12),
                ft.Row([self.parts_tab, self.services_tab], spacing=12),
                ft.Container(height=10),
                self.category_chips,
                ft.Container(height=12),
                ft.Row([self.search_field, self.qty_field], spacing=12),
                ft.Container(height=12),
                results_container,
            ],
            spacing=0,
            expand=True,
        )
        
        # ==================== BIG CARD ====================
        left_column = ft.Container(
            content=ft.Column(
                [
                    job_section,
                    ft.Container(height=20),
                    selected_section,
                ],
                spacing=0,
                expand=True,
            ),
            width=400,
        )
        
        right_column = ft.Container(
            content=select_items_section,
            width=620,
            expand=True,
        )
        
        two_columns_row = ft.Row(
            [
                left_column,
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),
                right_column,
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
        )
        
        big_card = ft.Container(
            content=two_columns_row,
            padding=ft.padding.symmetric(horizontal=24, vertical=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )
        
        # Main scrollable content (vertical scroll)
        scrollable_content = ft.Column(
            [
                big_card,
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.padding.all(20),
            bgcolor="#F0F2F5",
        )
        
        main_content = ft.Container(
            content=ft.Column(
                [
                    header,
                    content_area,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
        
        # Initialize empty table
        self._update_selected_items_table()
        
        # Load data after UI is built
        self.page.run_task(self._load_data_async)
        
        return main_content
    
    async def _load_data_async(self):
        """Load data asynchronously"""
        await asyncio.sleep(0.3)
        self.load_parts_and_services()
        self.load_pending_orders()
    
    def _update_selected_items_table(self):
        """Update the selected items table with current items"""
        self.items_table_body.controls.clear()
        
        if not self.temp_items:
            empty_row = ft.Container(
                content=ft.Text("ຍັງບໍ່ມີລາຍການທີ່ເລືອກ", size=13, color="#94A3B8"),
                padding=ft.padding.all(40),
                alignment=ft.Alignment(0, 0),
            )
            self.items_table_body.controls.append(empty_row)
            self.total_text.value = "0 KIP"
            self.page.update()
            return
        
        for idx, item in enumerate(self.temp_items):
            bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
            remove_callback = functools.partial(self.remove_item, item.get("temp_id"))
            
            row = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(content=ft.Text(str(idx + 1), size=13, color="#64748B"), width=45, alignment=ft.Alignment(0, 0)),
                        ft.Container(content=ft.Text(item.get("name", "-"), size=13, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1), width=180, alignment=ft.Alignment(-1, 0)),
                        ft.Container(content=ft.Text(str(item.get("qty", 1)), size=13, color="#1E293B"), width=70, alignment=ft.Alignment(0, 0)),
                        ft.Container(content=ft.Text(f"{int(item.get('unit_price', 0)):,}", size=13, color="#64748B"), width=120, alignment=ft.Alignment(1, 0)),
                        ft.Container(content=ft.Text(f"{int(item.get('total', 0)):,}", size=13, weight=ft.FontWeight.W_600, color="#10B981"), width=130, alignment=ft.Alignment(1, 0)),
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=18,
                                icon_color="#EF4444",
                                on_click=remove_callback,
                                padding=0,
                            ),
                            width=45,
                            alignment=ft.Alignment(0, 0),
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(vertical=10, horizontal=12),
                bgcolor=bg_color,
            )
            self.items_table_body.controls.append(row)
        
        total = sum(item.get("total", 0) for item in self.temp_items)
        self.total_text.value = f"{int(total):,} KIP"
        self.page.update()
    
    # ----------------------------------------------------------------------
    # Data Loading
    # ----------------------------------------------------------------------
    def load_pending_orders(self):
        """Load pending job orders"""
        try:
            all_orders = self.client.get_job_orders() or []
            self.pending_orders = [o for o in all_orders if o.get('status') in ['pending', 'quoting']]
            
            self.job_dropdown.options.clear()
            for o in self.pending_orders:
                self.job_dropdown.options.append(
                    ft.dropdown.Option(
                        str(o.get("id")),
                        f"{o.get('job_no')} - {o.get('customer_name')} - {o.get('plate_number')}"
                    )
                )
            
            if self.job_order_id and self.pending_orders:
                for opt in self.job_dropdown.options:
                    if opt.key == str(self.job_order_id):
                        self.job_dropdown.value = opt.key
                        break
                if self.job_dropdown.value:
                    self.on_job_select(None)
            
            self.job_dropdown.update()
            print(f"Loaded {len(self.pending_orders)} orders")
        except Exception as ex:
            print(f"Error loading orders: {ex}")
    
    def load_parts_and_services(self):
        try:
            self.parts_list = self.client.get_parts() or []
            self.services_list = self.client.get_services() or []
            print(f"Loaded {len(self.parts_list)} parts, {len(self.services_list)} services")
            self.load_category_chips()
            # Don't call search_items initially - keep welcome message
            # self.search_items()
            self.page.update()
        except Exception as ex:
            print(f"Error loading parts/services: {ex}")
    
    def load_category_chips(self):
        categories = [
            {"id": "all", "name": "ທັງໝົດ", "icon": ft.Icons.VIEW_LIST},
            {"id": "engine", "name": "ເຄື່ອງຈັກ", "icon": ft.Icons.SETTINGS},  # เปลี่ยนจาก ENGINE
            {"id": "brake", "name": "ເບຣກ", "icon": ft.Icons.WARNING},  # เปลี่ยนจาก BRAKE
            {"id": "electrical", "name": "ໄຟຟ້າ", "icon": ft.Icons.FLASH_ON},  # เปลี่ยนจาก ELECTRICAL
            {"id": "suspension", "name": "ຊ່ວງລຸ່ມ", "icon": ft.Icons.SETTINGS_APPLICATIONS},
        ]
        self.category_chips.controls.clear()
        for cat in categories:
            is_active = self.current_category == cat["id"]
            chip = ft.Container(
                content=ft.Row([
                    ft.Icon(cat["icon"], size=14, color=ft.Colors.WHITE if is_active else "#64748B"),
                    ft.Text(cat["name"], size=12, weight=ft.FontWeight.W_500,
                           color=ft.Colors.WHITE if is_active else "#64748B"),
                ], spacing=6),
                bgcolor=self.primary_color if is_active else ft.Colors.GREY_200,
                border_radius=20,
                padding=ft.padding.symmetric(horizontal=12, vertical=5),
                ink=True,
                on_click=lambda e, cid=cat["id"]: self.filter_by_category(cid),
            )
            self.category_chips.controls.append(chip)
        self.page.update()
    
    def filter_by_category(self, category_id):
        self.current_category = category_id
        self.load_category_chips()
        if self.search_field.value:
            self.search_items()
    
    # ----------------------------------------------------------------------
    # Event Handlers
    # ----------------------------------------------------------------------
    def on_job_select(self, e):
        if self.job_dropdown.value:
            self.selected_job_id = int(self.job_dropdown.value)
            order = next((o for o in self.pending_orders if o.get("id") == self.selected_job_id), None)
            if order:
                self.job_info_text.value = f"{order.get('job_no')} - {order.get('customer_name')} - {order.get('plate_number')}"
                self.job_info_container.visible = True
        else:
            self.selected_job_id = None
            self.job_info_container.visible = False
        self.page.update()
    
    def on_search_change(self, e):
        if self.search_field.value:
            self.search_items()
        else:
            # Clear and show welcome message
            self.results_list.controls.clear()
            welcome_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH, size=48, color="#CBD5E1"),
                    ft.Text("ພິມຄຳສັ່ງເພື່ອຄົ້ນຫາ", size=14, color="#94A3B8"),
                    ft.Text("ຄົ້ນຫາອາໄຫຼ່ ຫຼື ບໍລິການ", size=12, color="#CBD5E1"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.Alignment(0, 0),
                padding=ft.padding.all(40),
            )
            self.results_list.controls.append(welcome_container)
            self.page.update()
    
    def on_parts_click(self, e):
        self.current_tab = "parts"
        self.parts_tab.bgcolor = self.primary_color
        self.parts_tab.content.color = ft.Colors.WHITE
        self.services_tab.bgcolor = ft.Colors.GREY_200
        self.services_tab.content.color = "#64748B"
        self.search_field.hint_text = get_text("search_parts")
        if self.search_field.value:
            self.search_items()
        else:
            # Show welcome message
            self.results_list.controls.clear()
            welcome_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH, size=48, color="#CBD5E1"),
                    ft.Text("ພິມຄຳສັ່ງເພື່ອຄົ້ນຫາ", size=14, color="#94A3B8"),
                    ft.Text("ຄົ້ນຫາອາໄຫຼ່", size=12, color="#CBD5E1"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.Alignment(0, 0),
                padding=ft.padding.all(40),
            )
            self.results_list.controls.append(welcome_container)
        self.load_category_chips()
        self.category_chips.visible = True
        self.page.update()
    
    def on_services_click(self, e):
        self.current_tab = "services"
        self.services_tab.bgcolor = self.primary_color
        self.services_tab.content.color = ft.Colors.WHITE
        self.parts_tab.bgcolor = ft.Colors.GREY_200
        self.parts_tab.content.color = "#64748B"
        self.search_field.hint_text = get_text("search_services")
        if self.search_field.value:
            self.search_items()
        else:
            # Show welcome message
            self.results_list.controls.clear()
            welcome_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH, size=48, color="#CBD5E1"),
                    ft.Text("ພິມຄຳສັ່ງເພື່ອຄົ້ນຫາ", size=14, color="#94A3B8"),
                    ft.Text("ຄົ້ນຫາບໍລິການ", size=12, color="#CBD5E1"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.Alignment(0, 0),
                padding=ft.padding.all(40),
            )
            self.results_list.controls.append(welcome_container)
        self.category_chips.controls.clear()
        self.category_chips.visible = False
        self.page.update()
    
    def search_items(self):
        self.results_list.controls.clear()
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        
        if self.current_tab == "parts":
            results = self.parts_list
            if keyword:
                results = [p for p in results if keyword in p.get("name", "").lower()]
            else:
                # No keyword, show empty
                empty_container = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=48, color="#CBD5E1"),
                        ft.Text("ພິມຄຳສັ່ງເພື່ອຄົ້ນຫາ", size=14, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.all(40),
                )
                self.results_list.controls.append(empty_container)
                self.page.update()
                return
            
            if not results:
                empty_container = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=48, color="#CBD5E1"),
                        ft.Text(get_text("no_items_found"), size=14, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.all(40),
                )
                self.results_list.controls.append(empty_container)
            else:
                for part in results[:30]:
                    stock = part.get('stock_qty', 0)
                    min_stock = part.get('min_stock', 5)
                    if stock <= min_stock:
                        stock_color = "#EF4444"
                        stock_bg = "#FEE2E2"
                    elif stock <= min_stock * 2:
                        stock_color = "#F59E0B"
                        stock_bg = "#FEF3C7"
                    else:
                        stock_color = "#10B981"
                        stock_bg = "#D1FAE5"
                    
                    add_callback = functools.partial(
                        self.add_item, 
                        "part", 
                        part.get('id'), 
                        part.get('name'), 
                        part.get('sell_price', 0)
                    )
                    
                    item_card = ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.INVENTORY_2, size=28, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=12,
                                padding=ft.padding.all(10),
                            ),
                            ft.Column([
                                ft.Text(part.get("name", "-"), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(f"ສະຕ໋ອກ: {stock}", size=11, color=stock_color),
                                        bgcolor=stock_bg,
                                        border_radius=12,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                    ),
                                    ft.Text(f"{int(part.get('sell_price', 0)):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.primary_color),
                                ], spacing=8),
                            ], expand=True, spacing=4),
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                icon_size=28,
                                icon_color=self.primary_color,
                                on_click=add_callback,
                            ),
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.all(12),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        border=ft.border.all(1, ft.Colors.GREY_200),
                    )
                    self.results_list.controls.append(item_card)
        else:
            results = self.services_list
            if keyword:
                results = [s for s in results if keyword in s.get("name", "").lower()]
            else:
                # No keyword, show empty
                empty_container = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=48, color="#CBD5E1"),
                        ft.Text("ພິມຄຳສັ່ງເພື່ອຄົ້ນຫາ", size=14, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.all(40),
                )
                self.results_list.controls.append(empty_container)
                self.page.update()
                return
            
            if not results:
                empty_container = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=48, color="#CBD5E1"),
                        ft.Text(get_text("no_items_found"), size=14, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.all(40),
                )
                self.results_list.controls.append(empty_container)
            else:
                for service in results[:30]:
                    add_callback = functools.partial(
                        self.add_item,
                        "service",
                        service.get('id'),
                        service.get('name'),
                        service.get('price', 0)
                    )
                    
                    item_card = ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.BUILD, size=28, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=12,
                                padding=ft.padding.all(10),
                            ),
                            ft.Column([
                                ft.Text(service.get("name", "-"), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                                ft.Text(service.get("description", "-")[:50], size=11, color="#64748B"),
                                ft.Text(f"{int(service.get('price', 0)):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.primary_color),
                            ], expand=True, spacing=4),
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                icon_size=28,
                                icon_color=self.primary_color,
                                on_click=add_callback,
                            ),
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.all(12),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        border=ft.border.all(1, ft.Colors.GREY_200),
                    )
                    self.results_list.controls.append(item_card)
        
        self.page.update()
    
    def add_item(self, item_type, ref_id, name, price, e=None):
        print(f"DEBUG: add_item - type={item_type}, ref_id={ref_id}, name={name}, price={price}")
        
        if not ref_id:
            self.show_snackbar("Invalid item: missing ID", True)
            return
        
        self.temp_id_counter += 1
        qty = int(self.qty_field.value) if self.qty_field.value else 1
        
        self.temp_items.append({
            "temp_id": self.temp_id_counter,
            "item_type": item_type,
            "ref_id": ref_id,
            "name": name,
            "qty": qty,
            "unit_price": price,
            "total": qty * price
        })
        
        self._update_selected_items_table()
        self.show_snackbar(f"✓ Added: {name}", False)
        self.page.update()
    
    def remove_item(self, temp_id, e=None):
        self.temp_items = [item for item in self.temp_items if item.get("temp_id") != temp_id]
        self._update_selected_items_table()
        self.page.update()
    
    # ----------------------------------------------------------------------
    # Actions
    # ----------------------------------------------------------------------
    def save_quotation(self, e=None):
        if not self.selected_job_id:
            self.show_snackbar(get_text("select_job_order_first"), True)
            return
        if not self.temp_items:
            self.show_snackbar(get_text("please_add_items_first"), True)
            return
        
        try:
            result = self.client.create_quotation(self.selected_job_id)
            if result and result.get("id"):
                qid = result.get("id")
                for item in self.temp_items:
                    self.client.add_quotation_item(qid, item["item_type"], item["ref_id"], item["qty"])
                self.client.calculate_quotation_total(qid)
                self.show_snackbar(f"✅ {get_text('quotation_saved_successfully')}", False)
                self.navigate("quotation_list")
            else:
                self.show_snackbar("Failed to create quotation", True)
        except Exception as ex:
            print(f"ERROR: {ex}")
            self.show_snackbar(f"{get_text('error')}: {ex}", True)
    
    def approve_quotation(self, e=None):
        if not self.selected_job_id:
            self.show_snackbar(get_text("select_job_order_first"), True)
            return
        if not self.temp_items:
            self.show_snackbar(get_text("please_add_items_first"), True)
            return
        
        try:
            result = self.client.create_quotation(self.selected_job_id)
            if result and result.get("id"):
                qid = result.get("id")
                for item in self.temp_items:
                    self.client.add_quotation_item(qid, item["item_type"], item["ref_id"], item["qty"])
                self.client.calculate_quotation_total(qid)
                self.client.update_quotation_status(qid, "approved")
                self.show_snackbar(f"✅ {get_text('quotation_approved_successfully')}", False)
                self.navigate("quotation_list")
            else:
                self.show_snackbar("Failed to create quotation", True)
        except Exception as ex:
            print(f"ERROR: {ex}")
            self.show_snackbar(f"{get_text('error')}: {ex}", True)
    
    def show_snackbar(self, msg, is_error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, size=13),
            bgcolor="#EF4444" if is_error else "#10B981",
            open=True,
            duration=3000,
        )
        self.page.update()