# pages/repair/repair_create.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable, List

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
        self.job_order_data = None
        self.repair_id = None
        self.mechanics = []
        self.selected_mechanic_id = None
        self.selected_job_id = None
        self.selected_job_no = None
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.success_color = "#10B981"
        self.jobs_list = None
        self.search_field = None
        self.job_list = []
        
    def build(self):
        header = self._build_header()
        
        if not self.job_order_id:
            content = self._build_selection_content()
        else:
            content = self._build_create_content()
        
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
                                get_text("repair_management"),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("repair_create_subtitle"),
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=20, horizontal=32),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
            
        )
    
    def _build_selection_content(self):
        # Search field
        self.search_field = ft.TextField(
            hint_text=get_text("search_job_order"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            on_change=self.search_jobs,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.jobs_list = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)
        
        selection_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.CONSTRUCTION, size=24, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=12,
                                padding=ft.padding.all(10),
                            ),
                            ft.Text(
                                get_text("select_job_for_repair"),
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
                    self.search_field,
                    ft.Container(height=16),
                    ft.Text(
                        get_text("approved_jobs"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color="#64748B",
                    ),
                    ft.Container(height=12),
                    ft.Container(
                        content=self.jobs_list,
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
        
        self.load_approved_jobs()
        
        return content_area
    
    def _build_create_content(self):
        self.load_job_order()
        self.load_mechanics()
        
        # Check if repair order already exists
        existing_repair = self.check_existing_repair()
        
        # Job Info Card
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
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Select Mechanic
        self.mechanic_dropdown = ft.Dropdown(
            label=get_text("select_mechanic"),
            hint_text=get_text("select_mechanic_hint"),
            options=[],
            expand=True,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
        )
        
        # Create Button
        self.create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CONSTRUCTION, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("create_repair_order_btn"), size=16, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            on_click=self.create_repair_order,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=3,
                padding=ft.padding.symmetric(horizontal=32, vertical=16),
            ),
            width=280,
            height=50,
        )
        
        # Warning message if repair already exists
        self.warning_text = ft.Text(
            "",
            size=13,
            visible=False,
            color=ft.Colors.ORANGE_600,
        )
        
        mechanic_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.PERSON, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                get_text("assign_mechanic"),
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
                    ft.Row([self.mechanic_dropdown], spacing=12),
                ]),
                padding=ft.padding.all(20),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # If repair already exists, show message and disable create button
        if existing_repair:
            self.warning_text.value = get_text("repair_already_exists_warning").format(repair_id=existing_repair)
            self.warning_text.visible = True
            self.warning_text.color = ft.Colors.ORANGE_600
            self.create_btn.disabled = True
            self.create_btn.style = ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_400,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=32, vertical=16),
            )
            self.mechanic_dropdown.disabled = True
        
        scrollable_content = ft.Column(
            [
                job_info_card,
                mechanic_card,
                self.warning_text,
                ft.Container(
                    content=self.create_btn,
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.only(top=20),
                ),
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
        
        # Load dropdown
        self.update_mechanic_dropdown()
        
        return content_area
    
    def check_existing_repair(self):
        """Check if repair order already exists for this job"""
        try:
            repair_orders = self.client.get_repair_orders(job_order_id=self.selected_job_id)
            if repair_orders and len(repair_orders) > 0:
                return repair_orders[0].get('id')
            return None
        except:
            return None
    
    def load_approved_jobs(self):
        try:
            all_quotations = self.client.get_quotations()
            approved_job_ids = set()
            for q in all_quotations:
                if q.get('status') == 'approved':
                    job_id = q.get('job_order_id')
                    if job_id:
                        approved_job_ids.add(job_id)
            
            if not approved_job_ids:
                self.display_jobs([])
                return
            
            all_jobs = self.client.get_job_orders()
            approved_jobs = []
            for job in all_jobs:
                if job.get('id') in approved_job_ids:
                    # Also check if repair already exists
                    try:
                        existing_repairs = self.client.get_repair_orders(job_order_id=job.get('id'))
                        has_repair = existing_repairs and len(existing_repairs) > 0
                        job['has_repair'] = has_repair
                    except:
                        job['has_repair'] = False
                    approved_jobs.append(job)
            
            self.job_list = approved_jobs
            self.display_jobs(approved_jobs)
            
        except Exception as ex:
            print(f"Error loading jobs: {ex}")
            self.display_jobs([])
    
    def display_jobs(self, jobs):
        self.jobs_list.controls.clear()
        
        if not jobs:
            self.jobs_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=ft.Colors.GREY_400),
                        ft.Text(get_text("no_approved_jobs"), size=14, color="#64748B"),
                        ft.Text(get_text("approve_quotation_first"), size=12, color="#94A3B8"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(40),
                )
            )
        else:
            for job in jobs:
                job_id = job.get('id')
                job_no = job.get('job_no', 'N/A')
                customer_name = job.get('customer_name', '-')
                plate_number = job.get('plate_number', '-')
                has_repair = job.get('has_repair', False)
                
                # Create job card
                icon_container = ft.Container(
                    content=ft.Icon(ft.Icons.CONSTRUCTION, size=28, color=self.primary_color),
                    width=50,
                    height=50,
                    bgcolor="#E3F2FD",
                    border_radius=12,
                )
                
                info_column = ft.Column([
                    ft.Text(job_no, size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ft.Text(customer_name, size=13, color="#64748B"),
                    ft.Text(plate_number, size=12, color="#94A3B8"),
                ], spacing=4, expand=True)
                
                # Show different button if repair already exists
                if has_repair:
                    select_button = ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ft.Colors.GREEN_600),
                            ft.Text(get_text("already_created"), size=12, color=ft.Colors.GREEN_600),
                        ], spacing=4),
                        padding=ft.padding.symmetric(horizontal=15, vertical=8),
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=10,
                    )
                else:
                    select_button = ft.ElevatedButton(
                        get_text("select"),
                        on_click=lambda e, jid=job_id, jno=job_no: self.select_job(jid, jno),
                        style=ft.ButtonStyle(
                            bgcolor=self.primary_color,
                            color=ft.Colors.WHITE,
                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    )
                
                job_card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            icon_container,
                            info_column,
                            select_button,
                        ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.padding.all(15),
                    ),
                    elevation=2,
                    margin=ft.margin.only(bottom=10),
                )
                self.jobs_list.controls.append(job_card)
        
        self.page.update()
    
    def search_jobs(self, e):
        keyword = self.search_field.value.lower() if self.search_field else ""
        if keyword:
            filtered_jobs = []
            for job in self.job_list:
                job_no = job.get('job_no', '').lower()
                customer_name = job.get('customer_name', '').lower()
                plate_number = job.get('plate_number', '').lower()
                if keyword in job_no or keyword in customer_name or keyword in plate_number:
                    filtered_jobs.append(job)
            self.display_jobs(filtered_jobs)
        else:
            self.display_jobs(self.job_list)
    
    def select_job(self, job_id: int, job_no: str):
        self.selected_job_id = job_id
        self.selected_job_no = job_no
        self.job_order_id = job_id
        
        # Go to create form
        new_content = self._build_create_content()
        
        if self.content_container:
            self.content_container.content = new_content
            self.content_container.update()
        else:
            if self.page.controls and len(self.page.controls) > 0:
                main_container = self.page.controls[0]
                if isinstance(main_container, ft.Container) and isinstance(main_container.content, ft.Column):
                    if len(main_container.content.controls) >= 2:
                        content_holder = main_container.content.controls[1]
                        if isinstance(content_holder, ft.Container):
                            content_holder.content = new_content
                            content_holder.update()
                        else:
                            self.page.controls.clear()
                            self.page.add(self.build())
                            self.page.update()
                    else:
                        self.page.controls.clear()
                        self.page.add(self.build())
                        self.page.update()
                else:
                    self.page.controls.clear()
                    self.page.add(self.build())
                    self.page.update()
            else:
                self.page.controls.clear()
                self.page.add(self.build())
                self.page.update()
    
    def load_job_order(self):
        try:
            self.job_order_data = self.client.get_job_order(self.selected_job_id)
            self.page.update()
        except Exception as ex:
            print(f"Error loading job order: {ex}")
    
    def load_mechanics(self):
        try:
            self.mechanics = self.client.get_mechanics()
            print(f"DEBUG: Loaded {len(self.mechanics)} mechanics")
        except Exception as ex:
            print(f"Error loading mechanics: {ex}")
            self.mechanics = []
    
    def update_mechanic_dropdown(self):
        options = []
        options.append(ft.dropdown.Option("", get_text("select_mechanic_placeholder")))
        for mechanic in self.mechanics:
            options.append(
                ft.dropdown.Option(
                    str(mechanic.get('id')),
                    f"{mechanic.get('fullname', '')} - {mechanic.get('phone', '')}"
                )
            )
        self.mechanic_dropdown.options = options
        self.page.update()
    
    def create_repair_order(self, e):
        # Validate
        if not self.mechanic_dropdown.value or self.mechanic_dropdown.value == "":
            self.show_snack_bar(get_text("please_select_mechanic"), is_error=True)
            return
        
        selected_mechanic_id = int(self.mechanic_dropdown.value)
        
        # Show loading
        self.create_btn.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
        self.create_btn.disabled = True
        self.page.update()
        
        try:
            result = self.client.create_repair_order(self.selected_job_id, selected_mechanic_id)
            print(f"DEBUG: create_repair_order result = {result}")
            
            if result and result.get('id'):
                self.repair_id = result.get('id')
                self.show_success_popup()
            else:
                self.create_btn.content.controls[0].name = ft.Icons.CONSTRUCTION
                self.create_btn.disabled = False
                self.show_snack_bar(get_text("create_repair_order_failed"), is_error=True)
        except Exception as ex:
            error_msg = str(ex)
            print(f"DEBUG: Exception = {ex}")
            self.create_btn.content.controls[0].name = ft.Icons.CONSTRUCTION
            self.create_btn.disabled = False
            
            if "already exists" in error_msg.lower():
                self.show_snack_bar(get_text("repair_already_exists"), is_error=True)
                # Go back to job list
                self.go_back(None)
            else:
                self.show_snack_bar(f"{get_text('error')}: {error_msg}", is_error=True)
        
        self.page.update()
    
    def show_success_popup(self):
        """แสดง popup เมื่อสร้าง Repair Order สำเร็จ"""
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.Colors.WHITE,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN_600),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            get_text("repair_order_created_success"),
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            f"{get_text('repair_number')}: R{self.repair_id:04d}",
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=self.primary_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            get_text("go_to_repair_list_message"),
                            size=13,
                            color="#64748B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                width=380,
                padding=ft.padding.all(24),
            ),
            actions=[
                ft.ElevatedButton(
                    get_text("go_to_repair_list"),
                    on_click=lambda e: self.go_to_repair_list(popup),
                    style=ft.ButtonStyle(
                        bgcolor=self.primary_color,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def go_to_repair_list(self, popup):
        popup.open = False
        self.navigate("repair_list")
    
    def go_back(self, e):
        try:
            self.navigate("repair_create")
        except Exception as ex:
            print(f"Error navigating back: {ex}")
            self.navigate("repair_create")
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()