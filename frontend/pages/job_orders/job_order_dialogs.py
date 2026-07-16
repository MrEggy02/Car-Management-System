import flet as ft
from i18n import get_text


def show_create_job_order_dialog(primary_color, customers, vehicles_by_customer, on_save, on_close, page):
    """Show dialog to create new job order with modern split layout"""
    
    print(f"DEBUG DIALOG: customers count = {len(customers)}")
    print(f"DEBUG DIALOG: vehicles_by_customer keys = {list(vehicles_by_customer.keys())}")
    
    # ==================== LEFT PANE - VEHICLE INFO ====================
    
    # Customer selection
    customer_dropdown = ft.Dropdown(
        label=get_text("select_customer"),
        hint_text=get_text("search_and_select_customer"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        options=[
            ft.dropdown.Option(str(c.get("id")), f"{c.get('name')} - {c.get('phone', '-')}")
            for c in customers
        ],
        expand=True,
    )
    
    # Vehicle selection
    vehicle_dropdown = ft.Dropdown(
        label=get_text("select_vehicle"),
        hint_text=get_text("select_vehicle"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        options=[],
        expand=True,
    )
    
    # Customer info display
    customer_name_text = ft.Text("", size=13, weight=ft.FontWeight.W_500, color="#1E293B")
    customer_phone_text = ft.Text("", size=12, color="#64748B")
    customer_info_card = ft.Container(
        content=ft.Column([
            ft.Text(get_text("customer_information"), size=11, weight=ft.FontWeight.W_600, color=primary_color),
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            customer_name_text,
            customer_phone_text,
        ], spacing=6),
        padding=ft.Padding(left=12, right=12, top=12, bottom=12),
        bgcolor=ft.Colors.GREY_50,
        border_radius=10,
        visible=False,
    )
    
    # Problem description
    problem_description = ft.TextField(
        label=get_text("problem_description"),
        hint_text=get_text("problem_description_hint"),
        multiline=True,
        min_lines=4,
        max_lines=6,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=14, right=14, top=12, bottom=12),
        expand=True,
    )
    
    # Mileage and fuel level
    mileage = ft.TextField(
        label=get_text("mileage"),
        hint_text="0",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        expand=True,
        input_filter=ft.NumbersOnlyInputFilter(),
    )
    
    fuel_level = ft.Dropdown(
        label=get_text("fuel_level"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        options=[
            ft.dropdown.Option("full", "ເຕັມຖັງ (Full)"),
            ft.dropdown.Option("3/4", "3/4 ຖັງ"),
            ft.dropdown.Option("1/2", "1/2 ຖັງ"),
            ft.dropdown.Option("1/4", "1/4 ຖັງ"),
            ft.dropdown.Option("empty", "ໃກ້ໝົດ (Empty)"),
        ],
        expand=True,
    )
    
    # Vehicle info section (Left Pane Top)
    vehicle_info_section = ft.Container(
        content=ft.Column([
            ft.Text("ຂໍ້ມູນລົດ ແລະ ບັນຫາ", size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
            ft.Container(height=8),
            customer_dropdown,
            ft.Container(height=8),
            vehicle_dropdown,
            ft.Container(height=8),
            customer_info_card,
            ft.Container(height=8),
            problem_description,
        ], spacing=0),
        expand=True,
    )
    
    # Selected items storage
    temp_items = []
    temp_id_counter = 0
    
    # Selected items list (Left Pane Bottom)
    selected_items_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=150)
    
    # Total amount display
    total_amount = ft.Text("0 KIP", size=16, weight=ft.FontWeight.BOLD, color=primary_color)
    
    def update_total_display():
        total = sum(item.get("total", 0) for item in temp_items)
        total_amount.value = f"{int(total):,} KIP"
        if dialog_ref:
            dialog_ref.update()
    
    def display_selected_items():
        selected_items_list.controls.clear()
        
        if not temp_items:
            selected_items_list.controls.append(
                ft.Container(
                    content=ft.Text("ຍັງບໍ່ມີລາຍການທີ່ເລືອກ", size=12, color="#94A3B8"),
                    padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                    alignment=ft.Alignment(0, 0),
                )
            )
            return
        
        # Group items by type
        parts_items = [item for item in temp_items if item.get("item_type") == "part"]
        service_items = [item for item in temp_items if item.get("item_type") == "service"]
        
        if parts_items:
            selected_items_list.controls.append(
                ft.Text("ອາໄຫຼ່", size=12, weight=ft.FontWeight.W_600, color=primary_color)
            )
            for item in parts_items:
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(f"{item.get('qty')}x", size=12, weight=ft.FontWeight.W_500, color=primary_color),
                            width=35,
                        ),
                        ft.Column([
                            ft.Text(item.get("name", "-"), size=12, weight=ft.FontWeight.W_500, max_lines=1),
                            ft.Text(f"{int(item.get('unit_price', 0)):,} KIP", size=10, color="#64748B"),
                        ], spacing=1, expand=True),
                        ft.Text(f"{int(item.get('total', 0)):,} KIP", size=12, weight=ft.FontWeight.W_500, color="#1E293B", width=90),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, tid=item.get("temp_id"): remove_item(tid),
                            padding=0,
                        ),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=8, right=8, top=6, bottom=6),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=6,
                )
                selected_items_list.controls.append(item_row)
        
        if service_items:
            selected_items_list.controls.append(
                ft.Text("ບໍລິການ", size=12, weight=ft.FontWeight.W_600, color=primary_color)
            )
            for item in service_items:
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(f"{item.get('qty')}x", size=12, weight=ft.FontWeight.W_500, color=primary_color),
                            width=35,
                        ),
                        ft.Column([
                            ft.Text(item.get("name", "-"), size=12, weight=ft.FontWeight.W_500, max_lines=1),
                            ft.Text(f"{int(item.get('unit_price', 0)):,} KIP", size=10, color="#64748B"),
                        ], spacing=1, expand=True),
                        ft.Text(f"{int(item.get('total', 0)):,} KIP", size=12, weight=ft.FontWeight.W_500, color="#1E293B", width=90),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, tid=item.get("temp_id"): remove_item(tid),
                            padding=0,
                        ),
                    ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=8, right=8, top=6, bottom=6),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=6,
                )
                selected_items_list.controls.append(item_row)
        
        update_total_display()
    
    def remove_item(temp_id):
        nonlocal temp_items
        temp_items = [item for item in temp_items if item.get("temp_id") != temp_id]
        display_selected_items()
        if dialog_ref:
            dialog_ref.update()
    
    def add_item(item_type, ref_id, name, price):
        nonlocal temp_id_counter
        temp_id_counter += 1
        qty = int(qty_field.value) if qty_field.value else 1
        temp_items.append({
            "temp_id": temp_id_counter,
            "item_type": item_type,
            "ref_id": ref_id,
            "name": name,
            "qty": qty,
            "unit_price": price,
            "total": qty * price
        })
        display_selected_items()
        if dialog_ref:
            dialog_ref.update()
    
    # Selected items section (Left Pane Bottom)
    selected_items_section = ft.Container(
        content=ft.Column([
            ft.Text("ສະແດງຂໍ້ມູນທີ່ເລືອກ ແຍກ ອາໄຫຼ່ ກັບບໍລິການ", size=12, weight=ft.FontWeight.W_500, color="#64748B"),
            ft.Container(height=6),
            selected_items_list,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            ft.Row([
                ft.Text("ຍອດລວມ:", size=13, weight=ft.FontWeight.W_500),
                ft.Container(expand=True),
                total_amount,
            ]),
        ], spacing=4),
        expand=True,
    )
    
    # Left Pane
    left_pane = ft.Container(
        content=ft.Column([
            vehicle_info_section,
            ft.Container(height=12),
            ft.Row([mileage, fuel_level], spacing=10),
            ft.Container(height=12),
            selected_items_section,
        ], spacing=0),
        expand=True,
        bgcolor="#FAFBFC",
        border_radius=12,
        padding=ft.Padding(left=16, right=16, top=16, bottom=16),
    )
    
    # ==================== RIGHT PANE - SELECT ITEMS ====================
    
    # Tab buttons
    parts_tab = ft.Container(
        content=ft.Text(get_text("parts"), size=13, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
        bgcolor=primary_color,
        border_radius=8,
        padding=ft.Padding(left=20, right=20, top=8, bottom=8),
        expand=True,
    )
    
    services_tab = ft.Container(
        content=ft.Text(get_text("services"), size=13, weight=ft.FontWeight.W_600, color="#64748B"),
        bgcolor=ft.Colors.GREY_200,
        border_radius=8,
        padding=ft.Padding(left=20, right=20, top=8, bottom=8),
        expand=True,
    )
    
    # Search field
    search_field = ft.TextField(
        hint_text=get_text("search_items"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.SEARCH,
        content_padding=ft.Padding(left=14, right=14, top=12, bottom=12),
        expand=True,
    )
    
    qty_field = ft.TextField(
        label=get_text("quantity"),
        value="1",
        width=90,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        input_filter=ft.NumbersOnlyInputFilter(),
        text_align=ft.TextAlign.CENTER,
        content_padding=ft.Padding(left=10, right=10, top=8, bottom=8),
    )
    
    # Results list
    results_list = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=220)
    
    current_tab = "parts"
    current_category = "all"
    
    # Categories for parts
    categories = [
        {"id": "all", "name": "ທັງໝົດ"},
        {"id": "engine", "name": "ເຄື່ອງຈັກ"},
        {"id": "brake", "name": "ເບຣກ"},
        {"id": "electrical", "name": "ໄຟຟ້າ"},
        {"id": "suspension", "name": "ຊ່ວງລຸ່ມ"},
        {"id": "cooling", "name": "ລະບົບຄວາມເຢັນ"},
    ]
    
    category_chips = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
    
    def load_category_chips():
        category_chips.controls.clear()
        for cat in categories:
            is_active = current_category == cat["id"]
            chip = ft.Container(
                content=ft.Text(cat["name"], size=11, weight=ft.FontWeight.W_500, 
                               color=ft.Colors.WHITE if is_active else "#64748B"),
                bgcolor=primary_color if is_active else ft.Colors.GREY_200,
                border_radius=20,
                padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                ink=True,
                on_click=lambda e, cid=cat["id"]: filter_by_category(cid),
            )
            category_chips.controls.append(chip)
    
    def filter_by_category(category_id):
        nonlocal current_category
        current_category = category_id
        load_category_chips()
        search_items(search_field.value if search_field.value else "")
    
    def search_items(keyword):
        results_list.controls.clear()
        
        if current_tab == "parts":
            # Sample parts data - replace with actual API call
            results = [
                {"id": 1, "name": "ນ້ຳມັນເຄື່ອງ 10W-40", "price": 120000, "category": "engine", "stock": 15},
                {"id": 2, "name": "ຜ້າເບກໜ້າ Toyota", "price": 450000, "category": "brake", "stock": 8},
                {"id": 3, "name": "ໝໍ້ໄຟ 12V 60Ah", "price": 850000, "category": "electrical", "stock": 5},
                {"id": 4, "name": "ໂຊ້ກໜ້າ", "price": 750000, "category": "suspension", "stock": 6},
                {"id": 5, "name": "ນ້ຳຢາຫຼໍ່ເຢັນ", "price": 65000, "category": "cooling", "stock": 20},
            ]
            
            if current_category != "all":
                results = [r for r in results if r.get("category") == current_category]
            if keyword:
                results = [r for r in results if keyword.lower() in r.get("name", "").lower()]
            
            for part in results[:20]:
                item = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(part.get("name", "-"), size=12, weight=ft.FontWeight.W_500),
                            ft.Text(f"ສະຕ໋ອກ: {part.get('stock', 0)} | {int(part.get('price', 0)):,} KIP", size=10, color="#64748B"),
                        ], expand=True, spacing=2),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            icon_size=22,
                            icon_color=primary_color,
                            on_click=lambda e, pid=part.get('id'), pname=part.get('name'), pprice=part.get('price'): add_item("part", pid, pname, pprice),
                        ),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=10, right=10, top=8, bottom=8),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                )
                results_list.controls.append(item)
        else:
            # Sample services data
            results = [
                {"id": 1, "name": "ປ່ຽນນ້ຳມັນເຄື່ອງ", "price": 250000},
                {"id": 2, "name": "ປ່ຽນຜ້າເບກ", "price": 350000},
                {"id": 3, "name": "ກວດເຊັກລະບົບໄຟຟ້າ", "price": 200000},
                {"id": 4, "name": "ລ້າງແອ", "price": 450000},
            ]
            
            if keyword:
                results = [r for r in results if keyword.lower() in r.get("name", "").lower()]
            
            for service in results[:20]:
                item = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(service.get("name", "-"), size=12, weight=ft.FontWeight.W_500),
                            ft.Text(f"{int(service.get('price', 0)):,} KIP", size=10, color="#64748B"),
                        ], expand=True, spacing=2),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                            icon_size=22,
                            icon_color=primary_color,
                            on_click=lambda e, sid=service.get('id'), sname=service.get('name'), sprice=service.get('price'): add_item("service", sid, sname, sprice),
                        ),
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=10, right=10, top=8, bottom=8),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                )
                results_list.controls.append(item)
        
        if not results_list.controls:
            results_list.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_items_found"), size=12, color="#94A3B8"),
                    padding=ft.Padding(left=20, right=20, top=20, bottom=20),
                    alignment=ft.Alignment(0, 0),
                )
            )
        if dialog_ref:
            dialog_ref.update()
    
    def switch_tab(tab):
        nonlocal current_tab, current_category
        current_tab = tab
        current_category = "all"
        if tab == "parts":
            parts_tab.bgcolor = primary_color
            parts_tab.content.color = ft.Colors.WHITE
            services_tab.bgcolor = ft.Colors.GREY_200
            services_tab.content.color = "#64748B"
            search_field.hint_text = get_text("search_parts")
            load_category_chips()
            category_chips.visible = True
        else:
            services_tab.bgcolor = primary_color
            services_tab.content.color = ft.Colors.WHITE
            parts_tab.bgcolor = ft.Colors.GREY_200
            parts_tab.content.color = "#64748B"
            search_field.hint_text = get_text("search_services")
            category_chips.controls.clear()
            category_chips.visible = False
        search_field.value = ""
        search_items("")
        if dialog_ref:
            dialog_ref.update()
    
    def on_search_change(e):
        search_items(e.control.value.lower() if e.control.value else "")
    
    def on_parts_click(e):
        switch_tab("parts")
    
    def on_services_click(e):
        switch_tab("services")
    
    # Right Pane
    right_pane = ft.Container(
        content=ft.Column([
            ft.Text("ເລືອກ ອາໄຫຼ່ ແລະ ບໍລິການ - ເລືອກຕາມປະເພດອາໄຫຼ່", size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
            ft.Container(height=8),
            ft.Row([parts_tab, services_tab], spacing=8),
            ft.Container(height=8),
            category_chips,
            ft.Container(height=8),
            ft.Row([search_field, qty_field], spacing=10),
            ft.Container(height=8),
            ft.Container(
                content=results_list,
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                border_radius=10,
                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                height=240,
            ),
        ], spacing=0),
        expand=True,
        bgcolor="#FAFBFC",
        border_radius=12,
        padding=ft.Padding(left=16, right=16, top=16, bottom=16),
    )
    
    # Main content with two columns
    main_content = ft.Container(
        content=ft.Row([
            left_pane,
            ft.Container(width=16),
            right_pane,
        ], spacing=0, expand=True),
        width=950,
        height=620,
        padding=ft.Padding(left=16, right=16, top=16, bottom=16),
    )
    
    # ==================== EVENT HANDLERS ====================
    
    def on_customer_change(e):
        print(f"DEBUG DIALOG: Customer selected: {customer_dropdown.value}")
        if customer_dropdown.value:
            selected = next((c for c in customers if str(c.get("id")) == customer_dropdown.value), None)
            if selected:
                customer_name_text.value = selected.get("name", "")
                customer_phone_text.value = selected.get("phone", "")
                customer_info_card.visible = True
                
                customer_id = int(customer_dropdown.value)
                vehicles_list = vehicles_by_customer.get(customer_id, [])
                print(f"DEBUG DIALOG: Vehicles found for customer {customer_id}: {len(vehicles_list)}")
                
                # DEBUG: Print raw vehicles data
                for v in vehicles_list:
                    print(f"DEBUG: Vehicle data - id: {v.get('id')}, plate: {v.get('plate_number')}, brand: {v.get('brand')}, model: {v.get('model')}")
                
                # Clear and set new options
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
                    
                    print(f"DEBUG DIALOG: Adding vehicle option: id={v.get('id')}, text={display_text}")
                    vehicle_dropdown.options.append(
                        ft.dropdown.Option(str(v.get("id")), display_text)
                    )
                
                if vehicles_list:
                    vehicle_dropdown.options.append(
                        ft.dropdown.Option("new", f"+ {get_text('add_new_vehicle')}")
                    )
                
                # Force update
                vehicle_dropdown.update()
                if dialog_ref:
                    dialog_ref.update()
                if page:
                    page.update()
        else:
            customer_info_card.visible = False
            vehicle_dropdown.options.clear()
            vehicle_dropdown.update()
            if dialog_ref:
                dialog_ref.update()
            if page:
                page.update()
    
    def on_vehicle_change(e):
        if vehicle_dropdown.value == "new":
            if customer_dropdown.value:
                selected = next((c for c in customers if str(c.get("id")) == customer_dropdown.value), None)
                if selected:
                    show_add_vehicle_dialog(int(customer_dropdown.value), selected.get("name", ""))
            vehicle_dropdown.value = None
            vehicle_dropdown.update()
    
    def save(e):
        print(f"DEBUG DIALOG: Save clicked")
        if not customer_dropdown.value:
            customer_dropdown.error_text = get_text("required_field")
            if dialog_ref:
                dialog_ref.update()
            return
        if not vehicle_dropdown.value or vehicle_dropdown.value == "new":
            vehicle_dropdown.error_text = get_text("required_field")
            if dialog_ref:
                dialog_ref.update()
            return
        if not problem_description.value:
            problem_description.error_text = get_text("required_field")
            if dialog_ref:
                dialog_ref.update()
            return
        
        customer_id = int(customer_dropdown.value)
        vehicle_id = int(vehicle_dropdown.value)
        
        data = {
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "problem_description": problem_description.value,
            "mileage": int(mileage.value) if mileage.value else 0,
            "fuel_level": fuel_level.value if fuel_level.value else "",
        }
        on_save(data)
    
    # Set up event handlers
    customer_dropdown.on_change = on_customer_change
    vehicle_dropdown.on_change = on_vehicle_change
    search_field.on_change = on_search_change
    parts_tab.on_click = on_parts_click
    services_tab.on_click = on_services_click
    
    # Initialize
    load_category_chips()
    
    # Create dialog reference
    dialog_ref = None
    
    # Create dialog
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=16),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADD_CIRCLE, size=22, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=10,
                        padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                    ),
                    ft.Text(get_text("new_job_order"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=20, right=20, top=14, bottom=14),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=main_content,
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("create"), size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=save,
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.Padding(left=24, right=24, top=10, bottom=10),
                        ),
                    ),
                ], spacing=12, alignment=ft.MainAxisAlignment.END),
                padding=ft.Padding(left=20, right=20, top=14, bottom=14),
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    dialog_ref = dialog
    
    # ==================== ADD VEHICLE DIALOG ====================
    
    def show_add_vehicle_dialog(customer_id, customer_name):
        """Show dialog to add new vehicle"""
        from api_client import APIClient
        brands = []
        try:
            temp_client = APIClient()
            brands = temp_client.get_brands() or []
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
                    new_vehicles = temp_client.get_vehicles(customer_id=customer_id) or []
                    vehicles_list = []
                    for v in new_vehicles:
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
                    
                    vehicles_by_customer[customer_id] = vehicles_list
                    
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
                    
                    def show_snackbar(message):
                        snack = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.GREY_800, duration=3000)
                        if page:
                            page.snack_bar = snack
                            page.snack_bar.open = True
                            page.update()
                    
                    show_snackbar(f"{get_text('vehicle_added_successfully')}")
            except Exception as err:
                def show_snackbar(message):
                    snack = ft.SnackBar(content=ft.Text(message), bgcolor=ft.Colors.GREY_800, duration=3000)
                    if page:
                        page.snack_bar = snack
                        page.snack_bar.open = True
                        page.update()
                show_snackbar(f"{get_text('error')}: {err}")
        
        def close_add_dialog(d):
            d.open = False
            dialog.update()
        
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
                            padding=ft.Padding(left=5, right=5, top=5, bottom=5),
                        ),
                        ft.Text(f"{get_text('add_new_vehicle')} - {customer_name}", size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([plate_number, brand_dropdown], spacing=10, expand=True),
                    ft.Container(height=8),
                    ft.Row([model, year, color], spacing=10, expand=True),
                ], spacing=0),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
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
                    padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(add_dialog)
        add_dialog.open = True
        page.update()
    
    return dialog


def show_job_order_detail_dialog(order, primary_color, on_close, on_print=None, receipt_url=None):
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
    car_defects = order.get("car_defects", "")
    if not car_defects:
        car_defects = "-"
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
        padding=ft.Padding(left=12, right=12, top=4, bottom=4),
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
    
    content_controls = [
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
        ft.Text("ຕຳນິເດີມຂອງລົດ (Car Defects)", size=11, color="#64748B"),
        ft.Text(car_defects, size=12, color="#1E293B"),
        ft.Divider(height=1, color=ft.Colors.GREY_100),
        ft.Row([
            ft.Text(get_text("service_advisor"), size=11, color="#64748B"),
            ft.Text(created_by, size=12, color="#64748B", expand=True),
        ], spacing=8),
    ]

    if receipt_url:
        content_controls.append(ft.Divider(height=1, color=ft.Colors.GREY_100))
        content_controls.append(ft.Text("ຮູບໃບສັນຍາ (Receipt Image)", size=11, color="#64748B"))
        content_controls.append(
            ft.Container(
                content=ft.Image(src=receipt_url, fit="contain"),
                border_radius=8,
                border=ft.Border(
                    top=ft.BorderSide(1, ft.Colors.GREY_200), 
                    right=ft.BorderSide(1, ft.Colors.GREY_200), 
                    bottom=ft.BorderSide(1, ft.Colors.GREY_200), 
                    left=ft.BorderSide(1, ft.Colors.GREY_200)
                ),
                padding=5,
                height=200,
                alignment=ft.Alignment(0, 0)
            )
        )

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
                        padding=ft.Padding(left=5, right=5, top=5, bottom=5),
                    ),
                    ft.Text(f"{get_text('job_order_detail')}: {job_no}", size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column(content_controls, spacing=12, scroll=ft.ScrollMode.AUTO),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            width=450,
            height=480,
        ),
        actions=[
            ft.Container(
                content=actions_row,
                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
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
                        padding=ft.Padding(left=5, right=5, top=5, bottom=5),
                    ),
                    ft.Text(get_text("update_order_status"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(f"{get_text('job_number')}: {order.get('job_no')}", size=14, weight=ft.FontWeight.W_500),
                ft.Container(height=12),
                status_dropdown,
            ], spacing=0),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
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
                            padding=ft.Padding(left=16, right=16, top=6, bottom=6),
                        ),
                    ),
                ], spacing=8, alignment=ft.MainAxisAlignment.END),
                padding=ft.Padding(left=16, right=16, top=10, bottom=10),
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog