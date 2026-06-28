# pages/invoices/delivery_note_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
import os

from i18n import get_text


class DeliveryNoteListContent:
    """ໜ້າລາຍຊື່ໃບສົ່ງມອບລົດ — ສະແດງສະເພາະ invoices ທີ່ paid ແລ້ວ"""

    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.invoices = []
        self.filtered_invoices = []
        self.current_page_num = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.search_field = None
        self.table_rows = None
        self.pagination_container = None
        self.current_dialog = None

    def build(self):
        header = self._build_header()
        search_bar = self._build_search_bar()
        table = self._build_table()
        self.pagination_container = ft.Container(
            padding=ft.Padding(left=20, right=20, top=12, bottom=12)
        )

        content_area = ft.Container(
            content=ft.Column(
                [search_bar, table, self.pagination_container],
                expand=True,
            ),
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F5F7FA",
        )

        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )

        self.load_invoices()
        return main_content

    # ─────────────────────────────────────────────────────────────
    # Header
    # ─────────────────────────────────────────────────────────────
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.LOCAL_SHIPPING,
                                        size=22,
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.Text(
                                        "ໃບສົ່ງມອບລົດ",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Text(
                                "ລາຍຊື່ໃບສົ່ງມອບລົດທີ່ຊຳລະເງິນສຳເລັດແລ້ວ",
                                size=13,
                                color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=24, right=24, top=16, bottom=16),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )

    # ─────────────────────────────────────────────────────────────
    # Search bar
    # ─────────────────────────────────────────────────────────────
    def _build_search_bar(self):
        self.search_field = ft.TextField(
            hint_text="ຄົ້ນຫາດ້ວຍເລກໃບບິນ, ຊື່ລູກຄ້າ ຫຼື ທະບຽນລົດ...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        self.search_field.on_change = lambda e: self.apply_filters()

        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_invoices(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )

        return ft.Container(
            content=ft.Row([self.search_field, refresh_button], spacing=10),
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
        )

    # ─────────────────────────────────────────────────────────────
    # Table
    # ─────────────────────────────────────────────────────────────
    def _build_table(self):
        table_header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            get_text("invoice_no"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            get_text("job_number"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            get_text("customer_name"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=150,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            get_text("plate_number"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            "ຍີ່ຫໍ້ / ລຸ້ນ",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=150,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            "ວັນທີຊຳລະ",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=120,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            get_text("actions"),
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600,
                        ),
                        width=160,
                        alignment=ft.Alignment(0, 0),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )

        self.table_rows = ft.Column(
            spacing=0, scroll=ft.ScrollMode.AUTO, expand=True
        )

        return ft.Container(
            content=ft.Column(
                [
                    table_header,
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    self.table_rows,
                ],
                spacing=0,
            ),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
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

    # ─────────────────────────────────────────────────────────────
    # Data loading
    # ─────────────────────────────────────────────────────────────
    def load_invoices(self):
        self.table_rows.controls.clear()
        self.page.update()

        try:
            all_invoices = self.client.get_invoices()
            # Filter only paid invoices
            self.invoices = [
                inv for inv in all_invoices if inv.get("payment_status") == "paid"
            ]
            self.filtered_invoices = self.invoices.copy()
            self.display_invoices()
        except Exception as ex:
            print(f"Error loading invoices: {ex}")
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.ERROR_OUTLINE,
                                size=48,
                                color=ft.Colors.RED_400,
                            ),
                            ft.Text(
                                f"Error: {str(ex)}", size=14, color=ft.Colors.RED_600
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=40, right=40, top=40, bottom=40),
                )
            )
            self.page.update()

    def apply_filters(self):
        keyword = (
            self.search_field.value.lower() if self.search_field.value else ""
        )
        if keyword:
            self.filtered_invoices = [
                inv
                for inv in self.invoices
                if keyword in f"INV-{inv.get('id', 0):04d}".lower()
                or keyword in inv.get("customer_name", "").lower()
                or keyword in inv.get("plate_number", "").lower()
                or keyword in inv.get("job_no", "").lower()
            ]
        else:
            self.filtered_invoices = self.invoices.copy()
        self.current_page_num = 1
        self.display_invoices()

    def display_invoices(self):
        self.table_rows.controls.clear()

        total_items = len(self.filtered_invoices)
        self.total_pages = max(
            1, (total_items + self.items_per_page - 1) // self.items_per_page
        )
        if self.current_page_num > self.total_pages:
            self.current_page_num = self.total_pages
        if self.current_page_num < 1:
            self.current_page_num = 1

        start_idx = (self.current_page_num - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = self.filtered_invoices[start_idx:end_idx]

        if page_items:
            for i, invoice in enumerate(page_items):
                self.table_rows.controls.append(
                    self._create_row(invoice, start_idx + i)
                )
        else:
            self.table_rows.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.LOCAL_SHIPPING,
                                size=64,
                                color=ft.Colors.GREY_300,
                            ),
                            ft.Text(
                                "ຍັງບໍ່ມີໃບສົ່ງມອບລົດ",
                                size=16,
                                color=ft.Colors.GREY_500,
                            ),
                            ft.Text(
                                "ໃບສົ່ງມອບຈະປາກົດຂຶ້ນເມື່ອໃບບິນຖືກຊຳລະສຳເລັດ",
                                size=13,
                                color=ft.Colors.GREY_400,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=ft.Padding(left=40, right=40, top=60, bottom=60),
                    alignment=ft.Alignment(0, 0),
                )
            )

        self._update_pagination()
        self.page.update()

    # ─────────────────────────────────────────────────────────────
    # Row builder
    # ─────────────────────────────────────────────────────────────
    def _create_row(self, invoice: Dict, index: int):
        invoice_id = invoice.get("id")
        invoice_no = f"INV-{invoice_id:04d}"
        job_no = invoice.get("job_no", "-")
        customer_name = invoice.get("customer_name", "-")
        plate_number = invoice.get("plate_number", "-")
        brand = invoice.get("brand", "")
        model = invoice.get("model", "")
        brand_model = f"{brand} {model}".strip() or "-"
        paid_date = invoice.get("paid_date", "")
        if paid_date:
            paid_date = paid_date[:10]
        else:
            paid_date = "-"

        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE

        print_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.LOCAL_SHIPPING, size=16, color=self.success_color
                    ),
                    ft.Text("ພິມໃບສົ່ງມອບ", size=12, color=self.success_color),
                ],
                spacing=4,
            ),
            on_click=lambda e, iid=invoice_id: self.print_delivery_note(iid),
            padding=ft.Padding(left=8, right=8, top=5, bottom=5),
            border_radius=6,
            border=ft.Border(
                top=ft.BorderSide(1, self.success_color),
                right=ft.BorderSide(1, self.success_color),
                bottom=ft.BorderSide(1, self.success_color),
                left=ft.BorderSide(1, self.success_color),
            ),
            ink=True,
        )

        view_btn = ft.Container(
            content=ft.Icon(
                ft.Icons.RECEIPT_OUTLINED, size=18, color=ft.Colors.GREY_500
            ),
            tooltip="ດູໃບບິນ",
            on_click=lambda e, iid=invoice_id: self.navigate(
                "invoice_list"
            ),
            padding=ft.Padding(left=6, right=6, top=4, bottom=4),
            border_radius=6,
            ink=True,
        )

        row = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            invoice_no,
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color="#1E293B",
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(job_no, size=13, color="#1E293B"),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            customer_name, size=13, color="#1E293B", max_lines=1
                        ),
                        width=150,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            plate_number,
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color="#1E293B",
                        ),
                        width=110,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(
                            brand_model, size=12, color="#64748B", max_lines=1
                        ),
                        width=150,
                        padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    ),
                    ft.Container(
                        content=ft.Text(paid_date, size=12, color="#64748B"),
                        width=120,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(
                        content=ft.Row([print_btn, view_btn], spacing=6),
                        width=160,
                        alignment=ft.Alignment(0, 0),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            bgcolor=row_bg,
        )

        return ft.Column(
            [row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0
        )

    # ─────────────────────────────────────────────────────────────
    # Print delivery note PDF
    # ─────────────────────────────────────────────────────────────
    def print_delivery_note(self, invoice_id: int):
        try:
            self._show_snack("ກຳລັງກຽມພິມໃບສົ່ງມອບລົດ...", is_error=False)

            pdf_bytes = self.client.get_delivery_note_pdf(invoice_id)
            if not pdf_bytes:
                self._show_snack("ບໍ່ສາມາດສ້າງ PDF ໄດ້", is_error=True)
                return

            base_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.abspath(
                os.path.join(base_dir, "..", "..", "..")
            )
            output_dir = os.path.join(workspace_root, "output")
            os.makedirs(output_dir, exist_ok=True)

            invoice_no = f"INV-{invoice_id:04d}"
            pdf_path = os.path.join(
                output_dir, f"delivery_note_{invoice_no}.pdf"
            )
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)

            os.startfile(pdf_path)
            self._show_snack("ພິມໃບສົ່ງມອບລົດສຳເລັດ!", is_error=False)

        except Exception as ex:
            print(f"Error printing delivery note: {ex}")
            self._show_snack(f"Error: {str(ex)}", is_error=True)

    # ─────────────────────────────────────────────────────────────
    # Pagination
    # ─────────────────────────────────────────────────────────────
    def _update_pagination(self):
        prev_disabled = self.current_page_num <= 1
        next_disabled = self.current_page_num >= self.total_pages

        self.pagination_container.content = ft.Row(
            [
                ft.Text(
                    f"{get_text('showing')} {len(self.filtered_invoices)} {get_text('of')} {len(self.invoices)} {get_text('results')}",
                    size=12,
                    color="#64748B",
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_LEFT,
                                icon_size=20,
                                on_click=self._prev_page,
                                disabled=prev_disabled,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                            ),
                            ft.Container(
                                content=ft.Text(
                                    f"{self.current_page_num}/{self.total_pages}",
                                    size=13,
                                    weight=ft.FontWeight.W_500,
                                    color="#1E293B",
                                ),
                                padding=ft.Padding(
                                    left=15, right=15, top=0, bottom=0
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_RIGHT,
                                icon_size=20,
                                on_click=self._next_page,
                                disabled=next_disabled,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                            ),
                        ]
                    ),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()

    def _prev_page(self, e=None):
        if self.current_page_num > 1:
            self.current_page_num -= 1
            self.display_invoices()

    def _next_page(self, e=None):
        if self.current_page_num < self.total_pages:
            self.current_page_num += 1
            self.display_invoices()

    # ─────────────────────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────────────────────
    def _show_snack(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, size=13),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=3000,
        )
        self.page.update()
