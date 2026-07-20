# pages/services_page.py
import flet as ft
import sys
import os
import asyncio
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import get_text

# Constants
PRIMARY_COLOR = "#1565C0"
PRIMARY_DARK = "#0D47A1"
WARNING_COLOR = "#DC2626"
PRICE_MAX = 999999999

class ServicesContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.is_loading = False
        self.current_dialog = None
        self.current_snackbar = None
        self.services_data = []
        self.filtered_services = []
        self.search_input = None
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.primary_color = PRIMARY_COLOR
        self.primary_dark = PRIMARY_DARK
        
        # Table data rows container
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.pagination_container = ft.Container()
    
    def build(self):
        """Build services management content with table layout"""
        
        # Beautiful gradient header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("services_title"), 
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
                            ft.Text(get_text("add"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
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
            hint_text=f" {get_text('search')} {get_text('services_title')}...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            on_change=self.filter_services,
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
                    content=ft.Text(get_text('services_name'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=200,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text('services_description'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=250,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text('services_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=10, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text('actions'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _format_time(self, minutes):
        """Format minutes to readable time string"""
        if not minutes or minutes <= 0:
            return "-"
        
        if minutes < 60:
            return f"{minutes} {get_text('minutes')}"
        else:
            hours = minutes // 60
            mins = minutes % 60
            if mins > 0:
                return f"{hours} {get_text('hour')} {mins} {get_text('minute')}"
            else:
                return f"{hours} {get_text('hour')}"
    
    def _create_table_row(self, service, index, row_number):
        """Create a single table row"""
        service_id = service.get('id')
        name = service.get('name', '-')
        description = service.get('description', '-')
        price = service.get('price', 0)
        estimated_time = service.get('estimated_time', 0)
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        if price < 100000:
            price_category = get_text("budget_price")
            price_color = ft.Colors.GREEN_600
            price_bg = "#E8F5E9"
        elif price < 500000:
            price_category = get_text("medium_price")
            price_color = ft.Colors.ORANGE_600
            price_bg = "#FFF3E0"
        else:
            price_category = get_text("high_price")
            price_color = ft.Colors.RED_600
            price_bg = "#FFEBEE"
        
        desc_display = description if description != '-' else get_text("no_description")
        desc_color = ft.Colors.GREY_600 if description != '-' else ft.Colors.GREY_400
        
        price_column = ft.Column([
            ft.Text(
                f"{int(price):,} KIP", 
                size=13, 
                weight=ft.FontWeight.W_500, 
                color=ft.Colors.GREEN_700
            ),
            ft.Container(
                content=ft.Text(price_category, size=9, color=price_color),
                bgcolor=price_bg,
                border_radius=4,
                padding=ft.Padding(left=6, right=6, top=1, bottom=1),
            ),
        ], spacing=3)
        
        desc_container = ft.Container(
            content=ft.Text(desc_display, size=12, color=desc_color, max_lines=2),
            width=250,
            alignment=ft.Alignment(-1, 0),
            padding=ft.Padding(left=10, right=0, top=0, bottom=0),
        )
        if description and description != '-' and len(description) > 40:
            desc_container.tooltip = description
        
        edit_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=PRIMARY_COLOR),
                ft.Text(get_text("edit"), size=12, color=PRIMARY_COLOR),
            ], spacing=4),
            on_click=lambda e, sid=service_id: self._safe_edit(sid, e),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        delete_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
                ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
            ], spacing=4),
            on_click=lambda e, sid=service_id: self._safe_delete(sid, e),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
        )
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(str(row_number), size=13, weight=ft.FontWeight.W_500, color=PRIMARY_COLOR),
                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=6,
                        alignment=ft.Alignment(0, 0),
                    ),
                    width=50,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(name, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
                    width=200,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                    tooltip=name,
                ),
                desc_container,
                ft.Container(
                    content=price_column,
                    width=130,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(left=0, right=10, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Row([edit_btn, delete_btn], spacing=4),
                    width=120,
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
                ft.Icon(ft.Icons.BUILD, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_data"), size=16, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add"), size=13, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.Alignment(0, 0)),
            padding=ft.Padding(left=40, right=40, top=40, bottom=40),
            expand=True,
        )
    
    def update_pagination_controls(self):
        """Update pagination controls"""
        if not self.filtered_services:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (len(self.filtered_services) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Container(
            content=ft.Row([
                ft.Text(f"{get_text('showing')} {len(self.filtered_services)} {get_text('of')} {len(self.services_data)} {get_text('results')}", size=12, color="#64748B"),
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
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_services(self.filtered_services)
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_services(self.filtered_services)
    
    def filter_services(self, e=None):
        query = self.search_input.value.lower() if self.search_input.value else ""
        self.current_page = 1
        
        if not query:
            self.filtered_services = self.services_data.copy()
        else:
            self.filtered_services = [
                service for service in self.services_data
                if query in service.get('name', '').lower()
                or query in service.get('description', '').lower()
            ]
        
        self.display_services(self.filtered_services)
    
    def display_services(self, services):
        self.table_rows.controls.clear()
        
        if not services:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_services = services[start_idx:end_idx]
            
            global_start = start_idx + 1
            
            for i, service in enumerate(page_services):
                row_number = global_start + i
                row = self._create_table_row(service, start_idx + i, row_number)
                self.table_rows.controls.append(row)
        
        self.update_pagination_controls()
        self.page.update()
    
    async def _delayed_load(self):
        await asyncio.sleep(0.2)
        await asyncio.to_thread(self.load_data)
    
    def load_data(self):
        if self.is_loading:
            return
        self.is_loading = True
        
        try:
            print("DEBUG: Loading services data...")
            self.services_data = self.client.get_services()
            self.filtered_services = self.services_data.copy()
            print(f"DEBUG: Loaded {len(self.services_data)} services")
            
            self.display_services(self.filtered_services)
            
        except Exception as e:
            print(f"DEBUG: Error loading services: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
        finally:
            self.is_loading = False
    
    def _safe_edit(self, service_id, event):
        try:
            self.edit_service(service_id)
        except Exception as e:
            print(f"DEBUG: Error in edit: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
    
    def _safe_delete(self, service_id, event):
        try:
            self.delete_service(service_id)
        except Exception as e:
            print(f"DEBUG: Error in delete: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
    
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
    
    def show_add_dialog(self, e=None):
        """Add service dialog with validation"""
        
        # Error labels
        name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        price_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        
        # Price validation function
        def on_price_change(e):
            if price.value:
                # Remove non-digit characters
                cleaned = ''.join(filter(str.isdigit, price.value))
                if cleaned != price.value:
                    price.value = cleaned
                    price.update()
        
        name = ft.TextField(
            label=f"{get_text('services_name')} *",
            hint_text="ເຊັ່ນ: ປ່ຽນນ້ຳມັນເຄື່ອງ",
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
        )
        
        description = ft.TextField(
            label=get_text("services_description"),
            hint_text="ລາຍລະອຽດບໍລິການ",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=56,
        )
        
        price = ft.TextField(
            label=f"{get_text('services_price')} *",
            hint_text="0",
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="0",
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
            on_change=on_price_change,
        )
        
        def validate_fields():
            is_valid = True
            
            # Validate Name
            if not name.value or not name.value.strip():
                name_error.value = get_text("please_enter_name")
                name_error.visible = True
                is_valid = False
            else:
                name_error.visible = False
            
            # Validate Price
            if not price.value or not price.value.strip():
                price_error.value = get_text("please_enter_price")
                price_error.visible = True
                is_valid = False
            else:
                try:
                    price_val = float(price.value.strip())
                    if price_val < 0:
                        price_error.value = get_text("price_must_be_positive")
                        price_error.visible = True
                        is_valid = False
                    elif price_val > PRICE_MAX:
                        price_error.value = f"ລາຄາຕ້ອງບໍ່ເກີນ {PRICE_MAX:,}"
                        price_error.visible = True
                        is_valid = False
                    else:
                        price_error.visible = False
                except ValueError:
                    price_error.value = get_text("price_must_be_number")
                    price_error.visible = True
                    is_valid = False
            
            # Update UI
            name.update()
            price.update()
            name_error.update()
            price_error.update()
            
            return is_valid
        
        def save(e):
            if not validate_fields():
                return
            
            if name.value:
                try:
                    self.client.add_service(
                        name=name.value.strip(),
                        price=float(price.value.strip()) if price.value else 0,
                        description=description.value.strip() if description.value else "",
                        estimated_time=0
                    )
                    self._close_dialog()
                    self.load_data()
                    self.show_snackbar(get_text("add_success"), "success")
                except Exception as err:
                    print(f"Error saving: {err}")
                    traceback.print_exc()
                    self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.BUILD, size=18, color=ft.Colors.WHITE),
                            bgcolor=PRIMARY_COLOR,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text("services_add"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    # Name
                    ft.Column([
                        name,
                        name_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    # Description
                    description,
                    ft.Container(height=4),
                    # Price
                    ft.Column([
                        price,
                        price_error,
                    ], spacing=1),
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
                padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                width=340,
                height=200,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B", size=13),
                            on_click=self._close_dialog,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), color=ft.Colors.WHITE, size=13),
                            on_click=save,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY_COLOR,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                                padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                            ),
                        ),
                    ], spacing=6, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def edit_service(self, service_id):
        """Edit service dialog with validation"""
        
        service = None
        for s in self.services_data:
            if s.get('id') == service_id:
                service = s
                break
        
        if not service:
            self.show_snackbar(get_text("error"), "error")
            return
        
        # Error labels
        name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        price_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        
        # Price validation function
        def on_price_change(e):
            if price.value:
                cleaned = ''.join(filter(str.isdigit, price.value))
                if cleaned != price.value:
                    price.value = cleaned
                    price.update()
        
        name = ft.TextField(
            label=f"{get_text('services_name')} *",
            value=service.get('name', ''),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
        )
        
        description = ft.TextField(
            label=get_text("services_description"),
            value=service.get('description', ''),
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=56,
        )
        
        price = ft.TextField(
            label=f"{get_text('services_price')} *",
            value=str(service.get('price', 0)),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
            on_change=on_price_change,
        )
        
        def validate_fields():
            is_valid = True
            
            # Validate Name
            if not name.value or not name.value.strip():
                name_error.value = get_text("please_enter_name")
                name_error.visible = True
                is_valid = False
            else:
                name_error.visible = False
            
            # Validate Price
            if not price.value or not price.value.strip():
                price_error.value = get_text("please_enter_price")
                price_error.visible = True
                is_valid = False
            else:
                try:
                    price_val = float(price.value.strip())
                    if price_val < 0:
                        price_error.value = get_text("price_must_be_positive")
                        price_error.visible = True
                        is_valid = False
                    elif price_val > PRICE_MAX:
                        price_error.value = f"ລາຄາຕ້ອງບໍ່ເກີນ {PRICE_MAX:,}"
                        price_error.visible = True
                        is_valid = False
                    else:
                        price_error.visible = False
                except ValueError:
                    price_error.value = get_text("price_must_be_number")
                    price_error.visible = True
                    is_valid = False
            
            # Update UI
            name.update()
            price.update()
            name_error.update()
            price_error.update()
            
            return is_valid
        
        def save_edit(e):
            if not validate_fields():
                return
            
            try:
                self.client.update_service(service_id, {
                    'name': name.value.strip(),
                    'description': description.value.strip() if description.value else "",
                    'price': float(price.value.strip()) if price.value else 0,
                    'estimated_time': 0
                })
                self._close_dialog()
                self.load_data()
                self.show_snackbar(get_text("edit_success"), "success")
            except Exception as err:
                print(f"Error in save_edit: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=18, color=ft.Colors.WHITE),
                            bgcolor=PRIMARY_COLOR,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text("services_edit"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    # Name
                    ft.Column([
                        name,
                        name_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    # Description
                    description,
                    ft.Container(height=4),
                    # Price
                    ft.Column([
                        price,
                        price_error,
                    ], spacing=1),
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
                padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                width=340,
                height=200,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B", size=13),
                            on_click=self._close_dialog,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), color=ft.Colors.WHITE, size=13),
                            on_click=save_edit,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY_COLOR,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                                padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                            ),
                        ),
                    ], spacing=6, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def delete_service(self, service_id):
        """Delete confirmation dialog"""
        
        service = None
        for s in self.services_data:
            if s.get('id') == service_id:
                service = s
                break
        
        service_name = service.get('name', get_text('this_service')) if service else get_text('this_service')
        
        def confirm(e):
            try:
                self.client.delete_service(service_id)
                self._close_dialog()
                self.load_data()
                self.show_snackbar(get_text("delete_success"), "success")
            except Exception as err:
                print(f"Error in delete: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, size=18, color=ft.Colors.WHITE),
                            bgcolor=WARNING_COLOR,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
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
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=32, color=WARNING_COLOR),
                    ft.Container(height=4),
                    ft.Text(
                        f"ຕ້ອງການລຶບ '{service_name}' ຫຼື ບໍ່?",
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
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                width=280,
                height=150,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B", size=13),
                            on_click=self._close_dialog,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("delete"), color=ft.Colors.WHITE, size=13),
                            on_click=confirm,
                            style=ft.ButtonStyle(
                                bgcolor=WARNING_COLOR,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                                padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                            ),
                        ),
                    ], spacing=6, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
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