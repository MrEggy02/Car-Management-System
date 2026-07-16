# pages/quotations/quotation_dialog_helpers.py
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
    
    def close_dialog(e=None):
        dialog.open = False
        dialog.update()
    
    def print_order(e=None):
        show_snackbar(get_text("preparing_print"), "info")
    
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
        shape=ft.RoundedRectangleBorder(radius=12),
        bgcolor=ft.Colors.WHITE,
        title=ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.RECEIPT, size=18, color=ft.Colors.WHITE),
                        bgcolor=primary_color,
                        border_radius=8,
                        padding=ft.Padding(left=5, right=5, top=5, bottom=5),
                    ),
                    ft.Text(f"{get_text('job_order_detail')}: {job_no}", size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=10, bottom=10),
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
        ),
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(get_text("status"), size=11, color="#64748B", width=90),
                    status_badge,
                ], spacing=6),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Text(get_text("customer_information"), size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("customer_name"), size=10, color="#64748B"),
                        ft.Text(customer_name, size=12, weight=ft.FontWeight.W_500),
                    ], spacing=1, expand=True),
                    ft.Column([
                        ft.Text(get_text("customer_phone"), size=10, color="#64748B"),
                        ft.Text(customer_phone, size=12),
                    ], spacing=1, expand=True),
                ]),
                ft.Text(get_text("vehicle_information"), size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("plate_number"), size=10, color="#64748B"),
                        ft.Text(plate_number, size=12, weight=ft.FontWeight.W_500),
                    ], spacing=1, expand=True),
                    ft.Column([
                        ft.Text(get_text("car_brand_model"), size=10, color="#64748B"),
                        ft.Text(f"{brand} {model}", size=12),
                    ], spacing=1, expand=True),
                ]),
                ft.Text(get_text("job_details"), size=12, weight=ft.FontWeight.W_500, color="#1E293B"),
                ft.Row([
                    ft.Column([
                        ft.Text(get_text("receive_date"), size=10, color="#64748B"),
                        ft.Text(receive_date, size=11),
                    ], spacing=1, expand=True),
                    ft.Column([
                        ft.Text(get_text("mileage"), size=10, color="#64748B"),
                        ft.Text(f"{mileage} km", size=11),
                    ], spacing=1, expand=True),
                    ft.Column([
                        ft.Text(get_text("fuel_level"), size=10, color="#64748B"),
                        ft.Text(fuel_level, size=11),
                    ], spacing=1, expand=True),
                ]),
                ft.Text(get_text("problem_description"), size=10, color="#64748B"),
                ft.Text(problem, size=11, color="#1E293B"),
                ft.Divider(height=1, color=ft.Colors.GREY_100),
                ft.Row([
                    ft.Text(get_text("service_advisor"), size=10, color="#64748B"),
                    ft.Text(created_by, size=11, color="#64748B", expand=True),
                ], spacing=6),
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=ft.Padding(left=14, right=14, top=12, bottom=8),
            width=400,
            height=420,
        ),
        actions=[
            ft.Container(
                content=actions_row,
                padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog