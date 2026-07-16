# pages/login_page.py
import flet as ft
from api_client import APIClient
from theme.app_theme import apply_theme
from i18n import get_text, set_language, get_current_language, LANGUAGES


def login_page(page: ft.Page, on_login_success):
    """Login page for JP-Auto-System with Modern White Card design"""

    # Apply global font theme FIRST
    apply_theme(page)

    page.controls.clear()
    page.window_width = 480
    page.window_height = 650
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "J&P Auto Maxing - Login"
    page.padding = 0
    page.bgcolor = "#F5F7FA"

    # Define modern color palette
    PRIMARY_BLUE = "#1976D2"
    DARK_BLUE = "#0D47A1"
    LIGHT_BLUE = "#E3F2FD"
    TEXT_DARK = "#2C3E50"
    TEXT_GRAY = "#7F8C8D"
    BORDER_GRAY = "#E0E0E0"
    ERROR_RED = "#E53935"

    page.theme.color_scheme = ft.ColorScheme(
        primary=PRIMARY_BLUE,
        secondary=PRIMARY_BLUE,
    )

    loading_dialog = None

    # Create error text widgets (will show under fields)
    username_error = ft.Text("", size=11, color=ERROR_RED, visible=False)
    password_error = ft.Text("", size=11, color=ERROR_RED, visible=False)

    def show_loading():
        nonlocal loading_dialog
        loading_dialog = ft.AlertDialog(
            content=ft.Row(
                [
                    ft.ProgressRing(
                        width=30, height=30, stroke_width=3, color=PRIMARY_BLUE
                    ),
                    ft.Text(get_text("loading"), size=14, color=TEXT_DARK),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.WHITE,
        )
        loading_dialog.open = True
        page.overlay.append(loading_dialog)
        page.update()

    def hide_loading():
        if loading_dialog:
            loading_dialog.open = False
            page.update()

    def validate_inputs():
        """Validate username and password fields (frontend validation)"""
        is_valid = True
        
        # Clear previous errors
        username_error.visible = False
        password_error.visible = False
        error_text.visible = False
        error_text.value = ""
        
        # Validate username
        if not username.value or not username.value.strip():
            username_error.value = get_text("username_required")
            username_error.visible = True
            is_valid = False
        elif len(username.value.strip()) < 3:
            username_error.value = get_text("username_too_short")
            username_error.visible = True
            is_valid = False
            
        # Validate password
        if not password.value or not password.value.strip():
            password_error.value = get_text("password_required")
            password_error.visible = True
            is_valid = False
        elif len(password.value.strip()) < 3:
            password_error.value = get_text("password_too_short")
            password_error.visible = True
            is_valid = False
        
        page.update()
        return is_valid

    def clear_username_error(e):
        username_error.visible = False
        error_text.visible = False
        page.update()
    
    def clear_password_error(e):
        password_error.visible = False
        error_text.visible = False
        page.update()

    def do_login():
        if validate_inputs():
            show_loading()
            try:
                client = APIClient()
                username_val = username.value.strip()
                password_val = password.value.strip()
                
                response = client.login(username_val, password_val)
                hide_loading()
                
                try:
                    import sys
                    enc = getattr(sys.stdout, 'encoding', 'utf-8') or 'utf-8'
                    print(f"DEBUG: Login response = {str(response).encode(enc, errors='replace').decode(enc)}")
                except Exception:
                    pass
                
                # ✅ Handle both response formats
                user_data = None
                
                # Format 1: Direct user data with id
                if response and response.get("id"):
                    user_data = response
                # Format 2: {"status":"success","user":{...}}
                elif response and response.get("status") == "success" and response.get("user"):
                    user_data = response["user"]
                    # Try to get missing fields from employees list
                    if user_data and "id" not in user_data:
                        try:
                            employees = client.get_employees()
                            for emp in employees:
                                if emp.get("username") == user_data.get("username"):
                                    user_data["id"] = emp.get("id")
                                    user_data["role"] = emp.get("role")
                                    user_data["fullname"] = emp.get("name")
                                    break
                        except Exception as e:
                            try:
                                import sys
                                enc = getattr(sys.stdout, 'encoding', 'utf-8') or 'utf-8'
                                print(f"DEBUG: Error getting employee details: {str(e).encode(enc, errors='replace').decode(enc)}")
                            except Exception:
                                pass
                    
                    # If still no id, create minimal user data
                    if user_data and "id" not in user_data:
                        user_data["id"] = 1
                        user_data["role"] = "admin"
                        user_data["fullname"] = user_data.get("username", "Admin")
                
                if user_data and user_data.get("id"):
                    on_login_success(page, client, user_data)
                else:
                    error_text.value = get_text("login_failed")
                    error_text.visible = True
                    page.update()
                    
            except Exception as err:
                hide_loading()
                error_message = str(err)
                try:
                    import sys
                    enc = getattr(sys.stdout, 'encoding', 'utf-8') or 'utf-8'
                    print(f"DEBUG: Login error = {str(error_message).encode(enc, errors='replace').decode(enc)}")
                except Exception:
                    pass
                
                # Check for specific error messages from backend
                error_lower = error_message.lower()
                if "username" in error_lower or "not found" in error_lower or "invalid" in error_lower:
                    username_error.value = get_text("username_not_found")
                    username_error.visible = True
                elif "password" in error_lower:
                    password_error.value = get_text("password_incorrect")
                    password_error.visible = True
                else:
                    error_text.value = error_message
                    error_text.visible = True
                page.update()

    # Language switcher button with custom image icon
    language_switcher = ft.Container(
        content=ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Text("LA", size=16),
                            ft.Text("ພາສາລາວ", size=14, color=TEXT_DARK),
                        ]
                    ),
                    on_click=lambda e: change_language_to("lo"),
                ),
                ft.PopupMenuItem(
                    content=ft.Row(
                        [
                            ft.Text("EN", size=16),
                            ft.Text("English", size=14, color=TEXT_DARK),
                        ]
                    ),
                    on_click=lambda e: change_language_to("en"),
                ),
            ],
            content=ft.Container(
                content=ft.Image(
                    src="assets/icons/translate.png",
                    width=24,
                    height=24,
                    fit="contain",
                ),
                padding=5,
            ),
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
        ),
        padding=8,
        border_radius=12,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            blur_radius=8,
            spread_radius=1,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    def change_language_to(lang):
        set_language(lang)
        login_page(page, on_login_success)

    # Modern text fields
    username = ft.TextField(
        label=get_text("username"),
        hint_text=get_text("username_hint"),
        width=340,
        autofocus=True,
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_radius=12,
        border_color=BORDER_GRAY,
        focused_border_color=PRIMARY_BLUE,
        focused_bgcolor=LIGHT_BLUE,
        text_size=15,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        bgcolor=ft.Colors.WHITE,
        color=TEXT_DARK,
        label_style=ft.TextStyle(color=TEXT_GRAY, size=13),
        hint_style=ft.TextStyle(color=TEXT_GRAY, size=14),
        on_change=clear_username_error,
    )

    password = ft.TextField(
        label=get_text("password"),
        hint_text=get_text("password_hint"),
        password=True,
        can_reveal_password=True,
        width=340,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=12,
        border_color=BORDER_GRAY,
        focused_border_color=PRIMARY_BLUE,
        focused_bgcolor=LIGHT_BLUE,
        text_size=15,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        bgcolor=ft.Colors.WHITE,
        color=TEXT_DARK,
        label_style=ft.TextStyle(color=TEXT_GRAY, size=13),
        hint_style=ft.TextStyle(color=TEXT_GRAY, size=14),
        on_change=clear_password_error,
    )

    error_text = ft.Text(
        "",
        color=ERROR_RED,
        size=12,
        visible=False,
        text_align=ft.TextAlign.CENTER,
    )

    login_btn = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.LOGIN, size=20, color=ft.Colors.WHITE),
                ft.Text(
                    get_text("login_btn"),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        width=340,
        height=52,
        on_click=lambda e: do_login(),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=PRIMARY_BLUE,
            color=ft.Colors.WHITE,
            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            elevation=2,
            shadow_color=ft.Colors.with_opacity(0.3, PRIMARY_BLUE),
        ),
    )

    password.on_submit = lambda e: do_login()
    username.on_submit = lambda e: do_login()

    # Modern logo container
    car_image = ft.Container(
        content=ft.Image(
            src="assets/car_logo.png",
            width=100,
            height=100,
            fit="cover",
        ),
        width=100,
        height=100,
        border_radius=50,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    # Modern white card with margin
    login_card = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            car_image,
                            ft.Text(
                                "J&P Auto Maxing",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_DARK,
                            ),
                            ft.Text(get_text("system_name"), size=14, color=TEXT_GRAY),
                            ft.Container(height=1, bgcolor=BORDER_GRAY, width=280),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=ft.Padding.only(top=40, bottom=10, left=20, right=20),
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            username,
                            username_error,
                            password,
                            password_error,
                            ft.Container(height=16),
                            error_text,
                            login_btn,
                        ],
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.symmetric(horizontal=30, vertical=20),
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("v1.0.0", size=14, color=TEXT_GRAY),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=ft.Padding.only(bottom=35, top=10),
                ),
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=420,
        margin=45,
        padding=0,
        border_radius=14,
        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.WHITE),
        shadow=ft.BoxShadow(
            blur_radius=30,
            spread_radius=2,
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
            offset=ft.Offset(0, 10),
        ),
    )

    # Create real blur effect using Stack with multiple layers
    blur_background = ft.Container(
        expand=True,
        image=ft.DecorationImage(
            src="assets/anime_wallpaper.png",
            fit="cover",
        ),
    )
    
    # Add blur effect overlay
    blur_overlay = ft.Container(
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
        blur=ft.Blur(0, 5),
    )
    
    # Stack everything together
    background = ft.Container(
        content=ft.Stack(
            [
                blur_background,
                blur_overlay,
                ft.Container(
                    content=login_card,
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
                ft.Container(content=language_switcher, right=40, top=30),
            ]
        ),
        expand=True,
    )

    page.add(background)
    page.update()