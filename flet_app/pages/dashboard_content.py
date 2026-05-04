# pages/dashboard_content.py
import flet as ft
from i18n import get_text

class DashboardContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.search_field = None
        self.employees_table = None
        self.current_page = 1
        self.rows_per_page = 10
        self.total_employees = 0
        self.all_employees = []
        
        # Statistics data
        self.total_services = 0
        self.total_parts = 0
        self.low_stock_count = 0
        self.total_suppliers = 0

    def build(self):
        # Create search field
        self.search_field = ft.TextField(
            hint_text=get_text("search_employees"),
            border_color=ft.Colors.TRANSPARENT,
            bgcolor=ft.Colors.WHITE,
            width=300,
            height=45,
            content_padding=ft.padding.all(12),
            on_change=self.on_search,
            prefix_icon=ft.Icons.SEARCH,
        )
        
        # Load all real data
        self.load_all_data()
        
        # ===== Header with Search =====
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("dashboard_title"),
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color="#0D47A1",
                            ),
                            
                        ],
                        spacing=5,
                    ),
                    ft.Container(expand=True),
                    # Search Field
                    ft.Container(
                        content=self.search_field,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=30,
                        shadow=ft.BoxShadow(
                            blur_radius=10,
                            spread_radius=1,
                            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                            offset=ft.Offset(0, 2),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=20),
        )

        # ===== Statistics Cards with Real Data =====
        stats_row = ft.Row(
            [
                self._build_modern_stat_card(
                    ft.Icons.PEOPLE_OUTLINE,
                    get_text("total_staff"),
                    str(self.total_employees),
                    "#0D47A1",
                    "employees",
                ),
                self._build_modern_stat_card(
                    ft.Icons.BUILD,
                    get_text("active_services"),
                    str(self.total_services),
                    "#FF9800",
                    "services",
                ),
                self._build_modern_stat_card(
                    ft.Icons.PRECISION_MANUFACTURING,
                    get_text("total_parts"),
                    str(self.total_parts),
                    "#4CAF50",
                    "parts",
                ),
                self._build_modern_stat_card(
                    ft.Icons.WARNING_AMBER,
                    get_text("low_stock_alerts"),
                    str(self.low_stock_count),
                    "#F44336",
                    "alerts",
                ),
                self._build_modern_stat_card(
                    ft.Icons.LOCAL_SHIPPING,
                    get_text("total_suppliers"),
                    str(self.total_suppliers),
                    "#9C27B0",
                    "suppliers",
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=15,
            wrap=True,
        )

        # ===== Employees Table with Modern Design =====
        self.employees_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD, size=14)),
                ft.DataColumn(ft.Text(get_text("name"), weight=ft.FontWeight.BOLD, size=14)),
                ft.DataColumn(ft.Text(get_text("username"), weight=ft.FontWeight.BOLD, size=14)),
                ft.DataColumn(ft.Text(get_text("role"), weight=ft.FontWeight.BOLD, size=14)),
                ft.DataColumn(ft.Text(get_text("phone"), weight=ft.FontWeight.BOLD, size=14)),
                ft.DataColumn(ft.Text(get_text("status"), weight=ft.FontWeight.BOLD, size=14)),
                ft.DataColumn(ft.Text(get_text("action"), weight=ft.FontWeight.BOLD, size=14)),
            ],
            rows=[],
            heading_row_color=ft.Colors.with_opacity(0.08, "#0D47A1"),
            heading_text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD, color="#0D47A1"),
            data_row_color={
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.05, "#0D47A1"),
                ft.ControlState.DEFAULT: ft.Colors.WHITE,
            },
            border_radius=12,
            horizontal_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            vertical_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.05, ft.Colors.BLACK)),
            divider_thickness=0,
            column_spacing=20,
        )

        # ===== Pagination =====
        pagination = self._build_pagination()

        # ===== Table Container with Glassmorphism =====
        table_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        get_text("staff_profiles"),
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1A1A1A",
                                    ),
                                    ft.Text(
                                        get_text("staff_description"),
                                        size=13,
                                        color=ft.Colors.GREY_600,
                                    ),
                                ],
                                spacing=5,
                            ),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.REFRESH, size=18, color=ft.Colors.BLUE_700),
                                        ft.Text("Refresh", size=13, color=ft.Colors.BLUE_700),
                                    ],
                                    spacing=5,
                                ),
                                on_click=lambda e: self.load_all_data(),
                                ink=True,
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                                bgcolor=ft.Colors.with_opacity(0.1, "#0D47A1"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_200),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=self.employees_table,
                                    height=500,
                                ),
                                pagination,
                            ],
                            spacing=20,
                        ),
                        padding=ft.padding.only(top=15),
                    ),
                ],
                spacing=15,
            ),
            padding=ft.padding.all(25),
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.WHITE),
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=2,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 5),
            ),
        )

        # ===== Main Layout =====
        return ft.Container(
            content=ft.Column(
                [
                    header,
                    stats_row,
                    ft.Container(height=15),
                    table_container,
                ],
                spacing=20,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.all(25),
            expand=True,
            bgcolor=ft.Colors.TRANSPARENT,
        )

    def load_all_data(self):
        """Load all real data from API"""
        try:
            # Load employees
            self.all_employees = self.client.get_employees()
            self.total_employees = len(self.all_employees)
            
            # Load services
            services = self.client.get_services()
            self.total_services = len(services)
            
            # Load parts
            parts = self.client.get_parts()
            self.total_parts = len(parts)
            self.low_stock_count = len([p for p in parts if p.get('stock_quantity', 0) < p.get('min_stock', 5)])
            
            # Load suppliers
            suppliers = self.client.get_suppliers()
            self.total_suppliers = len(suppliers)
            
            # Update table
            self.current_page = 1
            self.update_table()
            
            self.show_snackbar(f"✅ Data loaded: {self.total_employees} employees")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            self.show_snackbar(f"⚠️ Error loading data: {e}")
            self.all_employees = []
            self.total_employees = 0
            self.total_services = 0
            self.total_parts = 0
            self.low_stock_count = 0
            self.total_suppliers = 0
            self.update_table()

    def update_table(self):
        """Update table with current page and search filter"""
        if not self.employees_table:
            return
        
        # Filter employees based on search
        search_term = self.search_field.value.lower() if self.search_field and self.search_field.value else ""
        filtered_employees = self.all_employees
        if search_term:
            filtered_employees = [
                e for e in self.all_employees 
                if search_term in e.get('fullname', '').lower() 
                or search_term in e.get('username', '').lower()
                or search_term in e.get('phone', '').lower()
                or search_term in self._get_role_text(e.get('role', '')).lower()
            ]
        
        # Pagination
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_employees = filtered_employees[start_idx:end_idx]
        
        # Clear and rebuild rows
        self.employees_table.rows.clear()
        
        for idx, emp in enumerate(page_employees):
            row_num = start_idx + idx + 1
            status = emp.get('status', 'active')
            status_color = ft.Colors.GREEN_700 if status == 'active' else ft.Colors.ORANGE_700
            status_text = "Active" if status == 'active' else "Inactive"
            
            self.employees_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row_num), size=13, color=ft.Colors.GREY_600)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(emp.get('fullname', '-')[:2].upper(), 
                                                      size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        width=40,
                                        height=40,
                                        alignment=ft.alignment.center,
                                        border_radius=25,
                                        bgcolor="#0D47A1",
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(emp.get('fullname', '-'), weight=ft.FontWeight.W_600, size=14),
                                            ft.Text(emp.get('email', '-') or 'No email', size=11, color=ft.Colors.GREY_500),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=10,
                            )
                        ),
                        ft.DataCell(ft.Text(emp.get('username', '-'), size=13)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(self._get_role_text(emp.get('role', '-')), size=12),
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                border_radius=15,
                                bgcolor=ft.Colors.with_opacity(0.1, self._get_role_color(emp.get('role', '-'))),
                                color=self._get_role_color(emp.get('role', '-')),
                            )
                        ),
                        ft.DataCell(ft.Text(emp.get('phone', '-'), size=13)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(status_text, size=12, color=status_color),
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                border_radius=20,
                                bgcolor=ft.Colors.with_opacity(0.1, status_color),
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.EDIT_OUTLINE,
                                        icon_color=ft.Colors.BLUE_700,
                                        icon_size=20,
                                        tooltip="Edit",
                                        on_click=lambda e, eid=emp.get('id'): self.edit_employee(eid),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_700,
                                        icon_size=20,
                                        tooltip="Delete",
                                        on_click=lambda e, eid=emp.get('id'): self.delete_employee(eid),
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ],
                )
            )
        
        # Update pagination info
        total_pages = (len(filtered_employees) + self.rows_per_page - 1) // self.rows_per_page if filtered_employees else 1
        self.update_pagination(total_pages, len(filtered_employees))
        self.page.update()

    def _build_modern_stat_card(self, icon, title, value, color, data_type):
        """Modern statistics card with real data"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon, size=28, color=color),
                                bgcolor=ft.Colors.with_opacity(0.1, color),
                                border_radius=12,
                                padding=ft.padding.all(10),
                            ),
                            ft.Container(expand=True),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color="#1A1A1A"),
                    ft.Text(title, size=13, color=ft.Colors.GREY_600),
                ],
                spacing=12,
            ),
            padding=ft.padding.all(20),
            width=200,
            height=130,
            border_radius=16,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                blur_radius=12,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 3),
            ),
        )

    def _build_pagination(self):
        """Build pagination controls"""
        self.pagination_container = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            )
        )
        return self.pagination_container

    def update_pagination(self, total_pages, total_items):
        """Update pagination controls"""
        if not hasattr(self, 'pagination_container'):
            return
        
        self.pagination_container.content.controls.clear()
        
        if total_items == 0:
            return
        
        # Info text
        start = (self.current_page - 1) * self.rows_per_page + 1
        end = min(start + self.rows_per_page - 1, total_items)
        
        info_text = ft.Text(
            f"Showing {start}-{end} of {total_items} results",
            size=13,
            color=ft.Colors.GREY_600,
        )
        
        # Previous button
        prev_btn = ft.IconButton(
            ft.Icons.CHEVRON_LEFT,
            icon_size=20,
            on_click=lambda e: self.go_to_page(self.current_page - 1),
            disabled=self.current_page <= 1,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )
        
        # Page buttons
        page_btns = []
        max_buttons = 5
        start_page = max(1, self.current_page - max_buttons // 2)
        end_page = min(total_pages, start_page + max_buttons - 1)
        
        if end_page - start_page + 1 < max_buttons and start_page > 1:
            start_page = max(1, end_page - max_buttons + 1)
        
        for i in range(start_page, end_page + 1):
            page_btns.append(
                ft.Container(
                    content=ft.Text(str(i), size=14, weight=ft.FontWeight.W_600),
                    width=40,
                    height=40,
                    alignment=ft.alignment.center,
                    border_radius=10,
                    bgcolor=ft.Colors.BLUE_700 if i == self.current_page else ft.Colors.TRANSPARENT,
                    color=ft.Colors.WHITE if i == self.current_page else ft.Colors.GREY_700,
                    on_click=lambda e, p=i: self.go_to_page(p),
                    ink=True,
                )
            )
        
        # Next button
        next_btn = ft.IconButton(
            ft.Icons.CHEVRON_RIGHT,
            icon_size=20,
            on_click=lambda e: self.go_to_page(self.current_page + 1),
            disabled=self.current_page >= total_pages,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )
        
        self.pagination_container.content.controls.extend([info_text, prev_btn] + page_btns + [next_btn])
        self.page.update()

    def go_to_page(self, page):
        """Go to specific page"""
        if page < 1:
            return
        self.current_page = page
        self.update_table()

    def on_search(self, e):
        """Handle search input"""
        self.current_page = 1
        self.update_table()

    def edit_employee(self, emp_id):
        """Edit employee"""
        from Management.employees_content import EmployeesContent
        emp_content = EmployeesContent(self.page, self.client, self.user, self.navigate)
        emp_content.edit_employee(emp_id)

    def delete_employee(self, emp_id):
        """Delete employee"""
        from Management.employees_content import EmployeesContent
        emp_content = EmployeesContent(self.page, self.client, self.user, self.navigate)
        emp_content.delete_employee(emp_id)

    def _get_role_text(self, role):
        """Convert role code to text"""
        roles = {
            'admin': 'Admin',
            'technician': 'Technician',
            'reception': 'Receptionist',
            'manager': 'Manager',
        }
        return roles.get(role, role)

    def _get_role_color(self, role):
        """Get color for role badge"""
        colors = {
            'admin': "#0D47A1",
            'technician': "#FF9800",
            'reception': "#4CAF50",
            'manager': "#9C27B0",
        }
        return colors.get(role, "#757575")

    def show_snackbar(self, message):
        """Show snackbar message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.GREY_800,
            duration=3000,
        )
        self.page.update()