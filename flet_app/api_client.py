# api_client.py
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

            if response.status_code == 200:
                return (
                    response.json()
                    if method != "GET" or response.content
                    else response.content
                )
            else:
                try:
                    error_msg = response.json().get(
                        "detail", f"HTTP {response.status_code}"
                    )
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            raise Exception("ไม่สามารถเชื่อมต่อกับ Server ได้ กรุณาเปิด Backend")

    # ========== Authentication ==========
    def login(self, username: str, password: str) -> Dict:
        self.username = username
        self.password = password
        return self._request("POST", "/login")

    # ========== Process 1.1: Employees ==========
    def get_employees(self) -> List[Dict]:
        return self._request("GET", "/employees")

    def add_employee(
        self, username: str, password: str, fullname: str, role: str, phone: str = ""
    ) -> Dict:
        return self._request(
            "POST",
            "/employees",
            data={
                "username": username,
                "password": password,
                "fullname": fullname,
                "role": role,
                "phone": phone,
            },
        )

    def update_employee(self, emp_id: int, data: Dict) -> Dict:
        """Update employee information"""
        return self._request("PUT", f"/employees/{emp_id}", data=data)

    def delete_employee(self, employee_id: int) -> Dict:
        return self._request("DELETE", f"/employees/{employee_id}")

    # ========== Process 1.2: Shop Info ==========
    def get_shop(self) -> Dict:
        return self._request("GET", "/shop")

    def update_shop(
        self,
        shop_name: str,
        address: str,
        phone: str,
        email: str = "",
        tax_id: str = "",
    ) -> Dict:
        return self._request(
            "PUT",
            "/shop",
            data={
                "shop_name": shop_name,
                "address": address,
                "phone": phone,
                "email": email,
                "tax_id": tax_id,
            },
        )

    def upload_shop_logo(self, logo_path: str) -> Dict:
        """Upload shop logo"""
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
        """Delete shop logo"""
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
        """Download shop logo"""
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
        service_name: str,
        description: str = "",
        price: float = 0,
        estimated_hours: int = 1,
    ) -> Dict:
        return self._request(
            "POST",
            "/services",
            data={
                "service_name": service_name,
                "description": description,
                "price": price,
                "estimated_hours": estimated_hours,
            },
        )

    def update_service(self, service_id: int, data: Dict) -> Dict:
        """Update service information"""
        return self._request("PUT", f"/services/{service_id}", data=data)

    def delete_service(self, service_id: int) -> Dict:
        return self._request("DELETE", f"/services/{service_id}")

    # ========== Process 1.5: Parts ==========
    def get_parts(self) -> List[Dict]:
        """Get all parts"""
        return self._request("GET", "/parts")

    def add_part(
        self,
        part_code: str,
        name: str,
        brand: str = "",
        cost_price: float = 0,
        sell_price: float = 0,
        stock_qty: int = 0,
        min_stock: int = 5,
        unit: str = "piece",
        supplier_id: int = None,
    ) -> Dict:
        """Add new part"""
        data = {
            "part_code": part_code,
            "name": name,
            "brand": brand,
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
        """Update part"""
        return self._request("PUT", f"/parts/{part_id}", data=data)

    def delete_part(self, part_id: int) -> Dict:
        """Delete part"""
        return self._request("DELETE", f"/parts/{part_id}")

    def search_parts(self, keyword: str = "") -> List[Dict]:
        """Search for parts"""
        params = {"keyword": keyword} if keyword else None
        return self._request("GET", "/search-parts", params=params)

    def search_services(self, keyword: str = "") -> List[Dict]:
        """Search for services"""
        params = {"keyword": keyword} if keyword else None
        return self._request("GET", "/search-services", params=params)

    # ========== Process 1.6: Promotions ==========
    def get_promotions(self) -> List[Dict]:
        """Get all promotions"""
        return self._request("GET", "/promotions")

    def add_promotion(
        self,
        promo_code: str,
        promo_name: str,
        discount_type: str,
        discount_value: float,
        start_date: str,
        end_date: str,
        is_active: bool = True,
    ) -> Dict:
        """Add new promotion"""
        return self._request(
            "POST",
            "/promotions",
            data={
                "promo_code": promo_code,
                "promo_name": promo_name,
                "discount_type": discount_type,
                "discount_value": discount_value,
                "start_date": start_date,
                "end_date": end_date,
                "is_active": is_active,
            },
        )

    def update_promotion(self, promo_id: int, data: Dict) -> Dict:
        """Update promotion"""
        return self._request("PUT", f"/promotions/{promo_id}", data=data)

    def delete_promotion(self, promo_id: int) -> Dict:
        """Delete promotion"""
        return self._request("DELETE", f"/promotions/{promo_id}")

    # ========== Process 2: Customers & Vehicles ==========

    def get_customers(self) -> List[Dict]:
        """Get all customers"""
        return self._request("GET", "/customers")

    def add_customer(self, name: str, phone: str = "", address: str = "") -> Dict:
        """Add new customer"""
        return self._request(
            "POST",
            "/customers",
            data={"name": name, "phone": phone, "address": address},
        )

    def update_customer(self, customer_id: int, customer_data: Dict) -> Dict:
        """Update customer information"""
        return self._request("PUT", f"/customers/{customer_id}", data=customer_data)

    def delete_customer(self, customer_id: int) -> Dict:
        """Delete customer"""
        return self._request("DELETE", f"/customers/{customer_id}")

    def get_vehicles(self, customer_id: int = None) -> List[Dict]:
        """Get vehicles by customer ID"""
        params = {"customer_id": customer_id} if customer_id else None
        return self._request("GET", "/vehicles", params=params)

    def add_vehicle(self, vehicle_data: Dict) -> Dict:
        """Add new vehicle"""
        return self._request("POST", "/vehicles", data=vehicle_data)

    def update_vehicle(self, vehicle_id: int, vehicle_data: Dict) -> Dict:
        """Update vehicle"""
        return self._request("PUT", f"/vehicles/{vehicle_id}", data=vehicle_data)

    def delete_vehicle(self, vehicle_id: int) -> Dict:
        """Delete vehicle"""
        return self._request("DELETE", f"/vehicles/{vehicle_id}")

    def register_customer_with_vehicle(
        self, customer_data: Dict, vehicle_data: Dict
    ) -> Dict:
        """Register customer with vehicle in one transaction"""
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
        """Create a new job order"""
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
        """Get all job orders, optionally filtered by status"""
        params = {"status": status} if status else None
        return self._request("GET", "/job-orders", params=params)

    def get_job_order(self, order_id: int) -> Dict:
        """Get a single job order by ID"""
        return self._request("GET", f"/job-orders/{order_id}")

    def update_job_order(self, order_id: int, **kwargs) -> Dict:
        """Update job order"""
        return self._request("PUT", f"/job-orders/{order_id}", data=kwargs)

    def delete_job_order(self, order_id: int) -> Dict:
        """Delete job order"""
        return self._request("DELETE", f"/job-orders/{order_id}")

    # ========== Process 4: Quotations ==========

    def get_quotations(self, job_order_id: int = None) -> List[Dict]:
        """Get all quotations, optionally filtered by job_order_id"""
        params = {"job_order_id": job_order_id} if job_order_id else None
        return self._request("GET", "/quotations", params=params)

    def get_quotation(self, quotation_id: int) -> Dict:
        """Get a single quotation with its items"""
        return self._request("GET", f"/quotations/{quotation_id}")

    def create_quotation(self, job_order_id: int, valid_until: str = None, notes: str = "") -> Dict:
        """Create a new quotation"""
        data = {"job_order_id": job_order_id, "notes": notes}
        if valid_until:
            data["valid_until"] = valid_until
        return self._request("POST", "/quotations", data=data)

    def add_quotation_item(self, quotation_id: int, item_type: str, ref_id: int, qty: int = 1) -> Dict:
        """Add item to quotation"""
        return self._request(
            "POST",
            f"/quotations/{quotation_id}/items",
            data={"item_type": item_type, "ref_id": ref_id, "qty": qty},
        )

    def update_quotation_item(self, quotation_id: int, item_id: int, qty: int, discount_amount: float = 0) -> Dict:
        """Update quotation item"""
        return self._request(
            "PUT",
            f"/quotations/{quotation_id}/items/{item_id}",
            data={"qty": qty, "discount_amount": discount_amount},
        )

    def delete_quotation_item(self, quotation_id: int, item_id: int) -> Dict:
        """Delete item from quotation"""
        return self._request("DELETE", f"/quotations/{quotation_id}/items/{item_id}")

    def calculate_quotation_total(self, quotation_id: int) -> Dict:
        """Calculate and update quotation total"""
        return self._request("PUT", f"/quotations/{quotation_id}/calculate")

    def update_quotation_status(self, quotation_id: int, status: str) -> Dict:
        """Update quotation status"""
        return self._request(
            "PUT", f"/quotations/{quotation_id}/status", data={"status": status}
        )

    def delete_quotation(self, quotation_id: int) -> Dict:
        """Delete quotation"""
        return self._request("DELETE", f"/quotations/{quotation_id}")

    # ========== Process 5: Repair Management ==========

    def get_repair_orders(self, job_order_id: int = None, status: str = None) -> List[Dict]:
        """Get repair orders, optionally filtered by job_order_id or status"""
        params = {}
        if job_order_id:
            params["job_order_id"] = job_order_id
        if status:
            params["status"] = status
        return self._request("GET", "/repair-orders", params=params)

    def get_repair_order(self, repair_id: int) -> Dict:
        """Get a single repair order with parts usage"""
        return self._request("GET", f"/repair-orders/{repair_id}")

    def create_repair_order(self, job_order_id: int, mechanic_id: int = None) -> Dict:
        """Create a new repair order"""
        data = {"job_order_id": job_order_id}
        if mechanic_id:
            data["mechanic_id"] = mechanic_id
        return self._request("POST", "/repair-orders", data=data)

    def assign_mechanic(self, repair_id: int, mechanic_id: int) -> Dict:
        """Assign mechanic to repair order"""
        return self._request(
            "PUT", f"/repair-orders/{repair_id}/mechanic", data={"mechanic_id": mechanic_id}
        )

    def update_repair_status(self, repair_id: int, status: str) -> Dict:
        """Update repair order status"""
        return self._request(
            "PUT", f"/repair-orders/{repair_id}/status", data={"status": status}
        )

    def add_part_usage(self, repair_id: int, part_id: int, qty: int) -> Dict:
        """Add part usage (withdraw from stock)"""
        return self._request(
            "POST",
            f"/repair-orders/{repair_id}/parts-usage",
            data={"part_id": part_id, "qty": qty},
        )

    def delete_part_usage(self, repair_id: int, usage_id: int) -> Dict:
        """Delete part usage and return to stock"""
        return self._request("DELETE", f"/repair-orders/{repair_id}/parts-usage/{usage_id}")

    def get_mechanics(self) -> List[Dict]:
        """Get all mechanics (employees with role = technician)"""
        return self._request("GET", "/employees/mechanics")

    # ========== Legacy/Backward Compatibility ==========
    def register_customer_with_car(self, customer_data: Dict, car_data: Dict) -> Dict:
        """Legacy method - use register_customer_with_vehicle instead"""
        return self.register_customer_with_vehicle(customer_data, car_data)

    def get_cars(self, customer_id: int = None) -> List[Dict]:
        """Legacy method - use get_vehicles instead"""
        return self.get_vehicles(customer_id)

    def add_car(self, car_data: Dict) -> Dict:
        """Legacy method - use add_vehicle instead"""
        return self.add_vehicle(car_data)

    def update_car(self, car_id: int, car_data: Dict) -> Dict:
        """Legacy method - use update_vehicle instead"""
        return self.update_vehicle(car_id, car_data)

    def delete_car(self, car_id: int) -> Dict:
        """Legacy method - use delete_vehicle instead"""
        return self.delete_vehicle(car_id)

    def update_car_info(self, car_id: int, car_data: Dict) -> Dict:
        """Legacy method - use update_vehicle instead"""
        return self.update_vehicle(car_id, car_data)