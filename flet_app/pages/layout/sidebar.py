# pages/layout.py - SidebarManager (Complete with Repair Management)
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
        self.submenu_column = None
        self.customer_submenu_column = None
        self.job_order_submenu_column = None
        self.quotation_submenu_column = None
        self.repair_submenu_column = None
        
    def build(self):
        """สร้าง Sidebar"""
        nav_column = ft.Column(spacing=0)  # Reduced spacing between main items
        
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
                    ft.Container(height=16),  # Reduced from 20
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
        """สร้างเมนู Data Management และซับเมนู"""
        data_menu_items = [
            {"icon": ft.Icons.PEOPLE_OUTLINE, "label": get_text("nav_employees"), "selected_icon": ft.Icons.PEOPLE, "index": 1},
            {"icon": ft.Icons.LOCAL_SHIPPING, "label": get_text("nav_suppliers"), "selected_icon": ft.Icons.LOCAL_SHIPPING, "index": 2},
            {"icon": ft.Icons.BUILD, "label": get_text("nav_services"), "selected_icon": ft.Icons.BUILD, "index": 3},
            {"icon": ft.Icons.PRECISION_MANUFACTURING, "label": get_text("nav_parts"), "selected_icon": ft.Icons.PRECISION_MANUFACTURING, "index": 4},
            {"icon": ft.Icons.STORE, "label": get_text("nav_shop"), "selected_icon": ft.Icons.STORE, "index": 5},
            {"icon": ft.Icons.LOCAL_OFFER, "label": get_text("nav_promotions"), "selected_icon": ft.Icons.LOCAL_OFFER, "index": 6},
        ]
        
        data_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),  # Reduced from 4
            margin=ft.margin.symmetric(horizontal=0, vertical=0),  # Reduced from 4
        )
        
        # ปุ่มหลัก Data Management
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
            padding=ft.padding.symmetric(vertical=10, horizontal=16),  # Reduced vertical from 12 to 10
            margin=ft.margin.symmetric(horizontal=12, vertical=2),  # Reduced from 4
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_data_menu(),
        )
        
        # ซับเมนู
        self.submenu_column = ft.Column(spacing=1, visible=self.parent.data_menu_expanded)  # Reduced from 2
        
        for item in data_menu_items:
            sub_btn_container, sub_icon, sub_label = self._create_submenu_button(item)
            self.data_submenu_buttons.append({
                "container": sub_btn_container,
                "icon": sub_icon,
                "label": sub_label,
                "icon_name": item["icon"],
                "selected_icon_name": item["selected_icon"],
                "index": item["index"]
            })
            self.submenu_column.controls.append(sub_btn_container)
        
        data_menu_container.content = ft.Column([
            data_main_btn,
            self.submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(data_menu_container)
    
    def _create_customer_management_menu(self, nav_column):
        """สร้างเมนู Customer Management และซับเมนู"""
        customer_menu_items = [
            {"icon": ft.Icons.INPUT, "label": get_text("input_customer_data"), "selected_icon": ft.Icons.INPUT, "index": 8},
            {"icon": ft.Icons.EDIT, "label": get_text("edit_customer_data"), "selected_icon": ft.Icons.EDIT, "index": 10},
            {"icon": ft.Icons.LIST, "label": get_text("customer_list"), "selected_icon": ft.Icons.LIST, "index": 11},
        ]
        
        customer_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),  # Reduced from 4
            margin=ft.margin.symmetric(horizontal=0, vertical=0),  # Reduced from 4
        )
        
        # ปุ่มหลัก Customer Management
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
            padding=ft.padding.symmetric(vertical=10, horizontal=16),  # Reduced vertical from 12 to 10
            margin=ft.margin.symmetric(horizontal=12, vertical=2),  # Reduced from 4
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_customer_menu(),
        )
        
        # ซับเมนู
        self.customer_submenu_column = ft.Column(spacing=1, visible=self.parent.customer_menu_expanded)  # Reduced from 2
        
        for item in customer_menu_items:
            sub_btn_container, sub_icon, sub_label = self._create_customer_submenu_button(item)
            self.customer_submenu_buttons.append({
                "container": sub_btn_container,
                "icon": sub_icon,
                "label": sub_label,
                "icon_name": item["icon"],
                "selected_icon_name": item["selected_icon"],
                "index": item["index"]
            })
            self.customer_submenu_column.controls.append(sub_btn_container)
        
        customer_menu_container.content = ft.Column([
            customer_main_btn,
            self.customer_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(customer_menu_container)
    
    def _create_job_order_management_menu(self, nav_column):
        """สร้างเมนู Job Order Management และซับเมนู"""
        job_order_menu_items = [
            {"icon": ft.Icons.ADD_CIRCLE_OUTLINE, "label": get_text("new_job_order"), "selected_icon": ft.Icons.ADD_CIRCLE, "index": 12},
            {"icon": ft.Icons.LIST_ALT, "label": get_text("job_order_list"), "selected_icon": ft.Icons.LIST, "index": 13},
        ]
        
        job_order_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),  # Reduced from 4
            margin=ft.margin.symmetric(horizontal=0, vertical=0),  # Reduced from 4
        )
        
        # ปุ่มหลัก Job Order Management
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
            padding=ft.padding.symmetric(vertical=10, horizontal=16),  # Reduced vertical from 12 to 10
            margin=ft.margin.symmetric(horizontal=12, vertical=2),  # Reduced from 4
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_job_order_menu(),
        )
        
        # ซับเมนู
        self.job_order_submenu_column = ft.Column(spacing=1, visible=self.parent.job_order_menu_expanded)  # Reduced from 2
        
        for item in job_order_menu_items:
            sub_btn_container, sub_icon, sub_label = self._create_job_order_submenu_button(item)
            self.job_order_submenu_buttons.append({
                "container": sub_btn_container,
                "icon": sub_icon,
                "label": sub_label,
                "icon_name": item["icon"],
                "selected_icon_name": item["selected_icon"],
                "index": item["index"]
            })
            self.job_order_submenu_column.controls.append(sub_btn_container)
        
        job_order_menu_container.content = ft.Column([
            job_order_main_btn,
            self.job_order_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(job_order_menu_container)
    
    def _create_quotation_management_menu(self, nav_column):
        """สร้างเมนู Quotation Management และซับเมนู"""
        quotation_menu_items = [
            {"icon": ft.Icons.ADD_CIRCLE_OUTLINE, "label": get_text("new_quotation"), "selected_icon": ft.Icons.ADD_CIRCLE, "index": 14},
            {"icon": ft.Icons.LIST_ALT, "label": get_text("quotations"), "selected_icon": ft.Icons.LIST, "index": 15},
        ]
        
        quotation_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),  # Reduced from 4
            margin=ft.margin.symmetric(horizontal=0, vertical=0),  # Reduced from 4
        )
        
        # ปุ่มหลัก Quotation Management
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
            padding=ft.padding.symmetric(vertical=10, horizontal=16),  # Reduced vertical from 12 to 10
            margin=ft.margin.symmetric(horizontal=12, vertical=2),  # Reduced from 4
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_quotation_menu(),
        )
        
        # ซับเมนู
        self.quotation_submenu_column = ft.Column(spacing=1, visible=self.parent.quotation_menu_expanded)  # Reduced from 2
        
        for item in quotation_menu_items:
            sub_btn_container, sub_icon, sub_label = self._create_quotation_submenu_button(item)
            self.quotation_submenu_buttons.append({
                "container": sub_btn_container,
                "icon": sub_icon,
                "label": sub_label,
                "icon_name": item["icon"],
                "selected_icon_name": item["selected_icon"],
                "index": item["index"]
            })
            self.quotation_submenu_column.controls.append(sub_btn_container)
        
        quotation_menu_container.content = ft.Column([
            quotation_main_btn,
            self.quotation_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(quotation_menu_container)
    
    def _create_repair_management_menu(self, nav_column):
        """สร้างเมนู Repair Management และซับเมนู"""
        repair_menu_items = [
            {"icon": ft.Icons.ADD_CIRCLE_OUTLINE, "label": get_text("new_repair"), "selected_icon": ft.Icons.ADD_CIRCLE, "index": 16},
            {"icon": ft.Icons.LIST_ALT, "label": get_text("repair_list"), "selected_icon": ft.Icons.LIST, "index": 17},
        ]
        
        repair_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),  # Reduced from 4
            margin=ft.margin.symmetric(horizontal=0, vertical=0),  # Reduced from 4
        )
        
        # ปุ่มหลัก Repair Management
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
            padding=ft.padding.symmetric(vertical=10, horizontal=16),  # Reduced vertical from 12 to 10
            margin=ft.margin.symmetric(horizontal=12, vertical=2),  # Reduced from 4
            border_radius=12,
            ink=True,
            on_click=lambda e: self.parent.toggle_repair_menu(),
        )
        
        # ซับเมนู
        self.repair_submenu_column = ft.Column(spacing=1, visible=self.parent.repair_menu_expanded)  # Reduced from 2
        
        for item in repair_menu_items:
            sub_btn_container, sub_icon, sub_label = self._create_repair_submenu_button(item)
            self.repair_submenu_buttons.append({
                "container": sub_btn_container,
                "icon": sub_icon,
                "label": sub_label,
                "icon_name": item["icon"],
                "selected_icon_name": item["selected_icon"],
                "index": item["index"]
            })
            self.repair_submenu_column.controls.append(sub_btn_container)
        
        repair_menu_container.content = ft.Column([
            repair_main_btn,
            self.repair_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(repair_menu_container)
    
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
        """สร้างปุ่มนำทางหลัก"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=10, horizontal=16),  # Reduced vertical from 12 to 10
            margin=ft.margin.symmetric(horizontal=12, vertical=2),  # Reduced from 4
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
        
        # Set selected style for dashboard
        if idx == 0:
            icon.color = self.parent.selected_color
            label.color = self.parent.selected_color
            btn_container.bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
            btn_container.border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
        
        return btn_container, icon, label
    
    def _create_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Data Management"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),  # Reduced from 8
            margin=ft.margin.symmetric(horizontal=12, vertical=1),  # Reduced from 2
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_submenu_hover(e, i),
        )
        
        icon = ft.Icon(item["icon"], color=self.parent.unselected_color, size=20)
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                icon,
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, icon, label
    
    def _create_customer_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Customer Management"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),  # Reduced from 8
            margin=ft.margin.symmetric(horizontal=12, vertical=1),  # Reduced from 2
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_customer_submenu_hover(e, i),
        )
        
        icon = ft.Icon(item["icon"], color=self.parent.unselected_color, size=20)
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                icon,
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, icon, label
    
    def _create_job_order_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Job Order Management"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),  # Reduced from 8
            margin=ft.margin.symmetric(horizontal=12, vertical=1),  # Reduced from 2
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_job_order_submenu_hover(e, i),
        )
        
        icon = ft.Icon(item["icon"], color=self.parent.unselected_color, size=20)
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                icon,
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, icon, label
    
    def _create_quotation_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Quotation Management"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),  # Reduced from 8
            margin=ft.margin.symmetric(horizontal=12, vertical=1),  # Reduced from 2
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_quotation_submenu_hover(e, i),
        )
        
        icon = ft.Icon(item["icon"], color=self.parent.unselected_color, size=20)
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                icon,
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, icon, label
    
    def _create_repair_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Repair Management"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),  # Reduced from 8
            margin=ft.margin.symmetric(horizontal=12, vertical=1),  # Reduced from 2
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_repair_submenu_hover(e, i),
        )
        
        icon = ft.Icon(item["icon"], color=self.parent.unselected_color, size=20)
        label = ft.Text(item["label"], size=13, weight=ft.FontWeight.W_400, color=self.parent.unselected_color)
        
        row = ft.Row(
            [
                ft.Container(width=8),
                icon,
                label,
            ], 
            spacing=12, 
            alignment=ft.MainAxisAlignment.START
        )
        btn_container.content = row
        
        return btn_container, icon, label
    
    def _update_selected_button(self):
        """อัพเดทสถานะปุ่มที่ถูกเลือก"""
        # Reset all buttons
        for btn_data in self.nav_buttons:
            btn_data["icon"].color = self.parent.unselected_color
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        for btn_data in self.data_submenu_buttons:
            btn_data["icon"].color = self.parent.unselected_color
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        for btn_data in self.customer_submenu_buttons:
            btn_data["icon"].color = self.parent.unselected_color
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
        
        if hasattr(self, 'job_order_submenu_buttons'):
            for btn_data in self.job_order_submenu_buttons:
                btn_data["icon"].color = self.parent.unselected_color
                btn_data["label"].color = self.parent.unselected_color
                btn_data["container"].bgcolor = None
                btn_data["container"].border = None
        
        if hasattr(self, 'quotation_submenu_buttons'):
            for btn_data in self.quotation_submenu_buttons:
                btn_data["icon"].color = self.parent.unselected_color
                btn_data["label"].color = self.parent.unselected_color
                btn_data["container"].bgcolor = None
                btn_data["container"].border = None
        
        if hasattr(self, 'repair_submenu_buttons'):
            for btn_data in self.repair_submenu_buttons:
                btn_data["icon"].color = self.parent.unselected_color
                btn_data["label"].color = self.parent.unselected_color
                btn_data["container"].bgcolor = None
                btn_data["container"].border = None
        
        # Select button based on current_index
        selected_btn = next((btn for btn in self.data_submenu_buttons if btn["index"] == self.parent.current_index), None)
        
        if selected_btn:
            selected_btn["icon"].color = self.parent.selected_color
            selected_btn["label"].color = self.parent.selected_color
            selected_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
            selected_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
            
            if selected_btn["selected_icon_name"] != selected_btn["icon_name"]:
                selected_btn["icon"].name = selected_btn["selected_icon_name"]
        else:
            selected_customer_btn = next((btn for btn in self.customer_submenu_buttons if btn["index"] == self.parent.current_index), None)
            
            if selected_customer_btn:
                selected_customer_btn["icon"].color = self.parent.selected_color
                selected_customer_btn["label"].color = self.parent.selected_color
                selected_customer_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                selected_customer_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                
                if selected_customer_btn["selected_icon_name"] != selected_customer_btn["icon_name"]:
                    selected_customer_btn["icon"].name = selected_customer_btn["selected_icon_name"]
            else:
                selected_job_btn = next((btn for btn in self.job_order_submenu_buttons if btn["index"] == self.parent.current_index), None)
                
                if selected_job_btn:
                    selected_job_btn["icon"].color = self.parent.selected_color
                    selected_job_btn["label"].color = self.parent.selected_color
                    selected_job_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                    selected_job_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                    
                    if selected_job_btn["selected_icon_name"] != selected_job_btn["icon_name"]:
                        selected_job_btn["icon"].name = selected_job_btn["selected_icon_name"]
                else:
                    selected_quotation_btn = next((btn for btn in self.quotation_submenu_buttons if btn["index"] == self.parent.current_index), None)
                    
                    if selected_quotation_btn:
                        selected_quotation_btn["icon"].color = self.parent.selected_color
                        selected_quotation_btn["label"].color = self.parent.selected_color
                        selected_quotation_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                        selected_quotation_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                        
                        if selected_quotation_btn["selected_icon_name"] != selected_quotation_btn["icon_name"]:
                            selected_quotation_btn["icon"].name = selected_quotation_btn["selected_icon_name"]
                    else:
                        selected_repair_btn = next((btn for btn in self.repair_submenu_buttons if btn["index"] == self.parent.current_index), None)
                        
                        if selected_repair_btn:
                            selected_repair_btn["icon"].color = self.parent.selected_color
                            selected_repair_btn["label"].color = self.parent.selected_color
                            selected_repair_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                            selected_repair_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
                            
                            if selected_repair_btn["selected_icon_name"] != selected_repair_btn["icon_name"]:
                                selected_repair_btn["icon"].name = selected_repair_btn["selected_icon_name"]
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
                                    if menu_index == 1:  # Data menu
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.data_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 2:  # Customer menu
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.customer_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 3:  # Job Order menu
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.job_order_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 4:  # Quotation menu
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.quotation_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                    elif menu_index == 5:  # Repair menu
                                        arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.repair_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                    menu_index += 1