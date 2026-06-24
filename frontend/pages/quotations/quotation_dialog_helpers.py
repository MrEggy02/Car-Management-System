import flet as ft
from i18n import get_text


def show_job_order_detail_dialog(order, primary_color, show_snackbar):
    """Show job order detail dialog"""
    
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
    car_defects = order.get("car_defects", "-") or "-"
    mileage = order.get("mileage", 0)
    fuel_level = order.get("fuel_level", "-")
    signed_receipt_image = order.get("signed_receipt_image", "") or ""
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
    
    def close_dialog(e=None):
        dialog.open = False
        dialog.update()
    
    def print_order(e=None):
        show_snackbar(get_text("preparing_print"), False)
        
    image_display_container = ft.Container()
    if signed_receipt_image:
        from api_client import API_BASE_URL
        import webbrowser
        image_url = f"{API_BASE_URL}/uploads/{signed_receipt_image}"
        image_display_container.content = ft.Column([
            ft.Text(get_text("signed_receipt_image"), size=11, color="#64748B", weight=ft.FontWeight.BOLD),
            ft.GestureDetector(
                on_tap=lambda e: webbrowser.open(image_url),
                mouse_cursor=ft.MouseCursor.CLICK,
                content=ft.Container(
                    content=ft.Image(
                        src=image_url,
                        width=400,
                        height=180,
                        fit="contain",
                    ),
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    bgcolor=ft.Colors.GREY_50,
                    padding=6,
                    tooltip="Click to view full image",
                )
            )
        ], spacing=4)
    else:
        image_display_container.content = ft.Column([
            ft.Text(get_text("signed_receipt_image"), size=11, color="#64748B", weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=18, color="#94A3B8"),
                    ft.Text(get_text("no_image_uploaded"), size=11, color="#94A3B8"),
                ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                border=ft.border.all(1, ft.Colors.GREY_200),
                border_radius=8,
                padding=10,
                alignment=ft.Alignment(0, 0),
            )
        ], spacing=4)
    
    actions_row = ft.Row([
        ft.TextButton(
            content=ft.Text(get_text("close"), color="#64748B"),
            on_click=close_dialog,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        ),
        ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.Icons.PRINT, size=16, color=primary_color),
                ft.Text(get_text("print"), size=12, color=primary_color),
            ], spacing=4),
            on_click=print_order,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
        ),
    ], spacing=8, alignment=ft.MainAxisAlignment.END)
    
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
                
                ft.Text(get_text("car_defects"), size=11, color="#64748B"),
                ft.Text(car_defects, size=12, color="#1E293B"),
                
                image_display_container,
                
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Row([
                    ft.Text(get_text("service_advisor"), size=11, color="#64748B"),
                    ft.Text(created_by, size=12, color="#64748B", expand=True),
                ], spacing=8),
            ], spacing=12, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.all(16),
            width=450,
            height=540,
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