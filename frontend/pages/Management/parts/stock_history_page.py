# Management/parts/stock_history_page.py (เวอร์ชันที่แก้ไขสมบูรณ์)
import flet as ft
import sys
import os
import asyncio
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import get_text


class StockHistoryPage:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.movements = []
        self.is_loading = False
        self.count_text = None  # เก็บ reference ของ Text ที่แสดงจำนวน

    def build(self):
        # สร้าง Text สำหรับแสดงจำนวน
        self.count_text = ft.Text(
            f"{get_text('records') or 'ລາຍການ'} 0",
            size=12,
            color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
        )

        # Header with back button
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=ft.Colors.WHITE,
                        icon_size=24,
                        on_click=lambda e: self.navigate("parts"),
                        tooltip=get_text("back") or "ກັບຄືນ",
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("stock_history") or "ປະຫວັດການເຄື່ອນໄຫວສາງ",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            self.count_text,  # ใช้ reference ที่เก็บไว้
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        icon_color=ft.Colors.WHITE,
                        icon_size=22,
                        on_click=self.refresh_data,
                        tooltip=get_text("refresh") or "ຣີເຟຣດ",
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, right=24, top=12, bottom=12),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )

        # Table Header
        table_header = self._create_table_header()

        # Table rows container
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

        # Table Container
        table_container = ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                self.table_rows,
            ], spacing=0),
            margin=ft.Margin(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.GREY_200),
                right=ft.BorderSide(1, ft.Colors.GREY_200),
                bottom=ft.BorderSide(1, ft.Colors.GREY_200),
                left=ft.BorderSide(1, ft.Colors.GREY_200),
            ),
            expand=True,
        )

        # Loading overlay
        self.loading_overlay = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=40, height=40),
                ft.Container(height=10),
                ft.Text(get_text("loading"), size=14, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
            visible=False,
        )

        # Main content
        main_content = ft.Container(
            content=ft.Stack([
                ft.Column([
                    header,
                    table_container,
                ], expand=True, spacing=0),
                self.loading_overlay,
            ], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )

        # Load data
        self.page.run_task(self._load_data)

        return main_content

    def _create_table_header(self):
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=40, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text("ອາໄຫຼ່", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=150, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text("ປະເພດ", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=60, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text("ຈຳນວນ", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=70, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text("ອ້າງອີງ", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text("ວັນທີ", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=160, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=12, bottom=12),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )

    def _create_table_row(self, mov, index):
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        mov_id = mov.get('id')
        part_name = mov.get('part_name', '-')
        mov_type = mov.get('type', '')
        qty = mov.get('qty', 0)
        ref_type = mov.get('ref_type', '')
        ref_id = mov.get('ref_id')
        date_str = mov.get('date', '')
        
        if date_str:
            try:
                dt = datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%d/%m/%Y %H:%M")
            except:
                pass
        else:
            date_str = '-'

        type_color = "#10B981" if mov_type == "IN" else "#EF4444"
        type_icon = ft.Icons.ARROW_UPWARD if mov_type == "IN" else ft.Icons.ARROW_DOWNWARD
        ref_display = f"{ref_type.upper()}-{ref_id}" if ref_id else "-"

        row = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(str(mov_id), size=12, color="#64748B"), width=40, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(part_name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1), width=150, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(type_icon, size=14, color=type_color),
                        ft.Text(mov_type, size=12, color=type_color, weight=ft.FontWeight.W_600),
                    ], spacing=4),
                    width=60,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(content=ft.Text(str(qty), size=12, color="#1E293B"), width=70, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(ref_display, size=12, color="#64748B"), width=100, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
                ft.Container(content=ft.Text(date_str, size=12, color="#64748B"), width=160, alignment=ft.Alignment(-1, 0), padding=ft.Padding(left=8, right=0, top=0, bottom=0)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=8, right=8, top=10, bottom=10),
            bgcolor=row_bg,
        )
        return ft.Column([row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0)

    def _create_empty_state(self):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.HISTORY, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_data"), size=16, color=ft.Colors.GREY_500),
                ft.Text("ບໍ່ມີຂໍ້ມູນການເຄື່ອນໄຫວ", size=13, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=40, right=40, top=60, bottom=60),
            expand=True,
        )

    def display_movements(self):
        """อัปเดตตารางและตัวเลขใน header"""
        self.table_rows.controls.clear()
        
        if not self.movements:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            for i, mov in enumerate(self.movements):
                row = self._create_table_row(mov, i)
                self.table_rows.controls.append(row)
        
        # อัปเดตจำนวนใน header
        self.count_text.value = f"{get_text('records') or 'ລາຍການ'} {len(self.movements)}"
        self.page.update()

    async def _load_data(self):
        self.loading_overlay.visible = True
        self.page.update()
        try:
            self.movements = await asyncio.to_thread(self.client.get_stock_movements, limit=200)
            print(f"DEBUG: Loaded {len(self.movements)} movements")
        except Exception as e:
            print(f"DEBUG: Error loading stock history: {e}")
            self.movements = []
        finally:
            self.loading_overlay.visible = False
            self.display_movements()

    def refresh_data(self, e=None):
        self.page.run_task(self._load_data)