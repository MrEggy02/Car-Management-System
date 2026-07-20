# pages/employees/employees_page.py
import flet as ft
import asyncio
import traceback
from i18n import get_text
from .employees_widgets import (
    create_table_header, create_table_row, create_empty_state,
    create_add_dialog, create_edit_dialog, create_delete_dialog
)


class EmployeesContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.is_loading = False
        self.current_dialog = None
        self.employees_data = []
        self.filtered_employees = []
        self.search_input = None
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.current_snackbar = None  # Keep track of current snackbar
        
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.pagination_container = ft.Container()

    def build(self):
        """Build employees management content with table layout"""
        
        # Beautiful gradient header matching customer pages
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("employees_title"), 
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
        
        # Search bar with beautiful design
        self.search_input = ft.TextField(
            hint_text=f" {get_text('search_employees')}",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            on_change=self.filter_employees,
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
        
        # Table header
        table_header = create_table_header()
        
        # Table scroll container
        table_scroll_container = ft.Container(
            content=self.table_rows,
            expand=True,
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            bgcolor=ft.Colors.WHITE,
        )
        
        # Table container
        table_container = ft.Container(
            content=ft.Column([table_header, ft.Divider(height=1, color=ft.Colors.GREY_300), table_scroll_container], spacing=0),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12, bottom_left=12, bottom_right=12),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
        )
        
        self.update_pagination_controls()
        
        # Main content area
        main_content = ft.Container(
            content=ft.Column([table_container, self.pagination_container], spacing=0),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        main_container = ft.Container(
            content=main_content,
            expand=True,
        )
        
        self.page.run_task(self._delayed_load)
        
        return ft.Column([header, control_bar, main_container], expand=True, spacing=0)
    
    def update_pagination_controls(self):
        """Update pagination controls"""
        if not self.filtered_employees:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (len(self.filtered_employees) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Container(
            content=ft.Row(
                [
                    ft.Text(f"{get_text('showing')} {len(self.filtered_employees)} {get_text('of')} {len(self.employees_data)} {get_text('results')}", size=12, color="#64748B"),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_LEFT, 
                                icon_size=20, 
                                on_click=self.prev_page, 
                                disabled=prev_disabled,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
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
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                        ]),
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=20, right=20, top=16, bottom=16),
            bgcolor="#F5F7FA",
        )
    
    def display_employees(self, employees):
        """Display employees in table format"""
        self.table_rows.controls.clear()
        
        if not employees:
            self.table_rows.controls.append(create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_employees = employees[start_idx:end_idx]
            
            # Calculate global row number
            global_start = start_idx + 1
            
            for i, emp in enumerate(page_employees):
                row_number = global_start + i
                row = create_table_row(emp, start_idx + i, row_number, self.edit_employee, self.delete_employee)
                self.table_rows.controls.append(row)
        
        self.update_pagination_controls()
        self.page.update()
    
    def update_pagination(self):
        self.update_pagination_controls()
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_employees(self.filtered_employees)
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_employees(self.filtered_employees)
    
    def filter_employees(self, e=None):
        query = self.search_input.value.lower() if self.search_input.value else ""
        self.current_page = 1
        
        if not query:
            self.filtered_employees = self.employees_data.copy()
        else:
            self.filtered_employees = [
                emp for emp in self.employees_data
                if query in emp.get('name', '').lower()
                or query in emp.get('role', '').lower()
                or (emp.get('phone') and query in emp.get('phone', '').lower())
                or (emp.get('username') and query in emp.get('username', '').lower())
            ]
        
        self.display_employees(self.filtered_employees)
    
    async def _delayed_load(self):
        await asyncio.sleep(0.2)
        await asyncio.to_thread(self.load_data)
    
    def load_data(self):
        if self.is_loading:
            return
        self.is_loading = True
        
        try:
            print("DEBUG: Loading employees data...")
            self.employees_data = self.client.get_employees()
            self.filtered_employees = self.employees_data.copy()
            print(f"DEBUG: Loaded {len(self.employees_data)} employees")
            self.display_employees(self.filtered_employees)
        except Exception as e:
            print(f"DEBUG: Error loading employees: {e}")
            traceback.print_exc()
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
    
    def show_add_dialog(self, e=None):
        def on_save(name, role, phone, status, can_login, username, password):
            try:
                self.client.add_employee(name, phone, role, status, can_login, username, password)
                self._close_dialog()
                self.load_data()
                self.show_snackbar(get_text("add_success"), "success")
            except Exception as err:
                print(f"Error saving: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = create_add_dialog(on_save, self._close_dialog, self.show_snackbar)
        self._open_dialog(dialog)
    
    def edit_employee(self, emp_id):
        emp = next((e for e in self.employees_data if e.get('id') == emp_id), None)
        if not emp:
            self.show_snackbar(get_text("error"), "error")
            return
        
        def on_save(update_data):
            try:
                self.client.update_employee(emp_id, update_data)
                self._close_dialog()
                self.load_data()
                self.show_snackbar(get_text("edit_success"), "success")
            except Exception as err:
                print(f"Error in save_edit: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = create_edit_dialog(emp, on_save, self._close_dialog, self.show_snackbar)
        self._open_dialog(dialog)
    
    def delete_employee(self, emp_id):
        emp = next((e for e in self.employees_data if e.get('id') == emp_id), None)
        emp_name = emp.get('name', get_text('this_employee')) if emp else get_text('this_employee')
        
        def on_confirm(e):
            try:
                self.client.delete_employee(emp_id)
                self._close_dialog()
                self.load_data()
                self.show_snackbar(get_text("delete_success"), "success")
            except Exception as err:
                print(f"Error in delete: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = create_delete_dialog(emp_name, on_confirm, self._close_dialog)
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
                    ft.Icon(icon, color=ft.Colors.WHITE, size=18),
                    ft.Text(message, color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.W_500),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            bgcolor=bgcolor,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
            ),
        )
        
        # Create overlay container - positioned at bottom center
        snackbar = ft.Container(
            content=snack_content,
            margin=ft.Margin(left=20, right=20, top=0, bottom=20),
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