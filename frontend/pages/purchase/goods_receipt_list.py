# pages/purchase/goods_receipt_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import asyncio  # เพิ่ม import asyncio

from i18n import get_text


class GoodsReceiptListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.current_snackbar = None
        self.receipts = []
        self.filtered_receipts = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.search_field = None
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
            ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.page.run_task(self._load_data_async)
        
        return main_content

    async def _load_data_async(self):
        await asyncio.sleep(0.1)
        await asyncio.to_thread(self.load_receipts)
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=24,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("purchase_order_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("goods_receipt_history_title"),
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
        self.search_field = ft.TextField(
            hint_text=get_text("search_purchase_order") + " / " + get_text("goods_receipt_no"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
        )
        self.search_field.on_change = self.on_search_change
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_receipts(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        return ft.Container(
            content=ft.Row([self.search_field, refresh_button], spacing=10),
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
        )
    
    def _build_table(self):
        table_header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("goods_receipt_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("po_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("supplier"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=180,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("receipt_date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=140,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("total_amount"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=8, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("received_by"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text("action"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=80,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
        
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        table_content = ft.Column([
            table_header,
            ft.Divider(height=1, color=ft.Colors.GREY_300),
            self.table_rows,
        ], spacing=0)
        
        table_scroll = ft.Container(
            content=table_content,
            width=950,
        )
        
        return ft.Container(
            content=ft.Row([table_scroll], scroll=ft.ScrollMode.AUTO),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
        )
    
    def load_receipts(self):
        self.table_rows.controls.clear()
        self.page.update()
        
        try:
            receipts = self.client.get_goods_receipts()
            self.receipts = receipts
            self.filtered_receipts = receipts.copy()
            self.display_receipts()
        except Exception as ex:
            print(f"Error loading goods receipts: {ex}")
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
            
    def on_search_change(self, e):
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        if keyword:
            self.filtered_receipts = [
                r for r in self.receipts
                if keyword in r.get("receipt_no", "").lower()
                or keyword in r.get("po_no", "").lower()
                or keyword in r.get("supplier_name", "").lower()
            ]
        else:
            self.filtered_receipts = self.receipts.copy()
            
        self.current_page = 1
        self.display_receipts()
        
    def display_receipts(self):
        self.table_rows.controls.clear()
        total_items = len(self.filtered_receipts)
        
        if total_items == 0:
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=48, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_goods_receipts"), size=16, color=ft.Colors.GREY_500),
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
        page_items = self.filtered_receipts[start_idx:end_idx]
        
        for i, receipt in enumerate(page_items):
            self.table_rows.controls.append(self._create_receipt_row(receipt, start_idx + i))
            
        self.update_pagination()
        self.page.update()
        
    def _create_receipt_row(self, receipt: Dict, index: int):
        receipt_id = receipt.get("id")
        receipt_no = receipt.get("receipt_no", "-")
        po_no = receipt.get("po_no", "-")
        supplier_name = receipt.get("supplier_name", "-")
        receipt_date = receipt.get("receipt_date", "")
        if receipt_date:
            receipt_date = receipt_date[:16]
        else:
            receipt_date = "-"
        total_amount = receipt.get("total_amount", 0)
        received_by_name = receipt.get("received_by_name", "-")
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        view_btn = ft.IconButton(
            icon=ft.Icons.VISIBILITY_OUTLINED,
            icon_size=18,
            tooltip=get_text("view_receipt_detail"),
            on_click=lambda e: self.show_receipt_detail_dialog(receipt_id),
        )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(receipt_no, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=130,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(po_no, size=13, color="#1E293B"),
                    width=120,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(supplier_name, size=13, color="#1E293B", max_lines=1),
                    width=180,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(receipt_date, size=12, color="#64748B"),
                    width=140,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(f"{int(total_amount):,}", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=8, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(received_by_name, size=12, color="#64748B", max_lines=1),
                    width=130,
                    padding=ft.Padding(left=8, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=view_btn,
                    width=80,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=10, bottom=10),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
        
    def show_receipt_detail_dialog(self, receipt_id: int):
        try:
            detail = self.client.get_goods_receipt(receipt_id)
            if not detail:
                self.show_snack_bar("Goods receipt details not found", "error")
                return
                
            items = detail.get("items", [])
            items_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=250)
            
            for idx, item in enumerate(items):
                bg_color = ft.Colors.GREY_50 if idx % 2 == 0 else ft.Colors.WHITE
                
                qty = item.get("qty_received", 0)
                cost = item.get("cost_price", 0)
                line_total = item.get("total_price", 0)
                
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Text(f"#{item.get('part_id')}", size=12, color="#64748B", width=60),
                        ft.Text(item.get("part_name", "-"), size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                        ft.Text(f"{qty}", size=13, color="#1E293B", width=60, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{int(cost):,}", size=13, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                        ft.Text(f"{int(line_total):,}", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700, width=110, text_align=ft.TextAlign.RIGHT),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    bgcolor=bg_color,
                    border_radius=8,
                )
                items_list.controls.append(item_row)
                
            dialog = ft.AlertDialog(
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=16),
                bgcolor=ft.Colors.WHITE,
                title=ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.INVENTORY, size=24, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=12,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(
                            f"{get_text('view_receipt_detail')}: {detail.get('receipt_no', '-')}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                        ),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                    border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"{get_text('po_no')}: {detail.get('po_no', '-')}", size=13, color="#64748B"),
                            ft.Container(expand=True),
                            ft.Text(f"{get_text('receipt_date')}: {detail.get('receipt_date', '')[:16]}", size=13, color="#64748B"),
                        ]),
                        ft.Row([
                            ft.Text(f"{get_text('supplier')}: {detail.get('supplier_name', '-')}", size=13, color="#64748B"),
                            ft.Container(expand=True),
                            ft.Text(f"{get_text('received_by')}: {detail.get('received_by_name', '-')}", size=13, color="#64748B"),
                        ]),
                        ft.Container(height=12),
                        ft.Row([
                            ft.Text(get_text("part_id"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", width=60),
                            ft.Text(get_text("part_name"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                            ft.Text(get_text("qty"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", width=60, text_align=ft.TextAlign.CENTER),
                            ft.Text(get_text("unit_cost"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                            ft.Text(get_text("total"), size=11, weight=ft.FontWeight.BOLD, color="#64748B", width=110, text_align=ft.TextAlign.RIGHT),
                        ], spacing=10),
                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                        items_list,
                        ft.Divider(height=1, color=ft.Colors.GREY_200),
                        ft.Row([
                            ft.Text(get_text("total_amount"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Container(expand=True),
                            ft.Text(f"{int(detail.get('total_amount', 0)):,} KIP", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ], spacing=10),
                    padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                    width=650,
                    height=450,
                ),
                actions=[
                    ft.TextButton(
                        get_text("close"),
                        on_click=lambda e: self._close_dialog(dialog),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self._open_dialog(dialog)
        except Exception as ex:
            print(f"Error displaying receipt details: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", "error")
            
    def _open_dialog(self, dialog):
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
        
    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
        
    def update_pagination(self):
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_receipts)} {get_text('of')} {len(self.receipts)} {get_text('results')}",
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
            self.display_receipts()
            
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_receipts()
            
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