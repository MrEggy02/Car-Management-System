# pages/employees/employees_widgets.py
import flet as ft
from i18n import get_text

# ==================== CONSTANTS ====================
PRIMARY_COLOR = "#1565C0"
WARNING_COLOR = "#DC2626"

ROLE_CONFIGS = {
    "admin": {
        "text": "role_admin",
        "color": "#1565C0",
        "bg_color": "#E3F2FD",
        "avatar_color": "#1565C0",
        "icon": ft.Icons.SHIELD
    },
    "mechanic": {
        "text": "role_mechanic",
        "color": "#E65100",
        "bg_color": "#FFF3E0",
        "avatar_color": "#E65100",
        "icon": ft.Icons.BUILD
    },
    "cashier": {
        "text": "role_cashier",
        "color": "#2E7D32",
        "bg_color": "#E8F5E9",
        "avatar_color": "#2E7D32",
        "icon": ft.Icons.PHONE
    }
}

STATUS_CONFIGS = {
    "active": {
        "text": "status_active",
        "color": "#2E7D32",
        "bg_color": "#E8F5E9",
        "icon": ft.Icons.CHECK_CIRCLE
    },
    "inactive": {
        "text": "status_inactive",
        "color": "#DC2626",
        "bg_color": "#FFEEEE",
        "icon": ft.Icons.DO_NOT_DISTURB
    }
}

# ==================== TABLE WIDGETS ====================
def create_table_header():
    """Create table header row"""
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=50, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("employees_name"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=160, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=10)),
                ft.Container(content=ft.Text(get_text("employees_role"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=120, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=10)),
                ft.Container(content=ft.Text(get_text("employees_phone"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=120, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("username"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=120, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("employees_status"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("action"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=100, alignment=ft.Alignment(0, 0)),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=14, horizontal=10),
        bgcolor=ft.Colors.GREY_100,
        border_radius=ft.BorderRadius.only(top_left=8, top_right=8),
    )

def create_role_badge(role):
    """Create role badge widget"""
    config = ROLE_CONFIGS.get(role, ROLE_CONFIGS["mechanic"])
    role_text = get_text(config["text"])
    
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(config["icon"], size=14, color=config["color"]),
                ft.Text(role_text, size=12, color=config["color"], weight=ft.FontWeight.W_500),
            ],
            spacing=4,
        ),
        bgcolor=config["bg_color"],
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )

def create_login_badge(can_login):
    """Create login permission badge"""
    if can_login:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LOGIN, size=12, color="#2E7D32"),
                    ft.Text(get_text("can_login"), size=10, color="#2E7D32", weight=ft.FontWeight.W_500),
                ],
                spacing=3,
            ),
            bgcolor="#E8F5E9",
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )
    else:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LOCK, size=12, color="#64748B"),
                    ft.Text(get_text("cannot_login"), size=10, color="#64748B"),
                ],
                spacing=3,
            ),
            bgcolor="#F1F5F9",
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )

def create_status_badge(status):
    """Create status badge widget"""
    config = STATUS_CONFIGS.get(status, STATUS_CONFIGS["active"])
    status_text = get_text(config["text"])
    
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(config["icon"], size=14, color=config["color"]),
                ft.Text(status_text, size=12, color=config["color"], weight=ft.FontWeight.W_500),
            ],
            spacing=4,
        ),
        bgcolor=config["bg_color"],
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )

def create_action_buttons(on_edit, on_delete):
    """Create edit and delete buttons"""
    edit_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=PRIMARY_COLOR),
            ft.Text(get_text("edit"), size=12, color=PRIMARY_COLOR),
        ], spacing=4),
        on_click=on_edit,
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=6,
    )
    
    delete_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
            ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
        ], spacing=4),
        on_click=on_delete,
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=6,
    )
    
    return ft.Row([edit_btn, delete_btn], spacing=4)

def create_empty_state():
    """Create empty state when no data"""
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_data"), size=16, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add"), size=13, color=ft.Colors.GREY_400),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.Alignment(0, 0),
        ),
        padding=ft.padding.all(40),
        expand=True,
    )

def create_table_row(emp, index, row_number, on_edit, on_delete):
    """Create a single table row"""
    emp_id = emp.get("id")
    name = emp.get("name", "-")
    role = emp.get("role", "-")
    phone = emp.get("phone", "-")
    status = emp.get("status", "active")
    can_login = emp.get("can_login", False)
    username = emp.get("username", "-")
    
    row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
    
    phone_display = phone if phone != "-" else get_text("no_phone")
    phone_color = ft.Colors.GREY_700 if phone != "-" else ft.Colors.GREY_400
    username_display = username if username and username != "-" else "-"
    username_color = "#2E7D32" if username_display != "-" else ft.Colors.GREY_400
    
    row = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(
                            str(row_number), 
                            size=13, 
                            weight=ft.FontWeight.W_500, 
                            color=PRIMARY_COLOR
                        ),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=6,
                        alignment=ft.Alignment(0, 0),
                    ),
                    width=50, 
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(name, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
                    width=160,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=create_role_badge(role),
                    width=120,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(phone_display, size=12, color=phone_color, max_lines=1),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Column([
                        create_login_badge(can_login),
                        ft.Text(username_display, size=10, color=username_color, max_lines=1) if can_login else ft.Container(),
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=create_status_badge(status),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=create_action_buttons(lambda e: on_edit(emp_id), lambda e: on_delete(emp_id)),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=12, horizontal=10),
        bgcolor=row_bg,
    )
    
    return ft.Column([row, ft.Divider(height=1, color=ft.Colors.GREY_200)], spacing=0)


# ==================== DIALOG WIDGETS ====================
def create_add_dialog(on_save, on_close):
    """Create add employee dialog with login fields"""
    
    name = ft.TextField(
        label=get_text("employees_name"),
        hint_text="ຊື່ພະນັກງານ",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
        expand=True,
    )
    
    role = ft.Dropdown(
        label=get_text("employees_role"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        value="mechanic",
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
        expand=True,
        options=[
            ft.dropdown.Option("admin", get_text('role_admin')),
            ft.dropdown.Option("mechanic", get_text('role_mechanic')),
            ft.dropdown.Option("cashier", get_text('role_cashier')),
        ],
    )
    
    phone = ft.TextField(
        label=get_text("employees_phone"),
        hint_text="0200000000",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
        expand=True,
    )
    
    status = ft.Dropdown(
        label=get_text("employees_status"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        value="active",
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
        expand=True,
        options=[
            ft.dropdown.Option("active", get_text('status_active')),
            ft.dropdown.Option("inactive", get_text('status_inactive')),
        ],
    )
    
    # Login section
    can_login_checkbox = ft.Checkbox(
        label=get_text("allow_login"),
        value=False,
        label_style=ft.TextStyle(size=13),
    )
    
    username_field = ft.TextField(
        label=get_text("username"),
        hint_text="username",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        visible=False,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
        expand=True,
    )
    
    password_field = ft.TextField(
        label=get_text("password"),
        hint_text="••••••••",
        password=True,
        can_reveal_password=True,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        visible=False,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
        expand=True,
    )
    
    def on_can_login_change(e):
        visible = can_login_checkbox.value
        username_field.visible = visible
        password_field.visible = visible
        if not visible:
            username_field.value = ""
            password_field.value = ""
        # Update the dialog
        if username_field.page:
            username_field.page.update()
    
    can_login_checkbox.on_change = on_can_login_change
    
    def save(e):
        if name.value and role.value:
            on_save(
                name.value, role.value, phone.value, status.value,
                can_login_checkbox.value,
                username_field.value if can_login_checkbox.value else None,
                password_field.value if can_login_checkbox.value else None
            )
    
    return ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON_ADD, size=22, color=ft.Colors.WHITE),
                        bgcolor=PRIMARY_COLOR,
                        border_radius=10,
                        padding=ft.padding.all(6),
                    ),
                    ft.Text(get_text("employees_add"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Row([name, role], spacing=12),
                ft.Container(height=8),
                ft.Row([phone, status], spacing=12),
                ft.Container(height=12),
                ft.Text(get_text("login_access"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Row([can_login_checkbox], spacing=12),
                ft.Container(height=8),
                ft.Row([username_field, password_field], spacing=12),
            ], spacing=0, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(18),
            width=540,
            height=430,
        ),
        actions=[
            ft.Container(
                content=ft.Row([
                    ft.TextButton(
                        content=ft.Text(get_text("cancel"), color="#64748B"),
                        on_click=on_close,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("save"), color=ft.Colors.WHITE),
                        on_click=save,
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY_COLOR,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=20, vertical=8),
                        ),
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=18, vertical=12),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

def create_edit_dialog(emp, on_save, on_close):
    """Create edit employee dialog - fields always visible, disabled when not allowed"""
    
    # Debug print
    print(f"=== EDIT DIALOG ===")
    print(f"Employee: {emp.get('name')}")
    print(f"can_login raw: {emp.get('can_login')}")
    
    # Convert can_login to boolean properly
    can_login_raw = emp.get("can_login", False)
    if can_login_raw in [1, "1", True, "true", "True"]:
        current_can_login = True
    else:
        current_can_login = False
    
    current_username = emp.get("username", "")
    if current_username is None or current_username == "-":
        current_username = ""
    
    print(f"can_login converted: {current_can_login}")
    print(f"username: {current_username}")
    
    # Name field
    name = ft.TextField(
        label=get_text("employees_name"),
        value=emp.get("name", ""),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        expand=True,
    )
    
    # Role dropdown
    role = ft.Dropdown(
        label=get_text("employees_role"),
        value=emp.get("role", "mechanic"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        expand=True,
        options=[
            ft.dropdown.Option("admin", get_text('role_admin')),
            ft.dropdown.Option("mechanic", get_text('role_mechanic')),
            ft.dropdown.Option("cashier", get_text('role_cashier')),
        ],
    )
    
    # Phone field
    phone = ft.TextField(
        label=get_text("employees_phone"),
        value=emp.get("phone", ""),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        expand=True,
    )
    
    # Status dropdown
    status = ft.Dropdown(
        label=get_text("employees_status"),
        value=emp.get("status", "active"),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        expand=True,
        options=[
            ft.dropdown.Option("active", get_text('status_active')),
            ft.dropdown.Option("inactive", get_text('status_inactive')),
        ],
    )
    
    # Allow login checkbox
    can_login_checkbox = ft.Checkbox(
        label=get_text("allow_login"),
        value=current_can_login,
        label_style=ft.TextStyle(size=13),
    )
    
    # Username field - ALWAYS VISIBLE
    username_field = ft.TextField(
        label=get_text("username"),
        value=current_username,
        hint_text="ຊື່ຜູ້ໃຊ້ສຳລັບເຂົ້າສູ່ລະບົບ",
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        disabled=not current_can_login,
        expand=True,
    )
    
    # Password field - ALWAYS VISIBLE
    password_field = ft.TextField(
        label=get_text("new_password"),
        hint_text="ປ່ອຍຫວ່າງໄວ້ຖ້າບໍ່ຕ້ອງການປ່ຽນ",
        password=True,
        can_reveal_password=True,
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        disabled=not current_can_login,
        expand=True,
    )
    
    def on_can_login_change(e):
        enabled = can_login_checkbox.value
        username_field.disabled = not enabled
        password_field.disabled = not enabled
        if enabled:
            password_field.hint_text = "ປ່ອຍຫວ່າງໄວ້ຖ້າບໍ່ຕ້ອງການປ່ຽນ"
        else:
            password_field.hint_text = "ບໍ່ຕ້ອງການເຂົ້າສູ່ລະບົບ"
        username_field.update()
        password_field.update()
    
    can_login_checkbox.on_change = on_can_login_change
    
    def save(e):
        update_data = {
            "name": name.value,
            "role": role.value,
            "phone": phone.value,
            "status": status.value,
            "can_login": can_login_checkbox.value,
        }
        if can_login_checkbox.value:
            if username_field.value and username_field.value.strip():
                update_data["username"] = username_field.value.strip()
            if password_field.value and password_field.value.strip():
                update_data["password"] = password_field.value.strip()
        else:
            update_data["username"] = None
        on_save(update_data)
    
    return ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.EDIT, size=22, color=ft.Colors.WHITE),
                        bgcolor=PRIMARY_COLOR,
                        border_radius=10,
                        padding=ft.padding.all(6),
                    ),
                    ft.Text(get_text("employees_edit"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=10,
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    # Row 1: Name and Role
                    ft.Row([name, role], spacing=12),
                    ft.Container(height=8),
                    # Row 2: Phone and Status
                    ft.Row([phone, status], spacing=12),
                    ft.Container(height=16),
                    # Login Access Section
                    ft.Text(get_text("login_access"), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(height=8),
                    # Allow login checkbox
                    can_login_checkbox,
                    ft.Container(height=12),
                    # Username field
                    username_field,
                    ft.Container(height=12),
                    # Password field
                    password_field,
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.all(20),
            width=520,
            height=480,
        ),
        actions=[
            ft.Container(
                content=ft.Row(
                    [
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B"),
                            on_click=on_close,
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), color=ft.Colors.WHITE),
                            on_click=save,
                            style=ft.ButtonStyle(bgcolor=PRIMARY_COLOR, elevation=0, padding=ft.padding.symmetric(horizontal=24, vertical=10)),
                        ),
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.END,
                ),
                padding=ft.padding.symmetric(horizontal=18, vertical=12),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

def create_delete_dialog(emp_name, on_confirm, on_close):
    """Create delete confirmation dialog"""
    return ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=14),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.WARNING_AMBER, size=22, color=ft.Colors.WHITE),
                        bgcolor=WARNING_COLOR,
                        border_radius=10,
                        padding=ft.padding.all(6),
                    ),
                    ft.Text(get_text("confirm"), size=16, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=40, color=WARNING_COLOR),
                ft.Container(height=8),
                ft.Text(
                    f"ຕ້ອງການລຶບ '{emp_name}' ຫຼື ບໍ່?",
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
                        on_click=on_close,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(get_text("delete"), color=ft.Colors.WHITE),
                        on_click=on_confirm,
                        style=ft.ButtonStyle(
                            bgcolor=WARNING_COLOR,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=20, vertical=8),
                        ),
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.symmetric(horizontal=18, vertical=12),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )