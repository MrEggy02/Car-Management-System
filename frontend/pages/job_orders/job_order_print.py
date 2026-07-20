# # pages/job_orders/job_order_print.py
# import flet as ft
# from flet import Alignment
# from typing import Dict, Callable
# from datetime import datetime

# from i18n import get_text


# class JobOrderPrintContent:
#     def __init__(self, page: ft.Page, client, user: dict, navigate: Callable, order_id: int = None):
#         self.page = page
#         self.client = client
#         self.user = user
#         self.navigate = navigate
#         self.order_id = order_id
#         self.order_data = None
#         self.primary_color = "#1565C0"
#         self.primary_dark = "#0D47A1"

#     def build(self):
#         # Beautiful gradient header
#         header = ft.Container(
#             content=ft.Row(
#                 [
#                     ft.IconButton(
#                         icon=ft.Icons.ARROW_BACK,
#                         icon_size=24,
#                         icon_color=ft.Colors.WHITE,
#                         on_click=lambda e: self.navigate("job_order_list"),
#                         tooltip=get_text("back"),
#                         style=ft.ButtonStyle(
#                             bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
#                             shape=ft.RoundedRectangleBorder(radius=10),
#                         ),
#                     ),
#                     ft.Column(
#                         [
#                             ft.Text(
#                                 get_text("job_order_print"),
#                                 size=22,
#                                 weight=ft.FontWeight.BOLD,
#                                 color=ft.Colors.WHITE,
#                             ),
#                             ft.Text(
#                                 get_text("print_receipt"),
#                                 size=13,
#                                 color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
#                             ),
#                         ],
#                         spacing=2,
#                     ),
#                     ft.Container(expand=True),
#                     ft.Container(
#                         content=ft.Icon(ft.Icons.PRINT, size=28, color=ft.Colors.WHITE),
#                         bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
#                         border_radius=15,
#                         padding=ft.Padding(left=8, right=8, top=8, bottom=8),
#                     ),
#                 ],
#                 spacing=16,
#                 vertical_alignment=ft.CrossAxisAlignment.CENTER,
#             ),
#             padding=ft.Padding(left=32, right=32, top=20, bottom=20),
#             gradient=ft.LinearGradient(
#                 begin=ft.Alignment(-1, -1),
#                 end=ft.Alignment(1, 1),
#                 colors=[self.primary_color, self.primary_dark],
#             ),
#             border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
#             shadow=ft.BoxShadow(
#                 blur_radius=15,
#                 color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
#             ),
#         )
        
#         # Load order data
#         if not self.order_data:
#             self.load_order_data()
        
#         # If no data yet, show loading
#         if not self.order_data:
#             loading = ft.Container(
#                 content=ft.Column([
#                     ft.ProgressRing(width=50, height=50, stroke_width=5),
#                     ft.Container(height=20),
#                     ft.Text(get_text("loading"), size=16, color="#64748B"),
#                 ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#                 alignment=Alignment.CENTER,
#                 expand=True,
#             )
            
#             return ft.Container(
#                 content=ft.Column([header, loading]),
#                 expand=True,
#                 bgcolor="#F5F7FA",
#             )
        
#         # Receipt content
#         receipt = self._create_receipt()
        
#         # Action buttons
#         action_buttons = ft.Container(
#             content=ft.Row([
#                 ft.OutlinedButton(
#                     content=ft.Row([
#                         ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
#                         ft.Text(get_text("close"), size=14, color="#64748B"),
#                     ], spacing=6),
#                     on_click=lambda e: self.navigate("job_order_list"),
#                     style=ft.ButtonStyle(
#                         shape=ft.RoundedRectangleBorder(radius=10),
#                         side=ft.BorderSide(1, ft.Colors.GREY_300),
#                         padding=ft.Padding(left=20, right=20, top=12, bottom=12),
#                     ),
#                 ),
#                 ft.ElevatedButton(
#                     content=ft.Row([
#                         ft.Icon(ft.Icons.PRINT, size=18, color=ft.Colors.WHITE),
#                         ft.Text(get_text("print"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
#                     ], spacing=6),
#                     on_click=self.print_receipt,
#                     style=ft.ButtonStyle(
#                         bgcolor=self.primary_color,
#                         shape=ft.RoundedRectangleBorder(radius=10),
#                         elevation=2,
#                         padding=ft.Padding(left=24, right=24, top=12, bottom=12),
#                     ),
#                 ),
#             ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
#             padding=ft.Padding(left=0, right=0, top=20, bottom=0),
#         )
        
#         # Scrollable content
#         scrollable_content = ft.Column(
#             [receipt, action_buttons],
#             spacing=20,
#             scroll=ft.ScrollMode.AUTO,
#             expand=True,
#         )
        
#         content_area = ft.Container(
#             content=scrollable_content,
#             expand=True,
#             padding=ft.Padding(left=32, right=32, top=32, bottom=32),
#             bgcolor="#F5F7FA",
#         )
        
#         # Main layout
#         main_content = ft.Container(
#             content=ft.Column([
#                 header,
#                 content_area,
#             ]),
#             expand=True,
#             bgcolor="#F5F7FA",
#         )
        
#         return main_content
    
#     def load_order_data(self):
#         """Load job order data from API"""
#         try:
#             self.order_data = self.client.get_job_order(self.order_id)
#             self.page.update()
#         except Exception as ex:
#             print(f"Error loading order: {ex}")
#             self.order_data = {}
#             self.page.update()
    
#     def _create_receipt(self):
#         """Create receipt UI"""
#         order = self.order_data or {}
        
#         job_no = order.get("job_no", "N/A")
#         receive_date = order.get("receive_date", "")
#         if receive_date:
#             try:
#                 dt = datetime.strptime(str(receive_date), "%Y-%m-%d %H:%M:%S")
#                 receive_date = dt.strftime("%d/%m/%Y %H:%M")
#             except:
#                 try:
#                     dt = datetime.strptime(str(receive_date), "%Y-%m-%d")
#                     receive_date = dt.strftime("%d/%m/%Y")
#                 except:
#                     pass
        
#         customer_name = order.get("customer_name", "-")
#         customer_phone = order.get("customer_phone", "-")
#         customer_address = order.get("address", "-")
        
#         plate_number = order.get("plate_number", "-")
#         brand = order.get("brand", "-")
#         model = order.get("model", "-")
#         year = order.get("year", "")
#         color = order.get("color", "-")
        
#         problem = order.get("problem_description", "-")
#         mileage = order.get("mileage", 0)
#         fuel_level = order.get("fuel_level", "-")
        
#         created_by = order.get("created_by_name", self.user.get("fullname", "-"))
        
#         # Shop info
#         shop_name = "J&P Auto Maxing"
#         shop_address = "Vientiane, Lao PDR"
#         shop_phone = "+856 20 0000 0000"
        
#         return ft.Card(
#             content=ft.Container(
#                 content=ft.Column([
#                     # Header
#                     ft.Container(
#                         content=ft.Column([
#                             ft.Text(shop_name, size=24, weight=ft.FontWeight.BOLD, color=self.primary_color, text_align=ft.TextAlign.CENTER),
#                             ft.Text(get_text("receipt_title"), size=16, weight=ft.FontWeight.W_500, color="#1E293B", text_align=ft.TextAlign.CENTER),
#                             ft.Text(shop_address, size=11, color="#64748B", text_align=ft.TextAlign.CENTER),
#                             ft.Text(shop_phone, size=11, color="#64748B", text_align=ft.TextAlign.CENTER),
#                             ft.Divider(height=1, color=ft.Colors.GREY_200),
#                         ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
#                         padding=ft.Padding(left=0, right=0, top=0, bottom=16),
#                     ),
                    
#                     # Job Info
#                     ft.Row([
#                         ft.Column([
#                             ft.Text(get_text("job_number"), size=12, color="#64748B"),
#                             ft.Text(job_no, size=18, weight=ft.FontWeight.BOLD, color="#1E293B"),
#                         ], spacing=2, expand=True),
#                         ft.Column([
#                             ft.Text(get_text("receive_date"), size=12, color="#64748B"),
#                             ft.Text(receive_date, size=14, weight=ft.FontWeight.W_500),
#                         ], spacing=2, expand=True, horizontal_alignment=ft.CrossAxisAlignment.END),
#                     ]),
                    
#                     ft.Container(height=16),
                    
#                     # Customer Info
#                     ft.Text(get_text("customer_info"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
#                     ft.Container(height=8),
#                     ft.Row([
#                         ft.Icon(ft.Icons.PERSON, size=16, color="#64748B"),
#                         ft.Text(f"{get_text('name')}: {customer_name}", size=13),
#                     ], spacing=8),
#                     ft.Row([
#                         ft.Icon(ft.Icons.PHONE, size=16, color="#64748B"),
#                         ft.Text(f"{get_text('phone')}: {customer_phone}", size=13),
#                     ], spacing=8),
#                     *(
#                         [ft.Row([
#                             ft.Icon(ft.Icons.LOCATION_ON, size=16, color="#64748B"),
#                             ft.Text(f"{get_text('address')}: {customer_address}", size=13, expand=True),
#                         ], spacing=8)]
#                         if customer_address and customer_address != "-"
#                         else []
#                     ),
                    
#                     ft.Container(height=16),
                    
#                     # Vehicle Info
#                     ft.Text(get_text("vehicle_info"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
#                     ft.Container(height=8),
#                     ft.Row([
#                         ft.Icon(ft.Icons.CONFIRMATION_NUMBER, size=16, color="#64748B"),
#                         ft.Text(f"{get_text('plate_number')}: {plate_number}", size=13),
#                     ], spacing=8),
#                     ft.Row([
#                         ft.Icon(ft.Icons.CAR_RENTAL, size=16, color="#64748B"),
#                         ft.Text(f"{get_text('brand')}: {brand} {model} {f'({year})' if year else ''}", size=13),
#                     ], spacing=8),
#                     ft.Row([
#                         ft.Icon(ft.Icons.COLOR_LENS, size=16, color="#64748B"),
#                         ft.Text(f"{get_text('color')}: {color}", size=13),
#                     ], spacing=8),
#                     ft.Row([
#                         ft.Icon(ft.Icons.SPEED, size=16, color="#64748B"),
#                         ft.Text(f"{get_text('mileage')}: {mileage:,} km", size=13),
#                     ], spacing=8),
#                     ft.Row([
#                         ft.Icon(ft.Icons.LOCAL_GAS_STATION, size=16, color="#64748B"),
#                         ft.Text(f"{get_text('fuel_level')}: {fuel_level}", size=13),
#                     ], spacing=8),
                    
#                     ft.Container(height=16),
                    
#                     # Problem Description
#                     ft.Text(get_text("problem_description"), size=14, weight=ft.FontWeight.BOLD, color="#1E293B"),
#                     ft.Container(height=8),
#                     ft.Container(
#                         content=ft.Text(problem, size=13, color="#1E293B"),
#                         padding=ft.Padding(left=12, right=12, top=12, bottom=12),
#                         bgcolor=ft.Colors.GREY_50,
#                         border_radius=8,
#                     ),
                    
#                     ft.Container(height=16),
                    
#                     # Service Advisor
#                     ft.Row([
#                         ft.Icon(ft.Icons.PERSON_OUTLINE, size=16, color="#64748B"),
#                         ft.Text(f"{get_text('service_advisor')}: {created_by}", size=12, color="#64748B"),
#                     ], spacing=8),
                    
#                     ft.Container(height=20),
                    
#                     # Footer
#                     ft.Divider(height=1, color=ft.Colors.GREY_200),
#                     ft.Container(height=8),
#                     ft.Text(get_text("thank_you_message"), size=11, color="#64748B", text_align=ft.TextAlign.CENTER),
#                     ft.Text(get_text("contact_info"), size=10, color="#64748B", text_align=ft.TextAlign.CENTER),
                    
#                 ], spacing=0),
#                 padding=ft.Padding(left=24, right=24, top=24, bottom=24),
#             ),
#             elevation=3,
#         )
    
#     def print_receipt(self, e):
#         """Export job order as A4 PDF and open it"""
#         try:
#             # Show preparing message
#             self._show_snack_bar(get_text("preparing_print"), is_error=False)
            
#             # Fetch PDF bytes from backend
#             pdf_bytes = self.client.get_job_order_pdf(self.order_id)
            
#             # Ensure output directory exists in project root
#             import os
#             output_dir = "output"
#             if not os.path.exists(output_dir):
#                 os.makedirs(output_dir)
                
#             job_no = (self.order_data or {}).get("job_no", f"JOB_{self.order_id}")
#             file_name = f"job_order_{job_no}.pdf"
#             file_path = os.path.join(output_dir, file_name)
            
#             # Write PDF bytes
#             with open(file_path, "wb") as f:
#                 f.write(pdf_bytes)
                
#             # Open PDF
#             os.startfile(file_path)
#             self._show_snack_bar(get_text("pdf_export_success"), is_error=False)
            
#         except Exception as ex:
#             print(f"Error printing PDF: {ex}")
#             self._show_snack_bar(f"{get_text('pdf_export_failed')}: {str(ex)}", is_error=True)

#     def _show_snack_bar(self, message, is_error=False):
#         self.page.snack_bar = ft.SnackBar(
#             content=ft.Text(message, size=13),
#             bgcolor=ft.Colors.RED_600 if is_error else ft.Colors.GREEN_600,
#             open=True,
#             duration=2000,
#         )
#         self.page.update()