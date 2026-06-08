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
                "services": [
                    {
                        "id": 1,
                        "name": "ຄ່າແຮງງານຊ່າງ",
                        "qty": 1,
                        "unit_price": 100000,
                        "total": 100000,
                        "discount_amount": 0
                    }
                ],
                "summary": {
                    "total_amount": 100000,
                    "total_discount": 0,
                    "final_total": 100000
                }
            }
        
        # Get parts usage from repair orders
        cursor.execute("""
            SELECT 
                pu.id, pu.part_id, pu.qty, pu.cost_price,
                p.name as part_name, p.sell_price
            FROM parts_usage pu
            LEFT JOIN parts p ON pu.part_id = p.id
            LEFT JOIN repair_orders ro ON pu.repair_id = ro.id
            WHERE ro.job_order_id = %s
        """, (job_order_id,))
        
        parts_usage = cursor.fetchall()
        
        # Format parts list
        parts_list = []
        for part in parts_usage:
            price = part.get('sell_price', part.get('cost_price', 0)) or 0
            parts_list.append({
                'id': part.get('id'),
                'name': part.get('part_name', '-'),
                'qty': part.get('qty', 0),
                'unit_price': price,
                'total': (part.get('qty', 0) * price),
                'discount_amount': 0
            })
        
        # Get services (simple default if no quotation)
        services_list = [
            {
                "id": 1,
                "name": "ຄ່າແຮງງານຊ່າງ",
                "qty": 1,
                "unit_price": 100000,
                "total": 100000,
                "discount_amount": 0
            }
        ]
        
        # Try to get services from quotation
        cursor.execute("""
            SELECT q.id as quotation_id
            FROM quotations q
            WHERE q.job_order_id = %s AND q.status = 'approved'
            ORDER BY q.id DESC LIMIT 1
        """, (job_order_id,))
        
        quotation = cursor.fetchone()
        
        if quotation:
            cursor.execute("""
                SELECT 
                    qi.id, qi.qty, qi.discount_amount,
                    s.id as service_id, s.name as service_name, s.price as service_price
                FROM quotation_items qi
                LEFT JOIN services s ON qi.ref_id = s.id
                WHERE qi.quotation_id = %s AND qi.item_type = 'service'
            """, (quotation['quotation_id'],))
            
            services = cursor.fetchall()
            if services:
                services_list = []
                for service in services:
                    price = service.get('service_price', 0) or 0
                    services_list.append({
                        'id': service['id'],
                        'name': service.get('service_name', '-'),
                        'qty': service['qty'],
                        'unit_price': price,
                        'total': service['qty'] * price,
                        'discount_amount': service.get('discount_amount', 0)
                    })
        
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
        # Return default data
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
            "services": [
                {
                    "id": 1,
                    "name": "ຄ່າແຮງງານຊ່າງ",
                    "qty": 1,
                    "unit_price": 100000,
                    "total": 100000,
                    "discount_amount": 0
                }
            ],
            "summary": {
                "total_amount": 100000,
                "total_discount": 0,
                "final_total": 100000
            }
        }
    finally:
        cursor.close()
        db.close()