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
        self.reports_submenu_buttons = []
        self.submenu_column = None
        self.customer_submenu_column = None
        self.job_order_submenu_column = None
        self.quotation_submenu_column = None
        self.repair_submenu_column = None
        self.invoice_submenu_column = None
        self.purchase_submenu_column = None
        self.reports_submenu_column = None
        
        # Store single item menu button references
        self.customer_main_btn = None
        self.job_order_main_btn = None
        self.quotation_main_btn = None
        
    def build(self):
        """สร้าง Sidebar"""
        nav_column = ft.Column(spacing=0)
        
        # สร้างปุ่มหลัก
        self._create_main_nav_buttons(nav_column)
        
        # สร้าง Data Management Menu
        self._create_data_management_menu(nav_column)
        
        # สร้าง Customer Management Menu (เฉพาะ Customer List)
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
        
        # สร้าง Reports Management Menu (Process 8)
        self._create_reports_management_menu(nav_column)
        
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
            {"icon": "assets/icons/dashboard.png", "label": get_text("dashboard"), "selected_icon": "assets/icons/dashboard.png"},
        ]
        
        for idx, item in enumerate(nav_items):
            btn_container, icon, label = self._create_nav_button(item, idx)
            self.nav_buttons.append({
                "container": btn_container,
                "icon": icon,
                "label": label,
                "icon_path": item["icon"],
                "selected_icon_path": item["selected_icon"],
                "index": idx
            })
            nav_column.controls.append(btn_container)
    
    def _create_data_management_menu(self, nav_column):
        """สร้างเมนู Data Management และซับเมนู"""
        data_menu_items = [
            {"label": get_text("nav_employees"), "index": 1},
            {"label": get_text("nav_suppliers"), "index": 2},
            {"label": get_text("nav_services"), "index": 3},
            {"label": get_text("nav_parts"), "index": 4},
            {"label": get_text("nav_shop"), "index": 5},
            {"label": get_text("nav_promotions"), "index": 6},
            {"label": get_text("nav_master_data"), "index": 7},
            
        ]
        
        data_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
        )
        
        data_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Image(src="assets/icons/data_management.png", width=22, height=22, color=self.parent.unselected_color),
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
        """สร้างเมนู Customer Management - คลิกได้เลย ไม่มี dropdown"""
        
        self.customer_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Image(src="assets/icons/customer_management.png", width=22, height=22, color=self.parent.unselected_color),
                    ft.Text(
                        get_text("customer_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            data="customer_menu",
            on_click=lambda e: self.parent.on_nav_click(11),
            on_hover=lambda e: self._on_single_menu_hover(e, self.customer_main_btn),
        )
        
        nav_column.controls.append(self.customer_main_btn)
    
    def _create_job_order_management_menu(self, nav_column):
        """สร้างเมนู Job Order Management - คลิกได้เลย ไม่มี dropdown"""
        
        self.job_order_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Image(src="assets/icons/job_order.png", width=22, height=22, color=self.parent.unselected_color),
                    ft.Text(
                        get_text("job_order_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            data="job_order_menu",
            on_click=lambda e: self.parent.on_nav_click(13),
            on_hover=lambda e: self._on_single_menu_hover(e, self.job_order_main_btn),
        )
        
        nav_column.controls.append(self.job_order_main_btn)
    
    def _create_quotation_management_menu(self, nav_column):
        """สร้างเมนู Quotation Management - คลิกได้เลย ไม่มี dropdown"""
        
        self.quotation_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Image(src="assets/icons/quotation.png", width=22, height=22, color=self.parent.unselected_color),
                    ft.Text(
                        get_text("quotation_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.padding.symmetric(vertical=10, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=2),
            border_radius=12,
            ink=True,
            data="quotation_menu",
            on_click=lambda e: self.parent.on_nav_click(15),
            on_hover=lambda e: self._on_single_menu_hover(e, self.quotation_main_btn),
        )
        
        nav_column.controls.append(self.quotation_main_btn)
    
    def _on_single_menu_hover(self, e, btn_container):
        """Handle hover for single item menus"""
        if e.data == "true":
            if self.parent.current_index not in [11, 13, 15]:
                btn_container.bgcolor = self.parent.hover_color
        else:
            if self.parent.current_index not in [11, 13, 15]:
                btn_container.bgcolor = None
        if btn_container.page:
            btn_container.page.update()
    
    def _create_repair_management_menu(self, nav_column):
        """สร้างเมนู Repair Management - มี dropdown"""
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
                    ft.Image(src="assets/icons/repair.png", width=22, height=22, color=self.parent.unselected_color),
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
        """สร้างเมนู Invoice Management - มี dropdown"""
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
                    ft.Image(src="assets/icons/invoice.png", width=22, height=22, color=self.parent.unselected_color),
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
        """สร้างเมนู Purchase Management - มี dropdown"""
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
                    ft.Image(src="assets/icons/purchase.png", width=22, height=22, color=self.parent.unselected_color),
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
    
    def _create_reports_management_menu(self, nav_column):
        """สร้างเมนู Reports Management - มี dropdown"""
        reports_menu_items = [
            {"label": get_text("revenue_report"), "index": 29},
            {"label": get_text("repair_summary_report"), "index": 30},
            {"label": get_text("parts_usage_report"), "index": 31},
            {"label": get_text("service_items_report"), "index": 32},
            {"label": get_text("promotion_usage_report"), "index": 33},
        ]
        
        reports_menu_container = ft.Container(
            padding=ft.padding.symmetric(vertical=2, horizontal=0),
            margin=ft.margin.symmetric(horizontal=0, vertical=0),
        )
        
        reports_main_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Image(src="assets/icons/report.png", width=22, height=22, color=self.parent.unselected_color),
                    ft.Text(
                        get_text("reports_management"),
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color=self.parent.unselected_color,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.KEYBOARD_ARROW_DOWN if not self.parent.reports_menu_expanded else ft.Icons.KEYBOARD_ARROW_UP,
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
            on_click=lambda e: self.parent.toggle_reports_menu(),
        )
        
        self.reports_submenu_column = ft.Column(spacing=1, visible=self.parent.reports_menu_expanded)
        
        for item in reports_menu_items:
            sub_btn_container, sub_label = self._create_reports_submenu_button(item)
            self.reports_submenu_buttons.append({
                "container": sub_btn_container,
                "label": sub_label,
                "index": item["index"]
            })
            self.reports_submenu_column.controls.append(sub_btn_container)
        
        reports_menu_container.content = ft.Column([
            reports_main_btn,
            self.reports_submenu_column,
        ], spacing=0)
        
        nav_column.controls.append(reports_menu_container)
    
    
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
        
        icon = ft.Image(src=item["icon"], width=22, height=22, color=self.parent.unselected_color)
        label = ft.Text(item["label"], size=14, weight=ft.FontWeight.W_500, color=self.parent.unselected_color)
        row = ft.Row([icon, label], spacing=16, alignment=ft.MainAxisAlignment.START)
        btn_container.content = row
        
        if idx == 0:
            icon.color = self.parent.selected_color
            label.color = self.parent.selected_color
            btn_container.bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
            btn_container.border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
            icon.src = item["selected_icon"]
        
        return btn_container, icon, label
    
    def _create_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Data Management"""
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
        """สร้างปุ่มซับเมนูสำหรับ Customer Management (ไม่ใช้แล้ว แต่เก็บไว้)"""
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
        """สร้างปุ่มซับเมนูสำหรับ Job Order Management (ไม่ใช้แล้ว แต่เก็บไว้)"""
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
        """สร้างปุ่มซับเมนูสำหรับ Quotation Management (ไม่ใช้แล้ว แต่เก็บไว้)"""
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
        """สร้างปุ่มซับเมนูสำหรับ Repair Management"""
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
        """สร้างปุ่มซับเมนูสำหรับ Invoice Management"""
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
        """สร้างปุ่มซับเมนูสำหรับ Purchase Management"""
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
    
    def _create_reports_submenu_button(self, item):
        """สร้างปุ่มซับเมนูสำหรับ Reports Management"""
        btn_container = ft.Container(
            padding=ft.padding.symmetric(vertical=6, horizontal=16),
            margin=ft.margin.symmetric(horizontal=12, vertical=1),
            border_radius=10,
            ink=True,
            data=item["index"],
            on_click=lambda e, i=item["index"]: self.parent.on_nav_click(i),
            on_hover=lambda e, i=item["index"]: self.parent.on_reports_submenu_hover(e, i),
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
        # Reset all main buttons (Dashboard)
        for btn_data in self.nav_buttons:
            btn_data["icon"].color = self.parent.unselected_color
            btn_data["label"].color = self.parent.unselected_color
            btn_data["container"].bgcolor = None
            btn_data["container"].border = None
            if "icon_path" in btn_data:
                btn_data["icon"].src = btn_data["icon_path"]
        
        # Reset all submenu buttons
        for btn_list in [self.data_submenu_buttons, self.customer_submenu_buttons, 
                         self.job_order_submenu_buttons, self.quotation_submenu_buttons,
                         self.repair_submenu_buttons, self.invoice_submenu_buttons,
                         self.purchase_submenu_buttons, self.reports_submenu_buttons]:
            for btn_data in btn_list:
                btn_data["label"].color = self.parent.unselected_color
                btn_data["container"].bgcolor = None
                btn_data["container"].border = None
        
        # Reset single item menu buttons (Customer, Job Order, Quotation)
        for btn in [self.customer_main_btn, self.job_order_main_btn, self.quotation_main_btn]:
            if btn:
                # Reset icon and text color
                for child in btn.content.controls:
                    if isinstance(child, ft.Image):
                        child.color = self.parent.unselected_color
                    elif isinstance(child, ft.Text):
                        child.color = self.parent.unselected_color
                btn.bgcolor = None
                btn.border = None
        
        # Highlight selected button based on current_index
        current = self.parent.current_index
        
        # Check submenu buttons first
        selected = None
        for btn_list in [self.data_submenu_buttons, self.customer_submenu_buttons,
                         self.job_order_submenu_buttons, self.quotation_submenu_buttons,
                         self.repair_submenu_buttons, self.invoice_submenu_buttons,
                         self.purchase_submenu_buttons, self.reports_submenu_buttons]:
            selected = next((btn for btn in btn_list if btn["index"] == current), None)
            if selected:
                break
        
        if selected:
            selected["label"].color = self.parent.selected_color
            selected["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
            selected["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
        elif current in [11, 13, 15]:
            # Single item menu
            btn_map = {
                11: self.customer_main_btn,
                13: self.job_order_main_btn,
                15: self.quotation_main_btn
            }
            btn = btn_map.get(current)
            if btn:
                for child in btn.content.controls:
                    if isinstance(child, ft.Image):
                        child.color = self.parent.selected_color
                    elif isinstance(child, ft.Text):
                        child.color = self.parent.selected_color
                btn.bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
                btn.border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
        elif current < len(self.nav_buttons):
            # Dashboard
            main_btn = self.nav_buttons[current]
            main_btn["icon"].color = self.parent.selected_color
            main_btn["label"].color = self.parent.selected_color
            main_btn["container"].bgcolor = ft.Colors.with_opacity(0.1, self.parent.selected_color)
            main_btn["container"].border = ft.border.only(left=ft.border.BorderSide(3, self.parent.selected_color))
            if "selected_icon_path" in main_btn:
                main_btn["icon"].src = main_btn["selected_icon_path"]
    
    def update_arrow_icons(self):
        """อัพเดทไอคอนลูกศรของเมนู"""
        if self.sidebar and len(self.sidebar.content.controls) > 0:
            nav_column = self.sidebar.content.controls[1].content.controls[0]
            
            for control in nav_column.controls:
                if isinstance(control, ft.Container):
                    content = control.content
                    # Check if it's a menu with dropdown (has Column and arrow)
                    if isinstance(content, ft.Column) and len(content.controls) > 0:
                        main_btn = content.controls[0]
                        if isinstance(main_btn, ft.Container) and isinstance(main_btn.content, ft.Row):
                            # Check if arrow exists (3rd child)
                            if len(main_btn.content.controls) > 2:
                                arrow_icon = main_btn.content.controls[2]
                                if isinstance(arrow_icon, ft.Icon):
                                    # Check text to identify menu
                                    text_widget = main_btn.content.controls[1]
                                    if isinstance(text_widget, ft.Text):
                                        menu_text = text_widget.value
                                        
                                        if menu_text == get_text("data_management"):
                                            arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.data_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                        elif menu_text == get_text("repair_management"):
                                            arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.repair_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                        elif menu_text == get_text("invoice_management"):
                                            arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.invoice_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                        elif menu_text == get_text("purchase_management"):
                                            arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.purchase_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
                                        elif menu_text == get_text("reports_management"):
                                            arrow_icon.name = ft.Icons.KEYBOARD_ARROW_UP if self.parent.reports_menu_expanded else ft.Icons.KEYBOARD_ARROW_DOWN