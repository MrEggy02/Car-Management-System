# app_layout.py (Complete with Repair Management, Personal Page, Reports)
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
from Management.parts.stock_history_page import StockHistoryPage
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
        self.invoice_menu_expanded = False
        self.purchase_menu_expanded = False
        self.reports_menu_expanded = False
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
        invoice_menu_expanded = self.invoice_menu_expanded
        purchase_menu_expanded = self.purchase_menu_expanded
        reports_menu_expanded = self.reports_menu_expanded

        # Clear page
        self.page.controls.clear()

        # Reset state
        self.current_index = current_index
        self.data_menu_expanded = data_menu_expanded
        self.customer_menu_expanded = customer_menu_expanded
        self.job_order_menu_expanded = job_order_menu_expanded
        self.quotation_menu_expanded = quotation_menu_expanded
        self.repair_menu_expanded = repair_menu_expanded
        self.invoice_menu_expanded = invoice_menu_expanded
        self.purchase_menu_expanded = purchase_menu_expanded
        self.reports_menu_expanded = reports_menu_expanded

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

    def toggle_invoice_menu(self):
        """Toggle invoice management submenu visibility"""
        self.invoice_menu_expanded = not self.invoice_menu_expanded
        if hasattr(self.sidebar_manager, 'invoice_submenu_column') and self.sidebar_manager.invoice_submenu_column:
            self.sidebar_manager.invoice_submenu_column.visible = self.invoice_menu_expanded
            self.sidebar_manager.update_arrow_icons()
        self.page.update()

    def toggle_purchase_menu(self):
        """Toggle purchase management submenu visibility"""
        self.purchase_menu_expanded = not self.purchase_menu_expanded
        if hasattr(self.sidebar_manager, 'purchase_submenu_column') and self.sidebar_manager.purchase_submenu_column:
            self.sidebar_manager.purchase_submenu_column.visible = self.purchase_menu_expanded
            self.sidebar_manager.update_arrow_icons()
        self.page.update()

    def toggle_reports_menu(self):
        """Toggle reports management submenu visibility"""
        self.reports_menu_expanded = not self.reports_menu_expanded
        if hasattr(self.sidebar_manager, 'reports_submenu_column') and self.sidebar_manager.reports_submenu_column:
            self.sidebar_manager.reports_submenu_column.visible = self.reports_menu_expanded
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

    def on_invoice_submenu_hover(self, e, index):
        """Handle hover effects for invoice submenu"""
        if hasattr(self.sidebar_manager, 'invoice_submenu_buttons'):
            btn_data = next(
                (
                    btn
                    for btn in self.sidebar_manager.invoice_submenu_buttons
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

    def on_purchase_submenu_hover(self, e, index):
        """Handle hover effects for purchase submenu"""
        if hasattr(self.sidebar_manager, 'purchase_submenu_buttons'):
            btn_data = next(
                (
                    btn
                    for btn in self.sidebar_manager.purchase_submenu_buttons
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

    def on_reports_submenu_hover(self, e, index):
        """Handle hover effects for reports submenu"""
        if hasattr(self.sidebar_manager, 'reports_submenu_buttons'):
            btn_data = next(
                (
                    btn
                    for btn in self.sidebar_manager.reports_submenu_buttons
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

        # Auto-expand menus if needed
        # For Data Management (indices 1-9)
        if index in range(1, 10) and not self.data_menu_expanded:
            self.data_menu_expanded = True
            if self.sidebar_manager.submenu_column:
                self.sidebar_manager.submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(11, 12) and not self.customer_menu_expanded:
            self.customer_menu_expanded = True
            if self.sidebar_manager.customer_submenu_column:
                self.sidebar_manager.customer_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(13, 14) and not self.job_order_menu_expanded:
            self.job_order_menu_expanded = True
            if self.sidebar_manager.job_order_submenu_column:
                self.sidebar_manager.job_order_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(15, 16) and not self.quotation_menu_expanded:
            self.quotation_menu_expanded = True
            if hasattr(self.sidebar_manager, 'quotation_submenu_column') and self.sidebar_manager.quotation_submenu_column:
                self.sidebar_manager.quotation_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(16, 19) and not self.repair_menu_expanded:
            self.repair_menu_expanded = True
            if hasattr(self.sidebar_manager, 'repair_submenu_column') and self.sidebar_manager.repair_submenu_column:
                self.sidebar_manager.repair_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in [20, 38] and not self.invoice_menu_expanded:
            self.invoice_menu_expanded = True
            if hasattr(self.sidebar_manager, 'invoice_submenu_column') and self.sidebar_manager.invoice_submenu_column:
                self.sidebar_manager.invoice_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(22, 27) and not self.purchase_menu_expanded:
            self.purchase_menu_expanded = True
            if hasattr(self.sidebar_manager, 'purchase_submenu_column') and self.sidebar_manager.purchase_submenu_column:
                self.sidebar_manager.purchase_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        if index in range(29, 34) and not self.reports_menu_expanded:
            self.reports_menu_expanded = True
            if hasattr(self.sidebar_manager, 'reports_submenu_column') and self.sidebar_manager.reports_submenu_column:
                self.sidebar_manager.reports_submenu_column.visible = True
                self.sidebar_manager.update_arrow_icons()
                self.page.update()

        self.current_index = index

        # Update sidebar button states
        self.sidebar_manager._update_selected_button()

        # Switch content
        self.content_manager.switch_content(index)

    def navigate_to(self, page_name: str, customer_id: int = None, order_id: int = None, 
                    quotation_id: int = None, job_order_id: int = None, repair_id: int = None,
                    po_id: int = None, promotion_id: int = None, promotion_name: str = None, 
                    part_id: int = None, invoice_id: int = None, read_only: bool = False):
        """Navigate to a specific page by name with optional parameters"""
        page_index_map = {
            "dashboard": 0,
            "employees": 1,
            "suppliers": 2,
            "services": 3,
            "parts": 4,
            "shop": 5,
            "promotions": 6,
            "brands": 7,
            "units": 8,
            "part_categories": 9,
            "input_customer": 10,
            "edit_customer": 11,
            "customer_list": 11,
            "job_order_create": 12,
            "job_order_list": 13,
            "quotation_create": 14,
            "quotation_list": 15,
            "repair_create": 16,
            "repair_list": 17,
            "repair_detail": 18,
            "invoice_create": 19,
            "invoice_list": 20,
            "invoice_detail": 21,
            "purchase_order_create": 22,
            "purchase_order_list": 35,
            "purchase_order_detail": 24,
            "purchase_order_receive": 25,
            "stock_movement": 26,
            "promotion_items": 27,
            "personal_page": 28,
            # Reports (Process 8)
            "revenue_report": 29,
            "repair_summary_report": 30,
            "parts_service_sales_report": 31,
            "mechanic_performance_report": 32,
            "promotion_usage_report": 33,
            "goods_receipt_list": 34,
            "purchase_management": 35,
            "receiving_management": 36,
            "receiving_po_list": 37,
            "delivery_note_list": 38,
            "stock_history": 39,
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
            self._read_only = read_only
        
        if page_name == "invoice_create" and job_order_id:
            self._job_order_id = job_order_id
        
        if page_name == "invoice_detail" and invoice_id:
            self._invoice_id = invoice_id
        
        if page_name == "purchase_order_detail" and po_id:
            self._po_id = po_id
        
        if page_name == "purchase_order_receive" and po_id:
            self._po_id = po_id
        
        if page_name == "promotion_items":
            self._promotion_id = promotion_id
            self._promotion_name = promotion_name
            
        if page_name == "purchase_order_create" and part_id:
           self._part_id = part_id

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
        """Show modern logout confirmation dialog"""
        print("DEBUG: Showing logout confirmation dialog")

        def confirm_logout(e):
            print("DEBUG: Logout confirmed")
            # Close the dialog
            if logout_dialog in self.page.overlay:
                self.page.overlay.remove(logout_dialog)
            self._close_dialog()
            
            # Navigate to login page
            from pages.login_page import login_page

            def on_login_success(p, c, u):
                from pages.dashboard_page import dashboard_page
                dashboard_page(p, c, u)

            login_page(self.page, on_login_success)

        def cancel_logout(e):
            print("DEBUG: Logout cancelled")
            # Close the dialog
            if logout_dialog in self.page.overlay:
                self.page.overlay.remove(logout_dialog)
            self._close_dialog()
            # Return to current page
            self.on_nav_click(self.current_index)

        # Create modern logout dialog
        logout_dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=20),
            bgcolor=ft.Colors.WHITE,
            content=ft.Container(
                content=ft.Column(
                    [
                        # Warning icon
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.LOGOUT_ROUNDED,
                                size=56,
                                color="#EF4444",
                            ),
                            bgcolor=ft.Colors.with_opacity(0.1, "#EF4444"),
                            border_radius=50,
                            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                        ),
                        ft.Container(height=16),
                        # Title
                        ft.Text(
                            get_text("confirm_logout"),
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color="#1E293B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=8),
                        # Message
                        ft.Text(
                            get_text("logout_confirm_message"),
                            size=14,
                            color="#64748B",
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                width=380,
                padding=ft.Padding(left=28, right=28, top=28, bottom=28),
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(
                                content=ft.Text(
                                    get_text("cancel"),
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                ),
                                on_click=cancel_logout,
                                style=ft.ButtonStyle(
                                    color="#64748B",
                                    overlay_color=ft.Colors.with_opacity(0.1, "#64748B"),
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                ),
                                expand=True,
                            ),
                            ft.ElevatedButton(
                                content=ft.Text(
                                    get_text("logout"),
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.Colors.WHITE,
                                ),
                                on_click=confirm_logout,
                                style=ft.ButtonStyle(
                                    bgcolor="#EF4444",
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=0,
                                    padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                                ),
                                expand=True,
                            ),
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(left=20, right=20, top=16, bottom=16),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        # Open the dialog
        self.page.overlay.append(logout_dialog)
        logout_dialog.open = True
        self.page.update()