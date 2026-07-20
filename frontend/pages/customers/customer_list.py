# pages/customers/customer_list.py
import flet as ft
from flet import Alignment
import asyncio
import traceback
from typing import Dict, Callable

from i18n import get_text
from pages.customers.customer_dialogs import (
    show_add_dialog, 
    show_edit_dialog, 
    show_detail_dialog,
    show_delete_dialog,
    show_success_popup
)


class CustomerListContent:
    def __init__(self, page: ft.Page, client, user: dict, navigate: Callable):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.is_loading = False
        self.current_dialog = None
        self.current_snackbar = None
        self.customers_data = []
        self.filtered_customers = []
        self.search_input = None
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.brands_list = []
        
        # Table data rows container
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.pagination_container = ft.Container()
    
    def build(self):
        """Build customers management content with table layout"""
        
        # Beautiful gradient header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("customer_list_title"), 
                                size=18, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.WHITE
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("add_new_customer"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=lambda e: self.show_add_dialog(e),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=0,
                            padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                        ),
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=24, right=24, top=12, bottom=12),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
        
        # Search Bar
        self.search_input = ft.TextField(
            hint_text=f" {get_text('search_customer_by_name_or_phone')}",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            on_change=self.filter_customers,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        search_container = ft.Container(
            content=self.search_input,
            expand=True,
        )
        
        control_bar = ft.Container(
            content=search_container,
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor="#F5F7FA",
        )
        
        table_header = self._create_table_header()
        
        table_scroll_container = ft.Container(
            content=self.table_rows,
            expand=True,
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            bgcolor=ft.Colors.WHITE,
        )
        
        table_container = ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                table_scroll_container,
            ], spacing=0),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(
                top_left=12, top_right=12, bottom_left=12, bottom_right=12
            ),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
        )
        
        self.update_pagination_controls()
        
        main_content = ft.Container(
            content=ft.Column([
                table_container,
                self.pagination_container,
            ], spacing=0),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        main_container = ft.Container(
            content=main_content,
            expand=True,
        )
        
        self.page.run_task(self._delayed_load)
        
        return ft.Column([
            header,
            control_bar,
            main_container,
        ], expand=True, spacing=0)
    
    def _create_table_header(self):
        """Create table header row"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=50,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('customer_name'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=180,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text('customer_phone'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=150,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('customer_address'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=250,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text('vehicles'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('actions'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=200,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _create_table_row(self, customer, index, row_number):
        """Create a single table row - using vehicle_count from API"""
        customer_id = customer.get('id')
        name = customer.get('name', '-')
        phone = customer.get('phone', '-')
        address = customer.get('address', '-')
        vehicle_count = customer.get('vehicle_count', 0)
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        # Shorten address if too long
        address_display = address if len(address) <= 30 else address[:27] + "..."
        
        # Action buttons
        view_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=16, color=self.primary_color),
                ft.Text(get_text("view"), size=12, color=self.primary_color),
            ], spacing=4),
            on_click=lambda e, cid=customer_id: self.show_detail_dialog(cid),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        edit_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=self.primary_color),
                ft.Text(get_text("edit"), size=12, color=self.primary_color),
            ], spacing=4),
            on_click=lambda e, cid=customer_id: self.show_edit_dialog(cid),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        delete_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
                ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
            ], spacing=4),
            on_click=lambda e, cid=customer_id, cname=name: self.show_delete_dialog(cid, cname),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        row = ft.Container(
            content=ft.Row([
                # Row number column
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(str(row_number), size=13, weight=ft.FontWeight.W_500, color=self.primary_color),
                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=6,
                        alignment=ft.Alignment(0, 0),
                    ),
                    width=50,
                    alignment=ft.Alignment(0, 0),
                ),
                # Name column
                ft.Container(
                    content=ft.Text(name, size=13, weight=ft.FontWeight.W_500, color="#1E293B", max_lines=1),
                    width=180,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    tooltip=name,
                ),
                # Phone column
                ft.Container(
                    content=ft.Text(phone, size=13, color="#1E293B", max_lines=1),
                    width=150,
                    alignment=ft.Alignment(0, 0),
                ),
                # Address column
                ft.Container(
                    content=ft.Text(address_display, size=12, color="#64748B", max_lines=2),
                    width=250,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    tooltip=address if len(address) > 30 else None,
                ),
                # Vehicles count
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(str(vehicle_count), size=13, weight=ft.FontWeight.W_500, color=self.primary_color),
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=12,
                        alignment=ft.Alignment(0, 0),
                    ),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                # Actions column
                ft.Container(
                    content=ft.Row([view_btn, edit_btn, delete_btn], spacing=4),
                    width=200,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    def _create_empty_state(self):
        """Create empty state when no data"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_data"), size=16, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add_to_register"), size=13, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.Alignment(0, 0)),
            padding=ft.Padding(left=40, right=40, top=40, bottom=40),
            expand=True,
        )
    
    def update_pagination_controls(self):
        """Update pagination controls"""
        if not self.filtered_customers:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (len(self.filtered_customers) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Container(
            content=ft.Row([
                ft.Text(f"{get_text('showing')} {len(self.filtered_customers)} {get_text('of')} {len(self.customers_data)} {get_text('results')}", size=12, color="#64748B"),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_LEFT,
                            icon_size=20,
                            on_click=self.prev_page,
                            disabled=prev_disabled,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                        ft.Container(
                            content=ft.Text(f"{self.current_page}/{self.total_pages}", size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                            padding=ft.Padding(left=15, right=15, top=0, bottom=0),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_RIGHT,
                            icon_size=20,
                            on_click=self.next_page,
                            disabled=next_disabled,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        ),
                    ]),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=20, right=20, top=16, bottom=16),
            bgcolor="#F5F7FA",
        )
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_customers()
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_customers()
    
    def filter_customers(self, e=None):
        query = self.search_input.value.lower() if self.search_input.value else ""
        self.current_page = 1
        
        if not query:
            self.filtered_customers = self.customers_data.copy()
        else:
            self.filtered_customers = [
                c for c in self.customers_data
                if query in c.get('name', '').lower()
                or query in c.get('phone', '').lower()
            ]
        
        self.display_customers()
    
    def display_customers(self):
        """Display customers with pagination (using already loaded data)"""
        self.table_rows.controls.clear()
        
        if not self.filtered_customers:
            self.table_rows.controls.append(self._create_empty_state())
            self.update_pagination_controls()
            self.page.update()
            return
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.filtered_customers))
        page_customers = self.filtered_customers[start_idx:end_idx]
        
        for i, customer in enumerate(page_customers):
            row_number = start_idx + i + 1
            row = self._create_table_row(customer, start_idx + i, row_number)
            self.table_rows.controls.append(row)
        
        self.update_pagination_controls()
        self.page.update()
    
    def load_brands(self):
        """Load brands for dropdown"""
        try:
            self.brands_list = self.client.get_brands()
        except Exception as ex:
            print(f"Error loading brands: {ex}")
            self.brands_list = []
    
    async def _delayed_load(self):
        await asyncio.gather(
            asyncio.to_thread(self.load_brands),
            asyncio.to_thread(self.load_data)
        )
    
    def load_data(self):
        if self.is_loading:
            return
        self.is_loading = True
        
        try:
            print("DEBUG: Loading customers with vehicle counts...")
            # Use new API that returns vehicle_count directly
            self.customers_data = self.client.get_customers_with_vehicles()
            # Sort by id descending (newest first)
            self.customers_data.sort(key=lambda x: x.get('id', 0), reverse=True)
            self.filtered_customers = self.customers_data.copy()
            print(f"DEBUG: Loaded {len(self.customers_data)} customers with vehicle counts")
            
            self.display_customers()
            
        except Exception as e:
            print(f"DEBUG: Error loading customers: {e}")
            traceback.print_exc()
            # Fallback to old method
            try:
                self.customers_data = self.client.get_customers()
                for customer in self.customers_data:
                    customer['vehicle_count'] = 0
                self.customers_data.sort(key=lambda x: x.get('id', 0), reverse=True)
                self.filtered_customers = self.customers_data.copy()
                self.display_customers()
            except:
                self.show_snackbar(f"{get_text('error')}: {e}", "error")
        finally:
            self.is_loading = False
    
    def _open_dialog(self, dialog):
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                if self.current_dialog in self.page.overlay:
                    self.page.overlay.remove(self.current_dialog)
            
            self.current_dialog = dialog
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
        except Exception as e:
            print(f"DEBUG: Error opening dialog: {e}")
    
    def _close_dialog(self, e=None):
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
    def show_success_popup(self, customer_id, customer_name, plate_number):
        """Show success popup after registration"""
        def close_popup(popup):
            popup.open = False
            self.page.update()
        
        popup = show_success_popup(customer_id, customer_name, plate_number, self.primary_color, close_popup)
        self.page.overlay.append(popup)
        popup.open = True
        self.page.update()
    
    def show_add_dialog(self, e=None):
        def on_save(customer_data, vehicle_data):
            try:
                result = self.client.register_customer_with_vehicle(customer_data, vehicle_data)
                if result:
                    customer_id = result.get('customer_id')
                    self._close_dialog()
                    self.load_data()
                    self.show_success_popup(customer_id, customer_data["name"], vehicle_data["plate_number"])
            except Exception as err:
                print(f"Error saving: {err}")
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = show_add_dialog(self.primary_color, self.brands_list, on_save, self._close_dialog)
        self._open_dialog(dialog)
    
    def show_detail_dialog(self, customer_id):
        customer = next((c for c in self.customers_data if c.get('id') == customer_id), None)
        if not customer:
            self.show_snackbar(f"❌ {get_text('error')}", "error")
            return
        
        # Get vehicles dynamically for this customer
        try:
            vehicles = self.client.get_vehicles(customer_id=customer_id) or []
            for vehicle in vehicles:
                brand_id = vehicle.get('brand_id')
                if brand_id:
                    brand = next((b for b in self.brands_list if b.get('id') == brand_id), None)
                    vehicle['brand_name'] = brand.get('name') if brand else "-"
                else:
                    vehicle['brand_name'] = "-"
        except Exception as ex:
            print(f"Error loading vehicles for customer details: {ex}")
            vehicles = []
        
        dialog = show_detail_dialog(customer, vehicles, self.brands_list, self.primary_color, self._close_dialog)
        self._open_dialog(dialog)
    
    def show_edit_dialog(self, customer_id):
        customer = next((c for c in self.customers_data if c.get('id') == customer_id), None)
        if not customer:
            self.show_snackbar(f"❌ {get_text('error')}", "error")
            return
        
        # Get vehicles dynamically for this customer
        try:
            vehicles = self.client.get_vehicles(customer_id=customer_id) or []
            for vehicle in vehicles:
                brand_id = vehicle.get('brand_id')
                if brand_id:
                    brand = next((b for b in self.brands_list if b.get('id') == brand_id), None)
                    vehicle['brand_name'] = brand.get('name') if brand else "-"
                else:
                    vehicle['brand_name'] = "-"
        except Exception as ex:
            print(f"Error loading vehicles for customer edit: {ex}")
            vehicles = []
        
        def on_save_customer(update_data):
            try:
                self.client.update_customer(customer_id, update_data)
                self.show_snackbar(get_text("update_successful"), "success")
                # Reload data after save
                self.load_data()
            except Exception as err:
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        def on_add_vehicle(vehicle_data, callback):
            try:
                result = self.client.add_vehicle(vehicle_data)
                if result:
                    brand_name = "-"
                    if vehicle_data.get('brand_id'):
                        brand = next((b for b in self.brands_list if b.get('id') == vehicle_data['brand_id']), None)
                        if brand:
                            brand_name = brand.get('name')
                    
                    new_vehicle = {
                        'id': result.get('id') if isinstance(result, dict) else result,
                        'plate_number': vehicle_data['plate_number'],
                        'brand_id': vehicle_data['brand_id'],
                        'brand_name': brand_name,
                        'model': vehicle_data['model'],
                        'year': vehicle_data['year'],
                        'color': vehicle_data['color'],
                        'customer_id': customer_id
                    }
                    if callback:
                        callback(new_vehicle)
                    self.show_snackbar(get_text("vehicle_added_successfully"), "success")
            except Exception as err:
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        def on_edit_vehicle(vehicle_id, vehicle_data, callback):
            try:
                self.client.update_vehicle(vehicle_id, vehicle_data)
                brand_name = "-"
                if vehicle_data.get('brand_id'):
                    brand = next((b for b in self.brands_list if b.get('id') == vehicle_data['brand_id']), None)
                    if brand:
                        brand_name = brand.get('name')
                
                updated_vehicle = {
                    'id': vehicle_id,
                    'plate_number': vehicle_data['plate_number'],
                    'brand_id': vehicle_data['brand_id'],
                    'brand_name': brand_name,
                    'model': vehicle_data['model'],
                    'year': vehicle_data['year'],
                    'color': vehicle_data['color'],
                    'customer_id': customer_id
                }
                if callback:
                    callback(updated_vehicle)
                self.show_snackbar(get_text("edit_success"), "success")
            except Exception as err:
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        def on_delete_vehicle(vehicle_id, callback):
            try:
                self.client.delete_vehicle(vehicle_id)
                if callback:
                    callback(vehicles)
                self.show_snackbar(get_text("vehicle_deleted_successfully"), "success")
            except Exception as err:
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        def on_save_complete():
            self.load_data()
            self._close_dialog()
        
        def on_cancel():
            self._close_dialog()
        
        dialog = show_edit_dialog(
            customer, vehicles, self.brands_list, self.primary_color,
            on_save_customer, on_add_vehicle, on_edit_vehicle, on_delete_vehicle,
            on_save_complete, on_cancel
        )
        self._open_dialog(dialog)
    
    def show_delete_dialog(self, customer_id, customer_name):
        def on_confirm(e):
            try:
                self.client.delete_customer(customer_id)
                self._close_dialog()
                self.load_data()
                self.show_snackbar(get_text("delete_success"), "success")
            except Exception as err:
                print(f"Error in delete: {err}")
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = show_delete_dialog(customer_name, on_confirm, self._close_dialog)
        self._open_dialog(dialog)
    
    def show_snackbar(self, message, type="success"):
        """Show snackbar notification - Bottom center with auto width"""
        
        # Remove existing snackbar if any
        if self.current_snackbar:
            try:
                self.page.overlay.remove(self.current_snackbar)
            except:
                pass
            self.current_snackbar = None
        
        if type == "success":
            bgcolor = ft.Colors.GREEN_600
            icon = ft.Icons.CHECK_CIRCLE
        elif type == "error":
            bgcolor = ft.Colors.RED_600
            icon = ft.Icons.ERROR
        else:
            bgcolor = ft.Colors.GREY_800
            icon = ft.Icons.INFO
        
        # Create snackbar content with auto width
        snack_content = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=ft.Colors.WHITE, size=16),
                    ft.Text(message, color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.W_500),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=8, bottom=8),
            bgcolor=bgcolor,
            border_radius=8,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            ),
        )
        
        # Create overlay container - positioned at bottom center
        snackbar = ft.Container(
            content=snack_content,
            margin=ft.Margin(left=30, right=30, top=0, bottom=20),
            alignment=ft.Alignment(0, 1),  # Bottom Center
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            opacity=0,
        )
        
        # Add to overlay
        self.page.overlay.append(snackbar)
        self.current_snackbar = snackbar
        
        # Animate in
        snackbar.opacity = 1
        self.page.update()
        
        # Auto dismiss after 3 seconds using asyncio
        async def dismiss_after_delay():
            await asyncio.sleep(2.0)
            if snackbar in self.page.overlay:
                snackbar.opacity = 0
                self.page.update()
                await asyncio.sleep(0.3)
                if snackbar in self.page.overlay:
                    self.page.overlay.remove(snackbar)
                    if self.current_snackbar == snackbar:
                        self.current_snackbar = None
                    self.page.update()
        
        # Run the dismiss task
        self.page.run_task(dismiss_after_delay)