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
                    v.brand,
                    v.model,
                    v.year,
                    v.color,
                    u.fullname as created_by_name
                FROM job_orders jo
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN users u ON jo.created_by = u.id
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
                    v.brand,
                    v.model,
                    v.year,
                    v.color,
                    u.fullname as created_by_name
                FROM job_orders jo
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN users u ON jo.created_by = u.id
                ORDER BY jo.id DESC
            """)
        
        job_orders = cursor.fetchall()
        print(f"DEBUG: Found {len(job_orders)} job orders")
        
        # Convert datetime to string for JSON serialization
        for order in job_orders:
            if order.get('receive_date'):
                order['receive_date'] = str(order['receive_date'])
            
            # Handle None values
            if not order.get('customer_name'):
                order['customer_name'] = f"Customer #{order.get('customer_id')}" if order.get('customer_id') else "-"
            if not order.get('customer_phone'):
                order['customer_phone'] = "-"
            if not order.get('plate_number'):
                order['plate_number'] = f"Vehicle #{order.get('vehicle_id')}" if order.get('vehicle_id') else "-"
            if not order.get('brand'):
                order['brand'] = "-"
            if not order.get('model'):
                order['model'] = "-"
            if not order.get('year'):
                order['year'] = ""
            if not order.get('color'):
                order['color'] = "-"
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
                v.brand,
                v.model,
                v.year,
                v.color,
                u.fullname as created_by_name
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN users u ON jo.created_by = u.id
            WHERE jo.id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        if order:
            if order.get('receive_date'):
                order['receive_date'] = str(order['receive_date'])
            if not order.get('customer_name'):
                order['customer_name'] = f"Customer #{order.get('customer_id')}" if order.get('customer_id') else "-"
            if not order.get('plate_number'):
                order['plate_number'] = f"Vehicle #{order.get('vehicle_id')}" if order.get('vehicle_id') else "-"
            if not order.get('created_by_name'):
                order['created_by_name'] = "-"
        return order
    except Exception as e:
        print(f"Error in get_job_order: {e}")
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
            (job_no, customer_id, vehicle_id, problem_description, mileage, fuel_level, status, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (job_no, customer_id, vehicle_id, problem_description, mileage, fuel_level, 'pending', user.get('id')))
        
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
        cursor.execute("DELETE FROM job_orders WHERE id = %s", (order_id,))
        db.commit()
        return {"message": "Job order deleted successfully"}
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
    """Get invoice information for a job order (parts used + services)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Get job order info with quotation total
        cursor.execute("""
            SELECT 
                jo.id, jo.job_no, jo.problem_description,
                c.name as customer_name, c.phone as customer_phone,
                v.plate_number, v.brand, v.model, v.year, v.color,
                q.id as quotation_id, q.total_price as quotation_total
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN quotations q ON jo.id = q.job_order_id AND q.status = 'approved'
            WHERE jo.id = %s
        """, (job_order_id,))
        
        job_info = cursor.fetchone()
        if not job_info:
            raise HTTPException(status_code=404, detail="Job order not found")
        
        # Get parts used from repair
        cursor.execute("""
            SELECT 
                pu.*, p.name as part_name, p.part_code, p.sell_price
            FROM parts_usage pu
            LEFT JOIN parts p ON pu.part_id = p.id
            LEFT JOIN repair_orders ro ON pu.repair_id = ro.id
            WHERE ro.job_order_id = %s
        """, (job_order_id,))
        
        parts_usage = cursor.fetchall()
        
        # Get services from quotation items (if any)
        if job_info.get('quotation_id'):
            cursor.execute("""
                SELECT 
                    qi.*, s.service_name as name, s.price as unit_price
                FROM quotation_items qi
                LEFT JOIN services s ON qi.ref_id = s.id
                WHERE qi.quotation_id = %s AND qi.item_type = 'service'
            """, (job_info.get('quotation_id'),))
            services = cursor.fetchall()
        else:
            services = []
        
        return {
            "job_info": job_info,
            "parts_usage": parts_usage,
            "services": services
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting invoice info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()