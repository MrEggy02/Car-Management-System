# pages/shop_page.py
import flet as ft
import asyncio
import traceback
from i18n import get_text

class ShopContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.is_loading = False
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"

    def build(self):
        """Build shop management content"""
        
        # Header - ปกติไม่ใหญ่เกินไป
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                get_text("shop_title"), 
                                size=24, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.WHITE
                            ),
                            ft.Text(
                                get_text("shop_subtitle"),
                                size=13,
                                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                            ),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.SAVE, size=18, color=ft.Colors.WHITE),
                            ft.Text(get_text("save"), size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        on_click=self.save_shop,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=0,
                            padding=ft.padding.symmetric(horizontal=20, vertical=12),
                        ),
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(top=20, bottom=20, left=32, right=32),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
        )
        
        # Form fields
        self.shop_name = ft.TextField(
            label=f"{get_text('shop_name')}",
            hint_text=get_text("shop_name_hint"),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        self.phone = ft.TextField(
            label=get_text("shop_phone"),
            hint_text=get_text("phone_hint"),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        self.address = ft.TextField(
            label=get_text("shop_address"),
            hint_text=get_text("address_hint"),
            multiline=True,
            min_lines=3,
            max_lines=4,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            text_size=14,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        # Form Card
        form_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Two column layout for name and phone
                    ft.Row([
                        self.shop_name,
                        ft.Container(width=16),
                        self.phone,
                    ], spacing=0, expand=True),
                    ft.Container(height=20),
                    self.address,
                ], spacing=0),
                padding=ft.padding.all(24),
            ),
            elevation=2,
        )
        
        # Main content - Center the form
        main_content = ft.Container(
            content=ft.Column([
                ft.Container(height=20),
                ft.Container(
                    content=form_card,
                    width=700,
                    alignment=ft.Alignment(0, 0),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Main layout
        main_content_layout = ft.Container(
            content=ft.Column([
                header,
                main_content,
            ]),
            expand=True,
            bgcolor="#F5F7FA",
        )
        
        # Load data after UI is built
        self.page.run_task(self._delayed_load)
        
        return main_content_layout
    
    async def _delayed_load(self):
        """Async delayed load to prevent UI blocking"""
        await asyncio.sleep(0.2)
        self.load_data()
    
    def load_data(self):
        """Load shop data from server"""
        if self.is_loading:
            return
        self.is_loading = True
        
        try:
            print("DEBUG: Loading shop data...")
            shop = self.client.get_shop()
            if shop:
                self.shop_name.value = shop.get('name', '')
                self.address.value = shop.get('address', '')
                self.phone.value = shop.get('phone', '')
                self.page.update()
                print("DEBUG: Shop data loaded successfully")
            
        except Exception as e:
            print(f"DEBUG: Error loading shop data: {e}")
            traceback.print_exc()
            self.shop_name.value = ""
            self.address.value = ""
            self.phone.value = ""
        finally:
            self.is_loading = False

    def save_shop(self, e):
        """Save shop information"""
        if not self.shop_name.value:
            self.show_snackbar(get_text("shop_name_required"))
            return
        
        btn = e.control
        original_text = btn.content.controls[1].value
        btn.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
        btn.disabled = True
        self.page.update()
        
        try:
            self.client.update_shop(
                name=self.shop_name.value,
                address=self.address.value,
                phone=self.phone.value
            )
            
            self.show_snackbar(f"✅ {get_text('save_success')}")
            self.load_data()
            
        except Exception as err:
            print(f"Error saving shop: {err}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {str(err)}")
        finally:
            btn.content.controls[0].name = ft.Icons.SAVE
            btn.disabled = False
            self.page.update()

    def show_snackbar(self, message):
        """Show snackbar message"""
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.GREY_800,
            duration=3000,
        )
        self.page.snack_bar = snack
        self.page.snack_bar.open = True
        self.page.update()