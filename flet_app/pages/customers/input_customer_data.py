# pages/customers/input_customer_data.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable

from i18n import get_text


class InputCustomerDataContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_light = "#E3F2FD"
        self.success_color = "#10B981"
        
    def build(self):
        # Header with gradient background
        header = ft.Container(
            content=ft.Row(
                [
                    
                    ft.Column(
                        [
                            ft.Text(
                                get_text("input_customer_data"), 
                                size=24, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.WHITE
                            ),
                            ft.Text(
                                get_text("job_order_list_subtitle"),
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
                colors=[self.primary_color, "#0D47A1"],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
           
        )
        
        # Customer Information Card
        customer_name = ft.TextField(
            label=get_text("customer_name"),
            hint_text=get_text("customer_name_hint"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            focused_bgcolor=ft.Colors.WHITE,
            text_size=14,
        )
        
        customer_phone = ft.TextField(
            label=get_text("customer_phone"),
            hint_text=get_text("customer_phone_hint"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.PHONE_OUTLINED,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            text_size=14,
        )
        
        customer_address = ft.TextField(
            label=get_text("customer_address"),
            hint_text=get_text("customer_address_hint"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            text_size=14,
        )
        
        customer_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.PEOPLE, size=20, color=self.primary_color),
                                bgcolor=self.primary_light,
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                get_text("customer_information"), 
                                size=18, 
                                weight=ft.FontWeight.BOLD, 
                                color="#1E293B"
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=8),
                    ft.Row([customer_name, customer_phone], spacing=16),
                    ft.Container(height=12),
                    ft.Row([customer_address], spacing=16),
                ]),
                padding=ft.padding.all(24),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Vehicle Information Card
        plate_number = ft.TextField(
            label=get_text("plate_number"),
            hint_text="ກຂ 1234",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CONFIRMATION_NUMBER,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            text_size=14,
        )
        
        brand = ft.TextField(
            label=get_text("car_brand"),
            hint_text="Toyota, Honda, etc.",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.CAR_RENTAL,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            text_size=14,
        )
        
        model = ft.TextField(
            label=get_text("car_model"),
            hint_text="Corolla, Civic, etc.",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.DIRECTIONS_CAR,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            text_size=14,
        )
        
        year = ft.TextField(
            label=get_text("car_year"),
            hint_text="2020",
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
            text_size=14,
        )
        
        color = ft.TextField(
            label=get_text("car_color"),
            hint_text="Red, Blue, etc.",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.COLOR_LENS,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            expand=True,
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            text_size=14,
        )
        
        vehicle_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.DIRECTIONS_CAR, size=20, color=self.primary_color),
                                bgcolor=self.primary_light,
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                get_text("vehicle_information"), 
                                size=18, 
                                weight=ft.FontWeight.BOLD, 
                                color="#1E293B"
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=8),
                    ft.Row([plate_number, brand, model], spacing=16),
                    ft.Container(height=12),
                    ft.Row([year, color], spacing=16),
                ]),
                padding=ft.padding.all(24),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=20),
        )
        
        # Status message
        status_text = ft.Text("", size=13, visible=False)
        
        def show_success_popup(customer_name, plate_number):
            """Show success popup with animation"""
            
            # Create animated success popup
            popup = ft.AlertDialog(
                modal=True,
                shape=ft.RoundedRectangleBorder(radius=20),
                bgcolor=ft.Colors.WHITE,
                content=ft.Container(
                    content=ft.Column(
                        [
                            # Animated success icon
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.CHECK_CIRCLE, 
                                    size=64, 
                                    color=self.success_color
                                ),
                                animate=ft.animation.Animation(500, ft.AnimationCurve.BOUNCE_OUT),
                                padding=ft.padding.all(20),
                            ),
                            ft.Text(
                                get_text("save_successful"),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=8),
                            ft.Text(
                                get_text("customer_registered_successfully"),
                                size=14,
                                color="#64748B",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=16),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            f"{get_text('customer_name')}: {customer_name}",
                                            size=14,
                                            weight=ft.FontWeight.W_500,
                                            color="#1E293B",
                                        ),
                                        ft.Text(
                                            f"{get_text('plate_number')}: {plate_number}",
                                            size=14,
                                            weight=ft.FontWeight.W_500,
                                            color="#1E293B",
                                        ),
                                    ],
                                    spacing=8,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                padding=ft.padding.all(16),
                                bgcolor=ft.Colors.GREY_50,
                                border_radius=12,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    width=400,
                    padding=ft.padding.all(24),
                ),
                actions=[
                    ft.ElevatedButton(
                        content=ft.Text(get_text("ok"), size=14, color=ft.Colors.WHITE),
                        on_click=lambda e: close_popup_and_continue(),
                        style=ft.ButtonStyle(
                            bgcolor=self.primary_color,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.symmetric(horizontal=30, vertical=12),
                        ),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.CENTER,
            )
            
            def close_popup_and_continue():
                popup.open = False
                self.page.update()
                # Navigate to customer list
                self.navigate("customer_list")
            
            self.page.overlay.append(popup)
            popup.open = True
            self.page.update()
        
        # Action Buttons
        def save_and_continue(e):
            # Validate required fields
            errors = False
            if not customer_name.value:
                customer_name.error_text = get_text("required_field")
                errors = True
            else:
                customer_name.error_text = None
                
            if not customer_phone.value:
                customer_phone.error_text = get_text("required_field")
                errors = True
            else:
                customer_phone.error_text = None
                
            if not plate_number.value:
                plate_number.error_text = get_text("required_field")
                errors = True
            else:
                plate_number.error_text = None
            
            self.page.update()
            
            if errors:
                return
            
            # Check if phone already exists
            try:
                existing_customers = self.client.get_customers()
                for customer in existing_customers:
                    if customer.get("phone") == customer_phone.value:
                        # Show error popup for duplicate
                        error_popup = ft.AlertDialog(
                            modal=True,
                            shape=ft.RoundedRectangleBorder(radius=20),
                            bgcolor=ft.Colors.WHITE,
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.Icons.WARNING_AMBER, size=64, color=ft.Colors.ORANGE_600),
                                        ft.Text(
                                            get_text("phone_already_exists"),
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color="#1E293B",
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Container(height=8),
                                        ft.Text(
                                            f"{get_text('customer_phone')}: {customer_phone.value}",
                                            size=14,
                                            color="#64748B",
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Text(
                                            get_text("existing_customer_name"),
                                            size=14,
                                            color="#64748B",
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                        ft.Text(
                                            customer.get("name", "-"),
                                            size=14,
                                            weight=ft.FontWeight.W_500,
                                            color=self.primary_color,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=0,
                                ),
                                width=350,
                                padding=ft.padding.all(24),
                            ),
                            actions=[
                                ft.TextButton(
                                    get_text("cancel"),
                                    on_click=lambda e: close_error_popup(),
                                ),
                                ft.ElevatedButton(
                                    get_text("edit_customer"),
                                    on_click=lambda e: go_to_edit(customer["id"]),
                                    style=ft.ButtonStyle(
                                        bgcolor=self.primary_color,
                                        shape=ft.RoundedRectangleBorder(radius=10),
                                    ),
                                ),
                            ],
                            actions_alignment=ft.MainAxisAlignment.END,
                        )
                        
                        def close_error_popup():
                            error_popup.open = False
                            self.page.update()
                        
                        def go_to_edit(customer_id):
                            error_popup.open = False
                            from pages.customers.edit_customer_data import EditCustomerDataContent
                            edit_content = EditCustomerDataContent(
                                self.page, 
                                self.client, 
                                self.user, 
                                self.navigate,
                                customer_id=customer_id
                            )
                            parent = self.page.controls[0] if self.page.controls else None
                            if parent:
                                parent.content = edit_content.build()
                            self.page.update()
                        
                        self.page.overlay.append(error_popup)
                        error_popup.open = True
                        self.page.update()
                        return
            except:
                pass
            
            # Prepare customer data
            customer_data = {
                "name": customer_name.value,
                "phone": customer_phone.value,
                "address": customer_address.value,
            }
            
            # Prepare vehicle data
            vehicle_data = {
                "plate_number": plate_number.value.upper(),
                "brand": brand.value,
                "model": model.value,
                "year": int(year.value) if year.value else 0,
                "color": color.value,
            }
            
            # Show loading state
            save_btn.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
            save_btn.disabled = True
            self.page.update()
            
            try:
                result = self.client.register_customer_with_vehicle(customer_data, vehicle_data)
                
                if result:
                    # Show success popup instead of navigating directly
                    show_success_popup(customer_name.value, plate_number.value.upper())
                else:
                    status_text.value = get_text("save_failed")
                    status_text.color = ft.Colors.RED_600
                    status_text.visible = True
                    self.page.update()
                    
            except Exception as ex:
                error_msg = str(ex)
                if "Duplicate entry" in error_msg and "phone" in error_msg:
                    status_text.value = get_text("phone_already_exists")
                else:
                    status_text.value = f"Error: {error_msg}"
                status_text.color = ft.Colors.RED_600
                status_text.visible = True
                self.page.update()
            finally:
                save_btn.content.controls[0].name = ft.Icons.SAVE
                save_btn.disabled = False
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
        
        save_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                ft.Text(get_text("save_and_continue"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ], spacing=6),
            on_click=save_and_continue,
            style=ft.ButtonStyle(
                bgcolor=self.primary_color,
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=2,
                padding=ft.padding.symmetric(horizontal=24, vertical=12),
            ),
        )
        
        action_buttons = ft.Container(
            content=ft.Row([cancel_btn, save_btn], alignment=ft.MainAxisAlignment.END, spacing=12),
            padding=ft.padding.only(top=20),
        )
        
        # Scrollable form content - use Column with scroll directly
        scrollable_content = ft.Column(
            [
                customer_section,
                vehicle_section,
                action_buttons,
                status_text,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        # Main content area with padding
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