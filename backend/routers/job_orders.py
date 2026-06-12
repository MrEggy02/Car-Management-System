# backend/routers/job_orders.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.get("/job-orders")
def get_job_orders(
    status: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """Get all job orders, optionally filtered by status"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if status:
            cursor.execute("""
                SELECT 
                    jo.id,
                    jo.job_no,
                    jo.customer_id,
                    jo.vehicle_id,
                    jo.receive_date,
                    jo.problem_description,
                    jo.mileage,
                    jo.fuel_level,
                    jo.status,
                    jo.created_by,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    v.plate_number,
                    b.name as brand,
                    v.model,
                    v.year,
                    v.color,
                    e.name as created_by_name
                FROM job_orders jo
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN brands b ON v.brand_id = b.id
                LEFT JOIN Employees e ON jo.created_by = e.id
                WHERE jo.status = %s
                ORDER BY jo.id DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT 
                    jo.id,
                    jo.job_no,
                    jo.customer_id,
                    jo.vehicle_id,
                    jo.receive_date,
                    jo.problem_description,
                    jo.mileage,
                    jo.fuel_level,
                    jo.status,
                    jo.created_by,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    v.plate_number,
                    b.name as brand,
                    v.model,
                    v.year,
                    v.color,
                    e.name as created_by_name
                FROM job_orders jo
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN brands b ON v.brand_id = b.id
                LEFT JOIN Employees e ON jo.created_by = e.id
                ORDER BY jo.id DESC
            """)
        
        job_orders = cursor.fetchall()
        
        # Convert datetime to string for JSON serialization
        for order in job_orders:
            if order.get('receive_date'):
                order['receive_date'] = str(order['receive_date'])
            
            # Handle None values
            if not order.get('customer_name'):
                order['customer_name'] = "-"
            if not order.get('customer_phone'):
                order['customer_phone'] = "-"
            if not order.get('plate_number'):
                order['plate_number'] = "-"
            if not order.get('brand'):
                order['brand'] = "-"
            if not order.get('model'):
                order['model'] = "-"
            if not order.get('created_by_name'):
                order['created_by_name'] = "-"
        
        return job_orders
    except Exception as e:
        print(f"Error in get_job_orders: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/job-orders/{order_id}")
def get_job_order(order_id: int, user: dict = Depends(authenticate_user)):
    """Get a single job order by ID"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                jo.id,
                jo.job_no,
                jo.customer_id,
                jo.vehicle_id,
                jo.receive_date,
                jo.problem_description,
                jo.mileage,
                jo.fuel_level,
                jo.status,
                jo.created_by,
                c.name as customer_name,
                c.phone as customer_phone,
                c.address,
                v.plate_number,
                b.name as brand,
                v.model,
                v.year,
                v.color,
                e.name as created_by_name
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN Employees e ON jo.created_by = e.id
            WHERE jo.id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        if order:
            if order.get('receive_date'):
                order['receive_date'] = str(order['receive_date'])
            if not order.get('customer_name'):
                order['customer_name'] = "-"
            if not order.get('plate_number'):
                order['plate_number'] = "-"
            if not order.get('brand'):
                order['brand'] = "-"
            if not order.get('model'):
                order['model'] = "-"
            if not order.get('created_by_name'):
                order['created_by_name'] = "-"
        return order
    except Exception as e:
        print(f"Error in get_job_order: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        cursor.close()
        db.close()


@router.post("/job-orders")
def create_job_order(
    customer_id: int = Form(...),
    vehicle_id: int = Form(...),
    problem_description: str = Form(...),
    mileage: int = Form(0),
    fuel_level: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """Create a new job order"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Generate job number
        year = datetime.now().year
        cursor.execute("SELECT COUNT(*) as count FROM job_orders WHERE YEAR(receive_date) = %s", (year,))
        count = cursor.fetchone()
        count_num = count[0] + 1 if count else 1
        job_no = f"JOB-{year}-{count_num:04d}"
        
        # Insert job order
        cursor.execute("""
            INSERT INTO job_orders 
            (job_no, customer_id, vehicle_id, problem_description, mileage, fuel_level, status, created_by, receive_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (job_no, customer_id, vehicle_id, problem_description, mileage, fuel_level, 'pending', user.get('id'), datetime.now()))
        
        db.commit()
        order_id = cursor.lastrowid
        
        return {
            "id": order_id,
            "job_no": job_no,
            "message": "Job order created successfully"
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating job order: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/job-orders/{order_id}")
def update_job_order(
    order_id: int,
    status: Optional[str] = Form(None),
    problem_description: Optional[str] = Form(None),
    mileage: Optional[int] = Form(None),
    fuel_level: Optional[str] = Form(None),
    user: dict = Depends(authenticate_user)
):
    """Update job order status or details"""
    db = get_db()
    cursor = db.cursor()
    try:
        update_fields = []
        values = []
        
        if status:
            update_fields.append("status = %s")
            values.append(status)
        if problem_description:
            update_fields.append("problem_description = %s")
            values.append(problem_description)
        if mileage is not None:
            update_fields.append("mileage = %s")
            values.append(mileage)
        if fuel_level:
            update_fields.append("fuel_level = %s")
            values.append(fuel_level)
        
        if update_fields:
            values.append(order_id)
            query = f"UPDATE job_orders SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, values)
            db.commit()
        
        return {"message": "Job order updated successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error updating job order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/job-orders/{order_id}")
def delete_job_order(order_id: int, user: dict = Depends(authenticate_user)):
    """Delete a job order"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if job order exists
        cursor.execute("SELECT id FROM job_orders WHERE id = %s", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job order not found")
        
        cursor.execute("DELETE FROM job_orders WHERE id = %s", (order_id,))
        db.commit()
        return {"message": "Job order deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting job order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


# ========== NEW ENDPOINTS FOR JOB ORDER PARTS AND SERVICES ==========

@router.post("/job-orders/{job_order_id}/parts")
def add_job_order_part(
    job_order_id: int,
    part_id: int = Form(...),
    quantity: int = Form(1),
    unit_price: float = Form(0),
    user: dict = Depends(authenticate_user)
):
    """Add a part to job order"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if job order exists
        cursor.execute("SELECT id FROM job_orders WHERE id = %s", (job_order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job order not found")
        
        # Check if job_order_parts table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_order_parts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_order_id INT NOT NULL,
                part_id INT NOT NULL,
                quantity INT NOT NULL DEFAULT 1,
                unit_price DECIMAL(12,2) NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_order_id) REFERENCES job_orders(id) ON DELETE CASCADE,
                FOREIGN KEY (part_id) REFERENCES parts(id)
            )
        """)
        db.commit()
        
        # Insert into job_order_parts
        cursor.execute("""
            INSERT INTO job_order_parts (job_order_id, part_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """, (job_order_id, part_id, quantity, unit_price))
        
        db.commit()
        return {"message": "Part added successfully", "id": cursor.lastrowid}
    except Exception as e:
        db.rollback()
        print(f"Error adding job order part: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.post("/job-orders/{job_order_id}/services")
def add_job_order_service(
    job_order_id: int,
    service_id: int = Form(...),
    quantity: int = Form(1),
    unit_price: float = Form(0),
    user: dict = Depends(authenticate_user)
):
    """Add a service to job order"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if job order exists
        cursor.execute("SELECT id FROM job_orders WHERE id = %s", (job_order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job order not found")
        
        # Check if job_order_services table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_order_services (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_order_id INT NOT NULL,
                service_id INT NOT NULL,
                quantity INT NOT NULL DEFAULT 1,
                unit_price DECIMAL(12,2) NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_order_id) REFERENCES job_orders(id) ON DELETE CASCADE,
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
        """)
        db.commit()
        
        # Insert into job_order_services
        cursor.execute("""
            INSERT INTO job_order_services (job_order_id, service_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """, (job_order_id, service_id, quantity, unit_price))
        
        db.commit()
        return {"message": "Service added successfully", "id": cursor.lastrowid}
    except Exception as e:
        db.rollback()
        print(f"Error adding job order service: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/job-orders/{job_order_id}/parts")
def get_job_order_parts(
    job_order_id: int,
    user: dict = Depends(authenticate_user)
):
    """Get all parts for a job order"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) as cnt FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = 'job_order_parts'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists or table_exists['cnt'] == 0:
            return []
        
        cursor.execute("""
            SELECT jop.*, p.name as part_name, p.sell_price
            FROM job_order_parts jop
            LEFT JOIN parts p ON jop.part_id = p.id
            WHERE jop.job_order_id = %s
        """, (job_order_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting job order parts: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/job-orders/{job_order_id}/services")
def get_job_order_services(
    job_order_id: int,
    user: dict = Depends(authenticate_user)
):
    """Get all services for a job order"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) as cnt FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name = 'job_order_services'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists or table_exists['cnt'] == 0:
            return []
        
        cursor.execute("""
            SELECT jos.*, s.name as service_name, s.price
            FROM job_order_services jos
            LEFT JOIN services s ON jos.service_id = s.id
            WHERE jos.job_order_id = %s
        """, (job_order_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting job order services: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.delete("/job-orders/{job_order_id}/parts/{item_id}")
def delete_job_order_part(
    job_order_id: int,
    item_id: int,
    user: dict = Depends(authenticate_user)
):
    """Delete a part from job order"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM job_order_parts WHERE id = %s AND job_order_id = %s", 
                      (item_id, job_order_id))
        db.commit()
        return {"message": "Part removed successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting job order part: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/job-orders/{job_order_id}/services/{item_id}")
def delete_job_order_service(
    job_order_id: int,
    item_id: int,
    user: dict = Depends(authenticate_user)
):
    """Delete a service from job order"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM job_order_services WHERE id = %s AND job_order_id = %s", 
                      (item_id, job_order_id))
        db.commit()
        return {"message": "Service removed successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting job order service: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/job-orders/{job_order_id}/invoice-info")
def get_invoice_info_by_job_order(
    job_order_id: int, 
    user: dict = Depends(authenticate_user)
):
    """Get invoice information for a job order"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Get job order info with brand from brands table
        cursor.execute("""
            SELECT 
                jo.id, jo.job_no, jo.problem_description, jo.mileage, jo.fuel_level,
                c.id as customer_id, c.name as customer_name, c.phone as customer_phone,
                v.id as vehicle_id, v.plate_number, b.name as brand, v.model, v.year
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            WHERE jo.id = %s
        """, (job_order_id,))
        
        job_info = cursor.fetchone()
        if not job_info:
            return {
                "job_order": {
                    "id": job_order_id,
                    "job_no": f"JO-{job_order_id:04d}",
                    "customer_name": "",
                    "customer_phone": "",
                    "plate_number": "",
                    "brand": "",
                    "model": "",
                    "year": "",
                    "mileage": 0,
                    "fuel_level": "",
                    "problem_description": ""
                },
                "parts": [],
                "services": [],
                "summary": {
                    "total_amount": 0,
                    "total_discount": 0,
                    "final_total": 0
                }
            }
        
        # Get parts from job_order_parts
        parts_list = []
        try:
            cursor.execute("""
                SELECT jop.*, p.name as part_name, p.sell_price
                FROM job_order_parts jop
                LEFT JOIN parts p ON jop.part_id = p.id
                WHERE jop.job_order_id = %s
            """, (job_order_id,))
            parts = cursor.fetchall()
            
            for part in parts:
                price = part.get('unit_price', part.get('sell_price', 0)) or 0
                parts_list.append({
                    'id': part.get('id'),
                    'name': part.get('part_name', '-'),
                    'qty': part.get('quantity', 0),
                    'unit_price': price,
                    'total': (part.get('quantity', 0) * price),
                    'discount_amount': 0
                })
        except Exception as e:
            print(f"Error getting parts: {e}")
        
        # Get services from job_order_services
        services_list = []
        try:
            cursor.execute("""
                SELECT jos.*, s.name as service_name, s.price
                FROM job_order_services jos
                LEFT JOIN services s ON jos.service_id = s.id
                WHERE jos.job_order_id = %s
            """, (job_order_id,))
            services = cursor.fetchall()
            
            for service in services:
                price = service.get('unit_price', service.get('price', 0)) or 0
                services_list.append({
                    'id': service.get('id'),
                    'name': service.get('service_name', '-'),
                    'qty': service.get('quantity', 1),
                    'unit_price': price,
                    'total': (service.get('quantity', 1) * price),
                    'discount_amount': 0
                })
        except Exception as e:
            print(f"Error getting services: {e}")
        
        # Calculate totals
        total_amount = sum(p['total'] for p in parts_list) + sum(s['total'] for s in services_list)
        total_discount = sum(p.get('discount_amount', 0) for p in parts_list) + sum(s.get('discount_amount', 0) for s in services_list)
        final_total = total_amount - total_discount
        
        return {
            "job_order": {
                "id": job_info['id'],
                "job_no": job_info.get('job_no', ''),
                "customer_name": job_info.get('customer_name', ''),
                "customer_phone": job_info.get('customer_phone', ''),
                "plate_number": job_info.get('plate_number', ''),
                "brand": job_info.get('brand', ''),
                "model": job_info.get('model', ''),
                "year": job_info.get('year', ''),
                "mileage": job_info.get('mileage', 0),
                "fuel_level": job_info.get('fuel_level', ''),
                "problem_description": job_info.get('problem_description', '')
            },
            "parts": parts_list,
            "services": services_list,
            "summary": {
                "total_amount": total_amount,
                "total_discount": total_discount,
                "final_total": final_total
            }
        }
        
    except Exception as e:
        print(f"Error getting invoice info: {e}")
        import traceback
        traceback.print_exc()
        return {
            "job_order": {
                "id": job_order_id,
                "job_no": f"JO-{job_order_id:04d}",
                "customer_name": "",
                "customer_phone": "",
                "plate_number": "",
                "brand": "",
                "model": "",
                "year": "",
                "mileage": 0,
                "fuel_level": "",
                "problem_description": ""
            },
            "parts": [],
            "services": [],
            "summary": {
                "total_amount": 0,
                "total_discount": 0,
                "final_total": 0
            }
        }
    finally:
        cursor.close()
        db.close()