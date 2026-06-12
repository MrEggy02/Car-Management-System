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
        self.current_category = "all"
        
    def build(self):
        # --- Header ---
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=18, color=ft.Colors.WHITE)], spacing=6),
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=8, vertical=8),
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
                                padding=ft.padding.symmetric(horizontal=20, vertical=10),
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
            padding=ft.padding.symmetric(vertical=12, horizontal=24),
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
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
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
        
        self.job_results_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=200)
        self.job_results_container = ft.Container(
            content=self.job_results_list,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=12,
            padding=ft.padding.all(8),
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
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                ),
                elevation=0,
                margin=ft.margin.all(0),
            ),
            margin=ft.margin.only(top=8),
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
            padding=ft.padding.all(12),
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
                padding=ft.padding.all(12),
            ),
            elevation=0,
            margin=ft.margin.only(top=4),
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
                ft.Container(content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=45, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("item_name"), size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=150, alignment=ft.Alignment(-1, 0)),
                ft.Container(content=ft.Text(get_text("quantity_short"), size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=100, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("price_kip_short"), size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=120, alignment=ft.Alignment(1, 0)),
                ft.Container(content=ft.Text(get_text("total_kip_short"), size=12, weight=ft.FontWeight.BOLD, color="#64748B"), width=120, alignment=ft.Alignment(1, 0)),
                ft.Container(content=ft.Text("", size=12), width=45),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=8,
        )
        
        self.items_table_body = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, height=250)
        selected_items_table = ft.Column([table_header, ft.Divider(height=1, color=ft.Colors.GREY_200), self.items_table_body], spacing=0)
        
        selected_section = ft.Column([
            ft.Row([ft.Icon(ft.Icons.LIST_ALT, size=18, color=self.primary_color), ft.Text(get_text("selected_items"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"), ft.Container(expand=True),
                ft.Container(content=ft.Row([ft.Text(get_text("total_amount") + ":", size=13, weight=ft.FontWeight.W_500, color="#64748B"), self.total_text], spacing=8), padding=ft.padding.symmetric(horizontal=10, vertical=5), bgcolor=ft.Colors.GREY_50, border_radius=20)],
                spacing=8),
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            ft.Container(height=10),
            selected_items_table,
        ], spacing=0)
        
        # ==================== SELECT ITEMS SECTION ====================
        self.parts_tab = ft.Container(content=ft.Text(get_text("parts"), size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), bgcolor=self.primary_color, border_radius=25, padding=ft.padding.symmetric(horizontal=28, vertical=8), expand=True)
        self.parts_tab.on_click = self.on_parts_click
        
        self.services_tab = ft.Container(content=ft.Text(get_text("services"), size=14, weight=ft.FontWeight.W_600, color="#64748B"), bgcolor=ft.Colors.GREY_200, border_radius=25, padding=ft.padding.symmetric(horizontal=28, vertical=8), expand=True)
        self.services_tab.on_click = self.on_services_click
        
        self.category_chips = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        self.search_field = ft.TextField(hint_text=get_text("search_items"), border_radius=25, bgcolor=ft.Colors.GREY_100, filled=True, prefix_icon=ft.Icons.SEARCH, border_color=ft.Colors.TRANSPARENT, content_padding=ft.padding.symmetric(horizontal=18, vertical=14), expand=True)
        self.search_field.on_change = self.on_search_change
        
        self.qty_field = ft.TextField(label=get_text("quantity"), value="1", width=100, border_radius=12, bgcolor=ft.Colors.GREY_100, filled=True, input_filter=ft.NumbersOnlyInputFilter(), text_align=ft.TextAlign.CENTER, content_padding=ft.padding.symmetric(horizontal=12, vertical=12))
        
        self.results_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=320)
        welcome_container = ft.Container(content=ft.Column([ft.Icon(ft.Icons.SEARCH, size=48, color="#CBD5E1"), ft.Text(get_text("type_to_search"), size=14, color="#94A3B8"), ft.Text(get_text("search_parts_or_services"), size=12, color="#CBD5E1")], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8), alignment=ft.Alignment(0, 0), padding=ft.padding.all(40))
        self.results_list.controls.append(welcome_container)
        
        results_container = ft.Container(content=self.results_list, border=ft.border.all(1, ft.Colors.GREY_200), border_radius=12, padding=ft.padding.all(10), bgcolor=ft.Colors.GREY_50, expand=True)
        
        select_items_section = ft.Column([
            ft.Row([ft.Icon(ft.Icons.SHOPPING_CART, size=18, color=self.primary_color), ft.Text(get_text("select_items"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B")], spacing=8),
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
        left_column = ft.Container(content=ft.Column([job_section, ft.Container(height=20), promotion_section, ft.Container(height=20), selected_section], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO), width=640)
        right_column = ft.Container(content=select_items_section, width=560, expand=True)
        
        two_columns_row = ft.Row([left_column, ft.VerticalDivider(width=1, color=ft.Colors.GREY_300), right_column], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.AUTO)
        
        big_card = ft.Container(content=two_columns_row, padding=ft.padding.symmetric(horizontal=24, vertical=20), bgcolor=ft.Colors.WHITE, border_radius=16)
        
        scrollable_content = ft.Column([big_card], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
        content_area = ft.Container(content=scrollable_content, expand=True, padding=ft.padding.all(20), bgcolor="#F0F2F5")
        
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
                    padding=ft.padding.all(16),
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
            # Get promotion items
            promo_parts = []
            promo_services = []
            try:
                promo_parts = self.client.get_promotion_parts(promo.get('id')) or []
                promo_services = self.client.get_promotion_services(promo.get('id')) or []
                promo_parts = [p.get('part_id') for p in promo_parts if p.get('part_id')]
                promo_services = [s.get('service_id') for s in promo_services if s.get('service_id')]
            except:
                pass
            
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
            
            # Calculate discount for display
            if promo['discount_type'] == 'percent':
                discount_amount = subtotal * (promo['value'] / 100)
                discount_display = f"{int(promo['value'])}%"
            else:
                discount_amount = promo['value']
                discount_display = f"{int(promo['value']):,} KIP"
            
            discount_amount = min(discount_amount, subtotal)
            
            # Create promotion card
            promo_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.LOCAL_OFFER, size=20, color="#10B981"),
                            ft.Text(promo.get('name', '-'), size=14, weight=ft.FontWeight.BOLD, color="#1E293B", expand=True),
                            ft.Container(
                                content=ft.Text(f"{discount_display}", size=13, weight=ft.FontWeight.BOLD, color="#10B981"),
                                bgcolor=ft.Colors.GREEN_50,
                                border_radius=12,
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            ),
                        ], spacing=8),
                        ft.Container(height=4),
                        ft.Text(f"{get_text('you_save')}: {int(discount_amount):,} KIP", size=12, color="#64748B"),
                        ft.Text(f"{get_text('min_amount_required')}: {int(min_amount):,} KIP" if min_amount > 0 else "", size=11, color="#F59E0B"),
                        ft.Container(height=4),
                        ft.Row([
                            ft.Container(expand=True),
                            ft.ElevatedButton(
                                content=ft.Text(get_text("apply"), size=12, color=ft.Colors.WHITE),
                                on_click=lambda e, p=promo: self.apply_promotion(p),
                                style=ft.ButtonStyle(
                                    bgcolor=self.primary_color,
                                    shape=ft.RoundedRectangleBorder(radius=6),
                                    elevation=0,
                                    padding=ft.padding.symmetric(horizontal=16, vertical=6),
                                ),
                            ),
                        ]),
                    ], spacing=4),
                    padding=ft.padding.all(12),
                ),
                elevation=0,
                margin=ft.margin.only(bottom=8),
            )
            self.promotion_list_container.controls.append(promo_card)
        
        if not self.available_promotions:
            self.promotion_list_container.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_applicable_promotions"), size=12, color="#94A3B8"),
                    padding=ft.padding.all(16),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        self.promotion_container.visible = True
        self.page.update()
    
    def apply_promotion(self, promo):
        """Apply selected promotion"""
        self.applied_promotion = promo
        self.selected_promotion_id = promo.get('id')
        
        # Load promotion items
        self.promotion_parts = []
        self.promotion_services = []
        try:
            parts = self.client.get_promotion_parts(self.selected_promotion_id)
            self.promotion_parts = [p.get('part_id') for p in parts if p.get('part_id')]
        except:
            pass
        try:
            services = self.client.get_promotion_services(self.selected_promotion_id)
            self.promotion_services = [s.get('service_id') for s in services if s.get('service_id')]
        except:
            pass
        
        # Calculate discount
        subtotal = sum(item.get("total", 0) for item in self.temp_items)
        min_amount = promo.get('min_amount', 0)
        
        if subtotal < min_amount:
            self.promotion_discount_amount = 0
            self.promotion_discount_text.value = f"⚠️ {get_text('add_more_to_get_discount')} (+{int(min_amount - subtotal):,} KIP)"
            self.promotion_discount_text.color = "#F59E0B"
        else:
            if promo['discount_type'] == 'percent':
                discount_amount = subtotal * (promo['value'] / 100)
            else:
                discount_amount = promo['value']
            discount_amount = min(discount_amount, subtotal)
            self.promotion_discount_amount = discount_amount
            
            if promo['discount_type'] == 'percent':
                self.promotion_discount_text.value = f"✅ {get_text('you_save')}: {int(discount_amount):,} KIP ({int(promo['value'])}%)"
            else:
                self.promotion_discount_text.value = f"✅ {get_text('you_save')}: {int(discount_amount):,} KIP"
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
        self.load_parts_and_services()
        self.load_pending_orders()
        self.load_promotions()
    
    def _update_selected_items_table(self):
        self.items_table_body.controls.clear()
        
        if not self.temp_items:
            empty_row = ft.Container(content=ft.Text(get_text("no_items_selected"), size=13, color="#94A3B8"), padding=ft.padding.all(40), alignment=ft.Alignment(0, 0))
            self.items_table_body.controls.append(empty_row)
            self.total_text.value = "0 KIP"
            self.update_promotion_list()
            self.page.update()
            return
        
        subtotal = 0
        for idx, item in enumerate(self.temp_items):
            bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
            temp_id = item.get("temp_id")
            
            # Create remove button with lambda that captures current temp_id
            remove_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_size=18,
                icon_color="#EF4444",
                on_click=lambda e, tid=temp_id: self.remove_item(tid),
                padding=0,
            )
            
            row = ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Text(str(idx + 1), size=13, color="#64748B"), width=45, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(item.get("name", "-"), size=13, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1), width=180, alignment=ft.Alignment(-1, 0)),
                    ft.Container(content=ft.Text(str(item.get("qty", 1)), size=13, color="#1E293B"), width=70, alignment=ft.Alignment(0, 0)),
                    ft.Container(content=ft.Text(f"{int(item.get('unit_price', 0)):,}", size=13, color="#64748B"), width=120, alignment=ft.Alignment(1, 0)),
                    ft.Container(content=ft.Text(f"{int(item.get('total', 0)):,}", size=13, weight=ft.FontWeight.W_600, color="#10B981"), width=130, alignment=ft.Alignment(1, 0)),
                    ft.Container(content=remove_btn, width=45, alignment=ft.Alignment(0, 0)),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=10, horizontal=12),
                bgcolor=bg_color,
            )
            self.items_table_body.controls.append(row)
            subtotal += item.get("total", 0)
        
        subtotal_row = ft.Container(content=ft.Row([ft.Container(expand=True), ft.Text(get_text("subtotal") + ":", size=12, weight=ft.FontWeight.W_500, color="#64748B"), ft.Text(f"{int(subtotal):,} KIP", size=13, weight=ft.FontWeight.W_600, color="#1E293B")], spacing=8), padding=ft.padding.symmetric(vertical=8, horizontal=12), bgcolor=ft.Colors.GREY_100)
        self.items_table_body.controls.append(subtotal_row)
        
        final_total = subtotal
        if self.applied_promotion and self.promotion_discount_amount > 0:
            discount_row = ft.Container(content=ft.Row([ft.Container(expand=True), ft.Text(f"{get_text('promotion_discount')} ({self.applied_promotion.get('name', '')}):", size=12, color="#64748B"), ft.Text(f"-{int(self.promotion_discount_amount):,} KIP", size=13, weight=ft.FontWeight.W_600, color="#10B981")], spacing=8), padding=ft.padding.symmetric(vertical=5, horizontal=12), bgcolor=ft.Colors.GREEN_50)
            self.items_table_body.controls.append(discount_row)
            final_total = subtotal - self.promotion_discount_amount
        
        self.total_text.value = f"{int(final_total):,} KIP"
        self.update_promotion_list()
        self.page.update()
    
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
            self.parts_list = self.client.get_parts() or []
            self.services_list = self.client.get_services() or []
            self.load_category_chips()
            self.page.update()
        except Exception as ex:
            print(f"Error loading parts/services: {ex}")
    
    def load_category_chips(self):
        categories = [
            {"id": "all", "name": get_text("all_items"), "icon": ft.Icons.VIEW_LIST},
            {"id": "engine", "name": get_text("engine"), "icon": ft.Icons.SETTINGS},
            {"id": "brake", "name": get_text("brake"), "icon": ft.Icons.WARNING},
            {"id": "electrical", "name": get_text("electrical"), "icon": ft.Icons.FLASH_ON},
            {"id": "suspension", "name": get_text("suspension"), "icon": ft.Icons.SETTINGS_APPLICATIONS},
        ]
        self.category_chips.controls.clear()
        for cat in categories:
            is_active = self.current_category == cat["id"]
            chip = ft.Container(content=ft.Row([ft.Icon(cat["icon"], size=14, color=ft.Colors.WHITE if is_active else "#64748B"), ft.Text(cat["name"], size=12, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE if is_active else "#64748B")], spacing=6), bgcolor=self.primary_color if is_active else ft.Colors.GREY_200, border_radius=20, padding=ft.padding.symmetric(horizontal=12, vertical=5), ink=True, on_click=lambda e, cid=cat["id"]: self.filter_by_category(cid))
            self.category_chips.controls.append(chip)
        self.page.update()
    
    def filter_by_category(self, category_id):
        self.current_category = category_id
        self.load_category_chips()
        if self.search_field.value:
            self.search_items()
    
    def load_promotions(self):
        try:
            self.promotions_list = self.client.get_active_promotions() or []
            print(f"Loaded {len(self.promotions_list)} promotions")
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
                ft.Container(content=ft.Text(get_text("no_orders_found"), size=13, color="#94A3B8"), padding=ft.padding.all(20), alignment=ft.Alignment(0, 0))
            )
        else:
            for order in self.filtered_orders[:10]:
                order_id = order.get('id')
                job_no = order.get('job_no', '-')
                customer_name = order.get('customer_name', '-')
                plate_number = order.get('plate_number', '-')
                
                result_item = ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color), bgcolor=ft.Colors.with_opacity(0.1, self.primary_color), border_radius=10, padding=ft.padding.all(8)),
                        ft.Column([ft.Text(job_no, size=14, weight=ft.FontWeight.W_500, color="#1E293B"), ft.Text(f"{customer_name} | {plate_number}", size=11, color="#64748B")], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color="#94A3B8"),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_200),
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
        if self.search_field.value:
            self.search_items()
        else:
            self.results_list.controls.clear()
            welcome_container = ft.Container(content=ft.Column([ft.Icon(ft.Icons.SEARCH, size=48, color="#CBD5E1"), ft.Text(get_text("type_to_search"), size=14, color="#94A3B8"), ft.Text(get_text("search_parts_or_services"), size=12, color="#CBD5E1")], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8), alignment=ft.Alignment(0, 0), padding=ft.padding.all(40))
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
            self.results_list.controls.clear()
            welcome_container = ft.Container(content=ft.Column([ft.Icon(ft.Icons.SEARCH, size=48, color="#CBD5E1"), ft.Text(get_text("type_to_search"), size=14, color="#94A3B8"), ft.Text(get_text("search_parts_only"), size=12, color="#CBD5E1")], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8), alignment=ft.Alignment(0, 0), padding=ft.padding.all(40))
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
            self.results_list.controls.clear()
            welcome_container = ft.Container(content=ft.Column([ft.Icon(ft.Icons.SEARCH, size=48, color="#CBD5E1"), ft.Text(get_text("type_to_search"), size=14, color="#94A3B8"), ft.Text(get_text("search_services_only"), size=12, color="#CBD5E1")], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8), alignment=ft.Alignment(0, 0), padding=ft.padding.all(40))
            self.results_list.controls.append(welcome_container)
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
                if self.current_category != "all":
                    results = [p for p in results if p.get("category", "").lower() == self.current_category]
                
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
                    
                    add_callback = functools.partial(self.add_item, "part", part.get('id'), part.get('name'), part.get('sell_price', 0))
                    
                    item_card = ft.Container(
                        content=ft.Row([
                            ft.Container(content=ft.Icon(ft.Icons.INVENTORY_2, size=28, color=self.primary_color), bgcolor=ft.Colors.with_opacity(0.1, self.primary_color), border_radius=12, padding=ft.padding.all(10)),
                            ft.Column([
                                ft.Text(part.get("name", "-"), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                                ft.Row([
                                    ft.Container(content=ft.Text(stock_text, size=11, color=stock_color), bgcolor=stock_bg, border_radius=12, padding=ft.padding.symmetric(horizontal=8, vertical=2)),
                                    ft.Text(f"{int(part.get('sell_price', 0)):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.primary_color),
                                ], spacing=8),
                            ], expand=True, spacing=4),
                            ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_size=28, icon_color=self.primary_color, on_click=add_callback),
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
                    add_callback = functools.partial(self.add_item, "service", service.get('id'), service.get('name'), service.get('price', 0))
                    
                    item_card = ft.Container(
                        content=ft.Row([
                            ft.Container(content=ft.Icon(ft.Icons.BUILD, size=28, color=self.primary_color), bgcolor=ft.Colors.with_opacity(0.1, self.primary_color), border_radius=12, padding=ft.padding.all(10)),
                            ft.Column([
                                ft.Text(service.get("name", "-"), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                                ft.Row([
                                    ft.Text(service.get("description", "-")[:50], size=11, color="#64748B"),
                                    ft.Text(f"{int(service.get('price', 0)):,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.primary_color),
                                ], spacing=8),
                            ], expand=True, spacing=4),
                            ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_size=28, icon_color=self.primary_color, on_click=add_callback),
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.all(12),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=12,
                        border=ft.border.all(1, ft.Colors.GREY_200),
                    )
                    self.results_list.controls.append(item_card)
        
        self.page.update()
    
    # ----------------------------------------------------------------------
    # Item Management
    # ----------------------------------------------------------------------
    def add_item(self, item_type, ref_id, name, price, e=None):
        if not ref_id:
            self.show_snackbar(get_text("invalid_item_missing_id"), True)
            return
        
        self.temp_id_counter += 1
        qty = int(self.qty_field.value) if self.qty_field.value and self.qty_field.value.isdigit() else 1
        
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
        self.show_snackbar(f"✓ {get_text('added')}: {name}", False)
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
                
                # Apply promotion discount if selected
                if self.applied_promotion and self.promotion_discount_amount > 0:
                    # Here you can add promotion_id to quotation
                    pass
                
                self.client.calculate_quotation_total(qid)
                self.show_snackbar(f"✅ {get_text('quotation_saved_successfully')}", False)
                self.navigate("quotation_list")
            else:
                self.show_snackbar(get_text("create_failed"), True)
        except Exception as ex:
            print(f"ERROR: {ex}")
            self.show_snackbar(f"{get_text('error')}: {ex}", True)
    
    def show_snackbar(self, msg, is_error=False):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(msg, size=13), bgcolor="#EF4444" if is_error else "#10B981", open=True, duration=3000)
        self.page.update()