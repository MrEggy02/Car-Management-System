import flet as ft
from i18n import get_text


def show_create_job_order_dialog(primary_color, customers, vehicles_by_customer, on_save, on_close, page):
    """Show dialog to create new job order"""
    
    print(f"DEBUG DIALOG: customers count = {len(customers)}")
    print(f"DEBUG DIALOG: vehicles_by_customer keys = {list(vehicles_by_customer.keys())}")
    
    # Customer selection
    customer_dropdown = ft.Dropdown(
        label=get_text("select_customer"),
        hint_text=get_text("search_and_select_customer"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        options=[
            ft.dropdown.Option(str(c.get("id")), f"{c.get('name')} - {c.get('phone', '-')}")
            for c in customers
        ],
        expand=True,
    )
    
    # Vehicle selection - back to dropdown
    vehicle_dropdown = ft.Dropdown(
        label=get_text("select_vehicle"),
        hint_text=get_text("select_vehicle"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        options=[],
        expand=True,
    )
    
    # Customer info display
    customer_name_text = ft.Text("", size=14, weight=ft.FontWeight.W_500)
    customer_phone_text = ft.Text("", size=12, color="#64748B")
    customer_info_card = ft.Container(
        content=ft.Column([
            ft.Text(get_text("customer_information"), size=12, weight=ft.FontWeight.W_500, color="#64748B"),
            customer_name_text,
            customer_phone_text,
        ], spacing=4),
        padding=ft.padding.all(12),
        bgcolor=ft.Colors.GREY_50,
        border_radius=10,
        visible=False,
    )
    
    # Form fields
    problem_description = ft.TextField(
        label=get_text("problem_description"),
        hint_text=get_text("problem_description_hint"),
        multiline=True,
        min_lines=3,
        max_lines=4,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        expand=True,
    )
    
    mileage = ft.TextField(
        label=get_text("mileage"),
        hint_text="0",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        expand=True,
        input_filter=ft.NumbersOnlyInputFilter(),
    )
    
    fuel_level = ft.Dropdown(
        label=get_text("fuel_level"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
        options=[
            ft.dropdown.Option("full", "ເຕັມຖັງ (Full)"),
            ft.dropdown.Option("3/4", "3/4 ຖັງ"),
            ft.dropdown.Option("1/2", "1/2 ຖັງ"),
            ft.dropdown.Option("1/4", "1/4 ຖັງ"),
            ft.dropdown.Option("empty", "ໃກ້ໝົດ (Empty)"),
        ],
        expand=True,
    )
    
    def on_customer_change(e):
        print(f"DEBUG DIALOG: Customer selected: {customer_dropdown.value}")
        if customer_dropdown.value:
            selected = next((c for c in customers if str(c.get("id")) == customer_dropdown.value), None)
            if selected:
                customer_name_text.value = selected.get("name", "")
                customer_phone_text.value = selected.get("phone", "")
                customer_info_card.visible = True
                
                # Load vehicles for this customer
                customer_id = int(customer_dropdown.value)
                vehicles_list = vehicles_by_customer.get(customer_id, [])
                print(f"DEBUG DIALOG: Vehicles found for customer {customer_id}: {len(vehicles_list)}")
                print(f"DEBUG DIALOG: Vehicles list: {vehicles_list}")
                
                # Clear and set new options
                vehicle_dropdown.options.clear()
                
                for v in vehicles_list:
                    # Build display text with plate number, brand, model
                    plate = v.get('plate_number', '-')
                    brand = v.get('brand', '')
                    model = v.get('model', '')
                    
                    display_text = plate
                    if brand and brand != '-':
                        display_text += f" - {brand}"
                    if model and model != '-':
                        display_text += f" {model}"
                    
                    print(f"DEBUG DIALOG: Adding vehicle option: id={v.get('id')}, text={display_text}")
                    vehicle_dropdown.options.append(
                        ft.dropdown.Option(str(v.get("id")), display_text)
                    )
                
                if vehicles_list:
                    vehicle_dropdown.options.append(
                        ft.dropdown.Option("new", f"+ {get_text('add_new_vehicle')}")
                    )
                
                # Force update the dropdown
                vehicle_dropdown.update()
        else:
            customer_info_card.visible = False
            vehicle_dropdown.options.clear()
            vehicle_dropdown.update()
        
        dialog.update()
    
    customer_dropdown.on_change = on_customer_change
    
    # Function to show add vehicle dialog
    def show_add_vehicle_dialog(customer_id, customer_name):
        """Show dialog to add new vehicle"""
        print(f"DEBUG: show_add_vehicle_dialog called for customer {customer_id}")
        
        # Get brands for dropdown
        brands = []
        try:
            from api_client import APIClient
            temp_client = APIClient()
            brands = temp_client.get_brands() or []
            print(f"DEBUG: Loaded {len(brands)} brands")
        except Exception as e:
            print(f"DEBUG: Error loading brands: {e}")
        
        plate_number = ft.TextField(
            label=get_text("plate_number"),
            hint_text="ກຂ 1234",
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
        )
        
        brand_dropdown = ft.Dropdown(
            label=get_text("car_brand"),
            hint_text=get_text("select_brand"),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            options=[
                ft.dropdown.Option(str(b.get("id")), b.get("name"))
                for b in brands
            ],
            expand=True,
        )
        
        model = ft.TextField(
            label=get_text("car_model"),
            hint_text="Corolla",
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
        )
        
        year = ft.TextField(
            label=get_text("car_year"),
            hint_text="2020",
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
        )
        
        color = ft.TextField(
            label=get_text("car_color"),
            hint_text="Black",
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
        )
        
        def save_vehicle(e):
            if not plate_number.value:
                plate_number.error_text = get_text("required_field")
                add_dialog.update()
                return
            if not brand_dropdown.value:
                brand_dropdown.error_text = get_text("required_field")
                add_dialog.update()
                return
            
            year_value = 0
            if year.value and year.value.isdigit():
                year_value = int(year.value)
            
            try:
                from api_client import APIClient
                temp_client = APIClient()
                result = temp_client.add_vehicle({
                    "customer_id": customer_id,
                    "plate_number": plate_number.value.upper(),
                    "brand_id": int(brand_dropdown.value),
                    "model": model.value,
                    "year": year_value,
                    "color": color.value,
                })
                
                if result:
                    # Refresh vehicles and update dropdown
                    new_vehicles = temp_client.get_vehicles(customer_id=customer_id) or []
                    vehicles_list = []
                    for v in new_vehicles:
                        # Get brand name
                        brand_name = ""
                        brand_id = v.get("brand_id", 0)
                        for b in brands:
                            if b.get("id") == brand_id:
                                brand_name = b.get("name", "")
                                break
                        
                        vehicles_list.append({
                            "id": v.get("id"),
                            "plate_number": v.get("plate_number", "-"),
                            "brand": brand_name,
                            "model": v.get("model", "-"),
                        })
                    
                    # Update vehicles_by_customer cache
                    vehicles_by_customer[customer_id] = vehicles_list
                    
                    # Update dropdown options
                    vehicle_dropdown.options.clear()
                    for v in vehicles_list:
                        plate = v.get('plate_number', '-')
                        brand = v.get('brand', '')
                        model = v.get('model', '')
                        
                        display_text = plate
                        if brand and brand != '-':
                            display_text += f" - {brand}"
                        if model and model != '-':
                            display_text += f" {model}"
                        
                        vehicle_dropdown.options.append(
                            ft.dropdown.Option(str(v.get("id")), display_text)
                        )
                    
                    vehicle_dropdown.options.append(
                        ft.dropdown.Option("new", f"+ {get_text('add_new_vehicle')}")
                    )
                    
                    add_dialog.open = False
                    dialog.update()
                    
                    # Show success message
                    show_snackbar(f"✅ {get_text('vehicle_added_successfully')}")
            except Exception as err:
                show_snackbar(f"{get_text('error')}: {err}")
        
        def show_snackbar(message):
            snack = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.GREY_800, duration=3000)
            if page:
                page.snack_bar = snack
                page.snack_bar.open = True
                page.update()
        
        add_dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=14),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.ADD_CIRCLE, size=20, color=ft.Colors.WHITE),
                            bgcolor=primary_color,
                            border_radius=10,
                            padding=ft.padding.all(5),
                        ),
                        ft.Text(f"{get_text('add_new_vehicle')} - {customer_name}", size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([plate_number, brand_dropdown], spacing=10, expand=True),
                    ft.Container(height=8),
                    ft.Row([model, year, color], spacing=10, expand=True),
                ], spacing=0),
                padding=ft.padding.all(16),
                width=500,
                height=220,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B"),
                            on_click=lambda e: close_add_dialog(add_dialog),
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), color=ft.Colors.WHITE),
                            on_click=save_vehicle,
                            style=ft.ButtonStyle(
                                bgcolor=primary_color,
                                shape=ft.RoundedRectangleBorder(radius=6),
                                elevation=0,
                            ),
                        ),
                    ], spacing=8, alignment=ft.MainAxisAlignment.END),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        def close_add_dialog(d):
            d.open = False
            dialog.update()
        
        page.overlay.append(add_dialog)
        add_dialog.open = True
        page.update()
    
    # Handle vehicle dropdown change (for "add new vehicle" option)
    def on_vehicle_change(e):
        if vehicle_dropdown.value == "new":
            # Show add vehicle dialog
            if customer_dropdown.value:
                selected = next((c for c in customers if str(c.get("id")) == customer_dropdown.value), None)
                if selected:
                    show_add_vehicle_dialog(int(customer_dropdown.value), selected.get("name", ""))
            # Reset dropdown value
            vehicle_dropdown.value = None
            vehicle_dropdown.update()
    
    vehicle_dropdown.on_change = on_vehicle_change
    
    def save(e):
        print(f"DEBUG DIALOG: Save clicked")
        if not customer_dropdown.value:
            customer_dropdown.error_text = get_text("required_field")
            dialog.update()
            return
        if not vehicle_dropdown.value or vehicle_dropdown.value == "new":
            vehicle_dropdown.error_text = get_text("required_field")
            dialog.update()
            return
        if not problem_description.value:
            problem_description.error_text = get_text("required_field")
            dialog.update()
            return
        
        customer_id = int(customer_dropdown.value)
        vehicle_id = int(vehicle_dropdown.value)
        
        print(f"DEBUG DIALOG: customer_id={customer_id}, vehicle_id={vehicle_id}")
        
        data = {
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "problem_description": problem_description.value,
            "mileage": int(mileage.value) if mileage.value else 0,
            "fuel_level": fuel_level.value if fuel_level.value else "",
        }
        on_save(data)
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADD_CIRCLE, size=20, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=10,
                        padding=ft.padding.all(5),
                    ),
                    ft.Text(get_text("new_job_order"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                customer_dropdown,
                ft.Container(height=8),
                customer_info_card,
                ft.Container(height=8),
                vehicle_dropdown,
                ft.Container(height=8),
                problem_description,
                ft.Container(height=8),
                ft.Row([mileage, fuel_level], spacing=10),
            ], spacing=0, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(16),
            width=500,
            height=520,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("create"), color=ft.Colors.WHITE),
                        on_click=save,
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=6),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=20, vertical=6),
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


def show_job_order_detail_dialog(order, primary_color, on_close, on_print=None):
    """Show job order detail dialog with print button"""
    
    order_id = order.get("id")
    job_no = order.get("job_no", "-")
    customer_name = order.get("customer_name", "-")
    customer_phone = order.get("customer_phone", "-")
    plate_number = order.get("plate_number", "-")
    brand = order.get("brand", "-")
    model = order.get("model", "-")
    receive_date = order.get("receive_date", "")
    if receive_date:
        try:
            receive_date = receive_date.split()[0] if " " in receive_date else receive_date[:10]
        except:
            receive_date = "-"
    else:
        receive_date = "-"
    problem = order.get("problem_description", "-")
    mileage = order.get("mileage", 0)
    fuel_level = order.get("fuel_level", "-")
    status = order.get("status", "pending")
    created_by = order.get("created_by_name", "-")
    
    status_colors = {
        "pending": "#FF9800",
        "quoting": "#2196F3",
        "repairing": "#9C27B0",
        "finished": "#4CAF50",
        "closed": "#607D8B",
        "cancelled": "#F44336"
    }
    status_color = status_colors.get(status, "#607D8B")
    status_text = get_text(status)
    
    status_badge = ft.Container(
        content=ft.Text(status_text, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
        bgcolor=status_color,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=12, vertical=4),
    )
    
    actions_row = ft.Row([
        ft.TextButton(
            content=ft.Text(get_text("close"), color="#64748B"),
            on_click=lambda e: on_close(),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        ),
    ], spacing=8, alignment=ft.MainAxisAlignment.END)
    
    if on_print:
        actions_row.controls.insert(0, ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT, size=16, color=primary_color),
                ft.Text(get_text("print"), size=12, color=primary_color),
            ], spacing=4),
            on_click=lambda e: on_print(order_id),
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        ))
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.RECEIPT, size=20, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=10,
                        padding=ft.padding.all(5),
                    ),
                    ft.Text(f"{get_text('job_order_detail')}: {job_no}", size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(get_text("status"), size=12, color="#64748B", width=100),
                    status_badge,
                ], spacing=8),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Text(get_text("customer_information"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("customer_name"), size=11, color="#64748B"),
                        ft.Text(customer_name, size=13, weight=ft.FontWeight.W_500),
                    ], spacing=2, expand=True),
                    ft.Column([
                        ft.Text(get_text("customer_phone"), size=11, color="#64748B"),
                        ft.Text(customer_phone, size=13),
                    ], spacing=2, expand=True),
                ]),
                ft.Text(get_text("vehicle_information"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("plate_number"), size=11, color="#64748B"),
                        ft.Text(plate_number, size=13, weight=ft.FontWeight.W_500),
                    ], spacing=2, expand=True),
                    ft.Column([
                        ft.Text(get_text("car_brand_model"), size=11, color="#64748B"),
                        ft.Text(f"{brand} {model}", size=13),
                    ], spacing=2, expand=True),
                ]),
                ft.Text(get_text("job_details"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("receive_date"), size=11, color="#64748B"),
                        ft.Text(receive_date, size=12),
                    ], spacing=2, expand=True),
                    ft.Column([
                        ft.Text(get_text("mileage"), size=11, color="#64748B"),
                        ft.Text(f"{mileage} km", size=12),
                    ], spacing=2, expand=True),
                    ft.Column([
                        ft.Text(get_text("fuel_level"), size=11, color="#64748B"),
                        ft.Text(fuel_level, size=12),
                    ], spacing=2, expand=True),
                ]),
                ft.Text(get_text("problem_description"), size=11, color="#64748B"),
                ft.Text(problem, size=12, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Row([
                    ft.Text(get_text("service_advisor"), size=11, color="#64748B"),
                    ft.Text(created_by, size=12, color="#64748B", expand=True),
                ], spacing=8),
            ], spacing=12, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(16),
            width=450,
            height=480,
        ),
        actions=[
            ft.Container(
                content=actions_row,
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_status_update_dialog(order, primary_color, on_update, on_close):
    """Show dialog to update order status"""
    
    current_status = order.get("status", "pending")
    
    status_dropdown = ft.Dropdown(
        label=get_text("new_status"),
        value=current_status,
        options=[
            ft.dropdown.Option("pending", get_text("pending")),
            ft.dropdown.Option("quoting", get_text("quoting")),
            ft.dropdown.Option("repairing", get_text("repairing")),
            ft.dropdown.Option("finished", get_text("finished")),
            ft.dropdown.Option("closed", get_text("closed")),
            ft.dropdown.Option("cancelled", get_text("cancelled")),
        ],
        width=300,
    )
    
    def update(e):
        if status_dropdown.value != current_status:
            on_update(status_dropdown.value)
        else:
            on_close()
    
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
                    ft.Text(get_text("update_order_status"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(f"{get_text('job_number')}: {order.get('job_no')}", size=14, weight=ft.FontWeight.W_500),
                ft.Container(height=12),
                status_dropdown,
            ], spacing=0),
            padding=ft.padding.all(16),
            width=350,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("update"), color=ft.Colors.WHITE),
                        on_click=update,
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