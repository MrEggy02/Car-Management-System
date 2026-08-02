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
            content = self._get_services_content()
        elif index == 3:
            content = self._get_suppliers_content()
        elif index == 4:
            content = self._get_shop_content()
        elif index == 5:
            content = self._get_parts_content()
        elif index == 6:
            content = self._get_promotions_content()
        elif index == 7:  # Brands page
            content = self._get_part_categories_content()
        elif index == 8:  # Units page
            content = self._get_units_content()
        elif index == 9:  # Part Categories page
            content = self._get_brands_content()
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
        elif index == 18:
            content = self._get_repair_detail_content()
        elif index == 19:
            content = self._get_invoice_create_content()
        elif index == 20:
            content = self._get_invoice_list_content()
        elif index == 21:
            content = self._get_invoice_detail_content()
        elif index == 22:
            content = self._get_purchase_order_create_content()
        elif index == 23:
            content = self._get_purchase_management_content()
        elif index == 24:
            content = self._get_purchase_order_detail_content()
        elif index == 25:
            content = self._get_purchase_order_receive_content()
        elif index == 26:
            content = self._get_stock_movement_content()
        elif index == 27:
            content = self._get_promotion_items_content()
        elif index == 28:
            content = self._get_personal_page_content()
        # Reports (Process 8)
        elif index == 29:
            content = self._get_revenue_report_content()
        elif index == 30:
            content = self._get_repair_summary_report_content()
        elif index == 31:
            content = self._get_parts_usage_report_content()
        elif index == 32:
            content = self._get_service_items_report_content()
        elif index == 33:
            content = self._get_promotion_usage_report_content()
        elif index == 34:
            content = self._get_goods_receipt_list_content()
        elif index == 35:
            content = self._get_purchase_management_content()
        elif index == 36:
            content = self._get_receiving_management_content()
        elif index == 37:
            content = self._get_receiving_po_list_content()
        elif index == 38:
            content = self._get_delivery_note_list_content()
        elif index == 39: 
            content = self._get_stock_history_content()
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
    
    def _get_brands_content(self):
        """Get brands page - in Management folder"""
        from Management.brands.brands_page import BrandsPageContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return BrandsPageContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_units_content(self):
        """Get units page - in Management folder"""
        from Management.units.units_page import UnitsPageContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return UnitsPageContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_part_categories_content(self):
        """Get part categories page - in Management folder"""
        from Management.part_categories.part_categories_page import PartCategoriesPageContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return PartCategoriesPageContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_invoice_detail_content(self):
        """Get invoice detail page"""
        from pages.invoices.invoice_detail import InvoiceDetailContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        invoice_id = getattr(self.parent, '_invoice_id', None)
        if invoice_id:
            delattr(self.parent, '_invoice_id')
            
        return InvoiceDetailContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate, 
            invoice_id=invoice_id
        ).build()
    def _get_stock_history_content(self):
        """Get stock history page"""
        from Management.parts.stock_history_page import StockHistoryPage
    
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
    
        return StockHistoryPage(
               self.parent.page,
               self.parent.client,
               self.parent.user,
               navigate
    ).build()
    def _get_services_content(self):
        from Management.service.services_page import ServicesContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return ServicesContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_parts_content(self):
        from Management.parts.parts_page import PartsContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return PartsContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_suppliers_content(self):
        from Management.supplier.suppliers_page import SuppliersContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return SuppliersContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_shop_content(self):
        from Management.store.shop_page import ShopContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return ShopContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_promotions_content(self):
        from Management.promotion.promotions_page import PromotionsContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return PromotionsContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_customer_list_content(self):
        """Get customer list page (add and edit are now dialogs)"""
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
        """Get quotation create page (Process 4) - FIXED IMPORT"""
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
            content_container=self.current_view
        ).build()
    
    def _get_repair_list_content(self):
        """Get repair list page"""
        from pages.repair.repair_list import RepairListContent
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        return RepairListContent(self.parent.page, self.parent.client, self.parent.user, navigate).build()
    
    def _get_repair_detail_content(self):
        """Get repair detail page"""
        from pages.repair.repair_detail import RepairDetailContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        repair_id = getattr(self.parent, '_repair_id', None)
        read_only = getattr(self.parent, '_read_only', False)
        if repair_id:
            delattr(self.parent, '_repair_id')
            if hasattr(self.parent, '_read_only'):
                delattr(self.parent, '_read_only')
        
        return RepairDetailContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate, 
            repair_id=repair_id,
            read_only=read_only
        ).build()
    
    def _get_invoice_create_content(self):
        """Get invoice create page (Process 6)"""
        from pages.invoices.invoice_create import InvoiceCreateContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        job_order_id = getattr(self.parent, '_job_order_id', None)
        if job_order_id:
            delattr(self.parent, '_job_order_id')
        
        return InvoiceCreateContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate, 
            job_order_id=job_order_id,
            content_container=self.current_view
        ).build()
    
    def _get_invoice_list_content(self):
        """Get invoice list page (Process 6)"""
        from pages.invoices.invoice_list import InvoiceListContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        return InvoiceListContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate
        ).build()
    
    # ========== Process 7: Stock Management (Purchase Orders) ==========
    
    def _get_purchase_order_create_content(self):
        """Get purchase order create page (Process 7.2)"""
        from pages.purchase.purchase_order_create import PurchaseOrderCreateContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        return PurchaseOrderCreateContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate,
            content_container=self.current_view
        ).build()
    
    def _get_purchase_order_list_content(self):
        """Get purchase order list page (Process 7.2)"""
        from pages.purchase.purchase_order_list import PurchaseOrderListContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        return PurchaseOrderListContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate
        ).build()
    
    def _get_purchase_order_detail_content(self):
        """Get purchase order detail page"""
        from pages.purchase.purchase_order_detail import PurchaseOrderDetailContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        po_id = getattr(self.parent, '_po_id', None)
        if po_id:
            delattr(self.parent, '_po_id')
        
        return PurchaseOrderDetailContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate, 
            po_id=po_id
        ).build()
    
    def _get_purchase_order_receive_content(self):
        """Get purchase order receive page (Process 7.3)"""
        from pages.purchase.purchase_order_receive import PurchaseOrderReceiveContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        po_id = getattr(self.parent, '_po_id', None)
        if po_id:
            delattr(self.parent, '_po_id')
        
        return PurchaseOrderReceiveContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate, 
            po_id=po_id
        ).build()
    
    def _get_stock_movement_content(self):
        """Get stock movement history page"""
        from pages.purchase.stock_movement import StockMovementContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        return StockMovementContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate
        ).build()
    
    # ========== Process 6.5: Promotion Items ==========
    
    def _get_promotion_items_content(self):
        """Get promotion items management page"""
        from pages.promotion_items import PromotionItemsContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        promotion_id = getattr(self.parent, '_promotion_id', None)
        promotion_name = getattr(self.parent, '_promotion_name', None)
        if promotion_id:
            delattr(self.parent, '_promotion_id')
        if promotion_name:
            delattr(self.parent, '_promotion_name')
        
        return PromotionItemsContent(
            self.parent.page, 
            self.parent.client, 
            self.parent.user, 
            navigate, 
            promotion_id=promotion_id,
            promotion_name=promotion_name
        ).build()
    
    def _get_personal_page_content(self):
        """Get personal page content"""
        from pages.personal_page import PersonalPageContent
    
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
    
        return PersonalPageContent(
            self.parent.page,
            self.parent.client,
            self.parent.user,
            navigate
        ).build()
    
    # ========== Process 8: Reports ==========
    
    def _get_revenue_report_content(self):
        """Get revenue report page (Process 8.1)"""
        from pages.reports.revenue_report import RevenueReportContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        return RevenueReportContent(
            self.parent.page,
            self.parent.client,
            self.parent.user,
            navigate
        ).build()
    
    def _get_repair_summary_report_content(self):
        """Get repair summary report page (Process 8.2)"""
        from pages.reports.repair_summary_report import RepairSummaryReportContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        return RepairSummaryReportContent(
            self.parent.page,
            self.parent.client,
            self.parent.user,
            navigate
        ).build()
    
    def _get_parts_usage_report_content(self):
        """Get parts and service sales report page (Process 8.3)"""
        from pages.reports.parts_service_sales_report import PartsServiceSalesReportContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        return PartsServiceSalesReportContent(
            self.parent.page,
            self.parent.client,
            self.parent.user,
            navigate
        ).build()
    
    def _get_service_items_report_content(self):
        """Get mechanic performance report page (Process 8.4)"""
        from pages.reports.mechanic_performance_report import MechanicPerformanceReportContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        return MechanicPerformanceReportContent(
            self.parent.page,
            self.parent.client,
            self.parent.user,
            navigate
        ).build()
    
    def _get_promotion_usage_report_content(self):
        """Get promotion usage report page (Process 8.5)"""
        from pages.reports.promotion_usage_report import PromotionUsageReportContent
        return PromotionUsageReportContent(
            page=self.parent.page,
            client=self.parent.client,
            user=self.parent.user,
            navigate=self.parent.navigate_to
        ).build()
        
    def _get_purchase_management_content(self):
        from pages.purchase.purchase_management import PurchaseManagementContent
        return PurchaseManagementContent(
            page=self.parent.page,
            client=self.parent.client,
            user=self.parent.user,
            navigate=self.parent.navigate_to
        ).build()
        
    def _get_receiving_management_content(self):
        from pages.purchase.receiving_management import ReceivingManagementContent
        return ReceivingManagementContent(
            page=self.parent.page,
            client=self.parent.client,
            user=self.parent.user,
            navigate=self.parent.navigate_to
        ).build()
        
    def _get_receiving_po_list_content(self):
        from pages.purchase.receiving_po_list import ReceivingPoListContent
        return ReceivingPoListContent(
            page=self.parent.page,
            client=self.parent.client,
            user=self.parent.user,
            navigate=self.parent.navigate_to
        ).build()

    def _get_delivery_note_list_content(self):
        """ໜ້າລາຍຊື່ໃບສົ່ງມອບລົດ"""
        from pages.invoices.delivery_note_list import DeliveryNoteListContent
        return DeliveryNoteListContent(
            page=self.parent.page,
            client=self.parent.client,
            user=self.parent.user,
            navigate=self.parent.navigate_to
        ).build()
    
    def _get_goods_receipt_list_content(self):
        """Get goods receipt list page (Process 7.3)"""
        from pages.purchase.goods_receipt_list import GoodsReceiptListContent
        
        def navigate(page_name, *args, **kwargs):
            self.parent.navigate_to(page_name, **kwargs)
        
        return GoodsReceiptListContent(
            self.parent.page,
            self.parent.client,
            self.parent.user,
            navigate
        ).build()
    
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