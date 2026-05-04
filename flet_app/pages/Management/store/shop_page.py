# pages/shop_page.py
import flet as ft
import base64
import os
import sys
import asyncio
import traceback
from PIL import Image
import io
import time
import threading
from tkinter import filedialog
import tkinter as tk

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import get_text

class ShopContent:
    def __init__(self, page: ft.Page, client, user, navigate):
        self.page = page
        self.client = client
        self.user = user
        self.navigate = navigate
        self.selected_image_path = None
        self.image_data = None
        self.current_logo_path = None
        self.current_dialog = None
        self.is_loading = False
        self.primary_color = "#1565C0"
        self.primary_dark = "#0D47A1"

    def build(self):
        """Build shop management content with beautiful gradient header"""
        
        # Beautiful gradient header
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
            padding=ft.padding.symmetric(vertical=20, horizontal=32),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=[self.primary_color, self.primary_dark],
            ),
            border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
            
        )
        
        # Logo section card
        self.logo_image = ft.Icon(ft.Icons.STORE, size=80, color=ft.Colors.GREY_300)
        
        self.logo_display_container = ft.Container(
            width=160,
            height=160,
            bgcolor=ft.Colors.GREY_50,
            border_radius=80,
            border=ft.border.all(3, ft.Colors.GREY_200),
            content=self.logo_image,
            alignment=ft.Alignment(0, 0),
        )
        
        logo_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.IMAGE, size=20, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                get_text("shop_logo"), 
                                size=16, 
                                weight=ft.FontWeight.BOLD, 
                                color="#1E293B"
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Stack([
                            self.logo_display_container,
                            ft.Container(
                                content=ft.Icon(ft.Icons.CAMERA_ALT, size=22, color=ft.Colors.WHITE),
                                bgcolor=self.primary_color,
                                border_radius=20,
                                padding=10,
                                right=0,
                                bottom=0,
                                on_click=self.pick_image,
                                shadow=ft.BoxShadow(
                                    blur_radius=5,
                                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                                ),
                            ),
                        ]),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(height=12),
                    ft.Text(
                        get_text("click_to_change_logo"), 
                        size=11, 
                        color="#64748B",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                padding=ft.padding.all(24),
            ),
            elevation=2,
            margin=ft.margin.symmetric(vertical=10),
        )
        
        # Form section card
        self.shop_name = ft.TextField(
            label=f"{get_text('shop_name')} *",
            hint_text=get_text("shop_name_hint"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            text_size=14,
            prefix_icon=ft.Icons.STORE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.address = ft.TextField(
            label=get_text("shop_address"),
            hint_text=get_text("address_hint"),
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            text_size=14,
            prefix_icon=ft.Icons.LOCATION_ON,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        self.phone = ft.TextField(
            label=get_text("shop_phone"),
            hint_text=get_text("phone_hint"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            text_size=14,
            prefix_icon=ft.Icons.PHONE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        self.email = ft.TextField(
            label=get_text("shop_email"),
            hint_text=get_text("email_hint"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            text_size=14,
            prefix_icon=ft.Icons.EMAIL,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
            expand=True,
        )
        
        self.tax_id = ft.TextField(
            label=get_text("shop_tax_id"),
            hint_text=get_text("tax_id_hint"),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            filled=True,
            text_size=14,
            prefix_icon=ft.Icons.ASSIGNMENT,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
            border_color=ft.Colors.GREY_200,
            focused_border_color=self.primary_color,
        )
        
        form_section = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=self.primary_color),
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                border_radius=10,
                                padding=ft.padding.all(8),
                            ),
                            ft.Text(
                                get_text("shop_information"), 
                                size=16, 
                                weight=ft.FontWeight.BOLD, 
                                color="#1E293B"
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_100),
                    ft.Container(height=16),
                    self.shop_name,
                    ft.Container(height=16),
                    self.address,
                    ft.Container(height=16),
                    ft.Row([self.phone, self.email], spacing=16),
                    ft.Container(height=16),
                    self.tax_id,
                ], spacing=0),
                padding=ft.padding.all(24),
            ),
            elevation=2,
            margin=ft.margin.symmetric(vertical=10),
        )
        
        # Main content with responsive layout
        main_content = ft.Container(
            content=ft.ResponsiveRow([
                # Left column - Logo
                ft.Container(
                    col={"xs": 12, "sm": 12, "md": 4, "lg": 3},
                    content=logo_section,
                    padding=ft.padding.only(left=20, right=10, top=20, bottom=20),
                ),
                # Right column - Form
                ft.Container(
                    col={"xs": 12, "sm": 12, "md": 8, "lg": 9},
                    content=form_section,
                    padding=ft.padding.only(left=10, right=20, top=20, bottom=20),
                ),
            ]),
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
                self.shop_name.value = shop.get('shop_name', '')
                self.address.value = shop.get('address', '')
                self.phone.value = shop.get('phone', '')
                self.email.value = shop.get('email', '')
                self.tax_id.value = shop.get('tax_id', '')
                self.current_logo_path = shop.get('logo_path', '')
                
                if self.current_logo_path:
                    self.load_logo_from_api()
                
                self.page.update()
                print("DEBUG: Shop data loaded successfully")
            
        except Exception as e:
            print(f"DEBUG: Error loading shop data: {e}")
            traceback.print_exc()
            self.shop_name.value = ""
            self.address.value = ""
            self.phone.value = ""
            self.email.value = ""
            self.tax_id.value = ""
        finally:
            self.is_loading = False

    def load_logo_from_api(self):
        """Load logo from API"""
        try:
            logo_data = self.client.get_shop_logo()
            if logo_data:
                img_base64 = base64.b64encode(logo_data).decode()
                data_uri = f"data:image/png;base64,{img_base64}"
                
                self.logo_display_container.content = ft.Image(
                    src=data_uri,
                    width=160,
                    height=160,
                    fit="cover",
                    border_radius=80,
                )
                self.page.update()
        except Exception as e:
            print(f"DEBUG: Error loading logo: {e}")

    def pick_image(self, e):
        """Open tkinter file dialog to select logo image"""
        def pick_file_thread():
            try:
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                
                file_path = filedialog.askopenfilename(
                    title=get_text("select_logo"),
                    filetypes=[
                        ("Image files", "*.png *.jpg *.jpeg *.gif *.webp"),
                        ("PNG files", "*.png"),
                        ("JPEG files", "*.jpg *.jpeg"),
                        ("All files", "*.*")
                    ]
                )
                root.destroy()
                
                if file_path:
                    self.selected_image_path = file_path
                    self.display_selected_image(file_path)
                else:
                    self.show_snackbar(get_text("no_image_selected"))
                    
            except Exception as ex:
                print(f"Error in file picker: {ex}")
                self.show_snackbar(f"{get_text('error')}: {str(ex)}")
        
        threading.Thread(target=pick_file_thread, daemon=True).start()
    
    def display_selected_image(self, file_path=None):
        """Display selected image in the UI"""
        if file_path is None:
            file_path = self.selected_image_path
            
        if file_path and os.path.exists(file_path):
            try:
                with Image.open(file_path) as img:
                    if img.mode == 'RGBA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    self.image_data = img_byte_arr.getvalue()
                    
                    img_base64 = base64.b64encode(self.image_data).decode()
                    data_uri = f"data:image/png;base64,{img_base64}"
                    
                    self.logo_display_container.content = ft.Image(
                        src=data_uri,
                        width=160,
                        height=160,
                        fit="cover",
                        border_radius=80,
                    )
                    self.page.update()
                    self.show_snackbar(f"✅ {get_text('logo_selected')}")
                    
            except Exception as e:
                print(f"Error processing image: {e}")
                self.show_snackbar(f"{get_text('error')}: {str(e)}")

    def save_shop(self, e):
        """Save shop information"""
        if not self.shop_name.value:
            self.show_snackbar(get_text("shop_name_required"))
            return
        
        # Show loading state
        save_button = e.control if hasattr(e, 'control') else None
        if save_button:
            original_text = save_button.content.controls[1].value
            save_button.content.controls[0].name = ft.Icons.HOURGLASS_EMPTY
            save_button.disabled = True
            self.page.update()
        
        try:
            self.client.update_shop(
                shop_name=self.shop_name.value,
                address=self.address.value,
                phone=self.phone.value,
                email=self.email.value,
                tax_id=self.tax_id.value
            )
            
            if self.image_data:
                self.upload_logo()
            else:
                self.show_snackbar(f"✅ {get_text('save_success')}")
                self.load_data()
            
        except Exception as err:
            print(f"Error saving shop: {err}")
            traceback.print_exc()
            self.show_snackbar(f"{get_text('error')}: {str(err)}")
        finally:
            if save_button:
                save_button.content.controls[0].name = ft.Icons.SAVE
                save_button.disabled = False
                self.page.update()

    def upload_logo(self):
        """Upload logo to server"""
        if not self.image_data:
            return
        
        temp_path = None
        try:
            temp_path = f"temp_logo_{int(time.time())}.png"
            with open(temp_path, 'wb') as f:
                f.write(self.image_data)
            
            result = self.client.upload_shop_logo(temp_path)
            
            if result:
                self.show_snackbar(f"✅ {get_text('logo_uploaded')}")
                self.image_data = None
                self.load_data()
            
        except Exception as e:
            print(f"Error uploading logo: {e}")
            error_msg = str(e)
            if "404" in error_msg or "Not Found" in error_msg:
                self.show_snackbar(get_text("logo_local_only"))
                self.save_logo_locally()
            else:
                self.show_snackbar(f"{get_text('error')}: {error_msg}")
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def save_logo_locally(self):
        """Save logo locally as fallback"""
        try:
            logo_dir = "assets"
            if not os.path.exists(logo_dir):
                os.makedirs(logo_dir)
            
            logo_path = os.path.join(logo_dir, "shop_logo.png")
            with open(logo_path, 'wb') as f:
                f.write(self.image_data)
            
            self.show_snackbar(f"✅ {get_text('logo_saved_local')}")
            self.image_data = None
            
        except Exception as e:
            print(f"Error saving logo locally: {e}")
            self.show_snackbar(f"{get_text('error')}: {str(e)}")

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