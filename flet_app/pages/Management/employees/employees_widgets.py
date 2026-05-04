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
    "technician": {
        "text": "role_technician",
        "color": "#E65100",
        "bg_color": "#FFF3E0",
        "avatar_color": "#E65100",
        "icon": ft.Icons.BUILD
    },
    "reception": {
        "text": "role_reception",
        "color": "#2E7D32",
        "bg_color": "#E8F5E9",
        "avatar_color": "#2E7D32",
        "icon": ft.Icons.PHONE
    },
    "manager": {
        "text": "role_manager",
        "color": "#6A1B9A",
        "bg_color": "#F3E5F5",
        "avatar_color": "#6A1B9A",
        "icon": ft.Icons.BAR_CHART
    }
}

# ==================== TABLE WIDGETS ====================
def create_table_header():
    """Create table header row"""
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=50, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("employees_username"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=120, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=10)),
                ft.Container(content=ft.Text(get_text("employees_fullname"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=160, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=10)),
                ft.Container(content=ft.Text(get_text("employees_role"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=140, alignment=ft.Alignment(-1, 0), padding=ft.padding.only(left=10)),
                ft.Container(content=ft.Text(get_text("employees_phone"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=140, alignment=ft.Alignment(0, 0)),
                ft.Container(content=ft.Text(get_text("action"), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600), width=120, alignment=ft.Alignment(0, 0)),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=14, horizontal=10),
        bgcolor=ft.Colors.GREY_100,
        border_radius=ft.BorderRadius.only(top_left=8, top_right=8),
    )

def create_role_badge(role):
    """Create role badge widget"""
    config = ROLE_CONFIGS.get(role, ROLE_CONFIGS["admin"])
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
    fullname = emp.get("fullname", "-")
    username = emp.get("username", "-")
    role = emp.get("role", "-")
    phone = emp.get("phone", "-")
    
    row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
    
    phone_display = phone if phone != "-" else get_text("no_phone")
    phone_color = ft.Colors.GREY_700 if phone != "-" else ft.Colors.GREY_400
    
    row = ft.Container(
        content=ft.Row(
            [
                # Row number column with badge styling
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
                    content=ft.Container(
                        content=ft.Text(f"@{username}", size=12, color=ft.Colors.GREY_700, weight=ft.FontWeight.W_500, max_lines=1),
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=4,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    ),
                    width=120,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(fullname, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
                    width=160,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=create_role_badge(role),
                    width=140,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(phone_display, size=12, color=phone_color, max_lines=1),
                    width=140,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=create_action_buttons(lambda e: on_edit(emp_id), lambda e: on_delete(emp_id)),
                    width=120,
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
    """Create add employee dialog"""
    
    username = ft.TextField(
        label=get_text("employees_username"),
        hint_text="เช่น john_doe",
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        autofocus=True,
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
    )
    
    password = ft.TextField(
        label=get_text("employees_password"),
        hint_text="••••••••",
        password=True,
        can_reveal_password=True,
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
    )
    
    fullname = ft.TextField(
        label=get_text("employees_fullname"),
        hint_text="เช่น สมชาย ใจดี",
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.BADGE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
    )
    
    role = ft.Dropdown(
        label=get_text("employees_role"),
        hint_text="เลือกบทบาท",
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
        options=[
            ft.dropdown.Option("admin", f"👑 {get_text('role_admin')}"),
            ft.dropdown.Option("technician", f"🔧 {get_text('role_technician')}"),
            ft.dropdown.Option("reception", f"📞 {get_text('role_reception')}"),
            ft.dropdown.Option("manager", f"📊 {get_text('role_manager')}"),
        ],
    )
    
    phone = ft.TextField(
        label=get_text("employees_phone"),
        hint_text="เช่น 0812345678",
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.PHONE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border_color=ft.Colors.GREY_300,
        focused_border_color=PRIMARY_COLOR,
    )
    
    def save(e):
        if username.value and password.value and fullname.value and role.value:
            on_save(username.value, password.value, fullname.value, role.value, phone.value)
    
    return ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=16),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON_ADD, size=28, color=ft.Colors.WHITE),
                        bgcolor=PRIMARY_COLOR,
                        border_radius=14,
                        padding=ft.padding.all(8),
                    ),
                    ft.Column(
                        [
                            ft.Text(get_text("employees_add"), size=20, weight=ft.FontWeight.BOLD, color="#1E293B"),
                            ft.Text("เพิ่มพนักงานใหม่เข้าสู่ระบบ", size=13, color="#64748B"),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(20),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    username, ft.Container(height=12),
                    password, ft.Container(height=12),
                    fullname, ft.Container(height=12),
                    role, ft.Container(height=12),
                    phone,
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.all(24),
            width=520,
            height=520,
        ),
        actions=[
            ft.Container(
                content=ft.Row(
                    [
                        ft.TextButton(
                            content=ft.Row([ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"), ft.Text(get_text("cancel"), size=14, color="#64748B")], spacing=6),
                            on_click=on_close,
                            style=ft.ButtonStyle(overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.GREY_400), shape=ft.RoundedRectangleBorder(radius=10)),
                        ),
                        ft.ElevatedButton(
                            content=ft.Row([ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE), ft.Text(get_text("save"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)], spacing=6),
                            on_click=save,
                            style=ft.ButtonStyle(bgcolor=PRIMARY_COLOR, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10), elevation=2, padding=ft.padding.symmetric(horizontal=20, vertical=12)),
                        ),
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.END,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

def create_edit_dialog(emp, on_save, on_close):
    """Create edit employee dialog"""
    
    username = ft.TextField(
        label=get_text("employees_username"),
        value=emp.get("username", ""),
        read_only=True,
        border_radius=12,
        bgcolor=ft.Colors.GREY_100,
        filled=True,
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    
    fullname = ft.TextField(
        label=get_text("employees_fullname"),
        value=emp.get("fullname", ""),
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.BADGE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    
    role = ft.Dropdown(
        label=get_text("employees_role"),
        value=emp.get("role", ""),
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        options=[
            ft.dropdown.Option("admin", f"👑 {get_text('role_admin')}"),
            ft.dropdown.Option("technician", f"🔧 {get_text('role_technician')}"),
            ft.dropdown.Option("reception", f"📞 {get_text('role_reception')}"),
            ft.dropdown.Option("manager", f"📊 {get_text('role_manager')}"),
        ],
    )
    
    phone = ft.TextField(
        label=get_text("employees_phone"),
        value=emp.get("phone", ""),
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.PHONE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    
    password = ft.TextField(
        label=get_text("new_password_optional"),
        hint_text=get_text("leave_blank_if_no_change"),
        password=True,
        can_reveal_password=True,
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        filled=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    
    def save(e):
        update_data = {
            "fullname": fullname.value,
            "role": role.value,
            "phone": phone.value,
        }
        if password.value:
            update_data["password"] = password.value
        on_save(update_data)
    
    return ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=16),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(content=ft.Icon(ft.Icons.EDIT, size=28, color=ft.Colors.WHITE), bgcolor=PRIMARY_COLOR, border_radius=14, padding=ft.padding.all(8)),
                    ft.Column([ft.Text(get_text("employees_edit"), size=20, weight=ft.FontWeight.BOLD, color="#1E293B"), ft.Text("แก้ไขข้อมูลพนักงาน", size=13, color="#64748B")], spacing=2),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(20),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    username, ft.Container(height=12),
                    fullname, ft.Container(height=12),
                    role, ft.Container(height=12),
                    phone, ft.Container(height=12),
                    password,
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.all(24),
            width=520,
            height=550,
        ),
        actions=[
            ft.Container(
                content=ft.Row(
                    [
                        ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"), ft.Text(get_text("cancel"), size=14, color="#64748B")], spacing=6), on_click=on_close),
                        ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE), ft.Text(get_text("save"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)], spacing=6), on_click=save, style=ft.ButtonStyle(bgcolor=PRIMARY_COLOR, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.END,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

def create_delete_dialog(emp_name, on_confirm, on_close):
    """Create delete confirmation dialog"""
    return ft.AlertDialog(
        modal=True,
        shape=ft.RoundedRectangleBorder(radius=16),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(content=ft.Icon(ft.Icons.WARNING_AMBER, size=28, color=ft.Colors.WHITE), bgcolor=WARNING_COLOR, border_radius=14, padding=ft.padding.all(8)),
                    ft.Column([ft.Text(get_text("confirm"), size=20, weight=ft.FontWeight.BOLD, color="#1E293B"), ft.Text("กรุณายืนยันการลบข้อมูล", size=13, color="#64748B")], spacing=2),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(20),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Container(content=ft.Icon(ft.Icons.DELETE_OUTLINE, size=56, color=WARNING_COLOR), alignment=ft.Alignment(0, 0)),
                    ft.Container(height=8),
                    ft.Text(f"คุณต้องการลบ '{emp_name}' หรือไม่?", size=16, weight=ft.FontWeight.W_500, color="#1E293B", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=4),
                    ft.Text(get_text("delete_warning"), size=13, color="#64748B", text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.padding.all(32),
            width=400,
        ),
        actions=[
            ft.Container(
                content=ft.Row(
                    [
                        ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"), ft.Text(get_text("cancel"), size=14, color="#64748B")], spacing=6), on_click=on_close),
                        ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.DELETE, size=18, color=ft.Colors.WHITE), ft.Text(get_text("delete"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)], spacing=6), on_click=on_confirm, style=ft.ButtonStyle(bgcolor=WARNING_COLOR, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10), elevation=2)),
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.END,
                ),
                padding=ft.padding.all(20),
                border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )