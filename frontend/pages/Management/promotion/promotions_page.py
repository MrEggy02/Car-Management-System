# pages/Management/promotion/promotions_page.py
import flet as ft
import sys
import os
import asyncio
import traceback
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from i18n import get_text
from Management.promotion.promotions_dialogs import (
    show_add_promotion_dialog,
    show_edit_promotion_dialog,
    show_delete_promotion_dialog,
    show_detail_promotion_dialog
)


class PromotionsContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.is_loading = False
        self.current_dialog = None
        self.current_snackbar = None
        self.promotions_data = []
        self.filtered_promotions = []
        self.search_input = None
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.pagination_container = ft.Container()
    
    def build(self):
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("promotions_title"), 
                                size=18, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.WHITE
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
                        on_click=lambda e: self.show_add_dialog(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=0,
                            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
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
        
        self.search_input = ft.TextField(
            hint_text=f" {get_text('search')} {get_text('promotions_title')}...",
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            on_change=self.filter_promotions,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        control_bar = ft.Container(
            content=self.search_input,
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor="#F5F7FA",
        )
        
        table_header = self._create_table_header()
        
        table_scroll_container = ft.Container(
            content=self.table_rows,
            expand=True,
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            bgcolor=ft.Colors.WHITE,
        )
        
        table_container = ft.Container(
            content=ft.Column([table_header, ft.Divider(height=1, color=ft.Colors.GREY_300), table_scroll_container], spacing=0),
            margin=ft.Margin(left=16, right=16, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12, bottom_left=12, bottom_right=12),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
        )
        
        self.update_pagination_controls()
        
        main_content = ft.Container(
            content=ft.Column([table_container, self.pagination_container], spacing=0),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.page.run_task(self._delayed_load)
        
        return ft.Column([header, control_bar, main_content], expand=True, spacing=0)
    
    def _create_table_header(self):
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("#", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=45, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('promo_name'), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=200, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text('discount_type'), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text('discount_value'), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=110, alignment=ft.Alignment(1, 0), padding=ft.Padding(left=0, right=8, top=0, bottom=0)),
                ft.Container(content=ft.Text(get_text('period'), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=160, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('status'), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=80, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text('actions'), size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=200, alignment=ft.Alignment(0, 0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=10, bottom=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _format_discount(self, discount_type, value):
        if discount_type == 'percent':
            return f"{int(value)}%"
        else:
            return f"{int(value):,} KIP"
    
    def _format_date(self, date_str):
        if not date_str:
            return "-"
        try:
            if isinstance(date_str, datetime):
                return date_str.strftime('%d-%m-%Y')
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
            return date_obj.strftime('%d-%m-%Y')
        except:
            return str(date_str)[:10]
    
    def _get_status_badge(self, status, start_date, end_date):
        try:
            today = datetime.now().date()
            if end_date:
                end = datetime.strptime(str(end_date), '%Y-%m-%d').date()
                if end < today:
                    status = 'inactive'
        except:
            pass
        
        if status == 'active':
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color="#2E7D32"),
                    ft.Text(get_text("status_active"), size=10, color="#2E7D32"),
                ], spacing=4),
                bgcolor="#E8F5E9",
                border_radius=12,
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
            )
        else:
            return ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color="#DC2626"),
                    ft.Text(get_text("status_inactive"), size=10, color="#DC2626"),
                ], spacing=4),
                bgcolor="#FFEEEE",
                border_radius=12,
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
            )
    
    def _create_table_row(self, promo, index, row_number):
        promo_id = promo.get('id')
        name = promo.get('name', '-')
        discount_type = promo.get('discount_type', 'percent')
        value = promo.get('value', 0)
        min_amount = promo.get('min_amount', 0)
        start_date = promo.get('start_date')
        end_date = promo.get('end_date')
        status = promo.get('status', 'active')
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        discount_display = self._format_discount(discount_type, value)
        discount_type_label = get_text("percentage") if discount_type == "percent" else get_text("fixed_amount")
        
        start_display = self._format_date(start_date)
        end_display = self._format_date(end_date)
        if start_display == "-" and end_display == "-":
            period_display = "-"
        else:
            period_display = f"{start_display} - {end_display}"
        
        try:
            today = datetime.now().date()
            if end_date:
                end = datetime.strptime(str(end_date), '%Y-%m-%d').date()
                if end < today and status == 'active':
                    status = 'inactive'
        except:
            pass
        
        status_badge = self._get_status_badge(status, start_date, end_date)
        
        req_text = ""
        if min_amount > 0:
            req_text = f"Min {int(min_amount):,} KIP"
        
        # Detail button - eye icon
        detail_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_RED_EYE,
            icon_size=16,
            icon_color="#1565C0",
            on_click=lambda e, pid=promo_id, pname=name: self.show_detail_dialog(pid, pname),
            tooltip=get_text("detail"),
            style=ft.ButtonStyle(padding=ft.Padding(left=4, right=4, top=4, bottom=4)),
        )
        
        edit_btn = ft.IconButton(
            icon=ft.Icons.EDIT_OUTLINED,
            icon_size=16,
            icon_color="#1565C0",
            on_click=lambda e, pid=promo_id: self._safe_edit(pid),
            tooltip=get_text("edit"),
            style=ft.ButtonStyle(padding=ft.Padding(left=4, right=4, top=4, bottom=4)),
        )
        
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_size=16,
            icon_color=ft.Colors.RED_600,
            on_click=lambda e, pid=promo_id: self._safe_delete(pid),
            tooltip=get_text("delete"),
            style=ft.ButtonStyle(padding=ft.Padding(left=4, right=4, top=4, bottom=4)),
        )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(str(row_number), size=12, weight=ft.FontWeight.W_500, color="#1565C0"),
                        padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=4,
                        alignment=ft.Alignment(0, 0),
                    ),
                    width=45,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(name, size=12, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
                        ft.Text(req_text, size=9, color="#64748B") if req_text else ft.Container(),
                    ], spacing=1),
                    width=200,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                    tooltip=name,
                ),
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(discount_type_label, size=11, color="#64748B"),
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=4,
                        padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                    ),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(discount_display, size=12, weight=ft.FontWeight.W_600, color=ft.Colors.ORANGE_700),
                    width=110,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=8, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(period_display, size=10, color=ft.Colors.GREY_600, max_lines=1),
                    width=160,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=status_badge,
                    width=80,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Row([detail_btn, edit_btn, delete_btn], spacing=0),
                    width=200,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
            bgcolor=row_bg,
        )
        
        return ft.Column([row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0)
    
    def _create_empty_state(self):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOCAL_OFFER, size=48, color=ft.Colors.GREY_300),
                ft.Container(height=8),
                ft.Text(get_text("no_data"), size=14, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add"), size=12, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.Alignment(0, 0)),
            padding=ft.Padding(left=30, right=30, top=30, bottom=30),
            expand=True,
        )
    
    def update_pagination_controls(self):
        if not self.filtered_promotions:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (len(self.filtered_promotions) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Container(
            content=ft.Row([
                ft.Text(f"{get_text('showing')} {len(self.filtered_promotions)} {get_text('of')} {len(self.promotions_data)} {get_text('results')}", size=11, color="#64748B"),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_size=18, on_click=self.prev_page, disabled=prev_disabled, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
                        ft.Container(content=ft.Text(f"{self.current_page}/{self.total_pages}", size=12, weight=ft.FontWeight.W_500, color="#1E293B"), padding=ft.Padding(left=12, right=12, top=0, bottom=0)),
                        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_size=18, on_click=self.next_page, disabled=next_disabled, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
                    ]),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=8,
                    padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            bgcolor="#F5F7FA",
        )
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_promotions(self.filtered_promotions)
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_promotions(self.filtered_promotions)
    
    def filter_promotions(self, e=None):
        query = self.search_input.value.lower() if self.search_input.value else ""
        self.current_page = 1
        
        if not query:
            self.filtered_promotions = self.promotions_data.copy()
        else:
            self.filtered_promotions = [promo for promo in self.promotions_data if query in promo.get('name', '').lower()]
        
        self.display_promotions(self.filtered_promotions)
    
    def display_promotions(self, promotions):
        self.table_rows.controls.clear()
        
        if not promotions:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_promotions = promotions[start_idx:end_idx]
            global_start = start_idx + 1
            
            for i, promo in enumerate(page_promotions):
                row_number = global_start + i
                row = self._create_table_row(promo, start_idx + i, row_number)
                self.table_rows.controls.append(row)
        
        self.update_pagination_controls()
        self.page.update()
    
    async def _delayed_load(self):
        await asyncio.sleep(0.2)
        await asyncio.to_thread(self.load_data)
    
    def load_data(self):
        if self.is_loading:
            return
        self.is_loading = True
        
        try:
            print("DEBUG: Loading promotions data...")
            self.promotions_data = self.client.get_promotions()
            self.filtered_promotions = self.promotions_data.copy()
            print(f"DEBUG: Loaded {len(self.promotions_data)} promotions")
            self.display_promotions(self.filtered_promotions)
        except Exception as e:
            print(f"DEBUG: Error loading promotions: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
        finally:
            self.is_loading = False
    
    def _safe_edit(self, promo_id):
        try:
            self.edit_promotion(promo_id)
        except Exception as e:
            print(f"DEBUG: Error in edit: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
    
    def _safe_delete(self, promo_id):
        try:
            self.delete_promotion(promo_id)
        except Exception as e:
            print(f"DEBUG: Error in delete: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
    
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
    
    def show_add_dialog(self):
        dialog = show_add_promotion_dialog(
            self.page,
            self.primary_color,
            self.client,
            self._close_dialog,
            self.load_data,
            self.show_snackbar
        )
        self._open_dialog(dialog)
    
    def edit_promotion(self, promo_id):
        promo = next((p for p in self.promotions_data if p.get('id') == promo_id), None)
        if not promo:
            self.show_snackbar(f"❌ {get_text('error')}", "error")
            return
        
        dialog = show_edit_promotion_dialog(
            self.page,
            self.primary_color,
            self.client,
            promo,
            self._close_dialog,
            self.load_data,
            self.show_snackbar
        )
        self._open_dialog(dialog)
    
    def delete_promotion(self, promo_id):
        promo = next((p for p in self.promotions_data if p.get('id') == promo_id), None)
        if not promo:
            self.show_snackbar(f"❌ {get_text('error')}", "error")
            return
        
        dialog = show_delete_promotion_dialog(
            self.primary_color,
            promo,
            self._close_dialog,
            self.load_data,
            self.show_snackbar,
            self.client
        )
        self._open_dialog(dialog)
    
    def show_detail_dialog(self, promotion_id: int, promotion_name: str):
        dialog = show_detail_promotion_dialog(
            self.primary_color,
            self.client,
            promotion_id,
            promotion_name,
            self._close_dialog,
            self.load_data,
            self.show_snackbar
        )
        self._open_dialog(dialog)
    
    def show_snackbar(self, message, type="success"):
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