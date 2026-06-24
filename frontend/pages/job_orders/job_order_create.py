import flet as ft
from flet import Alignment
from typing import Dict, Callable
from datetime import datetime
import asyncio
import functools
import os

from i18n import get_text


class JobOrderCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
        # Data storage
        self.customers = []
        self.filtered_customers = []
        self.vehicles_list = []
        self.selected_customer_id = None
        self.selected_customer_name = None
        self.selected_vehicle_id = None
        
        # UI references
        self.customer_search_field = None
        self.customer_clear_button = None
        self.customer_info_text = None
        self.customer_info_container = None
        self.customer_results = None
        self.customer_results_container = None
        self.vehicles_container = None
        self.vehicles_card = None
        self.vehicle_radio_group = None
        self.problem_description = None
        self.mileage = None
        self.fuel_level = None
        self.car_defects = None
        self.selected_image_path = None
        self.image_preview = None
        self.image_preview_container = None
        self.file_picker = None
        
    def build(self):
        # Setup file picker
        def on_file_picked(e):
            if e.files:
                self.selected_image_path = e.files[0].path
                self.image_preview.value = os.path.basename(self.selected_image_path)
                self.image_preview_container.visible = True
                self.page.update()
                
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = on_file_picked
        if self.file_picker not in self.page.overlay:
            self.page.overlay.append(self.file_picker)
            self.page.update()
            
        # --- Header with Back Button on Left ---
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ARROW_BACK, size=18, color=ft.Colors.WHITE),
                            ],
                            spacing=6,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=8, vertical=8),
                        on_click=lambda e: self.navigate("job_order_list"),
                        ink=True,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                get_text("new_job_order"),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Container(expand=True),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                                        ft.Text(get_text("create"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
                                    ],
                                    spacing=8,
                                ),
                                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                                border_radius=30,
                                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                                on_click=self.create_job_order,
                                ink=True,
                            ),
                        ],
                        spacing=12,
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
        
        # ==================== LEFT COLUMN: CUSTOMER & VEHICLE ====================
        
        # Search field for customers
        self.customer_search_field = ft.TextField(
            label=get_text("search_customer"),
            hint_text=get_text("search_customer_by_name_or_phone"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            on_change=self.on_search_customer,
            border_color=ft.Colors.GREY_200,
        )
        
        # Clear button for customer search
        self.customer_clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=18,
            icon_color=ft.Colors.GREY_500,
            on_click=lambda e: self.clear_customer_search(),
            visible=False,
        )
        
        # Search row with clear button
        search_row = ft.Row(
            [self.customer_search_field, self.customer_clear_button],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Customer results container
        self.customer_results = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=200)
        self.customer_results_container = ft.Container(
            content=self.customer_results,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=12,
            padding=ft.padding.all(8),
            bgcolor=ft.Colors.WHITE,
            visible=False,
        )
        
        # Customer info after selection
        self.customer_info_text = ft.Text("", size=13, color="#1E293B")
        self.customer_info_container = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.PERSON, size=16, color=self.primary_color),
                        ft.Text(get_text("selected_customer"), size=13, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=6,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                self.customer_info_text,
                ft.Row([
                    ft.Container(
                        content=ft.Text(get_text("change_customer"), size=12, color=self.primary_color),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                        border_radius=16,
                        on_click=lambda e: self.change_customer(),
                        ink=True,
                    ),
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=0),
            padding=ft.padding.all(10),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            visible=False,
        )
        
        # Vehicles container (Radio buttons)
        self.vehicles_container = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, height=120)
        self.vehicles_card = ft.Container(
            content=ft.Column([
                ft.Row(
                    [
                        ft.Icon(ft.Icons.DIRECTIONS_CAR, size=18, color=self.primary_color),
                        ft.Text(get_text("select_vehicle"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=8),
                self.vehicles_container,
            ]),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            visible=False,
        )
        
        # Left Column Content
        left_column = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON_SEARCH, size=20, color=self.primary_color),
                            ft.Text(get_text("customer_vehicle_info"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=12),
                    
                    # Customer Section
                    ft.Text(get_text("customer_information"), size=14, weight=ft.FontWeight.W_600, color="#475569"),
                    ft.Container(height=8),
                    search_row,
                    ft.Container(height=8),
                    self.customer_results_container,
                    ft.Container(height=8),
                    self.customer_info_container,
                    ft.Container(height=16),
                    
                    # Vehicle Section
                    self.vehicles_card,
                ],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=450,
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
        )
        
        # ==================== RIGHT COLUMN: PROBLEM DETAILS ====================
        
        # Problem description
        self.problem_description = ft.TextField(
            label=get_text("problem_description"),
            hint_text=get_text("problem_description_hint"),
            multiline=True,
            min_lines=6,
            max_lines=8,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
        )
        
        self.car_defects = ft.TextField(
            label=get_text("car_defects"),
            hint_text=get_text("car_defects_hint"),
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
        )
        
        self.selected_image_path = None
        self.image_preview = ft.Text("", size=12, color="#475569", expand=True)
        self.image_preview_container = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.IMAGE, size=16, color=self.primary_color),
                self.image_preview,
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_size=16,
                    icon_color=ft.Colors.RED_400,
                    on_click=lambda e: self.clear_selected_image(),
                )
            ], spacing=6),
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            visible=False,
        )
        
        upload_button = ft.OutlinedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.UPLOAD_FILE, size=18, color=self.primary_color),
                    ft.Text(get_text("upload_signed_receipt"), size=14, color=self.primary_color),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=lambda e: self.page.run_task(
                self.file_picker.pick_files,
                allow_multiple=False,
                file_type=ft.FilePickerFileType.IMAGE,
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, self.primary_color),
            ),
        )
        
        self.mileage = ft.TextField(
            label=get_text("mileage"),
            hint_text="0",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        
        self.fuel_level = ft.Dropdown(
            label=get_text("fuel_level"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            options=[
                ft.dropdown.Option("full", get_text("fuel_full")),
                ft.dropdown.Option("3/4", get_text("fuel_3_4")),
                ft.dropdown.Option("1/2", get_text("fuel_1_2")),
                ft.dropdown.Option("1/4", get_text("fuel_1_4")),
                ft.dropdown.Option("empty", get_text("fuel_empty")),
            ],
            expand=True,
        )
        
        # Right Column Content
        right_column = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.BUILD, size=20, color=self.primary_color),
                            ft.Text(get_text("problem_details"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=12),
                    
                    # Vehicle Details
                    ft.Text(get_text("vehicle_information"), size=14, weight=ft.FontWeight.W_600, color="#475569"),
                    ft.Container(height=8),
                    ft.Row([self.mileage, self.fuel_level], spacing=12),
                    ft.Container(height=16),
                    
                    # Problem Description
                    ft.Text(get_text("problem_description"), size=14, weight=ft.FontWeight.W_600, color="#475569"),
                    ft.Container(height=8),
                    self.problem_description,
                    ft.Container(height=16),
                    
                    # Vehicle Defects
                    ft.Text(get_text("car_defects"), size=14, weight=ft.FontWeight.W_600, color="#475569"),
                    ft.Container(height=8),
                    self.car_defects,
                    ft.Container(height=16),
                    
                    # Signed Receipt Image
                    ft.Text(get_text("signed_receipt_image"), size=14, weight=ft.FontWeight.W_600, color="#475569"),
                    ft.Container(height=8),
                    ft.Row([upload_button], alignment=ft.MainAxisAlignment.START),
                    ft.Container(height=8),
                    self.image_preview_container,
                ],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=450,
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
        )
        
        # Two Columns Row
        two_columns_row = ft.Row(
            [
                left_column,
                ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),
                right_column,
            ],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )
        
        # Main Card
        big_card = ft.Container(
            content=two_columns_row,
            padding=ft.padding.symmetric(horizontal=24, vertical=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            expand=True,
        )
        
        # Main scrollable content
        scrollable_content = ft.Column(
            [
                big_card,
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.padding.all(20),
            bgcolor="#F0F2F5",
        )
        
        main_content = ft.Container(
            content=ft.Column(
                [
                    header,
                    content_area,
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
        
        # Load data after UI is built
        self.page.run_task(self._load_data_async)
        
        return main_content
    
    async def _load_data_async(self):
        """Load data asynchronously"""
        await asyncio.sleep(0.3)
        self.load_customers()
    
    def load_customers(self):
        """Load all customers"""
        try:
            self.customers = self.client.get_customers() or []
            print(f"Loaded {len(self.customers)} customers")
        except Exception as ex:
            print(f"Error loading customers: {ex}")
            self.customers = []
    
    def on_search_customer(self, e):
        """Search customers by name or phone"""
        query = self.customer_search_field.value.lower() if self.customer_search_field.value else ""
        
        # Show/hide clear button
        self.customer_clear_button.visible = bool(query)
        
        if not query:
            self.customer_results_container.visible = False
            self.page.update()
            return
        
        print(f"DEBUG: Searching for '{query}' in {len(self.customers)} customers")
        
        self.filtered_customers = [
            c for c in self.customers
            if query in c.get('name', '').lower()
            or query in c.get('phone', '').lower()
        ]
        
        print(f"DEBUG: Found {len(self.filtered_customers)} customers")
        
        self.customer_results.controls.clear()
        
        if not self.filtered_customers:
            self.customer_results.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_customers_found"), size=13, color="#94A3B8"),
                    padding=ft.padding.all(20),
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for customer in self.filtered_customers[:10]:
                cust_id = customer.get('id')
                cust_name = customer.get('name', '-')
                cust_phone = customer.get('phone', '-')
                
                result_item = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON, size=20, color=self.primary_color),
                            bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                            border_radius=10,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column([
                            ft.Text(cust_name, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                            ft.Text(cust_phone, size=11, color="#64748B"),
                        ], spacing=2, expand=True),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color="#94A3B8"),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(10),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    ink=True,
                    on_click=lambda e, cid=cust_id, cname=cust_name, cphone=cust_phone: self.select_customer(cid, cname, cphone),
                )
                self.customer_results.controls.append(result_item)
        
        self.customer_results_container.visible = True
        self.page.update()
    
    def clear_customer_search(self):
        self.customer_search_field.value = ""
        self.customer_clear_button.visible = False
        self.customer_results_container.visible = False
        self.page.update()
    
    def change_customer(self):
        """Clear selected customer and allow searching again"""
        self.selected_customer_id = None
        self.selected_customer_name = None
        self.selected_vehicle_id = None
        self.customer_info_container.visible = False
        self.vehicles_card.visible = False
        self.customer_search_field.value = ""
        self.customer_search_field.read_only = False
        self.customer_clear_button.visible = False
        self.customer_results_container.visible = False
        self.page.update()
    
    def select_customer(self, customer_id, customer_name, customer_phone):
        """Select a customer and load their vehicles"""
        self.selected_customer_id = customer_id
        self.selected_customer_name = customer_name
        
        # Update customer info
        self.customer_info_text.value = f"{customer_name} - {customer_phone}"
        self.customer_info_container.visible = True
        
        # Hide search results and clear button
        self.customer_results_container.visible = False
        self.customer_clear_button.visible = False
        self.customer_search_field.value = customer_name
        self.customer_search_field.read_only = True
        
        # Load vehicles for this customer
        self.load_vehicles_for_customer(customer_id)
        
        self.page.update()
    
    def load_vehicles_for_customer(self, customer_id):
        """Load vehicles for selected customer and display as radio buttons"""
        try:
            print(f"DEBUG: Loading vehicles for customer_id={customer_id}")
            
            vehicles = self.client.get_vehicles(customer_id=customer_id) or []
            self.vehicles_list = vehicles
            
            print(f"DEBUG: Found {len(vehicles)} vehicles")
            for v in vehicles:
                print(f"DEBUG: Vehicle - id={v.get('id')}, plate={v.get('plate_number')}, brand={v.get('brand_name')}, model={v.get('model')}")
            
            self.vehicles_container.controls.clear()
            
            if not vehicles:
                self.vehicles_container.controls.append(
                    ft.Container(
                        content=ft.Text(get_text("no_vehicles_registered"), size=13, color="#94A3B8"),
                        padding=ft.padding.all(20),
                        alignment=ft.Alignment(0, 0),
                    )
                )
            else:
                # Create radio group for vehicles
                self.vehicle_radio_group = ft.RadioGroup(
                    content=ft.Column(spacing=8),
                    on_change=self.on_vehicle_select,
                )
                
                radio_column = self.vehicle_radio_group.content
                radio_column.controls.clear()
                
                for v in vehicles:
                    vehicle_id = v.get('id')
                    plate = v.get('plate_number', '-')
                    brand = v.get('brand_name', '')
                    model = v.get('model', '')
                    
                    display_text = plate
                    if brand:
                        display_text += f" - {brand}"
                    if model and model != '-':
                        display_text += f" {model}"
                    
                    print(f"DEBUG: Adding radio for vehicle: {display_text}")
                    
                    radio = ft.Radio(
                        value=str(vehicle_id),
                        label=display_text,
                    )
                    radio_column.controls.append(radio)
                
                self.vehicles_container.controls.append(self.vehicle_radio_group)
            
            # Show vehicles card
            self.vehicles_card.visible = True
            self.page.update()
            
        except Exception as e:
            print(f"Error loading vehicles: {e}")
            import traceback
            traceback.print_exc()
            self.vehicles_container.controls.clear()
            self.vehicles_container.controls.append(
                ft.Container(
                    content=ft.Text(f"{get_text('error')}: {str(e)}", size=13, color=ft.Colors.RED_400),
                    padding=ft.padding.all(20),
                )
            )
            self.vehicles_card.visible = True
            self.page.update()
    
    def on_vehicle_select(self, e):
        """Handle vehicle selection from radio button"""
        if e and e.data:
            self.selected_vehicle_id = int(e.data)
            print(f"Selected vehicle ID: {self.selected_vehicle_id}")
        else:
            print("No vehicle selected")
        self.page.update()
    
    def create_job_order(self, e=None):
        """Create job order"""
        if not self.selected_customer_id:
            self.show_snackbar(get_text("select_customer_first"), True)
            return
        if not self.selected_vehicle_id:
            self.show_snackbar(get_text("select_vehicle_first"), True)
            return
        if not self.problem_description.value:
            self.show_snackbar(get_text("required_field"), True)
            return
        
        print(f"DEBUG: Creating job order - customer_id={self.selected_customer_id}, vehicle_id={self.selected_vehicle_id}")
        
        try:
            result = self.client.create_job_order(
                customer_id=self.selected_customer_id,
                vehicle_id=self.selected_vehicle_id,
                problem_description=self.problem_description.value,
                mileage=int(self.mileage.value) if self.mileage.value and self.mileage.value.isdigit() else 0,
                fuel_level=self.fuel_level.value if self.fuel_level.value else "",
                car_defects=self.car_defects.value if self.car_defects.value else "",
                signed_receipt_image_path=self.selected_image_path,
            )
            
            if result:
                job_no = result.get('job_no', '')
                self.show_snackbar(f"✅ {get_text('job_order_created')}: {job_no}", False)
                self.navigate("job_order_list")
            else:
                self.show_snackbar(get_text("create_failed"), True)
        except Exception as ex:
            print(f"ERROR: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {ex}", True)
    
    def clear_selected_image(self):
        self.selected_image_path = None
        self.image_preview.value = ""
        self.image_preview_container.visible = False
        self.page.update()
        
    def show_snackbar(self, msg, is_error=False):
        """Show snackbar message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, size=13),
            bgcolor="#EF4444" if is_error else "#10B981",
            open=True,
            duration=3000,
        )
        self.page.update()