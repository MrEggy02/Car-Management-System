import requests
import os
from typing import Dict, Any, List, Optional

API_BASE_URL = "http://127.0.0.1:8000"


class APIClient:
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password

    def _get_auth(self):
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        params: Dict = None,
        files: Dict = None,
    ) -> Any:
        url = f"{API_BASE_URL}{endpoint}"
        auth = self._get_auth()

        try:
            if method == "GET":
                response = requests.get(url, auth=auth, params=params)
            elif method == "POST":
                response = requests.post(
                    url, auth=auth, params=params, data=data, files=files
                )
            elif method == "PUT":
                response = requests.put(
                    url, auth=auth, params=params, data=data, files=files
                )
            elif method == "DELETE":
                response = requests.delete(url, auth=auth, params=params)
            else:
                raise ValueError(f"Unknown method: {method}")

            # Debug logging
            print(f"=== REQUEST DEBUG ===")
            print(f"URL: {url}")
            print(f"Method: {method}")
            print(f"Status Code: {response.status_code}")
            if response.text:
                print(f"Response Text: {response.text[:500]}")

            if response.status_code == 200:
                if method == "GET" and not response.content:
                    return response.content
                try:
                    return response.json()
                except:
                    return response.content
            else:
                try:
                    error_msg = response.json().get(
                        "detail", f"HTTP {response.status_code}"
                    )
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            raise Exception("ບໍ່ສາມາດເຊື່ອມຕໍ່ກັບ Server ໄດ້ ກະລຸນາເປີດ Backend")
        except requests.exceptions.Timeout:
            raise Exception("ການເຊື່ອມຕໍ່ໝົດເວລາ ກະລຸນາລອງໃໝ່")
        except Exception as e:
            raise Exception(str(e))

    # ========== Authentication ==========
    def login(self, username: str, password: str) -> Dict:
        """ล็อกอินเข้าสู่ระบบ"""
        self.username = username
        self.password = password
        return self._request("POST", "/login", data={"username": username, "password": password})

    # ========== Process 1.1: Employees ==========
    def get_employees(self) -> List[Dict]:
        """ดึงข้อมูลพนักงานทั้งหมด"""
        return self._request("GET", "/employees")

    def add_employee(
        self, 
        name: str, 
        phone: str = "", 
        role: str = "mechanic",
        status: str = "active",
        can_login: bool = False,
        username: str = None,
        password: str = None
    ) -> Dict:
        """เพิ่มพนักงานใหม่"""
        data = {
            "name": name,
            "phone": phone,
            "role": role,
            "status": status,
            "can_login": can_login,
        }
        if username:
            data["username"] = username
        if password:
            data["password"] = password
        
        return self._request("POST", "/employees", data=data)

    def update_employee(self, emp_id: int, data: Dict) -> Dict:
        """อัปเดตข้อมูลพนักงาน"""
        return self._request("PUT", f"/employees/{emp_id}", data=data)

    def delete_employee(self, employee_id: int) -> Dict:
        """ลบพนักงาน"""
        return self._request("DELETE", f"/employees/{employee_id}")

    def get_mechanics(self) -> List[Dict]:
        """ดึงข้อมูลช่างซ่อมทั้งหมด"""
        return self._request("GET", "/employees/mechanics")

    def change_password(self, current_password: str, new_password: str) -> Dict:
        """เปลี่ยนรหัสผ่านของตัวเอง"""
        return self._request("POST", "/employees/change-password", data={
            "current_password": current_password,
            "new_password": new_password
        })

    # ========== Process 1.2: Shop Info ==========
    def get_shop(self) -> Dict:
        return self._request("GET", "/shop")

    def update_shop(
        self,
        name: str,
        address: str,
        phone: str,
    ) -> Dict:
        return self._request(
            "PUT",
            "/shop",
            data={
                "name": name,
                "address": address,
                "phone": phone,
            },
        )

    def upload_shop_logo(self, logo_path: str) -> Dict:
        url = f"{API_BASE_URL}/shop/logo"
        auth = self._get_auth()

        try:
            with open(logo_path, "rb") as f:
                files = {"logo": (os.path.basename(logo_path), f, "image/png")}
                response = requests.post(url, auth=auth, files=files)

                if response.status_code == 200:
                    return response.json()
                else:
                    try:
                        error_msg = response.json().get(
                            "detail", f"HTTP {response.status_code}"
                        )
                    except:
                        error_msg = response.text or f"HTTP {response.status_code}"
                    raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to server. Please start the backend.")
        except Exception as e:
            raise Exception(f"Error uploading logo: {e}")

    def delete_shop_logo(self) -> Dict:
        url = f"{API_BASE_URL}/shop/logo"
        auth = self._get_auth()

        try:
            response = requests.delete(url, auth=auth)
            if response.status_code == 200:
                return response.json()
            else:
                try:
                    error_msg = response.json().get(
                        "detail", f"HTTP {response.status_code}"
                    )
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to server. Please start the backend.")
        except Exception as e:
            raise Exception(f"Error deleting logo: {e}")

    def get_shop_logo(self) -> Optional[bytes]:
        url = f"{API_BASE_URL}/shop/logo"
        auth = self._get_auth()

        try:
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                return response.content
            else:
                return None
        except requests.exceptions.ConnectionError:
            return None
        except:
            return None

    # ========== Process 1.3: Suppliers ==========
    def get_suppliers(self) -> List[Dict]:
        return self._request("GET", "/suppliers")

    def add_supplier(
        self,
        name: str,
        contact_person: str = "",
        phone: str = "",
        email: str = "",
        address: str = "",
    ) -> Dict:
        return self._request(
            "POST",
            "/suppliers",
            data={
                "name": name,
                "contact_person": contact_person,
                "phone": phone,
                "email": email,
                "address": address,
            },
        )

    def update_supplier(
        self,
        supplier_id: int,
        name: str,
        contact_person: str = "",
        phone: str = "",
        email: str = "",
        address: str = "",
    ) -> Dict:
        return self._request(
            "PUT",
            f"/suppliers/{supplier_id}",
            data={
                "name": name,
                "contact_person": contact_person,
                "phone": phone,
                "email": email,
                "address": address,
            },
        )

    def delete_supplier(self, supplier_id: int) -> Dict:
        return self._request("DELETE", f"/suppliers/{supplier_id}")

    # ========== Process 1.4: Services ==========
    def get_services(self) -> List[Dict]:
        return self._request("GET", "/services")

    def add_service(
        self,
        name: str,
        price: float = 0,
        description: str = "",
        estimated_time: int = 0
    ) -> Dict:
        return self._request(
            "POST",
            "/services",
            data={
                "name": name,
                "price": price,
                "description": description,
                "estimated_time": estimated_time,
            },
        )

    def update_service(self, service_id: int, data: Dict) -> Dict:
        return self._request("PUT", f"/services/{service_id}", data=data)

    def delete_service(self, service_id: int) -> Dict:
        return self._request("DELETE", f"/services/{service_id}")

    def search_services(self, keyword: str = "") -> List[Dict]:
        params = {"keyword": keyword} if keyword else None
        return self._request("GET", "/search-services", params=params)

    # ========== Process 1.5: Parts ==========
    def get_parts(self) -> List[Dict]:
        return self._request("GET", "/parts")

    def add_part(
        self,
        name: str,
        cost_price: float = 0,
        sell_price: float = 0,
        stock_qty: int = 0,
        min_stock: int = 5,
        unit: str = "ຊິ້ນ",
        supplier_id: Optional[int] = None
    ) -> Dict:
        data = {
            "name": name,
            "cost_price": cost_price,
            "sell_price": sell_price,
            "stock_qty": stock_qty,
            "min_stock": min_stock,
            "unit": unit,
        }
        if supplier_id:
            data["supplier_id"] = supplier_id
        return self._request("POST", "/parts", data=data)

    def update_part(self, part_id: int, data: Dict) -> Dict:
        return self._request("PUT", f"/parts/{part_id}", data=data)

    def delete_part(self, part_id: int) -> Dict:
        return self._request("DELETE", f"/parts/{part_id}")

    def get_low_stock_parts(self) -> List[Dict]:
        return self._request("GET", "/parts/low-stock")

    def search_parts(self, keyword: str = "") -> List[Dict]:
        params = {"keyword": keyword} if keyword else None
        return self._request("GET", "/search-parts", params=params)

    # ========== Process 1.6: Promotions ==========
    def get_promotions(self) -> List[Dict]:
        return self._request("GET", "/promotions")

    def add_promotion(
        self,
        name: str,
        discount_type: str,
        value: float,
        min_qty: int = 1,
        min_amount: float = 0,
        start_date: str = None,
        end_date: str = None,
        status: str = "active"
    ) -> Dict:
        return self._request(
            "POST",
            "/promotions",
            data={
                "name": name,
                "discount_type": discount_type,
                "value": value,
                "min_qty": min_qty,
                "min_amount": min_amount,
                "start_date": start_date,
                "end_date": end_date,
                "status": status,
            },
        )

    def update_promotion(self, promo_id: int, data: Dict) -> Dict:
        return self._request("PUT", f"/promotions/{promo_id}", data=data)

    def delete_promotion(self, promo_id: int) -> Dict:
        return self._request("DELETE", f"/promotions/{promo_id}")

    def validate_promotion(self, promo_name: str, total_amount: float, quantity: int = 1) -> Dict:
        return self._request(
            "POST", 
            "/promotions/validate", 
            data={"promo_name": promo_name, "total_amount": total_amount, "quantity": quantity}
        )

    def get_active_promotions(self) -> List[Dict]:
        return self._request("GET", "/promotions/active")

    # ========== Promotion Items ==========
    def get_promotion_items(self, promotion_id: int) -> List[Dict]:
        return self._request("GET", f"/promotions/{promotion_id}/items")

    def add_promotion_item(self, promotion_id: int, item_type: str, item_id: int) -> Dict:
        return self._request(
            "POST",
            f"/promotions/{promotion_id}/items",
            data={
                "item_type": item_type,
                "item_id": item_id
            }
        )

    def delete_promotion_item(self, promotion_id: int, item_id: int) -> Dict:
        return self._request("DELETE", f"/promotions/{promotion_id}/items/{item_id}")

    def clear_promotion_items(self, promotion_id: int) -> Dict:
        return self._request("DELETE", f"/promotions/{promotion_id}/items")

    def get_available_parts_for_promotion(self, promotion_id: int, search: str = "") -> List[Dict]:
        params = {"search": search} if search else None
        return self._request("GET", f"/promotions/{promotion_id}/available-parts", params=params)

    def get_available_services_for_promotion(self, promotion_id: int, search: str = "") -> List[Dict]:
        params = {"search": search} if search else None
        return self._request("GET", f"/promotions/{promotion_id}/available-services", params=params)

    def validate_promotion_for_items(self, promotion_id: int, part_ids: List[int] = None, service_ids: List[int] = None) -> Dict:
        import json
        item_ids = {
            "parts": part_ids or [],
            "services": service_ids or []
        }
        return self._request(
            "POST",
            "/promotions/validate-for-items",
            data={
                "promotion_id": promotion_id,
                "item_ids": json.dumps(item_ids)
            }
        )

    # ========== Process 2: Customers & Vehicles ==========
    def get_customers(self) -> List[Dict]:
        return self._request("GET", "/customers")

    def add_customer(self, name: str, phone: str = "", address: str = "") -> Dict:
        return self._request(
            "POST",
            "/customers",
            data={"name": name, "phone": phone, "address": address},
        )

    def update_customer(self, customer_id: int, customer_data: Dict) -> Dict:
        return self._request("PUT", f"/customers/{customer_id}", data=customer_data)

    def delete_customer(self, customer_id: int) -> Dict:
        return self._request("DELETE", f"/customers/{customer_id}")

    def get_vehicles(self, customer_id: int = None) -> List[Dict]:
        params = {"customer_id": customer_id} if customer_id else None
        return self._request("GET", "/vehicles", params=params)

    def get_vehicle(self, vehicle_id: int) -> Dict:
        return self._request("GET", f"/vehicles/{vehicle_id}")

    def add_vehicle(self, vehicle_data: Dict) -> Dict:
        return self._request("POST", "/vehicles", data=vehicle_data)

    def update_vehicle(self, vehicle_id: int, vehicle_data: Dict) -> Dict:
        return self._request("PUT", f"/vehicles/{vehicle_id}", data=vehicle_data)

    def delete_vehicle(self, vehicle_id: int) -> Dict:
        return self._request("DELETE", f"/vehicles/{vehicle_id}")

    def get_brands(self) -> List[Dict]:
        """Get all vehicle brands"""
        return self._request("GET", "/brands")
    
    def add_brand(self, name: str, status: str = "active") -> Dict:
        """Add new brand"""
        return self._request("POST", "/brands", data={
            "name": name,
            "status": status
        })
        
    def update_brand(self, brand_id: int, name: str, status: str) -> Dict:
        """Update brand"""
        return self._request("PUT", f"/brands/{brand_id}", data={
            "name": name,
            "status": status
        })
    
    def delete_brand(self, brand_id: int) -> Dict:
        """Delete brand"""
        return self._request("DELETE", f"/brands/{brand_id}")
    
    def get_active_brands(self) -> List[Dict]:
        """Get active brands only"""
        return self._request("GET", "/brands/active")
 
    def register_customer_with_vehicle(
        self, customer_data: Dict, vehicle_data: Dict
    ) -> Dict:
        data = {**customer_data, **vehicle_data}
        return self._request("POST", "/register_customer", data=data)

    # ========== Process 3: Job Orders ==========
    def create_job_order(
        self,
        customer_id: int,
        vehicle_id: int,
        problem_description: str,
        mileage: int = 0,
        fuel_level: str = "",
    ) -> Dict:
        return self._request(
            "POST",
            "/job-orders",
            data={
                "customer_id": customer_id,
                "vehicle_id": vehicle_id,
                "problem_description": problem_description,
                "mileage": mileage,
                "fuel_level": fuel_level,
            },
        )

    def get_job_orders(self, status: str = None) -> List[Dict]:
        params = {"status": status} if status else None
        return self._request("GET", "/job-orders", params=params)

    def get_job_order(self, order_id: int) -> Dict:
        return self._request("GET", f"/job-orders/{order_id}")

    def update_job_order(self, order_id: int, **kwargs) -> Dict:
        return self._request("PUT", f"/job-orders/{order_id}", data=kwargs)

    def delete_job_order(self, order_id: int) -> Dict:
        return self._request("DELETE", f"/job-orders/{order_id}")

    # ========== Process 4: Quotations ==========
    def get_quotations(self, job_order_id: int = None) -> List[Dict]:
        params = {"job_order_id": job_order_id} if job_order_id else None
        return self._request("GET", "/quotations", params=params)

    def get_quotation(self, quotation_id: int) -> Dict:
        return self._request("GET", f"/quotations/{quotation_id}")

    def create_quotation(self, job_order_id: int, valid_until: str = None, notes: str = "") -> Dict:
        data = {"job_order_id": job_order_id, "notes": notes}
        if valid_until:
            data["valid_until"] = valid_until
        return self._request("POST", "/quotations", data=data)

    def add_quotation_item(self, quotation_id: int, item_type: str, ref_id: int, qty: int = 1) -> Dict:
        return self._request(
            "POST",
            f"/quotations/{quotation_id}/items",
            data={"item_type": item_type, "ref_id": ref_id, "qty": qty},
        )

    def update_quotation_item(self, quotation_id: int, item_id: int, qty: int, discount_amount: float = 0) -> Dict:
        return self._request(
            "PUT",
            f"/quotations/{quotation_id}/items/{item_id}",
            data={"qty": qty, "discount_amount": discount_amount},
        )

    def delete_quotation_item(self, quotation_id: int, item_id: int) -> Dict:
        return self._request("DELETE", f"/quotations/{quotation_id}/items/{item_id}")

    def calculate_quotation_total(self, quotation_id: int) -> Dict:
        return self._request("PUT", f"/quotations/{quotation_id}/calculate")

    def update_quotation_status(self, quotation_id: int, status: str) -> Dict:
        return self._request(
            "PUT", f"/quotations/{quotation_id}/status", data={"status": status}
        )

    def delete_quotation(self, quotation_id: int) -> Dict:
        return self._request("DELETE", f"/quotations/{quotation_id}")

    # ========== Process 5: Repair Management ==========
    def get_repair_orders(self, job_order_id: int = None, status: str = None) -> List[Dict]:
        params = {}
        if job_order_id:
            params["job_order_id"] = job_order_id
        if status:
            params["status"] = status
        return self._request("GET", "/repair-orders", params=params)

    def get_repair_order(self, repair_id: int) -> Dict:
        return self._request("GET", f"/repair-orders/{repair_id}")

    def create_repair_order(self, job_order_id: int, mechanic_id: int = None) -> Dict:
        data = {"job_order_id": job_order_id}
        if mechanic_id:
            data["mechanic_id"] = mechanic_id
        return self._request("POST", "/repair-orders", data=data)

    def assign_mechanic(self, repair_id: int, mechanic_id: int) -> Dict:
        return self._request(
            "PUT", f"/repair-orders/{repair_id}/mechanic", data={"mechanic_id": mechanic_id}
        )

    def update_repair_status(self, repair_id: int, status: str) -> Dict:
        return self._request(
            "PUT", f"/repair-orders/{repair_id}/status", data={"status": status}
        )

    def add_part_usage(self, repair_id: int, part_id: int, qty: int, note: str = None) -> Dict:
        data = {"part_id": part_id, "qty": qty}
        if note:
            data["note"] = note
        return self._request(
            "POST",
            f"/repair-orders/{repair_id}/parts-usage",
            data=data
        )

    def delete_part_usage(self, repair_id: int, usage_id: int) -> Dict:
        return self._request("DELETE", f"/repair-orders/{repair_id}/parts-usage/{usage_id}")

    # ========== Process 6: Invoice Management ==========
    def get_invoices(self, job_order_id: int = None, payment_status: str = None) -> List[Dict]:
        params = {}
        if job_order_id:
            params["job_order_id"] = job_order_id
        if payment_status:
            params["payment_status"] = payment_status
        return self._request("GET", "/invoices", params=params)

    def get_invoice(self, invoice_id: int) -> Dict:
        return self._request("GET", f"/invoices/{invoice_id}")

    def get_invoice_info_by_job_order(self, job_order_id: int) -> Dict:
        return self._request("GET", f"/job-orders/{job_order_id}/invoice-info")

    def create_invoice(
        self,
        job_order_id: int,
        total_amount: float,
        total_discount: float,
        final_total: float,
        payment_method: str = "cash",
        payment_status: str = "pending",
        received_amount: float = 0,
        change_amount: float = 0
    ) -> Dict:
        return self._request("POST", "/invoices", data={
            "job_order_id": job_order_id,
            "total_amount": total_amount,
            "total_discount": total_discount,
            "final_total": final_total,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "received_amount": received_amount,
            "change_amount": change_amount
        })

    def record_payment(self, invoice_id: int, payment_method: str, received_amount: float, change_amount: float) -> Dict:
        return self._request("PUT", f"/invoices/{invoice_id}/payment", data={
            "payment_method": payment_method,
            "received_amount": received_amount,
            "change_amount": change_amount
        })

    def update_invoice_status(self, invoice_id: int, payment_status: str) -> Dict:
        return self._request("PUT", f"/invoices/{invoice_id}/status", data={
            "payment_status": payment_status
        })

    def delete_invoice(self, invoice_id: int) -> Dict:
        return self._request("DELETE", f"/invoices/{invoice_id}")

    # ========== Process 7: Stock Management (Purchase Orders) ==========
    def get_purchase_orders(self, status: str = None) -> List[Dict]:
        params = {"status": status} if status else None
        return self._request("GET", "/purchase-orders", params=params)

    def get_purchase_order(self, po_id: int) -> Dict:
        return self._request("GET", f"/purchase-orders/{po_id}")

    def create_purchase_order(self, supplier_id: int, items: List[Dict]) -> Dict:
        import json
        return self._request("POST", "/purchase-orders", data={
            "supplier_id": supplier_id,
            "items": json.dumps(items)
        })

    def update_purchase_order_status(self, po_id: int, status: str) -> Dict:
        return self._request("PUT", f"/purchase-orders/{po_id}/status", data={
            "status": status
        })

    def receive_purchase_order(self, po_id: int, received_items: List[Dict]) -> Dict:
        import json
        return self._request("POST", f"/purchase-orders/{po_id}/receive", data={
            "received_items": json.dumps(received_items)
        })

    def delete_purchase_order(self, po_id: int) -> Dict:
        return self._request("DELETE", f"/purchase-orders/{po_id}")

    def get_stock_movements(self, part_id: int = None, limit: int = 50) -> List[Dict]:
        params = {}
        if part_id:
            params["part_id"] = part_id
        if limit:
            params["limit"] = limit
        return self._request("GET", "/stock-movements", params=params)

    # ========== Legacy/Backward Compatibility ==========
    def register_customer_with_car(self, customer_data: Dict, car_data: Dict) -> Dict:
        return self.register_customer_with_vehicle(customer_data, car_data)

    def get_cars(self, customer_id: int = None) -> List[Dict]:
        return self.get_vehicles(customer_id)

    def add_car(self, car_data: Dict) -> Dict:
        return self.add_vehicle(car_data)

    def update_car(self, car_id: int, car_data: Dict) -> Dict:
        return self.update_vehicle(car_id, car_data)

    def delete_car(self, car_id: int) -> Dict:
        return self.delete_vehicle(car_id)

    def update_car_info(self, car_id: int, car_data: Dict) -> Dict:
        return self.update_vehicle(car_id, car_data)

    # ========== Process 8: Reports ==========
    def get_revenue_report(self, start_date: str = None, end_date: str = None) -> Dict:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/revenue", params=params)

    def get_repair_summary_report(self, start_date: str = None, end_date: str = None) -> Dict:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/repair-summary", params=params)

    def get_parts_usage_report(self, start_date: str = None, end_date: str = None) -> Dict:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/parts-usage", params=params)

    def get_top_services_report(self, start_date: str = None, end_date: str = None) -> Dict:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/top-services", params=params)

    def get_promotion_usage_report(self, start_date: str = None, end_date: str = None) -> Dict:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/promotion-usage", params=params)

    def get_dashboard_summary(self) -> Dict:
        return self._request("GET", "/reports/dashboard-summary")

    def get_service_items_report(self, start_date: str = None, end_date: str = None) -> Dict:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/service-items", params=params)
    
    # Add these methods to APIClient class

# ========== Units ==========
    def get_units(self) -> List[Dict]:
        """Get all units"""
        return self._request("GET", "/units")

    def add_unit(self, name: str, status: str = "active") -> Dict:
        """Add new unit"""
        return self._request("POST", "/units", data={"name": name, "status": status})

    def update_unit(self, unit_id: int, name: str, status: str) -> Dict:
        """Update unit"""
        return self._request("PUT", f"/units/{unit_id}", data={"name": name, "status": status})

    def delete_unit(self, unit_id: int) -> Dict:
        """Delete unit"""
        return self._request("DELETE", f"/units/{unit_id}")

    def get_active_units(self) -> List[Dict]:
        """Get active units only"""
        return self._request("GET", "/units/active")

# ========== Part Categories ==========
    def get_part_categories(self) -> List[Dict]:
        """Get all part categories"""
        return self._request("GET", "/part-categories")

    def add_part_category(self, name: str, status: str = "active") -> Dict:
        """Add new part category"""
        return self._request("POST", "/part-categories", data={"name": name, "status": status})

    def update_part_category(self, category_id: int, name: str, status: str) -> Dict:
        """Update part category"""
        return self._request("PUT", f"/part-categories/{category_id}", data={"name": name, "status": status})

    def delete_part_category(self, category_id: int) -> Dict:
        """Delete part category"""
        return self._request("DELETE", f"/part-categories/{category_id}")

    def get_active_part_categories(self) -> List[Dict]:
        """Get active part categories only"""
        return self._request("GET", "/part-categories/active")