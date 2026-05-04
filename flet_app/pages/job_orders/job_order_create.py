# pages/job_orders/job_order_create.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable

from i18n import get_text


class JobOrderCreateContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.selected_customer = None
        self.selected_vehicle = None
        self.selected_vehicle_id = None
        self.customers = []
        self.vehicles = []
        self.search_field = None
        self.customers_list = None
        self.vehicle_dropdown = None
        self.customer_info_card = None
        self.customer_name_text = None
        self.customer_phone_text = None
        self.details_section = None
        self.problem_description = None
        self.mileage = None
        self.fuel_level = None
        self.status_text = None
        
    def build(self):
        # Beautiful gradient header
        header = ft.Container(
            content=ft.Row(
                [
                    
                    ft.Column(
                        [
                            ft.Text(
                                get_text("job_order_create"),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("register_customer_subtitle"),
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
        
        # Search customer section
        self.search_field = ft.TextField(
            hint_text=get_text("search_customer_by_name_or_phone"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            on_change=self.on_search_change,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.customers_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        
        search_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.SEARCH, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                get_text("search_customer"),
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
                    self.search_field,
                    ft.Container(height=16),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(get_text("select_customer"), size=14, weight=ft.FontWeight.W_500, color="#64748B"),
                            ft.Container(height=8),
                            self.customers_list,
                        ]),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=12,
                        padding=ft.padding.all(16),
                    ),
                ]),
                padding=ft.padding.all(24),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Create text widgets for customer info that we can update
        self.customer_name_text = ft.Text("", size=15, weight=ft.FontWeight.BOLD)
        self.customer_phone_text = ft.Text("", size=12, color="#64748B")
        
        # Selected customer info card
        self.customer_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.PERSON, size=18, color=ft.Colors.GREEN_700),
                                bgcolor="#E8F5E9",
                                border_radius=10,
                                padding=ft.padding.all(6),
                            ),
                            ft.Text(
                                get_text("selected_customer"),
                                size=14,
                                weight=ft.FontWeight.W_500,
                                color="#1E293B",
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=16,
                                tooltip=get_text("change_customer"),
                                on_click=self.clear_selected_customer,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=8),
                    self.customer_name_text,
                    self.customer_phone_text,
                ]),
                padding=ft.padding.all(16),
            ),
            elevation=1,
            margin=ft.margin.only(bottom=20),
            visible=False,
        )
        
        # Create vehicle selection dropdown with click handler
        self.vehicle_dropdown = ft.Dropdown(
            label=get_text("select_vehicle"),
            hint_text=get_text("select_vehicle_to_continue"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[],
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        # Problem details section
        self.problem_description = ft.TextField(
            label=get_text("problem_description"),
            hint_text=get_text("problem_description_hint"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.DESCRIPTION,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            multiline=True,
            min_lines=4,
            max_lines=6,
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.mileage = ft.TextField(
            label=get_text("mileage"),
            hint_text="0",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SPEED,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.fuel_level = ft.Dropdown(
            label=get_text("fuel_level"),
            hint_text=get_text("select_fuel_level"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option("full", "ເຕັມຖັງ (Full)"),
                ft.dropdown.Option("3/4", "3/4 ຖັງ"),
                ft.dropdown.Option("1/2", "1/2 ຖັງ"),
                ft.dropdown.Option("1/4", "1/4 ຖັງ"),
                ft.dropdown.Option("empty", "ໃກ້ໝົດ (Empty)"),
            ],
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.details_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.CAR_REPAIR, size=20, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                get_text("vehicle_problem_details"),
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
                    self.vehicle_dropdown,
                    ft.Container(height=12),
                    self.problem_description,
                    ft.Container(height=12),
                    ft.Row([self.mileage, self.fuel_level], spacing=16),
                ]),
                padding=ft.padding.all(24),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
            visible=False,
        )
        
        # Add change handler to dropdown after creation
        self.vehicle_dropdown.on_change = self.on_vehicle_select
        
        # Status message
        self.status_text = ft.Text("", size=13, visible=False)
        
        # Action buttons
        def create_job_order(e):
            print(f"DEBUG: Selected customer: {self.selected_customer}")
            print(f"DEBUG: Selected vehicle ID: {self.selected_vehicle_id}")
            print(f"DEBUG: Selected vehicle object: {self.selected_vehicle}")
            print(f"DEBUG: Dropdown value: {self.vehicle_dropdown.value}")
            
            if not self.selected_customer:
                self.show_status(get_text("select_customer_first"), is_error=True)
                return
            
            # Get vehicle ID from dropdown value directly
            vehicle_id = None
            if self.vehicle_dropdown.value and self.vehicle_dropdown.value != "new":
                try:
                    vehicle_id = int(self.vehicle_dropdown.value)
                except:
                    pass
            
            if not vehicle_id and self.selected_vehicle_id:
                vehicle_id = self.selected_vehicle_id
            if not vehicle_id and self.selected_vehicle:
                vehicle_id = self.selected_vehicle.get("id")
            
            if not vehicle_id:
                self.show_status(get_text("select_vehicle_first"), is_error=True)
                return
            
            if not self.problem_description.value:
                self.problem_description.error_text = get_text("required_field")
                self.page.update()
                return
            
            self.problem_description.error_text = None
            self.page.update()
            
            # Show loading
            create_btn.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
            create_btn.disabled = True
            self.page.update()
            
            try:
                print(f"DEBUG: Creating job order with customer_id={self.selected_customer['id']}, vehicle_id={vehicle_id}")
                
                result = self.client.create_job_order(
                    customer_id=self.selected_customer["id"],
                    vehicle_id=vehicle_id,
                    problem_description=self.problem_description.value,
                    mileage=int(self.mileage.value) if self.mileage.value else 0,
                    fuel_level=self.fuel_level.value if self.fuel_level.value else "",
                )
                
                print(f"DEBUG: Result: {result}")
                
                if result:
                    self.show_success_popup(result.get("job_no", "N/A"))
            except Exception as ex:
                print(f"DEBUG: Error: {ex}")
                self.show_status(f"Error: {str(ex)}", is_error=True)
            finally:
                create_btn.content.controls[0].name = ft.Icons.SAVE
                create_btn.disabled = False
                self.page.update()
        
        def cancel(e):
            self.navigate("dashboard")
        
        cancel_btn = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
                ft.Text(get_text("cancel"), size=14, color="#64748B"),
            ], spacing=6),
            on_click=cancel,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
        )
        
        create_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("create_job_order"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=create_job_order,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=2,
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
            ),
        )
        
        action_buttons = ft.Container(
            content=ft.Row([cancel_btn, create_btn], alignment=ft.MainAxisAlignment.END, spacing=12),
            padding=ft.padding.only(top=20),
        )
        
        # Scrollable content
        scrollable_content = ft.Column(
            [
                search_section,
                self.customer_info_card,
                self.details_section,
                action_buttons,
                self.status_text,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.padding.all(32),
            bgcolor="#F5F7FA",
        )
        
        # Main layout
        main_content = ft.Container(
            content=ft.Column([
                header,
                content_area,
            ]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        return main_content
    
    def show_status(self, message: str, is_error: bool = False):
        self.status_text.value = message
        self.status_text.color = ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600
        self.status_text.visible = True
        self.page.update()
    
    def show_success_popup(self, job_no: str):
        """Show success popup with job number"""
        
        def go_to_list(e):
            popup.open = False
            self.navigate("job_order_list")
        
        popup = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.Colors.WHITE,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN_600),
                            alignment=Alignment.CENTER,
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            get_text("job_order_created"),
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            f"{get_text('job_number')}: {job_no}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=self.primary_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            get_text("print_receipt_question"),
                            size=13,
                            color="#64748B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                width=400,
                padding=ft.padding.all(24),
            ),
            actions=[
                ft.TextButton(
                    get_text("later"),
                    on_click=lambda e: self.close_popup_and_go_to_list(popup),
                ),
                ft.ElevatedButton(
                    get_text("print_now"),
                    on_click=lambda e: self.print_job_order(popup, job_no),
                    style=ft.ButtonStyle(bgcolor=self.primary_color, color=ft.Colors.WHITE),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def close_popup_and_go_to_list(self, popup):
        popup.open = False
        self.navigate("job_order_list")
    
    def print_job_order(self, popup, job_no):
        popup.open = False
        self.navigate("job_order_print", order_id=job_no)
    
    def clear_selected_customer(self, e):
        self.selected_customer = None
        self.selected_vehicle = None
        self.selected_vehicle_id = None
        self.customer_info_card.visible = False
        self.details_section.visible = False
        self.vehicle_dropdown.options = []
        self.vehicle_dropdown.value = None
        self.problem_description.value = ""
        self.mileage.value = ""
        self.fuel_level.value = None
        self.page.update()
    
    def on_search_change(self, e):
        keyword = e.control.value if hasattr(e, 'control') else e
        self.search_customers(keyword)
    
    def search_customers(self, keyword: str = ""):
        try:
            customers = self.client.get_customers()
            
            if keyword:
                customers = [
                    c for c in customers
                    if keyword.lower() in c.get("name", "").lower()
                    or keyword.lower() in c.get("phone", "").lower()
                ]
            
            self.customers_list.controls.clear()
            
            for customer in customers:
                self.customers_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(customer.get("name", "-"), weight=ft.FontWeight.W_500, size=14),
                                ft.Text(customer.get("phone", "-"), size=12, color="#64748B"),
                            ], expand=True),
                            ft.IconButton(
                                icon=ft.Icons.ARROW_FORWARD,
                                icon_size=20,
                                icon_color=self.primary_color,
                                on_click=lambda e, c=customer: self.select_customer(c),
                                tooltip=get_text("select"),
                            ),
                        ]),
                        padding=ft.padding.symmetric(vertical=12, horizontal=16),
                        border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                        on_click=lambda e, c=customer: self.select_customer(c),
                    )
                )
            
            self.page.update()
            
        except Exception as ex:
            print(f"Error searching customers: {ex}")
    
    def select_customer(self, customer: Dict):
        self.selected_customer = customer
        # Update the text widgets directly
        self.customer_name_text.value = customer.get("name", "")
        self.customer_phone_text.value = customer.get("phone", "")
        self.customer_info_card.visible = True
        
        # Reset vehicle selection
        self.selected_vehicle = None
        self.selected_vehicle_id = None
        
        # Load vehicles for this customer
        self.load_vehicles(customer["id"])
        
        self.search_field.value = ""
        self.customers_list.controls.clear()
        self.details_section.visible = True
        self.page.update()
    
    def load_vehicles(self, customer_id: int):
        try:
            vehicles = self.client.get_vehicles(customer_id=customer_id)
            self.vehicles = vehicles
            
            print(f"DEBUG: Loaded {len(vehicles)} vehicles for customer {customer_id}")
            
            options = []
            for vehicle in vehicles:
                option_text = f"{vehicle.get('plate_number', 'N/A')} - {vehicle.get('brand', '')} {vehicle.get('model', '')}"
                options.append(
                    ft.dropdown.Option(
                        str(vehicle["id"]),
                        option_text
                    )
                )
                print(f"DEBUG: Added vehicle option: ID={vehicle['id']}, Text={option_text}")
            
            # Add option to add new vehicle
            options.append(
                ft.dropdown.Option("new", f"+ {get_text('add_new_vehicle')}")
            )
            
            self.vehicle_dropdown.options = options
            self.vehicle_dropdown.value = None
            self.page.update()
            
        except Exception as ex:
            print(f"Error loading vehicles: {ex}")
    
    def on_vehicle_select(self, e):
        """Handle vehicle selection from dropdown"""
        selected_value = e.control.value
        print(f"DEBUG: Dropdown selected value: {selected_value}")
        
        if selected_value == "new":
            self.show_add_vehicle_dialog()
            self.vehicle_dropdown.value = None
        elif selected_value:
            try:
                vehicle_id = int(selected_value)
                print(f"DEBUG: Looking for vehicle with ID: {vehicle_id}")
                
                # Store the vehicle ID directly from dropdown
                self.selected_vehicle_id = vehicle_id
                self.selected_vehicle = None
                
                # Find the vehicle for display
                for v in self.vehicles:
                    if v["id"] == vehicle_id:
                        self.selected_vehicle = v
                        break
                
                print(f"DEBUG: Selected vehicle ID stored: {self.selected_vehicle_id}")
                print(f"DEBUG: Selected vehicle object: {self.selected_vehicle}")
                
                # Show success message
                if self.selected_vehicle:
                    self.status_text.value = f"✅ {get_text('vehicle_selected')}: {self.selected_vehicle.get('plate_number')}"
                else:
                    self.status_text.value = f"✅ {get_text('vehicle_selected')}: ID {vehicle_id}"
                self.status_text.color = ft.Colors.GREEN_600
                self.status_text.visible = True
                self.page.update()
                
                # Hide status after 2 seconds
                import asyncio
                async def hide_status():
                    await asyncio.sleep(2)
                    self.status_text.visible = False
                    self.page.update()
                self.page.run_task(hide_status)
                
            except ValueError as ex:
                print(f"DEBUG: Error parsing vehicle ID: {ex}")
                self.selected_vehicle_id = None
                self.selected_vehicle = None
    
    def show_add_vehicle_dialog(self):
        plate_number = ft.TextField(label=get_text("plate_number"))
        brand = ft.TextField(label=get_text("car_brand"))
        model = ft.TextField(label=get_text("car_model"))
        year = ft.TextField(label=get_text("car_year"), input_filter=ft.NumbersOnlyInputFilter(), max_length=4)
        color = ft.TextField(label=get_text("car_color"))
        
        def add_vehicle(e):
            if not plate_number.value:
                plate_number.error_text = get_text("required_field")
                self.page.update()
                return
            
            vehicle_data = {
                "customer_id": self.selected_customer["id"],
                "plate_number": plate_number.value.upper(),
                "brand": brand.value,
                "model": model.value,
                "year": int(year.value) if year.value else 0,
                "color": color.value,
            }
            
            try:
                result = self.client.add_vehicle(vehicle_data)
                if result:
                    dialog.open = False
                    self.load_vehicles(self.selected_customer["id"])
                    self.show_status(get_text("vehicle_added_successfully"), is_error=False)
            except Exception as ex:
                self.show_status(f"Error: {str(ex)}", is_error=True)
        
        dialog = ft.AlertDialog(
            title=ft.Text(get_text("add_new_vehicle")),
            content=ft.Container(
                content=ft.Column([
                    plate_number,
                    ft.Container(height=8),
                    brand,
                    ft.Container(height=8),
                    model,
                    ft.Container(height=8),
                    year,
                    ft.Container(height=8),
                    color,
                ], spacing=0),
                width=400,
                padding=ft.padding.all(20),
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("add"), on_click=add_vehicle),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()