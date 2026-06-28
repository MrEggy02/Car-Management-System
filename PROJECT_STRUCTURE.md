# PROJECT_STRUCTURE.md — J&P Auto Maxxing
# ໄຟລ໌ນີ້ອະທິບາຍໂຄງສ້າງ ແລະ ໜ້າທີ່ຂອງທຸກໄຟລ໌ໃນໂຄງການ
# ສ້າງໄວ້ສຳລັບ AI ແລະ ນັກພັດທະນາເພື່ອໃຊ້ອ້າງອິງ

---

## ພາບລວມໂຄງການ (Project Summary)

**ຊື່ໂຄງການ**: J&P Auto Maxxing  
**ປະເພດ**: ລະບົບຄຸ້ມຄອງອູ່ສ້ອມແປງລົດ (Car Repair Shop Management System)  
**Tech Stack**:
- Backend: **FastAPI** (Python) — REST API, ເຊື່ອມ MySQL
- Frontend: **Flet** (Python) — Desktop UI
- Database: **MySQL** — ຊື່ database: `jp_auto_db`
- PDF: **ReportLab** — ສ້າງ PDF ສຳລັບໃບຕ່າງໆ

**ທີ່ຢູ່ Backend**: `http://127.0.0.1:8000`  
**ວິທີລັນ Backend**: `python -m uvicorn main:app` ໃນໂຟນເດີ `backend/`  
**ວິທີລັນ Frontend**: `python main.py` ໃນໂຟນເດີ `frontend/`

---

## ໂຄງສ້າງໄດເຣັກທໍລີ (Directory Tree)

```
Car-Management-System/
├── SYSTEM_OVERVIEW.md          # ໄຟລ໌ອະທິບາຍລະບົບລວມ (DFD, Workflow)
├── PROJECT_STRUCTURE.md        # ໄຟລ໌ນີ້ — ໂຄງສ້າງໄຟລ໌ທັງໝົດ
├── jp_auto_db.sql              # SQL Schema ຂອງຖານຂໍ້ມູນທັງໝົດ
├── jp_auto_api.json            # API collection (Postman/reference)
├── library                     # ບັນຊີ Python dependencies
├── promotions_schema.txt       # ໂຄງສ້າງຕາຕະລາງ promotions (reference)
│
├── backend/                    # ລະບົບຫຼັງບ້ານ (FastAPI)
│   ├── main.py
│   ├── database.py
│   ├── auth.py
│   ├── utils.py
│   ├── utils_pdf.py
│   ├── requirements.txt
│   └── routers/
│       ├── __init__.py
│       ├── employees.py
│       ├── shop.py
│       ├── suppliers.py
│       ├── services.py
│       ├── parts.py
│       ├── promotions.py
│       ├── promotion_items.py
│       ├── customers.py
│       ├── cars.py
│       ├── vehicles.py
│       ├── job_orders.py
│       ├── quotations.py
│       ├── repair_orders.py
│       ├── invoices.py
│       ├── purchase_orders.py
│       ├── reports.py
│       ├── brands.py
│       ├── units.py
│       └── part_categories.py
│
└── frontend/                   # ລະບົບໜ້າບ້ານ (Flet Desktop App)
    ├── main.py
    ├── api_client.py
    ├── i18n.py
    ├── mock_patch.py
    ├── requirements.txt
    ├── theme/
    │   └── app_theme.py
    ├── components/
    │   └── language_switcher.py
    └── pages/
        ├── app_layout.py
        ├── login_page.py
        ├── dashboard_page.py
        ├── dashboard_content.py
        ├── personal_page.py
        ├── promotion_items.py
        ├── layout/
        │   ├── sidebar.py
        │   ├── content_manager.py
        │   └── top_nav_bar.py
        ├── Management/
        │   ├── employees/
        │   │   ├── employees_page.py
        │   │   └── employees_widgets.py
        │   ├── supplier/
        │   │   └── suppliers_page.py
        │   ├── service/
        │   │   └── services_page.py
        │   ├── parts/
        │   │   ├── parts_page.py
        │   │   └── parts_dialogs.py
        │   ├── store/
        │   │   └── shop_page.py
        │   ├── promotion/
        │   │   ├── promotions_page.py
        │   │   └── promotions_dialogs.py
        │   ├── brands/
        │   │   ├── brands_page.py
        │   │   └── brands_dialogs.py
        │   ├── units/
        │   │   ├── units_page.py
        │   │   └── units_dialogs.py
        │   └── part_categories/
        │       ├── part_categories_page.py
        │       └── part_categories_dialogs.py
        ├── customers/
        │   ├── customer_list.py
        │   └── customer_dialogs.py
        ├── job_orders/
        │   ├── job_order_create.py
        │   ├── job_order_list.py
        │   ├── job_order_dialogs.py
        │   └── job_order_print.py
        ├── quotations/
        │   ├── quotation_create.py
        │   ├── quotation_list.py
        │   ├── quotation_dialogs.py
        │   └── quotation_dialog_helpers.py
        ├── repair/
        │   ├── repair_create.py
        │   ├── repair_list.py
        │   └── repair_detail.py
        ├── invoices/
        │   ├── invoice_create.py
        │   ├── invoice_list.py
        │   └── invoice_detail.py
        ├── purchase/
        │   ├── purchase_management.py
        │   ├── purchase_order_create.py
        │   ├── purchase_order_detail.py
        │   ├── receiving_management.py
        │   ├── receiving_po_list.py
        │   ├── goods_receipt_list.py
        │   └── stock_movement.py
        └── reports/
            ├── revenue_report.py
            ├── repair_summary_report.py
            ├── parts_service_sales_report.py
            ├── mechanic_performance_report.py
            └── promotion_usage_report.py
```

---

## Backend — ອະທິບາຍແຕ່ລະໄຟລ໌

### `backend/main.py`
ຈຸດເລີ່ມຕົ້ນຂອງ FastAPI Application.  
- ລົງທະບຽນ Router ທັງໝົດ (employees, shop, quotations, invoices, ...)
- ຕັ້ງຄ່າ CORS ໃຫ້ Frontend ສາມາດເຊື່ອມຕໍ່ໄດ້
- Endpoint `/login` — ຮັບ username/password ແລ້ວ return user object (id, role, fullname)
- Endpoint `GET /` — health check
- Endpoint `GET /debug/users` — ດູລາຍຊື່ user ທີ່ login ໄດ້ (debug only)

### `backend/database.py`
ຈັດການ Connection Pool ກັບ MySQL.
- ສ້າງ `MySQLConnectionPool` ຂະໜາດ 10 connections ຊື່ `jp_auto_pool`
- ຟັງຊັນ `get_db()` — ດຶງ connection ຈາກ pool ເພື່ອໃຊ້ໃນ router ຕ່າງໆ
- ເຊື່ອມ `127.0.0.1`, database `jp_auto_db`, user `root`

### `backend/auth.py`
ລະບົບ Authentication ດ້ວຍ HTTP Basic Auth.
- `hash_password()` — Hash ລະຫັດດ້ວຍ SHA-256
- `verify_password()` — ກວດລະຫັດ
- `authenticate_user()` — ກວດ username/password ຈາກຕາຕະລາງ `Employees`, ຮອງຮັບສະຖານະ `active` ແລະ `can_login = TRUE`

### `backend/utils.py`
Utility functions ຂະໜາດນ້ອຍ (ໂດຍທົ່ວໄປໃຊ້ format ຕ່າງໆ).

### `backend/utils_pdf.py`
⭐ **ໄຟລ໌ໃຫຍ່ທີ່ສຸດໃນ backend** — ສ້າງ PDF ທຸກປະເພດດ້ວຍ ReportLab.
- `generate_job_order_pdf()` — ໃບຮັບລົດ (Job Order Receipt)
- `generate_quotation_pdf()` — ໃບສະເໜີລາຄາ (Quotation)
- `generate_invoice_pdf()` — ໃບບິນເກັບເງິນ (Invoice/Receipt)
- `generate_delivery_note_pdf()` — ໃບສົ່ງມອບລົດ (Delivery Note) — ໄມ່ມີ Status Statement, ໄມ່ມີລາຄາ
- ທຸກ function ລຶງຂໍ້ມູນຮ້ານ (shop logo, name, address) ຈາກ DB ໂດຍອັດຕະໂນມັດ
- Font ທີ່ໃຊ້: NotoSansLao (ຮອງຮັບພາສາລາວ)
- Font files ຢູ່ໃນ `backend/assets/fonts/`

### `backend/requirements.txt`
Dependencies: fastapi, uvicorn, mysql-connector-python, reportlab, python-multipart, pillow

---

## Backend Routers — `backend/routers/`

### `routers/__init__.py`
Import ແລະ Export Router ທັງໝົດເພື່ອໃຊ້ໃນ `main.py`.

### `routers/employees.py`
CRUD ສຳລັບຕາຕະລາງ `Employees`.
- `GET /employees/` — ດຶງລາຍຊື່ພະນັກງານ
- `POST /employees/` — ເພີ່ມພະນັກງານ (hash password ໄວ້ໃນ DB)
- `PUT /employees/{id}` — ແກ້ໄຂພະນັກງານ
- `DELETE /employees/{id}` — ລຶບພະນັກງານ
- `GET /mechanics/` — ດຶງສະເພາະຊ່າງ (role=mechanic)

### `routers/shop.py`
ຈັດການຂໍ້ມູນຮ້ານ (ຕາຕະລາງ `shop`).
- `GET /shop/` — ດຶງຂໍ້ມູນຮ້ານ
- `PUT /shop/` — ອັບເດດຂໍ້ມູນຮ້ານ (ຊື່, ທີ່ຢູ່, ໂທ, ເລກພາສີ)
- `POST /shop/logo` — ອັບໂຫຼດໂລໂກ້ (multipart)

### `routers/suppliers.py`
CRUD ຜູ້ສະໜອງ (ຕາຕະລາງ `suppliers`).
- GET, POST, PUT, DELETE `/suppliers/`

### `routers/services.py`
CRUD ລາຍການບໍລິການ (ຕາຕະລາງ `services`).
- GET, POST, PUT, DELETE `/services/`

### `routers/parts.py`
CRUD ອາໄຫຼ່ + ຄຸ້ມຄອງ Stock (ຕາຕະລາງ `parts`).
- `GET /parts/` — ດຶງລາຍຊື່ອາໄຫຼ່ທັງໝົດ (ລວມ brand, category)
- `GET /parts/low-stock` — ອາໄຫຼ່ໃກ້ໝົດ (qty <= min_qty)
- `POST /parts/` — ເພີ່ມອາໄຫຼ່
- `PUT /parts/{id}` — ແກ້ໄຂ
- `DELETE /parts/{id}` — ລຶບ
- `POST /parts/{id}/stock-movement` — ບັນທຶກການຈ່າຍ/ຮັບເຂົ້າສາງ

### `routers/promotions.py`
CRUD ໂປຣໂມຊັນ (ຕາຕະລາງ `promotions`).
- ຮອງຮັບ discount_type: `percentage` / `fixed`
- GET, POST, PUT, DELETE `/promotions/`

### `routers/promotion_items.py`
ຈັດການລາຍການທີ່ຢູ່ໃນໂປຣໂມຊັນ (ຕາຕະລາງ `promotion_items`).
- `GET /promotions/{promo_id}/items/` — ດຶງ items ໃນ promo
- `POST /promotions/{promo_id}/items/` — ເພີ່ມ item
- `DELETE /promotions/{promo_id}/items/{item_id}` — ລຶບ item

### `routers/customers.py`
CRUD ລູກຄ້າ (ຕາຕະລາງ `customers`).
- `GET /customers/` — ດຶງລາຍຊື່ລູກຄ້າ ​(ລວມ vehicles)
- `GET /customers/search` — ຄົ້ນຫາດ້ວຍ phone/name
- POST, PUT, DELETE `/customers/`

### `routers/cars.py`
Router ເກົ່າສຳລັບ `cars` table (deprecated, ຍັງຄົງໄວ້ເພື່ອ compatibility).

### `routers/vehicles.py`
CRUD ລົດທີ່ຜູກກັບ customer (ຕາຕະລາງ `vehicles`).
- `GET /customers/{cust_id}/vehicles/` — ດຶງລາຍລົດຂອງລູກຄ້າ
- `POST /customers/{cust_id}/vehicles/` — ເພີ່ມລົດ
- `PUT /vehicles/{id}` — ແກ້ໄຂ
- `DELETE /vehicles/{id}` — ລຶບ

### `routers/job_orders.py`
⭐ ຈັດການໃບຮັບລົດ (ຕາຕະລາງ `job_orders`).
- `GET /job-orders/` — ດຶງທັງໝົດ (filter ໄດ້ by status)
- `POST /job-orders/` — ສ້າງໃບຮັບລົດ (ສ້ອງ customer + vehicle ໃໝ່ຖ້າຈຳເປັນ)
- `PUT /job-orders/{id}/status` — ອັບເດດສະຖານະ
- `GET /job-orders/{id}/pdf` — ສ້າງ PDF ໃບຮັບລົດ → ໃຊ້ `utils_pdf.generate_job_order_pdf()`
- ສະຖານະ: `pending` → `in_progress` → `completed` / `cancelled`

### `routers/quotations.py`
⭐ ຈັດການໃບສະເໜີລາຄາ (ຕາຕະລາງ `quotations`, `quotation_items`).
- `GET /quotations/` — ດຶງທັງໝົດ
- `POST /quotations/` — ສ້າງໃບສະເໜີ (ຜູກກັບ job_order)
- `POST /quotations/{id}/items` — ເພີ່ມ item (part ຫຼື service)
- `PUT /quotations/{id}/status` — ອັບເດດສະຖານະ (draft → approved → rejected)
- `GET /quotations/{id}/pdf` — PDF ໃບສະເໜີ → `utils_pdf.generate_quotation_pdf()`

### `routers/repair_orders.py`
⭐ ຈັດການໃບສັ່ງຊ້ອມ (ຕາຕະລາງ `repair_orders`, `repair_parts`, `repair_services`).
- `GET /repair-orders/` — ດຶງທັງໝົດ (join job_order, customer, mechanic)
- `POST /repair-orders/` — ສ້າງໃບສັ່ງຊ້ອມ (ຜູກກັບ approved quotation)
- `POST /repair-orders/{id}/parts` — ເພີ່ມ/ອັບເດດອາໄຫຼ່ທີ່ໃຊ້ (ຕັດ stock ອັດຕະໂນມັດ)
- `PUT /repair-orders/{id}/status` — ປ່ຽນສະຖານະ (pending → working → completed)
- `DELETE /repair-orders/{id}/parts/{part_id}` — ລຶບ part usage

### `routers/invoices.py`
⭐ ຈັດການໃບບິນ / ການຊຳລະ (ຕາຕະລາງ `invoices`).
- `GET /invoices/` — ດຶງທັງໝົດ
- `POST /invoices/` — ສ້າງໃບບິນຈາກ repair_order
- `PUT /invoices/{id}/pay` — ບັນທຶກການຊຳລະ (cash/transfer/qr) + ປ່ຽນສະຖານະ → `paid`
- `GET /invoices/{id}/pdf` — PDF ໃບບິນ → `utils_pdf.generate_invoice_pdf()`
- `GET /invoices/{id}/delivery-note/pdf` — PDF ໃບສົ່ງມອບລົດ → `utils_pdf.generate_delivery_note_pdf()`

### `routers/purchase_orders.py`
⭐ ຈັດການໃບສັ່ງຊື້ (ຕາຕະລາງ `purchase_orders`, `purchase_order_items`, `goods_receipts`).
- `GET /purchase-orders/` — ດຶງທັງໝົດ (filter by status)
- `POST /purchase-orders/` — ສ້າງ PO
- `PUT /purchase-orders/{id}/status` — ອັບເດດສະຖານະ (pending → approved → completed → cancelled)
- `POST /purchase-orders/{id}/receive` — ຮັບເຂົ້າ goods (ອັບ stock + ສ້າງ goods_receipt)
- `GET /purchase-orders/{id}/items` — ດຶງ items ຂອງ PO

### `routers/reports.py`
⭐ ລາຍງານທຸກຮູບແບບສຳລັບຜູ້ບໍລິຫານ.
- `GET /reports/revenue` — ລາຍຮັບ + ກຳໄລ (filter by date range)
- `GET /reports/repair-summary` — ສະຫຼຸບການຊ້ອມ (ສະຖານະ, ໄລຍະ, ຍີ່ຫໍ້ລົດ)
- `GET /reports/parts-usage` — ຍອດນຳໃຊ້ອາໄຫຼ່ + low stock
- `GET /reports/mechanic-performance` — ປະສິດທິພາບຊ່າງ
- `GET /reports/promotion-usage` — ການນຳໃຊ້ໂປຣໂມຊັນ

### `routers/brands.py`
CRUD ຍີ່ຫໍ້ລົດ (ຕາຕະລາງ `brands`).

### `routers/units.py`
CRUD ໜ່ວຍວັດ (ຕາຕະລາງ `units`) — ໃຊ້ໃນ parts.

### `routers/part_categories.py`
CRUD ໝວດໝູ່ອາໄຫຼ່ (ຕາຕະລາງ `part_categories`).

---

## Frontend — ອະທິບາຍແຕ່ລະໄຟລ໌

### `frontend/main.py`
ຈຸດເລີ່ມຕົ້ນຂອງ Flet App.
- ຕັ້ງຄ່າໜ້າຈໍ: fullscreen, min size 900x600
- ນຳໃຊ້ theme ຈາກ `app_theme.py`
- ຊ່ວຍ `login_page()` → ຫຼັງ login ສຳເລັດ `dashboard_page()`

### `frontend/api_client.py`
⭐ **ໄຟລ໌ສຳຄັນທີ່ສຸດ** — Class `APIClient` ທີ່ Frontend ໃຊ້ເຊື່ອມ Backend.
- `_request()` — ເມທອດຫຼັກສຳລັບ GET/POST/PUT/DELETE ກັບ Basic Auth
- ທຸກ Method ຢູ່ໃນ class `APIClient`:
  - `get_employees()`, `create_employee()`, `update_employee()`, `delete_employee()`
  - `get_suppliers()`, `create_supplier()`, ...
  - `get_parts()`, `get_low_stock_parts()`, `create_part()`, ...
  - `get_customers()`, `search_customers()`, `create_customer()`, ...
  - `get_job_orders()`, `create_job_order()`, `update_job_order_status()`, `get_job_order_pdf()`
  - `get_quotations()`, `create_quotation()`, `add_quotation_item()`, `get_quotation_pdf()`
  - `get_repair_orders()`, `create_repair_order()`, `add_repair_part()`, ...
  - `get_invoices()`, `create_invoice()`, `pay_invoice()`, `get_invoice_pdf()`, `get_delivery_note_pdf()`
  - `get_purchase_orders()`, `create_purchase_order()`, `receive_purchase_order()`, ...
  - `get_revenue_report()`, `get_repair_summary_report()`, ...
  - `get_brands()`, `get_units()`, `get_part_categories()`, ...

### `frontend/i18n.py`
⭐ ໄຟລ໌ Translation ທຸກພາສາ.
- Dict `LO` — ພາສາລາວ (~1100 keys)
- Dict `EN` — ພາສາອັງກິດ
- Dict `TH` — ພາສາໄທ (ບາງສ່ວນ)
- ຟັງຊັນ `get_text(key)` — ດຶງຄຳແປຕາມພາສາທີ່ເລືອກ
- ຖ້າ key ບໍ່ມີ → return key ດ້ວຍ (fallback safe)

### `frontend/mock_patch.py`
Patch ສຳລັບ test mode (Mock Mode) — ແທນທີ່ API ດ້ວຍຂໍ້ມູນ dummy.

### `frontend/requirements.txt`
Dependencies: flet, requests, pillow

---

## Frontend Pages — ໂຄງສ້າງໜ້າຈໍ

### ໂຄງສ້າງ Navigation (Page Index Map)

| Index | Page Name | ໄຟລ໌ |
|-------|-----------|-------|
| 0 | Dashboard | `dashboard_content.py` |
| 1 | Employees | `Management/employees/employees_page.py` |
| 2 | Suppliers | `Management/supplier/suppliers_page.py` |
| 3 | Services | `Management/service/services_page.py` |
| 4 | Parts | `Management/parts/parts_page.py` |
| 5 | Shop | `Management/store/shop_page.py` |
| 6 | Promotions | `Management/promotion/promotions_page.py` |
| 7 | Brands | `Management/brands/brands_page.py` |
| 8 | Units | `Management/units/units_page.py` |
| 9 | Part Categories | `Management/part_categories/part_categories_page.py` |
| 11 | Customer List | `customers/customer_list.py` |
| 13 | Job Order List | `job_orders/job_order_list.py` |
| 15 | Quotation List | `quotations/quotation_list.py` |
| 17 | Repair List | `repair/repair_list.py` |
| 20 | Invoice List | `invoices/invoice_list.py` |
| 22 | Purchase Order Create | `purchase/purchase_order_create.py` |
| 23 | ຄັງອາໄຫຼ່ (Purchase Mgmt) | `purchase/purchase_management.py` |
| 26 | Stock Movement | `purchase/stock_movement.py` |
| 29 | Revenue Report | `reports/revenue_report.py` |
| 30 | Repair Summary | `reports/repair_summary_report.py` |
| 31 | Parts Usage | `reports/parts_service_sales_report.py` |
| 32 | Mechanic Performance | `reports/mechanic_performance_report.py` |
| 33 | Promotion Usage | `reports/promotion_usage_report.py` |
| 35 | ຄັງອາໄຫຼ່ (New PO List) | `purchase/purchase_management.py` |
| 36 | ຮັບເຂົ້າ (Receiving) | `purchase/receiving_management.py` |
| 37 | ສ້າງໃບນຳເຂົ້າ | `purchase/receiving_po_list.py` |

---

## ໂຄງສ້າງ Layout — `frontend/pages/layout/`

### `layout/sidebar.py` — `class SidebarManager`
ຈັດການ Sidebar ເມນູດ້ານຊ້າຍ.
- `build()` — ສ້າງ sidebar ທັງໝົດ
- ເມນູ: Dashboard, Data Management (dropdown), ລົງທະບຽນ, ຮັບລົດ, ໃບສະເໜີ, ສ້ອມແປງ, ໃບບິນ, ຄັງອາໄຫຼ່, ຮັບເຂົ້າ, Reports (dropdown)
- `_update_selected_button()` — ໄຮໄລ້ເມນູທີ່ active ຕາມ index
- **ຂໍ້ສຳຄັນ**: `self.purchase_main_btn` → index 35, `self.receiving_main_btn` → index 36

### `layout/content_manager.py` — `class ContentManager`
ສ່ວນທີ່ເລືອກ ແລະ load ໜ້າຈໍຕາມ index.
- `switch_content(index)` — ດຶງ content ຂອງໜ້າທີ່ຕ້ອງການ
- ແຕ່ລະ `_get_xxx_content()` function → import class ຈາກໄຟລ໌ page ແລ້ວ `.build()`

### `layout/top_nav_bar.py` — `class TopNavBar`
Top bar: ຊື່ app, ຊື່ user, ປຸ່ມ logout, ປຸ່ມ toggle sidebar.

---

## ໂຄງສ້າງ App — ໄຟລ໌ຫຼັກ

### `pages/app_layout.py` — `class AppLayout`
⭐ **ໄຟລ໌ຄວບຄຸມຫຼັກ** ຂອງ App ຫຼັງ login.
- ຈັດການ state ທັງໝົດ: `current_index`, `sidebar_visible`, `sidebar_width`
- `navigate_to(page_name, **kwargs)` — ແປງຊື່ page ເປັນ index ແລ້ວ switch content
  - `kwargs` ທີ່ຮອງຮັບ: `customer_id`, `order_id`, `quotation_id`, `job_order_id`, `repair_id`, `po_id`, `promotion_id`, `invoice_id`, `read_only`
- `on_nav_click(index)` — ຈາກ sidebar ໂດຍກົງ
- `toggle_data_menu()`, `toggle_reports_menu()` — toggle dropdown menus
- ສ້າງ `SidebarManager`, `ContentManager`, `TopNavBar` ພ້ອມ inject ຕາມໂຄງສ້າງ

### `pages/login_page.py`
ໜ້າ Login — ຮັບ username + password, ເຊື່ອມ API `/login`, callback `on_login_success`.

### `pages/dashboard_page.py`
ໜ້າ Dashboard Wrapper — ສ້າງ `AppLayout` ຫຼັງ login.

### `pages/dashboard_content.py`
Content ພາຍໃນ Dashboard:
- ສະຖິຕິ: ຍອດຂາຍວັນນີ້, ເດືອນນີ້, ລົດທີ່ກຳລັງຊ້ອມ
- Chart: ລາຍຮັບ 6 ເດືອນ, Top services, Low stock alerts

### `pages/personal_page.py`
ໜ້າ Profile ຂອງ User — ແກ້ໄຂລະຫັດຜ່ານ, ດູຂໍ້ມູນສ່ວນຕົວ.

### `pages/promotion_items.py`
ໜ້າ Promotion Items — ຈັດການລາຍການ parts/services ທີ່ຢູ່ໃນໂປຣໂມຊັນ.

---

## ໜ້າ Management (Master Data)

### `Management/employees/employees_page.py`
ໜ້າຫຼັກຈັດການພະນັກງານ — ຕາຕະລາງ, ຄົ້ນຫາ, ປຸ່ມ CRUD.

### `Management/employees/employees_widgets.py`
Dialog/Form ເພີ່ມ/ແກ້ໄຂພະນັກງານ.

### `Management/supplier/suppliers_page.py`
ໜ້າຈັດການຜູ້ສະໜອງ — ຕາຕະລາງ, ຟອມ CRUD ຢູ່ໃນໄຟລ໌ດຽວ.

### `Management/service/services_page.py`
ໜ້າຈັດການລາຍການບໍລິການ — ລາຄາ, ຄ່າແຮງ, ໝວດໝູ່.

### `Management/parts/parts_page.py`
ໜ້າຫຼັກຈັດການອາໄຫຼ່ — ຕາຕະລາງ, ຄົ້ນຫາ, ແຈ້ງ low stock.

### `Management/parts/parts_dialogs.py`
Dialog: ເພີ່ມ/ແກ້ໄຂ/ລຶບອາໄຫຼ່, ກຳນົດ min_qty.

### `Management/store/shop_page.py`
ໜ້າຕັ້ງຄ່າຂໍ້ມູນຮ້ານ — ຊື່, ທີ່ຢູ່, ໂທ, ໂລໂກ້.

### `Management/promotion/promotions_page.py`
ໜ້າຫຼັກ Promotions — ສ້າງ/ແກ້ໄຂ/ລຶບ.

### `Management/promotion/promotions_dialogs.py`
Dialog ໃຫຍ່ຂອງ Promotions — ຟອມ CRUD ລາຍລະອຽດ.

### `Management/brands/brands_page.py`
ໜ້າຈັດການຍີ່ຫໍ້ລົດ.

### `Management/brands/brands_dialogs.py`
Dialog ເພີ່ມ/ແກ້ໄຂຍີ່ຫໍ້.

### `Management/units/units_page.py`
ໜ້າຈັດການໜ່ວຍວັດ (ຊິ້ນ, ລິດ, ກ່ອງ ...)

### `Management/units/units_dialogs.py`
Dialog CRUD ໜ່ວຍວັດ.

### `Management/part_categories/part_categories_page.py`
ໜ້າຈັດການໝວດໝູ່ອາໄຫຼ່.

### `Management/part_categories/part_categories_dialogs.py`
Dialog CRUD ໝວດໝູ່ອາໄຫຼ່.

---

## ໜ້າ Customers

### `customers/customer_list.py`
ໜ້າລາຍຊື່ລູກຄ້າ — ຄົ້ນຫາ, ດຶງລາຍລົດ, ນຳທາງໄປ register ໃໝ່ ຫຼື ແກ້ໄຂ.

### `customers/customer_dialogs.py`
Dialog ທຸກຢ່າງກ່ຽວກັບ customer: ລົງທະບຽນໃໝ່, ແກ້ໄຂ, ເພີ່ມ/ລຶບລົດ.

---

## ໜ້າ Job Orders (ໃບຮັບລົດ)

### `job_orders/job_order_create.py`
ໜ້າສ້າງໃບຮັບລົດ — ຄົ້ນຫາລູກຄ້າ, ເລືອກລົດ, ປ້ອນອາການ, ກຳນົດໜ້ານໍ້າມັນ + km.

### `job_orders/job_order_list.py`
ໜ້າລາຍຊື່ໃບຮັບລົດ — filter ຕາມສະຖານະ, ຄົ້ນຫາ, pagination.

### `job_orders/job_order_dialogs.py`
Dialog: ດູລາຍລະອຽດ, ອັບເດດສະຖານະ, ເປີດ dialog ສ້ອງ quotation.

### `job_orders/job_order_print.py`
ໜ້າ/Dialog preview PDF ໃບຮັບລົດ — ດຶງ PDF bytes ແລ້ວເປີດດ້ວຍ temp file.

---

## ໜ້າ Quotations (ໃບສະເໜີລາຄາ)

### `quotations/quotation_create.py`
⭐ ໜ້າ 2-Panel ສ້າງໃບສະເໜີ:
- ຊ້າຍ: ຄົ້ນຫາ Job Order + ລາຍຊື່ JO ທີ່ລໍຖ້າ
- ຂວາ: ເລືອກ parts/services, ຈຳນວນ, ສ່ວນຫຼຸດ, ຍອດລວມ
- ຮອງຮັບ Promotions

### `quotations/quotation_list.py`
ໜ້າລາຍຊື່ Quotations — filter, ຄົ້ນຫາ, pagination.

### `quotations/quotation_dialogs.py`
Dialog: ດູລາຍລະອຽດ quotation, ອັບເດດສະຖານະ, ພິມ PDF.

### `quotations/quotation_dialog_helpers.py`
Helper functions ສຳລັບ quotation dialogs (ສ້າງ widget ຊ້ຳໆ).

---

## ໜ້າ Repair (ສ້ອມແປງ)

### `repair/repair_create.py`
ໜ້າສ້າງໃບສັ່ງຊ້ອມ — ຈາກ approved quotation, ເລືອກຊ່າງ.

### `repair/repair_list.py`
ໜ້າລາຍຊື່ Repair Orders — filter ຕາມສະຖານະ, ຄົ້ນຫາ, ລາຍລະອຽດ.

### `repair/repair_detail.py`
ໜ້າລາຍລະອຽດ Repair — ສະຖານະ, ລາຍການ parts ທີ່ໃຊ້, ບໍລິການ, ອັບເດດ.

---

## ໜ້າ Invoices (ໃບບິນ)

### `invoices/invoice_create.py`
ໜ້າສ້າງໃບບິນ — ຈາກ completed repair order.

### `invoices/invoice_list.py`
⭐ ໜ້າລາຍຊື່ໃບບິນ — ສຳຄັນ:
- ປຸ່ມ "ຊຳລະ" → `show_payment_dialog()` → `pay_invoice()` → `show_post_payment_dialog()`
- `show_post_payment_dialog()` — popup ຫຼັງຊຳລະ: ພິມໃບສົ່ງມອບລົດ / ພິມໃບບິນ / ປິດ
- ແຖວ Paid invoice ມີປຸ່ມ truck icon → `print_delivery_note(invoice_id)`
- `print_delivery_note()` — ດຶງ PDF bytes ຈາກ `/invoices/{id}/delivery-note/pdf`

### `invoices/invoice_detail.py`
Dialog ລາຍລະອຽດໃບບິນ — ລາຍການ, ຍອດ, ສ່ວນຫຼຸດ, ຊ່ອງຊຳລະ.

---

## ໜ້າ Purchase (ຄັງອາໄຫຼ່ / ການຈັດຊື້)

### `purchase/purchase_management.py` — `class PurchaseManagementContent`
⭐ **ໜ້າຫຼັກຄັງອາໄຫຼ່** (index 23 ແລະ 35 ທັງ 2 ຊີ້ທີ່ນີ້):
- ສະແດງລາຍຊື່ PO ທັງໝົດ
- filter by status (all/pending/approved/completed/cancelled)
- ແຈ້ງ Low Stock ຜ່ານ notification badge
- ນຳທາງ: ກົດ "ສ້າງ PO" → `purchase_order_create.py`; ກົດ row → `purchase_order_detail.py`

### `purchase/purchase_order_create.py`
ໜ້າສ້າງ PO — ເລືອກ supplier, ເພີ່ມ parts + qty + unit_cost, ສົ່ງ.

### `purchase/purchase_order_detail.py`
ໜ້າລາຍລະອຽດ PO — ດູ items, ອັບເດດສະຖານະ, ນຳທາງໄປ receive.

### `purchase/receiving_management.py` — `class ReceivingManagementContent`
ໜ້າ "ຮັບເຂົ້າ" (index 36) — ລາຍຊື່ goods_receipts ທີ່ຮັບເຂົ້າແລ້ວ.
- ສ້ອງ "+ ສ້າງໃບນຳເຂົ້າ" → ນຳທາງ `receiving_po_list.py`

### `purchase/receiving_po_list.py` — `class ReceivingPoListContent`
⭐ **ໜ້າ 2-Panel ສ້າງໃບນຳເຂົ້າ** (index 37):
- ຊ້າຍ: ຄົ້ນຫາ + ລາຍຊື່ PO ທີ່ pending/approved ເທົ່ານັ້ນ (ຕັດ completed/cancelled)
- ຂວາ: ສະແດງ items ຂອງ PO ທີ່ເລືອກ — ປ້ອນ receive_qty ແລະ unit_cost
- "ຢືນຢັນການນຳເຂົ້າ" → `receive_purchase_order()` → ອັບ stock ອັດຕະໂນມັດ + refresh

### `purchase/goods_receipt_list.py`
ໜ້າ Goods Receipt (ໂຕເກົ່າ) — ລາຍຊື່ goods receipts.

### `purchase/stock_movement.py`
ໜ້າ Stock Movement History — ດູປະຫວັດການຈ່າຍ/ຮັບເຂົ້າຂອງອາໄຫຼ່.

---

## ໜ້າ Reports

### `reports/revenue_report.py`
ລາຍງານລາຍຮັບ — ຍອດໃບບິນ, ຕົ້ນທຶນ, ກຳໄລ (filter by date range).

### `reports/repair_summary_report.py`
ສະຫຼຸບການຊ້ອມ — ສະຖານະ, ໄລຍະ, ຍີ່ຫໍ້ລົດ.

### `reports/parts_service_sales_report.py`
ຍອດນຳໃຊ້ອາໄຫຼ່ + ບໍລິການ — ອາໄຫຼ່ທີ່ໃຊ້ຫຼາຍ, low stock.

### `reports/mechanic_performance_report.py`
ປະສິດທິພາບຊ່າງ — ຈຳນວນລົດ, ໄລຍະ, rating.

### `reports/promotion_usage_report.py`
ການນຳໃຊ້ໂປຣໂມຊັນ — ຈຳນວນໃຊ້, ສ່ວນຫຼຸດທີ່ໃຫ້.

---

## Theme & Components

### `theme/app_theme.py`
ຕັ້ງຄ່າ Theme ຂອງ Flet App — ສີຫຼັກ, fonts, color scheme.

### `components/language_switcher.py`
Widget ສ່ວນປ່ຽນພາສາ (dropdown Lao/English).

---

## ໄຟລ໌ Root ອື່ນໆ

### `jp_auto_db.sql`
⭐ SQL dump ຂອງ Database ທັງໝົດ:
- ຕາຕະລາງຫຼັກ: `employees`, `shop`, `suppliers`, `services`, `parts`, `promotions`, `customers`, `vehicles`, `job_orders`, `quotations`, `quotation_items`, `repair_orders`, `repair_parts`, `repair_services`, `invoices`, `purchase_orders`, `purchase_order_items`, `goods_receipts`, `stock_movements`, `brands`, `units`, `part_categories`
- ຂໍ້ສຳຄັນ: `job_orders.status` enum = `pending|in_progress|completed|cancelled`
- ຂໍ້ສຳຄັນ: `invoices.status` = `unpaid|paid`

### `jp_auto_api.json`
Postman Collection — ທຸກ API endpoint ຂອງລະບົບ (ໃຊ້ test ດ້ວຍ Postman ຫຼື Insomnia).

### `SYSTEM_OVERVIEW.md`
ເອກະສານລະດັບສູງ — DFD, Workflow sequence diagram, Roles, Technical stack.

---

## ຄວາມສຳພັນລະຫວ່າງໄຟລ໌ (Key Dependencies)

```
frontend/main.py
  └── pages/login_page.py          ← ເຂົ້າສູ່ລະບົບ
       └── pages/dashboard_page.py ← ຫຼັງ login
            └── pages/app_layout.py ← ຄວບຄຸມທັງໝົດ
                 ├── pages/layout/sidebar.py      ← ເມນູ
                 ├── pages/layout/content_manager.py ← load ໜ້າ
                 └── pages/layout/top_nav_bar.py  ← bar ເທິງ

ທຸກໜ້າ (page class) → api_client.APIClient → backend FastAPI → MySQL
```

## ຂໍ້ສຳຄັນສຳລັບ AI (Notes for AI)

1. **Navigation**: ໃຊ້ `self.navigate("page_name", **kwargs)` ໃນໜ້າ, ຮອງຮັບ kwargs ຄື `po_id`, `invoice_id`, `job_order_id` ແລະ `read_only`.
2. **Flet Constraints**: `ft.alignment.center` ບໍ່ຮອງຮັບ → ໃຊ້ `ft.Alignment(0, 0)`. TextField ໃຊ້ `text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)` ແທນ `weight`.
3. **API Client**: ທຸກ method ຢູ່ໃນ `api_client.py`. ຖ້າ endpoint ໃໝ່ → ເພີ່ມ method ທີ່ນີ້ກ່ອນ.
4. **PDF**: ທຸກ PDF generator ຢູ່ໃນ `backend/utils_pdf.py`. ທຸກ endpoint PDF ຢູ່ໃນ router ທີ່ກ່ຽວຂ້ອງ (ບໍ່ແຍກໄຟລ໌).
5. **i18n**: ເພີ່ມ translation key ໃໝ່ທຸກຄັ້ງຕ້ອງເພີ່ມທັງ `LO` ແລະ `EN` dict.
6. **Database connection**: ທຸກ router ໃຊ້ `from database import get_db` ແລ້ວ `db = get_db()` → `cursor = db.cursor(dictionary=True)` → `cursor.close(); db.close()`.
7. **Purchase flow**: PO create → PO approve → Receive (receiving_po_list) → stock updated → goods_receipt created.
8. **Invoice flow**: Repair complete → Invoice create → Pay → show_post_payment_dialog → print delivery note or invoice PDF.
