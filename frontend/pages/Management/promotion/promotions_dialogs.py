# pages/Management/promotion/promotions_dialogs.py
import flet as ft
from i18n import get_text
from datetime import datetime


def db_to_display_date(date_val):
    if not date_val:
        return ""
    try:
        if isinstance(date_val, datetime):
            return date_val.strftime("%d-%m-%Y")
        from datetime import date
        if isinstance(date_val, date):
            return date_val.strftime("%d-%m-%Y")
        
        # If it is a string
        date_str = str(date_val).split(" ")[0]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d-%m-%Y")
    except Exception as e:
        print(f"Error formatting date {date_val}: {e}")
        return str(date_val)

def display_to_db_date(date_str):
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        return dt.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
        # Try fallback if it's already YYYY-MM-DD
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except:
            return None


def show_add_promotion_dialog(page, primary_color, client, on_close, on_success, show_snackbar):
    """Show add promotion dialog"""
    
    name = ft.TextField(
        label=f"{get_text('promo_name')} *",
        hint_text="ເຊັ່ນ: Summer Sale 2024",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.LOCAL_OFFER,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
    )
    
    discount_type = ft.Dropdown(
        label=f"{get_text('discount_type')} *",
        value="percent",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        options=[
            ft.dropdown.Option("percent", f"% {get_text('percentage')}"),
            ft.dropdown.Option("amount", f"KIP {get_text('fixed_amount')}"),
        ],
        expand=True,
    )
    
    value = ft.TextField(
        label=f"{get_text('discount_value')} *",
        hint_text="ເຊັ່ນ: 10 ຫຼື 50000",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.ATTACH_MONEY,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
    )
    
    min_amount = ft.TextField(
        label=get_text("min_amount"),
        hint_text="0",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        value="0",
        prefix_icon=ft.Icons.ATTACH_MONEY,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
    )
    
    ignore_start_focus = False
    ignore_end_focus = False

    def clear_start_date(e):
        nonlocal ignore_start_focus
        ignore_start_focus = True
        start_date.value = ""
        dialog.update()

    def clear_end_date(e):
        nonlocal ignore_end_focus
        ignore_end_focus = True
        end_date.value = ""
        dialog.update()

    def _pick_start_date(e):
        nonlocal ignore_start_focus
        if ignore_start_focus:
            ignore_start_focus = False
            return
            
        def on_date_selected(e_picker):
            nonlocal ignore_start_focus
            ignore_start_focus = True
            if e_picker.control.value:
                start_date.value = e_picker.control.value.strftime("%d-%m-%Y")
                start_date.error_text = None
                dialog.update()
        
        def on_dismiss(e_picker):
            nonlocal ignore_start_focus
            ignore_start_focus = True
        
        initial_val = None
        if start_date.value:
            try:
                initial_val = datetime.strptime(start_date.value, "%d-%m-%Y")
            except:
                pass
                
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            on_dismiss=on_dismiss,
            value=initial_val,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2100, 12, 31),
        )
        page.overlay.append(date_picker)
        date_picker.open = True
        page.update()

    def _pick_end_date(e):
        nonlocal ignore_end_focus
        if ignore_end_focus:
            ignore_end_focus = False
            return
            
        def on_date_selected(e_picker):
            nonlocal ignore_end_focus
            ignore_end_focus = True
            if e_picker.control.value:
                end_date.value = e_picker.control.value.strftime("%d-%m-%Y")
                end_date.error_text = None
                dialog.update()
        
        def on_dismiss(e_picker):
            nonlocal ignore_end_focus
            ignore_end_focus = True
        
        initial_val = None
        if end_date.value:
            try:
                initial_val = datetime.strptime(end_date.value, "%d-%m-%Y")
            except:
                pass
                
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            on_dismiss=on_dismiss,
            value=initial_val,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2100, 12, 31),
        )
        page.overlay.append(date_picker)
        date_picker.open = True
        page.update()

    start_date = ft.TextField(
        label=get_text("start_date"),
        hint_text="DD-MM-YYYY",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.CALENDAR_TODAY,
        suffix=ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=16,
            icon_color=ft.Colors.GREY_600,
            on_click=clear_start_date,
            tooltip=get_text("clear") or "Clear"
        ),
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
        read_only=True,
        on_focus=_pick_start_date,
    )
    
    end_date = ft.TextField(
        label=get_text("end_date"),
        hint_text="DD-MM-YYYY",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.CALENDAR_MONTH,
        suffix=ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=16,
            icon_color=ft.Colors.GREY_600,
            on_click=clear_end_date,
            tooltip=get_text("clear") or "Clear"
        ),
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
        read_only=True,
        on_focus=_pick_end_date,
    )
    
    status = ft.Dropdown(
        label=get_text("status"),
        value="active",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        options=[
            ft.dropdown.Option("active", f"✅ {get_text('status_active')}"),
            ft.dropdown.Option("inactive", f"❌ {get_text('status_inactive')}"),
        ],
        expand=True,
    )
    
    # Parts selection
    selected_parts = []
    selected_parts_list = ft.Column(spacing=4, height=120, scroll=ft.ScrollMode.AUTO)
    
    parts_search = ft.TextField(
        hint_text=get_text("search_parts"),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.SEARCH,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        expand=True,
    )
    
    parts_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=180)
    
    def load_parts(search=""):
        try:
            parts = client.get_parts()
            if search:
                parts = [p for p in parts if search.lower() in p.get('name', '').lower()]
            
            parts_list.controls.clear()
            for part in parts[:15]:
                part_id = part.get('id')
                part_name = part.get('name')
                part_price = part.get('sell_price', 0)
                is_selected = part_id in [sp['id'] for sp in selected_parts]
                
                parts_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Checkbox(
                                value=is_selected,
                                on_change=lambda e, pid=part_id, pname=part_name, pprice=part_price: toggle_part(pid, pname, pprice, e.control.value),
                            ),
                            ft.Text(part_name, size=13, weight=ft.FontWeight.W_500, expand=True),
                            ft.Text(f"{int(part_price):,} KIP", size=11, color="#1565C0"),
                        ], spacing=8),
                        padding=ft.padding.symmetric(vertical=4, horizontal=8),
                        bgcolor=ft.Colors.GREY_50 if is_selected else None,
                        border_radius=6,
                    )
                )
            dialog.update()
        except Exception as e:
            print(f"Error loading parts: {e}")
    
    def toggle_part(part_id, part_name, part_price, is_selected):
        if is_selected:
            selected_parts.append({'id': part_id, 'name': part_name, 'price': part_price})
        else:
            for i, sp in enumerate(selected_parts):
                if sp['id'] == part_id:
                    selected_parts.pop(i)
                    break
        
        selected_parts_list.controls.clear()
        for sp in selected_parts:
            selected_parts_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(sp['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"{int(sp['price']):,} KIP", size=11, color="#1565C0"),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, pid=sp['id']: remove_part(pid),
                        ),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=6,
                )
            )
        load_parts()
    
    def remove_part(part_id):
        for i, sp in enumerate(selected_parts):
            if sp['id'] == part_id:
                selected_parts.pop(i)
                break
        selected_parts_list.controls.clear()
        for sp in selected_parts:
            selected_parts_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(sp['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"{int(sp['price']):,} KIP", size=11, color="#1565C0"),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, pid=sp['id']: remove_part(pid),
                        ),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=6,
                )
            )
        load_parts()
    
    # Services selection
    selected_services = []
    selected_services_list = ft.Column(spacing=4, height=120, scroll=ft.ScrollMode.AUTO)
    
    services_search = ft.TextField(
        hint_text=get_text("search_services"),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.SEARCH,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        expand=True,
    )
    
    services_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=180)
    
    def load_services(search=""):
        try:
            services = client.get_services()
            if search:
                services = [s for s in services if search.lower() in s.get('name', '').lower()]
            
            services_list.controls.clear()
            for service in services[:15]:
                service_id = service.get('id')
                service_name = service.get('name')
                service_price = service.get('price', 0)
                is_selected = service_id in [ss['id'] for ss in selected_services]
                
                services_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Checkbox(
                                value=is_selected,
                                on_change=lambda e, sid=service_id, sname=service_name, sprice=service_price: toggle_service(sid, sname, sprice, e.control.value),
                            ),
                            ft.Text(service_name, size=13, weight=ft.FontWeight.W_500, expand=True),
                            ft.Text(f"{int(service_price):,} KIP", size=11, color="#1565C0"),
                        ], spacing=8),
                        padding=ft.padding.symmetric(vertical=4, horizontal=8),
                        bgcolor=ft.Colors.GREY_50 if is_selected else None,
                        border_radius=6,
                    )
                )
            dialog.update()
        except Exception as e:
            print(f"Error loading services: {e}")
    
    def toggle_service(service_id, service_name, service_price, is_selected):
        if is_selected:
            selected_services.append({'id': service_id, 'name': service_name, 'price': service_price})
        else:
            for i, ss in enumerate(selected_services):
                if ss['id'] == service_id:
                    selected_services.pop(i)
                    break
        
        selected_services_list.controls.clear()
        for ss in selected_services:
            selected_services_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(ss['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"{int(ss['price']):,} KIP", size=11, color="#1565C0"),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, sid=ss['id']: remove_service(sid),
                        ),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=6,
                )
            )
        load_services()
    
    def remove_service(service_id):
        for i, ss in enumerate(selected_services):
            if ss['id'] == service_id:
                selected_services.pop(i)
                break
        selected_services_list.controls.clear()
        for ss in selected_services:
            selected_services_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(ss['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"{int(ss['price']):,} KIP", size=11, color="#1565C0"),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, sid=ss['id']: remove_service(sid),
                        ),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=6,
                )
            )
        load_services()
    
    parts_search.on_change = lambda e: load_parts(e.control.value)
    services_search.on_change = lambda e: load_services(e.control.value)
    
    load_parts()
    load_services()
    
    def save(e):
        if not name.value:
            name.error_text = get_text("required_field")
            dialog.update()
            return
        if not value.value:
            value.error_text = get_text("required_field")
            dialog.update()
            return
        
        start_date.error_text = None
        end_date.error_text = None
        dialog.update()

        formatted_start = None
        if start_date.value:
            formatted_start = display_to_db_date(start_date.value)
            if not formatted_start:
                start_date.error_text = get_text("invalid_date_format")
                dialog.update()
                return

        formatted_end = None
        if end_date.value:
            formatted_end = display_to_db_date(end_date.value)
            if not formatted_end:
                end_date.error_text = get_text("invalid_date_format")
                dialog.update()
                return

        if formatted_start and formatted_end:
            if formatted_start > formatted_end:
                start_date.error_text = get_text("start_date_error")
                end_date.error_text = get_text("end_date_error")
                dialog.update()
                return

        try:
            result = client.add_promotion(
                name=name.value,
                discount_type=discount_type.value,
                value=float(value.value),
                min_amount=float(min_amount.value) if min_amount.value else 0,
                start_date=formatted_start,
                end_date=formatted_end,
                status=status.value
            )
            
            promo_id = result.get('id')
            
            for part in selected_parts:
                try:
                    client.add_promotion_part(promo_id, part['id'], 1)
                except:
                    pass
            
            for service in selected_services:
                try:
                    client.add_promotion_service(promo_id, service['id'], 1)
                except:
                    pass
            
            on_close()
            on_success()
            show_snackbar(f"✅ {get_text('add_success')}")
        except Exception as err:
            show_snackbar(f"{get_text('error')}: {err}")
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.LOCAL_OFFER, size=22, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=10,
                        padding=ft.padding.all(6),
                    ),
                    ft.Text(get_text('promotions_add'), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(get_text("basic_information"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Row([name, discount_type], spacing=10),
                ft.Row([value, min_amount], spacing=10),
                ft.Row([start_date, end_date, status], spacing=10),
                ft.Container(height=12),
                ft.Text(get_text("select_parts"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                parts_search,
                ft.Container(content=parts_list, height=200),
                ft.Text(get_text("selected_parts"), size=12, weight=ft.FontWeight.W_500, color="#1565C0"),
                selected_parts_list,
                ft.Container(height=12),
                ft.Text(get_text("select_services"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                services_search,
                ft.Container(content=services_list, height=200),
                ft.Text(get_text("selected_services"), size=12, weight=ft.FontWeight.W_500, color="#1565C0"),
                selected_services_list,
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(18),
            width=700,
            height=650,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("save"), color=ft.Colors.WHITE),
                        on_click=save,
                        style=ft.ButtonStyle(bgcolor=primary_color, elevation=0, padding=ft.padding.symmetric(horizontal=24, vertical=10)),
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=18, vertical=12),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_edit_promotion_dialog(page, primary_color, client, promo, on_close, on_success, show_snackbar):
    """Show edit promotion dialog with parts/services selection (same as add dialog)"""
    
    name = ft.TextField(
        label=f"{get_text('promo_name')} *",
        value=promo.get('name', ''),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.LOCAL_OFFER,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
    )
    
    discount_type = ft.Dropdown(
        label=f"{get_text('discount_type')} *",
        value=promo.get('discount_type', 'percent'),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        options=[
            ft.dropdown.Option("percent", f"% {get_text('percentage')}"),
            ft.dropdown.Option("amount", f"KIP {get_text('fixed_amount')}"),
        ],
        expand=True,
    )
    
    value = ft.TextField(
        label=f"{get_text('discount_value')} *",
        value=str(promo.get('value', 0)),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.ATTACH_MONEY,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
    )
    
    min_amount = ft.TextField(
        label=get_text("min_amount"),
        value=str(promo.get('min_amount', 0)),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.ATTACH_MONEY,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
    )
    
    ignore_start_focus = False
    ignore_end_focus = False

    def clear_start_date(e):
        nonlocal ignore_start_focus
        ignore_start_focus = True
        start_date.value = ""
        dialog.update()

    def clear_end_date(e):
        nonlocal ignore_end_focus
        ignore_end_focus = True
        end_date.value = ""
        dialog.update()

    def _pick_start_date(e):
        nonlocal ignore_start_focus
        if ignore_start_focus:
            ignore_start_focus = False
            return
            
        def on_date_selected(e_picker):
            nonlocal ignore_start_focus
            ignore_start_focus = True
            if e_picker.control.value:
                start_date.value = e_picker.control.value.strftime("%d-%m-%Y")
                start_date.error_text = None
                dialog.update()
        
        def on_dismiss(e_picker):
            nonlocal ignore_start_focus
            ignore_start_focus = True
        
        initial_val = None
        if start_date.value:
            try:
                initial_val = datetime.strptime(start_date.value, "%d-%m-%Y")
            except:
                pass
                
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            on_dismiss=on_dismiss,
            value=initial_val,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2100, 12, 31),
        )
        page.overlay.append(date_picker)
        date_picker.open = True
        page.update()

    def _pick_end_date(e):
        nonlocal ignore_end_focus
        if ignore_end_focus:
            ignore_end_focus = False
            return
            
        def on_date_selected(e_picker):
            nonlocal ignore_end_focus
            ignore_end_focus = True
            if e_picker.control.value:
                end_date.value = e_picker.control.value.strftime("%d-%m-%Y")
                end_date.error_text = None
                dialog.update()
        
        def on_dismiss(e_picker):
            nonlocal ignore_end_focus
            ignore_end_focus = True
        
        initial_val = None
        if end_date.value:
            try:
                initial_val = datetime.strptime(end_date.value, "%d-%m-%Y")
            except:
                pass
                
        date_picker = ft.DatePicker(
            on_change=on_date_selected,
            on_dismiss=on_dismiss,
            value=initial_val,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2100, 12, 31),
        )
        page.overlay.append(date_picker)
        date_picker.open = True
        page.update()

    start_date_val = promo.get('start_date')
    start_date = ft.TextField(
        label=get_text("start_date"),
        value=db_to_display_date(start_date_val),
        hint_text="DD-MM-YYYY",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.CALENDAR_TODAY,
        suffix=ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=16,
            icon_color=ft.Colors.GREY_600,
            on_click=clear_start_date,
            tooltip=get_text("clear") or "Clear"
        ),
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
        read_only=True,
        on_focus=_pick_start_date,
    )
    
    end_date_val = promo.get('end_date')
    end_date = ft.TextField(
        label=get_text("end_date"),
        value=db_to_display_date(end_date_val),
        hint_text="DD-MM-YYYY",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.CALENDAR_MONTH,
        suffix=ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=16,
            icon_color=ft.Colors.GREY_600,
            on_click=clear_end_date,
            tooltip=get_text("clear") or "Clear"
        ),
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        expand=True,
        read_only=True,
        on_focus=_pick_end_date,
    )
    
    status = ft.Dropdown(
        label=get_text("status"),
        value=promo.get('status', 'active'),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        options=[
            ft.dropdown.Option("active", f"✅ {get_text('status_active')}"),
            ft.dropdown.Option("inactive", f"❌ {get_text('status_inactive')}"),
        ],
        expand=True,
    )
    
    # Load existing parts and services
    existing_parts = []
    existing_services = []
    selected_parts = []
    selected_services = []
    
    try:
        existing_parts = client.get_promotion_parts(promo.get('id')) or []
        existing_services = client.get_promotion_services(promo.get('id')) or []
        for p in existing_parts:
            selected_parts.append({'id': p.get('part_id'), 'name': p.get('part_name'), 'price': p.get('sell_price', 0)})
        for s in existing_services:
            selected_services.append({'id': s.get('service_id'), 'name': s.get('service_name'), 'price': s.get('price', 0)})
    except:
        pass
    
    selected_parts_list = ft.Column(spacing=4, height=120, scroll=ft.ScrollMode.AUTO)
    selected_services_list = ft.Column(spacing=4, height=120, scroll=ft.ScrollMode.AUTO)
    
    # Display selected parts
    for sp in selected_parts:
        selected_parts_list.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(sp['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                    ft.Text(f"{int(sp['price']):,} KIP", size=11, color="#1565C0"),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, pid=sp['id']: remove_part(pid),
                    ),
                ], spacing=8),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                bgcolor=ft.Colors.BLUE_50,
                border_radius=6,
            )
        )
    
    for ss in selected_services:
        selected_services_list.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(ss['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                    ft.Text(f"{int(ss['price']):,} KIP", size=11, color="#1565C0"),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        on_click=lambda e, sid=ss['id']: remove_service(sid),
                    ),
                ], spacing=8),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                bgcolor=ft.Colors.GREEN_50,
                border_radius=6,
            )
        )
    
    # Parts selection
    parts_search = ft.TextField(
        hint_text=get_text("search_parts"),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.SEARCH,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        expand=True,
    )
    
    parts_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=180)
    
    def load_parts(search=""):
        try:
            parts = client.get_parts()
            if search:
                parts = [p for p in parts if search.lower() in p.get('name', '').lower()]
            
            parts_list.controls.clear()
            for part in parts[:15]:
                part_id = part.get('id')
                part_name = part.get('name')
                part_price = part.get('sell_price', 0)
                is_selected = part_id in [sp['id'] for sp in selected_parts]
                
                parts_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Checkbox(
                                value=is_selected,
                                on_change=lambda e, pid=part_id, pname=part_name, pprice=part_price: toggle_part(pid, pname, pprice, e.control.value),
                            ),
                            ft.Text(part_name, size=13, weight=ft.FontWeight.W_500, expand=True),
                            ft.Text(f"{int(part_price):,} KIP", size=11, color="#1565C0"),
                        ], spacing=8),
                        padding=ft.padding.symmetric(vertical=4, horizontal=8),
                        bgcolor=ft.Colors.GREY_50 if is_selected else None,
                        border_radius=6,
                    )
                )
            dialog.update()
        except Exception as e:
            print(f"Error loading parts: {e}")
    
    def toggle_part(part_id, part_name, part_price, is_selected):
        if is_selected:
            selected_parts.append({'id': part_id, 'name': part_name, 'price': part_price})
        else:
            for i, sp in enumerate(selected_parts):
                if sp['id'] == part_id:
                    selected_parts.pop(i)
                    break
        
        selected_parts_list.controls.clear()
        for sp in selected_parts:
            selected_parts_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(sp['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"{int(sp['price']):,} KIP", size=11, color="#1565C0"),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, pid=sp['id']: remove_part(pid),
                        ),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=6,
                )
            )
        load_parts()
    
    def remove_part(part_id):
        for i, sp in enumerate(selected_parts):
            if sp['id'] == part_id:
                selected_parts.pop(i)
                break
        selected_parts_list.controls.clear()
        for sp in selected_parts:
            selected_parts_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(sp['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"{int(sp['price']):,} KIP", size=11, color="#1565C0"),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, pid=sp['id']: remove_part(pid),
                        ),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=6,
                )
            )
        load_parts()
    
    # Services selection
    services_search = ft.TextField(
        hint_text=get_text("search_services"),
        border_radius=8,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.SEARCH,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        expand=True,
    )
    
    services_list = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, height=180)
    
    def load_services(search=""):
        try:
            services = client.get_services()
            if search:
                services = [s for s in services if search.lower() in s.get('name', '').lower()]
            
            services_list.controls.clear()
            for service in services[:15]:
                service_id = service.get('id')
                service_name = service.get('name')
                service_price = service.get('price', 0)
                is_selected = service_id in [ss['id'] for ss in selected_services]
                
                services_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Checkbox(
                                value=is_selected,
                                on_change=lambda e, sid=service_id, sname=service_name, sprice=service_price: toggle_service(sid, sname, sprice, e.control.value),
                            ),
                            ft.Text(service_name, size=13, weight=ft.FontWeight.W_500, expand=True),
                            ft.Text(f"{int(service_price):,} KIP", size=11, color="#1565C0"),
                        ], spacing=8),
                        padding=ft.padding.symmetric(vertical=4, horizontal=8),
                        bgcolor=ft.Colors.GREY_50 if is_selected else None,
                        border_radius=6,
                    )
                )
            dialog.update()
        except Exception as e:
            print(f"Error loading services: {e}")
    
    def toggle_service(service_id, service_name, service_price, is_selected):
        if is_selected:
            selected_services.append({'id': service_id, 'name': service_name, 'price': service_price})
        else:
            for i, ss in enumerate(selected_services):
                if ss['id'] == service_id:
                    selected_services.pop(i)
                    break
        
        selected_services_list.controls.clear()
        for ss in selected_services:
            selected_services_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(ss['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"{int(ss['price']):,} KIP", size=11, color="#1565C0"),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, sid=ss['id']: remove_service(sid),
                        ),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=6,
                )
            )
        load_services()
    
    def remove_service(service_id):
        for i, ss in enumerate(selected_services):
            if ss['id'] == service_id:
                selected_services.pop(i)
                break
        selected_services_list.controls.clear()
        for ss in selected_services:
            selected_services_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(ss['name'], size=12, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"{int(ss['price']):,} KIP", size=11, color="#1565C0"),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, sid=ss['id']: remove_service(sid),
                        ),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=6,
                )
            )
        load_services()
    
    parts_search.on_change = lambda e: load_parts(e.control.value)
    services_search.on_change = lambda e: load_services(e.control.value)
    
    load_parts()
    load_services()
    
    def save(e):
        if not name.value:
            name.error_text = get_text("required_field")
            dialog.update()
            return
        if not value.value:
            value.error_text = get_text("required_field")
            dialog.update()
            return
        
        start_date.error_text = None
        end_date.error_text = None
        dialog.update()

        formatted_start = None
        if start_date.value:
            formatted_start = display_to_db_date(start_date.value)
            if not formatted_start:
                start_date.error_text = get_text("invalid_date_format")
                dialog.update()
                return

        formatted_end = None
        if end_date.value:
            formatted_end = display_to_db_date(end_date.value)
            if not formatted_end:
                end_date.error_text = get_text("invalid_date_format")
                dialog.update()
                return

        if formatted_start and formatted_end:
            if formatted_start > formatted_end:
                start_date.error_text = get_text("start_date_error")
                end_date.error_text = get_text("end_date_error")
                dialog.update()
                return

        try:
            # Clear existing items first
            client.clear_promotion_parts(promo['id'])
            client.clear_promotion_services(promo['id'])
            
            # Update promotion info
            client.update_promotion(promo['id'], {
                'name': name.value,
                'discount_type': discount_type.value,
                'value': float(value.value),
                'min_amount': float(min_amount.value) if min_amount.value else 0,
                'start_date': formatted_start,
                'end_date': formatted_end,
                'status': status.value,
            })
            
            # Add new parts and services
            for part in selected_parts:
                try:
                    client.add_promotion_part(promo['id'], part['id'], 1)
                except:
                    pass
            
            for service in selected_services:
                try:
                    client.add_promotion_service(promo['id'], service['id'], 1)
                except:
                    pass
            
            on_close()
            on_success()
            show_snackbar(f"✅ {get_text('edit_success')}")
        except Exception as err:
            show_snackbar(f"{get_text('error')}: {err}")
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.EDIT, size=22, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=10,
                        padding=ft.padding.all(6),
                    ),
                    ft.Text(get_text('promotions_edit'), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Text(get_text("basic_information"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Row([name, discount_type], spacing=10),
                ft.Row([value, min_amount], spacing=10),
                ft.Row([start_date, end_date, status], spacing=10),
                ft.Container(height=12),
                ft.Text(get_text("select_parts"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                parts_search,
                ft.Container(content=parts_list, height=200),
                ft.Text(get_text("selected_parts"), size=12, weight=ft.FontWeight.W_500, color="#1565C0"),
                selected_parts_list,
                ft.Container(height=12),
                ft.Text(get_text("select_services"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                services_search,
                ft.Container(content=services_list, height=200),
                ft.Text(get_text("selected_services"), size=12, weight=ft.FontWeight.W_500, color="#1565C0"),
                selected_services_list,
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(18),
            width=700,
            height=650,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("save"), color=ft.Colors.WHITE),
                        on_click=save,
                        style=ft.ButtonStyle(bgcolor=primary_color, elevation=0, padding=ft.padding.symmetric(horizontal=24, vertical=10)),
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=18, vertical=12),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_delete_promotion_dialog(primary_color, promo, on_close, on_success, show_snackbar, client):
    """Show delete confirmation dialog"""
    
    promo_name = promo.get('name', get_text('this_promotion'))
    
    def confirm(e):
        try:
            client.delete_promotion(promo['id'])
            on_close()
            on_success()
            show_snackbar(f"✅ {get_text('delete_success')}")
        except Exception as err:
            show_snackbar(f"{get_text('error')}: {err}")
    
    dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.WARNING_AMBER, size=22, color=ft.Colors.WHITE),
                        bgcolor="#DC2626",
                        border_radius=10,
                        padding=ft.padding.all(6),
                    ),
                    ft.Text(get_text("confirm_delete"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=40, color="#DC2626"),
                ft.Container(height=8),
                ft.Text(
                    f"ຕ້ອງການລຶບ '{promo_name}' ຫຼື ບໍ່?",
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
            padding=ft.padding.all(20),
            width=320,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("delete"), color=ft.Colors.WHITE),
                        on_click=confirm,
                        style=ft.ButtonStyle(bgcolor="#DC2626", elevation=0, padding=ft.padding.symmetric(horizontal=20, vertical=10)),
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=18, vertical=12),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_detail_promotion_dialog(primary_color, client, promotion_id, promotion_name, on_close, on_success, show_snackbar):
    """Show promotion detail dialog with all information and parts/services list"""
    
    # ดึงข้อมูล promotion
    promotion = None
    try:
        promotions = client.get_promotions()
        for p in promotions:
            if p.get('id') == promotion_id:
                promotion = p
                break
    except:
        pass
    
    if not promotion:
        promotion = {'name': promotion_name, 'discount_type': 'percent', 'value': 0, 'min_amount': 0}
    
    # Format values
    discount_type_text = get_text("percentage") if promotion.get('discount_type') == 'percent' else get_text("fixed_amount")
    discount_value = f"{int(promotion.get('value', 0))}%" if promotion.get('discount_type') == 'percent' else f"{int(promotion.get('value', 0)):,} KIP"
    min_amount_text = f"{int(promotion.get('min_amount', 0)):,} KIP" if promotion.get('min_amount', 0) > 0 else "-"
    status_text = get_text("status_active") if promotion.get('status') == 'active' else get_text("status_inactive")
    status_color = "#2E7D32" if promotion.get('status') == 'active' else "#DC2626"
    status_bg = "#E8F5E9" if promotion.get('status') == 'active' else "#FFEEEE"
    
    # Format dates
    start_date = promotion.get('start_date')
    end_date = promotion.get('end_date')
    start_display = db_to_display_date(start_date) or "-"
    end_display = db_to_display_date(end_date) or "-"
    
    parts_items = []
    services_items = []
    
    # Use Columns without fixed height to expand with content
    parts_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    services_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    
    def load_items():
        nonlocal parts_items, services_items
        try:
            parts_items = client.get_promotion_parts(promotion_id) or []
            services_items = client.get_promotion_services(promotion_id) or []
            display_items()
        except Exception as e:
            print(f"Error loading items: {e}")
    
    def display_items():
        parts_list.controls.clear()
        services_list.controls.clear()
        
        # Display parts
        if parts_items:
            for item in parts_items:
                parts_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(item.get('part_name', '-'), size=13, weight=ft.FontWeight.W_500),
                                ft.Text(f"ລາຄາ: {int(item.get('sell_price', 0)):,} KIP", size=11, color="#64748B"),
                            ], spacing=2, expand=True),
                        ], spacing=8),
                        padding=ft.padding.symmetric(vertical=8, horizontal=12),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=8,
                    )
                )
        else:
            parts_list.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_parts"), size=13, color="#64748B"),
                    padding=ft.padding.all(20),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        # Display services
        if services_items:
            for item in services_items:
                services_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(item.get('service_name', '-'), size=13, weight=ft.FontWeight.W_500),
                                ft.Text(f"ລາຄາ: {int(item.get('price', 0)):,} KIP", size=11, color="#64748B"),
                            ], spacing=2, expand=True),
                        ], spacing=8),
                        padding=ft.padding.symmetric(vertical=8, horizontal=12),
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=8,
                    )
                )
        else:
            services_list.controls.append(
                ft.Container(
                    content=ft.Text(get_text("no_services"), size=13, color="#64748B"),
                    padding=ft.padding.all(20),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        detail_dialog.update()
    
    load_items()
    
    detail_dialog = ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=16),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.REMOVE_RED_EYE, size=22, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=10,
                        padding=ft.padding.all(6),
                    ),
                    ft.Text(promotion.get('name', promotion_name), size=16, weight=ft.FontWeight.BOLD, color="#1E293B", expand=True),
                    # Status badge - top right corner
                    ft.Container(
                        content=ft.Text(status_text, size=10, color=status_color, weight=ft.FontWeight.W_500),
                        bgcolor=status_bg,
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=12),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                # Promotion details grid
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("ປະເພດສ່ວນຫຼຸດ", size=11, color="#64748B"),
                                    ft.Text(discount_type_text, size=13, weight=ft.FontWeight.W_500),
                                ], spacing=3),
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("ມູນຄ່າສ່ວນຫຼຸດ", size=11, color="#64748B"),
                                    ft.Text(discount_value, size=13, weight=ft.FontWeight.W_600, color="#EF6C00"),
                                ], spacing=3),
                                expand=True,
                            ),
                        ], spacing=12),
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("ຍອດຊື້ຂັ້ນຕ່ຳ", size=11, color="#64748B"),
                                    ft.Text(min_amount_text, size=13, weight=ft.FontWeight.W_500),
                                ], spacing=3),
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("ໄລຍະເວລາ", size=11, color="#64748B"),
                                    ft.Text(f"{start_display} - {end_display}", size=12, weight=ft.FontWeight.W_500),
                                ], spacing=3),
                                expand=True,
                            ),
                        ], spacing=12),
                    ]),
                    padding=ft.padding.symmetric(vertical=10),
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                # Parts section - expands with content
                ft.Row([
                    ft.Icon(ft.Icons.CATEGORY, size=16, color=primary_color),
                    ft.Text(get_text("promotion_parts"), size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Container(
                        content=ft.Text(f"{len(parts_items)} ລາຍການ", size=10, color="#64748B"),
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    ),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    content=parts_list,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    border_radius=10,
                    padding=4,
                ),
                ft.Container(height=8),
                # Services section - expands with content
                ft.Row([
                    ft.Icon(ft.Icons.BUILD, size=16, color=primary_color),
                    ft.Text(get_text("promotion_services"), size=13, weight=ft.FontWeight.W_600, color="#1E293B"),
                    ft.Container(
                        content=ft.Text(f"{len(services_items)} ລາຍການ", size=10, color="#64748B"),
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=10,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    ),
                ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    content=services_list,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                    border_radius=10,
                    padding=4,
                ),
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(18),
            width=500,
            height=500,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("close"), size=13, color="#64748B"),
                        on_click=lambda e: on_close(),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return detail_dialog