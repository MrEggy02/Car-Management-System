# pages/purchase/purchase_order_detail.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import asyncio
import os

from i18n import get_text


class PurchaseOrderDetailContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, po_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.po_id = po_id
        self.po_data = None
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.warning_color = "#F59E0B"
        self.current_snackbar = None
        self.content_area = None
        
    def build(self):
        header = self._build_header()
        
        self.content_area = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Container(height=20),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F8FAFC",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area], expand=True),
            expand=True,
            bgcolor="#F1F5F9",
        )
        
        self.load_purchase_order()
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
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
                                get_text("purchase_order_detail"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
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
    
    def load_purchase_order(self):
        try:
            if self.po_id:
                self.po_data = self.client.get_purchase_order(self.po_id)
                print(f"DEBUG: PO detail loaded: {self.po_data}")
                self._refresh_content()
        except Exception as ex:
            print(f"Error loading purchase order detail: {ex}")
            import traceback
            traceback.print_exc()
            self._show_error(str(ex))
    
    def _show_error(self, message):
        self.content_area.content = ft.Column([
            ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED_400),
            ft.Container(height=16),
            ft.Text(get_text("error_loading_data"), size=16, color="#64748B"),
            ft.Container(height=8),
            ft.Text(message, size=13, color="#94A3B8"),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
        self.page.update()
    
    def _refresh_content(self):
        if not self.po_data:
            self.content_area.content = ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.RED_400),
                ft.Container(height=16),
                ft.Text(get_text("error_loading_data"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16)
            self.page.update()
            return
        
        new_content = self._build_content()
        self.content_area.content = ft.Column([new_content], scroll=ft.ScrollMode.AUTO, expand=True)
        self.page.update()
    
    def _create_info_row(self, label, value):
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=12, color="#64748B", width=100),
                ft.Text(value, size=13, color="#1E293B", weight=ft.FontWeight.W_500, expand=True),
            ], spacing=12),
            padding=ft.Padding(left=0, right=0, top=5, bottom=5),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)),
        )
    
    def _build_content(self):
        data = self.po_data
        
        po_no = data.get('po_no', '-')
        supplier_name = data.get('supplier_name', '-')
        order_date = data.get('order_date', '')
        if order_date:
            order_date = order_date[:16] if len(order_date) > 16 else order_date
        else:
            order_date = '-'
        status = data.get('status', 'pending')
        created_by = data.get('created_by_name', '-')
        received_by = data.get('received_by_name', '-')
        received_at = data.get('received_at', '')
        if received_at:
            received_at = received_at[:16] if len(received_at) > 16 else received_at
        else:
            received_at = '-'
        items = data.get('items', [])
        
        # ຄຳນວນຈຳນວນລາຍການທັງໝົດ
        total_items = sum(item.get('qty', 0) for item in items)
        
        status_colors = {
            "ordering": "#2196F3",
            "partial": "#FF9800",
            "completed": "#4CAF50",
            "cancelled": "#F44336"
        }
        status_texts = {
            "ordering": get_text("ordering") if get_text("ordering") else "Ordering",
            "partial": get_text("partial") if get_text("partial") else "Partial",
            "completed": get_text("completed") if get_text("completed") else "Completed",
            "cancelled": get_text("cancelled") if get_text("cancelled") else "Cancelled"
        }
        
        status_badge = ft.Container(
            content=ft.Text(status_texts.get(status, status), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            bgcolor=status_colors.get(status, "#607D8B"),
            border_radius=20,
            padding=ft.Padding(left=14, right=14, top=5, bottom=5),
        )
        
        # ========== LEFT COLUMN ==========
        # PO Info Card
        po_info_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LOCAL_SHIPPING, size=18, color=self.primary_color),
                    ft.Text(get_text("po_info"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Container(expand=True),
                    status_badge,
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=4),
                self._create_info_row(get_text("po_no"), po_no),
                self._create_info_row(get_text("supplier"), supplier_name),
                self._create_info_row(get_text("order_date"), order_date),
                self._create_info_row(get_text("created_by"), created_by),
                self._create_info_row(get_text("received_by"), received_by if received_by != '-' else '-'),
                self._create_info_row(get_text("received_date"), received_at),
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.Margin(left=0, right=0, top=0, bottom=12),
        )
        
        # Total Items Card - ປ່ຽນຈາກ total_amount ເປັນ ຈຳນວນລາຍການທັງໝົດ
        total_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INVENTORY, size=18, color=self.primary_color),
                    ft.Text(get_text("total_amount"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(f"{total_items} {get_text('items')}", size=20, weight=ft.FontWeight.W_800, color=self.primary_color),
                        padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                        border_radius=16,
                    ),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        left_column = ft.Container(
            content=ft.Column([po_info_card, total_card], spacing=0),
            width=380,
            expand=True,
        )
        
        # ========== RIGHT COLUMN ==========
        # Items Card - ເອົາຄໍລຳລາຄາອອກ
        items_list = ft.Column(spacing=0)
        
        if items and len(items) > 0:
            for idx, item in enumerate(items):
                part_name = item.get('part_name', '-')
                qty = item.get('qty', 0)
                received_qty = item.get('received_qty', 0)
                
                border_bottom = ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)) if idx < len(items) - 1 else None
                
                if received_qty >= qty:
                    received_color = self.success_color
                    received_text = get_text("completed") if get_text("completed") else "Completed"
                elif received_qty > 0:
                    received_color = self.warning_color
                    received_text = get_text("partial") if get_text("partial") else "Partial"
                else:
                    received_color = "#64748B"
                    received_text = get_text("ordering") if get_text("ordering") else "Ordering"
                
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Text(f"{idx+1}", size=12, color="#64748B", width=30),
                        ft.Text(part_name, size=12, color="#1E293B", expand=True, max_lines=2),
                        ft.Text(f"x{qty}", size=12, color="#64748B", width=60, text_align=ft.TextAlign.CENTER),
                        ft.Container(
                            content=ft.Text(f"{received_qty}/{qty}", size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                            bgcolor=received_color,
                            border_radius=12,
                            padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                            width=80,
                            alignment=ft.Alignment(0, 0),
                        ),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=0, right=0, top=6, bottom=6),
                    border=border_bottom,
                )
                items_list.controls.append(item_row)
            
            # ສະແດງຈຳນວນລາຍການທັງໝົດ ແທນຍອດເງິນ
            total_row = ft.Container(
                content=ft.Row([
                    ft.Container(expand=True),
                    ft.Text(get_text("total_qty") + ":", size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Text(f"{total_items} {get_text('items')}", size=14, weight=ft.FontWeight.W_700, color=self.primary_color),
                ], spacing=12),
                padding=ft.Padding(left=0, right=0, top=8, bottom=8),
                bgcolor="#F8FAFC",
                border_radius=8,
                margin=ft.Margin(left=0, right=0, top=6, bottom=0),
            )
            items_list.controls.append(total_row)
        else:
            items_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=32, color="#CBD5E1"),
                        ft.Text(get_text("no_items"), size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.Padding(left=30, right=30, top=30, bottom=30),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        # ຫົວຂໍ້ຕາຕະລາງ - ບໍ່ມີຄໍລຳ price ແລະ total
        items_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LIST_ALT, size=18, color=self.primary_color),
                    ft.Text(get_text("items"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=4),
                ft.Row([
                    ft.Text("#", size=10, weight=ft.FontWeight.W_600, color="#64748B", width=30),
                    ft.Text(get_text("part_name"), size=10, weight=ft.FontWeight.W_600, color="#64748B", expand=True),
                    ft.Text(get_text("qty"), size=10, weight=ft.FontWeight.W_600, color="#64748B", width=60, text_align=ft.TextAlign.CENTER),
                    ft.Text(get_text("received"), size=10, weight=ft.FontWeight.W_600, color="#64748B", width=80, text_align=ft.TextAlign.CENTER),
                ], spacing=6),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                items_list,
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        right_column = ft.Container(
            content=ft.Column([items_card], spacing=0),
            width=450,
            expand=True,
        )
        
        # ========== TWO COLUMN LAYOUT ==========
        two_columns = ft.Row(
            [left_column, ft.VerticalDivider(width=1, color=ft.Colors.GREY_300), right_column],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        main_content = ft.Container(
            content=two_columns,
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            expand=True,
        )
        
        # Action Buttons
        back_btn = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ARROW_BACK, size=18, color=self.primary_color),
                ft.Text(get_text("back_to_list"), size=14, color=self.primary_color, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=lambda e: self.navigate("purchase_order_list"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, self.primary_color),
                padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            ),
        )
        
        print_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("print") if get_text("print") else "Print", size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=self.print_purchase_order,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            ),
        )
        
        action_row = ft.Row([back_btn, print_btn], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
        
        return ft.Column([
            main_content,
            ft.Container(height=16),
            action_row,
        ], spacing=0)
    
    def print_purchase_order(self, e):
        self.show_snack_bar(get_text("loading"), "info")
        try:
            pdf_bytes = self.client.get_purchase_order_pdf(self.po_id)
            if not pdf_bytes:
                self.show_snack_bar(get_text("pdf_export_failed"), "error")
                return
                
            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            po_no = self.po_data.get('po_no', f"PO-{self.po_id}")
            pdf_path = os.path.join(output_dir, f"purchase_order_{po_no}.pdf")
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
                
            os.startfile(pdf_path)
            self.show_snack_bar(get_text("pdf_export_success"), "success")
            
        except Exception as ex:
            print(f"Error printing purchase order PDF: {ex}")
            self.show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", "error")
    
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