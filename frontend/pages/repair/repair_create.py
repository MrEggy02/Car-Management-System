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
        
        # Data storage
        self.pending_jobs = []
        self.selected_job_id = None
        self.selected_job_data = None
        self.mechanics = []
        
        # UI references
        self.job_dropdown = None
        self.job_info_container = None
        self.job_info_text = None
        self.mechanic_dropdown = None
        self.create_btn = None
        self.warning_text = None
        self.content_area = None
        self.loading_overlay = None
        
    def build(self):
        header = self._build_header()
        
        # Create main content area with loading
        self.content_area = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )
        
        main_content = ft.Container(
            content=ft.Column([header, self.content_area], expand=True),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Load data
        self.page.run_task(self._load_data)
        
        return main_content
    
    def _build_header(self):
        return ft.Container(
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
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("repair_create_subtitle"),
                                size=12,
                                color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=14, horizontal=24),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
    
    async def _load_data(self):
        """Load pending jobs and mechanics"""
        await asyncio.sleep(0.2)
        self.load_mechanics()
        self.load_pending_jobs()
    
    def load_pending_jobs(self):
        """Load job orders that are ready for repair"""
        try:
            # Get approved quotations first
            all_quotations = self.client.get_quotations()
            approved_job_ids = set()
            for q in all_quotations:
                if q.get('status') == 'approved':
                    job_id = q.get('job_order_id')
                    if job_id:
                        approved_job_ids.add(job_id)
            
            if not approved_job_ids:
                self._build_no_jobs_ui()
                return
            
            # Get job orders that are approved
            all_jobs = self.client.get_job_orders()
            self.pending_jobs = []
            
            for job in all_jobs:
                if job.get('id') in approved_job_ids:
                    # Check if repair already exists
                    try:
                        existing_repairs = self.client.get_repair_orders(job_order_id=job.get('id'))
                        if not existing_repairs:
                            self.pending_jobs.append(job)
                    except:
                        self.pending_jobs.append(job)
            
            if self.job_order_id:
                # If specific job ID provided, select it
                for job in self.pending_jobs:
                    if job.get('id') == self.job_order_id:
                        self.selected_job_id = self.job_order_id
                        self.selected_job_data = job
                        self._build_create_form()
                        return
            
            # Build selection UI
            self._build_selection_ui()
            
        except Exception as ex:
            print(f"Error loading pending jobs: {ex}")
            self._show_error(str(ex))
    
    def _build_no_jobs_ui(self):
        """Show message when no jobs available"""
        no_jobs_card = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=ft.Colors.GREY_400),
                ft.Text("ບໍ່ມີໃບຮັບລົດທີ່ພ້ອມສ້ອມແປງ", size=16, color="#64748B", text_align=ft.TextAlign.CENTER),
                ft.Text("ກະລຸນາອະນຸມັດໃບສະເໜີລາຄາກ່ອນ", size=12, color="#94A3B8", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            padding=ft.padding.all(40),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        self.content_area.content = no_jobs_card
        self.page.update()
    
    def _build_selection_ui(self):
        """Build UI for selecting job order"""
        
        # Job dropdown
        self.job_dropdown = ft.Dropdown(
            label=get_text("select_job_order"),
            hint_text=get_text("select_job_order_for_repair"),
            border_radius=12,
            bgcolor=ft.Colors.GREY_100,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            options=[],
            expand=True,
        )
        self.job_dropdown.on_change = self.on_job_select
        
        # Populate dropdown
        for job in self.pending_jobs:
            self.job_dropdown.options.append(
                ft.dropdown.Option(
                    str(job.get('id')),
                    f"{job.get('job_no')} - {job.get('customer_name')} - {job.get('plate_number')}"
                )
            )
        
        # Job info container
        self.job_info_text = ft.Text("", size=13, color="#1E293B")
        self.job_info_container = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=self.primary_color),
                        ft.Text(get_text("selected_job"), size=12, weight=ft.FontWeight.W_500, color="#64748B"),
                    ],
                    spacing=4,
                ),
                ft.Container(height=4),
                self.job_info_text,
            ]),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            visible=False,
        )
        
        # Selection card
        selection_card = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CONSTRUCTION, size=20, color=self.primary_color),
                        ft.Text("ເລືອກໃບຮັບລົດ", size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=12),
                self.job_dropdown,
                ft.Container(height=10),
                self.job_info_container,
            ]),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        # Update content area
        self.content_area.content = selection_card
        self.page.update()
    
    def on_job_select(self, e):
        """Handle job selection"""
        if self.job_dropdown.value:
            self.selected_job_id = int(self.job_dropdown.value)
            for job in self.pending_jobs:
                if job.get('id') == self.selected_job_id:
                    self.selected_job_data = job
                    self.job_info_text.value = f"{job.get('job_no')} - {job.get('customer_name')} - {job.get('plate_number')}"
                    self.job_info_container.visible = True
                    break
            
            # Build create form
            self._build_create_form()
        else:
            self.selected_job_id = None
            self.job_info_container.visible = False
        self.page.update()
    
    def load_mechanics(self):
        try:
            self.mechanics = self.client.get_mechanics()
            print(f"DEBUG: Loaded {len(self.mechanics)} mechanics")
        except Exception as ex:
            print(f"Error loading mechanics: {ex}")
            self.mechanics = []
    
    def _build_create_form(self):
        """Build the create repair form"""
        
        # Show loading
        self.content_area.content = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=50, height=50),
                ft.Text(get_text("loading"), size=16, color="#64748B"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )
        self.page.update()
        
        # Check if repair already exists
        existing_repair = self.check_existing_repair()
        
        # Job Info Card
        job_info_card = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.RECEIPT, size=18, color=self.primary_color),
                            bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                            border_radius=10,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(get_text("job_order_info"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=12),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("job_number"), size=11, color="#64748B"),
                        ft.Text(self.selected_job_data.get("job_no", "-"), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ], expand=True),
                    ft.Column([
                        ft.Text(get_text("customer_name"), size=11, color="#64748B"),
                        ft.Text(self.selected_job_data.get("customer_name", "-"), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ], expand=True),
                    ft.Column([
                        ft.Text(get_text("plate_number"), size=11, color="#64748B"),
                        ft.Text(self.selected_job_data.get("plate_number", "-"), size=14, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ], expand=True),
                ]),
                ft.Container(height=12),
                ft.Text(get_text("problem_description"), size=11, color="#64748B"),
                ft.Container(
                    content=ft.Text(self.selected_job_data.get("problem_description", "-"), 
                                   size=13, color="#1E293B"),
                    padding=ft.padding.all(12),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                ),
            ]),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        # Select Mechanic Card
        self.mechanic_dropdown = ft.Dropdown(
            label=get_text("select_mechanic"),
            hint_text=get_text("select_mechanic_hint"),
            options=[],
            expand=True,
            border_radius=12,
            bgcolor=ft.Colors.GREY_100,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        # Update dropdown options
        for mechanic in self.mechanics:
            mechanic_name = mechanic.get('name', '')
            mechanic_phone = mechanic.get('phone', '')
            display = mechanic_name if not mechanic_phone else f"{mechanic_name} - {mechanic_phone}"
            self.mechanic_dropdown.options.append(
                ft.dropdown.Option(str(mechanic.get('id')), display)
            )
        
        mechanic_card = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON, size=18, color=self.primary_color),
                            bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                            border_radius=10,
                            padding=ft.padding.all(8),
                        ),
                        ft.Text(get_text("assign_mechanic"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=12),
                self.mechanic_dropdown,
            ]),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
        )
        
        # Warning message if repair already exists
        self.warning_text = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING, size=16, color=ft.Colors.ORANGE_600),
                ft.Text("", size=12, color=ft.Colors.ORANGE_600),
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ORANGE_600),
            border_radius=8,
            visible=False,
        )
        
        # Create Button
        self.create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CONSTRUCTION, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("create_repair_order_btn"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
            ], spacing=8),
            on_click=self.create_repair_order,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=2,
                padding=ft.padding.symmetric(horizontal=28, vertical=12),
            ),
        )
        
        # If repair already exists, disable form
        if existing_repair:
            self.warning_text.content.controls[1].value = get_text("repair_already_exists_warning").replace("{repair_id}", str(existing_repair))
            self.warning_text.visible = True
            self.create_btn.disabled = True
            self.create_btn.style = ft.ButtonStyle(
                bgcolor=ft.Colors.GREY_400,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=28, vertical=12),
            )
            self.mechanic_dropdown.disabled = True
        
        scrollable_content = ft.Column(
            [
                job_info_card,
                ft.Container(height=16),
                mechanic_card,
                ft.Container(height=16),
                self.warning_text,
                ft.Container(height=20),
                ft.Container(
                    content=self.create_btn,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(height=20),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        self.content_area.content = scrollable_content
        self.page.update()
    
    def check_existing_repair(self):
        """Check if repair order already exists for this job"""
        try:
            repair_orders = self.client.get_repair_orders(job_order_id=self.selected_job_id)
            if repair_orders and len(repair_orders) > 0:
                return repair_orders[0].get('id')
            return None
        except:
            return None
    
    def create_repair_order(self, e):
        # Validate
        if not self.mechanic_dropdown.value:
            self.show_snack_bar(get_text("please_select_mechanic"), is_error=True)
            return
        
        selected_mechanic_id = int(self.mechanic_dropdown.value)
        
        # Show loading
        self.create_btn.disabled = True
        self.create_btn.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
        self.page.update()
        
        try:
            result = self.client.create_repair_order(self.selected_job_id, selected_mechanic_id)
            print(f"DEBUG: create_repair_order result = {result}")
            
            if result and result.get('id'):
                self.repair_id = result.get('id')
                self.show_success_popup()
            else:
                self.create_btn.disabled = False
                self.create_btn.content.controls[0].name = ft.Icons.CONSTRUCTION
                self.show_snack_bar(get_text("create_repair_order_failed"), is_error=True)
        except Exception as ex:
            error_msg = str(ex)
            print(f"DEBUG: Exception = {ex}")
            self.create_btn.disabled = False
            self.create_btn.content.controls[0].name = ft.Icons.CONSTRUCTION
            
            if "already exists" in error_msg.lower():
                self.show_snack_bar(get_text("repair_already_exists"), is_error=True)
                self.navigate("repair_list")
            else:
                self.show_snack_bar(f"{get_text('error')}: {error_msg}", is_error=True)
        
        self.page.update()
    
    def show_success_popup(self):
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
                            padding=ft.padding.all(8),
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
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
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
                                f"{get_text('repair_number')}: R{self.repair_id:04d}",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=self.primary_color,
                            ),
                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.padding.all(12),
                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                        border_radius=10,
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        get_text("go_to_repair_list_message"),
                        size=12,
                        color="#64748B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                padding=ft.padding.all(24),
                width=360,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            get_text("go_to_repair_list"),
                            on_click=lambda e: self._close_popup_and_go(popup),
                            style=ft.ButtonStyle(
                                bgcolor=self.primary_color,
                                color=ft.Colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=24, vertical=10),
                            ),
                        ),
                        ft.Container(expand=True),
                    ]),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def _close_popup_and_go(self, popup):
        popup.open = False
        self.navigate("repair_list")
    
    def _show_error(self, message):
        """Show error message"""
        error_content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400),
                ft.Text(f"{get_text('error')}: {message}", size=14, color=ft.Colors.RED_600),
                ft.ElevatedButton(
                    content=ft.Text(get_text("retry")),
                    on_click=lambda e: self.load_pending_jobs(),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )
        self.content_area.content = error_content
        self.page.update()
    
    def show_snack_bar(self, message: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, size=13),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
            duration=3000,
        )
        self.page.update()