# pages/purchase/receiving_po_list.py
import flet as ft
from typing import Callable, Dict, List
import asyncio

from i18n import get_text


class ReceivingPoListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.accent_green = "#10B981"
        self.current_snackbar = None

        # State
        self.all_orders: List[Dict] = []
        self.selected_po: Dict = None
        self.receive_items: List[Dict] = []
        self.qty_fields: Dict[int, ft.TextField] = {}
        self.cost_fields: Dict[int, ft.TextField] = {}

        # UI refs
        self.po_list_column = None
        self.search_field = None
        self.right_panel = None
        self.empty_right = None
        self.items_column = None
        self.po_header_text = None
        self.supplier_text = None

    # ──────────────────────────────────────────────
    #  BUILD
    # ──────────────────────────────────────────────
    def build(self):
        header = self._build_header()
        body = ft.Row([
            self._build_left_panel(),
            self._build_right_panel(),
        ], spacing=0, expand=True, vertical_alignment=ft.CrossAxisAlignment.START)

        self.page.run_task(self._load_data_async)

        return ft.Container(
            content=ft.Column([header, body], spacing=0, expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )

    async def _load_data_async(self):
        await asyncio.sleep(0.1)
        await asyncio.to_thread(self.load_purchase_orders)

    # ──────────────────────────────────────────────
    #  HEADER
    # ──────────────────────────────────────────────
    def _build_header(self):
        return ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_size=24,
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda e: self.navigate("receiving_management"),
                    tooltip=get_text("back"),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
                ft.Column([
                    ft.Text("ສ້າງໃບນຳເຂົ້າ", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("ເລືອກໃບສັ່ງຊື້ ແລ້ວກວດສອບຈຳນວນອາໄຫຼ່ທີ່ຕ້ອງການຮັບ", size=13, color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
                ], spacing=2, expand=True),
            ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=24, right=24, top=14, bottom=14),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )

    # ──────────────────────────────────────────────
    #  LEFT PANEL – PO list
    # ──────────────────────────────────────────────
    def _build_left_panel(self):
        self.search_field = ft.TextField(
            hint_text="ຄົ້ນຫາໃບສັ່ງຊື້...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=14, right=14, top=12, bottom=12),
            on_change=self._on_search,
        )

        self.po_list_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        return ft.Container(
            content=ft.Column([
                # Section title
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LIST_ALT_ROUNDED, color=self.primary_color, size=20),
                        ft.Text("ລາຍການໃບສັ່ງຊື້", size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ], spacing=8),
                    padding=ft.Padding(left=0, right=0, top=0, bottom=8),
                ),
                self.search_field,
                ft.Container(height=12),
                self.po_list_column,
            ], spacing=0, expand=True),
            width=340,
            padding=24,
            bgcolor="#F8FAFC",
            border=ft.Border(right=ft.BorderSide(1, "#E2E8F0")),
            expand=False,
        )

    # ──────────────────────────────────────────────
    #  RIGHT PANEL – PO items / receive form
    # ──────────────────────────────────────────────
    def _build_right_panel(self):
        self.empty_right = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=72, color="#CBD5E1"),
                ft.Text("ກະລຸນາເລືອກໃບສັ່ງຊື້ທາງດ້ານຊ້າຍ", size=15, color="#94A3B8"),
                ft.Text("ລາຍການອາໄຫຼ່ຈະສະແດງຢູ່ທີ່ນີ້", size=13, color="#CBD5E1"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

        self.po_header_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color="#1E293B")
        self.supplier_text = ft.Text("", size=13, color="#64748B")
        self.items_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

        self.right_panel = ft.Container(
            content=self.empty_right,
            expand=True,
            padding=24,
            bgcolor=ft.Colors.WHITE,
        )
        return self.right_panel

    # ──────────────────────────────────────────────
    #  LOAD DATA
    # ──────────────────────────────────────────────
    def load_purchase_orders(self):
        try:
            orders = self.client.get_purchase_orders()
            self.all_orders = [o for o in orders if o.get("status") in ["ordering", "partial"]]
            self._render_po_list(self.all_orders)
        except Exception as ex:
            self._show_snack(f"ໂຫຼດຂໍ້ມູນບໍ່ສຳເລັດ: {ex}", "error")

    def _render_po_list(self, orders: List[Dict]):
        self.po_list_column.controls.clear()

        if not orders:
            self.po_list_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=40, color="#CBD5E1"),
                        ft.Text("ບໍ່ມີໃບສັ່ງຊື້ທີ່ລໍຖ້າ", size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=30,
                )
            )
        else:
            for order in orders:
                self.po_list_column.controls.append(self._build_po_card(order))

        if hasattr(self.page, 'update'):
            self.page.update()

    def _build_po_card(self, order: Dict):
        po_id = order.get("id")
        po_no = order.get("po_no", "-")
        supplier = order.get("supplier_name", "-")
        status = order.get("status", "ordering")
        total = order.get("total_amount", 0)

        status_color = "#2196F3" if status == "ordering" else "#FF9800"
        status_label = "ສັ່ງຊື້" if status == "ordering" else "ຮັບບາງສ່ວນ"
        is_selected = self.selected_po and self.selected_po.get("id") == po_id

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(po_no, size=14, weight=ft.FontWeight.BOLD, color="#1E293B", expand=True),
                    ft.Container(
                        content=ft.Text(status_label, size=11, color=ft.Colors.WHITE),
                        bgcolor=status_color,
                        border_radius=10,
                        padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                    ),
                ], spacing=8),
                ft.Text(supplier, size=12, color="#64748B"),
               
            ], spacing=4),
            padding=14,
            bgcolor=ft.Colors.with_opacity(0.12, self.primary_color) if is_selected else ft.Colors.WHITE,
            border=ft.Border(
                top=ft.BorderSide(1, "#E2E8F0"),
                right=ft.BorderSide(1, "#E2E8F0"),
                bottom=ft.BorderSide(1, "#E2E8F0"),
                left=ft.BorderSide(4, self.primary_color if is_selected else "#E2E8F0"),
            ),
            border_radius=12,
            ink=True,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color=ft.Colors.with_opacity(0.06, "black"), offset=ft.Offset(0, 2)) if is_selected else None,
            on_click=lambda e, oid=po_id: self._select_po(oid),
        )
        return card

    def _select_po(self, po_id: int):
        try:
            po_data = self.client.get_purchase_order(po_id)
            if not po_data:
                self._show_snack("ບໍ່ພົບຂໍ້ມູນໃບສັ່ງຊື້", "error")
                return

            self.selected_po = po_data
            self._render_po_list(self.all_orders)   # refresh to highlight selected
            self._render_right_panel(po_data)
        except Exception as ex:
            self._show_snack(f"ໂຫຼດລາຍການບໍ່ສຳເລັດ: {ex}", "error")

    # ──────────────────────────────────────────────
    #  RIGHT PANEL render
    # ──────────────────────────────────────────────
    def _render_right_panel(self, po_data: Dict):
        po_no = po_data.get("po_no", "-")
        supplier = po_data.get("supplier_name", "-")
        items = po_data.get("items", [])
        po_id = po_data.get("id")

        self.receive_items = []
        self.qty_fields = {}
        self.cost_fields = {}

        receive_rows = []
        for idx, item in enumerate(items):
            qty = item.get("qty", 0)
            received_qty = item.get("received_qty", 0)
            remaining = qty - received_qty
            if remaining <= 0:
                continue

            entry = {
                'part_id': item.get("part_id"),
                'part_name': item.get("part_name", "-"),
                'qty': qty,
                'already_received': received_qty,
                'remaining': remaining,
                'unit_cost': item.get("unit_cost", 0),
            }
            self.receive_items.append(entry)
            idx_r = len(self.receive_items) - 1

            qty_field = ft.TextField(
                value=str(remaining),
                width=100,
                text_align=ft.TextAlign.CENTER,
                input_filter=ft.NumbersOnlyInputFilter(),
                border_radius=10,
                bgcolor="#F8FAFC",
                border_color="#CBD5E1",
                focused_border_color=self.primary_color,
                content_padding=ft.Padding(left=8, right=8, top=10, bottom=10),
                text_size=15,
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            )
            self.qty_fields[idx_r] = qty_field

            # ─── ປ່ຽນ: ສະແດງ 0 ແທນທີ່ຈະດຶງລາຄາຈາກ PO ───
            cost_field = ft.TextField(
                value="0",  # ສະແດງ 0 ໃຫ້ຜູ້ໃຊ້ປ້ອນເອງ
                width=140,
                text_align=ft.TextAlign.RIGHT,
                input_filter=ft.NumbersOnlyInputFilter(),
                border_radius=10,
                bgcolor="#F8FAFC",
                border_color="#CBD5E1",
                focused_border_color=self.primary_color,
                content_padding=ft.Padding(left=12, right=12, top=10, bottom=10),
                text_size=14,
                hint_text="ປ້ອນລາຄາ",
            )
            self.cost_fields[idx_r] = cost_field

            def make_qty_handler(field_ref, max_qty):
                def handler(e):
                    try:
                        val = int(field_ref.value) if field_ref.value else 0
                        if val > max_qty: field_ref.value = str(max_qty)
                        elif val < 0: field_ref.value = "0"
                    except:
                        field_ref.value = "0"
                    self.page.update()
                return handler

            qty_field.on_change = make_qty_handler(qty_field, remaining)

            row_card = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.BUILD_CIRCLE_OUTLINED, color=self.primary_color, size=22),
                        padding=10,
                        bgcolor=ft.Colors.with_opacity(0.08, self.primary_color),
                        border_radius=10,
                    ),
                    ft.Column([
                        ft.Text(entry['part_name'], size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(f"ສັ່ງ {qty}", size=11, color="#64748B"),
                                bgcolor="#F1F5F9", border_radius=6,
                                padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                            ),
                            ft.Container(
                                content=ft.Text(f"ຮັບແລ້ວ {received_qty}", size=11, color="#64748B"),
                                bgcolor="#F1F5F9", border_radius=6,
                                padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                            ),
                            ft.Container(
                                content=ft.Text(f"ເຫຼືອ {remaining}", size=11, color="#F59E0B", weight=ft.FontWeight.BOLD),
                                bgcolor="#FEF3C7", border_radius=6,
                                padding=ft.Padding(left=8, right=8, top=3, bottom=3),
                            ),
                        ], spacing=6),
                    ], spacing=6, expand=True),
                    ft.Column([
                        ft.Text("ປ້ອນລາຄາ (₭)", size=11, color="#64748B", text_align=ft.TextAlign.CENTER),
                        cost_field,
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([
                        ft.Text("ຈຳນວນທີ່ໄດ້ຮັບ", size=11, color="#64748B", text_align=ft.TextAlign.CENTER),
                        qty_field,
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=16,
                bgcolor=ft.Colors.WHITE,
                border=ft.Border(
                    top=ft.BorderSide(1, "#E2E8F0"),
                    right=ft.BorderSide(1, "#E2E8F0"),
                    bottom=ft.BorderSide(1, "#E2E8F0"),
                    left=ft.BorderSide(4, self.primary_color),
                ),
                border_radius=12,
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color=ft.Colors.with_opacity(0.05, "black"), offset=ft.Offset(0, 2)),
            )
            receive_rows.append(row_card)

        # Empty items state
        if not receive_rows:
            items_body = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=48, color=self.accent_green),
                    ft.Text("ຮັບເຂົ້າສຳເລັດທຸກລາຍການແລ້ວ", size=14, color="#64748B"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                padding=40,
                alignment=ft.alignment.center,
            )
        else:
            items_body = ft.Column(receive_rows, spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

        confirm_btn = ft.ElevatedButton(
            "ຢືນຢັນການຮັບເຂົ້າ",
            icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
            style=ft.ButtonStyle(
                bgcolor=self.accent_green,
                color=ft.Colors.WHITE,
                padding=ft.Padding(left=28, right=28, top=14, bottom=14),
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            on_click=lambda e: self._confirm_receive(po_id),
            disabled=not receive_rows,
        )

        content = ft.Column([
            # PO info header
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.RECEIPT_LONG, color=self.primary_color, size=20),
                            ft.Text(po_no, size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ], spacing=8),
                        ft.Text(f"ຜູ້ສະໜອງ: {supplier}", size=13, color="#64748B"),
                    ], spacing=4, expand=True),
                    confirm_btn,
                ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=0, right=0, top=0, bottom=20),
                border=ft.Border(bottom=ft.BorderSide(1, "#E2E8F0")),
            ),

            # Column headers
            ft.Container(
                content=ft.Row([
                    ft.Container(width=42),
                    ft.Text("ລາຍການອາໄຫຼ່", size=12, weight=ft.FontWeight.BOLD, color="#64748B", expand=True),
                    ft.Text("ລາຄາທຶນ/ໜ່ວຍ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=140, text_align=ft.TextAlign.CENTER),
                    ft.Text("ຈຳນວນທີ່ໄດ້ຮັບ", size=12, weight=ft.FontWeight.BOLD, color="#64748B", width=100, text_align=ft.TextAlign.CENTER),
                ], spacing=16),
                padding=ft.Padding(left=0, right=0, top=12, bottom=8),
            ),

            items_body,
        ], spacing=0, expand=True)

        self.right_panel.content = content
        self.page.update()

    # ──────────────────────────────────────────────
    #  CONFIRM
    # ──────────────────────────────────────────────
    def _confirm_receive(self, po_id: int):
        payload = []
        for idx, item in enumerate(self.receive_items):
            qty_field = self.qty_fields.get(idx)
            cost_field = self.cost_fields.get(idx)
            try:
                qty = int(qty_field.value) if qty_field and qty_field.value else 0
            except:
                qty = 0
            try:
                cost = float(cost_field.value) if cost_field and cost_field.value else 0.0
            except:
                cost = 0.0

            if qty > 0:
                payload.append({
                    'part_id': item['part_id'],
                    'received_qty': min(qty, item['remaining']),
                    'cost_price': cost,
                })

        if not payload:
            self._show_snack("ກະລຸນາລະບຸຈຳນວນຢ່າງໜ້ອຍ 1 ລາຍການ", "error")
            return

        try:
            result = self.client.receive_purchase_order(po_id, payload)
            if result:
                self._show_snack("ຮັບເຂົ້າສຳເລັດ! ອັບເດດສາງຮຽບຮ້ອຍ", "success")
                self.selected_po = None
                self.right_panel.content = self._build_right_panel_empty()
                self.page.update()
                self.load_purchase_orders()
            else:
                self._show_snack("ບັນທຶກລົ້ມເຫຼວ ກະລຸນາລອງໃໝ່", "error")
        except Exception as ex:
            print(f"❌ confirm_receive error: {ex}")
            self._show_snack(f"❌ {ex}", "error")

    def _build_right_panel_empty(self):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=72, color="#CBD5E1"),
                ft.Text("ກະລຸນາເລືອກໃບສັ່ງຊື້ທາງດ້ານຊ້າຍ", size=15, color="#94A3B8"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

    # ──────────────────────────────────────────────
    #  SEARCH
    # ──────────────────────────────────────────────
    def _on_search(self, e):
        kw = self.search_field.value.lower() if self.search_field.value else ""
        filtered = [
            o for o in self.all_orders
            if kw in o.get("po_no", "").lower() or kw in o.get("supplier_name", "").lower()
        ] if kw else self.all_orders
        self._render_po_list(filtered)

    # ──────────────────────────────────────────────
    #  SNACK
    # ──────────────────────────────────────────────
    def _show_snack(self, msg: str, type="success"):
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