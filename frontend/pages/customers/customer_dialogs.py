# pages/customers/customer_dialogs.py
import flet as ft
from i18n import get_text

PRIMARY_COLOR = "#1565C0"
WARNING_COLOR = "#DC2626"


def show_add_dialog(primary_color, brands_list, on_save, on_close):
    """Show add customer dialog"""
    
    customer_name = ft.TextField(
        label=get_text("customer_name"),
        hint_text=get_text("customer_name_hint"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
        expand=True,
    )
    
    customer_phone = ft.TextField(
        label=get_text("customer_phone"),
        hint_text=get_text("customer_phone_hint"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
        expand=True,
    )
    
    customer_address = ft.TextField(
        label=get_text("customer_address"),
        hint_text=get_text("customer_address_hint"),
        multiline=True,
        min_lines=2,
        max_lines=3,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
    )
    
    plate_number = ft.TextField(
        label=get_text("plate_number"),
        hint_text="ກຂ 1234",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
        expand=True,
    )
    
    # Brand dropdown
    brand_dropdown = ft.Dropdown(
        label=get_text("car_brand"),
        hint_text=get_text("select_brand"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        options=[
            ft.dropdown.Option(str(b.get("id")), b.get("name"))
            for b in brands_list
        ],
        expand=True,
    )
    
    model = ft.TextField(
        label=get_text("car_model"),
        hint_text="Corolla",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
        expand=True,
    )
    
    year = ft.TextField(
        label=get_text("car_year"),
        hint_text="2020",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
        expand=True,
        # max_length=4,
    )
    
    color = ft.TextField(
        label=get_text("car_color"),
        hint_text="Black",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
        expand=True,
    )
    
    def save(e):
        if not customer_name.value:
            customer_name.error_text = get_text("required_field")
            return
        if not customer_phone.value:
            customer_phone.error_text = get_text("required_field")
            return
        if not plate_number.value:
            plate_number.error_text = get_text("required_field")
            return
        if not brand_dropdown.value:
            brand_dropdown.error_text = get_text("required_field")
            return
        
        customer_data = {
            "name": customer_name.value,
            "phone": customer_phone.value,
            "address": customer_address.value,
        }
        
        year_value = 0
        if year.value and year.value.isdigit():
            year_value = int(year.value)
        
        vehicle_data = {
            "plate_number": plate_number.value.upper(),
            "brand_id": int(brand_dropdown.value),
            "model": model.value,
            "year": year_value,
            "color": color.value,
        }
        on_save(customer_data, vehicle_data)
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON_ADD, size=20, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=10,
                        padding=ft.padding.all(5),
                    ),
                    ft.Text(get_text("add_new_customer"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(get_text("customer_information"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Container(height=6),
                ft.Row([customer_name, customer_phone], spacing=10, expand=True),
                ft.Container(height=6),
                customer_address,
                ft.Container(height=12),
                ft.Text(get_text("vehicle_information"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Container(height=6),
                ft.Row([plate_number, brand_dropdown], spacing=10, expand=True),
                ft.Container(height=6),
                ft.Row([model, year, color], spacing=10, expand=True),
            ], spacing=0),
            padding=ft.padding.all(16),
            width=520,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), color="#64748B"),
                        on_click=on_close,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("save"), color=ft.Colors.WHITE),
                        on_click=save,
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=6),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=16, vertical=6),
                        ),
                    ),
                ], spacing=8, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_success_popup(customer_name, plate_number, primary_color, on_close):
    """Show success popup after customer registration (without animation for older Flet)"""
    
    popup = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=20),
        bgcolor=ft.Colors.WHITE,
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE, 
                        size=64, 
                        color=ft.Colors.GREEN_600
                    ),
                    ft.Container(height=16),
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
            width=380,
            padding=ft.padding.all(24),
        ),
        actions=[
            ft.ElevatedButton(
                content=ft.Text(get_text("ok"), size=14, color=ft.Colors.WHITE),
                on_click=lambda e: on_close(popup),
                style=ft.ButtonStyle(
                    bgcolor=primary_color,
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.padding.symmetric(horizontal=30, vertical=10),
                ),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    
    return popup


def show_edit_dialog(customer, primary_color, on_save, on_close):
    """Show edit customer dialog"""
    
    customer_name = ft.TextField(
        label=get_text("customer_name"),
        value=customer.get("name", ""),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
        expand=True,
    )
    
    customer_phone = ft.TextField(
        label=get_text("customer_phone"),
        value=customer.get("phone", ""),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
        expand=True,
    )
    
    customer_address = ft.TextField(
        label=get_text("customer_address"),
        value=customer.get("address", ""),
        multiline=True,
        min_lines=2,
        max_lines=3,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=13,
    )
    
    def save(e):
        if not customer_name.value:
            customer_name.error_text = get_text("required_field")
            return
        
        update_data = {
            "name": customer_name.value,
            "phone": customer_phone.value,
            "address": customer_address.value,
        }
        on_save(update_data)
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.EDIT, size=20, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=10,
                        padding=ft.padding.all(5),
                    ),
                    ft.Text(get_text("edit_customer"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(get_text("customer_information"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Container(height=6),
                ft.Row([customer_name, customer_phone], spacing=10, expand=True),
                ft.Container(height=6),
                customer_address,
            ], spacing=0),
            padding=ft.padding.all(16),
            width=450,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), color="#64748B"),
                        on_click=on_close,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("save"), color=ft.Colors.WHITE),
                        on_click=save,
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=6),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=16, vertical=6),
                        ),
                    ),
                ], spacing=8, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_detail_dialog(customer, vehicles, brands_list, primary_color, on_add_vehicle, on_delete_vehicle, on_close):
    """Show customer detail dialog with vehicle list and brand dropdown"""
    
    customer_id = customer.get("id")
    name = customer.get("name", "-")
    phone = customer.get("phone", "-")
    address = customer.get("address", "-")
    
    # Vehicle list
    vehicle_list = ft.Column(spacing=8)
    
    if vehicles and len(vehicles) > 0:
        for vehicle in vehicles:
            vehicle_id = vehicle.get("id")
            plate_number = vehicle.get("plate_number", "-")
            brand_id = vehicle.get("brand_id", 0)
            brand_name = vehicle.get("brand_name", "-")
            model = vehicle.get("model", "-")
            year = vehicle.get("year", "-")
            color = vehicle.get("color", "-")
            
            vehicle_row = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DIRECTIONS_CAR, size=18, color=primary_color),
                    ft.Text(f"{plate_number}", size=13, weight=ft.FontWeight.W_500, color="#1E293B", expand=True),
                    ft.Text(f"{brand_name} {model}", size=12, color="#64748B"),
                    ft.Text(f"{year}", size=12, color="#64748B") if str(year) != "-" and year else ft.Container(),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=18,
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, vid=vehicle_id: on_delete_vehicle(vid),
                    ),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(vertical=6, horizontal=10),
                bgcolor=ft.Colors.GREY_50,
                border_radius=8,
            )
            vehicle_list.controls.append(vehicle_row)
    else:
        vehicle_list.controls.append(
            ft.Container(
                content=ft.Text(get_text("no_vehicles_registered"), size=13, color="#64748B"),
                padding=ft.padding.all(20),
                alignment=ft.Alignment(0, 0),
            )
        )
    
    # Add vehicle form with brand dropdown
    new_plate = ft.TextField(
        label=get_text("plate_number"),
        hint_text="ກຂ 1234",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        text_size=12,
        expand=True,
    )
    
    new_brand = ft.Dropdown(
        label=get_text("car_brand"),
        hint_text=get_text("select_brand"),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        options=[
            ft.dropdown.Option(str(b.get("id")), b.get("name"))
            for b in brands_list
        ],
        expand=True,
    )
    
    new_model = ft.TextField(
        label=get_text("car_model"),
        hint_text="Corolla",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        text_size=12,
        expand=True,
    )
    
    new_year = ft.TextField(
        label=get_text("car_year"),
        hint_text="2020",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        text_size=12,
        expand=True,
        # max_length=4,
    )
    
    new_color = ft.TextField(
        label=get_text("car_color"),
        hint_text="Black",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        text_size=12,
        expand=True,
    )
    
    def add_vehicle(e):
        if not new_plate.value:
            new_plate.error_text = get_text("required_field")
            return
        if not new_brand.value:
            new_brand.error_text = get_text("required_field")
            return
        
        year_value = 0
        if new_year.value and new_year.value.isdigit():
            year_value = int(new_year.value)
        
        vehicle_data = {
            "customer_id": customer_id,
            "plate_number": new_plate.value.upper(),
            "brand_id": int(new_brand.value),
            "model": new_model.value,
            "year": year_value,
            "color": new_color.value,
        }
        on_add_vehicle(vehicle_data)
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON, size=20, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=10,
                        padding=ft.padding.all(5),
                    ),
                    ft.Text(get_text("customer_details"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                # Customer info
                ft.Text(get_text("customer_information"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Container(height=4),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("customer_name"), size=11, color="#64748B"),
                        ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    ], spacing=2, expand=True),
                    ft.Column([
                        ft.Text(get_text("customer_phone"), size=11, color="#64748B"),
                        ft.Text(phone, size=13, color="#1E293B"),
                    ], spacing=2, expand=True),
                ], expand=True),
                ft.Container(height=8),
                ft.Text(get_text("customer_address"), size=11, color="#64748B"),
                ft.Text(address, size=12, color="#64748B"),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=8),
                # Vehicle list
                ft.Row([
                    ft.Text(get_text("vehicles"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ]),
                ft.Container(height=4),
                vehicle_list,
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=8),
                # Add vehicle form
                ft.Text(get_text("add_new_vehicle"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Container(height=4),
                ft.Row([new_plate, new_brand], spacing=8, expand=True),
                ft.Container(height=6),
                ft.Row([new_model, new_year, new_color], spacing=8, expand=True),
                ft.Container(height=8),
                ft.Row([
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("add_vehicle"), size=12, color=ft.Colors.WHITE),
                        on_click=add_vehicle,
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=6),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=16, vertical=6),
                        ),
                    ),
                ]),
            ], spacing=0, scroll=ft.ScrollMode.AUTO),
            width=500,
            height=500,
            padding=ft.padding.all(16),
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.Container(expand=True),
                    ft.TextButton(
                        content=ft.Text(get_text("close"), color="#64748B"),
                        on_click=on_close,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                    ),
                ], spacing=8, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_delete_dialog(customer_name, on_confirm, on_close):
    """Show delete confirmation dialog"""
    
    def confirm(e):
        on_confirm(e)
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.WARNING_AMBER, size=20, color=ft.Colors.WHITE),
                        bgcolor=WARNING_COLOR,
                        border_radius=10,
                        padding=ft.padding.all(5),
                    ),
                    ft.Text(get_text("confirm_delete"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    f"ຕ້ອງການລຶບ '{customer_name}' ຫຼື ບໍ່?",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color="#1E293B",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=4),
                ft.Text(
                    get_text("delete_warning"),
                    size=12,
                    color="#64748B",
                    text_align=ft.TextAlign.CENTER,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            padding=ft.padding.all(20),
            width=320,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), color="#64748B"),
                        on_click=on_close,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("delete"), color=ft.Colors.WHITE),
                        on_click=confirm,
                        style=ft.ButtonStyle(
                            bgcolor=WARNING_COLOR,
                            shape=ft.RoundedRectangleBorder(radius=6),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=16, vertical=6),
                        ),
                    ),
                ], spacing=8, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog