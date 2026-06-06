# pages/quotations/quotation_create.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable, List
from datetime import datetime, timedelta

from i18n import get_text


class QuotationCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, job_order_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.job_order_id = job_order_id
        self.job_order_data = None
        self.quotation_id = None
        self.quotation_items = []
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.job_orders = []
        self.show_selection = job_order_id is None
        self.parts_list = []
        self.services_list = []
        self.temp_items = []
        self.current_tab = "parts"
        self.search_field = None
        self.results_list = None
        self.qty_field = None
        self.items_list = None
        self.subtotal_text = None
        self.total_text = None
        self.parts_btn = None
        self.services_btn = None
        self.job_orders_list = None
        
    def build(self):
        header = self._build_header()
        
        if self.show_selection:
            content = self._build_selection_content()
        else:
            content = self._build_quotation_content()
        
        main_content = ft.Container(
            content=ft.Column([header, content]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    
                    ft.Column(
                        [
                            ft.Text(
                                get_text("quotation_create"),
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
            padding=ft.padding.symmetric(vertical=14, horizontal=26),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
            
        )
    
    def _build_selection_content(self):
        search_field = ft.TextField(
            hint_text=get_text("search_job_order"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            on_change=self.search_job_orders,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.job_orders_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        
        selection_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT, size=24, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=12,
                                padding=ft.padding.all(10),
                            ),
                            ft.Text(
                                get_text("select_job_order_for_quotation"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=16),
                    search_field,
                    ft.Container(height=16),
                    ft.Text(
                        get_text("pending_job_orders"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color="#64748B",
                    ),
                    ft.Container(height=12),
                    ft.Container(
                        content=self.job_orders_list,
                        expand=True,
                    ),
                ], spacing=0),
                padding=ft.padding.all(24),
                expand=True,
            ),
            elevation=2,
            expand=True,
        )
        
        content_area = ft.Container(
            content=ft.Column([selection_card], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
            padding=ft.padding.all(32),
            bgcolor="#F5F7FA",
        )
        
        self.load_pending_job_orders()
        
        return content_area
    
    def _build_quotation_content(self):
        self.load_job_order()
        self.load_parts_and_services()
        
        # Job Order Info Card
        job_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                get_text("job_order_info"),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Column([
                            ft.Text(get_text("job_number"), size=12, color="#64748B"),
                            ft.Text(self.job_order_data.get("job_no", "-") if self.job_order_data else "-", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("customer_name"), size=12, color="#64748B"),
                            ft.Text(self.job_order_data.get("customer_name", "-") if self.job_order_data else "-", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                        ft.Column([
                            ft.Text(get_text("plate_number"), size=12, color="#64748B"),
                            ft.Text(self.job_order_data.get("plate_number", "-") if self.job_order_data else "-", size=14, weight=ft.FontWeight.W_500),
                        ], spacing=2, expand=True),
                    ]),
                    ft.Container(height=8),
                    ft.Text(
                        get_text("problem_description"),
                        size=12,
                        color="#64748B",
                    ),
                    ft.Text(
                        self.job_order_data.get("problem_description", "-") if self.job_order_data else "-",
                        size=13,
                        color="#1E293B",
                    ),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Add Item Section
        add_item_header = ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=20, color=self.primary_color),
                    bgcolor="#E3F2FD",
                    border_radius=8,
                    padding=ft.padding.all(6),
                ),
                ft.Text(
                    get_text("add_items"),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#1E293B",
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Tab buttons
        parts_btn = ft.Container(
            content=ft.Text(get_text("parts"), size=14, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
            bgcolor=self.primary_color,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            on_click=lambda e: self.switch_tab("parts"),
        )
        
        services_btn = ft.Container(
            content=ft.Text(get_text("services"), size=14, weight=ft.FontWeight.W_500, color="#64748B"),
            bgcolor=ft.Colors.GREY_200,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            on_click=lambda e: self.switch_tab("services"),
        )
        
        self.parts_btn = parts_btn
        self.services_btn = services_btn
        
        # Search and quantity row
        self.search_field = ft.TextField(
            hint_text=get_text("search_items"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            expand=True,
            on_change=self.search_items,
        )
        
        self.qty_field = ft.TextField(
            label=get_text("quantity"),
            value="1",
            width=100,
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            input_filter=ft.NumbersOnlyInputFilter(),
            text_align=ft.TextAlign.CENTER,
        )
        
        # Results list
        self.results_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=250)
        
        add_item_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    add_item_header,
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([parts_btn, services_btn], spacing=10),
                    ft.Container(height=12),
                    ft.Row([self.search_field, self.qty_field], spacing=12),
                    ft.Container(height=12),
                    self.results_list,
                ]),
                padding=ft.padding.all(16),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Items List Header
        items_header = ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.LIST, size=20, color=self.primary_color),
                    bgcolor="#E3F2FD",
                    border_radius=8,
                    padding=ft.padding.all(6),
                ),
                ft.Text(
                    get_text("quotation_items"),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#1E293B",
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Items List
        self.items_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        items_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    items_header,
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Container(
                        content=self.items_list,
                        expand=True,
                    ),
                ]),
                padding=ft.padding.all(16),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Summary Card
        self.subtotal_text = ft.Text("0", size=18, weight=ft.FontWeight.BOLD, color="#1E293B")
        self.total_text = ft.Text("0", size=22, weight=ft.FontWeight.BOLD, color=self.primary_color)
        
        summary_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.CALCULATE, size=18, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=8,
                                padding=ft.padding.all(6),
                            ),
                            ft.Text(
                                get_text("summary"),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=12),
                    ft.Row([
                        ft.Text(get_text("subtotal"), size=14, color="#64748B"),
                        ft.Container(expand=True),
                        self.subtotal_text,
                    ]),
                    ft.Row([
                        ft.Text(get_text("total_amount"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ft.Container(expand=True),
                        self.total_text,
                    ]),
                ]),
                padding=ft.padding.all(16),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Action Buttons
        save_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("save_quotation"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=self.save_quotation,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=2,
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
        )
        
        approve_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("approve_quotation"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=self.approve_quotation,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                shape=ft.RoundedRectangleBorder(radius=8),
                elevation=2,
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
        )
        
        print_btn = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT, size=18, color=self.primary_color),
                ft.Text(get_text("print"), size=14, color=self.primary_color),
            ], spacing=6),
            on_click=self.print_quotation,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, self.primary_color),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
        )
        
        action_row = ft.Row([save_btn, approve_btn, print_btn], spacing=12, alignment=ft.MainAxisAlignment.END)
        
        scrollable_content = ft.Column(
            [
                job_info_card,
                add_item_card,
                items_card,
                summary_card,
                action_row,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.padding.all(24),
            bgcolor="#F5F7FA",
        )
        
        # Initial search
        self.search_items(None)
        self.update_total_display()
        
        return content_area
    
    def switch_tab(self, tab):
        """Switch between parts and services tabs"""
        self.current_tab = tab
        
        if tab == "parts":
            self.parts_btn.bgcolor = self.primary_color
            self.parts_btn.content.color = ft.Colors.WHITE
            self.services_btn.bgcolor = ft.Colors.GREY_200
            self.services_btn.content.color = "#64748B"
            self.search_field.hint_text = get_text("search_parts")
        else:
            self.services_btn.bgcolor = self.primary_color
            self.services_btn.content.color = ft.Colors.WHITE
            self.parts_btn.bgcolor = ft.Colors.GREY_200
            self.parts_btn.content.color = "#64748B"
            self.search_field.hint_text = get_text("search_services")
        
        self.search_field.value = ""
        self.search_items(None)
        self.page.update()
    
    def search_items(self, e):
        """Search for parts or services"""
        keyword = self.search_field.value.lower() if self.search_field.value else ""
        self.results_list.controls.clear()
        
        if self.current_tab == "parts":
            results = self.parts_list
            if keyword:
                results = [p for p in results if keyword in p.get("name", "").lower() or keyword in p.get("part_code", "").lower()]
            
            for part in results[:20]:
                item = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"{part.get('part_code', '')} - {part.get('name', '')}", weight=ft.FontWeight.W_500, size=13),
                            ft.Text(f"{part.get('brand', '-')} | Stock: {part.get('stock_qty', 0)}", size=10, color="#64748B"),
                        ], expand=True),
                        ft.Text(f"{int(part.get('sell_price', 0)):,} KIP", size=13, weight=ft.FontWeight.BOLD, color=self.primary_color),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_size=20,
                            icon_color=self.primary_color,
                            tooltip=get_text("add"),
                            on_click=lambda e, pid=part.get('id'), pname=part.get('name'), pprice=part.get('sell_price'): self.add_to_temp_list("part", pid, pname, pprice),
                        ),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=6,
                )
                self.results_list.controls.append(item)
        else:
            results = self.services_list
            if keyword:
                results = [s for s in results if keyword in s.get("service_name", "").lower()]
            
            for service in results[:20]:
                item = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(service.get("service_name", ""), weight=ft.FontWeight.W_500, size=13),
                            ft.Text(service.get("description", "-")[:40], size=10, color="#64748B"),
                        ], expand=True),
                        ft.Text(f"{int(service.get('price', 0)):,} KIP", size=13, weight=ft.FontWeight.BOLD, color=self.primary_color),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_size=20,
                            icon_color=self.primary_color,
                            tooltip=get_text("add"),
                            on_click=lambda e, sid=service.get('id'), sname=service.get('service_name'), sprice=service.get('price'): self.add_to_temp_list("service", sid, sname, sprice),
                        ),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=6,
                )
                self.results_list.controls.append(item)
        
        if not self.results_list.controls:
            self.results_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=40, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_items_found"), size=13, color="#64748B"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(30),
                )
            )
        
        self.page.update()
    
    def add_to_temp_list(self, item_type, ref_id, name, price):
        """Add item to temporary list"""
        qty = int(self.qty_field.value) if self.qty_field.value else 1
        
        temp_id = len(self.temp_items) + 1
        self.temp_items.append({
            "temp_id": temp_id,
            "item_type": item_type,
            "ref_id": ref_id,
            "name": name,
            "qty": qty,
            "unit_price": price,
            "total": qty * price
        })
        
        self.display_temp_items()
        self.show_snack_bar(f"✅ {get_text('item_added')}: {name}", is_error=False)
    
    def display_temp_items(self):
        """Display temporary items list"""
        self.items_list.controls.clear()
        total = 0
        
        for item in self.temp_items:
            temp_id = item.get("temp_id")
            name = item.get("name", "-")
            qty = item.get("qty", 1)
            unit_price = item.get("unit_price", 0)
            item_total = item.get("total", 0)
            total += item_total
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Text(f"{qty}x", size=13, weight=ft.FontWeight.W_500, color=self.primary_color, width=40),
                    ft.Column([
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500),
                        ft.Text(f"{int(unit_price):,} KIP", size=10, color="#64748B"),
                    ], expand=True),
                    ft.Text(f"{int(item_total):,} KIP", size=13, weight=ft.FontWeight.BOLD, color="#1E293B", width=100),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_size=16,
                        tooltip=get_text("edit"),
                        on_click=lambda e, tid=temp_id, iqty=qty: self.show_edit_qty_dialog(tid, iqty),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        tooltip=get_text("delete"),
                        on_click=lambda e, tid=temp_id: self.remove_temp_item(tid),
                    ),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=6, horizontal=10),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
            )
            self.items_list.controls.append(item_row)
        
        self.update_total_display()
        self.page.update()
    
    def show_edit_qty_dialog(self, temp_id, current_qty):
        """Show dialog to edit quantity"""
        qty_field = ft.TextField(
            label=get_text("quantity"), 
            value=str(current_qty), 
            width=120,
            input_filter=ft.NumbersOnlyInputFilter(),
            text_align=ft.TextAlign.CENTER,
        )
        
        def update_qty(e):
            new_qty = int(qty_field.value) if qty_field.value else 1
            for item in self.temp_items:
                if item.get("temp_id") == temp_id:
                    item["qty"] = new_qty
                    item["total"] = new_qty * item["unit_price"]
                    break
            self.display_temp_items()
            dialog.open = False
            self.page.update()
            self.show_snack_bar(get_text("item_updated"), is_error=False)
        
        dialog = ft.AlertDialog(
            title=ft.Text(get_text("edit_quantity")),
            content=ft.Container(
                content=qty_field,
                padding=ft.padding.all(20),
                width=200,
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("save"), on_click=update_qty),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def remove_temp_item(self, temp_id):
        """Remove item from temporary list"""
        self.temp_items = [item for item in self.temp_items if item.get("temp_id") != temp_id]
        self.display_temp_items()
    
    def update_total_display(self):
        """Update total price display"""
        total = sum(item.get("total", 0) for item in self.temp_items)
        self.subtotal_text.value = f"{int(total):,} KIP"
        self.total_text.value = f"{int(total):,} KIP"
        self.page.update()
    
    def save_quotation(self, e):
        if not self.temp_items:
            self.show_snack_bar(get_text("no_items_added"), is_error=True)
            return
        
        if not self.quotation_id:
            success = self.create_quotation()
            if not success:
                return
        
        try:
            for item in self.temp_items:
                self.client.add_quotation_item(
                    self.quotation_id, 
                    item["item_type"], 
                    item["ref_id"], 
                    item["qty"]
                )
            self.client.calculate_quotation_total(self.quotation_id)
            
            job_no = self.job_order_data.get("job_no", "N/A") if self.job_order_data else "N/A"
            self.show_success_popup(job_no)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def approve_quotation(self, e):
        if not self.temp_items:
            self.show_snack_bar(get_text("no_items_added"), is_error=True)
            return
        
        if not self.quotation_id:
            success = self.create_quotation()
            if not success:
                return
        
        try:
            for item in self.temp_items:
                self.client.add_quotation_item(
                    self.quotation_id, 
                    item["item_type"], 
                    item["ref_id"], 
                    item["qty"]
                )
            self.client.calculate_quotation_total(self.quotation_id)
            self.client.update_quotation_status(self.quotation_id, "approved")
            
            job_no = self.job_order_data.get("job_no", "N/A") if self.job_order_data else "N/A"
            self.show_success_popup(job_no)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
    
    def print_quotation(self, e):
        if self.quotation_id:
            self.navigate("quotation_print", quotation_id=self.quotation_id)
        else:
            self.show_snack_bar(get_text("save_quotation_first"), is_error=True)
    
    def load_parts_and_services(self):
        try:
            self.parts_list = self.client.get_parts()
            self.services_list = self.client.get_services()
        except Exception as ex:
            print(f"Error loading parts/services: {ex}")
            self.parts_list = []
            self.services_list = []
    
    def load_pending_job_orders(self):
        try:
            all_orders = self.client.get_job_orders()
            self.job_orders = [o for o in all_orders if o.get('status') in ['pending', 'quoting']]
            self.display_job_orders()
        except Exception as ex:
            print(f"Error loading job orders: {ex}")
    
    def display_job_orders(self):
        self.job_orders_list.controls.clear()
        
        if not self.job_orders:
            self.job_orders_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_pending_job_orders"), size=14, color="#64748B"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(40),
                )
            )
        else:
            for order in self.job_orders:
                order_id = order.get('id')
                job_no = order.get('job_no', 'N/A')
                customer_name = order.get('customer_name', '-')
                plate_number = order.get('plate_number', '-')
                status = order.get('status', 'pending')
                
                status_color = "#FF9800" if status == 'pending' else "#2196F3"
                status_text = get_text("pending") if status == 'pending' else get_text("quoting")
                
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT, size=24, color=self.primary_color),
                                width=40,
                            ),
                            ft.Column([
                                ft.Text(job_no, size=14, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{customer_name} | {plate_number}", size=11, color="#64748B"),
                            ], expand=True),
                            ft.Container(
                                content=ft.Text(status_text, size=10, color=ft.Colors.WHITE),
                                bgcolor=status_color,
                                border_radius=10,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                            ft.ElevatedButton(
                                get_text("select"),
                                on_click=lambda e, oid=order_id: self.select_job_order(oid),
                                style=ft.ButtonStyle(
                                    bgcolor=self.primary_color,
                                    color=ft.Colors.WHITE,
                                    padding=ft.padding.symmetric(horizontal=12, vertical=5),
                                    shape=ft.RoundedRectangleBorder(radius=6),
                                ),
                            ),
                        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.all(10),
                    ),
                    elevation=1,
                    margin=ft.margin.only(bottom=6),
                )
                self.job_orders_list.controls.append(card)
        
        self.page.update()
    
    def search_job_orders(self, e):
        keyword = e.control.value.lower() if e.control.value else ""
        
        if keyword:
            filtered = [o for o in self.job_orders if 
                       keyword in o.get('job_no', '').lower() or
                       keyword in o.get('customer_name', '').lower() or
                       keyword in o.get('plate_number', '').lower()]
        else:
            filtered = self.job_orders
        
        self.job_orders_list.controls.clear()
        
        if not filtered:
            self.job_orders_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_results_found"), size=14, color="#64748B"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(40),
                )
            )
        else:
            for order in filtered:
                order_id = order.get('id')
                job_no = order.get('job_no', 'N/A')
                customer_name = order.get('customer_name', '-')
                plate_number = order.get('plate_number', '-')
                status = order.get('status', 'pending')
                
                status_color = "#FF9800" if status == 'pending' else "#2196F3"
                status_text = get_text("pending") if status == 'pending' else get_text("quoting")
                
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.RECEIPT, size=24, color=self.primary_color),
                                width=40,
                            ),
                            ft.Column([
                                ft.Text(job_no, size=14, weight=ft.FontWeight.BOLD),
                                ft.Text(f"{customer_name} | {plate_number}", size=11, color="#64748B"),
                            ], expand=True),
                            ft.Container(
                                content=ft.Text(status_text, size=10, color=ft.Colors.WHITE),
                                bgcolor=status_color,
                                border_radius=10,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                            ft.ElevatedButton(
                                get_text("select"),
                                on_click=lambda e, oid=order_id: self.select_job_order(oid),
                                style=ft.ButtonStyle(
                                    bgcolor=self.primary_color,
                                    color=ft.Colors.WHITE,
                                    padding=ft.padding.symmetric(horizontal=12, vertical=5),
                                    shape=ft.RoundedRectangleBorder(radius=6),
                                ),
                            ),
                        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.all(10),
                    ),
                    elevation=1,
                    margin=ft.margin.only(bottom=6),
                )
                self.job_orders_list.controls.append(card)
        
        self.page.update()
    
    def select_job_order(self, order_id: int):
        self.job_order_id = order_id
        self.show_selection = False
        self.load_job_order()
        
        if len(self.page.controls) > 0:
            main_layout = self.page.controls[0]
            if isinstance(main_layout, ft.Column) and len(main_layout.controls) > 1:
                main_row = main_layout.controls[1]
                if isinstance(main_row, ft.Row) and len(main_row.controls) > 1:
                    content_container = main_row.controls[1]
                    if isinstance(content_container, ft.Container):
                        new_header = self._build_header()
                        new_content = self._build_quotation_content()
                        full_content = ft.Container(
                            content=ft.Column([new_header, new_content]),
                            expand=True,
                            bgcolor="#F5F7FA",
                        )
                        content_container.content = full_content
                        content_container.update()
                        return
        
        self.page.controls.clear()
        self.page.add(self.build())
        self.page.update()
    
    def load_job_order(self):
        try:
            self.job_order_data = self.client.get_job_order(self.job_order_id)
            self.page.update()
        except Exception as ex:
            print(f"Error loading job order: {ex}")
    
    def create_quotation(self):
        try:
            result = self.client.create_quotation(self.job_order_id)
            if result:
                self.quotation_id = result.get("id")
                return True
        except Exception as ex:
            print(f"Error creating quotation: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", is_error=True)
            return False
    
    def show_success_popup(self, job_no: str):
        def go_to_list(e):
            popup.open = False
            self.page.update()
            self.navigate("quotation_list")
        
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.Colors.WHITE,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=self.success_color),
                        ft.Container(height=16),
                        ft.Text(
                            get_text("quotation_created"),
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            f"{get_text('job_number')}: {job_no}",
                            size=14,
                            color="#64748B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=16),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("view_quotations"), size=14, color=ft.Colors.WHITE),
                            on_click=go_to_list,
                            style=ft.ButtonStyle(
                                bgcolor=self.primary_color,
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=ft.padding.symmetric(horizontal=24, vertical=10),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                width=350,
                padding=ft.padding.all(24),
            ),
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def go_back(self, e):
        try:
            self.navigate("dashboard")
        except Exception as ex:
            print(f"Error navigating back: {ex}")
            self.page.controls.clear()
            self.page.add(ft.Text("Loading..."))
            self.navigate("dashboard")
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def close_all_dialogs(self):
        for dialog in self.page.overlay:
            try:
                dialog.open = False
            except:
                pass
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()