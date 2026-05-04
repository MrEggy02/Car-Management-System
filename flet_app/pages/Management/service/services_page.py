# pages/services_page.py
import flet as ft
import sys
import os
import asyncio
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import get_text

class ServicesContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.is_loading = False
        self.current_dialog = None
        self.services_data = []
        self.filtered_services = []
        self.search_input = None
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        
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
                                size=24, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.WHITE
                            ),
                            ft.Text(
                                get_text("card_services_sub"),
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
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
                            padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        ),
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=20, horizontal=32),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
           
        )
        
        # Search Bar with beautiful design
        self.search_input = ft.TextField(
            hint_text=f"🔍 {get_text('search')} {get_text('services_title')}...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            on_change=self.filter_services,
            prefix_icon=ft.Icons.SEARCH,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        search_container = ft.Container(
            content=self.search_input,
            expand=True,
        )
        
        # Control bar
        control_bar = ft.Container(
            content=search_container,
            padding=ft.padding.all(20),
            bgcolor="#F5F7FA",
        )
        
        # Table Header
        table_header = self._create_table_header()
        
        # Table scroll container
        table_scroll_container = ft.Container(
            content=self.table_rows,
            expand=True,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            bgcolor=ft.Colors.WHITE,
        )
        
        # Table Container
        table_container = ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                table_scroll_container,
            ], spacing=0),
            margin=ft.margin.only(left=20, right=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(
                top_left=12, top_right=12, bottom_left=12, bottom_right=12
            ),
            border=ft.border.all(1, ft.Colors.GREY_200),
            expand=True,
        )
        
        # Pagination container (will be updated by update_pagination)
        self.pagination_container = ft.Container(
            padding=ft.padding.symmetric(vertical=16, horizontal=20),
            bgcolor="#F5F7FA",
        )
        
        # Main content area
        main_content = ft.Container(
            content=ft.Column([
                table_container,
                self.pagination_container,
            ], spacing=0),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Main container
        main_container = ft.Container(
            content=main_content,
            expand=True,
        )
        
        # Load data after UI is built
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
                    width=180,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('services_description'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=220,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('services_price'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                ft.Container(
                    content=ft.Text(get_text('services_hours'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('actions'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=14, horizontal=10),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _create_table_row(self, service, index, row_number):
        """Create a single table row"""
        service_id = service.get('id')
        service_name = service.get('service_name', '-')
        description = service.get('description', '-')
        price = service.get('price', 0)
        estimated_hours = service.get('estimated_hours', 0)
        
        # Row background color (alternate)
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        # Determine price range category
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
        
        # Description display
        desc_display = description if description != '-' else get_text("no_description")
        desc_color = ft.Colors.GREY_600 if description != '-' else ft.Colors.GREY_400
        
        # Hours display
        if estimated_hours == 1:
            hours_text = f"{get_text('hours_single')}"
        else:
            hours_text = f"{get_text('hours_plural').format(estimated_hours)}"
        
        # Price column with category badge
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
                padding=ft.padding.symmetric(horizontal=6, vertical=1),
            ),
        ], spacing=3)
        
        # Description with tooltip if truncated
        desc_container = ft.Container(
            content=ft.Text(desc_display, size=12, color=desc_color, max_lines=2),
            width=220,
            alignment=ft.Alignment(-1, 0),
            padding=ft.padding.only(left=10),
        )
        if description and description != '-' and len(description) > 40:
            desc_container.tooltip = description
        
        # Action buttons
        edit_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color="#1565C0"),
                ft.Text(get_text("edit"), size=12, color="#1565C0"),
            ], spacing=4),
            on_click=lambda e, sid=service_id: self._safe_edit(sid, e),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        delete_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
                ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
            ], spacing=4),
            on_click=lambda e, sid=service_id: self._safe_delete(sid, e),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
        )
        
        row = ft.Container(
            content=ft.Row([
                # Row number column with badge styling
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(str(row_number), size=13, weight=ft.FontWeight.W_500, color="#1565C0"),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=6,
                        alignment=ft.Alignment(0, 0),
                    ),
                    width=50,
                    alignment=ft.Alignment(0, 0),
                ),
                # Service Name column
                ft.Container(
                    content=ft.Text(service_name, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
                    width=180,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.padding.only(left=10),
                    tooltip=service_name,
                ),
                # Description column
                desc_container,
                # Price column
                ft.Container(
                    content=price_column,
                    width=120,
                    alignment=ft.Alignment(1, 0),
                    padding=ft.padding.only(right=10),
                ),
                # Hours column
                ft.Container(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SCHEDULE, size=14, color=ft.Colors.GREY_600),
                            ft.Text(hours_text, size=12, color=ft.Colors.GREY_700),
                        ], spacing=4),
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=6,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    ),
                    width=100,
                    alignment=ft.Alignment(0, 0),
                ),
                # Actions column
                ft.Container(
                    content=ft.Row([edit_btn, delete_btn], spacing=4),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=12, horizontal=10),
            bgcolor=row_bg,
        )
        
        # Add divider at bottom
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
            padding=ft.padding.all(40),
            expand=True,
        )
    
    def update_pagination(self):
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
        
        self.pagination_container.content = ft.Row([
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
                        padding=ft.padding.symmetric(horizontal=15),
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
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
            ),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.update()
    
    def prev_page(self, e=None):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_services(self.filtered_services)
    
    def next_page(self, e=None):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_services(self.filtered_services)
    
    def filter_services(self, e=None):
        """Filter services based on search query"""
        query = self.search_input.value.lower() if self.search_input.value else ""
        
        self.current_page = 1
        
        if not query:
            self.filtered_services = self.services_data.copy()
        else:
            self.filtered_services = [
                service for service in self.services_data
                if query in service.get('service_name', '').lower()
                or query in service.get('description', '').lower()
            ]
        
        self.display_services(self.filtered_services)
    
    def display_services(self, services):
        """Display services in table format"""
        self.table_rows.controls.clear()
        
        if not services:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_services = services[start_idx:end_idx]
            
            # Calculate global row number
            global_start = start_idx + 1
            
            for i, service in enumerate(page_services):
                row_number = global_start + i
                row = self._create_table_row(service, start_idx + i, row_number)
                self.table_rows.controls.append(row)
        
        self.update_pagination()
        self.page.update()
    
    async def _delayed_load(self):
        """Async delayed load"""
        await asyncio.sleep(0.2)
        self.load_data()
    
    def load_data(self):
        """Load services from API"""
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
            self.show_snackbar(f"{get_text('error')}: {e}")
        finally:
            self.is_loading = False
    
    def _safe_edit(self, service_id, event):
        """Safe wrapper for edit button"""
        try:
            self.edit_service(service_id)
        except Exception as e:
            print(f"DEBUG: Error in edit: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
    
    def _safe_delete(self, service_id, event):
        """Safe wrapper for delete button"""
        try:
            self.delete_service(service_id)
        except Exception as e:
            print(f"DEBUG: Error in delete: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}")
    
    def _open_dialog(self, dialog):
        """Centralized dialog opening method"""
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
        """Centralized dialog closing method"""
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
    
    def show_add_dialog(self, e=None):
        """Show add service dialog with modern UI"""
        print("DEBUG: show_add_dialog called")
        
        name = ft.TextField(
            label=f"{get_text('services_name')} *",
            hint_text="เช่น เปลี่ยนถ่ายน้ำมันเครื่อง",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            autofocus=True,
            prefix_icon=ft.Icons.BUILD,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        desc = ft.TextField(
            label=get_text("services_description"),
            hint_text="รายละเอียดบริการ เช่น ใช้น้ำมันเครื่อง Fully Synthetic",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.DESCRIPTION,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        price = ft.TextField(
            label=f"{get_text('services_price')} *",
            hint_text="0",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="0",
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        hours = ft.TextField(
            label=get_text("services_hours"),
            hint_text="1",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="1",
            prefix_icon=ft.Icons.SCHEDULE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        def save(e):
            if name.value and price.value:
                try:
                    self.client.add_service(
                        name.value,
                        desc.value,
                        float(price.value),
                        int(hours.value) if hours.value else 1
                    )
                    self._close_dialog()
                    self.load_data()
                    self.show_snackbar(f"✅ {get_text('add_success')}")
                except Exception as err:
                    print(f"Error saving: {err}")
                    traceback.print_exc()
                    self.show_snackbar(f"{get_text('error')}: {err}")
            else:
                self.show_snackbar(get_text("fill_all_fields"))
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.BUILD, size=28, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=14,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    get_text('services_add'),
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    "เพิ่มบริการใหม่เข้าสู่ระบบ",
                                    size=13,
                                    color="#64748B",
                                ),
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
                        name,
                        ft.Container(height=12),
                        desc,
                        ft.Container(height=12),
                        ft.Row([price, hours], spacing=12),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(24),
                width=520,
                height=450,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
                                        ft.Text(get_text("cancel"), size=14, color="#64748B"),
                                    ],
                                    spacing=6,
                                ),
                                on_click=self._close_dialog,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.GREY_400),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                                        ft.Text(get_text("save"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    ],
                                    spacing=6,
                                ),
                                on_click=save,
                                style=ft.ButtonStyle(
                                    bgcolor=self.primary_color,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=2,
                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                ),
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
        
        self._open_dialog(dialog)
    
    def edit_service(self, service_id):
        """Edit service dialog with modern UI"""
        
        # Find service from stored data
        service = None
        for s in self.services_data:
            if s.get('id') == service_id:
                service = s
                break
        
        if not service:
            self.show_snackbar(f"❌ {get_text('error')}")
            return
        
        name = ft.TextField(
            label=f"{get_text('services_name')} *",
            value=service.get('service_name', ''),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.BUILD,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        desc = ft.TextField(
            label=get_text("services_description"),
            value=service.get('description', ''),
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.DESCRIPTION,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        price = ft.TextField(
            label=f"{get_text('services_price')} *",
            value=str(service.get('price', 0)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        hours = ft.TextField(
            label=get_text("services_hours"),
            value=str(service.get('estimated_hours', 1)),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SCHEDULE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.primary_color,
        )
        
        def save_edit(e):
            try:
                if not name.value or not price.value:
                    self.show_snackbar(get_text("fill_all_fields"))
                    return
                
                self.client.update_service(service_id, {
                    'service_name': name.value,
                    'description': desc.value,
                    'price': float(price.value),
                    'estimated_hours': int(hours.value) if hours.value else 1
                })
                self._close_dialog()
                self.load_data()
                self.show_snackbar(f"✅ {get_text('edit_success')}")
            except Exception as err:
                print(f"Error in save_edit: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=28, color=ft.Colors.WHITE),
                            bgcolor=self.primary_color,
                            border_radius=14,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    get_text('services_edit'),
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    "แก้ไขข้อมูลบริการ",
                                    size=13,
                                    color="#64748B",
                                ),
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
                        name,
                        ft.Container(height=12),
                        desc,
                        ft.Container(height=12),
                        ft.Row([price, hours], spacing=12),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.all(24),
                width=520,
                height=450,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
                                        ft.Text(get_text("cancel"), size=14, color="#64748B"),
                                    ],
                                    spacing=6,
                                ),
                                on_click=self._close_dialog,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.GREY_400),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                                        ft.Text(get_text("save"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    ],
                                    spacing=6,
                                ),
                                on_click=save_edit,
                                style=ft.ButtonStyle(
                                    bgcolor=self.primary_color,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=2,
                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                ),
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
        
        self._open_dialog(dialog)
    
    def delete_service(self, service_id):
        """Delete service with confirmation dialog"""
        
        # Find service from stored data
        service = None
        for s in self.services_data:
            if s.get('id') == service_id:
                service = s
                break
        
        service_name = service.get('service_name', get_text('this_service')) if service else get_text('this_service')
        WARNING_COLOR = "#DC2626"
        
        def confirm(e):
            try:
                self.client.delete_service(service_id)
                self._close_dialog()
                self.load_data()
                self.show_snackbar(f"✅ {get_text('delete_success')}")
            except Exception as err:
                print(f"Error in delete: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, size=28, color=ft.Colors.WHITE),
                            bgcolor=WARNING_COLOR,
                            border_radius=14,
                            padding=ft.padding.all(8),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    get_text("confirm"),
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    "กรุณายืนยันการลบข้อมูล",
                                    size=13,
                                    color="#64748B",
                                ),
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
                        ft.Container(
                            content=ft.Icon(ft.Icons.DELETE_OUTLINE, size=56, color=WARNING_COLOR),
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(height=8),
                        ft.Text(
                            f"คุณต้องการลบ '{service_name}' หรือไม่?",
                            size=16,
                            weight=ft.FontWeight.W_500,
                            color="#1E293B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=4),
                        ft.Text(
                            get_text("delete_warning"),
                            size=13,
                            color="#64748B",
                            text_align=ft.TextAlign.CENTER,
                        ),
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
                            ft.TextButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CLOSE, size=18, color="#64748B"),
                                        ft.Text(get_text("cancel"), size=14, color="#64748B"),
                                    ],
                                    spacing=6,
                                ),
                                on_click=self._close_dialog,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.GREY_400),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                            ),
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.DELETE, size=18, color=ft.Colors.WHITE),
                                        ft.Text(get_text("delete"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    ],
                                    spacing=6,
                                ),
                                on_click=confirm,
                                style=ft.ButtonStyle(
                                    bgcolor=WARNING_COLOR,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=2,
                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                ),
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
        
        self._open_dialog(dialog)
    
    def show_snackbar(self, message):
        """Show snackbar message"""
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.GREY_800,
            duration=3000,
        )
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()