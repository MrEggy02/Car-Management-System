# pages/layout/content_manager.py
import flet as ft
from flet import Alignment
from i18n import get_text

class ContentManager:
    def __init__(self, parent):
        self.parent = parent
        self.current_view = None
    
    def build(self):
        """สร้าง Content Area"""
        self.current_view = ft.Container(
            content=self._get_dashboard_content(),
            expand=True,
            bgcolor="#F5F7FA",
            padding=0,
        )
        return self.current_view
    
    def switch_content(self, index):
        """สลับเนื้อหาตาม index ที่เลือก"""
        if index == 0:
            content = self._get_dashboard_content()
        elif index == 1:
            content = self._get_employees_content()
        elif index == 2:
            content = self._get_suppliers_content()
        elif index == 3:
            content = self._get_services_content()
        elif index == 4:
            content = self._get_parts_content()
        elif index == 5:
            content = self._get_shop_content()
        elif index == 6:
            content = self._get_promotions_content()
        elif index == 8:
            content = self._get_input_customer_content()
        elif index == 10:
            content = self._get_edit_customer_content()
        elif index == 11:
            content = self._get_customer_list_content()
        elif index == 12:
            content = self._get_job_order_create_content()
        elif index == 13:
            content = self._get_job_order_list_content()
        elif index == 14:
            content = self._get_quotation_create_content()
        elif index == 15:
            content = self._get_quotation_list_content()
        elif index == 16:
            content = self._get_repair_create_content()
        elif index == 17:
            content = self._get_repair_list_content()
        else:
            content = self._get_placeholder(f"📄 {get_text('under_development')}")
        
        self.current_view.content = content
        self.current_view.update()
    
    def _get_dashboard_content(self):
        from pages.dashboard_content import DashboardContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return DashboardContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_employees_content(self):
        from Management.employees.employees_page import EmployeesContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return EmployeesContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_services_content(self):
        try:
            from pages.services_page import ServicesContent
        except ImportError:
            try:
                from Management.service.services_page import ServicesContent
            except ImportError:
                from services_page import ServicesContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return ServicesContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_parts_content(self):
        try:
            from pages.parts_page import PartsContent
        except ImportError:
            try:
                from Management.parts.parts_page import PartsContent
            except ImportError:
                from parts_page import PartsContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return PartsContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_suppliers_content(self):
        try:
            from pages.suppliers_page import SuppliersContent
        except ImportError:
            try:
                from Management.supplier.suppliers_page import SuppliersContent
            except ImportError:
                from suppliers_page import SuppliersContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return SuppliersContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_shop_content(self):
        try:
            from pages.shop_page import ShopContent
        except ImportError:
            try:
                from Management.store.shop_page import ShopContent
            except ImportError:
                from shop_page import ShopContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return ShopContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_promotions_content(self):
        try:
            from pages.promotions_page import PromotionsContent
        except ImportError:
            try:
                from Management.promotion.promotions_page import PromotionsContent
            except ImportError:
                from promotions_page import PromotionsContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return PromotionsContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_input_customer_content(self):
        from pages.customers.input_customer_data import InputCustomerDataContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return InputCustomerDataContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_edit_customer_content(self):
        """Get edit customer data page (Process 2.3)"""
        from pages.customers.edit_customer_data import EditCustomerDataContent
        
        def navigate(page_name, *args, **kwargs):
            customer_id = kwargs.get('customer_id')
            self.parent.navigate_to(page_name, customer_id=customer_id)
        
        customer_id = getattr(self.parent, '_edit_customer_id', None)
        if customer_id:
            delattr(self.parent, '_edit_customer_id')
        
        return EditCustomerDataContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate, 
            customer_id=customer_id
        ).build()
    
    def _get_customer_list_content(self):
        from pages.customers.customer_list import CustomerListContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return CustomerListContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_job_order_create_content(self):
        """Get job order create page (Process 3)"""
        from pages.job_orders.job_order_create import JobOrderCreateContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return JobOrderCreateContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_job_order_list_content(self):
        """Get job order list page"""
        from pages.job_orders.job_order_list import JobOrderListContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return JobOrderListContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_quotation_create_content(self):
        """Get quotation create page (Process 4)"""
        from pages.quotations.quotation_create import QuotationCreateContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        job_order_id = getattr(self.parent, '_job_order_id', None)
        if job_order_id:
            delattr(self.parent, '_job_order_id')
        
        return QuotationCreateContent(self.parent.page, self.parent.client, self.parent.user, navigate, job_order_id=job_order_id).build()
    
    def _get_quotation_list_content(self):
        """Get quotation list page"""
        from pages.quotations.quotation_list import QuotationListContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return QuotationListContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_repair_create_content(self):
        """Get repair create page (Process 5)"""
        from pages.repair.repair_create import RepairCreateContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        job_order_id = getattr(self.parent, '_job_order_id', None)
        if job_order_id:
            delattr(self.parent, '_job_order_id')
        
        # Pass current_view (content_container) to RepairCreateContent
        return RepairCreateContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate, 
            job_order_id=job_order_id,
            content_container=self.current_view  # Pass the content container
        ).build()
    
    def _get_repair_list_content(self):
        """Get repair list page"""
        from pages.repair.repair_list import RepairListContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return RepairListContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_placeholder(self, title):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.INFO, size=80, color=ft.Colors.GREY_400),
                    ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color=self.parent.primary_dark),
                    ft.Text(get_text("under_development"), size=16, color=ft.Colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=Alignment.CENTER,
        )