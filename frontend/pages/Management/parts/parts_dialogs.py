# Management/parts/parts_dialogs.py
import flet as ft
import traceback
from i18n import get_text


class PartsDialogs:
    def __init__(self, parent):
        self.parent = parent
        self.current_dialog = None
        self.search_unit_field = None
        self.search_category_field = None
        self.search_supplier_field = None
        self.filtered_units = []
        self.filtered_categories = []
        self.filtered_suppliers = []
        
    def create_searchable_dropdown(self, label, hint_text, items, value=None, on_change=None):
        """Create a searchable dropdown with text field for typing search"""
        
        # Store all items
        all_items = items.copy()
        
        # Selected value
        selected_id = [value]
        selected_name = [""]
        
        # Track if dropdown is visible
        is_dropdown_visible = [False]
        
        # Find selected name if value exists
        if value:
            for item in all_items:
                if str(item.get('id')) == str(value):
                    selected_name[0] = item.get('name', '')
                    break
        
        # TextField for search input and display
        text_field = ft.TextField(
            label=label,
            hint_text=hint_text,
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            prefix_icon=ft.Icons.SEARCH,
            suffix_icon=ft.Icons.ARROW_DROP_DOWN,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            value=selected_name[0] if selected_name[0] else "",
            height=38,
            text_size=12,
            on_change=lambda e: on_search_change(e),
            on_focus=lambda e: show_dropdown(),
            on_blur=lambda e: hide_dropdown_delayed(),
        )
        
        # Dropdown list container
        list_column = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO, height=150)
        list_container = ft.Container(
            content=list_column,
            border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_200), right=ft.BorderSide(1, ft.Colors.GREY_200), bottom=ft.BorderSide(1, ft.Colors.GREY_200), left=ft.BorderSide(1, ft.Colors.GREY_200)),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            padding=ft.Padding(left=4, right=4, top=4, bottom=4),
            visible=False,
            margin=ft.Margin(left=0, right=0, top=2, bottom=0),
        )
        
        # Current filtered items
        current_filtered = all_items.copy()
        
        def on_search_change(e):
            """Filter items based on search text"""
            query = text_field.value.lower() if text_field.value else ""
            current_filtered.clear()
            
            if not query:
                current_filtered.extend(all_items)
            else:
                for item in all_items:
                    name = item.get('name', '').lower()
                    if query in name:
                        current_filtered.append(item)
            
            update_list()
            # Show dropdown if there are results and dropdown was visible
            if current_filtered and is_dropdown_visible[0]:
                list_container.visible = True
            self.parent.page.update()
        
        def show_dropdown():
            """Show dropdown list"""
            is_dropdown_visible[0] = True
            if current_filtered:
                update_list()
                list_container.visible = True
            self.parent.page.update()
        
        def hide_dropdown_delayed():
            """Hide dropdown list with small delay to allow selection"""
            import asyncio
            async def delayed_hide():
                await asyncio.sleep(0.2)
                if is_dropdown_visible[0]:
                    is_dropdown_visible[0] = False
                    list_container.visible = False
                    self.parent.page.update()
            
            async def run():
                await delayed_hide()
            
            asyncio.create_task(run())
        
        def update_list():
            """Update the dropdown list with filtered items"""
            list_column.controls.clear()
            
            if not current_filtered:
                list_column.controls.append(
                    ft.Container(
                        content=ft.Text(get_text("no_items_found"), size=12, color="#94A3B8"),
                        padding=ft.Padding(left=12, right=12, top=12, bottom=12),
                        alignment=ft.Alignment(0, 0),
                    )
                )
            else:
                for item in current_filtered[:20]:  # Limit to 20 items for performance
                    item_id = item.get('id')
                    item_name = item.get('name', '-')
                    
                    # Highlight if this item is selected
                    is_selected = (selected_id[0] is not None and str(item_id) == str(selected_id[0]))
                    
                    btn = ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE if is_selected else ft.Icons.CIRCLE_OUTLINED, size=16, color=self.parent.primary_color if is_selected else ft.Colors.GREY_400),
                            ft.Text(item_name, size=13, color="#1E293B", expand=True),
                        ], spacing=10),
                        padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                        border_radius=6,
                        bgcolor=ft.Colors.BLUE_50 if is_selected else ft.Colors.TRANSPARENT,
                        ink=True,
                        on_click=lambda e, iid=item_id, iname=item_name: select_item(iid, iname),
                    )
                    list_column.controls.append(btn)
        
        def select_item(item_id, item_name):
            """Select an item from dropdown"""
            selected_id[0] = item_id
            selected_name[0] = item_name
            text_field.value = item_name
            text_field.error_text = None
            is_dropdown_visible[0] = False
            list_container.visible = False
            
            if on_change:
                on_change(selected_id[0], selected_name[0])
            
            self.parent.page.update()
        
        # Create main container
        container = ft.Container(
            content=ft.Stack([
                ft.Column([
                    text_field,
                    list_container,
                ], spacing=0),
            ]),
        )
        
        # Store references for external access
        container.text_field = text_field
        container.list_container = list_container
        container.select_item = select_item
        container.get_selected_id = lambda: selected_id[0]
        container.get_selected_name = lambda: selected_name[0]
        
        return container, text_field
    
    def show_add_dialog(self, units, categories, suppliers):
        """Show add part dialog with searchable dropdowns"""
        
        selected_unit_id = [None]
        selected_unit_name = [None]
        selected_category_id = [None]
        selected_category_name = [None]
        selected_supplier_id = [None]
        selected_supplier_name = [None]
        
        def on_unit_selected(item_id, item_name):
            selected_unit_id[0] = item_id
            selected_unit_name[0] = item_name
        
        def on_category_selected(item_id, item_name):
            selected_category_id[0] = item_id
            selected_category_name[0] = item_name
        
        def on_supplier_selected(item_id, item_name):
            selected_supplier_id[0] = item_id
            selected_supplier_name[0] = item_name
        
        # Create searchable dropdowns
        unit_container, unit_field = self.create_searchable_dropdown(
            get_text("unit"), 
            get_text("select_unit_hint"),
            units, 
            on_change=on_unit_selected
        )
        category_container, category_field = self.create_searchable_dropdown(
            get_text("category"), 
            get_text("select_category_hint"),
            categories, 
            on_change=on_category_selected
        )
        supplier_container, supplier_field = self.create_searchable_dropdown(
            get_text("supplier"), 
            get_text("select_supplier_hint"),
            suppliers, 
            on_change=on_supplier_selected
        )
        
        # Error labels
        name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        sell_price_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        
        # Price validation functions
        def on_price_change(e):
            if cost_price.value:
                cleaned = ''.join(filter(str.isdigit, cost_price.value))
                if cleaned != cost_price.value:
                    cost_price.value = cleaned
                    cost_price.update()
        
        def on_sell_price_change(e):
            if sell_price.value:
                cleaned = ''.join(filter(str.isdigit, sell_price.value))
                if cleaned != sell_price.value:
                    sell_price.value = cleaned
                    sell_price.update()
        
        def on_stock_change(e):
            if stock_qty.value:
                cleaned = ''.join(filter(str.isdigit, stock_qty.value))
                if cleaned != stock_qty.value:
                    stock_qty.value = cleaned
                    stock_qty.update()
        
        def on_min_stock_change(e):
            if min_stock.value:
                cleaned = ''.join(filter(str.isdigit, min_stock.value))
                if cleaned != min_stock.value:
                    min_stock.value = cleaned
                    min_stock.update()
        
        name = ft.TextField(
            label=f"{get_text('parts_name')} *",
            hint_text=get_text("parts_name_hint"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            autofocus=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
        )
        
        cost_price = ft.TextField(
            label=get_text("cost_price"),
            hint_text=get_text("cost_price_hint"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="0",
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
            on_change=on_price_change,
        )
        
        sell_price = ft.TextField(
            label=f"{get_text('sell_price')} *",
            hint_text=get_text("sell_price_hint"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="0",
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
            on_change=on_sell_price_change,
        )
        
        stock_qty = ft.TextField(
            label=get_text("parts_stock"),
            hint_text=get_text("stock_qty_hint"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="0",
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
            on_change=on_stock_change,
        )
        
        min_stock = ft.TextField(
            label=get_text("parts_min_stock"),
            hint_text=get_text("min_stock_hint"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            value="5",
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
            on_change=on_min_stock_change,
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
            
            # Validate Sell Price
            if not sell_price.value or not sell_price.value.strip():
                sell_price_error.value = get_text("please_enter_price")
                sell_price_error.visible = True
                is_valid = False
            else:
                try:
                    price_val = float(sell_price.value.strip())
                    if price_val < 0:
                        sell_price_error.value = get_text("price_must_be_positive")
                        sell_price_error.visible = True
                        is_valid = False
                    else:
                        sell_price_error.visible = False
                except ValueError:
                    sell_price_error.value = get_text("price_must_be_number")
                    sell_price_error.visible = True
                    is_valid = False
            
            # Update UI
            name.update()
            sell_price.update()
            name_error.update()
            sell_price_error.update()
            
            return is_valid
        
        def save(e):
            if not validate_fields():
                return
            
            try:
                sell_price_val = float(sell_price.value) if sell_price.value else 0
                cost_price_val = float(cost_price.value) if cost_price.value else 0
                stock_qty_val = int(stock_qty.value) if stock_qty.value else 0
                min_stock_val = int(min_stock.value) if min_stock.value else 5
                
                self.parent.client.add_part(
                    name=name.value.strip(),
                    cost_price=cost_price_val,
                    sell_price=sell_price_val,
                    stock_qty=stock_qty_val,
                    min_stock=min_stock_val,
                    unit_id=selected_unit_id[0] if selected_unit_id[0] else None,
                    category_id=selected_category_id[0] if selected_category_id[0] else None,
                    supplier_id=selected_supplier_id[0] if selected_supplier_id[0] else None,
                )
                self._close_dialog()
                self.parent.load_data(force=True)
                self.parent.show_snackbar(get_text("add_success"), "success")
            except Exception as err:
                print(f"Error saving: {err}")
                traceback.print_exc()
                self.parent.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.ADD_CIRCLE, size=18, color=ft.Colors.WHITE),
                            bgcolor=self.parent.primary_color,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text('parts_add'), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        # Name
                        ft.Column([
                            name,
                            name_error,
                        ], spacing=1),
                        ft.Container(height=4),
                        # Category
                        category_container,
                        ft.Container(height=4),
                        # Unit
                        unit_container,
                        ft.Container(height=4),
                        # Cost & Sell Price
                        ft.Row([cost_price, sell_price], spacing=8),
                        ft.Column([
                            sell_price_error,
                        ], spacing=1),
                        ft.Container(height=4),
                        # Stock & Min Stock
                        ft.Row([stock_qty, min_stock], spacing=8),
                        ft.Container(height=4),
                        # Supplier
                        supplier_container,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                width=360,
                height=340,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(
                                content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                                on_click=self._close_dialog,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            ),
                            ft.ElevatedButton(
                                content=ft.Text(get_text("save"), size=13, color=ft.Colors.WHITE),
                                on_click=save,
                                style=ft.ButtonStyle(
                                    bgcolor=self.parent.primary_color,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    elevation=0,
                                    padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                                ),
                            ),
                        ],
                        spacing=6,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def show_edit_dialog(self, part, units, categories, suppliers):
        """Show edit part dialog with searchable dropdowns"""
        
        selected_unit_id = [part.get('unit_id')]
        selected_unit_name = [None]
        selected_category_id = [part.get('category_id')]
        selected_category_name = [None]
        selected_supplier_id = [part.get('supplier_id')]
        selected_supplier_name = [None]
        
        def on_unit_selected(item_id, item_name):
            selected_unit_id[0] = item_id
            selected_unit_name[0] = item_name
        
        def on_category_selected(item_id, item_name):
            selected_category_id[0] = item_id
            selected_category_name[0] = item_name
        
        def on_supplier_selected(item_id, item_name):
            selected_supplier_id[0] = item_id
            selected_supplier_name[0] = item_name
        
        # Create searchable dropdowns with values
        unit_container, unit_field = self.create_searchable_dropdown(
            get_text("unit"), 
            get_text("select_unit_hint"),
            units, 
            value=part.get('unit_id'),
            on_change=on_unit_selected
        )
        category_container, category_field = self.create_searchable_dropdown(
            get_text("category"), 
            get_text("select_category_hint"),
            categories, 
            value=part.get('category_id'),
            on_change=on_category_selected
        )
        supplier_container, supplier_field = self.create_searchable_dropdown(
            get_text("supplier"), 
            get_text("select_supplier_hint"),
            suppliers, 
            value=part.get('supplier_id'),
            on_change=on_supplier_selected
        )
        
        # Error labels
        name_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        sell_price_error = ft.Text("", color=ft.Colors.RED_600, size=10, visible=False)
        
        # Price validation functions
        def on_price_change(e):
            if cost_price.value:
                cleaned = ''.join(filter(str.isdigit, cost_price.value))
                if cleaned != cost_price.value:
                    cost_price.value = cleaned
                    cost_price.update()
        
        def on_sell_price_change(e):
            if sell_price.value:
                cleaned = ''.join(filter(str.isdigit, sell_price.value))
                if cleaned != sell_price.value:
                    sell_price.value = cleaned
                    sell_price.update()
        
        def on_stock_change(e):
            if stock_qty.value:
                cleaned = ''.join(filter(str.isdigit, stock_qty.value))
                if cleaned != stock_qty.value:
                    stock_qty.value = cleaned
                    stock_qty.update()
        
        def on_min_stock_change(e):
            if min_stock.value:
                cleaned = ''.join(filter(str.isdigit, min_stock.value))
                if cleaned != min_stock.value:
                    min_stock.value = cleaned
                    min_stock.update()
        
        name = ft.TextField(
            label=f"{get_text('parts_name')} *",
            hint_text=get_text("parts_name_hint"),
            value=part.get('name', ''),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
        )
        
        cost_price = ft.TextField(
            label=get_text("cost_price"),
            hint_text=get_text("cost_price_hint"),
            value=str(part.get('cost_price', 0)),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
            on_change=on_price_change,
        )
        
        sell_price = ft.TextField(
            label=f"{get_text('sell_price')} *",
            hint_text=get_text("sell_price_hint"),
            value=str(part.get('sell_price', 0)),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
            on_change=on_sell_price_change,
        )
        
        stock_qty = ft.TextField(
            label=get_text("parts_stock"),
            hint_text=get_text("stock_qty_hint"),
            value=str(part.get('stock_qty', 0)),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
            on_change=on_stock_change,
        )
        
        min_stock = ft.TextField(
            label=get_text("parts_min_stock"),
            hint_text=get_text("min_stock_hint"),
            value=str(part.get('min_stock', 5)),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            content_padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            border_color=ft.Colors.GREY_300,
            focused_border_color=self.parent.primary_color,
            expand=True,
            height=38,
            text_size=12,
            on_change=on_min_stock_change,
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
            
            # Validate Sell Price
            if not sell_price.value or not sell_price.value.strip():
                sell_price_error.value = get_text("please_enter_price")
                sell_price_error.visible = True
                is_valid = False
            else:
                try:
                    price_val = float(sell_price.value.strip())
                    if price_val < 0:
                        sell_price_error.value = get_text("price_must_be_positive")
                        sell_price_error.visible = True
                        is_valid = False
                    else:
                        sell_price_error.visible = False
                except ValueError:
                    sell_price_error.value = get_text("price_must_be_number")
                    sell_price_error.visible = True
                    is_valid = False
            
            # Update UI
            name.update()
            sell_price.update()
            name_error.update()
            sell_price_error.update()
            
            return is_valid
        
        def save_edit(e):
            if not validate_fields():
                return
            
            try:
                sell_price_val = float(sell_price.value) if sell_price.value else 0
                cost_price_val = float(cost_price.value) if cost_price.value else 0
                stock_qty_val = int(stock_qty.value) if stock_qty.value else 0
                min_stock_val = int(min_stock.value) if min_stock.value else 5
                
                update_data = {
                    'name': name.value.strip(),
                    'cost_price': cost_price_val,
                    'sell_price': sell_price_val,
                    'stock_qty': stock_qty_val,
                    'min_stock': min_stock_val,
                    'unit_id': selected_unit_id[0] if selected_unit_id[0] else None,
                    'category_id': selected_category_id[0] if selected_category_id[0] else None,
                    'supplier_id': selected_supplier_id[0] if selected_supplier_id[0] else None,
                }
                
                self.parent.client.update_part(part.get('id'), update_data)
                self._close_dialog()
                self.parent.load_data(force=True)
                self.parent.show_snackbar(get_text("edit_success"), "success")
            except Exception as err:
                print(f"Error in save_edit: {err}")
                traceback.print_exc()
                self.parent.show_snackbar(f"{get_text('error')}: {err}", "error")
        
        dialog = ft.AlertDialog(
            modal=True,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor=ft.Colors.WHITE,
            title=ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.EDIT, size=18, color=ft.Colors.WHITE),
                            bgcolor=self.parent.primary_color,
                            border_radius=8,
                            padding=ft.Padding(left=6, right=6, top=6, bottom=6),
                        ),
                        ft.Text(get_text('parts_edit'), size=15, weight=ft.FontWeight.BOLD, color="#1E293B"),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        # Name
                        ft.Column([
                            name,
                            name_error,
                        ], spacing=1),
                        ft.Container(height=4),
                        # Category
                        category_container,
                        ft.Container(height=4),
                        # Unit
                        unit_container,
                        ft.Container(height=4),
                        # Cost & Sell Price
                        ft.Row([cost_price, sell_price], spacing=8),
                        ft.Column([
                            sell_price_error,
                        ], spacing=1),
                        ft.Container(height=4),
                        # Stock & Min Stock
                        ft.Row([stock_qty, min_stock], spacing=8),
                        ft.Container(height=4),
                        # Supplier
                        supplier_container,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.Padding(left=16, right=16, top=12, bottom=8),
                width=360,
                height=340,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(
                                content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                                on_click=self._close_dialog,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            ),
                            ft.ElevatedButton(
                                content=ft.Text(get_text("save"), size=13, color=ft.Colors.WHITE),
                                on_click=save_edit,
                                style=ft.ButtonStyle(
                                    bgcolor=self.parent.primary_color,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    elevation=0,
                                    padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                                ),
                            ),
                        ],
                        spacing=6,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def show_delete_dialog(self, part_name, part_id):
        """Show delete confirmation dialog"""
        WARNING_COLOR = "#DC2626"
        
        def confirm(e):
            try:
                self.parent.client.delete_part(part_id)
                self._close_dialog()
                self.parent.load_data(force=True)
                self.parent.show_snackbar(get_text("delete_success"), "success")
            except Exception as err:
                print(f"Error in delete: {err}")
                traceback.print_exc()
                self.parent.show_snackbar(f"{get_text('error')}: {err}", "error")
        
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
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.DELETE_OUTLINE, size=32, color=WARNING_COLOR),
                        ft.Container(height=4),
                        ft.Text(f"ຕ້ອງການລຶບ '{part_name}' ຫຼື ບໍ່?", size=14, weight=ft.FontWeight.W_500, color="#1E293B", text_align=ft.TextAlign.CENTER),
                        ft.Text(get_text("delete_warning"), size=12, color="#64748B", text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                width=280,
                height=150,
            ),
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.TextButton(
                                content=ft.Text(get_text("cancel"), size=13, color="#64748B"),
                                on_click=self._close_dialog,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            ),
                            ft.ElevatedButton(
                                content=ft.Text(get_text("delete"), size=13, color=ft.Colors.WHITE),
                                on_click=confirm,
                                style=ft.ButtonStyle(
                                    bgcolor=WARNING_COLOR,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    elevation=0,
                                    padding=ft.Padding(left=18, right=18, top=6, bottom=6),
                                ),
                            ),
                        ],
                        spacing=6,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.Padding(left=14, right=14, top=8, bottom=8),
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self._open_dialog(dialog)
    
    def _open_dialog(self, dialog):
        try:
            # Close existing dialog if any
            if self.current_dialog:
                self._close_dialog()
            self.current_dialog = dialog
            self.parent.page.overlay.append(dialog)
            dialog.open = True
            self.parent.page.update()
        except Exception as e:
            print(f"DEBUG: Error opening dialog: {e}")
    
    def _close_dialog(self, e=None):
        """Close the current dialog - simplified version like promotions page"""
        try:
            if self.current_dialog:
                # Just close it, let Flet handle the overlay removal
                self.current_dialog.open = False
                self.current_dialog = None
                self.parent.page.update()
        except Exception as ex:
            print(f"DEBUG: Error closing dialog: {ex}")
            # If error occurs, try to force close
            try:
                if self.current_dialog:
                    self.current_dialog.open = False
                    self.current_dialog = None
                    self.parent.page.update()
            except:
                pass