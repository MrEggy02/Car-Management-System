# pages/quotations/quotation_create.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime
import asyncio
import functools

from i18n import get_text
from pages.quotations.quotation_dialog_helpers import show_job_order_detail_dialog


class QuotationCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, job_order_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.job_order_id = job_order_id
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.current_snackbar = None
        
        # Data storage
        self.parts_list = []
        self.services_list = []
        self.pending_orders = []
        self.filtered_orders = []
        self.temp_items = []
        self.temp_id_counter = 0
        self.selected_job_id = None
        self.selected_order = None
        
        # Promotion data
        self.promotions_list = []
        self.applied_promotion = None
        self.promotion_discount_amount = 0
        self.selected_promotion_id = None
        self.promotion_parts = []
        self.promotion_services = []
        
        # UI references
        self.search_field = None
        self.qty_field = None
        self.results_list = None
        self.items_table_body = None
        self.total_text = ft.Text("0 KIP", size=16, weight=ft.FontWeight.BOLD, color="#10B981")
        self.job_search_field = None
        self.job_clear_button = None
        self.job_results_container = None
        self.job_results_list = None
        self.selected_job_card = None
        self.selected_job_label = None
        self.parts_tab = None
        self.services_tab = None
        self.category_chips = None
        self.promotion_container = None
        self.promotion_info_text = None
        self.promotion_discount_text = None
        self.promotion_details_card = None
        self.promotion_list_container = None
        self.available_promotions = []
        
        # State
        self.current_tab = "parts"
        self.current_category_id = None
        self.part_categories = []
        
    def build(self):
        # --- Header ---
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=18, color=ft.Colors.WHITE)], spacing=6),
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                        border_radius=8,
                        padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        on_click=lambda e: self.navigate("quotation_list"),
                        ink=True,
                    ),
                    ft.Column([ft.Text(get_text("create_quotation"), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)], spacing=4),
                    ft.Container(expand=True),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Row([ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE), ft.Text(get_text("save_quotation"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600)], spacing=8),
                                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                                border_radius=30,
                                padding=ft.Padding(left=20, right=20, top=10, bottom=10),
                                on_click=self.save_quotation,
                                ink=True,
                            ),
                        ],
                        spacing=12,
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=[self.primary_color, self.primary_dark]),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
        
        # ==================== JOB ORDER SEARCH SECTION ====================
        self.job_search_field = ft.TextField(
            label=get_text("search_job_order"),
            hint_text=get_text("search_by_job_no_customer_plate"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
            on_change=self.on_search_job_order,
            border_color=ft.Colors.GREY_200,
        )
        
        self.job_clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=18,
            icon_color=ft.Colors.GREY_500,
            on_click=lambda e: self.clear_job_search(),
            visible=False,
        )
        
        search_row = ft.Row([self.job_search_field, self.job_clear_button], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.job_results_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=150)
        self.job_results_container = ft.Container(
            content=self.job_results_list,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            border_radius=12,
            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
            bgcolor=ft.Colors.WHITE,
            visible=False,
        )
        
        self.selected_job_label = ft.Text("", size=13, weight=ft.FontWeight.W_500, color="#1E293B")
        
        self.selected_job_card = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color="#10B981"),
                        ft.Column([
                            ft.Text(get_text("selected_job"), size=11, color="#64748B"),
                            self.selected_job_label,
                        ], spacing=2, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color="#64748B",
                            on_click=lambda e: self.clear_selected_job(),
                            tooltip=get_text("clear_selection"),
                        ),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                ),
                elevation=0,
                margin=ft.Margin(left=0, right=0, top=0, bottom=0),
            ),
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
            visible=False,
            on_click=self.show_job_detail_dialog,
        )
        
        job_section = ft.Column(
            [
                ft.Row([ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color), ft.Text(get_text("job_order_info"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B")], spacing=8),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=12),
                search_row,
                ft.Container(height=8),
                self.job_results_container,
                self.selected_job_card,
            ],
            spacing=0,
        )
        
        # ==================== PROMOTION SECTION ====================
        self.promotion_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LOCAL_OFFER, size=18, color=self.primary_color),
                    ft.Text(get_text("available_promotions"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ], spacing=8),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=8),
                self._build_promotion_list(),
            ], spacing=0),
            padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
            visible=False,
        )
        
        self.promotion_info_text = ft.Text("", size=12, color="#1E293B")
        self.promotion_discount_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD, color="#10B981")
        
        self.promotion_details_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.LOCAL_OFFER, size=16, color="#10B981"),
                        ft.Text(get_text("promotion_details"), size=13, weight=ft.FontWeight.BOLD, color="#10B981"),
                    ], spacing=8),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=4),
                    self.promotion_info_text,
                    ft.Container(height=4),
                    self.promotion_discount_text,
                ], spacing=4),
                padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            ),
            elevation=0,
            margin=ft.Margin(left=0, right=0, top=4, bottom=0),
            visible=False,
        )
        
        promotion_section = ft.Column(
            [
                self.promotion_container,
                self.promotion_details_card,
            ],
            spacing=0,
        )
        
        # ==================== SELECTED ITEMS TABLE ====================
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=35, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("item_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B"), expand=True, alignment=ft.Alignment(-1, 0)),
                ft.Container(content=ft.Text(get_text("quantity_short"), size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=65, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("price_kip_short"), size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=110, alignment=ft.Alignment(1, 0)),
                ft.Container(content=ft.Text(get_text("total_kip_short"), size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=110, alignment=ft.Alignment(1, 0)),
                ft.Container(content=ft.Text("", size=12), width=40),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=10, bottom=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=8,
        )
        
        self.items_table_body = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, height=180)
        selected_items_table = ft.Column([table_header, ft.Divider(height=1, color=ft.Colors.GREY_200), self.items_table_body], spacing=0)
        
        selected_section = ft.Column([
            ft.Row([ft.Icon(ft.Icons.LIST_ALT, size=18, color=self.primary_color), ft.Text(get_text("selected_items"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"), ft.Container(expand=True),
                ft.Container(content=ft.Row([ft.Text(get_text("total_amount") + ":", size=13, weight=ft.FontWeight.W_500, color="#64748B"), self.total_text], spacing=8), padding=ft.Padding(left=10, right=10, top=5, bottom=5), bgcolor=ft.Colors.GREY_50, border_radius=20)],
                spacing=8),
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            ft.Container(height=10),
            selected_items_table,
        ], spacing=0)
        
        # ==================== SELECT ITEMS SECTION ====================
        self.parts_tab = ft.Container(content=ft.Text(get_text("parts"), size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), bgcolor=self.primary_color, border_radius=25, padding=ft.Padding(left=28, right=28, top=8, bottom=8), expand=True)
        self.parts_tab.on_click = self.on_parts_click
        
        self.services_tab = ft.Container(content=ft.Text(get_text("services"), size=14, weight=ft.FontWeight.W_600, color="#64748B"), bgcolor=ft.Colors.GREY_200, border_radius=25, padding=ft.Padding(left=28, right=28, top=8, bottom=8), expand=True)
        self.services_tab.on_click = self.on_services_click
        
        self.category_chips = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        self.search_field = ft.TextField(hint_text=get_text("search_items"), border_radius=25, bgcolor=ft.Colors.GREY_100, filled=True, prefix_icon=ft.Icons.SEARCH, border_color=ft.Colors.TRANSPARENT, content_padding=ft.Padding(left=18, right=18, top=14, bottom=14), expand=True)
        self.search_field.on_change = self.on_search_change
        
        self.qty_field = ft.TextField(label=get_text("quantity"), value="1", width=100, border_radius=12, bgcolor=ft.Colors.GREY_100, filled=True, input_filter=ft.NumbersOnlyInputFilter(), text_align=ft.TextAlign.CENTER, content_padding=ft.Padding(left=12, right=12, top=12, bottom=12))
        
        self.results_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=240)
        welcome_container = ft.Container(content=ft.Column([ft.Icon(ft.Icons.SEARCH, size=48, color="#CBD5E1"), ft.Text(get_text("type_to_search"), size=14, color="#94A3B8"), ft.Text(get_text("search_parts_or_services"), size=12, color="#CBD5E1")], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8), alignment=ft.Alignment(0, 0), padding=ft.Padding(left=40, right=40, top=40, bottom=40))
        self.results_list.controls.append(welcome_container)
        
        results_container = ft.Container(content=self.results_list, border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)), border_radius=12, padding=ft.Padding(left=10, right=10, top=10, bottom=10), bgcolor=ft.Colors.GREY_50, expand=True)
        
        select_items_section = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SHOPPING_CART, size=18, color=self.primary_color),
                ft.Text(get_text("select_items"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(expand=True),
                ft.TextButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD, size=16, color=self.primary_color),
                        ft.Text(get_text("add_custom_service"), size=13, color=self.primary_color, weight=ft.FontWeight.W_600)
                    ], spacing=4),
                    on_click=self.show_add_custom_service_dialog
                )
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            ft.Container(height=12),
            ft.Row([self.parts_tab, self.services_tab], spacing=12),
            ft.Container(height=10),
            self.category_chips,
            ft.Container(height=12),
            ft.Row([self.search_field, self.qty_field], spacing=12),
            ft.Container(height=12),
            results_container,
        ], spacing=0, expand=True)
        
        # ==================== BIG CARD ====================
        left_column = ft.Container(content=ft.Column([job_section, ft.Container(height=12), promotion_section, ft.Container(height=12), selected_section], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO), col={"sm": 12, "md": 7, "lg": 7})
        right_column = ft.Container(content=select_items_section, col={"sm": 12, "md": 5, "lg": 5})
        
        two_columns_row = ft.ResponsiveRow([left_column, right_column], spacing=20, vertical_alignment=ft.CrossAxisAlignment.START)
        
        big_card = ft.Container(content=two_columns_row, padding=ft.Padding(left=16, right=16, top=16, bottom=16), bgcolor=ft.Colors.WHITE, border_radius=16)
        
        scrollable_content = ft.Column([big_card], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        content_area = ft.Container(content=scrollable_content, expand=True, padding=ft.Padding(left=12, right=12, top=12, bottom=12), bgcolor="#F0F2F5")
        
        main_content = ft.Container(content=ft.Column([header, content_area], spacing=0, expand=True), expand=True)
        
        self._update_selected_items_table()
        self.page.run_task(self._load_data_async)
        
        return main_content
    
    def _build_promotion_list(self):
        """Build promotion list container"""
        self.promotion_list_container = ft.Column(spacing=8)
        return self.promotion_list_container
    
    def update_promotion_list(self):
        """Update promotion list based on selected parts/services"""
        self.promotion_list_container.controls.clear()
        self.available_promotions = []
        
        # Get all temp item IDs
        selected_part_ids = [item.get("ref_id") for item in self.temp_items if item.get("item_type") == "part"]
        selected_service_ids = [item.get("ref_id") for item in self.temp_items if item.get("item_type") == "service"]
        
        if not selected_part_ids and not selected_service_ids:
            # No items selected, show message
            self.promotion_list_container.controls.append(
                ft.Container(
                    content=ft.Text(get_text("select_items_first_to_see_promotions"), size=12, color="#94A3B8"),
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                    alignment=ft.Alignment(0, 0),
                )
            )
            self.promotion_container.visible = True
            self.promotion_details_card.visible = False
            self.page.update()
            return
        
        # Find promotions that are applicable
        subtotal = sum(item.get("total", 0) for item in self.temp_items)
        
        for promo in self.promotions_list:
            # Get promotion items (from cache)
            promo_parts = promo.get('parts', [])
            promo_services = promo.get('services', [])
            
            # Check if promotion applies
            is_applicable = False
            if not promo_parts and not promo_services:
                # Promotion applies to all items
                is_applicable = True
            else:
                # Check if any selected part is in promo parts
                if selected_part_ids:
                    for pid in selected_part_ids:
                        if pid in promo_parts:
                            is_applicable = True
                            break
                # Check if any selected service is in promo services
                if not is_applicable and selected_service_ids:
                    for sid in selected_service_ids:
                        if sid in promo_services:
                            is_applicable = True
                            break
            
            if not is_applicable:
                continue
            
            # Check min amount
            min_amount = promo.get('min_amount', 0)
            if subtotal < min_amount:
                continue
            
            self.available_promotions.append(promo)
            
            # Calculate eligible subtotal for display
            promo_part_ids = set(promo.get('parts', []))
            promo_service_ids = set(promo.get('services', []))
            if not promo_part_ids and not promo_service_ids:
                applicable_subtotal = subtotal
            else:
                applicable_subtotal = sum(
                    item.get("total", 0) for item in self.temp_items
                    if (item["item_type"] == "part" and item["ref_id"] in promo_part_ids)
                    or (item["item_type"] == "service" and item["ref_id"] in promo_service_ids)
                )
            
            # Calculate discount for display
            discount_amount = self._calculate_promotion_discount(promo)
            
            if promo['discount_type'] == 'percent':
                discount_display = f"{int(promo['value'])}%"
            else:
                discount_display = f"{int(promo['value']):,} KIP"
            
            is_applied = (self.applied_promotion and self.applied_promotion.get('id') == promo.get('id'))
            
            border_color = "#10B981" if is_applied else ft.Colors.GREY_200
            bg_color = "#F0FDF4" if is_applied else ft.Colors.WHITE
            
            promo_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.LOCAL_OFFER, size=20, color="#10B981" if is_applied else "#64748B"),
                            ft.Text(promo.get('name', '-'), size=14, weight=ft.FontWeight.BOLD, color="#1E293B", expand=True),
                            ft.Container(
                                content=ft.Text(f"{discount_display}", size=13, weight=ft.FontWeight.BOLD, color="#10B981" if is_applied else "#64748B"),
                                bgcolor="#D1FAE5" if is_applied else ft.Colors.GREY_100,
                                border_radius=12,
                                padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                            ),
                        ], spacing=8),
                        ft.Container(height=4),
                        ft.Text(f"{get_text('you_save')}: {int(discount_amount):,} KIP", size=12, color="#10B981" if is_applied else "#64748B", weight=ft.FontWeight.W_600 if is_applied else ft.FontWeight.NORMAL),
                        ft.Text(f"{get_text('min_amount_required')}: {int(min_amount):,} KIP" if min_amount > 0 else "", size=11, color="#F59E0B") if min_amount > 0 else ft.Container(),
                        ft.Container(height=4),
                        ft.Row([
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE if is_applied else ft.Icons.INFO_OUTLINE, size=14, color="#10B981" if is_applied else "#64748B"),
                                    ft.Text(get_text("applied_best") if is_applied else get_text("available"), size=12, color="#10B981" if is_applied else "#64748B", weight=ft.FontWeight.BOLD if is_applied else ft.FontWeight.NORMAL)
                                ], spacing=4),
                                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                            )
                        ]),
                    ]),
                    padding=ft.Padding(left=12, right=12, top=12, bottom=12),
                ),
                elevation=0,
                margin=ft.Margin(left=0, right=0, top=0, bottom=0),
            )
            
            promo_container = ft.Container(
                content=promo_card,
                bgcolor=bg_color,
                border=ft.Border(top=ft.BorderSide(1, border_color), right=ft.BorderSide(1, border_color), bottom=ft.BorderSide(1, border_color), left=ft.BorderSide(1, border_color)),
                border_radius=12,
                padding=ft.Padding(left=2, right=2, top=2, bottom=2),
                margin=ft.Margin(left=0, right=0, top=0, bottom=8),
            )
            self.promotion_list_container.controls.append(promo_container)
        
        if not self.available_promotions:
            self.promotion_list_container.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_applicable_promotions"), size=12, color="#94A3B8"),
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        self.promotion_container.visible = True
        self.page.update()
    
    def apply_promotion(self, promo):
        """Apply selected promotion"""
        self.applied_promotion = promo
        self.selected_promotion_id = promo.get('id')
        
        # Load promotion items (from cache)
        self.promotion_parts = promo.get('parts', [])
        self.promotion_services = promo.get('services', [])
        
        promo_part_ids = set(self.promotion_parts)
        promo_service_ids = set(self.promotion_services)
        
        # Full subtotal used for min_amount eligibility check
        full_subtotal = sum(item.get("total", 0) for item in self.temp_items)
        min_amount = promo.get('min_amount', 0)
        
        # Eligible subtotal: only the items actually covered by this promotion
        if not promo_part_ids and not promo_service_ids:
            # Global promotion — applies to every item
            applicable_subtotal = full_subtotal
        else:
            # Targeted promotion — only matching parts/services
            applicable_subtotal = sum(
                item.get("total", 0) for item in self.temp_items
                if (item["item_type"] == "part" and item["ref_id"] in promo_part_ids)
                or (item["item_type"] == "service" and item["ref_id"] in promo_service_ids)
            )
        
        if full_subtotal < min_amount:
            self.promotion_discount_amount = 0
            self.promotion_discount_text.value = f"⚠️ {get_text('add_more_to_get_discount')} (+{int(min_amount - full_subtotal):,} KIP)"
            self.promotion_discount_text.color = "#F59E0B"
        else:
            if promo['discount_type'] == 'percent':
                discount_amount = applicable_subtotal * (promo['value'] / 100)
            else:
                discount_amount = promo['value']
            discount_amount = min(discount_amount, applicable_subtotal)
            self.promotion_discount_amount = discount_amount
            
            if promo['discount_type'] == 'percent':
                self.promotion_discount_text.value = f"{get_text('you_save')}: {int(discount_amount):,} KIP ({int(promo['value'])}%)"
            else:
                self.promotion_discount_text.value = f"{get_text('you_save')}: {int(discount_amount):,} KIP"
            self.promotion_discount_text.color = "#10B981"
        
        # Build promotion info text
        info_lines = []
        if promo['discount_type'] == 'percent':
            info_lines.append(f"💸 {get_text('discount')}: {int(promo['value'])}%")
        else:
            info_lines.append(f"💸 {get_text('discount')}: {int(promo['value']):,} KIP")
        
        if min_amount > 0:
            info_lines.append(f"💰 {get_text('min_amount_required')}: {int(min_amount):,} KIP")
        
        if self.promotion_parts or self.promotion_services:
            item_list = []
            if self.promotion_parts:
                item_list.append(f"🔧 {len(self.promotion_parts)} {get_text('parts')}")
            if self.promotion_services:
                item_list.append(f"🛠️ {len(self.promotion_services)} {get_text('services')}")
            info_lines.append(f"🎯 {get_text('applicable_items')}: {', '.join(item_list)}")
        else:
            info_lines.append(f"🎉 {get_text('promotion_applies_to_all_items')}")
        
        self.promotion_info_text.value = "\n".join(info_lines)
        self.promotion_details_card.visible = True
        self.promotion_container.visible = False
        
        self._update_selected_items_table()
        
        # Refresh search results to show only applicable items
        if self.search_field.value:
            self.search_items()
        
        self.page.update()
    
    async def _load_data_async(self):
        await asyncio.sleep(0.3)
        await asyncio.to_thread(self.load_parts_and_services)
        await asyncio.to_thread(self.load_pending_orders)
        await asyncio.to_thread(self.load_promotions)
    
    def _calculate_promotion_discount(self, promo):
        """Calculate the discount amount for a promotion based on current temp_items.
        Returns the discount amount (float) if applicable, else 0."""
        if not self.temp_items:
            return 0
        
        selected_part_ids = [item.get("ref_id") for item in self.temp_items if item.get("item_type") == "part"]
        selected_service_ids = [item.get("ref_id") for item in self.temp_items if item.get("item_type") == "service"]
        
        promo_parts = promo.get('parts', [])
        promo_services = promo.get('services', [])
        
        is_applicable = False
        if not promo_parts and not promo_services:
            is_applicable = True
        else:
            if selected_part_ids:
                for pid in selected_part_ids:
                    if pid in promo_parts:
                        is_applicable = True
                        break
            if not is_applicable and selected_service_ids:
                for sid in selected_service_ids:
                    if sid in promo_services:
                        is_applicable = True
                        break
        
        if not is_applicable:
            return 0
        
        # Check min amount
        subtotal = sum(item.get("total", 0) for item in self.temp_items)
        min_amount = promo.get('min_amount', 0)
        if subtotal < min_amount:
            return 0
        
        # Calculate eligible subtotal
        if not promo_parts and not promo_services:
            applicable_subtotal = subtotal
        else:
            applicable_subtotal = sum(
                item.get("total", 0) for item in self.temp_items
                if (item["item_type"] == "part" and item["ref_id"] in promo_parts)
                or (item["item_type"] == "service" and item["ref_id"] in promo_services)
            )
        
        # Calculate discount
        if promo.get('discount_type') == 'percent':
            discount_amount = applicable_subtotal * (promo.get('value', 0) / 100)
        else:
            discount_amount = promo.get('value', 0)
            
        return min(discount_amount, applicable_subtotal)

    def auto_apply_best_promotion(self):
        """Automatically find and apply the promotion with the highest discount."""
        if not self.temp_items or not self.promotions_list:
            self.applied_promotion = None
            self.selected_promotion_id = None
            self.promotion_discount_amount = 0
            self.promotion_parts = []
            self.promotion_services = []
            return

        best_promo = None
        best_discount = 0

        for promo in self.promotions_list:
            discount = self._calculate_promotion_discount(promo)
            if discount > best_discount:
                best_discount = discount
                best_promo = promo

        if best_promo and best_discount > 0:
            self.applied_promotion = best_promo
            self.selected_promotion_id = best_promo.get('id')
            self.promotion_discount_amount = best_discount
            self.promotion_parts = best_promo.get('parts', [])
            self.promotion_services = best_promo.get('services', [])
        else:
            self.applied_promotion = None
            self.selected_promotion_id = None
            self.promotion_discount_amount = 0
            self.promotion_parts = []
            self.promotion_services = []

    # ==================== MODIFIED: UPDATE SELECTED ITEMS TABLE WITH STOCK WARNING ====================
    def _update_selected_items_table(self):
        self.auto_apply_best_promotion()
        
        self.items_table_body.controls.clear()
        
        if not self.temp_items:
            empty_row = ft.Container(content=ft.Text(get_text("no_items_selected"), size=13, color="#94A3B8"), padding=ft.Padding(left=40, right=40, top=40, bottom=40), alignment=ft.Alignment(0, 0))
            self.items_table_body.controls.append(empty_row)
            self.total_text.value = "0 KIP"
            self.update_promotion_list()
            self.page.update()
            return
        
        subtotal = 0
        has_stock_warning = False
        warning_items = []
        
        for idx, item in enumerate(self.temp_items):
            bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
            temp_id = item.get("temp_id")
            
            # Check stock for parts
            stock_qty = item.get('stock_qty', 0)
            qty = item.get('qty', 0)
            
            # If item is a part and qty exceeds stock, highlight yellow
            is_stock_warning = False
            if item.get('item_type') == 'part' and stock_qty > 0 and qty > stock_qty:
                is_stock_warning = True
                has_stock_warning = True
                warning_items.append(item.get('name', '-'))
                # Yellow highlight
                bg_color = "#FEF3C7"  # Amber/Yellow background
            elif item.get('item_type') == 'part' and stock_qty == 0:
                # Also warn if stock is 0
                is_stock_warning = True
                has_stock_warning = True
                warning_items.append(item.get('name', '-'))
                bg_color = "#FEF3C7"
            
            # Remove button with lambda that captures current temp_id
            remove_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_size=18,
                icon_color="#EF4444",
                on_click=lambda e, tid=temp_id: self.remove_item(tid),
                padding=0,
            )
            
            # Show stock info in the row
            stock_info = ""
            if item.get('item_type') == 'part':
                if stock_qty > 0:
                    stock_info = f" | ຄັງ: {stock_qty}"
                    if qty > stock_qty:
                        stock_info = f" | ⚠️ ຄັງ: {stock_qty} (ຕ້ອງການ {qty})"
                else:
                    stock_info = " | ⚠️ ສິນຄ້າຫມົດສະຕ໋ອກ"
            
            row = ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Text(str(idx + 1), size=13, color="#64748B"), width=35, alignment=ft.Alignment(0, 0)),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(item.get("name", "-"), size=13, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1),
                            ft.Text(stock_info, size=10, color="#EF4444" if is_stock_warning else "#64748B"),
                        ], spacing=0),
                        expand=True,
                        alignment=ft.Alignment(-1, 0),
                    ),
                    ft.Container(content=ft.Text(str(item.get("qty", 1)), size=13, color="#EF4444" if is_stock_warning else "#1E293B"), width=65, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(f"{int(item.get('unit_price', 0)):,}", size=13, color="#64748B"), width=110, alignment=ft.Alignment(1, 0)),
                    ft.Container(content=ft.Text(f"{int(item.get('total', 0)):,}", size=13, weight=ft.FontWeight.W_600, color="#10B981"), width=110, alignment=ft.Alignment(1, 0)),
                    ft.Container(content=remove_btn, width=40, alignment=ft.Alignment(0, 0)),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=10, right=10, top=8, bottom=8),
                bgcolor=bg_color,
                border=ft.Border(top=ft.BorderSide(2, "#F59E0B")) if is_stock_warning else None,
            )
            self.items_table_body.controls.append(row)
            subtotal += item.get("total", 0)
        
        # Show warning snackbar if any stock issue
        if has_stock_warning:
            self._show_warning_snackbar("ຈຳນວນອາໄຫລ່ທີ່ມີບໍ່ພໍ ກາລຸນາເພີ່ມອາໄຫຼ່ເຂົ້າຄັງກ່ອນສ້ອມແປງ")
        
        subtotal_row = ft.Container(content=ft.Row([ft.Container(expand=True), ft.Text(get_text("subtotal") + ":", size=12, weight=ft.FontWeight.W_500, color="#64748B"), ft.Text(f"{int(subtotal):,} KIP", size=13, weight=ft.FontWeight.W_600, color="#1E293B")], spacing=8), padding=ft.Padding(left=10, right=10, top=8, bottom=8), bgcolor=ft.Colors.GREY_100)
        self.items_table_body.controls.append(subtotal_row)
        
        final_total = subtotal
        if self.applied_promotion and self.promotion_discount_amount > 0:
            discount_row = ft.Container(content=ft.Row([ft.Container(expand=True), ft.Text(f"{get_text('promotion_discount')} ({self.applied_promotion.get('name', '')}):", size=12, color="#64748B"), ft.Text(f"-{int(self.promotion_discount_amount):,} KIP", size=13, weight=ft.FontWeight.W_600, color="#10B981")], spacing=8), padding=ft.Padding(left=10, right=10, top=5, bottom=5), bgcolor=ft.Colors.GREEN_50)
            self.items_table_body.controls.append(discount_row)
            final_total = subtotal - self.promotion_discount_amount
        
        self.total_text.value = f"{int(final_total):,} KIP"
        self.update_promotion_list()
        self.page.update()
    
    # ==================== NEW: SHOW WARNING SNACKBAR ====================
    def _show_warning_snackbar(self, message):
        """Show warning snackbar with yellow/amber color"""
        
        # Remove existing snackbar if any
        if self.current_snackbar:
            try:
                self.page.overlay.remove(self.current_snackbar)
            except:
                pass
            self.current_snackbar = None
        
        bgcolor = "#F59E0B"  # Yellow/Amber
        icon = ft.Icons.WARNING
        
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
            await asyncio.sleep(3.0)
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

    # ----------------------------------------------------------------------
    # Data Loading
    # ----------------------------------------------------------------------
    def load_pending_orders(self):
        try:
            all_orders = self.client.get_job_orders() or []
            self.pending_orders = [o for o in all_orders if o.get('status') in ['pending', 'quoting']]
            self.filtered_orders = self.pending_orders.copy()
            print(f"Loaded {len(self.pending_orders)} pending orders")
        except Exception as ex:
            print(f"Error loading orders: {ex}")
            self.pending_orders = []
            self.filtered_orders = []
    
    def load_parts_and_services(self):
        try:
            self.part_categories = self.client.get_part_categories() or []
            self.parts_list = self.client.get_parts() or []
            self.services_list = self.client.get_services() or []
            self.load_category_chips()
            self.search_items()
            self.page.update()
        except Exception as ex:
            print(f"Error loading parts/services: {ex}")
    
    def load_category_chips(self):
        self.category_chips.controls.clear()
        
        # Add "All" chip
        is_all_active = self.current_category_id is None
        all_chip = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.VIEW_LIST, size=14, color=ft.Colors.WHITE if is_all_active else "#64748B"),
                ft.Text(get_text("all_items"), size=12, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE if is_all_active else "#64748B")
            ], spacing=6),
            bgcolor=self.primary_color if is_all_active else ft.Colors.GREY_200,
            border_radius=20,
            padding=ft.Padding(left=12, right=12, top=5, bottom=5),
            ink=True,
            on_click=lambda e: self.filter_by_category(None),
        )
        self.category_chips.controls.append(all_chip)
        
        # Add dynamic category chips from DB
        for cat in self.part_categories:
            if cat.get('status') == 'active':
                cat_id = cat.get('id')
                is_active = self.current_category_id == cat_id
                chip = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CATEGORY, size=14, color=ft.Colors.WHITE if is_active else "#64748B"),
                        ft.Text(cat.get('name', '-'), size=12, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE if is_active else "#64748B")
                    ], spacing=6),
                    bgcolor=self.primary_color if is_active else ft.Colors.GREY_200,
                    border_radius=20,
                    padding=ft.Padding(left=12, right=12, top=5, bottom=5),
                    ink=True,
                    on_click=lambda e, cid=cat_id: self.filter_by_category(cid),
                )
                self.category_chips.controls.append(chip)
        self.page.update()
    
    def filter_by_category(self, category_id):
        self.current_category_id = category_id
        self.load_category_chips()
        self.search_items()
    
    def load_promotions(self):
        try:
            self.promotions_list = self.client.get_active_promotions() or []
            for promo in self.promotions_list:
                promo_id = promo.get('id')
                try:
                    parts = self.client.get_promotion_parts(promo_id) or []
                    services = self.client.get_promotion_services(promo_id) or []
                    promo['parts'] = [p.get('part_id') for p in parts if p.get('part_id')]
                    promo['services'] = [s.get('service_id') for s in services if s.get('service_id')]
                except Exception as ex:
                    print(f"Error loading promotion details for ID {promo_id}: {ex}")
                    promo['parts'] = []
                    promo['services'] = []
            print(f"Loaded {len(self.promotions_list)} promotions with details")
        except Exception as e:
            print(f"Error loading promotions: {e}")
    
    # ----------------------------------------------------------------------
    # Job Search Handlers
    # ----------------------------------------------------------------------
    def on_search_job_order(self, e):
        query = self.job_search_field.value.lower() if self.job_search_field.value else ""
        
        self.job_clear_button.visible = bool(query)
        
        if not query:
            self.job_results_container.visible = False
            self.page.update()
            return
        
        self.filtered_orders = [
            o for o in self.pending_orders
            if query in o.get('job_no', '').lower()
            or query in o.get('customer_name', '').lower()
            or query in o.get('plate_number', '').lower()
        ]
        
        self.job_results_list.controls.clear()
        
        if not self.filtered_orders:
            self.job_results_list.controls.append(
                ft.Container(content=ft.Text(get_text("no_orders_found"), size=13, color="#94A3B8"), padding=ft.Padding(left=20, right=20, top=20, bottom=20), alignment=ft.Alignment(0, 0))
            )
        else:
            for order in self.filtered_orders[:10]:
                order_id = order.get('id')
                job_no = order.get('job_no', '-')
                customer_name = order.get('customer_name', '-')
                plate_number = order.get('plate_number', '-')
                
                result_item = ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color), bgcolor=ft.Colors.with_opacity(0.1, self.primary_color), border_radius=10, padding=ft.Padding(left=8, right=8, top=8, bottom=8)),
                        ft.Column([ft.Text(job_no, size=14, weight=ft.FontWeight.W_500, color="#1E293B"), ft.Text(f"{customer_name} | {plate_number}", size=11, color="#64748B")], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color="#94A3B8"),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                    ink=True,
                    on_click=lambda e, oid=order_id: self.select_job_order(oid),
                )
                self.job_results_list.controls.append(result_item)
        
        self.job_results_container.visible = True
        self.page.update()
    
    def clear_job_search(self):
        self.job_search_field.value = ""
        self.job_clear_button.visible = False
        self.job_results_container.visible = False
        self.page.update()
    
    def clear_selected_job(self):
        self.selected_job_id = None
        self.selected_order = None
        self.selected_job_card.visible = False
        self.job_search_field.value = ""
        self.reset_promotion()
        self.temp_items.clear()
        self._update_selected_items_table()
        self.page.update()
    
    def select_job_order(self, order_id):
        self.selected_job_id = order_id
        self.selected_order = next((o for o in self.pending_orders if o.get("id") == order_id), None)
        
        if self.selected_order:
            job_no = self.selected_order.get('job_no', '-')
            customer_name = self.selected_order.get('customer_name', '-')
            plate_number = self.selected_order.get('plate_number', '-')
            self.selected_job_label.value = f"{job_no} - {customer_name} - {plate_number}"
            self.job_search_field.value = job_no
            self.job_results_container.visible = False
            self.job_clear_button.visible = False
            self.selected_job_card.visible = True
            self.reset_promotion()
            self.temp_items.clear()
            self._update_selected_items_table()
        
        self.page.update()
    
    def reset_promotion(self):
        self.applied_promotion = None
        self.selected_promotion_id = None
        self.promotion_discount_amount = 0
        self.promotion_parts = []
        self.promotion_services = []
        self.promotion_info_text.value = ""
        self.promotion_discount_text.value = ""
        self.promotion_details_card.visible = False
        self.promotion_container.visible = False
        self.page.update()
    
    def show_job_detail_dialog(self, e=None):
        if not self.selected_job_id or not self.selected_order:
            self.show_snackbar(get_text("select_job_order_first"), True)
            return
        dialog = show_job_order_detail_dialog(self.selected_order, self.primary_color, self.show_snackbar)
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    # ----------------------------------------------------------------------
    # Search Items Handlers
    # ----------------------------------------------------------------------
    def on_search_change(self, e):
        self.search_items()
    
    def on_parts_click(self, e):
        self.current_tab = "parts"
        self.parts_tab.bgcolor = self.primary_color
        self.parts_tab.content.color = ft.Colors.WHITE
        self.services_tab.bgcolor = ft.Colors.GREY_200
        self.services_tab.content.color = "#64748B"
        self.search_field.hint_text = get_text("search_parts")
        self.search_items()
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
        self.search_items()
        self.category_chips.controls.clear()
        self.category_chips.visible = False
        self.page.update()
    
    def search_items(self):
        """Search and display parts or services based on current tab"""
        self.results_list.controls.clear()
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        
        if self.current_tab == "parts":
            results = self.parts_list
            if keyword:
                results = [p for p in results if keyword in p.get("name", "").lower()]
            if self.current_category_id is not None:
                results = [p for p in results if p.get("category_id") == self.current_category_id]
            
            if not results:
                empty_container = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=48, color="#CBD5E1"),
                        ft.Text(get_text("no_items_found"), size=14, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
                self.results_list.controls.append(empty_container)
            else:
                for part in results[:30]:
                    stock = part.get('stock_qty', 0)
                    min_stock = part.get('min_stock', 5)
                    
                    if stock <= min_stock:
                        stock_color = "#EF4444"
                        stock_bg = "#FEE2E2"
                        stock_text = f"{get_text('low_stock')}: {stock}"
                    elif stock <= min_stock * 2:
                        stock_color = "#F59E0B"
                        stock_bg = "#FEF3C7"
                        stock_text = f"{get_text('stock')}: {stock}"
                    else:
                        stock_color = "#10B981"
                        stock_bg = "#D1FAE5"
                        stock_text = f"{get_text('stock')}: {stock}"
                    
                    add_callback = functools.partial(self.add_item, "part", part.get('id'), part.get('name'), part.get('sell_price', 0), part.get('stock_qty', 0))
                    
                    item_card = ft.Container(
                        content=ft.Row([
                            ft.Container(content=ft.Icon(ft.Icons.INVENTORY_2, size=28, color=self.primary_color), bgcolor=ft.Colors.with_opacity(0.1, self.primary_color), border_radius=12, padding=ft.Padding(left=10, right=10, top=10, bottom=10)),
                            ft.Column([
                                ft.Text(part.get("name", "-"), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                                ft.Row([
                                    ft.Container(content=ft.Text(stock_text, size=11, color=stock_color), bgcolor=stock_bg, border_radius=12, padding=ft.Padding(left=8, right=8, top=2, bottom=2)),
                                    ft.Text(f"{int(part.get('sell_price', 0)):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.primary_color),
                                ], spacing=8),
                            ], expand=True, spacing=4),
                            ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_size=28, icon_color=self.primary_color, on_click=add_callback),
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.Padding(left=12, right=12, top=12, bottom=12),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                    )
                    self.results_list.controls.append(item_card)
        else:
            results = self.services_list
            if keyword:
                results = [s for s in results if keyword in s.get("name", "").lower()]
            
            if not results:
                empty_container = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=48, color="#CBD5E1"),
                        ft.Text(get_text("no_items_found"), size=14, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
                self.results_list.controls.append(empty_container)
            else:
                for service in results[:30]:
                    add_callback = functools.partial(self.add_item, "service", service.get('id'), service.get('name'), service.get('price', 0))
                    
                    item_card = ft.Container(
                        content=ft.Row([
                            ft.Container(content=ft.Icon(ft.Icons.BUILD, size=28, color=self.primary_color), bgcolor=ft.Colors.with_opacity(0.1, self.primary_color), border_radius=12, padding=ft.Padding(left=10, right=10, top=10, bottom=10)),
                            ft.Column([
                                ft.Text(service.get("name", "-"), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                                ft.Row([
                                    ft.Text(service.get("description", "-")[:50], size=11, color="#64748B"),
                                    ft.Text(f"{int(service.get('price', 0)):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.primary_color),
                                ], spacing=8),
                            ], expand=True, spacing=4),
                            ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_size=28, icon_color=self.primary_color, on_click=add_callback),
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.Padding(left=12, right=12, top=12, bottom=12),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                    )
                    self.results_list.controls.append(item_card)
        
        self.page.update()
    
    # ----------------------------------------------------------------------
    # Item Management
    # ----------------------------------------------------------------------
    def add_item(self, item_type, ref_id, name, price, stock_qty=0, e=None):
        if not ref_id:
            self.show_snackbar(get_text("invalid_item_missing_id"), True)
            return
        
        qty = int(self.qty_field.value) if self.qty_field.value and self.qty_field.value.isdigit() else 1
        
        # Check if item already exists in temp_items and update quantity
        existing = next((item for item in self.temp_items if item.get("item_type") == item_type and item.get("ref_id") == ref_id), None)
        if existing:
            existing["qty"] += qty
            existing["total"] = existing["qty"] * existing["unit_price"]
        else:
            self.temp_id_counter += 1
            new_item = {
                "temp_id": self.temp_id_counter,
                "item_type": item_type,
                "ref_id": ref_id,
                "name": name,
                "qty": qty,
                "unit_price": price,
                "total": qty * price,
            }
            # Store stock quantity for parts to enable warning
            if item_type == "part":
                new_item["stock_qty"] = stock_qty
            self.temp_items.append(new_item)
        
        self._update_selected_items_table()
        self.show_snackbar(f"{get_text('added')}: {name}", "success")
        self.page.update()
    
    def remove_item(self, temp_id, e=None):
        self.temp_items = [item for item in self.temp_items if item.get("temp_id") != temp_id]
        self._update_selected_items_table()
        self.page.update()
    
    # ----------------------------------------------------------------------
    # Actions
    # ----------------------------------------------------------------------
    def _calc_per_item_discounts(self):
        """Distribute total promotion discount proportionally across eligible items.
        Returns a dict mapping temp_id -> discount_amount for that item."""
        if not self.applied_promotion or self.promotion_discount_amount <= 0:
            return {}
        
        promo_part_ids = set(self.promotion_parts)
        promo_service_ids = set(self.promotion_services)
        
        if not promo_part_ids and not promo_service_ids:
            # Global promotion: all items are eligible
            eligible_items = self.temp_items
        else:
            # Targeted promotion: only matching items get the discount
            eligible_items = [
                item for item in self.temp_items
                if (item["item_type"] == "part" and item["ref_id"] in promo_part_ids)
                or (item["item_type"] == "service" and item["ref_id"] in promo_service_ids)
            ]
        
        eligible_subtotal = sum(item.get("total", 0) for item in eligible_items)
        if eligible_subtotal == 0:
            return {}
        
        discounts = {}
        total_discount = self.promotion_discount_amount
        accumulated = 0.0
        for i, item in enumerate(eligible_items):
            if i == len(eligible_items) - 1:
                # Last item gets the remainder to avoid rounding drift
                item_discount = total_discount - accumulated
            else:
                item_discount = round((item.get("total", 0) / eligible_subtotal) * total_discount, 2)
            accumulated += item_discount
            discounts[item["temp_id"]] = item_discount
        
        return discounts
    
    # ==================== MODIFIED: SAVE QUOTATION WITH PART VALIDATION ====================
    def save_quotation(self, e=None):
        if not self.selected_job_id:
            self.show_snackbar(get_text("select_job_order_first"), "error")
            return
        if not self.temp_items:
            self.show_snackbar(get_text("please_add_items_first"), "error")
            return
        
        # --- NEW: Check if at least one part is selected ---
        has_parts = any(item.get("item_type") == "part" for item in self.temp_items)
        if not has_parts:
            self.show_snackbar(get_text("please_select_at_least_one_part"), "error")
            return
        
        try:
            # 1. Create the quotation (with promotion_id if one is selected)
            result = self.client.create_quotation(
                self.selected_job_id,
                promotion_id=self.selected_promotion_id if self.applied_promotion else None,
            )
            if result and result.get("id"):
                qid = result.get("id")
                
                # 2. Compute per-item discount shares so each item carries its portion
                item_discounts = self._calc_per_item_discounts()
                
                # 3. Add all items with their individual discount amounts
                for item in self.temp_items:
                    item_discount = item_discounts.get(item["temp_id"], 0)
                    if item["item_type"] == "custom":
                        self.client.add_quotation_item(
                            qid,
                            item_type="custom",
                            ref_id=None,
                            qty=item["qty"],
                            discount_amount=item_discount,
                            custom_name=item["name"],
                            unit_price=item["unit_price"],
                        )
                    else:
                        self.client.add_quotation_item(
                            qid,
                            item["item_type"],
                            item["ref_id"],
                            item["qty"],
                            item_discount,
                        )
                
                # 4. Apply promotion to quotation header (sets promotion_id + discount_amount → triggers recalculation)
                if self.applied_promotion and self.promotion_discount_amount > 0:
                    self.client.update_quotation_promotion(
                        qid,
                        promotion_id=self.selected_promotion_id,
                        discount_amount=self.promotion_discount_amount,
                    )
                else:
                    # No promotion — still recalculate totals
                    self.client.calculate_quotation_total(qid)
                
                self.show_snackbar(f"{get_text('quotation_saved_successfully')}", "success")
                self.navigate("quotation_list")
            else:
                self.show_snackbar(get_text("create_failed"), "error")
        except Exception as ex:
            print(f"ERROR: {ex}")
            self.show_snackbar(f"{get_text('error')}: {ex}", "error")
    
    def show_snackbar(self, msg, type="success"):
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
                    ft.Text(msg, color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.W_500),
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

    # ==================== MODIFIED: ADD CUSTOM SERVICE DIALOG (NO QUANTITY FIELD) ====================
    def show_add_custom_service_dialog(self, e=None):
        """ແດງ Dialog ເພີ່ມບໍລິການທີ່ສ້າງເອງ (ບໍ່ມີຟີນຈຳນວນ) ດ້ວຍ UI ທີ່ທັນສະໄໝ"""
        
        name_input = ft.TextField(
            label=get_text("service_name") or "ຊື່ບໍລິການ",
            hint_text="ປ້ອນຊື່ບໍລິການ",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        price_input = ft.TextField(
            label=get_text("price") or "ລາຄາ (KIP)",
            hint_text="0",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            input_filter=ft.NumbersOnlyInputFilter(),
            content_padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        def on_confirm(evt):
            if not name_input.value:
                name_input.error_text = get_text("required_field")
                name_input.update()
                return
            if not price_input.value:
                price_input.error_text = get_text("required_field")
                price_input.update()
                return
            
            # ກຳນົດຈຳນວນເປັນ 1 ສະເໝີ (ບໍ່ມີຟີນໃຫ້ປ້ອນ)
            qty = 1
            price = float(price_input.value) if price_input.value else 0.0
            
            self.temp_id_counter += 1
            self.temp_items.append({
                "temp_id": self.temp_id_counter,
                "item_type": "custom",
                "ref_id": None,
                "name": name_input.value,
                "qty": qty,
                "unit_price": price,
                "total": qty * price
            })
            
            self._update_selected_items_table()
            dialog.open = False
            self.page.update()
            self.show_snackbar(f"{get_text('added')}: {name_input.value}", "success")
            
        def on_close(evt):
            dialog.open = False
            self.page.update()
        
        # ສ້າງ Dialog ດ້ວຍ UI ທີ່ທັນສະໄໝ ແລະ ເຂົ້າກັບໜ້າອື່ນ
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.ADD_CIRCLE, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(
                            get_text("add_custom_service") or "ເພີ່ມບໍລິການ",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(height=4),
                    name_input,
                    ft.Container(height=12),
                    price_input,
                    ft.Container(height=4),
                    ft.Text(
                        "ຈຳນວນຈະຖືກກຳນົດເປັນ 1 ອັດຕະໂນມັດ",
                        size=12,
                        color="#94A3B8",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], spacing=0),
                padding=ft.Padding(left=20, right=20, top=12, bottom=20),
                width=360,
                height=200,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            get_text("cancel") or "ຍົກເລີກ",
                            on_click=on_close,
                            style=ft.ButtonStyle(
                                color="#64748B",
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.ElevatedButton(
                            get_text("confirm") or "ຢືນຢັນ",
                            on_click=on_confirm,
                            style=ft.ButtonStyle(
                                bgcolor=self.primary_color,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                                padding=ft.Padding(left=20, right=20, top=10, bottom=10),
                            ),
                        ),
                    ], spacing=12, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()