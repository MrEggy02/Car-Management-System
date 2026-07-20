# pages/suppliers_page.py
import flet as ft
import sys
import os
import asyncio
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import get_text

# Constants
PRIMARY_COLOR = "#1565C0"
PRIMARY_DARK = "#0D47A1"
WARNING_COLOR = "#DC2626"
PHONE_MAX_LENGTH = 20
EMAIL_MAX_LENGTH = 100

class SuppliersContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.is_loading = False
        self.current_dialog = None
        self.current_snackbar = None
        self.suppliers_data = []
        self.filtered_suppliers = []
        self.search_input = None
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.primary_color = PRIMARY_COLOR
        self.primary_dark = PRIMARY_DARK
        
        # Table data rows container
        self.table_rows = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        self.pagination_container = ft.Container()
    
    def build(self):
        """Build suppliers management content with table layout"""
        
        # Beautiful gradient header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("suppliers_title"), 
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
        
        # Search Bar
        self.search_input = ft.TextField(
            hint_text=f"{get_text('search')} {get_text('suppliers_title')}...",
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            expand=True,
            on_change=self.filter_suppliers,
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
        
        table_header = self._create_table_header()
        
        table_scroll_container = ft.Container(
            content=self.table_rows,
            expand=True,
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            bgcolor=ft.Colors.WHITE,
        )
        
        table_container = ft.Container(
            content=ft.Column([
                table_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                table_scroll_container,
            ], spacing=0),
            margin=ft.Margin(left=20, right=20, top=0, bottom=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(
                top_left=12, top_right=12, bottom_left=12, bottom_right=12
            ),
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            expand=True,
        )
        
        self.pagination_container = ft.Container(
            padding=ft.Padding(left=20, right=20, top=16, bottom=16),
            bgcolor="#F5F7FA",
        )
        
        main_content = ft.Container(
            content=ft.Column([
                table_container,
                self.pagination_container,
            ], spacing=0),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        main_container = ft.Container(
            content=main_content,
            expand=True,
        )
        
        self.page.run_task(self._delayed_load)
        
        return ft.Column([
            header,
            control_bar,
            main_container,
        ], expand=True, spacing=0)
    
    def _create_table_header(self):
        """Create table header row"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("#", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=50,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('suppliers_name'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=160,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text('contact_person'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=140,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text('suppliers_phone'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=130,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(get_text('suppliers_email'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=180,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(get_text('actions'), size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=14, bottom=14),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.BorderRadius.only(top_left=12, top_right=12),
        )
    
    def _create_table_row(self, sup, index, row_number):
        """Create a single table row"""
        sup_id = sup.get('id')
        name = sup.get('name', '-')
        contact_person = sup.get('contact_person', '-')
        phone = sup.get('phone', '-')
        email = sup.get('email', '-')
        address = sup.get('address', '-')
        
        row_bg = ft.Colors.GREY_50 if index % 2 == 0 else ft.Colors.WHITE
        
        contact_display = contact_person if contact_person != '-' else "-"
        contact_color = ft.Colors.GREY_700 if contact_person != '-' else ft.Colors.GREY_400
        
        phone_display = phone if phone != '-' else "-"
        phone_color = ft.Colors.GREEN_700 if phone != '-' else ft.Colors.GREY_400
        
        email_display = email if email != '-' else "-"
        email_color = ft.Colors.BLUE_600 if email != '-' else ft.Colors.GREY_400
        
        edit_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=PRIMARY_COLOR),
                ft.Text(get_text("edit"), size=12, color=PRIMARY_COLOR),
            ], spacing=4),
            on_click=lambda e, sid=sup_id: self._safe_edit(sid, e),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
            tooltip=get_text("edit"),
        )
        
        delete_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_600),
                ft.Text(get_text("delete"), size=12, color=ft.Colors.RED_600),
            ], spacing=4),
            on_click=lambda e, sid=sup_id: self._safe_delete(sid, e),
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=6,
            tooltip=get_text("delete"),
        )
        
        name_column = ft.Column([
            ft.Text(name, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK, max_lines=1),
        ], spacing=1)
        
        if address and address != '-':
            short_address = address if len(address) <= 30 else address[:27] + "..."
            name_column.controls.append(
                ft.Text(short_address, size=10, color=ft.Colors.GREY_500, max_lines=1)
            )
            name_column.tooltip = address
        
        row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Container(
                        content=ft.Text(str(row_number), size=13, weight=ft.FontWeight.W_500, color=PRIMARY_COLOR),
                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=6,
                        alignment=ft.Alignment(0, 0),
                    ),
                    width=50,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=name_column,
                    width=160,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(contact_display, size=12, color=contact_color, max_lines=1),
                    width=140,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Text(phone_display, size=12, color=phone_color, max_lines=1),
                    width=130,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Text(email_display, size=11, color=email_color, max_lines=1),
                    width=180,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(left=10, right=0, top=0, bottom=0),
                ),
                ft.Container(
                    content=ft.Row([edit_btn, delete_btn], spacing=4),
                    width=120,
                    alignment=ft.Alignment(0, 0),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            bgcolor=row_bg,
        )
        
        return ft.Column([
            row,
            ft.Divider(height=1, color=ft.Colors.GREY_200),
        ], spacing=0)
    
    def _create_empty_state(self):
        """Create empty state when no data"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOCAL_SHIPPING, size=64, color=ft.Colors.GREY_300),
                ft.Container(height=10),
                ft.Text(get_text("no_data"), size=16, color=ft.Colors.GREY_500),
                ft.Text(get_text("click_add"), size=13, color=ft.Colors.GREY_400),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.Alignment(0, 0)),
            padding=ft.Padding(left=40, right=40, top=40, bottom=40),
            expand=True,
        )
    
    def update_pagination(self):
        """Update pagination controls"""
        if not self.filtered_suppliers:
            self.total_pages = 1
        else:
            self.total_pages = max(1, (len(self.filtered_suppliers) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1
        
        prev_disabled = self.current_page <= 1
        next_disabled = self.current_page >= self.total_pages
        
        self.pagination_container.content = ft.Row([
            ft.Text(f"{get_text('showing')} {len(self.filtered_suppliers)} {get_text('of')} {len(self.suppliers_data)} {get_text('results')}", size=12, color="#64748B"),
            ft.Container(expand=True),
            ft.Container(
                content=ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_LEFT,
                        icon_size=20,
                        on_click=self.prev_page,
                        disabled=prev_disabled,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
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
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    ),
                ]),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            ),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.page.update()
    
    def prev_page(self, e=None):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_suppliers(self.filtered_suppliers)
    
    def next_page(self, e=None):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_suppliers(self.filtered_suppliers)
    
    def filter_suppliers(self, e=None):
        query = self.search_input.value.lower() if self.search_input.value else ""
        self.current_page = 1
        
        if not query:
            self.filtered_suppliers = self.suppliers_data.copy()
        else:
            self.filtered_suppliers = [
                sup for sup in self.suppliers_data
                if query in sup.get('name', '').lower()
                or query in sup.get('contact_person', '').lower()
                or query in sup.get('phone', '').lower()
                or query in sup.get('email', '').lower()
            ]
        
        self.display_suppliers(self.filtered_suppliers)
    
    def display_suppliers(self, suppliers):
        self.table_rows.controls.clear()
        
        if not suppliers:
            self.table_rows.controls.append(self._create_empty_state())
        else:
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_suppliers = suppliers[start_idx:end_idx]
            
            global_start = start_idx + 1
            
            for i, sup in enumerate(page_suppliers):
                row_number = global_start + i
                row = self._create_table_row(sup, start_idx + i, row_number)
                self.table_rows.controls.append(row)
        
        self.update_pagination()
        self.page.update()
    
    async def _delayed_load(self):
        await asyncio.sleep(0.2)
        await asyncio.to_thread(self.load_data)
    
    def load_data(self):
        if self.is_loading:
            return
        self.is_loading = True
        
        try:
            print("DEBUG: Loading suppliers data...")
            self.suppliers_data = self.client.get_suppliers()
            self.filtered_suppliers = self.suppliers_data.copy()
            print(f"DEBUG: Loaded {len(self.suppliers_data)} suppliers")
            
            self.display_suppliers(self.filtered_suppliers)
            
        except Exception as e:
            print(f"DEBUG: Error loading suppliers: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
        finally:
            self.is_loading = False
    
    def _safe_edit(self, sup_id, event):
        try:
            self.edit_supplier(sup_id)
        except Exception as e:
            print(f"DEBUG: Error in edit: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
    
    def _safe_delete(self, sup_id, event):
        try:
            self.delete_supplier(sup_id)
        except Exception as e:
            print(f"DEBUG: Error in delete: {e}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {e}", "error")
    
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
        """Add supplier dialog with validation"""
        
        # Error labels
        name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        phone_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        email_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        
        # Phone hint
        phone_hint = ft.Text(
            f"ສາມາດປ້ອນໄດ້ສູງສຸດ {PHONE_MAX_LENGTH} ຕົວ",
            size=10,
            color=ft.Colors.GREY_500,
        )
        
        # Email hint
        email_hint = ft.Text(
            "ຕົວຢ່າງ: example@domain.com",
            size=10,
            color=ft.Colors.GREY_500,
        )
        
        def on_phone_change(e):
            if phone.value:
                cleaned = ''.join(filter(str.isdigit, phone.value))
                if len(cleaned) > PHONE_MAX_LENGTH:
                    self.show_snackbar(f"ເກີນ {PHONE_MAX_LENGTH} ຕົວ", "error")
                    cleaned = cleaned[:PHONE_MAX_LENGTH]
                phone.value = cleaned
                phone.update()
            if phone.value and len(phone.value) <= PHONE_MAX_LENGTH:
                phone_error.visible = False
                phone_error.update()
        
        def validate_email(email_val):
            if not email_val:
                return True
            if '@' not in email_val or '.' not in email_val:
                return False
            return True
        
        name = ft.TextField(
            label=f"{get_text('suppliers_name')} *",
            hint_text=get_text("suppliers_name_hint"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
        )
        
        contact = ft.TextField(
            label=get_text("contact_person"),
            hint_text=get_text("contact_person_hint"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
        )
        
        phone = ft.TextField(
            label=get_text("suppliers_phone"),
            hint_text="020xxxxxxxx",
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
            on_change=on_phone_change,
        )
        
        email = ft.TextField(
            label=get_text("suppliers_email"),
            hint_text="example@domain.com",
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
        )
        
        address = ft.TextField(
            label=get_text("suppliers_address"),
            hint_text=get_text("address_hint"),
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=56,
        )
        
        def validate_fields():
            is_valid = True
            
            # Validate Name
            if not name.value or not name.value.strip():
                name_error.value = get_text("please_enter_name")
                name_error.visible = True
                is_valid = False
            else:
                name_error.visible = False
            
            # Validate Phone
            if phone.value and phone.value.strip():
                phone_clean = phone.value.strip().replace(" ", "")
                if not phone_clean.isdigit():
                    phone_error.value = get_text("phone_must_be_number")
                    phone_error.visible = True
                    is_valid = False
                elif len(phone_clean) > PHONE_MAX_LENGTH:
                    phone_error.value = f"ເບີໂທລະສັບຕ້ອງບໍ່ເກີນ {PHONE_MAX_LENGTH} ຕົວ"
                    phone_error.visible = True
                    is_valid = False
                else:
                    phone_error.visible = False
            else:
                phone_error.visible = False
            
            # Validate Email
            if email.value and email.value.strip():
                if not validate_email(email.value.strip()):
                    email_error.value = get_text("email_invalid")
                    email_error.visible = True
                    is_valid = False
                elif len(email.value.strip()) > EMAIL_MAX_LENGTH:
                    email_error.value = f"ອີເມວຍາວເກີນ {EMAIL_MAX_LENGTH} ຕົວ"
                    email_error.visible = True
                    is_valid = False
                else:
                    email_error.visible = False
            else:
                email_error.visible = False
            
            # Update UI
            name.update()
            phone.update()
            email.update()
            name_error.update()
            phone_error.update()
            email_error.update()
            
            return is_valid
        
        def save(e):
            if not validate_fields():
                return
            
            if name.value:
                try:
                    self.client.add_supplier(
                        name.value.strip(),
                        contact.value.strip() if contact.value else "",
                        phone.value.strip() if phone.value else "",
                        email.value.strip() if email.value else "",
                        address.value.strip() if address.value else ""
                    )
                    self._close_dialog()
                    self.load_data()
                    self.show_snackbar(get_text("add_success"), "success")
                except Exception as err:
                    print(f"Error saving: {err}")
                    traceback.print_exc()
                    self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.LOCAL_SHIPPING, size=18, color=ft.Colors.WHITE),
                            bgcolor=PRIMARY_COLOR,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text("suppliers_add"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    # Name
                    ft.Column([
                        name,
                        name_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    # Contact
                    contact,
                    ft.Container(height=4),
                    # Phone
                    ft.Column([
                        phone,
                        phone_hint,
                        phone_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    # Email
                    ft.Column([
                        email,
                        email_hint,
                        email_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    # Address
                    address,
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
                padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                width=360,
                height=270,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B", size=13),
                            on_click=self._close_dialog,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), color=ft.Colors.WHITE, size=13),
                            on_click=save,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY_COLOR,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                                padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                            ),
                        ),
                    ], spacing=6, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def edit_supplier(self, sup_id):
        sup = None
        for s in self.suppliers_data:
            if s.get('id') == sup_id:
                sup = s
                break
        
        if not sup:
            self.show_snackbar(get_text("error"), "error")
            return
        
        # Error labels
        name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        phone_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        email_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        
        # Phone hint
        phone_hint = ft.Text(
            f"ສາມາດປ້ອນໄດ້ສູງສຸດ {PHONE_MAX_LENGTH} ຕົວ",
            size=10,
            color=ft.Colors.GREY_500,
        )
        
        # Email hint
        email_hint = ft.Text(
            "ຕົວຢ່າງ: example@domain.com",
            size=10,
            color=ft.Colors.GREY_500,
        )
        
        def on_phone_change(e):
            if phone.value:
                cleaned = ''.join(filter(str.isdigit, phone.value))
                if len(cleaned) > PHONE_MAX_LENGTH:
                    self.show_snackbar(f"ເກີນ {PHONE_MAX_LENGTH} ຕົວ", "error")
                    cleaned = cleaned[:PHONE_MAX_LENGTH]
                phone.value = cleaned
                phone.update()
            if phone.value and len(phone.value) <= PHONE_MAX_LENGTH:
                phone_error.visible = False
                phone_error.update()
        
        def validate_email(email_val):
            if not email_val:
                return True
            if '@' not in email_val or '.' not in email_val:
                return False
            return True
        
        name = ft.TextField(
            label=f"{get_text('suppliers_name')} *",
            value=sup.get('name', ''),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
        )
        
        contact = ft.TextField(
            label=get_text("contact_person"),
            value=sup.get('contact_person', ''),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
        )
        
        phone = ft.TextField(
            label=get_text("suppliers_phone"),
            value=sup.get('phone', ''),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
            on_change=on_phone_change,
        )
        
        email = ft.TextField(
            label=get_text("suppliers_email"),
            value=sup.get('email', ''),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=38,
        )
        
        address = ft.TextField(
            label=get_text("suppliers_address"),
            value=sup.get('address', ''),
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=PRIMARY_COLOR,
            expand=True,
            height=56,
        )
        
        def validate_fields():
            is_valid = True
            
            # Validate Name
            if not name.value or not name.value.strip():
                name_error.value = get_text("please_enter_name")
                name_error.visible = True
                is_valid = False
            else:
                name_error.visible = False
            
            # Validate Phone
            if phone.value and phone.value.strip():
                phone_clean = phone.value.strip().replace(" ", "")
                if not phone_clean.isdigit():
                    phone_error.value = get_text("phone_must_be_number")
                    phone_error.visible = True
                    is_valid = False
                elif len(phone_clean) > PHONE_MAX_LENGTH:
                    phone_error.value = f"ເບີໂທລະສັບຕ້ອງບໍ່ເກີນ {PHONE_MAX_LENGTH} ຕົວ"
                    phone_error.visible = True
                    is_valid = False
                else:
                    phone_error.visible = False
            else:
                phone_error.visible = False
            
            # Validate Email
            if email.value and email.value.strip():
                if not validate_email(email.value.strip()):
                    email_error.value = get_text("email_invalid")
                    email_error.visible = True
                    is_valid = False
                elif len(email.value.strip()) > EMAIL_MAX_LENGTH:
                    email_error.value = f"ອີເມວຍາວເກີນ {EMAIL_MAX_LENGTH} ຕົວ"
                    email_error.visible = True
                    is_valid = False
                else:
                    email_error.visible = False
            else:
                email_error.visible = False
            
            # Update UI
            name.update()
            phone.update()
            email.update()
            name_error.update()
            phone_error.update()
            email_error.update()
            
            return is_valid
        
        def save_edit(e):
            if not validate_fields():
                return
            
            if name.value:
                try:
                    self.client.update_supplier(
                        sup_id,
                        name.value.strip(),
                        contact.value.strip() if contact.value else "",
                        phone.value.strip() if phone.value else "",
                        email.value.strip() if email.value else "",
                        address.value.strip() if address.value else ""
                    )
                    self._close_dialog()
                    self.load_data()
                    self.show_snackbar(get_text("edit_success"), "success")
                except Exception as err:
                    print(f"Error in save_edit: {err}")
                    traceback.print_exc()
                    self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=18, color=ft.Colors.WHITE),
                            bgcolor=PRIMARY_COLOR,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text("suppliers_edit"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    # Name
                    ft.Column([
                        name,
                        name_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    # Contact
                    contact,
                    ft.Container(height=4),
                    # Phone
                    ft.Column([
                        phone,
                        phone_hint,
                        phone_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    # Email
                    ft.Column([
                        email,
                        email_hint,
                        email_error,
                    ], spacing=1),
                    ft.Container(height=4),
                    # Address
                    address,
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
                padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                width=360,
                height=274,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B", size=13),
                            on_click=self._close_dialog,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("save"), color=ft.Colors.WHITE, size=13),
                            on_click=save_edit,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY_COLOR,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                                padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                            ),
                        ),
                    ], spacing=6, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def delete_supplier(self, sup_id):
        sup = None
        for s in self.suppliers_data:
            if s.get('id') == sup_id:
                sup = s
                break
        
        sup_name = sup.get('name', get_text('this_supplier')) if sup else get_text('this_supplier')
        
        def confirm(e):
            try:
                self.client.delete_supplier(sup_id)
                self._close_dialog()
                self.load_data()
                self.show_snackbar(get_text("delete_success"), "success")
            except Exception as err:
                print(f"Error in delete: {err}")
                traceback.print_exc()
                self.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, size=18, color=ft.Colors.WHITE),
                            bgcolor=WARNING_COLOR,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text("confirm"), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, size=32, color=WARNING_COLOR),
                    ft.Container(height=4),
                    ft.Text(
                        f"ຕ້ອງການລຶບ '{sup_name}' ຫຼື ບໍ່?",
                        size=14,
                        weight=ft.FontWeight.W_500,
                        color="#1E293B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        get_text("delete_warning"),
                        size=12,
                        color="#64748B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                width=280,
                height=150,
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            content=ft.Text(get_text("cancel"), color="#64748B", size=13),
                            on_click=self._close_dialog,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(get_text("delete"), color=ft.Colors.WHITE, size=13),
                            on_click=confirm,
                            style=ft.ButtonStyle(
                                bgcolor=WARNING_COLOR,
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                                padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                            ),
                        ),
                    ], spacing=6, alignment=ft.MainAxisAlignment.END),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
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
                    ft.Icon(icon, color=ft.Colors.WHITE, size=16),
                    ft.Text(message, color=ft.Colors.WHITE, size=13, weight=ft.FontWeight.W_500),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, right=14, top=8, bottom=8),
            bgcolor=bgcolor,
            border_radius=8,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            ),
        )
        
        # Create overlay container - positioned at bottom center
        snackbar = ft.Container(
            content=snack_content,
            margin=ft.Margin(left=30, right=30, top=0, bottom=20),
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