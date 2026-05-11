# pages/layout/sidebar_manager.py
import flet as ft
from i18n import get_text

class SidebarManager:
    def __init__(self, parent):
        self.parent = parent
        self.sidebar = None
        self.nav_buttons = []
        self.data_submenu_buttons = []
        self.customer_submenu_buttons = []
        self.job_order_submenu_buttons = []
        self.quotation_submenu_buttons = []
        self.repair_submenu_buttons = []
        self.invoice_submenu_buttons = []
        self.purchase_submenu_buttons = []
        self.submenu_column = None
        self.customer_submenu_column = None
        self.job_order_submenu_column = None
        self.quotation_submenu_column = None
        self.repair_submenu_column = None
        self.invoice_submenu_column = None
        self.purchase_submenu_column = None
        
    def build(self):
        """สร้าง Sidebar"""
        nav_column = ft.Column(spacing=0)
        
        # สร้างปุ่มหลัก
        self._create_main_nav_buttons(nav_column)
        
        # สร้าง Data Management Menu
        self._create_data_management_menu(nav_column)
        
        # สร้าง Customer Management Menu
        self._create_customer_management_menu(nav_column)
        
        # สร้าง Job Order Management Menu
        self._create_job_order_management_menu(nav_column)
        
        # สร้าง Quotation Management Menu
        self._create_quotation_management_menu(nav_column)
        
        # สร้าง Repair Management Menu
        self._create_repair_management_menu(nav_column)
        
        # สร้าง Invoice Management Menu
        self._create_invoice_management_menu(nav_column)
        
        # สร้าง Purchase Management Menu (Process 7)
        self._create_purchase_management_menu(nav_column)
        
        # สร้างปุ่ม Logout
        self._create_logout_button(nav_column)
        
        # อัพเดทสถานะปุ่มที่ถูกเลือก
        self._update_selected_button()
        
        # สร้าง Sidebar Container
        self.sidebar = ft.Container(
            width=self.parent.sidebar_width if self.parent.sidebar_visible else 0,
            visible=self.parent.sidebar_visible,
            bgcolor=ft.Colors.WHITE,
            content=ft.Column(
                [
                    ft.Container(height=16),
                    ft.Container(
                        content=ft.Column(
                            [nav_column],
                            spacing=0,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        expand=True,
                        padding=ft.padding.only(top=0, left=0, right=0),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            ),
        )
        
        return self.sidebar
    
    def _create_main_nav_buttons(self, nav_column):
        """สร้างปุ่มนำทางหลัก"""
        nav_items = [
            {"icon": ft.Icons.DASHBOARD_ROUNDED, "label": get_text("dashboard"), "selected_icon": ft.Icons.DASHBOARD_ROUNDED},
        ]
        
        for idx, item in enumerate(nav_items):
            btn_container, icon, label = self._create_nav_button(item, idx)
            self.nav_buttons.append({
                "container": btn_container,
                "icon": icon,
                "label": label,
                "icon_name": item["icon"],
                "selected_icon_name": item["selected_icon"],
                "index": idx
            })
            nav_column.controls.append(btn_container)
    
    def _create_data_management_menu(self, nav_column):
        """สร้างเมนู Data Management และซับเมนู (submenu ไม่มีไอคอน)"""
        data_menu_items = [
            {"label": get_text("nav_employees"), "index": 1},
            {"label": get_text("nav_suppliers"), "index": 2},
            {"label": get_text("nav_services"), "index": 3},
            {"label": get_text("nav_parts"), "index": 4},
            {"label": get_text("nav_shop"), "index": 5},
            {"label": get_text("nav_promotions"), "index": 6},
        ]
        
        data_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
        )
        
        data_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.FOLDER_OPEN, color=self.parent.unselected_color, size=22),
                    ft.Text(
                        get_text("data_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_DOWN if not self.parent.data_menu_expanded else ft.Icons.KEYBOARD_ARROW_UP,
                        color=self.parent.unselected_color,
                        size=20,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_data_menu(),
        )
        
        self.submenu_column = ft.Column(spacing=1, visible=self.parent.data_menu_expanded)
        
        for item in data_menu_items:
            sub_btn_container, sub_label = self._create_submenu_button(item)
            self.data_submenu_buttons.append({
                "container": sub_btn_container,
                "label": sub_label,
                "index": item["index"]
            })
            self.submenu_column.controls.append(sub_btn_container)
        
        data_menu_container.content = ft.Column([
            data_main_btn,
            self.submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(data_menu_container)
    
    def _create_customer_management_menu(self, nav_column):
        """สร้างเมนู Customer Management และซับเมนู (submenu ไม่มีไอคอน)"""
        customer_menu_items = [
            {"label": get_text("input_customer_data"), "index": 8},
            {"label": get_text("edit_customer_data"), "index": 10},
            {"label": get_text("customer_list"), "index": 11},
        ]
        
        customer_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
        )
        
        customer_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PEOPLE, color=self.parent.unselected_color, size=22),
                    ft.Text(
                        get_text("customer_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_DOWN if not self.parent.customer_menu_expanded else ft.Icons.KEYBOARD_ARROW_UP,
                        color=self.parent.unselected_color,
                        size=20,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_customer_menu(),
        )
        
        self.customer_submenu_column = ft.Column(spacing=1, visible=self.parent.customer_menu_expanded)
        
        for item in customer_menu_items:
            sub_btn_container, sub_label = self._create_customer_submenu_button(item)
            self.customer_submenu_buttons.append({
                "container": sub_btn_container,
                "label": sub_label,
                "index": item["index"]
            })
            self.customer_submenu_column.controls.append(sub_btn_container)
        
        customer_menu_container.content = ft.Column([
            customer_main_btn,
            self.customer_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(customer_menu_container)
    
    def _create_job_order_management_menu(self, nav_column):
        """สร้างเมนู Job Order Management และซับเมนู (submenu ไม่มีไอคอน)"""
        job_order_menu_items = [
            {"label": get_text("new_job_order"), "index": 12},
            {"label": get_text("job_order_list"), "index": 13},
        ]
        
        job_order_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
        )
        
        job_order_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.RECEIPT, color=self.parent.unselected_color, size=22),
                    ft.Text(
                        get_text("job_order_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_DOWN if not self.parent.job_order_menu_expanded else ft.Icons.KEYBOARD_ARROW_UP,
                        color=self.parent.unselected_color,
                        size=20,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_job_order_menu(),
        )
        
        self.job_order_submenu_column = ft.Column(spacing=1, visible=self.parent.job_order_menu_expanded)
        
        for item in job_order_menu_items:
            sub_btn_container, sub_label = self._create_job_order_submenu_button(item)
            self.job_order_submenu_buttons.append({
                "container": sub_btn_container,
                "label": sub_label,
                "index": item["index"]
            })
            self.job_order_submenu_column.controls.append(sub_btn_container)
        
        job_order_menu_container.content = ft.Column([
            job_order_main_btn,
            self.job_order_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(job_order_menu_container)
    
    def _create_quotation_management_menu(self, nav_column):
        """สร้างเมนู Quotation Management และซับเมนู (submenu ไม่มีไอคอน)"""
        quotation_menu_items = [
            {"label": get_text("new_quotation"), "index": 14},
            {"label": get_text("quotations"), "index": 15},
        ]
        
        quotation_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
        )
        
        quotation_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.REQUEST_QUOTE, color=self.parent.unselected_color, size=22),
                    ft.Text(
                        get_text("quotation_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_DOWN if not self.parent.quotation_menu_expanded else ft.Icons.KEYBOARD_ARROW_UP,
                        color=self.parent.unselected_color,
                        size=20,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_quotation_menu(),
        )
        
        self.quotation_submenu_column = ft.Column(spacing=1, visible=self.parent.quotation_menu_expanded)
        
        for item in quotation_menu_items:
            sub_btn_container, sub_label = self._create_quotation_submenu_button(item)
            self.quotation_submenu_buttons.append({
                "container": sub_btn_container,
                "label": sub_label,
                "index": item["index"]
            })
            self.quotation_submenu_column.controls.append(sub_btn_container)
        
        quotation_menu_container.content = ft.Column([
            quotation_main_btn,
            self.quotation_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(quotation_menu_container)
    
    def _create_repair_management_menu(self, nav_column):
        """สร้างเมนู Repair Management และซับเมนู (submenu ไม่มีไอคอน)"""
        repair_menu_items = [
            {"label": get_text("new_repair"), "index": 16},
            {"label": get_text("repair_list"), "index": 17},
        ]
        
        repair_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
        )
        
        repair_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CONSTRUCTION, color=self.parent.unselected_color, size=22),
                    ft.Text(
                        get_text("repair_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_DOWN if not self.parent.repair_menu_expanded else ft.Icons.KEYBOARD_ARROW_UP,
                        color=self.parent.unselected_color,
                        size=20,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_repair_menu(),
        )
        
        self.repair_submenu_column = ft.Column(spacing=1, visible=self.parent.repair_menu_expanded)
        
        for item in repair_menu_items:
            sub_btn_container, sub_label = self._create_repair_submenu_button(item)
            self.repair_submenu_buttons.append({
                "container": sub_btn_container,
                "label": sub_label,
                "index": item["index"]
            })
            self.repair_submenu_column.controls.append(sub_btn_container)
        
        repair_menu_container.content = ft.Column([
            repair_main_btn,
            self.repair_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(repair_menu_container)
    
    def _create_invoice_management_menu(self, nav_column):
        """สร้างเมนู Invoice Management (Process 6) - submenu ไม่มีไอคอน"""
        invoice_menu_items = [
            {"label": get_text("new_invoice"), "index": 19},
            {"label": get_text("invoice_list"), "index": 20},
        ]
        
        invoice_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
        )
        
        invoice_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.RECEIPT, color=self.parent.unselected_color, size=22),
                    ft.Text(
                        get_text("invoice_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_DOWN if not self.parent.invoice_menu_expanded else ft.Icons.KEYBOARD_ARROW_UP,
                        color=self.parent.unselected_color,
                        size=20,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_invoice_menu(),
        )
        
        self.invoice_submenu_column = ft.Column(spacing=1, visible=self.parent.invoice_menu_expanded)
        
        for item in invoice_menu_items:
            sub_btn_container, sub_label = self._create_invoice_submenu_button(item)
            self.invoice_submenu_buttons.append({
                "container": sub_btn_container,
                "label": sub_label,
                "index": item["index"]
            })
            self.invoice_submenu_column.controls.append(sub_btn_container)
        
        invoice_menu_container.content = ft.Column([
            invoice_main_btn,
            self.invoice_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(invoice_menu_container)
    
    def _create_purchase_management_menu(self, nav_column):
        """สร้างเมนู Purchase Management (Process 7) - submenu ไม่มีไอคอน"""
        purchase_menu_items = [
            {"label": get_text("create_purchase_order"), "index": 22},
            {"label": get_text("purchase_order_list"), "index": 23},
            {"label": get_text("stock_movement"), "index": 26},
        ]
        
        purchase_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
        )
        
        purchase_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LOCAL_SHIPPING, color=self.parent.unselected_color, size=22),
                    ft.Text(
                        get_text("purchase_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_DOWN if not self.parent.purchase_menu_expanded else ft.Icons.KEYBOARD_ARROW_UP,
                        color=self.parent.unselected_color,
                        size=20,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_purchase_menu(),
        )
        
        self.purchase_submenu_column = ft.Column(spacing=1, visible=self.parent.purchase_menu_expanded)
        
        for item in purchase_menu_items:
            sub_btn_container, sub_label = self._create_purchase_submenu_button(item)
            self.purchase_submenu_buttons.append({
                "container": sub_btn_container,
                "label": sub_label,
                "index": item["index"]
            })
            self.purchase_submenu_column.controls.append(sub_btn_container)
        
        purchase_menu_container.content = ft.Column([
            purchase_main_btn,
            self.purchase_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(purchase_menu_container)
    
    def _create_logout_button(self, nav_column):
        """สร้างปุ่ม Logout"""
        logout_item = {"icon": ft.Icons.LOGOUT, "label": get_text("logout"), "selected_icon": ft.Icons.LOGOUT}
        logout_btn_container, logout_icon, logout_label = self._create_nav_button(logout_item, 7)
        self.nav_buttons.append({
            "container": logout_btn_container,
            "icon": logout_icon,
            "label": logout_label,
            "icon_name": logout_item["icon"],
            "selected_icon_name": logout_item["selected_icon"],
            "index": 7
        })
        nav_column.controls.append(logout_btn_container)
    
    def _create_nav_button(self, item, idx):
        """สร้างปุ่มนำทางหลัก (มีไอคอน)"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            data=idx,
            on_click=lambda e, i=idx: self.parent.on_nav_click(i),
            on_hover=lambda e, i=idx: self.parent.on_nav_hover(e, i),
        )
        
        icon = ft.Icon(item["icon"], color=self.parent.unselected_color, size=22)
        label = ft.Text(item["label"], size=14, weight=ft.FontWeight.W_500, color=self.parent.unselected_color)
        row = ft.Row([icon, label], spacing=16, alignment=ft.MainAxisAlignment.START)
        btn_container.content = row
        
        if idx == 0:
            icon.color = self.parent.selected_color
            label.color = self.parent.selected_color
            btn_container.bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
            btn_container.border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
        
        return btn_container, icon, label
    
    def _create_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Data Management (ไม่มีไอคอน)"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=1),
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_submenu_hover(e, i),
        )
        
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        # ไม่มีไอคอน เหลือแค่ข้อความ (มีช่องว่างเล็กน้อยเพื่อจัดตำแหน่ง)
        row = ft.Row(
            [
                ft.Container(width=8),
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, label
    
    def _create_customer_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Customer Management (ไม่มีไอคอน)"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=1),
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_customer_submenu_hover(e, i),
        )
        
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, label
    
    def _create_job_order_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Job Order Management (ไม่มีไอคอน)"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=1),
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_job_order_submenu_hover(e, i),
        )
        
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, label
    
    def _create_quotation_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Quotation Management (ไม่มีไอคอน)"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=1),
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_quotation_submenu_hover(e, i),
        )
        
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, label
    
    def _create_repair_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Repair Management (ไม่มีไอคอน)"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=1),
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_repair_submenu_hover(e, i),
        )
        
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, label
    
    def _create_invoice_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Invoice Management (ไม่มีไอคอน)"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=1),
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_invoice_submenu_hover(e, i),
        )
        
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, label
    
    def _create_purchase_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Purchase Management (ไม่มีไอคอน)"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=1),
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_purchase_submenu_hover(e, i),
        )
        
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, label
    
    def _update_selected_button(self):
        """อัพเดทสถานะปุ่มที่ถูกเลือก"""
        # Reset all main buttons
        for btn_data in self.nav_buttons:
            btn_data["icon"].color = self.parent.unselected_color
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        # Reset submenu buttons (ไม่มีไอคอน)
        for btn_data in self.data_submenu_buttons:
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        for btn_data in self.customer_submenu_buttons:
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        for btn_data in self.job_order_submenu_buttons:
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        for btn_data in self.quotation_submenu_buttons:
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        for btn_data in self.repair_submenu_buttons:
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        for btn_data in self.invoice_submenu_buttons:
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        for btn_data in self.purchase_submenu_buttons:
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        # Select button based on current_index
        selected_btn = next((btn for btn in self.data_submenu_buttons if btn["index"] == self.parent.current_index), None)
        if selected_btn:
            selected_btn["label"].color = self.parent.selected_color
            selected_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
            selected_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
        else:
            selected_customer_btn = next((btn for btn in self.customer_submenu_buttons if btn["index"] == self.parent.current_index), None)
            if selected_customer_btn:
                selected_customer_btn["label"].color = self.parent.selected_color
                selected_customer_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                selected_customer_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
            else:
                selected_job_btn = next((btn for btn in self.job_order_submenu_buttons if btn["index"] == self.parent.current_index), None)
                if selected_job_btn:
                    selected_job_btn["label"].color = self.parent.selected_color
                    selected_job_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                    selected_job_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                else:
                    selected_quotation_btn = next((btn for btn in self.quotation_submenu_buttons if btn["index"] == self.parent.current_index), None)
                    if selected_quotation_btn:
                        selected_quotation_btn["label"].color = self.parent.selected_color
                        selected_quotation_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                        selected_quotation_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                    else:
                        selected_repair_btn = next((btn for btn in self.repair_submenu_buttons if btn["index"] == self.parent.current_index), None)
                        if selected_repair_btn:
                            selected_repair_btn["label"].color = self.parent.selected_color
                            selected_repair_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                            selected_repair_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                        else:
                            selected_invoice_btn = next((btn for btn in self.invoice_submenu_buttons if btn["index"] == self.parent.current_index), None)
                            if selected_invoice_btn:
                                selected_invoice_btn["label"].color = self.parent.selected_color
                                selected_invoice_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                                selected_invoice_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                            else:
                                selected_purchase_btn = next((btn for btn in self.purchase_submenu_buttons if btn["index"] == self.parent.current_index), None)
                                if selected_purchase_btn:
                                    selected_purchase_btn["label"].color = self.parent.selected_color
                                    selected_purchase_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                                    selected_purchase_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                                else:
                                    main_btn = self.nav_buttons[self.parent.current_index] if self.parent.current_index < len(self.nav_buttons) else None
                                    if main_btn:
                                        main_btn["icon"].color = self.parent.selected_color
                                        main_btn["label"].color = self.parent.selected_color
                                        main_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                                        main_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                                        if main_btn["selected_icon_name"] != main_btn["icon_name"]:
                                            main_btn["icon"].name = main_btn["selected_icon_name"]
    
    def update_arrow_icons(self):
        """อัพเดทไอคอนลูกศรของเมนู"""
        if self.sidebar and len(self.sidebar.content.controls) > 0:
            nav_column = self.sidebar.content.controls[1].content.controls[0]
            menu_index = 0
            for control in nav_column.controls:
                if isinstance(control, ft.Container):
                    content = control.content
                    if isinstance(content, ft.Column) and len(content.controls) > 0:
                        main_btn = content.controls[0]
                        if isinstance(main_btn, ft.Container) and isinstance(main_btn.content, ft.Row):
                            if len(main_btn.content.controls) > 2:
                                arrow_icon = main_btn.content.controls[2]
                                if isinstance(arrow_icon, ft.Icon):
                                    if menu_index == 1:
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.data_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 2:
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.customer_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 3:
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.job_order_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 4:
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.quotation_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 5:
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.repair_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 6:
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.invoice_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 7:
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.purchase_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                    menu_index += 1