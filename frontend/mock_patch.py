import flet as ft
from api_client import APIClient
import re

# Patch layout helper modules with their class equivalents to support lowercase modules across the codebase
# padding
ft.padding.symmetric = ft.Padding.symmetric
ft.padding.all = ft.Padding.all
ft.padding.only = ft.Padding.only
ft.padding.zero = ft.Padding.zero

# margin
ft.margin.symmetric = ft.Margin.symmetric
ft.margin.all = ft.Margin.all
ft.margin.only = ft.Margin.only

# border
ft.border.all = ft.Border.all
ft.border.only = ft.Border.only
ft.border.symmetric = ft.Border.symmetric

# border_radius
ft.border_radius.all = ft.BorderRadius.all
ft.border_radius.only = ft.BorderRadius.only
ft.border_radius.horizontal = ft.BorderRadius.horizontal
ft.border_radius.vertical = ft.BorderRadius.vertical

def mask_text(text):
    if text is None:
        return None
    if not isinstance(text, str):
        text = str(text)
    
    # Preserve date / time / version
    if re.match(r'^\d{4}-\d{2}-\d{2}$', text) or re.match(r'^\d{2}-\d{2}-\d{4}$', text):
        return text
    if re.match(r'^\d{2}:\d{2}$', text):
        return text
    if text.strip().lower() == "v1.0.0":
        return text
        
    # Replace any digit with 'X'
    return re.sub(r'\d', 'X', text)

# Monkey-patch ft.Text
original_text_setattr = ft.Text.__setattr__
def custom_text_setattr(self, name, val):
    if name == "value" and val is not None and getattr(APIClient, "GLOBAL_MOCK_MODE", False):
        val = mask_text(val)
    original_text_setattr(self, name, val)
ft.Text.__setattr__ = custom_text_setattr

# Monkey-patch ft.TextField
original_textfield_setattr = ft.TextField.__setattr__
def custom_textfield_setattr(self, name, val):
    if name == "value" and val is not None and getattr(APIClient, "GLOBAL_MOCK_MODE", False):
        val = mask_text(val)
    original_textfield_setattr(self, name, val)
ft.TextField.__setattr__ = custom_textfield_setattr

# Monkey-patch ft.dropdown.Option
try:
    original_option_setattr = ft.dropdown.Option.__setattr__
    def custom_option_setattr(self, name, val):
        if name == "text" and val is not None and getattr(APIClient, "GLOBAL_MOCK_MODE", False):
            val = mask_text(val)
        original_option_setattr(self, name, val)
    ft.dropdown.Option.__setattr__ = custom_option_setattr
except Exception as e:
    pass
