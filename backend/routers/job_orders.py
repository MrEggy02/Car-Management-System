# backend/routers/job_orders.py
from fastapi import APIRouter, HTTPException, Depends, Form, Response, UploadFile, File
from fastapi.responses import FileResponse
from database import get_db
from auth import authenticate_user
import os
import uuid
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
                    jo.car_defects,
                    jo.signed_receipt_image,
                    jo.mileage,
                    jo.fuel_level,
                    jo.status,
                    jo.created_by,
                    jo.closed_by,
                    jo.closed_at,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    c.address,
                    v.plate_number,
                    b.name as brand,
                    v.model,
                    v.year,
                    v.color,
                    e.name as created_by_name,
                    ce.name as closed_by_name
                FROM job_orders jo
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN brands b ON v.brand_id = b.id
                LEFT JOIN employees e ON jo.created_by = e.id
                LEFT JOIN employees ce ON jo.closed_by = ce.id
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
                    jo.car_defects,
                    jo.signed_receipt_image,
                    jo.mileage,
                    jo.fuel_level,
                    jo.status,
                    jo.created_by,
                    jo.closed_by,
                    jo.closed_at,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    c.address,
                    v.plate_number,
                    b.name as brand,
                    v.model,
                    v.year,
                    v.color,
                    e.name as created_by_name,
                    ce.name as closed_by_name
                FROM job_orders jo
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN brands b ON v.brand_id = b.id
                LEFT JOIN employees e ON jo.created_by = e.id
                LEFT JOIN employees ce ON jo.closed_by = ce.id
                ORDER BY jo.id DESC
            """)
        
        job_orders = cursor.fetchall()
        
        for order in job_orders:
            if order.get('receive_date'):
                order['receive_date'] = str(order['receive_date'])
            if order.get('closed_at'):
                order['closed_at'] = str(order['closed_at'])
            
            # Set default values for null fields
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
            if not order.get('closed_by_name'):
                order['closed_by_name'] = "-"
            if not order.get('address'):
                order['address'] = "-"
        
        return job_orders
    except Exception as e:
        print(f"Error in get_job_orders: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()


# ========== NEW FAST API: Get job orders with all details in ONE query ==========
@router.get("/job-orders-with-details")
def get_job_orders_with_details(
    status: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """
    Get all job orders with customer and vehicle details in ONE query (FASTER)
    ດຶງຂໍ້ມູນ Job Orders ພ້ອມລາຍລະອຽດລູກຄ້າ ແລະ ລົດ ໃນຄຳສັ່ງດຽວ (ໄວຂຶ້ນ)
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                jo.id,
                jo.job_no,
                jo.customer_id,
                jo.vehicle_id,
                jo.receive_date,
                jo.problem_description,
                jo.car_defects,
                jo.signed_receipt_image,
                jo.mileage,
                jo.fuel_level,
                jo.status,
                jo.created_by,
                jo.closed_by,
                jo.closed_at,
                c.name as customer_name,
                c.phone as customer_phone,
                c.address,
                v.plate_number,
                b.name as brand,
                v.model,
                v.year,
                v.color,
                e.name as created_by_name,
                ce.name as closed_by_name
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN employees e ON jo.created_by = e.id
            LEFT JOIN employees ce ON jo.closed_by = ce.id
        """
        params = []
        
        if status:
            query += " WHERE jo.status = %s"
            params.append(status)
        
        query += " ORDER BY jo.id DESC"
        
        cursor.execute(query, params)
        job_orders = cursor.fetchall()
        
        for order in job_orders:
            if order.get('receive_date'):
                order['receive_date'] = str(order['receive_date'])
            if order.get('closed_at'):
                order['closed_at'] = str(order['closed_at'])
            
            # Set default values for null fields
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
            if not order.get('closed_by_name'):
                order['closed_by_name'] = "-"
            if not order.get('address'):
                order['address'] = "-"
        
        return job_orders
    except Exception as e:
        print(f"Error in get_job_orders_with_details: {e}")
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
                jo.car_defects,
                jo.signed_receipt_image,
                jo.mileage,
                jo.fuel_level,
                jo.status,
                jo.created_by,
                jo.closed_by,
                jo.closed_at,
                c.name as customer_name,
                c.phone as customer_phone,
                c.address,
                v.plate_number,
                b.name as brand,
                v.model,
                v.year,
                v.color,
                e.name as created_by_name,
                ce.name as closed_by_name
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN employees e ON jo.created_by = e.id
            LEFT JOIN employees ce ON jo.closed_by = ce.id
            WHERE jo.id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        if order:
            if order.get('receive_date'):
                order['receive_date'] = str(order['receive_date'])
            if order.get('closed_at'):
                order['closed_at'] = str(order['closed_at'])
            
            # Set default values for null fields
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
            if not order.get('closed_by_name'):
                order['closed_by_name'] = "-"
        
        return order
    except Exception as e:
        print(f"Error in get_job_order: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        cursor.close()
        db.close()


# ==================== NEW: GET JOB ORDER WITH ALL DETAILS (Multiple Quotations, Repairs, Invoices) ====================
@router.get("/job-orders/{order_id}/all-details")
def get_job_order_all_details(order_id: int, user: dict = Depends(authenticate_user)):
    """
    Get job order with all related quotations, repair orders, and invoices
    ດຶງ Job Order ພ້ອມຂໍ້ມູນທີ່ກ່ຽວຂ້ອງທັງໝົດ:
    - Quotations ທັງໝົດ
    - Repair Orders ທັງໝົດ
    - Invoices ທັງໝົດ
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # 1. Get main job order info
        cursor.execute("""
            SELECT 
                jo.id,
                jo.job_no,
                jo.customer_id,
                jo.vehicle_id,
                jo.receive_date,
                jo.problem_description,
                jo.car_defects,
                jo.signed_receipt_image,
                jo.mileage,
                jo.fuel_level,
                jo.status,
                jo.created_by,
                jo.closed_by,
                jo.closed_at,
                c.name as customer_name,
                c.phone as customer_phone,
                c.address,
                v.plate_number,
                b.name as brand,
                v.model,
                v.year,
                v.color,
                e.name as created_by_name,
                ce.name as closed_by_name
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN employees e ON jo.created_by = e.id
            LEFT JOIN employees ce ON jo.closed_by = ce.id
            WHERE jo.id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Job order not found")
        
        if order.get('receive_date'):
            order['receive_date'] = str(order['receive_date'])
        if order.get('closed_at'):
            order['closed_at'] = str(order['closed_at'])
        
        # 2. Get all quotations for this job order
        cursor.execute("""
            SELECT 
                id, 
                status, 
                sub_total, 
                discount_amount, 
                net_total,
                created_at,
                created_by,
                approved_by
            FROM quotations 
            WHERE job_order_id = %s 
            ORDER BY id DESC
        """, (order_id,))
        quotations = cursor.fetchall()
        for q in quotations:
            if q.get('created_at'):
                q['created_at'] = str(q['created_at'])
            if q.get('sub_total'):
                q['sub_total'] = float(q['sub_total'])
            if q.get('discount_amount'):
                q['discount_amount'] = float(q['discount_amount'])
            if q.get('net_total'):
                q['net_total'] = float(q['net_total'])
        
        # 3. Get all repair orders for this job order
        # FIXED: Removed ro.quotation_id because column does not exist
        cursor.execute("""
            SELECT 
                ro.id,
                ro.job_order_id,
                ro.mechanic_id,
                ro.status,
                ro.start_date,
                ro.end_date,
                e.name as mechanic_name
            FROM repair_orders ro
            LEFT JOIN employees e ON ro.mechanic_id = e.id
            WHERE ro.job_order_id = %s 
            ORDER BY ro.id DESC
        """, (order_id,))
        repair_orders = cursor.fetchall()
        for ro in repair_orders:
            if ro.get('start_date'):
                ro['start_date'] = str(ro['start_date'])
            if ro.get('end_date'):
                ro['end_date'] = str(ro['end_date'])
        
        # 4. Get all invoices for this job order
        # FIXED: Removed quotation_id because column does not exist
        cursor.execute("""
            SELECT 
                id,
                job_order_id,
                total_amount,
                total_discount,
                final_total,
                payment_method,
                payment_status,
                received_amount,
                change_amount,
                paid_date,
                created_by
            FROM invoices 
            WHERE job_order_id = %s 
            ORDER BY id DESC
        """, (order_id,))
        invoices = cursor.fetchall()
        for inv in invoices:
            if inv.get('paid_date'):
                inv['paid_date'] = str(inv['paid_date'])
            if inv.get('total_amount'):
                inv['total_amount'] = float(inv['total_amount'])
            if inv.get('total_discount'):
                inv['total_discount'] = float(inv['total_discount'])
            if inv.get('final_total'):
                inv['final_total'] = float(inv['final_total'])
            if inv.get('received_amount'):
                inv['received_amount'] = float(inv['received_amount'])
            if inv.get('change_amount'):
                inv['change_amount'] = float(inv['change_amount'])
        
        # Return combined data
        return {
            "job_order": order,
            "quotations": quotations,
            "repair_orders": repair_orders,
            "invoices": invoices
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_job_order_all_details: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


# ==================== END NEW ====================


@router.post("/job-orders")
def create_job_order(
    customer_id: int = Form(...),
    vehicle_id: int = Form(...),
    problem_description: str = Form(...),
    car_defects: str = Form(""),
    mileage: int = Form(0),
    fuel_level: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """Create a new job order"""
    db = get_db()
    cursor = db.cursor()
    try:
        year = datetime.now().year
        cursor.execute("SELECT COUNT(*) as count FROM job_orders WHERE YEAR(receive_date) = %s", (year,))
        count = cursor.fetchone()
        count_num = count[0] + 1 if count else 1
        job_no = f"JOB-{year}-{count_num:04d}"
        
        cursor.execute("""
            INSERT INTO job_orders 
            (job_no, customer_id, vehicle_id, problem_description, car_defects, mileage, fuel_level, status, created_by, receive_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (job_no, customer_id, vehicle_id, problem_description, car_defects, mileage, fuel_level, 'pending', user.get('id'), datetime.now()))
        
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
    car_defects: Optional[str] = Form(None),
    mileage: Optional[int] = Form(None),
    fuel_level: Optional[str] = Form(None),
    user: dict = Depends(authenticate_user)
):
    """Update job order status or details"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if job order exists
        cursor.execute("SELECT id FROM job_orders WHERE id = %s", (order_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job order not found")
        
        update_fields = []
        values = []
        
        if status:
            update_fields.append("status = %s")
            values.append(status)
            
            # If status is 'closed', set closed_by and closed_at
            if status == 'closed':
                update_fields.append("closed_by = %s")
                values.append(user.get('id'))
                update_fields.append("closed_at = %s")
                values.append(datetime.now())
        
        if problem_description:
            update_fields.append("problem_description = %s")
            values.append(problem_description)
        if car_defects is not None:
            update_fields.append("car_defects = %s")
            values.append(car_defects)
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating job order: {e}")
        import traceback
        traceback.print_exc()
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


# Directory for saving uploads
UPLOAD_DIR = "uploads/receipts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/job-orders/{order_id}/upload-receipt")
def upload_receipt(
    order_id: int,
    receipt: UploadFile = File(...),
    user: dict = Depends(authenticate_user)
):
    """Upload signed receipt image for a job order"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if job order exists
        cursor.execute("SELECT id, signed_receipt_image FROM job_orders WHERE id = %s", (order_id,))
        job_order = cursor.fetchone()
        if not job_order:
            raise HTTPException(status_code=404, detail="Job order not found")
        
        # Generate unique filename
        ext = receipt.filename.split('.')[-1] if '.' in receipt.filename else 'png'
        filename = f"signed_{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(receipt.file.read())
            
        # Delete old image if it exists
        old_image = job_order[1]
        if old_image:
            old_filepath = os.path.join(UPLOAD_DIR, old_image)
            if os.path.exists(old_filepath):
                try:
                    os.remove(old_filepath)
                except:
                    pass
        
        # Update database
        cursor.execute("UPDATE job_orders SET signed_receipt_image = %s WHERE id = %s", (filename, order_id))
        db.commit()
        
        return {"message": "Receipt image uploaded successfully", "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error uploading receipt: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/job-orders/{order_id}/receipt")
def get_receipt_image(order_id: int):
    """Get the signed receipt image for a job order"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT signed_receipt_image FROM job_orders WHERE id = %s", (order_id,))
        job_order = cursor.fetchone()
        if not job_order or not job_order[0]:
            raise HTTPException(status_code=404, detail="Receipt image not found")
            
        image_path = os.path.join(UPLOAD_DIR, job_order[0])
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Receipt image file not found")
            
        return FileResponse(image_path)
    finally:
        cursor.close()
        db.close()


# ========== JOB ORDERS READY FOR INVOICE ==========

@router.get("/job-orders/ready-for-invoice")
def get_job_orders_ready_for_invoice(user: dict = Depends(authenticate_user)):
    """
    Get job orders that are ready to be invoiced
    ດຶງ Job Orders ທີ່ສາມາດສ້າງໃບເກັບເງິນໄດ້
    (status = 'finished' OR 'repairing') AND no invoice yet
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                jo.id,
                jo.job_no,
                jo.status,
                jo.receive_date,
                COALESCE(c.name, '') as customer_name,
                COALESCE(c.phone, '') as customer_phone,
                COALESCE(v.plate_number, '') as plate_number,
                COALESCE(b.name, '') as brand,
                COALESCE(v.model, '') as model,
                q.id as quotation_id
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN quotations q ON jo.id = q.job_order_id AND q.status = 'approved'
            WHERE jo.status IN ('finished', 'repairing')
              AND jo.id NOT IN (SELECT COALESCE(job_order_id, 0) FROM invoices)
            ORDER BY jo.id DESC
        """)
        
        job_orders = cursor.fetchall()
        
        for order in job_orders:
            if order.get('receive_date'):
                order['receive_date'] = str(order['receive_date'])
        
        return job_orders
    except Exception as e:
        print(f"Error getting ready invoices: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()


# ========== INVOICE INFO - Get data from Quotation (D11, D12) ==========

@router.get("/job-orders/{job_order_id}/invoice-info")
def get_invoice_info_by_job_order(
    job_order_id: int, 
    quotation_id: Optional[int] = None,
    user: dict = Depends(authenticate_user)
):
    """
    Get invoice information for a job order
    ດຶງຂໍ້ມູນຈາກ:
    - Parts_Usage (ອາໄຫຼ່ທີ່ເບີກໃຊ້ຈິງ)
    - Quotation_Items (ບໍລິການ ແລະ ອາໄຫຼ່ທີ່ຕົກລົງໃນໃບສະເໜີ)
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Get job order basic info with COALESCE
        cursor.execute("""
            SELECT 
                jo.id, 
                COALESCE(jo.job_no, '') as job_no, 
                COALESCE(jo.problem_description, '') as problem_description, 
                COALESCE(jo.mileage, 0) as mileage, 
                COALESCE(jo.fuel_level, '') as fuel_level,
                COALESCE(c.id, 0) as customer_id, 
                COALESCE(c.name, '') as customer_name, 
                COALESCE(c.phone, '') as customer_phone,
                COALESCE(v.id, 0) as vehicle_id, 
                COALESCE(v.plate_number, '') as plate_number, 
                COALESCE(v.model, '') as model, 
                COALESCE(v.year, 0) as year,
                COALESCE(b.name, '') as brand
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
                    "job_no": f"JOB-{job_order_id:04d}",
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
        
        parts_list = []
        services_list = []
        total_amount = 0
        total_discount = 0
        
        # ========== GET PARTS AND SERVICES FROM APPROVED QUOTATION ==========
        if quotation_id:
            cursor.execute("""
                SELECT id, discount_amount, sub_total, net_total
                FROM quotations
                WHERE id = %s AND job_order_id = %s AND status = 'approved'
            """, (quotation_id, job_order_id))
            quotation = cursor.fetchone()
        else:
            cursor.execute("""
                SELECT id, discount_amount, sub_total, net_total
                FROM quotations
                WHERE job_order_id = %s AND status = 'approved'
                ORDER BY id DESC LIMIT 1
            """, (job_order_id,))
            quotation = cursor.fetchone()
        
        if quotation:
            total_discount = float(quotation.get('discount_amount', 0) or 0)
            
            # 1. Get parts from quotation_items
            cursor.execute("""
                SELECT 
                    qi.id,
                    qi.qty,
                    qi.unit_price,
                    qi.total,
                    qi.part_id,
                    COALESCE(p.name, qi.custom_name, 'ອາໄຫຼ່ທີ່ບໍ່ຮູ້ຈັກ') as item_name
                FROM quotation_items qi
                LEFT JOIN parts p ON qi.part_id = p.id
                WHERE qi.quotation_id = %s AND qi.part_id IS NOT NULL
                ORDER BY qi.id
            """, (quotation['id'],))
            quotation_parts = cursor.fetchall()
            
            for part in quotation_parts:
                qty = part.get('qty', 0)
                unit_price = float(part.get('unit_price', 0) or 0)
                total = float(part.get('total', qty * unit_price) or 0)
                
                parts_list.append({
                    'id': part.get('id'),
                    'part_id': part.get('part_id'),
                    'name': part.get('item_name', '-'),
                    'qty': qty,
                    'unit_price': unit_price,
                    'total': total,
                    'note': ''
                })
                total_amount += total
            
            # 2. Get services from quotation_items
            cursor.execute("""
                SELECT 
                    qi.id,
                    qi.qty,
                    qi.unit_price,
                    qi.total,
                    qi.service_id,
                    COALESCE(s.name, qi.custom_name, 'ບໍລິການທີ່ບໍ່ຮູ້ຈັກ') as item_name
                FROM quotation_items qi
                LEFT JOIN services s ON qi.service_id = s.id
                WHERE qi.quotation_id = %s AND qi.part_id IS NULL
                ORDER BY qi.id
            """, (quotation['id'],))
            quotation_services = cursor.fetchall()
            
            for service in quotation_services:
                qty = service.get('qty', 1)
                unit_price = float(service.get('unit_price', 0) or 0)
                total = float(service.get('total', qty * unit_price) or 0)
                
                services_list.append({
                    'id': service.get('id'),
                    'service_id': service.get('service_id'),
                    'name': service.get('item_name', '-'),
                    'qty': qty,
                    'unit_price': unit_price,
                    'total': total
                })
                total_amount += total
        
        final_total = total_amount - total_discount
        if final_total < 0:
            final_total = 0
        
        return {
            "job_order": {
                "id": job_info['id'],
                "job_no": job_info.get('job_no', f"JOB-{job_order_id:04d}"),
                "customer_name": job_info.get('customer_name') or "-",
                "customer_phone": job_info.get('customer_phone') or "-",
                "plate_number": job_info.get('plate_number') or "-",
                "brand": job_info.get('brand') or "-",
                "model": job_info.get('model') or "-",
                "year": job_info.get('year') or "",
                "mileage": job_info.get('mileage') or 0,
                "fuel_level": job_info.get('fuel_level') or "",
                "problem_description": job_info.get('problem_description') or ""
            },
            "parts": parts_list,
            "services": services_list,
            "summary": {
                "total_amount": total_amount,
                "total_discount": total_discount,
                "final_total": final_total
            },
            "quotation_id": quotation['id'] if quotation else None
        }
        
    except Exception as e:
        print(f"Error getting invoice info: {e}")
        import traceback
        traceback.print_exc()
        return {
            "job_order": {
                "id": job_order_id,
                "job_no": f"JOB-{job_order_id:04d}",
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


@router.get("/job-orders/{order_id}/pdf")
def get_job_order_pdf(order_id: int, user: dict = Depends(authenticate_user)):
    """Generate a formal A4 job order PDF receipt"""
    try:
        from utils_pdf import generate_job_order_pdf
        pdf_bytes = generate_job_order_pdf(order_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=job_order_{order_id}.pdf"
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error generating job order PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))