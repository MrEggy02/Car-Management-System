# pages/quotations/quotation_dialogs.py
import flet as ft
from i18n import get_text


def show_create_quotation_dialog(primary_color, parts_list, services_list, pending_orders, on_save, on_approve, on_close, show_snack):
    """Show dialog to create new quotation"""
    
    selected_job_id = None
    temp_items = []
    temp_id_counter = 0
    current_tab = "parts"
    dialog_ref = None
    
    # Job order dropdown
    job_order_dropdown = ft.Dropdown(
        label=get_text("select_job_order"),
        hint_text=get_text("select_job_order_for_quotation"),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        height=38,
        options=[
            ft.dropdown.Option(
                str(o.get("id")), 
                f"{o.get('job_no')} - {o.get('customer_name')} - {o.get('plate_number')}"
            )
            for o in pending_orders
        ],
        expand=True,
    )
    
    # Selected job info display
    job_info_text = ft.Text("", size=12, color="#64748B")
    job_info_container = ft.Container(
        content=ft.Column([
            ft.Text(get_text("selected_job"), size=11, weight=ft.FontWeight.W_500, color="#64748B"),
            job_info_text,
        ]),
        padding=ft.Padding(left=10, right=10, top=8, bottom=8),
        bgcolor=ft.Colors.GREY_50,
        border_radius=6,
        visible=False,
    )
    
    # Tab buttons
    parts_btn = ft.Container(
        content=ft.Text(get_text("parts"), size=12, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
        bgcolor=primary_color,
        border_radius=6,
        padding=ft.Padding(left=16, right=16, top=4, bottom=4),
    )
    
    services_btn = ft.Container(
        content=ft.Text(get_text("services"), size=12, weight=ft.FontWeight.W_500, color="#64748B"),
        bgcolor=ft.Colors.GREY_200,
        border_radius=6,
        padding=ft.Padding(left=16, right=16, top=4, bottom=4),
    )
    
    # Search field
    search_field = ft.TextField(
        hint_text=get_text("search_items"),
        border_radius=6,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.SEARCH,
        content_padding=ft.Padding(left=12, right=12, top=4, bottom=4),
        expand=True,
        height=38,
        text_size=12,
    )
    
    qty_field = ft.TextField(
        label=get_text("quantity"),
        value="1",
        width=70,
        border_radius=6,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        input_filter=ft.NumbersOnlyInputFilter(),
        text_align=ft.TextAlign.CENTER,
        height=38,
        text_size=12,
        content_padding=ft.Padding(left=8, right=8, top=4, bottom=4),
    )
    
    # Results list
    results_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=180)
    
    # Items list
    items_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=120)
    
    # Total display
    total_text = ft.Text("0 KIP", size=16, weight=ft.FontWeight.BOLD, color=primary_color)
    
    def update_total_display():
        total = sum(item.get("total", 0) for item in temp_items)
        total_text.value = f"{int(total):,} KIP"
        if dialog_ref:
            dialog_ref.update()
    
    def display_items():
        items_list.controls.clear()
        for item in temp_items:
            try:
                unit_price = float(item.get("unit_price", 0))
            except (TypeError, ValueError):
                unit_price = 0
            try:
                total = float(item.get("total", 0))
            except (TypeError, ValueError):
                total = 0
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Text(f"{item.get('qty')}x", size=11, weight=ft.FontWeight.W_500, color=primary_color, width=35),
                    ft.Column([
                        ft.Text(item.get("name", "-"), size=11, weight=ft.FontWeight.W_500, max_lines=1),
                        ft.Text(f"{int(unit_price):,} KIP", size=9, color="#64748B"),
                    ], spacing=1, expand=True),
                    ft.Text(f"{int(total):,} KIP", size=11, weight=ft.FontWeight.W_500, color="#1E293B", width=90),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=14,
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, tid=item.get("temp_id"): remove_item(tid),
                    ),
                ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=6, right=6, top=4, bottom=4),
                bgcolor=ft.Colors.GREY_50,
                border_radius=4,
            )
            items_list.controls.append(item_row)
        update_total_display()
    
    def remove_item(temp_id):
        nonlocal temp_items
        temp_items = [item for item in temp_items if item.get("temp_id") != temp_id]
        display_items()
        if dialog_ref:
            dialog_ref.update()
    
    def add_item(item_type, ref_id, name, price):
        qty = int(qty_field.value) if qty_field.value and qty_field.value.isdigit() else 1
        try:
            price = float(price)
        except (TypeError, ValueError):
            price = 0
            
        # Check if item already exists in temp_items and update quantity
        existing = next((item for item in temp_items if item.get("item_type") == item_type and item.get("ref_id") == ref_id), None)
        if existing:
            existing["qty"] += qty
            existing["total"] = existing["qty"] * existing["unit_price"]
        else:
            nonlocal temp_id_counter
            temp_id_counter += 1
            temp_items.append({
                "temp_id": temp_id_counter,
                "item_type": item_type,
                "ref_id": ref_id,
                "name": name,
                "qty": qty,
                "unit_price": price,
                "total": qty * price
            })
            
        display_items()
        if dialog_ref:
            dialog_ref.update()
    
    def switch_tab(tab):
        nonlocal current_tab
        current_tab = tab
        if tab == "parts":
            parts_btn.bgcolor = primary_color
            parts_btn.content.color = ft.Colors.WHITE
            services_btn.bgcolor = ft.Colors.GREY_200
            services_btn.content.color = "#64748B"
            search_field.hint_text = get_text("search_parts")
        else:
            services_btn.bgcolor = primary_color
            services_btn.content.color = ft.Colors.WHITE
            parts_btn.bgcolor = ft.Colors.GREY_200
            parts_btn.content.color = "#64748B"
            search_field.hint_text = get_text("search_services")
        search_field.value = ""
        search_items("")
        if dialog_ref:
            dialog_ref.update()
    
    def search_items(keyword):
        results_list.controls.clear()
        if current_tab == "parts":
            results = parts_list
            if keyword:
                results = [p for p in results if keyword.lower() in p.get("name", "").lower()]
            
            for part in results[:15]:
                try:
                    sell_price = float(part.get('sell_price', 0))
                except (TypeError, ValueError):
                    sell_price = 0
                    
                item = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(part.get("name", "-"), size=11, weight=ft.FontWeight.W_500, max_lines=1),
                            ft.Text(f"Stock: {part.get('stock_qty', 0)}", size=9, color="#64748B"),
                        ], expand=True, spacing=1),
                        ft.Text(f"{int(sell_price):,} KIP", size=11, weight=ft.FontWeight.W_500, color=primary_color),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_size=18,
                            icon_color=primary_color,
                            on_click=lambda e, pid=part.get('id'), pname=part.get('name'), pprice=sell_price: add_item("part", pid, pname, pprice),
                        ),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=4,
                )
                results_list.controls.append(item)
        else:
            results = services_list
            if keyword:
                results = [s for s in results if keyword.lower() in s.get("name", "").lower()]
            
            for service in results[:15]:
                try:
                    price = float(service.get('price', 0))
                except (TypeError, ValueError):
                    price = 0
                    
                item = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(service.get("name", "-"), size=11, weight=ft.FontWeight.W_500, max_lines=1),
                            ft.Text(service.get("description", "-")[:20], size=9, color="#64748B"),
                        ], expand=True, spacing=1),
                        ft.Text(f"{int(price):,} KIP", size=11, weight=ft.FontWeight.W_500, color=primary_color),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_size=18,
                            icon_color=primary_color,
                            on_click=lambda e, sid=service.get('id'), sname=service.get('name'), sprice=price: add_item("service", sid, sname, sprice),
                        ),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=4,
                )
                results_list.controls.append(item)
        
        if not results_list.controls:
            results_list.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_items_found"), size=11, color="#64748B"),
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                    alignment=ft.Alignment(0, 0),
                )
            )
        if dialog_ref:
            dialog_ref.update()
    
    def on_job_select(e):
        nonlocal selected_job_id
        if job_order_dropdown.value:
            selected_job_id = int(job_order_dropdown.value)
            order = next((o for o in pending_orders if o.get("id") == selected_job_id), None)
            if order:
                job_info_text.value = f"{order.get('job_no')} - {order.get('customer_name')} - {order.get('plate_number')}"
                job_info_container.visible = True
        else:
            job_info_container.visible = False
        if dialog_ref:
            dialog_ref.update()
    
    def on_search_change(e):
        search_items(e.control.value.lower() if e.control.value else "")
    
    def on_parts_click(e):
        switch_tab("parts")
    
    def on_services_click(e):
        switch_tab("services")
    
    # Error labels
    job_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    items_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
    
    def validate_fields():
        is_valid = True
        
        if not selected_job_id:
            job_error.value = get_text("please_select_job_order")
            job_error.visible = True
            is_valid = False
        else:
            job_error.visible = False
        
        if not temp_items:
            items_error.value = get_text("please_add_at_least_one_item")
            items_error.visible = True
            is_valid = False
        else:
            items_error.visible = False
        
        if dialog_ref:
            dialog_ref.update()
        
        return is_valid
    
    def save(e):
        if not validate_fields():
            return
        on_save(selected_job_id, temp_items)
    
    def approve(e):
        if not validate_fields():
            return
        on_approve(selected_job_id, temp_items)
    
    # Create dialog
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=12),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.REQUEST_QUOTE, size=18, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=8,
                        padding=ft.Padding(left=5, right=5, top=5, bottom=5),
                    ),
                    ft.Text(get_text("new_quotation"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Column([
                    job_order_dropdown,
                    job_error,
                ], spacing=1),
                job_info_container,
                ft.Container(height=8),
                ft.Row([parts_btn, services_btn], spacing=8),
                ft.Container(height=8),
                ft.Row([search_field, qty_field], spacing=8),
                results_list,
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Row([
                    ft.Text(get_text("items"), size=12, weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),
                    ft.Text(get_text("total"), size=11, color="#64748B"),
                    total_text,
                ]),
                ft.Column([
                    items_list,
                    items_error,
                ], spacing=1),
            ], spacing=6, scroll=ft.ScrollMode.AUTO),
            width=500,
            height=520,
            padding=ft.Padding(left=14, right=14, top=12, bottom=8),
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
                        on_click=save,
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.Padding(left=16, right=16, top=6, bottom=6),
                        ),
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ft.Colors.WHITE),
                            ft.Text(get_text("approve"), size=13, color=ft.Colors.WHITE),
                        ], spacing=4),
                        on_click=approve,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN_600,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.Padding(left=16, right=16, top=6, bottom=6),
                        ),
                    ),
                ], spacing=6, alignment=ft.MainAxisAlignment.END),
                padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Set dialog reference
    dialog_ref = dialog
    
    # Set up event handlers
    job_order_dropdown.on_change = on_job_select
    parts_btn.on_click = on_parts_click
    services_btn.on_click = on_services_click
    search_field.on_change = on_search_change
    
    return dialog


def show_quotation_detail_dialog(quotation, primary_color, on_print, on_close):
    """Show quotation detail dialog"""
    
    items = quotation.get("items", [])
    
    items_column = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)
    
    if not items:
        items_column.controls.append(
            ft.Container(
                content=ft.Text(get_text("no_items"), size=12, color="#64748B"),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                alignment=ft.Alignment(0, 0),
            )
        )
    else:
        for item in items:
            item_type = item.get("item_type")
            name = item.get("name", "-")
            qty = item.get("qty", 1)
            unit_price = item.get("unit_price", 0)
            item_total = item.get("total", 0)
            
            try:
                unit_price = float(unit_price)
            except (TypeError, ValueError):
                unit_price = 0
            
            try:
                item_total = float(item_total)
            except (TypeError, ValueError):
                item_total = 0
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.INVENTORY if item_type == "part" else ft.Icons.BUILD, 
                                       size=16, color=primary_color),
                        width=24,
                    ),
                    ft.Column([
                        ft.Text(name, size=12, weight=ft.FontWeight.W_500, max_lines=1),
                        ft.Row([
                            ft.Text(f"{get_text('qty')}: {qty}", size=9, color="#64748B"),
                            ft.Text(f"{int(unit_price):,} KIP", size=9, color="#64748B"),
                        ], spacing=6),
                    ], spacing=1, expand=True),
                    ft.Text(f"{int(item_total):,} KIP", size=12, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                bgcolor=ft.Colors.GREY_50,
                border_radius=6,
            )
            items_column.controls.append(item_row)
    
    # Get total amount from net_total or sub_total
    total_amount = quotation.get('net_total', quotation.get('sub_total', 0))
    try:
        total_amount = float(total_amount)
    except (TypeError, ValueError):
        total_amount = 0
    
    scrollable_content = ft.Column(
        [
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.REQUEST_QUOTE, size=20, color=primary_color),
                    bgcolor="#E3F2FD",
                    border_radius=8,
                    padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                ),
                ft.Column([
                    ft.Text(f"{get_text('quotation')} #{quotation.get('id')}", size=15, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{get_text('status')}: {quotation.get('status', 'draft')}", size=10, color="#64748B"),
                ], spacing=1),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=1, color=ft.Colors.GREY_100),
            ft.Container(height=4),
            ft.Row([
                ft.Column([
                    ft.Text(get_text("job_number"), size=10, color="#64748B"),
                    ft.Text(quotation.get("job_no", "-"), size=12, weight=ft.FontWeight.W_500),
                ], expand=True),
                ft.Column([
                    ft.Text(get_text("customer_name"), size=10, color="#64748B"),
                    ft.Text(quotation.get("customer_name", "-"), size=12, weight=ft.FontWeight.W_500),
                ], expand=True),
            ]),
            ft.Row([
                ft.Column([
                    ft.Text(get_text("plate_number"), size=10, color="#64748B"),
                    ft.Text(quotation.get("plate_number", "-"), size=12, weight=ft.FontWeight.W_500),
                ], expand=True),
                ft.Column([
                    ft.Text(get_text("created_date"), size=10, color="#64748B"),
                    ft.Text(quotation.get("created_at", "-")[:10] if quotation.get("created_at") else "-", size=12, weight=ft.FontWeight.W_500),
                ], expand=True),
            ]),
            ft.Container(height=6),
            ft.Text(get_text("items"), size=12, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=items_column,
                height=200,
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                border_radius=6,
                padding=ft.Padding(left=6, right=6, top=6, bottom=6),
            ),
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            ft.Row([
                ft.Text(get_text("total"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Container(expand=True),
                ft.Text(f"{int(total_amount):,} KIP", size=16, weight=ft.FontWeight.BOLD, color=primary_color),
            ]),
        ],
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    
    dialog_content = ft.Container(
        content=scrollable_content,
        width=460,
        height=420,
        padding=ft.Padding(left=14, right=14, top=12, bottom=8),
    )
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=12),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.INFO, size=18, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=8,
                        padding=ft.Padding(left=5, right=5, top=5, bottom=5),
                    ),
                    ft.Text(get_text("quotation_details"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=dialog_content,
        actions=[
            ft.TextButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.PRINT, size=16, color=primary_color),
                    ft.Text(get_text("print"), size=12, color=primary_color),
                ], spacing=4),
                on_click=lambda e: on_print(quotation.get("id")),
            ),
            ft.TextButton(
                content=ft.Text(get_text("close"), size=12, color="#64748B"),
                on_click=lambda e: on_close(),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_update_status_dialog(quotation_id, current_status, primary_color, on_update, on_close):
    """Show dialog to update quotation status"""
    
    status_dropdown = ft.Dropdown(
        label=get_text("select_status"),
        value=current_status,
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
        height=38,
        options=[
            ft.dropdown.Option("draft", get_text("draft")),
            ft.dropdown.Option("approved", get_text("approved")),
            ft.dropdown.Option("rejected", get_text("rejected")),
        ],
        width=220,
    )
    
    def update(e):
        new_status = status_dropdown.value
        if new_status and new_status != current_status:
            on_update(quotation_id, new_status)
        else:
            on_close()
    
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
                        padding=ft.Padding(left=5, right=5, top=5, bottom=5),
                    ),
                    ft.Text(get_text("update_quotation_status"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(f"{get_text('current_status')}: {get_text(current_status)}", size=12, color="#64748B"),
                ft.Container(height=8),
                status_dropdown,
            ]),
            padding=ft.Padding(left=14, right=14, top=12, bottom=8),
            width=310,
            height=130,
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
                        content=ft.Text(get_text("update"), size=13, color=ft.Colors.WHITE),
                        on_click=update,
                        style=ft.ButtonStyle(
                            bgcolor=primary_color,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.Padding(left=16, right=16, top=6, bottom=6),
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


def show_delete_quotation_dialog(quotation_name, on_confirm, on_close):
    """Show delete quotation confirmation dialog"""
    
    def confirm(e):
        on_confirm()
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=12),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.WARNING_AMBER, size=18, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.RED_600,
                        border_radius=8,
                        padding=ft.Padding(left=5, right=5, top=5, bottom=5),
                    ),
                    ft.Text(get_text("confirm"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=32, color=ft.Colors.RED_600),
                ft.Container(height=4),
                ft.Text(f"ຕ້ອງການລຶບ '{quotation_name}' ຫຼືບໍ່?", size=14, weight=ft.FontWeight.W_500, color="#1E293B", text_align=ft.TextAlign.CENTER),
                ft.Text(get_text("delete_warning"), size=12, color="#64748B", text_align=ft.TextAlign.CENTER),
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
                            bgcolor=ft.Colors.RED_600,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.Padding(left=16, right=16, top=6, bottom=6),
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