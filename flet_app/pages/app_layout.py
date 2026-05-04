# app_layout.py (Complete with Repair Management)
import flet as ft
from flet import Alignment
import sys
import os

# Add parent directory to path so imports work correctly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
FLET_APP_DIR = os.path.dirname(PARENT_DIR)

for path in [CURRENT_DIR, PARENT_DIR, FLET_APP_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from Management.employees.employees_page import EmployeesContent
from api_client import APIClient
from i18n import get_text, set_language, get_current_language, LANGUAGES
from pages.layout import SidebarManager, TopNavBarManager, ContentManager


class AppLayout:
    def __init__(self, page: ft.Page, client: APIClient, user: dict):
        self.page = page
        self.client = client
        self.user = user
        self.current_view = None
        self.current_index = 0
        self.data_menu_expanded = False
        self.customer_menu_expanded = False
        self.job_order_menu_expanded = False
        self.quotation_menu_expanded = False
        self.repair_menu_expanded = False
        self.current_dialog = None
        self.sidebar_visible = True
        self.sidebar_width = 280

        # Color scheme
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.selected_color = "#1565C0"
        self.unselected_color = "#666666"
        self.hover_color = "#E3F2FD"

        # Initialize managers
        self.sidebar_manager = SidebarManager(self)
        self.top_nav_bar_manager = TopNavBarManager(self)
        self.content_manager = ContentManager(self)

        # References
        self.sidebar = None
        self.main_row = None
        self.top_nav_bar = None

    def build(self):
        print("DEBUG: AppLayout.build() called")

        # Build components
        self.sidebar = self.sidebar_manager.build()
        self.top_nav_bar = self.top_nav_bar_manager.build()
        self.current_view = self.content_manager.build()

        # Create main layout
        self.main_row = ft.Row(
            [self.sidebar, self.current_view],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        # Final layout
        final_layout = ft.Column(
            [
                self.top_nav_bar,
                self.main_row,
            ],
            expand=True,
            spacing=0,
        )

        self.page.controls.clear()
        self.page.add(final_layout)
        self.page.bgcolor = "#F5F7FA"
        self.page.update()
        print("DEBUG: Layout added to page")

    def _rebuild_all(self):
        """Rebuild entire UI when language changes"""
        # Save current state
        current_index = self.current_index
        data_menu_expanded = self.data_menu_expanded
        customer_menu_expanded = self.customer_menu_expanded
        job_order_menu_expanded = self.job_order_menu_expanded
        quotation_menu_expanded = self.quotation_menu_expanded
        repair_menu_expanded = self.repair_menu_expanded

        # Clear page
        self.page.controls.clear()

        # Reset state
        self.current_index = current_index
        self.data_menu_expanded = data_menu_expanded
        self.customer_menu_expanded = customer_menu_expanded
        self.job_order_menu_expanded = job_order_menu_expanded
        self.quotation_menu_expanded = quotation_menu_expanded
        self.repair_menu_expanded = repair_menu_expanded

        # Rebuild everything
        self.sidebar = self.sidebar_manager.build()
        self.top_nav_bar = self.top_nav_bar_manager.build()
        self.current_view = self.content_manager.build()

        # Rebuild main layout
        self.main_row = ft.Row(
            [self.sidebar, self.current_view],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        final_layout = ft.Column(
            [
                self.top_nav_bar,
                self.main_row,
            ],
            expand=True,
            spacing=0,
        )

        self.page.add(final_layout)
        self.page.bgcolor = "#F5F7FA"

        # Navigate to saved index
        if current_index != 0:
            self.on_nav_click(current_index)

        self.page.update()

    def toggle_sidebar(self, e=None):
        """Toggle sidebar visibility"""
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar:
            if self.sidebar_visible:
                self.sidebar.width = self.sidebar_width
                self.sidebar.visible = True
            else:
                self.sidebar.width = 0
                self.sidebar.visible = False
            self.page.update()

    def toggle_data_menu(self):
        """Toggle data management submenu visibility"""
        self.data_menu_expanded = not self.data_menu_expanded
        if self.sidebar_manager.submenu_column:
            self.sidebar_manager.submenu_column.visible = self.data_menu_expanded
            self.sidebar_manager.update_arrow_icons()
        self.page.update()

    def toggle_customer_menu(self):
        """Toggle customer management submenu visibility"""
        self.customer_menu_expanded = not self.customer_menu_expanded
        if self.sidebar_manager.customer_submenu_column:
            self.sidebar_manager.customer_submenu_column.visible = self.customer_menu_expanded
            self.sidebar_manager.update_arrow_icons()
        self.page.update()

    def toggle_job_order_menu(self):
        """Toggle job order management submenu visibility"""
        self.job_order_menu_expanded = not self.job_order_menu_expanded
        if self.sidebar_manager.job_order_submenu_column:
            self.sidebar_manager.job_order_submenu_column.visible = self.job_order_menu_expanded
            self.sidebar_manager.update_arrow_icons()
        self.page.update()

    def toggle_quotation_menu(self):
        """Toggle quotation management submenu visibility"""
        self.quotation_menu_expanded = not self.quotation_menu_expanded
        if hasattr(self.sidebar_manager, 'quotation_submenu_column') and self.sidebar_manager.quotation_submenu_column:
            self.sidebar_manager.quotation_submenu_column.visible = self.quotation_menu_expanded
            self.sidebar_manager.update_arrow_icons()
        self.page.update()

    def toggle_repair_menu(self):
        """Toggle repair management submenu visibility"""
        self.repair_menu_expanded = not self.repair_menu_expanded
        if hasattr(self.sidebar_manager, 'repair_submenu_column') and self.sidebar_manager.repair_submenu_column:
            self.sidebar_manager.repair_submenu_column.visible = self.repair_menu_expanded
            self.sidebar_manager.update_arrow_icons()
        self.page.update()

    def on_submenu_hover(self, e, index):
        """Handle hover effects for data submenu"""
        btn_data = next(
            (
                btn
                for btn in self.sidebar_manager.data_submenu_buttons
                if btn["index"] == index
            ),
            None,
        )
        if btn_data:
            if e.data == "true":
                if index != self.current_index:
                    btn_data["container"].bgcolor = self.hover_color
            else:
                if index != self.current_index:
                    btn_data["container"].bgcolor = None
            self.page.update()

    def on_customer_submenu_hover(self, e, index):
        """Handle hover effects for customer submenu"""
        btn_data = next(
            (
                btn
                for btn in self.sidebar_manager.customer_submenu_buttons
                if btn["index"] == index
            ),
            None,
        )
        if btn_data:
            if e.data == "true":
                if index != self.current_index:
                    btn_data["container"].bgcolor = self.hover_color
            else:
                if index != self.current_index:
                    btn_data["container"].bgcolor = None
            self.page.update()

    def on_job_order_submenu_hover(self, e, index):
        """Handle hover effects for job order submenu"""
        if hasattr(self.sidebar_manager, 'job_order_submenu_buttons'):
            btn_data = next(
                (
                    btn
                    for btn in self.sidebar_manager.job_order_submenu_buttons
                    if btn["index"] == index
                ),
                None,
            )
            if btn_data:
                if e.data == "true":
                    if index != self.current_index:
                        btn_data["container"].bgcolor = self.hover_color
                else:
                    if index != self.current_index:
                        btn_data["container"].bgcolor = None
                self.page.update()

    def on_quotation_submenu_hover(self, e, index):
        """Handle hover effects for quotation submenu"""
        if hasattr(self.sidebar_manager, 'quotation_submenu_buttons'):
            btn_data = next(
                (
                    btn
                    for btn in self.sidebar_manager.quotation_submenu_buttons
                    if btn["index"] == index
                ),
                None,
            )
            if btn_data:
                if e.data == "true":
                    if index != self.current_index:
                        btn_data["container"].bgcolor = self.hover_color
                else:
                    if index != self.current_index:
                        btn_data["container"].bgcolor = None
                self.page.update()

    def on_repair_submenu_hover(self, e, index):
        """Handle hover effects for repair submenu"""
        if hasattr(self.sidebar_manager, 'repair_submenu_buttons'):
            btn_data = next(
                (
                    btn
                    for btn in self.sidebar_manager.repair_submenu_buttons
                    if btn["index"] == index
                ),
                None,
            )
            if btn_data:
                if e.data == "true":
                    if index != self.current_index:
                        btn_data["container"].bgcolor = self.hover_color
                else:
                    if index != self.current_index:
                        btn_data["container"].bgcolor = None
                self.page.update()

    def on_nav_hover(self, e, index):
        """Handle hover effects for main nav"""
        btn_data = (
            self.sidebar_manager.nav_buttons[index]
            if index < len(self.sidebar_manager.nav_buttons)
            else None
        )
        if btn_data:
            if e.data == "true":
                if index != self.current_index:
                    btn_data["container"].bgcolor = self.hover_color
            else:
                if index != self.current_index:
                    btn_data["container"].bgcolor = None
            self.page.update()

    def on_nav_click(self, index):
        """Handle navigation click"""
        print(f"DEBUG: Nav clicked index {index}")

        if index == 7:
            self.logout()
            return

        # Auto-expand menus if needed
        if index in range(1, 7) and not self.data_menu_expanded:
            self.data_menu_expanded = True
            if self.sidebar_manager.submenu_column:
                self.sidebar_manager.submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(8, 12) and not self.customer_menu_expanded:
            self.customer_menu_expanded = True
            if self.sidebar_manager.customer_submenu_column:
                self.sidebar_manager.customer_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(12, 14) and not self.job_order_menu_expanded:
            self.job_order_menu_expanded = True
            if self.sidebar_manager.job_order_submenu_column:
                self.sidebar_manager.job_order_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(14, 16) and not self.quotation_menu_expanded:
            self.quotation_menu_expanded = True
            if hasattr(self.sidebar_manager, 'quotation_submenu_column') and self.sidebar_manager.quotation_submenu_column:
                self.sidebar_manager.quotation_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(16, 18) and not self.repair_menu_expanded:
            self.repair_menu_expanded = True
            if hasattr(self.sidebar_manager, 'repair_submenu_column') and self.sidebar_manager.repair_submenu_column:
                self.sidebar_manager.repair_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        self.current_index = index

        # Update sidebar button states
        self.sidebar_manager._update_selected_button()

        # Switch content
        self.content_manager.switch_content(index)

    def navigate_to(self, page_name: str, customer_id: int = None, order_id: int = None, quotation_id: int = None, job_order_id: int = None, repair_id: int = None):
        """Navigate to a specific page by name with optional parameters"""
        page_index_map = {
            "dashboard": 0,
            "employees": 1,
            "suppliers": 2,
            "services": 3,
            "parts": 4,
            "shop": 5,
            "promotions": 6,
            "input_customer": 8,
            "edit_customer": 10,
            "customer_list": 11,
            "job_order_create": 12,
            "job_order_list": 13,
            "quotation_create": 14,
            "quotation_list": 15,
            "repair_create": 16,
            "repair_list": 17,
        }

        # Store IDs for pages
        if page_name == "edit_customer" and customer_id:
            self._edit_customer_id = customer_id

        if page_name == "job_order_print" and order_id:
            self._job_order_id = order_id
        
        if page_name == "quotation_create" and job_order_id:
            self._job_order_id = job_order_id
        
        if page_name == "quotation_view" and quotation_id:
            self._quotation_id = quotation_id
        
        if page_name == "quotation_print" and quotation_id:
            self._quotation_id = quotation_id
        
        if page_name == "repair_create" and job_order_id:
            self._job_order_id = job_order_id
        
        if page_name == "repair_detail" and repair_id:
            self._repair_id = repair_id

        if page_name in page_index_map:
            self.on_nav_click(page_index_map[page_name])
        else:
            self.current_view.content = self.content_manager._get_placeholder(page_name)
            self.page.update()

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
            print("DEBUG: Dialog opened successfully")
        except Exception as e:
            import traceback

            print(f"DEBUG: Error opening dialog: {e}")
            traceback.print_exc()

    def _close_dialog(self, e=None):
        try:
            if self.current_dialog:
                self.current_dialog.open = False
                self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")

    def logout(self):
        print("DEBUG: Logging out")

        def confirm_logout(e):
            print("DEBUG: Logout confirmed")
            self._close_dialog()
            from pages.login_page import login_page

            def on_login_success(p, c, u):
                from pages.dashboard_page import dashboard_page

                dashboard_page(p, c, u)

            login_page(self.page, on_login_success)

        def cancel_logout(e):
            print("DEBUG: Logout cancelled")
            self._close_dialog()
            self.on_nav_click(self.current_index)

        dialog = ft.AlertDialog(
            title=ft.Text(get_text("confirm_logout")),
            content=ft.Text(get_text("logout_confirm_message")),
            actions=[
                ft.TextButton(get_text("cancel"), on_click=cancel_logout),
                ft.TextButton(
                    get_text("logout"),
                    on_click=confirm_logout,
                    style=ft.ButtonStyle(color=ft.Colors.RED),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._open_dialog(dialog)