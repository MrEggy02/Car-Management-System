# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# ============================================
# hiddenimports ทั้งหมด (ใช้ชื่อ module ที่ถูกต้อง)
# ============================================
hiddenimports = [
    # Core packages
    'pages',
    'pages.Management',
    'pages.layout',
    
    # Management modules (ใช้ชื่อ module จริง)
    'pages.Management.employees',
    'pages.Management.employees.employees_content',
    'pages.Management.employees.employees_dialogs',
    'pages.Management.brands',
    'pages.Management.brands.brands_page',
    'pages.Management.brands.brands_dialogs',
    'pages.Management.parts',
    'pages.Management.parts.parts_page',
    'pages.Management.parts.parts_dialogs',
    'pages.Management.service',
    'pages.Management.service.services_page',
    'pages.Management.service.services_dialogs',
    'pages.Management.supplier',
    'pages.Management.supplier.suppliers_page',
    'pages.Management.supplier.suppliers_dialogs',
    'pages.Management.store',
    'pages.Management.store.shop_page',
    'pages.Management.promotion',
    'pages.Management.promotion.promotions_page',
    'pages.Management.promotion.promotions_dialogs',
    'pages.Management.units',
    'pages.Management.units.units_page',
    'pages.Management.units.units_dialogs',
    'pages.Management.part_categories',
    'pages.Management.part_categories.part_categories_page',
    'pages.Management.part_categories.part_categories_dialogs',
]

# ============================================

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Car Repair Management System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # เปิดไว้ดู Error
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico', 
)