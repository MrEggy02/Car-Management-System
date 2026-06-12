# pages/quotations/quotation_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import tempfile
import os
import webbrowser
import threading
import time
from datetime import datetime

from i18n import get_text, get_current_language
from pages.quotations.quotation_dialogs import (
    show_quotation_detail_dialog,
    show_update_status_dialog,
    show_delete_quotation_dialog
)


class QuotationListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, job_order_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.job_order_id = job_order_id
        self.quotations = []
        self.filtered_quotations = []
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.selected_quotation = None
        self.detail_dialog = None
        self.search_field = None
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.current_dialog = None
        self.parts_list = []
        self.services_list = []

    def build(self):
        # ส่วนหัว
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("quotation_list"),
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
                            ft.Text(get_text("new_quotation"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.navigate("quotation_create"),
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
        
        # ช่องค้นหา
        self.search_field = ft.TextField(
            hint_text=get_text("search_quotation"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            on_change=self.filter_quotations,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_quotations(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )
        
        # สร้างส่วนหัวตาราง
        table_header = self._create_table_header()
        
        # ส่วนแสดงแถวตาราง
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # คอนเทนเนอร์ตาราง
        table_container = ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                self.table_rows,
            ], spacing=0),
            margin=ft.margin.only(left=20, right=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12, bottom_left=12, bottom_right=12),
            border=ft.border.all(1, ft.Colors.GREY_200),
            expand=True,
        )
        
        # ส่วนแบ่งหน้า
        self.pagination_container = ft.Container(
            padding=ft.padding.symmetric(vertical=12, horizontal=20),
            bgcolor="#F5F7FA",
        )
        
        # ตัวโหลด
        self.loading_indicator = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=4),
                ft.Container(height=16),
                ft.Text(get_text("loading"), size=14, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=Alignment.CENTER,
            padding=ft.padding.all(40),
            visible=False,
        )
        
        # สถานะไม่มีข้อมูล
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.REQUEST_QUOTE, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=16),
                ft.Text(get_text("no_quotations_found"), size=18, weight=ft.FontWeight.W_500, color="#64748B"),
                ft.Text(get_text("click_add_to_register"), size=13, color="#94A3B8"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    content=ft.Text(get_text("new_quotation"), size=14),
                    on_click=lambda e: self.navigate("quotation_create"),
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=Alignment.CENTER,
            padding=ft.padding.all(60),
            visible=False,
        )
        
        # ส่วนเนื้อหาหลัก
        content_area = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([self.search_field, refresh_button], spacing=10),
                    margin=ft.margin.only(bottom=16),
                ),
                table_container,
                self.pagination_container,
                self.loading_indicator,
                self.empty_state,
            ], expand=True),
            expand=True,
            padding=ft.padding.all(24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        self.load_quotations()
        
        return main_content
    
    def _create_table_header(self):
        """สร้างส่วนหัวตาราง"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(get_text("quotation_no"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("customer_name"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("plate_number"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("total"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text("status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("date"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text("actions"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=180,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=14, horizontal=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _create_table_row(self, quote: Dict, index: int):
        """สร้างแถวในตาราง"""
        quote_id = quote.get("id")
        customer_name = quote.get("customer_name", "-")
        plate_number = quote.get("plate_number", "-")
        total_price = quote.get("total_price", 0)
        status = quote.get("status", "draft")
        created_at = quote.get("created_at", "").split()[0] if quote.get("created_at") else "-"
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        status_colors = {
            "draft": "#FF9800",
            "approved": "#4CAF50",
            "rejected": "#F44336"
        }
        status_texts = {
            "draft": get_text("draft"),
            "approved": get_text("approved"),
            "rejected": get_text("rejected")
        }
        
        # Check if status is approved - no dropdown icon, not clickable
        is_approved = status == "approved"
        
        if is_approved:
            # Simple badge without dropdown arrow (not clickable)
            status_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                    ft.Text(status_texts.get(status, status), size=11, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=status_colors.get(status, "#607D8B"),
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                # No on_click for approved status
            )
        else:
            # Clickable badge with dropdown arrow for draft/rejected
            status_badge = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.WHITE),
                    ft.Text(status_texts.get(status, status), size=11, color=ft.Colors.WHITE),
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=ft.Colors.WHITE),
                ], spacing=4),
                bgcolor=status_colors.get(status, "#607D8B"),
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                on_click=lambda e, qid=quote_id, cur_status=status: self.show_update_status_dialog(qid, cur_status),
            )
        
        view_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("view"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, qid=quote_id: self.show_quotation_detail(qid),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        print_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("print"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, qid=quote_id: self.print_quotation(qid),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        # Delete button - disabled for approved status
        if is_approved:
            delete_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.GREY_400),
                    ft.Text(get_text("delete"), size=12, color=ft.Colors.GREY_400),
                ], spacing=4),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=6,
                tooltip=get_text("cannot_delete_approved_quotation"),
            )
        else:
            delete_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
                    ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
                ], spacing=4),
                on_click=lambda e, qid=quote_id: self.delete_quotation(qid),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=6,
            )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(f"QT-{quote_id:04d}", size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    width=100,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(customer_name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1),
                    width=150,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(plate_number, size=12, color="#64748B", max_lines=1),
                    width=120,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(f"{int(total_price):,} KIP", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREEN_700),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=status_badge,
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(created_at, size=12, color="#64748B"),
                    width=110,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Row([view_btn, print_btn, delete_btn], spacing=4),
                    width=180,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=10),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    def load_quotations(self):
        """โหลดข้อมูลใบเสนอราคาจาก API"""
        self.loading_indicator.visible = True
        self.empty_state.visible = False
        self.table_rows.controls.clear()
        self.page.update()
        
        try:
            quotations = self.client.get_quotations(job_order_id=self.job_order_id)
            self.quotations = quotations
            self.filtered_quotations = quotations.copy()
            self.display_quotations()
        except Exception as ex:
            print(f"Error loading quotations: {ex}")
            self.loading_indicator.visible = False
            self.page.update()
    
    def filter_quotations(self, e):
        """กรองใบเสนอราคาตามคำค้นหา"""
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        self.current_page = 1
        
        if not keyword:
            self.filtered_quotations = self.quotations.copy()
        else:
            self.filtered_quotations = [
                q for q in self.quotations
                if keyword in f"QT-{q.get('id', 0):04d}".lower()
                or keyword in q.get("customer_name", "").lower()
                or keyword in q.get("plate_number", "").lower()
                or keyword in q.get("job_no", "").lower()
            ]
        
        self.display_quotations()
    
    def display_quotations(self):
        """แสดงใบเสนอราคาพร้อมการแบ่งหน้า"""
        self.table_rows.controls.clear()
        
        total_items = len(self.filtered_quotations)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_quotations[start_idx:end_idx]
        
        if page_items and len(page_items) > 0:
            self.loading_indicator.visible = False
            self.empty_state.visible = False
            for i, quote in enumerate(page_items):
                self.table_rows.controls.append(self._create_table_row(quote, start_idx + i))
        else:
            self.loading_indicator.visible = False
            self.empty_state.visible = True
        
        self.update_pagination_controls()
        self.page.update()
    
    def update_pagination_controls(self):
        """อัปเดตตัวควบคุมการแบ่งหน้า"""
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_quotations)} {get_text('of')} {len(self.quotations)} {get_text('results')}",
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
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_quotations()
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_quotations()
    
    def show_quotation_detail(self, quotation_id: int):
        """แสดงรายละเอียดใบเสนอราคาใน dialog"""
        self.loading_indicator.visible = True
        self.page.update()
        
        try:
            quotation = self.client.get_quotation(quotation_id)
            self.loading_indicator.visible = False
            
            if quotation:
                def on_print(qid):
                    self.print_quotation(qid)
                
                dialog = show_quotation_detail_dialog(
                    quotation,
                    self.primary_color,
                    on_print,
                    self._close_dialog
                )
                self._open_dialog(dialog)
            else:
                self.show_snack_bar(get_text("error_loading_quotation"), is_error=True)
        except Exception as ex:
            self.loading_indicator.visible = False
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
            self.page.update()
    
    def show_update_status_dialog(self, quotation_id: int, current_status: str):
        """แสดง dialog สำหรับอัปเดตสถานะใบเสนอราคา"""
        
        # ไม่อนุญาตให้เปลี่ยนสถานะถ้าอนุมัติแล้ว
        if current_status == "approved":
            self.show_snack_bar(get_text("cannot_change_approved_quotation"), is_error=True)
            return
        
        def on_update(qid, new_status):
            try:
                # อัปเดตสถานะใบเสนอราคาเท่านั้น
                # Backend จะอัปเดตสถานะ Job Order เป็น 'approved' ให้อัตโนมัติ
                self.client.update_quotation_status(qid, new_status)
                
                self._close_dialog()
                self.load_quotations()
                self.show_snack_bar(f"✅ {get_text('status_updated_to')} {get_text(new_status)}", is_error=False)
                
                # ถ้าใบเสนอราคาถูกอนุมัติ ให้ถามว่าจะสร้างใบสั่งซ่อมเลยหรือไม่
                if new_status == "approved":
                    try:
                        quotation = self.client.get_quotation(qid)
                        if quotation and quotation.get('job_order_id'):
                            def go_to_repair(e):
                                dialog.open = False
                                self.navigate("repair_create", job_order_id=quotation.get('job_order_id'))
                            
                            dialog = ft.AlertDialog(
                                modal=True,
                                title=ft.Text(get_text("quotation_approved"), size=16, weight=ft.FontWeight.BOLD),
                                content=ft.Text(get_text("create_repair_order_now")),
                                actions=[
                                    ft.TextButton(get_text("later"), on_click=lambda e: setattr(dialog, 'open', False)),
                                    ft.ElevatedButton(get_text("go_to_repair"), on_click=go_to_repair, style=ft.ButtonStyle(bgcolor=self.primary_color)),
                                ],
                                actions_alignment=ft.MainAxisAlignment.END,
                            )
                            self.page.overlay.append(dialog)
                            dialog.open = True
                            self.page.update()
                    except:
                        pass
                        
            except Exception as ex:
                print(f"DEBUG: Error in update: {ex}")
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = show_update_status_dialog(
            quotation_id,
            current_status,
            self.primary_color,
            on_update,
            self._close_dialog
        )
        self._open_dialog(dialog)
    
    def delete_quotation(self, quotation_id: int):
        """ลบใบเสนอราคาพร้อมยืนยัน"""
        quote = next((q for q in self.quotations if q.get("id") == quotation_id), None)
        quote_name = f"QT-{quotation_id:04d}" if quote else get_text("this_quotation")
        
        # ห้ามลบใบเสนอราคาที่อนุมัติแล้ว
        if quote and quote.get("status") == "approved":
            self.show_snack_bar(get_text("cannot_delete_approved_quotation"), is_error=True)
            return
        
        def on_confirm():
            try:
                self.client.delete_quotation(quotation_id)
                self._close_dialog()
                self.load_quotations()
                self.show_snack_bar(f"✅ {get_text('delete_success')}", is_error=False)
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
        
        dialog = show_delete_quotation_dialog(
            quote_name,
            on_confirm,
            self._close_dialog
        )
        self._open_dialog(dialog)
    
    def print_quotation(self, quotation_id: int):
        """พิมพ์ใบเสนอราคาโดยใช้ browser print dialog"""
        try:
            self.show_snack_bar(get_text("preparing_print"), is_error=False)
            
            def generate_and_print():
                quotation = self.client.get_quotation(quotation_id)
                if quotation:
                    html_content = self._generate_print_html(quotation)
                    
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                        f.write(html_content)
                        temp_path = f.name
                    
                    time.sleep(0.5)
                    webbrowser.open(f'file://{temp_path}')
                    
                    def cleanup():
                        time.sleep(30)
                        try:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        except:
                            pass
                    
                    threading.Thread(target=cleanup, daemon=True).start()
                else:
                    self.show_snack_bar(get_text("error_loading_quotation"), is_error=True)
            
            threading.Thread(target=generate_and_print, daemon=True).start()
            
        except Exception as ex:
            print(f"Error printing: {ex}")
            self.show_snack_bar(f"{get_text('error')}: {str(ex)}", is_error=True)
    
    def _generate_print_html(self, quotation: Dict) -> str:
        """สร้าง HTML สำหรับพิมพ์ใบเสนอราคา"""
        
        items = quotation.get("items", [])
        shop_info = {}
        try:
            shop_info = self.client.get_shop()
        except:
            pass
        
        shop_name = shop_info.get('name', 'ຮ້ານຈີ້ ແອັບ ພີ ອໍໂຕ ແມັກຊິ້ງ')
        shop_address = shop_info.get('address', 'ນະຄອນຫຼວງວຽງຈັນ')
        shop_phone = shop_info.get('phone', '020 92431434')
        
        quotation_no = f"QT-{quotation.get('id', 0):04d}"
        created_date = quotation.get("created_at", "")
        if created_date:
            try:
                dt = datetime.strptime(str(created_date), "%Y-%m-%d %H:%M:%S")
                created_date = dt.strftime("%d/%m/%Y")
            except:
                created_date = str(created_date)[:10]
        else:
            created_date = datetime.now().strftime("%d/%m/%Y")
        
        status = quotation.get("status", "draft")
        if status == "draft":
            status_text = "ຖ້າສະເໜີ"
        elif status == "approved":
            status_text = "ອະນຸມັດແລ້ວ"
        elif status == "rejected":
            status_text = "ປະຕິເສດ"
        else:
            status_text = status
        
        # คำนวณยอดรวม
        subtotal = 0
        total_discount = 0
        for item in items:
            subtotal += item.get("total", 0)
            total_discount += item.get("discount_amount", 0)
        grand_total = subtotal - total_discount
        
        # สร้าง HTML ตารางรายการ
        items_html = ""
        for idx, item in enumerate(items, 1):
            name = item.get("name", "-")
            qty = item.get("qty", 1)
            unit_price = item.get("unit_price", 0)
            discount = item.get("discount_amount", 0)
            total = item.get("total", qty * unit_price)
            
            items_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{idx}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{name}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{qty}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{int(unit_price):,}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{int(discount):,}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{int(total):,}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>ໃບສະເໜີລາຄາ {quotation_no}</title>
            <style>
                @media print {{
                    body {{ margin: 0; padding: 15px; }}
                }}
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Noto Sans', 'DejaVu Sans', 'Segoe UI', Arial, sans-serif;
                    font-size: 13px;
                    background: white;
                    padding: 20px;
                }}
                .quotation {{ max-width: 1000px; margin: 0 auto; }}
                .header {{ text-align: center; padding: 15px; border-bottom: 2px solid #1565C0; margin-bottom: 20px; }}
                .shop-name {{ font-size: 20px; font-weight: bold; color: #1565C0; }}
                .shop-address {{ font-size: 11px; color: #666; margin-top: 5px; }}
                .shop-phone {{ font-size: 12px; font-weight: bold; margin-top: 3px; }}
                .title {{ font-size: 16px; font-weight: bold; margin-top: 10px; }}
                .info-row {{ display: flex; margin-bottom: 8px; padding: 4px 0; border-bottom: 1px dotted #ddd; }}
                .info-label {{ font-weight: bold; width: 130px; }}
                .info-value {{ flex: 1; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #f5f5f5; padding: 10px 8px; text-align: left; font-size: 12px; font-weight: bold; border-bottom: 2px solid #ddd; }}
                th:first-child {{ width: 40px; text-align: center; }}
                th:nth-child(2) {{ text-align: left; }}
                th:nth-child(3) {{ width: 60px; text-align: center; }}
                th:nth-child(4) {{ width: 100px; text-align: right; }}
                th:nth-child(5) {{ width: 100px; text-align: right; }}
                th:nth-child(6) {{ width: 120px; text-align: right; }}
                td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                .total-section {{ margin-top: 20px; text-align: right; border-top: 2px solid #ddd; padding-top: 15px; }}
                .total-line {{ margin-bottom: 5px; }}
                .total-label {{ display: inline-block; width: 150px; font-weight: bold; }}
                .total-amount {{ display: inline-block; width: 150px; text-align: right; }}
                .grand-total {{ font-size: 16px; font-weight: bold; color: #1565C0; margin-top: 8px; padding-top: 8px; border-top: 1px solid #ddd; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 10px; color: #666; }}
                .stamp {{ margin-top: 30px; display: flex; justify-content: space-between; }}
                .signature {{ border-top: 1px solid #000; width: 180px; padding-top: 5px; text-align: center; font-size: 11px; }}
            </style>
        </head>
        <body>
            <div class="quotation">
                <div class="header">
                    <div class="shop-name">{shop_name}</div>
                    <div class="shop-address">{shop_address}</div>
                    <div class="shop-phone">ເບີໂທ: {shop_phone}</div>
                    <div class="title">ໃບສະເໜີລາຄາ</div>
                </div>
                
                <div class="info-row">
                    <div class="info-label">ເລກທີ່ໃບສະເໜີ:</div>
                    <div class="info-value">{quotation_no}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">ວັນທີ:</div>
                    <div class="info-value">{created_date}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">ສະຖານະ:</div>
                    <div class="info-value">{status_text}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">ຊື່ລູກຄ້າ:</div>
                    <div class="info-value">{quotation.get('customer_name', '-')}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">ເບີໂທ:</div>
                    <div class="info-value">{quotation.get('customer_phone', '-')}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">ທະບຽນລົດ:</div>
                    <div class="info-value">{quotation.get('plate_number', '-')}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">ຍີ່ຫໍ້/ລຸ້ນ:</div>
                    <div class="info-value">{quotation.get('brand', '')} {quotation.get('model', '')}</div>
                </div>
                <div class="info-row">
                    <div class="info-label">ເລກທີ່ໃບຮັບລົດ:</div>
                    <div class="info-value">{quotation.get('job_no', '-')}</div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>ລຳດັບ</th>
                            <th>ລາຍການ</th>
                            <th>ຈຳນວນ</th>
                            <th>ລາຄາ</th>
                            <th>ສ່ວນຫຼຸດ</th>
                            <th>ລວມ</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html if items_html else '<tr><td colspan="6" style="text-align: center; padding: 40px;">ບໍ່ມີລາຍການ</td></tr>'}
                    </tbody>
                </table>
                
                <div class="total-section">
                    <div class="total-line">
                        <span class="total-label">ລວມຍ່ອຍ:</span>
                        <span class="total-amount">{int(subtotal):,} KIP</span>
                    </div>
                    <div class="total-line">
                        <span class="total-label">ສ່ວນຫຼຸດ:</span>
                        <span class="total-amount">{int(total_discount):,} KIP</span>
                    </div>
                    <div class="grand-total">
                        <span class="total-label">ລວມທັງໝົດ:</span>
                        <span class="total-amount">{int(grand_total):,} KIP</span>
                    </div>
                </div>
                
                <div class="stamp">
                    <div class="signature">ລາຍເຊັນລູກຄ້າ</div>
                    <div class="signature">ລາຍເຊັນຮ້ານ</div>
                </div>
                
                <div class="footer">
                    <p>ຂອບໃຈທີ່ໄວ້ໃຈບໍລິການຂອງພວກເຮົາ</p>
                    <p>{shop_phone} | {shop_address}</p>
                    <p>ພິມເມື່ອ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </div>
            <script>
                window.onload = function() {{
                    setTimeout(function() {{
                        window.print();
                    }}, 500);
                }}
            </script>
        </body>
        </html>
        """
        return html
    
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
    
    def _close_dialog(self, dialog=None):
        try:
            if dialog:
                dialog.open = False
            elif self.current_dialog:
                self.current_dialog.open = False
            self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, size=13),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=3000,
        )
        self.page.update()