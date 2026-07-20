# frontend/pages/dashboard_content.py
import flet as ft
from i18n import get_text
from datetime import datetime
import math


class DashboardContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"
        self.primary_light = "#E3F2FD"
        
        # Dashboard data
        self.summary_data = {}
        self.employees = []
        self.low_stock_parts = []
        self.recent_repairs = []
        
    def build(self):
        # Load data
        self.load_all_data()
        
        # Header with gradient
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("dashboard"),
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.CALENDAR_TODAY, size=18, color=ft.Colors.WHITE),
                                ft.Text(
                                    datetime.now().strftime("%d/%m/%Y"),
                                    size=14,
                                    color=ft.Colors.WHITE,
                                ),
                            ],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                        border_radius=30,
                        padding=ft.Padding(left=16, right=16, top=8, bottom=8),
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=26, right=26, top=14, bottom=14),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
           
        )
        
        # Quick Actions Row - IMPROVED
        quick_actions_row = self._build_quick_actions()
        
        # Stats Row with Icons
        stats_row = ft.Container(
            content=ft.Row(
                [
                    self._build_stats_card(
                        title=get_text("today_revenue"),
                        value=self._format_currency(self.summary_data.get('today_revenue', 0)),
                        subtitle=f"{self.summary_data.get('today_invoices', 0)} {get_text('invoices')}",
                        icon=ft.Icons.ATTACH_MONEY,
                        color="#10B981",
                        progress=None,
                    ),
                    self._build_stats_card(
                        title=get_text("pending_quotations"),
                        value=str(self.summary_data.get('pending_quotations', 0)),
                        subtitle=get_text("waiting"),
                        icon=ft.Icons.PENDING_ACTIONS,
                        color="#F59E0B",
                        progress=None,
                    ),
                    self._build_stats_card(
                        title=get_text("unpaid_invoices"),
                        value=self._format_currency(self.summary_data.get('unpaid_invoices_amount', 0)),
                        subtitle=f"{self.summary_data.get('unpaid_invoices_count', 0)} {get_text('invoices')}",
                        icon=ft.Icons.ACCOUNT_BALANCE_WALLET,
                        color="#EF4444",
                        progress=None,
                    ),
                ],
                spacing=20,
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=12, right=12, top=12, bottom=12),
            bgcolor="#F5F7FA",
        )
        
        # Repair Status Section with Circular Progress Charts
        total_repairs = self.summary_data.get('total_repairs', 0) or 1
        
        repair_status = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        get_text("repair_status"),
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#1E293B",
                    ),
                    ft.Container(height=12),
                    ft.Row(
                        [
                            self._build_circular_chart_card(
                                title=get_text("working"),
                                value=self.summary_data.get('working_repairs', 0),
                                total=total_repairs,
                                icon=ft.Icons.BUILD,
                                color="#2196F3",
                            ),
                            self._build_circular_chart_card(
                                title=get_text("pending"),
                                value=self.summary_data.get('pending_repairs', 0),
                                total=total_repairs,
                                icon=ft.Icons.HOURGLASS_EMPTY,
                                color="#FF9800",
                            ),
                            self._build_circular_chart_card(
                                title=get_text("completed"),
                                value=self.summary_data.get('completed_repairs', 0),
                                total=total_repairs,
                                icon=ft.Icons.CHECK_CIRCLE,
                                color="#4CAF50",
                            ),
                        ],
                        spacing=20,
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=0,
            ),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=0, right=0, top=0, bottom=0),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            expand=True,
        )
        
        # Middle row
        middle_row = ft.Row(
            [repair_status],
            spacing=20,
            expand=True,
        )
        

        
        # Low Stock Parts Section
        low_stock_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                get_text("low_stock_alert"),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#EF4444",
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                get_text("view_all"),
                                on_click=lambda e: self.navigate("parts"),
                                style=ft.ButtonStyle(color=self.primary_color),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Column(
                            [self._build_low_stock_row(part) for part in self.low_stock_parts[:3]] if self.low_stock_parts else [
                                ft.Text(get_text("no_low_stock"), size=13, color="#64748B")
                            ],
                            spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                            height=160,
                        ),
                    ),
                ],
                spacing=0,
            ),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=0, right=0, top=0, bottom=0),
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
        
        # Recent Repairs Section
        recent_repairs_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                get_text("recent_repairs"),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                get_text("view_all"),
                                on_click=lambda e: self.navigate("repair_list"),
                                style=ft.ButtonStyle(color=self.primary_color),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Column(
                            [self._build_repair_row(repair) for repair in self.recent_repairs[:3]] if self.recent_repairs else [
                                ft.Text(get_text("no_repairs"), size=13, color="#64748B")
                            ],
                            spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                            height=160,
                        ),
                    ),
                ],
                spacing=0,
            ),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=0, right=0, top=0, bottom=0),
            expand=True,
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
        
        # Two column layout
        two_column_row = ft.Row(
            [
                low_stock_container,
                recent_repairs_container,
            ],
            spacing=20,
            expand=True,
        )
        
        # Scrollable content
        scrollable_content = ft.Column(
            [
                quick_actions_row,
                stats_row,
                middle_row,
                two_column_row,
            ],
            spacing=20,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        content_area = ft.Container(
            content=scrollable_content,
            expand=True,
            padding=ft.Padding(left=24, right=24, top=24, bottom=24),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([header, content_area]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        return main_content
    
    def load_all_data(self):
        """Load all dashboard data"""
        try:
            self.summary_data = self.client.get_dashboard_summary()
            if not self.summary_data:
                self.summary_data = {}
            
            self.employees = self.client.get_employees()
            if not self.employees:
                self.employees = []
            
            # Get low stock parts
            try:
                self.low_stock_parts = self.client.get_low_stock_parts()
                if not self.low_stock_parts:
                    self.low_stock_parts = []
            except Exception as ex:
                print(f"Error loading low stock parts: {ex}")
                self.low_stock_parts = []
            
            # Get recent repairs
            try:
                repair_orders = self.client.get_repair_orders()
                self.recent_repairs = repair_orders[:10] if repair_orders else []
            except Exception as ex:
                print(f"Error loading recent repairs: {ex}")
                self.recent_repairs = []
            
            print(f"DEBUG: Data loaded - Employees: {len(self.employees)}, Low Stock: {len(self.low_stock_parts)}, Repairs: {len(self.recent_repairs)}")
        except Exception as ex:
            print(f"Error loading dashboard data: {ex}")
            import traceback
            traceback.print_exc()
    
    def _format_currency(self, amount):
        """Format currency with commas"""
        try:
            return f"{int(amount or 0):,} KIP"
        except:
            return "0 KIP"
    
    def _get_today_progress(self):
        """Calculate today's progress (based on month target)"""
        month_revenue = self.summary_data.get('month_revenue', 0) or 0
        today_revenue = self.summary_data.get('today_revenue', 0) or 0
        if month_revenue > 0:
            return min(today_revenue / month_revenue, 1)
        return 0
    
    def _get_month_progress(self):
        """Calculate month progress (days passed in month)"""
        today = datetime.now()
        days_in_month = 30
        progress = (today.day - 1) / days_in_month
        return min(max(progress, 0), 1)
    
    def _get_completion_rate(self):
        """Calculate repair completion rate"""
        total = self.summary_data.get('total_repairs', 0) or 0
        completed = self.summary_data.get('completed_repairs', 0) or 0
        if total > 0:
            return int((completed / total) * 100)
        return 0
    
    # ======================= IMPROVED QUICK ACTIONS =======================
    def _build_quick_actions(self):
        """Build quick action buttons with modern card style"""
        def create_action_card(icon, text, route, color, bg_color):
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, size=24, color=ft.Colors.WHITE),
                            bgcolor=color,
                            border_radius=12,
                            padding=ft.Padding(left=12, right=12, top=12, bottom=12),
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    text,
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color="#1E293B",
                                ),
                                ft.Text(
                                    get_text("click_to_start"),
                                    size=10,
                                    color="#94A3B8",
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Icon(
                            ft.Icons.CHEVRON_RIGHT,
                            size=16,
                            color="#94A3B8",
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=16, right=12, top=12, bottom=12),
                bgcolor=bg_color,
                border_radius=12,
                border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
                shadow=ft.BoxShadow(
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
                on_click=lambda e: self.navigate(route),
                ink=True,
                expand=True,
            )
        
        # Buttons with different colors
        return ft.Container(
            content=ft.Row(
                [
                    create_action_card(
                        ft.Icons.ADD_BOX,
                        get_text("new_job_order"),
                        "job_order_create",
                        self.primary_color,
                        ft.Colors.WHITE,
                    ),
                    create_action_card(
                        ft.Icons.DESCRIPTION,
                        get_text("new_quotation"),
                        "quotation_create",
                        "#F59E0B",
                        ft.Colors.WHITE,
                    ),
                    create_action_card(
                        ft.Icons.PAYMENT,
                        get_text("receive_payment"),
                        "invoice_list",
                        "#10B981",
                        ft.Colors.WHITE,
                    ),
                ],
                spacing=16,
                expand=True,
            ),
            margin=ft.Margin(left=0, right=0, top=0, bottom=12),
            padding=ft.Padding(left=4, right=4, top=0, bottom=0),
        )

    # ======================= END IMPROVED QUICK ACTIONS =======================
    
    def _build_stats_card(self, title, value, subtitle, icon, color, progress=None):
        """Build stats card with progress ring"""
        content_items = [
            ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=24, color=ft.Colors.WHITE),
                        bgcolor=color,
                        border_radius=12,
                        padding=ft.Padding(left=10, right=10, top=10, bottom=10),
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        value,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color="#1E293B",
                        text_align=ft.TextAlign.RIGHT,
                    ),
                ],
                spacing=12,
            ),
            ft.Container(height=4),
            ft.Text(title, size=13, color="#64748B"),
            ft.Text(subtitle, size=10, color="#94A3B8"),
        ]
        
        if progress is not None:
            content_items.extend([
                ft.Container(height=8),
                ft.ProgressBar(
                    value=progress,
                    color=color,
                    bgcolor=ft.Colors.GREY_200,
                    height=4,
                    border_radius=2,
                )
            ])
            
        return ft.Container(
            content=ft.Column(
                content_items,
                spacing=0,
            ),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100), right=ft.BorderSide(1, ft.Colors.GREY_100), bottom=ft.BorderSide(1, ft.Colors.GREY_100), left=ft.BorderSide(1, ft.Colors.GREY_100)),
            expand=True,
        )
    
    def _build_circular_chart_card(self, title, value, total, icon, color):
        """Build circular chart card with percentage"""
        percentage = (value / total * 100) if total > 0 else 0
        angle = (percentage / 100) * 360
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Stack(
                        [
                            ft.Container(
                                width=100,
                                height=100,
                                bgcolor=ft.Colors.GREY_100,
                                border_radius=50,
                            ),
                            ft.Container(
                                width=100,
                                height=100,
                                border_radius=50,
                                gradient=ft.SweepGradient(
                                    center=ft.Alignment(0, 0),
                                    start_angle=0,
                                    end_angle=angle * (math.pi / 180),
                                    colors=[color, ft.Colors.with_opacity(0.3, color)],
                                ),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            str(value),
                                            size=22,
                                            weight=ft.FontWeight.BOLD,
                                            color=color,
                                        ),
                                        ft.Icon(icon, size=20, color=color),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                ),
                                width=80,
                                height=80,
                                bgcolor=ft.Colors.WHITE,
                                border_radius=40,
                                alignment=ft.Alignment(0, 0),
                            ),
                        ],
                        width=100,
                        height=100,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(height=8),
                    ft.Text(title, size=13, weight=ft.FontWeight.W_500, color="#64748B"),
                    ft.Text(f"{percentage:.1f}%", size=11, color=color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.Padding(left=16, right=16, top=16, bottom=16),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100), right=ft.BorderSide(1, ft.Colors.GREY_100), bottom=ft.BorderSide(1, ft.Colors.GREY_100), left=ft.BorderSide(1, ft.Colors.GREY_100)),
            expand=True,
        )
    
    def _build_revenue_chart(self):
        """Build revenue chart (simple bar chart)"""
        month_revenue = self.summary_data.get('month_revenue', 0) or 0
        target = 10000000  # 10,000,000 KIP target
        progress = min(month_revenue / target, 1) if target > 0 else 0
        
        # Calculate average per day
        avg_per_day = month_revenue / 30 if month_revenue > 0 else 0
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                get_text("revenue_progress"),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#1E293B",
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                f"{get_text('target')}: {self._format_currency(target)}",
                                size=12,
                                color="#64748B",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=16),
                    ft.Row(
                        [
                            ft.Text(
                                self._format_currency(month_revenue),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=self.primary_color,
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                f"{int(progress * 100)}%",
                                size=14,
                                color="#64748B",
                            ),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.ProgressBar(
                        value=progress,
                        color=self.primary_color,
                        bgcolor=ft.Colors.GREY_200,
                        height=10,
                        border_radius=5,
                    ),
                    ft.Container(height=12),
                    ft.Row(
                        [
                            self._build_metric_item(
                                get_text("avg_per_day"),
                                self._format_currency(avg_per_day),
                                ft.Icons.TRENDING_UP,
                                "#10B981",
                            ),
                            self._build_metric_item(
                                get_text("best_day"),
                                self._format_currency(self.summary_data.get('today_revenue', 0)),
                                ft.Icons.STAR,
                                "#F59E0B",
                            ),
                            self._build_metric_item(
                                get_text("growth"),
                                "+15%",
                                ft.Icons.ARROW_UPWARD,
                                "#10B981",
                            ),
                        ],
                        spacing=16,
                        expand=True,
                    ),
                ],
                spacing=0,
            ),
            padding=ft.Padding(left=20, right=20, top=20, bottom=20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            margin=ft.Margin(left=0, right=0, top=0, bottom=20),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _build_metric_item(self, title, value, icon, color):
        """Build small metric item"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=16, color=ft.Colors.WHITE),
                        bgcolor=color,
                        border_radius=8,
                        padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                    ),
                    ft.Column(
                        [
                            ft.Text(str(value), size=13, weight=ft.FontWeight.W_500, color="#1E293B"),
                            ft.Text(title, size=10, color="#64748B"),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
            expand=True,
        )
    
    def _build_employee_row(self, employee):
        """Build employee row for list"""
        name = employee.get('name', '-')
        role = employee.get('role', '-')
        phone = employee.get('phone', '-')
        
        role_colors = {
            'admin': ("#EF4444", get_text("role_admin")),
            'manager': ("#F59E0B", get_text("role_manager")),
            'technician': ("#3B82F6", get_text("role_technician")),
            'reception': ("#10B981", get_text("role_reception")),
            'mechanic': ("#3B82F6", get_text("role_mechanic")),
        }
        role_color, role_text = role_colors.get(role, ("#64748B", role.capitalize() if role else '-'))
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text(name[0].upper() if name else "?", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        width=40,
                        height=40,
                        bgcolor=self.primary_color,
                        border_radius=20,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        [
                            ft.Text(name, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                            ft.Text(phone, size=11, color="#64748B"),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(role_text, size=11, color=role_color),
                        bgcolor=ft.Colors.with_opacity(0.1, role_color),
                        border_radius=12,
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100), right=ft.BorderSide(1, ft.Colors.GREY_100), bottom=ft.BorderSide(1, ft.Colors.GREY_100), left=ft.BorderSide(1, ft.Colors.GREY_100)),
        )
    
    def _build_low_stock_row(self, part):
        """Build low stock part row"""
        name = part.get('name', '-')
        stock_qty = part.get('stock_qty', 0)
        min_stock = part.get('min_stock', 5)
        
        # Calculate percentage
        percentage = min(stock_qty / min_stock, 1) if min_stock > 0 else 0
        
        # Determine color based on stock level
        if stock_qty <= 0:
            color = "#EF4444"
            status = get_text("out_of_stock")
        elif stock_qty <= min_stock / 2:
            color = "#F59E0B"
            status = get_text("critical")
        else:
            color = "#FF9800"
            status = get_text("low")
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.INVENTORY, size=20, color=color),
                        width=40,
                        height=40,
                        bgcolor=ft.Colors.with_opacity(0.1, color),
                        border_radius=10,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        [
                            ft.Text(name, size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                            ft.Text(f"{get_text('stock')}: {stock_qty} / {get_text('min_stock')}: {min_stock}", size=11, color="#64748B"),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.ProgressBar(
                                    value=percentage,
                                    color=color,
                                    bgcolor=ft.Colors.GREY_200,
                                    width=60,
                                    height=4,
                                    border_radius=2,
                                ),
                                ft.Text(status, size=11, color=color),
                            ],
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=120,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100), right=ft.BorderSide(1, ft.Colors.GREY_100), bottom=ft.BorderSide(1, ft.Colors.GREY_100), left=ft.BorderSide(1, ft.Colors.GREY_100)),
        )
    
    def _build_repair_row(self, repair):
        """Build recent repair row"""
        repair_id = repair.get('id')
        job_no = repair.get('job_no', '-')
        status = repair.get('status', 'pending')
        mechanic_name = repair.get('mechanic_name', '-')
        
        status_colors = {
            'working': ("#2196F3", get_text("working")),
            'completed': ("#4CAF50", get_text("completed")),
            'pending': ("#FF9800", get_text("pending")),
        }
        status_color, status_text = status_colors.get(status, ("#64748B", status.capitalize() if status else '-'))
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.CONSTRUCTION, size=20, color=self.primary_color),
                        width=40,
                        height=40,
                        bgcolor=self.primary_light,
                        border_radius=10,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Column(
                        [
                            ft.Text(f"{get_text('repair_no')}: #{repair_id}", size=14, weight=ft.FontWeight.W_500, color="#1E293B"),
                            ft.Text(f"{get_text('job_number')}: {job_no} | {get_text('mechanic')}: {mechanic_name}", size=11, color="#64748B"),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(status_text, size=11, color=status_color),
                        bgcolor=ft.Colors.with_opacity(0.1, status_color),
                        border_radius=12,
                        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100), right=ft.BorderSide(1, ft.Colors.GREY_100), bottom=ft.BorderSide(1, ft.Colors.GREY_100), left=ft.BorderSide(1, ft.Colors.GREY_100)),
        )