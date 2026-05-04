# pages/customers/customer_list.py
import flet as ft
from flet import Alignment
from typing import Dict, Callable

from i18n import get_text


class CustomerListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.customers = []
        self.expanded_customer_id = None
        self.search_field = None
        self.clear_button = None

    def build(self):
        # Beautiful gradient header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("customer_list_title"),
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                get_text("customer_list_subtitle"),
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                                ft.Text(
                                    get_text("add_new_customer"),
                                    size=14,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ],
                            spacing=6,
                        ),
                        on_click=lambda e: self.navigate("input_customer"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        ),
                    ),
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

        # Search bar with real-time search
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

        self.clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=20,
            tooltip=get_text("clear_search"),
            on_click=lambda e: self.clear_search(),
            visible=False,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )

        refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=22,
            tooltip=get_text("refresh"),
            on_click=lambda e: self.load_customers(),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(1, ft.Colors.GREY_300),
            ),
        )

        # Stats row
        self.stats_container = ft.Container(
            content=ft.Row(
                [
                    self._create_stat_card(
                        get_text("total_customers"), "0", ft.Icons.PEOPLE, "#1565C0"
                    ),
                    self._create_stat_card(
                        get_text("total_vehicles"),
                        "0",
                        ft.Icons.DIRECTIONS_CAR,
                        "#10B981",
                    ),
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            margin=ft.margin.only(bottom=20),
        )

        # Search row with clear button
        search_row = ft.Container(
            content=ft.Row([self.search_field, self.clear_button, refresh_button], spacing=10),
            margin=ft.margin.only(bottom=16),
        )

        # Customers list (this will scroll)
        self.customers_list = ft.Column(
            spacing=12, scroll=ft.ScrollMode.AUTO, expand=True
        )

        # Loading indicator
        self.loading_indicator = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(width=40, height=40, stroke_width=4),
                    ft.Container(height=16),
                    ft.Text(get_text("loading"), size=14, color="#64748B"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=Alignment.CENTER,
            padding=ft.padding.all(40),
        )

        # Empty state
        self.empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=64, color=ft.Colors.GREY_300),
                    ft.Container(height=16),
                    ft.Text(
                        get_text("no_customers_found"),
                        size=18,
                        weight=ft.FontWeight.W_500,
                        color="#64748B",
                    ),
                    ft.Text(
                        get_text("click_add_to_register"), size=13, color="#94A3B8"
                    ),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("register_new_customer"), size=14),
                        on_click=lambda e: self.navigate("input_customer"),
                        style=ft.ButtonStyle(
                            bgcolor=self.primary_color,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=Alignment.CENTER,
            padding=ft.padding.all(60),
            visible=False,
        )

        # Scrollable content area
        scrollable_content = ft.Column(
            [
                self.stats_container,
                search_row,
                self.customers_list,
                self.loading_indicator,
                self.empty_state,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # Main content area with padding
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.padding.all(24),
            bgcolor="#F5F7FA",
        )

        # Main layout
        main_content = ft.Container(
            content=ft.Column(
                [
                    header,
                    content_area,
                ]
            ),
            expand=True,
            bgcolor="#F5F7FA",
        )

        # Load customers
        self.load_customers()

        return main_content

    def _create_stat_card(self, title: str, value: str, icon, color: str):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=24, color=ft.Colors.WHITE),
                        bgcolor=color,
                        border_radius=10,
                        padding=ft.padding.all(10),
                    ),
                    ft.Column(
                        [
                            ft.Text(title, size=12, color="#64748B"),
                            ft.Text(
                                value,
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_100),
            expand=True,
        )

    def load_customers(self, search_keyword: str = ""):
        """Load customers from API"""
        self.loading_indicator.visible = True
        self.empty_state.visible = False
        self.customers_list.controls.clear()
        self.page.update()

        try:
            customers = self.client.get_customers()

            if search_keyword:
                customers = [
                    c
                    for c in customers
                    if search_keyword.lower() in c.get("name", "").lower()
                    or search_keyword.lower() in c.get("phone", "").lower()
                ]

            self.customers = customers

            # Update stats
            self._update_stats()

            if customers and len(customers) > 0:
                self.loading_indicator.visible = False
                for idx, customer in enumerate(customers, start=1):
                    self.customers_list.controls.append(
                        self._create_customer_card(customer, idx)
                    )
            else:
                self.loading_indicator.visible = False
                self.empty_state.visible = True

            self.page.update()

        except Exception as ex:
            print(f"Error loading customers: {ex}")
            self.loading_indicator.visible = False
            self.customers_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED_400
                            ),
                            ft.Text(
                                f"Error: {str(ex)}", size=14, color=ft.Colors.RED_600
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(40),
                )
            )
            self.page.update()

    def _update_stats(self):
        """Update statistics cards"""
        total_customers = len(self.customers)
        total_vehicles = 0

        for customer in self.customers:
            try:
                vehicles = self.client.get_vehicles(customer_id=customer["id"])
                total_vehicles += len(vehicles) if vehicles else 0
            except:
                pass

        if len(self.stats_container.content.controls) > 0:
            self.stats_container.content.controls[0].content.controls[1].controls[
                1
            ].value = str(total_customers)
            self.stats_container.content.controls[1].content.controls[1].controls[
                1
            ].value = str(total_vehicles)

    def on_search_change(self, e):
        """Handle real-time search when typing"""
        keyword = e.control.value if hasattr(e, 'control') else e
        # Show/hide clear button
        if self.clear_button:
            self.clear_button.visible = bool(keyword)
            self.page.update()
        self.load_customers(keyword)

    def clear_search(self):
        """Clear search field and reload all customers"""
        if self.search_field:
            self.search_field.value = ""
            if self.clear_button:
                self.clear_button.visible = False
            self.page.update()
            self.load_customers("")

    def _create_customer_card(self, customer: Dict, row_number: int):
        """Create a customer card with vehicle list"""
        customer_id = customer.get("id")
        name = customer.get("name", "-")
        phone = customer.get("phone", "-")
        address = customer.get("address", "")
        is_expanded = self.expanded_customer_id == customer_id

        # Customer header with row number badge instead of avatar
        header = ft.Container(
            content=ft.Row(
                [
                    # Row number badge (replacing avatar circle)
                    ft.Container(
                        content=ft.Container(
                            content=ft.Text(
                                str(row_number),
                                size=13,
                                weight=ft.FontWeight.W_500,
                                color=self.primary_color,
                            ),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=8,
                            alignment=Alignment.CENTER,
                        ),
                        width=48,
                        height=48,
                        alignment=Alignment.CENTER,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                name,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                            ft.Text(phone, size=13, color="#64748B"),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_size=20,
                        tooltip=get_text("edit"),
                        on_click=lambda e, cid=customer_id: self.navigate_to_edit(cid),
                    ),
                    ft.IconButton(
                        icon=(
                            ft.Icons.KEYBOARD_ARROW_DOWN
                            if not is_expanded
                            else ft.Icons.KEYBOARD_ARROW_UP
                        ),
                        icon_size=20,
                        tooltip=get_text("view_vehicles"),
                        on_click=lambda e, cid=customer_id: self.toggle_vehicles(cid),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

        # Address section (if exists)
        address_section = None
        if address:
            address_section = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCATION_ON, size=16, color="#64748B"),
                        ft.Text(address, size=12, color="#64748B", expand=True),
                    ],
                    spacing=8,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                bgcolor=ft.Colors.GREY_50,
            )

        # Vehicles section
        vehicles_section = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    get_text("vehicles"),
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color="#1E293B",
                                ),
                                ft.TextButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.ADD, size=16),
                                            ft.Text(get_text("add_vehicle"), size=12),
                                        ],
                                        spacing=4,
                                    ),
                                    on_click=lambda e, cid=customer_id: self.show_add_vehicle_dialog(
                                        cid
                                    ),
                                    style=ft.ButtonStyle(color=self.primary_color),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(bottom=8),
                    ),
                    self._load_vehicles_for_customer(customer_id),
                ]
            ),
            padding=ft.padding.all(16),
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            visible=is_expanded,
        )

        # Combine all sections
        card_content = ft.Column(
            [
                header,
                address_section if address_section else ft.Container(),
                vehicles_section,
            ],
            spacing=0,
        )

        return ft.Card(
            content=card_content,
            elevation=2,
            margin=ft.margin.only(bottom=8),
        )

    def _load_vehicles_for_customer(self, customer_id: int):
        """Load and display vehicles for a customer (read-only, no edit button)"""
        vehicles_column = ft.Column(spacing=8)

        try:
            vehicles = self.client.get_vehicles(customer_id=customer_id)

            if not vehicles or len(vehicles) == 0:
                vehicles_column.controls.append(
                    ft.Container(
                        content=ft.Text(
                            get_text("no_vehicles_registered"), size=13, color="#64748B"
                        ),
                        padding=ft.padding.all(20),
                        alignment=Alignment.CENTER,
                    )
                )
            else:
                for vehicle in vehicles:
                    vehicles_column.controls.append(
                        self._create_vehicle_row(vehicle, customer_id)
                    )
        except Exception as ex:
            print(f"Error loading vehicles: {ex}")
            vehicles_column.controls.append(
                ft.Container(
                    content=ft.Text(
                        get_text("no_vehicles_registered"), size=13, color="#64748B"
                    ),
                    padding=ft.padding.all(20),
                    alignment=Alignment.CENTER,
                )
            )

        return vehicles_column

    def _create_vehicle_row(self, vehicle: Dict, customer_id: int):
        """Create a vehicle row with delete button only (no edit)"""
        vehicle_id = vehicle.get("id")
        plate_number = vehicle.get("plate_number", "-")
        brand = vehicle.get("brand", "-")
        model = vehicle.get("model", "-")
        year = vehicle.get("year", "-")
        color = vehicle.get("color", "-")

        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.DIRECTIONS_CAR, size=20, color=self.primary_color
                        ),
                        width=32,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                f"{plate_number}", size=14, weight=ft.FontWeight.W_500
                            ),
                            ft.Text(
                                f"{brand} {model} {f'({year})' if year != '-' else ''} {f'- {color}' if color != '-' else ''}",
                                size=12,
                                color="#64748B",
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=18,
                        icon_color=ft.Colors.RED_400,
                        tooltip=get_text("delete"),
                        on_click=lambda e, vid=vehicle_id: self.show_delete_vehicle_dialog(
                            vid, plate_number, customer_id
                        ),
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=4, horizontal=8),
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
        )

    def toggle_vehicles(self, customer_id: int):
        """Toggle vehicle list visibility"""
        if self.expanded_customer_id == customer_id:
            self.expanded_customer_id = None
        else:
            self.expanded_customer_id = customer_id

        # Reload customers to refresh expansion state
        self.load_customers()

    def navigate_to_edit(self, customer_id: int):
        """Navigate to edit customer page"""
        self.navigate("edit_customer", customer_id=customer_id)

    def show_snack_bar(self, message: str, is_error: bool = False):
        """Show snack bar message (compatible with Flet 0.84.0)"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
            open=True,
        )
        self.page.update()

    def show_add_vehicle_dialog(self, customer_id: int):
        """Show dialog to add a new vehicle"""
        plate_number = ft.TextField(label=get_text("plate_number"), expand=True)
        brand = ft.TextField(label=get_text("car_brand"), expand=True)
        model = ft.TextField(label=get_text("car_model"), expand=True)
        year = ft.TextField(
            label=get_text("car_year"),
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=4,
        )
        color = ft.TextField(label=get_text("car_color"), expand=True)

        def add_vehicle(e):
            if not plate_number.value:
                plate_number.error_text = get_text("required_field")
                self.page.update()
                return

            vehicle_data = {
                "customer_id": customer_id,
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
                    self.load_customers()
                    self.show_snack_bar(
                        get_text("vehicle_added_successfully"), is_error=False
                    )
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)

        dialog = ft.AlertDialog(
            title=ft.Text(get_text("add_new_vehicle")),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([plate_number, brand], spacing=12),
                        ft.Row([model, year], spacing=12),
                        ft.Row([color], spacing=12),
                    ],
                    spacing=12,
                ),
                width=500,
                padding=ft.padding.all(20),
            ),
            actions=[
                ft.TextButton(
                    get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)
                ),
                ft.ElevatedButton(get_text("add"), on_click=add_vehicle),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def show_delete_vehicle_dialog(
        self, vehicle_id: int, plate_number: str, customer_id: int
    ):
        """Show confirmation dialog to delete vehicle"""

        def delete_vehicle(e):
            try:
                result = self.client.delete_vehicle(vehicle_id)
                if result:
                    dialog.open = False
                    self.page.update()
                    self.load_customers()
                    self.show_snack_bar(
                        get_text("vehicle_deleted_successfully"), is_error=False
                    )
            except Exception as ex:
                self.show_snack_bar(f"Error: {str(ex)}", is_error=True)

        dialog = ft.AlertDialog(
            title=ft.Text(get_text("confirm_delete_vehicle")),
            content=ft.Text(
                f"{get_text('delete_vehicle_warning')}\n{get_text('plate_number')}: {plate_number}"
            ),
            actions=[
                ft.TextButton(
                    get_text("cancel"), on_click=lambda e: self.close_dialog(dialog)
                ),
                ft.ElevatedButton(
                    get_text("delete"),
                    on_click=delete_vehicle,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()