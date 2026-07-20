# pages/customers/customer_dialogs.py
import flet as ft
from i18n import get_text

PRIMARY_COLOR = "#1565C0"
WARNING_COLOR = "#DC2626"
PHONE_MAX_LENGTH = 20
YEAR_MAX_LENGTH = 4


def show_add_dialog(primary_color, brands_list, on_save, on_close):
    """Show add customer dialog with validation"""
    
    # Error labels
    name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    phone_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    plate_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    brand_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    year_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    
    # Phone hint
    phone_hint = ft.Text(
        f"ສາມາດປ້ອນໄດ້ສູງສຸດ {PHONE_MAX_LENGTH} ຕົວ",
        size=10,
        color=ft.Colors.GREY_500,
    )
    
    # Validation functions
    def on_phone_change(e):
        if customer_phone.value:
            cleaned = ''.join(filter(str.isdigit, customer_phone.value))
            if len(cleaned) > PHONE_MAX_LENGTH:
                cleaned = cleaned[:PHONE_MAX_LENGTH]
            customer_phone.value = cleaned
            customer_phone.update()
        if customer_phone.value and len(customer_phone.value) <= PHONE_MAX_LENGTH:
            phone_error.visible = False
            phone_error.update()
    
    def on_year_change(e):
        if year.value:
            cleaned = ''.join(filter(str.isdigit, year.value))
            if len(cleaned) > YEAR_MAX_LENGTH:
                cleaned = cleaned[:YEAR_MAX_LENGTH]
            year.value = cleaned
            year.update()
        if year.value and len(year.value) == YEAR_MAX_LENGTH:
            year_error.visible = False
            year_error.update()
    
    def on_plate_change(e):
        if plate_number.value:
            plate_number.value = plate_number.value.upper()
            plate_number.update()
    
    customer_name = ft.TextField(
        label=get_text("customer_name"),
        hint_text=get_text("customer_name_hint"),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        expand=True,
        height=38,
    )
    
    customer_phone = ft.TextField(
        label=get_text("customer_phone"),
        hint_text="020xxxxxxxx",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        expand=True,
        height=38,
        on_change=on_phone_change,
    )
    
    customer_address = ft.TextField(
        label=get_text("customer_address"),
        hint_text=get_text("customer_address_hint"),
        multiline=True,
        min_lines=2,
        max_lines=3,
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        height=56,
    )
    
    plate_number = ft.TextField(
        label=get_text("plate_number"),
        hint_text="ກຂ 1234",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        expand=True,
        height=38,
        on_change=on_plate_change,
    )
    
    brand_dropdown = ft.Dropdown(
        label=get_text("car_brand"),
        hint_text=get_text("select_brand"),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        height=38,
        options=[
            ft.dropdown.Option(str(b.get("id")), b.get("name"))
            for b in brands_list
        ],
        expand=True,
    )
    
    model = ft.TextField(
        label=get_text("car_model"),
        hint_text="Corolla",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        expand=True,
        height=38,
    )
    
    year = ft.TextField(
        label=get_text("car_year"),
        hint_text="2020",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        expand=True,
        height=38,
        on_change=on_year_change,
    )
    
    color = ft.TextField(
        label=get_text("car_color"),
        hint_text="Black",
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        expand=True,
        height=38,
    )
    
    def validate_fields():
        is_valid = True
        
        # Validate Name
        if not customer_name.value or not customer_name.value.strip():
            name_error.value = get_text("please_enter_name")
            name_error.visible = True
            is_valid = False
        else:
            name_error.visible = False
        
        # Validate Phone
        if not customer_phone.value or not customer_phone.value.strip():
            phone_error.value = get_text("please_enter_phone")
            phone_error.visible = True
            is_valid = False
        else:
            phone_clean = customer_phone.value.strip().replace(" ", "")
            if not phone_clean.isdigit():
                phone_error.value = get_text("phone_must_be_number")
                phone_error.visible = True
                is_valid = False
            elif len(phone_clean) > PHONE_MAX_LENGTH:
                phone_error.value = f"ເບີໂທລະສັບຕ້ອງບໍ່ເກີນ {PHONE_MAX_LENGTH} ຕົວ"
                phone_error.visible = True
                is_valid = False
            else:
                phone_error.visible = False
        
        # Validate Plate Number
        if not plate_number.value or not plate_number.value.strip():
            plate_error.value = get_text("please_enter_plate_number")
            plate_error.visible = True
            is_valid = False
        else:
            plate_error.visible = False
        
        # Validate Brand
        if not brand_dropdown.value:
            brand_error.value = get_text("please_select_brand")
            brand_error.visible = True
            is_valid = False
        else:
            brand_error.visible = False
        
        # Validate Year (if provided)
        if year.value and year.value.strip():
            year_clean = year.value.strip()
            if not year_clean.isdigit():
                year_error.value = get_text("year_must_be_number")
                year_error.visible = True
                is_valid = False
            elif len(year_clean) != YEAR_MAX_LENGTH:
                year_error.value = f"ປີຕ້ອງມີ {YEAR_MAX_LENGTH} ຕົວ"
                year_error.visible = True
                is_valid = False
            else:
                year_error.visible = False
        else:
            year_error.visible = False
        
        return is_valid
    
    def _save():
        if not validate_fields():
            # Update dialog to show errors
            if dialog_ref:
                dialog_ref.update()
            return
        
        customer_data = {
            "name": customer_name.value.strip(),
            "phone": customer_phone.value.strip(),
            "address": customer_address.value.strip() if customer_address.value else "",
        }
        
        year_value = 0
        if year.value and year.value.isdigit():
            year_value = int(year.value)
        
        vehicle_data = {
            "plate_number": plate_number.value.strip().upper(),
            "brand_id": int(brand_dropdown.value),
            "model": model.value.strip() if model.value else "",
            "year": year_value,
            "color": color.value.strip() if color.value else "",
        }
        on_save(customer_data, vehicle_data)
    
    dialog_ref = None
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=12),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON_ADD, size=18, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=8,
                        padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                    ),
                    ft.Text(get_text("add_new_customer"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(get_text("customer_information"), size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=4),
                ft.Column([
                    ft.Row([customer_name, customer_phone], spacing=8),
                    phone_hint,
                    phone_error,
                ], spacing=1),
                ft.Container(height=4),
                customer_address,
                ft.Container(height=8),
                ft.Text(get_text("vehicle_information"), size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=4),
                ft.Column([
                    ft.Row([plate_number, brand_dropdown], spacing=8),
                    plate_error,
                    brand_error,
                ], spacing=1),
                ft.Container(height=4),
                ft.Row([model, year, color], spacing=8),
                year_error,
            ], spacing=0),
            padding=ft.Padding(left=14, right=14, top=12, bottom=8),
            width=360,
            height=300,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("save"), size=13, color=ft.Colors.WHITE),
                        on_click=lambda e: _save(),
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                        ),
                    ),
                ], spacing=6, alignment=ft.MainAxisAlignment.END),
                padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    dialog_ref = dialog
    return dialog


def show_detail_dialog(customer, vehicles, brands_list, primary_color, on_close):
    """Show customer detail dialog (view only)"""
    
    name = customer.get("name", "-")
    phone = customer.get("phone", "-")
    address = customer.get("address", "-")
    
    # Vehicle list - display only
    vehicle_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    
    if vehicles and len(vehicles) > 0:
        for vehicle in vehicles:
            plate_number = vehicle.get("plate_number", "-")
            brand_name = vehicle.get("brand_name", "-")
            model = vehicle.get("model", "-")
            year = vehicle.get("year", "-")
            color = vehicle.get("color", "-")
            
            vehicle_row = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DIRECTIONS_CAR, size=14, color=primary_color),
                    ft.Text(plate_number, size=12, weight=ft.FontWeight.W_500, color="#1E293B", width=90),
                    ft.Text(f"{brand_name} {model}", size=11, color="#64748B", expand=True),
                    ft.Text(str(year), size=11, color="#64748B") if year and year != 0 else ft.Container(),
                    ft.Text(color, size=11, color="#64748B", width=60) if color and color != "-" else ft.Container(),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
            )
            vehicle_list.controls.append(vehicle_row)
    else:
        vehicle_list.controls.append(
            ft.Container(
                content=ft.Text(get_text("no_vehicles_registered"), size=12, color="#64748B"),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                alignment=ft.Alignment(0, 0),
            )
        )
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=12),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON, size=18, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=8,
                        padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                    ),
                    ft.Text(get_text("customer_details"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(get_text("customer_information"), size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=4),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("customer_name"), size=10, color="#64748B"),
                        ft.Text(name, size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                    ], spacing=1, expand=True),
                    ft.Column([
                        ft.Text(get_text("customer_phone"), size=10, color="#64748B"),
                        ft.Text(phone, size=12, color="#1E293B"),
                    ], spacing=1, expand=True),
                ]),
                ft.Container(height=4),
                ft.Text(get_text("customer_address"), size=10, color="#64748B"),
                ft.Text(address, size=11, color="#64748B"),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Container(height=6),
                ft.Text(get_text("vehicles"), size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=4),
                vehicle_list,
            ], spacing=0, scroll=ft.ScrollMode.AUTO),
            width=360,
            height=260,
            padding=ft.Padding(left=14, right=14, top=12, bottom=8),
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.Container(expand=True),
                    ft.TextButton(
                        content=ft.Text(get_text("close"), size=13, color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ], spacing=6, alignment=ft.MainAxisAlignment.END),
                padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_edit_dialog(customer, vehicles, brands_list, primary_color, on_save_customer, on_add_vehicle, on_edit_vehicle, on_delete_vehicle, on_save_complete, on_cancel):
    """Show edit customer dialog with vehicle management"""
    
    customer_id = customer.get("id")
    dialog_ref = None
    
    # Error labels
    name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    phone_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    year_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    
    # Phone hint
    phone_hint = ft.Text(
        f"ສາມາດປ້ອນໄດ້ສູງສຸດ {PHONE_MAX_LENGTH} ຕົວ",
        size=10,
        color=ft.Colors.GREY_500,
    )
    
    # Validation functions
    def on_phone_change(e):
        if customer_phone.value:
            cleaned = ''.join(filter(str.isdigit, customer_phone.value))
            if len(cleaned) > PHONE_MAX_LENGTH:
                cleaned = cleaned[:PHONE_MAX_LENGTH]
            customer_phone.value = cleaned
            customer_phone.update()
        if customer_phone.value and len(customer_phone.value) <= PHONE_MAX_LENGTH:
            phone_error.visible = False
            phone_error.update()
    
    def on_year_change(e):
        if new_year.value:
            cleaned = ''.join(filter(str.isdigit, new_year.value))
            if len(cleaned) > YEAR_MAX_LENGTH:
                cleaned = cleaned[:YEAR_MAX_LENGTH]
            new_year.value = cleaned
            new_year.update()
        if new_year.value and len(new_year.value) == YEAR_MAX_LENGTH:
            year_error.visible = False
            year_error.update()
    
    # Customer fields
    customer_name = ft.TextField(
        label=get_text("customer_name"),
        value=customer.get("name", ""),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        expand=True,
        height=38,
    )
    
    customer_phone = ft.TextField(
        label=get_text("customer_phone"),
        value=customer.get("phone", ""),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        expand=True,
        height=38,
        on_change=on_phone_change,
    )
    
    customer_address = ft.TextField(
        label=get_text("customer_address"),
        value=customer.get("address", ""),
        multiline=True,
        min_lines=2,
        max_lines=3,
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        border_color=ft.Colors.GREY_300,
        focused_border_color=primary_color,
        text_size=12,
        height=56,
    )
    
    # Vehicle list
    vehicle_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    
    # Store data
    deleted_vehicle_ids = []
    added_vehicles = []
    
    # Form for adding new vehicle
    new_plate = ft.TextField(
        label=get_text("plate_number"),
        hint_text="ກຂ 1234",
        border_radius=6,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        text_size=11,
        expand=True,
        height=32,
    )
    
    new_brand = ft.Dropdown(
        label=get_text("car_brand"),
        hint_text=get_text("select_brand"),
        border_radius=6,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        height=32,
        options=[
            ft.dropdown.Option(str(b.get("id")), b.get("name"))
            for b in brands_list
        ],
        expand=True,
    )
    
    new_model = ft.TextField(
        label=get_text("car_model"),
        hint_text="Corolla",
        border_radius=6,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        text_size=11,
        expand=True,
        height=32,
    )
    
    new_year = ft.TextField(
        label=get_text("car_year"),
        hint_text="2020",
        border_radius=6,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        text_size=11,
        expand=True,
        height=32,
        on_change=on_year_change,
    )
    
    new_color = ft.TextField(
        label=get_text("car_color"),
        hint_text="Black",
        border_radius=6,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        text_size=11,
        expand=True,
        height=32,
    )
    
    add_form_visible = [False]
    add_form_container = ft.Container(visible=False)
    
    def toggle_add_form():
        add_form_visible[0] = not add_form_visible[0]
        add_form_container.visible = add_form_visible[0]
        if dialog_ref:
            try:
                dialog_ref.update()
            except:
                pass
    
    def refresh_vehicle_list_display():
        """Refresh vehicle list display"""
        vehicle_list.controls.clear()
        
        # Show existing vehicles (excluding deleted ones)
        for vehicle in vehicles:
            if vehicle.get('id') in deleted_vehicle_ids:
                continue
                
            vehicle_id = vehicle.get("id")
            plate_number = vehicle.get("plate_number", "-")
            brand_name = vehicle.get("brand_name", "-")
            model = vehicle.get("model", "-")
            year = vehicle.get("year", "-")
            color = vehicle.get("color", "-")
            
            row = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DIRECTIONS_CAR, size=14, color=primary_color),
                    ft.Text(plate_number, size=12, weight=ft.FontWeight.W_500, color="#1E293B", width=90),
                    ft.Text(f"{brand_name} {model}", size=11, color="#64748B", expand=True),
                    ft.Text(str(year), size=11, color="#64748B") if year and year != 0 else ft.Container(),
                    ft.Text(color, size=11, color="#64748B", width=60) if color and color != "-" else ft.Container(),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=14,
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, vid=vehicle_id: mark_vehicle_for_deletion(vid),
                        tooltip=get_text("delete"),
                    ),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=6, right=6, top=4, bottom=4),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
            )
            vehicle_list.controls.append(row)
        
        # Show added vehicles
        for idx, added in enumerate(added_vehicles):
            row = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD_CIRCLE, size=14, color=ft.Colors.GREEN_600),
                    ft.Text(added.get('plate_number', '-'), size=12, weight=ft.FontWeight.W_500, color="#1E293B", width=90),
                    ft.Text(added.get('brand_name', '-'), size=11, color="#64748B", expand=True),
                    ft.Text(added.get('model', '-'), size=11, color="#64748B"),
                    ft.Text(str(added.get('year', '')), size=11, color="#64748B"),
                    ft.Text(added.get('color', '-'), size=11, color="#64748B", width=60),
                    ft.IconButton(
                        icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                        icon_size=14,
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, i=idx: remove_added_vehicle(i),
                        tooltip=get_text("remove"),
                    ),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=6, right=6, top=4, bottom=4),
                bgcolor=ft.Colors.GREEN_50,
                border_radius=6,
            )
            vehicle_list.controls.append(row)
        
        if dialog_ref:
            try:
                dialog_ref.update()
            except:
                pass
    
    def mark_vehicle_for_deletion(vehicle_id):
        if vehicle_id not in deleted_vehicle_ids:
            deleted_vehicle_ids.append(vehicle_id)
        refresh_vehicle_list_display()
    
    def remove_added_vehicle(index):
        if index < len(added_vehicles):
            added_vehicles.pop(index)
        refresh_vehicle_list_display()
    
    def add_vehicle_to_list():
        if not new_plate.value:
            new_plate.error_text = get_text("required_field")
            if dialog_ref:
                try:
                    dialog_ref.update()
                except:
                    pass
            return
        if not new_brand.value:
            new_brand.error_text = get_text("required_field")
            if dialog_ref:
                try:
                    dialog_ref.update()
                except:
                    pass
            return
        
        if new_year.value and new_year.value.strip():
            if not new_year.value.strip().isdigit():
                year_error.value = get_text("year_must_be_number")
                year_error.visible = True
                if dialog_ref:
                    try:
                        dialog_ref.update()
                    except:
                        pass
                return
            elif len(new_year.value.strip()) != YEAR_MAX_LENGTH:
                year_error.value = f"ປີຕ້ອງມີ {YEAR_MAX_LENGTH} ຕົວ"
                year_error.visible = True
                if dialog_ref:
                    try:
                        dialog_ref.update()
                    except:
                        pass
                return
            else:
                year_error.visible = False
        
        year_value = 0
        if new_year.value and new_year.value.isdigit():
            year_value = int(new_year.value)
        
        brand_name = "-"
        brand_id = int(new_brand.value)
        brand = next((b for b in brands_list if b.get('id') == brand_id), None)
        if brand:
            brand_name = brand.get('name')
        
        added_vehicles.append({
            'plate_number': new_plate.value.strip().upper(),
            'brand_id': brand_id,
            'brand_name': brand_name,
            'model': new_model.value.strip() if new_model.value else "",
            'year': year_value,
            'color': new_color.value.strip() if new_color.value else "",
        })
        
        # Clear form
        new_plate.value = ""
        new_brand.value = ""
        new_model.value = ""
        new_year.value = ""
        new_color.value = ""
        new_plate.error_text = None
        new_brand.error_text = None
        year_error.visible = False
        
        add_form_visible[0] = False
        add_form_container.visible = False
        refresh_vehicle_list_display()
    
    # Build add form container
    add_form_container.content = ft.Column([
        ft.Container(height=4),
        ft.Text(get_text("add_new_vehicle"), size=11, weight=ft.FontWeight.W_500, color="#1E293B"),
        ft.Divider(height=1, color=ft.Colors.GREY_200),
        ft.Container(height=2),
        ft.Row([new_plate, new_brand], spacing=6),
        ft.Container(height=4),
        ft.Row([new_model, new_year, new_color], spacing=6),
        ft.Column([year_error], spacing=1),
        ft.Container(height=4),
        ft.Row([
            ft.Container(expand=True),
            ft.TextButton(content=ft.Text(get_text("cancel"), size=11), on_click=lambda e: toggle_add_form()),
            ft.ElevatedButton(content=ft.Text(get_text("add"), size=11, color=ft.Colors.WHITE), on_click=lambda e: add_vehicle_to_list(), bgcolor=primary_color),
        ], spacing=6, alignment=ft.MainAxisAlignment.END),
    ], spacing=0)
    
    # Initial display
    refresh_vehicle_list_display()
    
    def validate_customer_fields():
        is_valid = True
        
        if not customer_name.value or not customer_name.value.strip():
            name_error.value = get_text("please_enter_name")
            name_error.visible = True
            is_valid = False
        else:
            name_error.visible = False
        
        if not customer_phone.value or not customer_phone.value.strip():
            phone_error.value = get_text("please_enter_phone")
            phone_error.visible = True
            is_valid = False
        else:
            phone_clean = customer_phone.value.strip().replace(" ", "")
            if not phone_clean.isdigit():
                phone_error.value = get_text("phone_must_be_number")
                phone_error.visible = True
                is_valid = False
            elif len(phone_clean) > PHONE_MAX_LENGTH:
                phone_error.value = f"ເບີໂທລະສັບຕ້ອງບໍ່ເກີນ {PHONE_MAX_LENGTH} ຕົວ"
                phone_error.visible = True
                is_valid = False
            else:
                phone_error.visible = False
        
        # Update dialog to show errors
        if dialog_ref:
            try:
                dialog_ref.update()
            except:
                pass
        
        return is_valid
    
    def save_all():
        if not validate_customer_fields():
            return
        
        update_data = {
            "name": customer_name.value.strip(),
            "phone": customer_phone.value.strip(),
            "address": customer_address.value.strip() if customer_address.value else "",
        }
        on_save_customer(update_data)
        
        for av in added_vehicles:
            vehicle_data = {
                "customer_id": customer_id,
                "plate_number": av['plate_number'],
                "brand_id": av['brand_id'],
                "model": av['model'],
                "year": av['year'],
                "color": av['color'],
            }
            on_add_vehicle(vehicle_data, None)
        
        for vid in deleted_vehicle_ids:
            on_delete_vehicle(vid, None)
        
        on_save_complete()
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=12),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.EDIT, size=18, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=8,
                        padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                    ),
                    ft.Text(get_text("edit_customer"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(get_text("customer_information"), size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=4),
                ft.Column([
                    ft.Row([customer_name, customer_phone], spacing=8),
                    phone_hint,
                    phone_error,
                ], spacing=1),
                ft.Container(height=4),
                customer_address,
                ft.Container(height=8),
                ft.Text(get_text("vehicles"), size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Row([
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                        icon_size=18,
                        icon_color=primary_color,
                        on_click=lambda e: toggle_add_form(),
                        tooltip=get_text("add_vehicle"),
                    ),
                ]),
                vehicle_list,
                add_form_container,
            ], spacing=0, scroll=ft.ScrollMode.AUTO),
            width=360,
            height=300,
            padding=ft.Padding(left=14, right=14, top=12, bottom=8),
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                        on_click=lambda e: on_cancel(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("save"), size=13, color=ft.Colors.WHITE),
                        on_click=lambda e: save_all(),
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                        ),
                    ),
                ], spacing=6, alignment=ft.MainAxisAlignment.END),
                padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    dialog_ref = dialog
    return dialog


def show_delete_dialog(customer_name, on_confirm, on_close):
    """Show delete confirmation dialog"""
    
    def confirm(e):
        on_confirm(e)
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=12),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.WARNING_AMBER, size=18, color=ft.Colors.WHITE),
                        bgcolor=WARNING_COLOR,
                        border_radius=8,
                        padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                    ),
                    ft.Text(get_text("confirm_delete"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=32, color=WARNING_COLOR),
                ft.Container(height=4),
                ft.Text(
                    f"ຕ້ອງການລຶບ '{customer_name}' ຫຼື ບໍ່?",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color="#1E293B",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    get_text("delete_warning"),
                    size=12,
                    color="#64748B",
                    text_align=ft.TextAlign.CENTER,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            width=280,
            height=150,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("delete"), size=13, color=ft.Colors.WHITE),
                        on_click=confirm,
                        style=ft.ButtonStyle(
                            bgcolor=WARNING_COLOR,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                        ),
                    ),
                ], spacing=6, alignment=ft.MainAxisAlignment.END),
                padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_success_popup(customer_id, customer_name, plate_number, primary_color, on_close):
    """Show success popup after customer registration"""
    
    popup = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=16),
        bgcolor=ft.Colors.WHITE,
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE, 
                        size=48, 
                        color=ft.Colors.GREEN_600
                    ),
                    ft.Container(height=12),
                    ft.Text(
                        get_text("save_successful"),
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color="#1E293B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=6),
                    ft.Text(
                        get_text("customer_registered_successfully"),
                        size=13,
                        color="#64748B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"{get_text('customer_id')}: {customer_id}",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    f"{get_text('customer_name')}: {customer_name}",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    f"{get_text('plate_number')}: {plate_number}",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color="#1E293B",
                                ),
                            ],
                            spacing=4,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.Padding(left=14, right=14, top=12, bottom=12),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=10,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            width=340,
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
        ),
        actions=[
            ft.ElevatedButton(
                content=ft.Text(get_text("ok"), size=13, color=ft.Colors.WHITE),
                on_click=lambda e: on_close(popup),
                style=ft.ButtonStyle(
                    bgcolor=primary_color,
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(left=28, right=28, top=8, bottom=8),
                ),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    
    return popup