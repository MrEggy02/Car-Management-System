import flet as ft
from api_client import APIClient
import re

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
