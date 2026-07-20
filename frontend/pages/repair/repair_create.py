# pages/repair/repair_create.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime
import asyncio

from i18n import get_text


class RepairCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, 
                 job_order_id: int = None, content_container: ft.Container = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.job_order_id = job_order_id
        self.content_container = content_container
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.warning_color = "#F59E0B"
        self.current_snackbar = None
        
        # Data storage
        self.approved_jobs = []  # Job orders with status 'approved'
        self.selected_job = None
        self.selected_quotation = None  # The approved quotation for this job
        self.quotation_items = []
        self.mechanics = []
        self.filtered_mechanics = []
        
        # UI references - Left side (Job Order Selection & Mechanic)
        self.job_search_field = None
        self.job_clear_button = None
        self.job_results_container = None
        self.job_results_list = None
        self.selected_job_card = None
        self.selected_job_label = None
        self.job_details_card = None
        
        # UI references - Left side (Mechanic)
        self.mechanic_search_field = None
        self.mechanic_clear_button = None
        self.mechanic_results_list = None
        self.selected_mechanic_card = None
        self.selected_mechanic_label = None
        self.selected_mechanic_id = None
        self.selected_mechanic_data = None
        
        # UI references - Right side (Quotation Items)
        self.quotation_card = None
        self.items_table_body = None
        self.total_text = ft.Text("0 KIP", size=16, weight=ft.FontWeight.BOLD, color=self.success_color)
        
    def build(self):
        # --- Header with Create Button ---
        self.create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CONSTRUCTION, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("create_repair_order_btn"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=8),
            on_click=self.create_repair_order,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=0,
                padding=ft.Padding(left=20, right=20, top=12, bottom=12),
            ),
        )
        
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_size=20,
                        icon_color=ft.Colors.WHITE,
                        on_click=lambda e: self.navigate("repair_list"),
                        tooltip=get_text("back"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("new_repair"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    self.create_btn,
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
        
        # ==================== LEFT COLUMN: JOB ORDER & MECHANIC ====================
        # Job Order Search Section
        self.job_search_field = ft.TextField(
            label=get_text("search_job_order"),
            hint_text=get_text("search_by_job_no_customer_plate"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
            on_change=self.on_search_job,
            border_color=ft.Colors.GREY_200,
        )
        
        self.job_clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=18,
            icon_color=ft.Colors.GREY_500,
            on_click=lambda e: self.clear_job_search(),
            visible=False,
        )
        
        search_row = ft.Row([self.job_search_field, self.job_clear_button], spacing=8)
        
        self.job_results_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=200)
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
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=self.success_color),
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
            ),
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
            visible=False,
        )
        
        # Job Details Section (Clean Card style)
        self.job_details_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                    ft.Text(get_text("job_order_info"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=4),
                ft.Column(spacing=5, controls=[
                    self._create_info_row(get_text("job_number"), ""),
                    self._create_info_row(get_text("customer_name"), ""),
                    self._create_info_row(get_text("plate_number"), ""),
                    self._create_info_row(get_text("car_brand_model"), ""),
                    self._create_info_row(get_text("problem_description"), "", max_lines=2),
                ]),
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
            visible=False,
        )
        
        # Job Section
        job_section = ft.Column(
            [
                ft.Row([
                    ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                    ft.Text(get_text("select_job_order"), size=15, weight=ft.FontWeight.W_600, color="#1E293B")
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=8),
                search_row,
                ft.Container(height=8),
                self.job_results_container,
                self.selected_job_card,
                self.job_details_card,
            ],
            spacing=0,
        )
        
        # Mechanic Section
        self.mechanic_search_field = ft.TextField(
            label=get_text("search_mechanic"),
            hint_text=get_text("search_by_name_or_phone"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            expand=True,
            on_change=self.on_search_mechanic,
            border_color=ft.Colors.GREY_200,
        )
        
        self.mechanic_clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=18,
            icon_color=ft.Colors.GREY_500,
            on_click=lambda e: self.clear_mechanic_search(),
            visible=False,
        )
        
        mechanic_search_row = ft.Row([self.mechanic_search_field, self.mechanic_clear_button], spacing=8)
        
        self.mechanic_results_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        mechanic_results_container = ft.Container(
            content=self.mechanic_results_list,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            border_radius=12,
            padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            bgcolor=ft.Colors.WHITE,
        )
        
        self.selected_mechanic_label = ft.Text("", size=13, weight=ft.FontWeight.W_500, color="#1E293B")
        
        self.selected_mechanic_card = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=self.success_color),
                        ft.Column([
                            ft.Text(get_text("selected_mechanic"), size=11, color="#64748B"),
                            self.selected_mechanic_label,
                        ], spacing=2, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color="#64748B",
                            on_click=lambda e: self.clear_selected_mechanic(),
                            tooltip=get_text("clear_selection"),
                        ),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                ),
                elevation=0,
            ),
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
            visible=False,
        )
        
        mechanic_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=18, color=self.primary_color),
                    ft.Text(get_text("assign_mechanic"), size=15, weight=ft.FontWeight.W_600, color="#1E293B")
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=8),
                mechanic_search_row,
                ft.Container(height=8),
                self.selected_mechanic_card,
                ft.Container(height=8),
                ft.Text(get_text("mechanic_list"), size=12, color="#64748B"),
                ft.Container(height=4),
                mechanic_results_container,
            ], spacing=0),
            padding=0,
            bgcolor=None,
            margin=ft.Margin(left=0, right=0, top=0, bottom=0),
        )
        
        left_column = ft.Container(
            content=ft.Column([job_section, ft.Container(height=16), mechanic_section], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO),
            width=450,
            expand=True,
        )
        
        # ==================== RIGHT COLUMN: QUOTATION ITEMS (Clean Card) ====================
        self.items_table_body = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, height=350)
        
        self.quotation_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.REQUEST_QUOTE, size=18, color=self.primary_color),
                    ft.Text(get_text("approved_quotation_items"), size=15, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PRICE_CHANGE, size=14, color=self.success_color),
                            self.total_text,
                        ], spacing=4),
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                        bgcolor=ft.Colors.with_opacity(0.1, self.success_color),
                        border_radius=16,
                    ),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=8),
                # Header row
                ft.Row([
                    ft.Text("#", size=11, weight=ft.FontWeight.W_600, color="#64748B", width=35),
                    ft.Text(get_text("item_name"), size=11, weight=ft.FontWeight.W_600, color="#64748B", expand=True),
                    ft.Text(get_text("qty"), size=11, weight=ft.FontWeight.W_600, color="#64748B", width=60, text_align=ft.TextAlign.CENTER),
                    ft.Text(get_text("price"), size=11, weight=ft.FontWeight.W_600, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                    ft.Text(get_text("total"), size=11, weight=ft.FontWeight.W_600, color="#64748B", width=110, text_align=ft.TextAlign.RIGHT),
                ], spacing=6),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=4),
                self.items_table_body,
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            visible=False,
        )
        
        right_column = ft.Container(
            content=ft.Column([self.quotation_card], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO),
            width=600,
            expand=True,
        )
        
        # ==================== TWO COLUMN LAYOUT ====================
        two_columns = ft.Row(
            [left_column, ft.VerticalDivider(width=1, color=ft.Colors.GREY_300), right_column],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        main_card = ft.Container(
            content=two_columns,
            padding=ft.Padding(left=24, right=24, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            expand=True,
        )
        
        content_area = ft.Container(
            content=ft.Column([main_card], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor="#F0F2F5",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area], spacing=0, expand=True),
            expand=True,
        )
        
        # Load data
        self.page.run_task(self._load_data)
        
        return main_content
    
    def _create_info_row(self, label, value, max_lines=1):
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=12, color="#64748B", width=100),
                ft.Text(value, size=13, color="#1E293B", weight=ft.FontWeight.W_500, expand=True, max_lines=max_lines),
            ], spacing=12),
            padding=ft.Padding(left=0, right=0, top=5, bottom=5),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)),
        )
    
    async def _load_data(self):
        await asyncio.sleep(0.2)
        await asyncio.to_thread(self.load_mechanics)
        await asyncio.to_thread(self.load_approved_job_orders)
    
    def load_mechanics(self):
        try:
            self.mechanics = self.client.get_mechanics() or []
            self.filtered_mechanics = self.mechanics.copy()
            print(f"DEBUG: Loaded {len(self.mechanics)} mechanics")
            self._update_mechanic_list()
        except Exception as ex:
            print(f"Error loading mechanics: {ex}")
            self.mechanics = []
            self.filtered_mechanics = []
    
    def load_approved_job_orders(self):
        try:
            all_jobs = self.client.get_job_orders(status='approved') or []
            
            # Optimized: Fetch all repair orders in one single call and build a set of job_order_ids
            # that already have repair orders. This reduces database queries and API latency significantly.
            all_repairs = self.client.get_repair_orders() or []
            jobs_with_repairs = {r.get('job_order_id') for r in all_repairs if r.get('job_order_id')}
            
            self.approved_jobs = [job for job in all_jobs if job.get('id') not in jobs_with_repairs]
            
            print(f"DEBUG: Loaded {len(self.approved_jobs)} approved job orders ready for repair")
            
            if self.job_order_id:
                for job in self.approved_jobs:
                    if job.get('id') == self.job_order_id:
                        self.select_job_order(job)
                        break
            
            self._update_job_list()
            
        except Exception as ex:
            print(f"Error loading approved job orders: {ex}")
            self.approved_jobs = []
    
    def _update_job_list(self):
        self.job_results_list.controls.clear()
        
        if not self.approved_jobs:
            self.job_results_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=40, color="#CBD5E1"),
                        ft.Text(get_text("no_approved_jobs"), size=13, color="#94A3B8"),
                        ft.Text(get_text("need_approved_quotation_first"), size=11, color="#CBD5E1"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.Padding(left=30, right=30, top=30, bottom=30),
                    alignment=ft.Alignment(0, 0),
                )
            )
            return
        
        for job in self.approved_jobs:
            job_id = job.get('id')
            job_no = job.get('job_no', '-')
            customer_name = job.get('customer_name', '-')
            plate_number = job.get('plate_number', '-')
            
            result_item = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color),
                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                        border_radius=10,
                        padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                    ),
                    ft.Column([
                        ft.Text(job_no, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                        ft.Text(f"{customer_name} | {plate_number}", size=11, color="#64748B"),
                    ], spacing=2, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color="#94A3B8"),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                ink=True,
                on_click=lambda e, j=job: self.select_job_order(j),
            )
            self.job_results_list.controls.append(result_item)
    
    def _update_mechanic_list(self):
        self.mechanic_results_list.controls.clear()
        
        if not self.filtered_mechanics:
            self.mechanic_results_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_OFF, size=40, color="#CBD5E1"),
                        ft.Text(get_text("no_mechanics_found"), size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.Padding(left=30, right=30, top=30, bottom=30),
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for mechanic in self.filtered_mechanics[:20]:
                mech_id = mechanic.get('id')
                name = mechanic.get('fullname', mechanic.get('name', '-'))
                phone = mechanic.get('phone', '-')
                role = mechanic.get('role', '-')
                
                is_selected = self.selected_mechanic_id == mech_id
                
                item_card = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON, size=24, color=self.primary_color if is_selected else "#64748B"),
                            bgcolor=ft.Colors.with_opacity(0.1, self.primary_color) if is_selected else ft.Colors.GREY_100,
                            border_radius=12,
                            padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                        ),
                        ft.Column([
                            ft.Text(name, size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                            ft.Text(f"{phone}", size=11, color="#64748B"),
                        ], spacing=2, expand=True),
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if is_selected else ft.Icons.RADIO_BUTTON_UNCHECKED,
                            size=20,
                            color=self.success_color if is_selected else "#CBD5E1",
                        ),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=12, right=12, top=12, bottom=12),
                    bgcolor=ft.Colors.GREY_50 if is_selected else ft.Colors.WHITE,
                    border_radius=12,
                    border=ft.Border(top=ft.BorderSide(1, self.primary_color if is_selected else ft.Colors.GREY_200), right=ft.BorderSide(1, self.primary_color if is_selected else ft.Colors.GREY_200), bottom=ft.BorderSide(1, self.primary_color if is_selected else ft.Colors.GREY_200), left=ft.BorderSide(1, self.primary_color if is_selected else ft.Colors.GREY_200)),
                    ink=True,
                    on_click=lambda e, m=mechanic: self.select_mechanic(m),
                )
                self.mechanic_results_list.controls.append(item_card)
        
        self.page.update()
    
    def select_job_order(self, job: dict):
        self.selected_job = job
        
        job_no = job.get('job_no', '-')
        customer_name = job.get('customer_name', '-')
        plate_number = job.get('plate_number', '-')
        brand = job.get('brand', '-')
        model = job.get('model', '-')
        problem = job.get('problem_description', '-')
        
        self.selected_job_label.value = f"{job_no} - {customer_name} - {plate_number}"
        self.job_search_field.value = job_no
        self.job_results_container.visible = False
        self.selected_job_card.visible = True
        
        self._update_job_details_card(job_no, customer_name, plate_number, brand, model, problem)
        self.job_details_card.visible = True
        
        self.load_approved_quotation_items(job.get('id'))
        
        self.page.update()
    
    def _update_job_details_card(self, job_no, customer_name, plate_number, brand, model, problem):
        details_column = self.job_details_card.content.controls[3]
        
        details_column.controls[0].content.controls[1].value = job_no
        details_column.controls[1].content.controls[1].value = customer_name
        details_column.controls[2].content.controls[1].value = plate_number
        details_column.controls[3].content.controls[1].value = f"{brand} {model}"
        details_column.controls[4].content.controls[1].value = problem
    
    def load_approved_quotation_items(self, job_order_id: int):
        try:
            quotations = self.client.get_quotations(job_order_id=job_order_id) or []
            
            approved_quotation = None
            for q in quotations:
                if q.get('status') == 'approved':
                    approved_quotation = q
                    break
            
            if not approved_quotation:
                self.quotation_card.visible = False
                self.show_snack_bar(get_text("no_approved_quotation_found"), "error")
                return
            
            self.selected_quotation = approved_quotation
            
            quotation_id = approved_quotation.get('id')
            items = self.client.get_quotation_items(quotation_id) or []
            
            self.quotation_items = []
            for item in items:
                # Convert Decimal to float/int safely
                try:
                    unit_price = float(item.get('unit_price', 0))
                except (TypeError, ValueError):
                    unit_price = 0
                
                try:
                    total = float(item.get('total', 0))
                except (TypeError, ValueError):
                    total = unit_price * int(item.get('qty', 1))
                
                try:
                    qty = int(item.get('qty', 1))
                except (TypeError, ValueError):
                    qty = 1
                
                self.quotation_items.append({
                    'item_type': item.get('item_type'),
                    'name': item.get('name', '-'),
                    'qty': qty,
                    'unit_price': unit_price,
                    'total': total
                })
            
            self._update_items_table()
            self.quotation_card.visible = True
            
        except Exception as ex:
            print(f"Error loading quotation items: {ex}")
            self.quotation_card.visible = False
    
    def _update_items_table(self):
        self.items_table_body.controls.clear()
        
        if not self.quotation_items:
            self.items_table_body.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.REQUEST_QUOTE, size=32, color="#CBD5E1"),
                        ft.Text(get_text("no_items_in_quotation"), size=13, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    padding=ft.Padding(left=30, right=30, top=30, bottom=30),
                    alignment=ft.Alignment(0, 0),
                )
            )
            self.total_text.value = "0 KIP"
            self.page.update()
            return
        
        subtotal = 0.0
        for idx, item in enumerate(self.quotation_items):
            name = item.get('name', '-')
            qty = item.get('qty', 1)
            unit_price = item.get('unit_price', 0.0)
            total = item.get('total', 0.0)
            subtotal += total
            
            border_bottom = ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_50)) if idx < len(self.quotation_items) - 1 else None
            
            # Convert to int for display with commas
            unit_price_int = int(unit_price) if unit_price else 0
            total_int = int(total) if total else 0
            
            row = ft.Container(
                content=ft.Row([
                    ft.Text(f"{idx+1}", size=12, color="#64748B", width=35),
                    ft.Text(name, size=13, color="#1E293B", expand=True, max_lines=2),
                    ft.Text(f"x{qty}", size=13, color="#64748B", width=60, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"{unit_price_int:,}", size=13, color="#64748B", width=100, text_align=ft.TextAlign.RIGHT),
                    ft.Text(f"{total_int:,}", size=13, weight=ft.FontWeight.W_600, color=self.success_color, width=110, text_align=ft.TextAlign.RIGHT),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=0, right=0, top=8, bottom=8),
                border=border_bottom,
            )
            self.items_table_body.controls.append(row)
        
        # Discount row
        discount_amount = self.selected_quotation.get('discount_amount', 0) if self.selected_quotation else 0
        try:
            discount_amount = float(discount_amount)
        except (TypeError, ValueError):
            discount_amount = 0
        
        if discount_amount > 0:
            discount_int = int(discount_amount)
            discount_row = ft.Container(
                content=ft.Row([
                    ft.Container(expand=True),
                    ft.Text(get_text("discount") + ":", size=12, color="#64748B"),
                    ft.Text(f"-{discount_int:,} KIP", size=13, weight=ft.FontWeight.W_600, color=self.warning_color),
                ], spacing=12),
                padding=ft.Padding(left=0, right=0, top=8, bottom=8),
                bgcolor="#F8FAFC",
                border_radius=8,
                margin=ft.Margin(left=0, right=0, top=4, bottom=0),
            )
            self.items_table_body.controls.append(discount_row)
            subtotal -= discount_amount
        
        # Total row
        subtotal_int = int(subtotal) if subtotal else 0
        total_row = ft.Container(
            content=ft.Row([
                ft.Container(expand=True),
                ft.Text(get_text("total") + ":", size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                ft.Text(f"{subtotal_int:,} KIP", size=14, weight=ft.FontWeight.W_700, color=self.success_color),
            ], spacing=12),
            padding=ft.Padding(left=0, right=0, top=10, bottom=10),
            bgcolor="#F8FAFC",
            border_radius=8,
            margin=ft.Margin(left=0, right=0, top=4, bottom=0),
        )
        self.items_table_body.controls.append(total_row)
        
        self.total_text.value = f"{subtotal_int:,} KIP"
        self.page.update()
    
    def select_mechanic(self, mechanic: dict):
        self.selected_mechanic_id = mechanic.get('id')
        self.selected_mechanic_data = mechanic
        name = mechanic.get('fullname', mechanic.get('name', '-'))
        phone = mechanic.get('phone', '-')
        self.selected_mechanic_label.value = f"{name} - {phone}"
        self.selected_mechanic_card.visible = True
        self.mechanic_search_field.value = name
        self._update_mechanic_list()
        self.page.update()
    
    def clear_selected_mechanic(self):
        self.selected_mechanic_id = None
        self.selected_mechanic_data = None
        self.selected_mechanic_card.visible = False
        self.mechanic_search_field.value = ""
        self._update_mechanic_list()
        self.page.update()
    
    def clear_selected_job(self):
        self.selected_job = None
        self.selected_quotation = None
        self.quotation_items = []
        self.selected_job_card.visible = False
        self.job_details_card.visible = False
        self.quotation_card.visible = False
        self.job_search_field.value = ""
        self._update_job_list()
        self._update_items_table()
        self.page.update()
    
    # ==================== SEARCH HANDLERS ====================
    def on_search_job(self, e):
        query = self.job_search_field.value.lower() if self.job_search_field.value else ""
        self.job_clear_button.visible = bool(query)
        
        if not query:
            self.job_results_container.visible = False
            self.page.update()
            return
        
        filtered = [
            job for job in self.approved_jobs
            if query in job.get('job_no', '').lower()
            or query in job.get('customer_name', '').lower()
            or query in job.get('plate_number', '').lower()
        ]
        
        self.job_results_list.controls.clear()
        
        if not filtered:
            self.job_results_list.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_orders_found"), size=13, color="#94A3B8"),
                    padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for job in filtered[:10]:
                job_no = job.get('job_no', '-')
                customer_name = job.get('customer_name', '-')
                plate_number = job.get('plate_number', '-')
                
                result_item = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.RECEIPT, size=20, color=self.primary_color),
                            bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                            border_radius=10,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Column([
                            ft.Text(job_no, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                            ft.Text(f"{customer_name} | {plate_number}", size=11, color="#64748B"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color="#94A3B8"),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                    ink=True,
                    on_click=lambda e, j=job: self.select_job_order(j),
                )
                self.job_results_list.controls.append(result_item)
        
        self.job_results_container.visible = True
        self.page.update()
    
    def clear_job_search(self):
        self.job_search_field.value = ""
        self.job_clear_button.visible = False
        self.job_results_container.visible = False
        self.page.update()
    
    def on_search_mechanic(self, e):
        query = self.mechanic_search_field.value.lower() if self.mechanic_search_field.value else ""
        self.mechanic_clear_button.visible = bool(query)
        
        if not query:
            self.filtered_mechanics = self.mechanics.copy()
        else:
            self.filtered_mechanics = [
                m for m in self.mechanics
                if query in (m.get('fullname', m.get('name', '')).lower())
                or query in m.get('phone', '').lower()
            ]
        
        self._update_mechanic_list()
        self.page.update()
    
    def clear_mechanic_search(self):
        self.mechanic_search_field.value = ""
        self.mechanic_clear_button.visible = False
        self.filtered_mechanics = self.mechanics.copy()
        self._update_mechanic_list()
        self.page.update()
    
    # ==================== CREATE REPAIR ====================
    def create_repair_order(self, e):
        if not self.selected_job:
            self.show_snack_bar(get_text("please_select_job_order"), "error")
            return
        
        if not self.selected_mechanic_id:
            self.show_snack_bar(get_text("please_select_mechanic"), "error")
            return
        
        self.create_btn.disabled = True
        self.create_btn.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
        self.page.update()
        
        try:
            result = self.client.create_repair_order(
                self.selected_job.get('id'), 
                self.selected_mechanic_id
            )
            print(f"DEBUG: create_repair_order result = {result}")
            
            if result and result.get('id'):
                repair_id = result.get('id')
                
                try:
                    self.client.update_repair_status(repair_id, 'working')
                    print(f"DEBUG: Updated repair {repair_id} status to 'working'")
                except Exception as status_ex:
                    print(f"DEBUG: Error updating status: {status_ex}")
                
                self.show_success_popup(repair_id)
            else:
                self.create_btn.disabled = False
                self.create_btn.content.controls[0].name = ft.Icons.CONSTRUCTION
                self.show_snack_bar(get_text("create_repair_order_failed"), "error")
        except Exception as ex:
            error_msg = str(ex)
            print(f"DEBUG: Exception = {ex}")
            self.create_btn.disabled = False
            self.create_btn.content.controls[0].name = ft.Icons.CONSTRUCTION
            
            if "already exists" in error_msg.lower():
                self.show_snack_bar(get_text("repair_already_exists"), "error")
                self.navigate("repair_list")
            else:
                self.show_snack_bar(f"{get_text('error')}: {error_msg}", "error")
        
        self.page.update()
    
    # ==================== FIXED SUCCESS POPUP ====================
    def show_success_popup(self, repair_id):
        def go_to_detail(e):
            # Close and remove popup before navigating
            popup.open = False
            self.page.update()
            if popup in self.page.overlay:
                self.page.overlay.remove(popup)
            self.navigate("repair_detail", repair_id=repair_id)
        
        def go_to_list(e):
            # Close and remove popup before navigating
            popup.open = False
            self.page.update()
            if popup in self.page.overlay:
                self.page.overlay.remove(popup)
            self.navigate("repair_list")
        
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=28, color=ft.Colors.WHITE),
                            bgcolor=self.success_color,
                            border_radius=12,
                            padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                        ),
                        ft.Text(
                            get_text("success"),
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
                    ft.Container(height=8),
                    ft.Text(
                        get_text("repair_order_created_success"),
                        size=15,
                        weight=ft.FontWeight.W_500,
                        color="#1E293B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CONSTRUCTION, size=16, color=self.primary_color),
                            ft.Text(
                                f"{get_text('repair_number')}: R{repair_id:04d}",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=self.primary_color,
                            ),
                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.Padding(left=12, right=12, top=12, bottom=12),
                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                        border_radius=10,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                padding=ft.Padding(left=24, right=24, top=24, bottom=24),
                width=360,
                height=200,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.OutlinedButton(
                            get_text("back_to_list"),
                            on_click=go_to_list,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, self.primary_color),
                            ),
                        ),
                        ft.ElevatedButton(
                            get_text("go_to_repair_detail"),
                            on_click=go_to_detail,
                            style=ft.ButtonStyle(
                                bgcolor=self.primary_color,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.Padding(left=20, right=20, top=10, bottom=10),
                            ),
                        ),
                    ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
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