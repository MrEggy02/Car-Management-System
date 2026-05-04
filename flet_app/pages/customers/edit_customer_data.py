# pages/customers/edit_customer_data.py
import asyncio

import flet as ft
from flet import Alignment
from typing import Dict, Callable, Optional

from i18n import get_text


class EditCustomerDataContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, 
                 customer_id: int = None):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.customer_id = customer_id
        self.selected_customer = None
        self.selected_vehicles = []
        self.selected_vehicle_id = None
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
    def build(self):
        # Beautiful gradient header with back button
        header = ft.Container(
            content=ft.Row(
                [
                    
                    ft.Column(
                        [
                            ft.Text(
                                get_text("edit_customer_data"), 
                                size=24, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.WHITE
                            ),
                            ft.Text(
                                get_text("edit_customer_data"),
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
        
        # Customer edit form card (visible directly when customer_id is provided)
        self.customer_name = ft.TextField(
            label=get_text("customer_name"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.customer_phone = ft.TextField(
            label=get_text("customer_phone"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.PHONE_OUTLINED,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.customer_address = ft.TextField(
            label=get_text("customer_address"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            multiline=True,
            min_lines=2,
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        # Vehicle selection dropdown
        self.vehicle_dropdown = ft.Dropdown(
            label=get_text("select_vehicle"),
            hint_text=get_text("select_vehicle_to_edit"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[],
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        # Vehicle edit fields
        self.plate_number = ft.TextField(
            label=get_text("plate_number"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CONFIRMATION_NUMBER,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.brand = ft.TextField(
            label=get_text("car_brand"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CAR_RENTAL,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.model = ft.TextField(
            label=get_text("car_model"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.DIRECTIONS_CAR,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.year = ft.TextField(
            label=get_text("car_year"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=4,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.color = ft.TextField(
            label=get_text("car_color"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.COLOR_LENS,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        edit_form_card = ft.Card(
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
                                get_text("edit_customer_information"), 
                                size=16, 
                                weight=ft.FontWeight.BOLD, 
                                color="#1E293B"
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=16),
                    ft.Row([self.customer_name, self.customer_phone], spacing=16),
                    ft.Container(height=16),
                    self.customer_address,
                    ft.Container(height=24),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.DIRECTIONS_CAR, size=18, color=self.primary_color),
                                bgcolor="#E3F2FD",
                                border_radius=8,
                                padding=ft.padding.all(6),
                            ),
                            ft.Text(
                                get_text("edit_vehicle_information"), 
                                size=15, 
                                weight=ft.FontWeight.BOLD, 
                                color="#1E293B"
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=16),
                    self.vehicle_dropdown,
                    ft.Container(height=16),
                    ft.Row([self.plate_number, self.brand, self.model], spacing=16),
                    ft.Container(height=16),
                    ft.Row([self.year, self.color], spacing=16),
                ]),
                padding=ft.padding.all(24),
            ),
            elevation=3,
            margin=ft.margin.only(bottom=20),
        )
        
        self.status_text = ft.Text("", size=13, visible=False)
        
        def on_vehicle_select(e):
            """Handle vehicle selection from dropdown"""
            if self.vehicle_dropdown.value:
                self.selected_vehicle_id = int(self.vehicle_dropdown.value)
                vehicle = next((v for v in self.selected_vehicles if v["id"] == self.selected_vehicle_id), None)
                if vehicle:
                    self.load_vehicle_data(vehicle)
        
        # Add change handler to dropdown
        self.vehicle_dropdown.on_change = on_vehicle_select
        
        def save_changes(e):
            if not self.selected_customer:
                self.status_text.value = get_text("no_customer_selected")
                self.status_text.color = ft.Colors.RED_600
                self.status_text.visible = True
                self.page.update()
                return
            
            # Update customer
            customer_update = {
                "name": self.customer_name.value,
                "phone": self.customer_phone.value,
                "address": self.customer_address.value,
            }
            
            # Show loading state
            save_btn.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
            save_btn.disabled = True
            self.page.update()
            
            try:
                # Update customer
                self.client.update_customer(self.selected_customer["id"], customer_update)
                
                # Update vehicle if selected
                if self.selected_vehicle_id:
                    vehicle_update = {
                        "plate_number": self.plate_number.value.upper(),
                        "brand": self.brand.value,
                        "model": self.model.value,
                        "year": int(self.year.value) if self.year.value else 0,
                        "color": self.color.value,
                    }
                    self.client.update_vehicle(self.selected_vehicle_id, vehicle_update)
                
                self.status_text.value = get_text("update_successful")
                self.status_text.color = ft.Colors.GREEN_600
                self.status_text.visible = True
                self.page.update()
                
                # Refresh data after 1 second
                self.page.run_task(self._refresh_data)
                
            except Exception as ex:
                self.status_text.value = f"Error: {str(ex)}"
                self.status_text.color = ft.Colors.RED_600
                self.status_text.visible = True
                self.page.update()
            finally:
                save_btn.content.controls[0].name = ft.Icons.SAVE
                save_btn.disabled = False
                self.page.update()
        
        async def _refresh_data():
            await asyncio.sleep(1)
            self.load_customer_data(self.selected_customer["id"])
        
        def add_new_vehicle(e):
            if not self.selected_customer:
                self.status_text.value = get_text("no_customer_selected")
                self.status_text.color = ft.Colors.RED_600
                self.status_text.visible = True
                self.page.update()
                return
            
            self.show_add_vehicle_dialog()
        
        def delete_vehicle(e):
            if not self.selected_vehicle_id:
                self.status_text.value = get_text("no_vehicle_selected")
                self.status_text.color = ft.Colors.RED_600
                self.status_text.visible = True
                self.page.update()
                return
            
            self.show_delete_vehicle_dialog()
        
        save_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("save_changes"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=save_changes,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=2,
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
            ),
        )
        
        action_buttons = ft.Container(
            content=ft.Row([
                ft.OutlinedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=18, color=self.primary_color),
                        ft.Text(get_text("add_new_vehicle"), size=14, color=self.primary_color),
                    ], spacing=6),
                    on_click=add_new_vehicle,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        side=ft.BorderSide(1, self.primary_color),
                    ),
                ),
                ft.OutlinedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DELETE_OUTLINE, size=18, color=ft.Colors.RED_600),
                        ft.Text(get_text("delete_vehicle"), size=14, color=ft.Colors.RED_600),
                    ], spacing=6),
                    on_click=delete_vehicle,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        side=ft.BorderSide(1, ft.Colors.RED_600),
                    ),
                ),
                save_btn,
            ], alignment=ft.MainAxisAlignment.END, spacing=12),
            padding=ft.padding.only(top=24),
        )
        
        edit_section = ft.Column([edit_form_card, action_buttons, self.status_text], spacing=16)
        
        # Scrollable content
        scrollable_content = ft.Column(
            [edit_section],
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
        
        # If customer_id is provided, load directly
        if self.customer_id:
            self.load_customer_data(self.customer_id)
        
        return main_content
    
    def load_customer_data(self, customer_id: int):
        try:
            customers = self.client.get_customers()
            self.selected_customer = next((c for c in customers if c["id"] == customer_id), None)
            
            if self.selected_customer:
                self.customer_name.value = self.selected_customer.get("name", "")
                self.customer_phone.value = self.selected_customer.get("phone", "")
                self.customer_address.value = self.selected_customer.get("address", "")
                
                # Load vehicles
                self.selected_vehicles = self.client.get_vehicles(customer_id=customer_id)
                
                # Update dropdown
                options = []
                for vehicle in self.selected_vehicles:
                    options.append(
                        ft.dropdown.Option(
                            str(vehicle["id"]), 
                            f"{vehicle.get('plate_number', 'N/A')} - {vehicle.get('brand', '')} {vehicle.get('model', '')}"
                        )
                    )
                self.vehicle_dropdown.options = options
                
                if self.selected_vehicles:
                    self.vehicle_dropdown.value = str(self.selected_vehicles[0]["id"])
                    self.selected_vehicle_id = self.selected_vehicles[0]["id"]
                    self.load_vehicle_data(self.selected_vehicles[0])
                else:
                    self.vehicle_dropdown.value = None
                    self.selected_vehicle_id = None
                    self.clear_vehicle_data()
                
                self.page.update()
                
        except Exception as ex:
            self.status_text.value = f"Error loading customer: {str(ex)}"
            self.status_text.color = ft.Colors.RED_600
            self.status_text.visible = True
            self.page.update()
    
    def load_vehicle_data(self, vehicle: Dict):
        self.plate_number.value = vehicle.get("plate_number", "")
        self.brand.value = vehicle.get("brand", "")
        self.model.value = vehicle.get("model", "")
        self.year.value = str(vehicle.get("year", "")) if vehicle.get("year") else ""
        self.color.value = vehicle.get("color", "")
        self.page.update()
    
    def clear_vehicle_data(self):
        self.plate_number.value = ""
        self.brand.value = ""
        self.model.value = ""
        self.year.value = ""
        self.color.value = ""
        self.page.update()
    
    def show_add_vehicle_dialog(self):
        plate_number = ft.TextField(label=get_text("plate_number"), expand=True)
        brand = ft.TextField(label=get_text("car_brand"), expand=True)
        model = ft.TextField(label=get_text("car_model"), expand=True)
        year = ft.TextField(label=get_text("car_year"), input_filter=ft.NumbersOnlyInputFilter(), max_length=4, expand=True)
        color = ft.TextField(label=get_text("car_color"), expand=True)
        
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
                width=450,
                padding=ft.padding.all(20),
            ),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(get_text("add"), on_click=lambda e: self.add_vehicle(dialog, plate_number, brand, model, year, color)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def add_vehicle(self, dialog, plate_number, brand, model, year, color):
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
                self.page.update()
                self.load_customer_data(self.selected_customer["id"])
                self.status_text.value = get_text("vehicle_added_successfully")
                self.status_text.color = ft.Colors.GREEN_600
                self.status_text.visible = True
                self.page.update()
        except Exception as ex:
            self.status_text.value = f"Error: {str(ex)}"
            self.status_text.color = ft.Colors.RED_600
            self.status_text.visible = True
            self.page.update()
    
    def show_delete_vehicle_dialog(self):
        dialog = ft.AlertDialog(
            title=ft.Text(get_text("confirm_delete_vehicle")),
            content=ft.Text(get_text("delete_vehicle_warning")),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton(
                    get_text("delete"), 
                    on_click=lambda e: self.delete_vehicle(dialog),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def delete_vehicle(self, dialog):
        try:
            self.client.delete_vehicle(self.selected_vehicle_id)
            dialog.open = False
            self.page.update()
            self.load_customer_data(self.selected_customer["id"])
            self.status_text.value = get_text("vehicle_deleted_successfully")
            self.status_text.color = ft.Colors.GREEN_600
            self.status_text.visible = True
            self.page.update()
        except Exception as ex:
            self.status_text.value = f"Error: {str(ex)}"
            self.status_text.color = ft.Colors.RED_600
            self.status_text.visible = True
            self.page.update()