import requests
import os
from typing import Dict, Any, List, Optional

API_BASE_URL = "http://127.0.0.1:8000"


class APIClient:
    GLOBAL_MOCK_MODE = False

    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.mock_mode = False

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
            try:
                print(f"=== REQUEST DEBUG ===")
                print(f"URL: {url}")
                print(f"Method: {method}")
                print(f"Status Code: {response.status_code}")
                if response.text:
                    import sys
                    enc = getattr(sys.stdout, 'encoding', 'utf-8') or 'utf-8'
                    safe_text = response.text[:500].encode(enc, errors='replace').decode(enc)
                    print(f"Response Text: {safe_text}")
            except Exception:
                pass

            if response.status_code == 200:
                if method == "GET" and not response.content:
                    return response.content
                try:
                    res_json = response.json()
                    if getattr(self, "mock_mode", False):
                        return self._mask_data(res_json, endpoint)
                    return res_json
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

    def _mask_data(self, data, endpoint=""):
        if not getattr(self, "mock_mode", False):
            return data

        import copy
        
        # Define replacements for specific sensitive keys
        SENSITIVE_REPLACEMENTS = {
            "customer_name": "ລູກຄ້າ ຕົວຢ່າງ (Demo Customer)",
            "fullname": "ຜູ້ໃຊ້ ຕົວຢ່າງ (Demo User)",
            "contact_person": "ຜູ້ຕິດຕໍ່ ຕົວຢ່າງ (Demo Contact)",
            "mechanic_name": "ຊ່າງຊ້ອມ ຕົວຢ່າງ (Demo Mechanic)",
            "creator_name": "ຜູ້ສ້າງ ຕົວຢ່າງ (Demo Creator)",
            "phone": "020-XXXX-XXXX",
            "customer_phone": "020-XXXX-XXXX",
            "email": "demo_email@example.com",
            "address": "ນະຄອນຫຼວງວຽງຈັນ (Vientiane, Laos)",
            "plate_number": "ກກ XXXX",
            "chassis_number": "XXXX-CHASSIS-XXXX",
            "engine_number": "XXXX-ENGINE-XXXX",
            "username": "demo_user",
            "problem_description": "ລາຍລະອຽດອາການເພຕົວຢ່າງ (Demo symptom description...)",
            "note": "ໝາຍເຫດຕົວຢ່າງ (Demo note...)",
            "shop_name": "ອູ່ສ້ອມແປງລົດ ຕົວຢ່າງ J&P",
        }

        # Handle deep copy to avoid mutating cache in-place
        data_copy = copy.deepcopy(data)

        def walk(obj, parent_key=None, current_endpoint=""):
            if isinstance(obj, list):
                return [walk(item, parent_key, current_endpoint) for item in obj]
            elif isinstance(obj, dict):
                # Guess context based on dict structure or endpoint
                is_employee = "role" in obj or "can_login" in obj
                is_supplier = "contact_person" in obj or "email" in obj
                is_customer = "phone" in obj and "address" in obj and not is_employee and not is_supplier
                is_shop = "address" in obj and "phone" in obj and current_endpoint.endswith("/shop")

                new_dict = {}
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        new_dict[k] = walk(v, k, current_endpoint)
                    elif isinstance(v, str):
                        # Direct replacements
                        if k in SENSITIVE_REPLACEMENTS:
                            new_dict[k] = SENSITIVE_REPLACEMENTS[k]
                        elif k == "name":
                            if is_employee:
                                new_dict[k] = "ພະນັກງານ ຕົວຢ່າງ (Demo Employee)"
                            elif is_supplier:
                                new_dict[k] = "ບໍລິສັດສະໜອງ ຕົວຢ່າງ (Demo Supplier)"
                            elif is_customer or "customer" in current_endpoint:
                                new_dict[k] = "ລູກຄ້າ ຕົວຢ່າງ (Demo Customer)"
                            elif is_shop or current_endpoint.endswith("/shop"):
                                new_dict[k] = "ອູ່ J&P Auto Maxing (ຕົວຢ່າງ)"
                            else:
                                # Keep original name for services, parts, categories, brands, units
                                new_dict[k] = v
                        else:
                            new_dict[k] = v
                    else:
                        new_dict[k] = v
                return new_dict
            return obj

        return walk(data_copy, current_endpoint=endpoint)

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
        unit_id: Optional[int] = None,
        category_id: Optional[int] = None,
        supplier_id: Optional[int] = None
    ) -> Dict:
        data = {
            "name": name,
            "cost_price": cost_price,
            "sell_price": sell_price,
            "stock_qty": stock_qty,
            "min_stock": min_stock,
            
        }
        if unit_id:
            data["unit_id"] = unit_id
        if category_id:
            data["category_id"] = category_id
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
        """Get all customers"""
        return self._request("GET", "/customers")

    def get_customers_with_vehicles(self) -> List[Dict]:
        """Get all customers with vehicle count in one query (FASTER)"""
        try:
            return self._request("GET", "/customers-with-vehicles")
        except:
            return []

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
        car_defects: str = "",
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
                "car_defects": car_defects,
                "mileage": mileage,
                "fuel_level": fuel_level,
            },
        )

    def get_job_orders(self, status: str = None) -> List[Dict]:
        params = {"status": status} if status else None
        return self._request("GET", "/job-orders", params=params)

    def get_job_order(self, order_id: int) -> Dict:
        return self._request("GET", f"/job-orders/{order_id}")

    def get_job_order_pdf(self, order_id: int) -> bytes:
        """Get job order PDF as bytes"""
        return self._request("GET", f"/job-orders/{order_id}/pdf")

    def update_job_order(self, order_id: int, **kwargs) -> Dict:
        return self._request("PUT", f"/job-orders/{order_id}", data=kwargs)

    def upload_job_order_receipt(self, order_id: int, receipt_path: str) -> Dict:
        url = f"{API_BASE_URL}/job-orders/{order_id}/upload-receipt"
        auth = self._get_auth()
        try:
            with open(receipt_path, "rb") as f:
                files = {"receipt": (os.path.basename(receipt_path), f, "image/png")}
                response = requests.post(url, auth=auth, files=files)
                if response.status_code == 200:
                    return response.json()
                else:
                    try:
                        error_msg = response.json().get("detail", f"HTTP {response.status_code}")
                    except:
                        error_msg = response.text or f"HTTP {response.status_code}"
                    raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to server. Please start the backend.")
        except Exception as e:
            raise Exception(f"Error uploading receipt: {e}")

    def get_job_order_receipt_url(self, order_id: int) -> str:
        return f"{API_BASE_URL}/job-orders/{order_id}/receipt"

    def delete_job_order(self, order_id: int) -> Dict:
        return self._request("DELETE", f"/job-orders/{order_id}")

    # ========== Process 4: Quotations ==========
    def get_quotations(self, job_order_id: int = None) -> List[Dict]:
        params = {"job_order_id": job_order_id} if job_order_id else None
        return self._request("GET", "/quotations", params=params)

    def get_quotation(self, quotation_id: int) -> Dict:
        return self._request("GET", f"/quotations/{quotation_id}")

    def get_quotation_pdf(self, quotation_id: int) -> bytes:
        """Get quotation PDF as bytes"""
        return self._request("GET", f"/quotations/{quotation_id}/pdf")

    def get_quotation_items(self, quotation_id: int) -> List[Dict]:
        """Get all items for a quotation"""
        return self._request("GET", f"/quotations/{quotation_id}/items")

    def create_quotation(self, job_order_id: int, promotion_id: int = None) -> Dict:
        data = {"job_order_id": job_order_id}
        if promotion_id:
            data["promotion_id"] = promotion_id
        return self._request("POST", "/quotations", data=data)

    def add_quotation_item(self, quotation_id: int, item_type: str, ref_id: int, qty: int = 1, discount_amount: float = 0, custom_name: str = None, unit_price: float = None) -> Dict:
        data = {"item_type": item_type, "qty": qty, "discount_amount": discount_amount}
        if ref_id is not None:
            data["ref_id"] = ref_id
        if custom_name is not None:
            data["custom_name"] = custom_name
        if unit_price is not None:
            data["unit_price"] = unit_price
        return self._request(
            "POST",
            f"/quotations/{quotation_id}/items",
            data=data,
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

    def update_quotation_promotion(self, quotation_id: int, promotion_id: int, discount_amount: float) -> Dict:
        """Apply a promotion discount to a quotation and persist promotion_id"""
        return self._request(
            "PUT",
            f"/quotations/{quotation_id}/promotion",
            data={"promotion_id": promotion_id, "discount_amount": discount_amount},
        )

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

    def get_repair_order_pdf(self, repair_id: int) -> bytes:
        """Get repair work order PDF as bytes"""
        return self._request("GET", f"/repair-orders/{repair_id}/pdf")

    def get_invoice_pdf(self, invoice_id: int) -> bytes:
        """Get invoice PDF as bytes"""
        return self._request("GET", f"/invoices/{invoice_id}/pdf")

    def get_delivery_note_pdf(self, invoice_id: int) -> bytes:
        """Get car delivery note PDF as bytes"""
        return self._request("GET", f"/invoices/{invoice_id}/delivery-note/pdf")

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

    def pull_quotation_parts(self, repair_id: int) -> Dict:
        return self._request("POST", f"/repair-orders/{repair_id}/pull-quotation-parts")

    def delete_repair_order(self, repair_id: int) -> Dict:
        return self._request("DELETE", f"/repair-orders/{repair_id}")

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

    def record_invoice_payment(self, invoice_id: int, payment_method: str, received_amount: float, change_amount: float) -> Dict:
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

    def get_purchase_order_pdf(self, po_id: int) -> bytes:
        """Get purchase order PDF as bytes"""
        return self._request("GET", f"/purchase-orders/{po_id}/pdf")

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
    
    # ========== Promotion Parts ==========
    def get_promotion_parts(self, promotion_id: int) -> List[Dict]:
        """Get parts in promotion"""
        return self._request("GET", f"/promotions/{promotion_id}/parts")

    def add_promotion_part(self, promotion_id: int, part_id: int, qty: int = 1) -> Dict:
        """Add part to promotion"""
        return self._request("POST", f"/promotions/{promotion_id}/parts", data={
            "part_id": part_id,
            "qty": qty
        })

    def delete_promotion_part(self, promotion_id: int, item_id: int) -> Dict:
        """Remove part from promotion"""
        return self._request("DELETE", f"/promotions/{promotion_id}/parts/{item_id}")

    def clear_promotion_parts(self, promotion_id: int) -> Dict:
        """Clear all parts from promotion"""
        return self._request("DELETE", f"/promotions/{promotion_id}/parts")

    # ========== Promotion Services ==========
    def get_promotion_services(self, promotion_id: int) -> List[Dict]:
        """Get services in promotion"""
        return self._request("GET", f"/promotions/{promotion_id}/services")

    def add_promotion_service(self, promotion_id: int, service_id: int, qty: int = 1) -> Dict:
        """Add service to promotion"""
        return self._request("POST", f"/promotions/{promotion_id}/services", data={
            "service_id": service_id,
            "qty": qty
        })

    def delete_promotion_service(self, promotion_id: int, item_id: int) -> Dict:
        """Remove service from promotion"""
        return self._request("DELETE", f"/promotions/{promotion_id}/services/{item_id}")

    def clear_promotion_services(self, promotion_id: int) -> Dict:
        """Clear all services from promotion"""
        return self._request("DELETE", f"/promotions/{promotion_id}/services")

    # ========== Job Order Parts & Services (Deprecated - for backward compatibility) ==========
    def add_job_order_part(self, job_order_id: int, part_id: int, quantity: int = 1, unit_price: float = 0) -> Dict:
        """Add part to job order (Deprecated - use quotation items instead)"""
        return self._request("POST", f"/job-orders/{job_order_id}/parts", data={
            "part_id": part_id,
            "quantity": quantity,
            "unit_price": unit_price
        })

    def add_job_order_service(self, job_order_id: int, service_id: int, quantity: int = 1, unit_price: float = 0) -> Dict:
        """Add service to job order (Deprecated - use quotation items instead)"""
        return self._request("POST", f"/job-orders/{job_order_id}/services", data={
            "service_id": service_id,
            "quantity": quantity,
            "unit_price": unit_price
        })

    def get_job_order_parts(self, job_order_id: int) -> List[Dict]:
        """Get all parts for a job order (Deprecated)"""
        return self._request("GET", f"/job-orders/{job_order_id}/parts")

    def get_job_order_services(self, job_order_id: int) -> List[Dict]:
        """Get all services for a job order (Deprecated)"""
        return self._request("GET", f"/job-orders/{job_order_id}/services")
    
    def delete_job_order_part(self, job_order_id: int, item_id: int) -> Dict:
        """Delete part from job order (Deprecated)"""
        return self._request("DELETE", f"/job-orders/{job_order_id}/parts/{item_id}")

    def delete_job_order_service(self, job_order_id: int, item_id: int) -> Dict:
        """Delete service from job order (Deprecated)"""
        return self._request("DELETE", f"/job-orders/{job_order_id}/services/{item_id}")

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

    def get_parts_service_sales_report(self, start_date: str = None, end_date: str = None) -> Dict:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/parts-service-sales", params=params)

    def get_mechanic_performance_report(self, start_date: str = None, end_date: str = None) -> Dict:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/mechanic-performance", params=params)

    def get_revenue_report_pdf(self, start_date: str = None, end_date: str = None) -> bytes:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/revenue/pdf", params=params)

    def get_repair_summary_report_pdf(self, start_date: str = None, end_date: str = None) -> bytes:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/repair-summary/pdf", params=params)

    def get_parts_service_sales_report_pdf(self, start_date: str = None, end_date: str = None) -> bytes:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/parts-service-sales/pdf", params=params)

    def get_mechanic_performance_report_pdf(self, start_date: str = None, end_date: str = None) -> bytes:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/mechanic-performance/pdf", params=params)

    def get_promotion_usage_report_pdf(self, start_date: str = None, end_date: str = None) -> bytes:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._request("GET", "/reports/promotion-usage/pdf", params=params)
    
    def get_job_orders_with_details(self, status: str = None) -> List[Dict]:
        """Get all job orders with customer and vehicle details in ONE query"""
        params = {"status": status} if status else None
        return self._request("GET", "/job-orders-with-details", params=params)

    def get_goods_receipts(self) -> List[Dict]:
        """Get all goods receipts"""
        return self._request("GET", "/goods-receipts")

    def get_goods_receipt(self, receipt_id: int) -> Dict:
        """Get a single goods receipt with details"""
        return self._request("GET", f"/goods-receipts/{receipt_id}")