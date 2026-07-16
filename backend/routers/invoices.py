# backend/routers/invoices.py
from fastapi import APIRouter, HTTPException, Depends, Form, Response
from database import get_db
from auth import authenticate_user
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/invoices")
def get_invoices(
    job_order_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """Get all invoices"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT i.*, 
                   jo.job_no,
                   COALESCE(c.name, '') as customer_name,
                   COALESCE(v.plate_number, '') as plate_number,
                   COALESCE(b.name, '') as brand,
                   COALESCE(v.model, '') as model
            FROM invoices i
            LEFT JOIN job_orders jo ON i.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            WHERE 1=1
        """
        params = []
        
        if job_order_id:
            query += " AND i.job_order_id = %s"
            params.append(job_order_id)
        if payment_status:
            query += " AND i.payment_status = %s"
            params.append(payment_status)
        
        query += " ORDER BY i.id DESC"
        
        cursor.execute(query, params)
        invoices = cursor.fetchall()
        
        for invoice in invoices:
            if invoice.get('paid_date'):
                invoice['paid_date'] = str(invoice['paid_date'])
        
        return invoices
    except Exception as e:
        print(f"Error in get_invoices: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/invoices/ready-for-invoice")
def get_invoices_ready_for_invoice(user: dict = Depends(authenticate_user)):
    """
    Get job orders that are ready to be invoiced
    ດຶງ Job Orders ທີ່ສາມາດສ້າງໃບເກັບເງິນໄດ້
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


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, user: dict = Depends(authenticate_user)):
    """Get a single invoice by ID with its items"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT i.*, 
                   jo.job_no,
                   COALESCE(c.name, '') as customer_name, 
                   COALESCE(c.phone, '') as customer_phone,
                   COALESCE(v.plate_number, '') as plate_number,
                   COALESCE(b.name, '') as brand,
                   COALESCE(v.model, '') as model,
                   COALESCE(e.name, '') as created_by_name
            FROM invoices i
            LEFT JOIN job_orders jo ON i.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN employees e ON i.created_by = e.id
            WHERE i.id = %s
        """, (invoice_id,))
        
        invoice = cursor.fetchone()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        if invoice.get('paid_date'):
            invoice['paid_date'] = str(invoice['paid_date'])
        
        return invoice
    except Exception as e:
        print(f"Error in get_invoice: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        cursor.close()
        db.close()


@router.get("/job-orders/{job_order_id}/invoice-info")
def get_invoice_info_by_job_order(
    job_order_id: int, 
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
        cursor.execute("""
            SELECT id, discount_amount, sub_total, net_total
            FROM quotations
            WHERE job_order_id = %s AND status = 'approved'
            ORDER BY id DESC LIMIT 1
        """, (job_order_id,))
        quotation = cursor.fetchone()
        
        if quotation:
            total_discount = float(quotation.get('discount_amount', 0) or 0)
            
            # 1. Get parts from quotation_items (using sell price from quotation)
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
            
            # 2. Get only services from quotation_items (including custom services)
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
            }
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


@router.post("/invoices")
def create_invoice(
    job_order_id: int = Form(...),
    total_amount: float = Form(...),
    total_discount: float = Form(0),
    final_total: float = Form(...),
    payment_method: str = Form("cash"),
    payment_status: str = Form("pending"),
    received_amount: float = Form(0),
    change_amount: float = Form(0),
    user: dict = Depends(authenticate_user)
):
    """Create a new invoice"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Check if invoice already exists
        cursor.execute("SELECT id FROM invoices WHERE job_order_id = %s", (job_order_id,))
        existing = cursor.fetchone()
        
        if existing:
            return {
                "id": existing['id'],
                "message": "Invoice already exists",
                "existing": True
            }
        
        # Create new invoice
        paid_date = datetime.now() if payment_status == 'paid' else None
        cursor.execute("""
            INSERT INTO invoices 
            (job_order_id, total_amount, total_discount, final_total, 
             payment_method, payment_status, received_amount, change_amount, 
             paid_date, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (job_order_id, total_amount, total_discount, final_total, 
              payment_method, payment_status, received_amount, change_amount, 
              paid_date, user.get('id')))
        
        db.commit()
        invoice_id = cursor.lastrowid
        
        # If paid, close the job order
        if payment_status == 'paid':
            cursor.execute("""
                UPDATE job_orders 
                SET status = 'closed', closed_at = %s, closed_by = %s
                WHERE id = %s
            """, (datetime.now(), user.get('id'), job_order_id))
            db.commit()
            print(f"DEBUG: Closed job order {job_order_id} after payment")
        
        return {
            "id": invoice_id,
            "message": "Invoice created successfully",
            "existing": False
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating invoice: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/invoices/{invoice_id}/payment")
def record_payment(
    invoice_id: int,
    payment_method: str = Form(...),
    received_amount: float = Form(...),
    change_amount: float = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Record payment for an invoice and close job order"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Get job_order_id from invoice
        cursor.execute("SELECT job_order_id FROM invoices WHERE id = %s", (invoice_id,))
        result = cursor.fetchone()
        job_order_id = result['job_order_id'] if result else None
        
        # Update invoice payment
        cursor.execute("""
            UPDATE invoices 
            SET payment_method = %s, 
                received_amount = %s, 
                change_amount = %s, 
                payment_status = 'paid',
                paid_date = %s
            WHERE id = %s
        """, (payment_method, received_amount, change_amount, datetime.now(), invoice_id))
        db.commit()
        
        # Close the job order
        if job_order_id:
            cursor.execute("""
                UPDATE job_orders 
                SET status = 'closed', closed_at = %s, closed_by = %s
                WHERE id = %s
            """, (datetime.now(), user.get('id'), job_order_id))
            db.commit()
            print(f"DEBUG: Closed job order {job_order_id} after payment")
        
        return {"message": "Payment recorded successfully, job order closed"}
    except Exception as e:
        db.rollback()
        print(f"Error recording payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/invoices/{invoice_id}/status")
def update_invoice_status(
    invoice_id: int,
    payment_status: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Update invoice payment status"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if payment_status == 'paid':
            cursor.execute("""
                UPDATE invoices 
                SET payment_status = %s, paid_date = %s
                WHERE id = %s
            """, (payment_status, datetime.now(), invoice_id))
            
            cursor.execute("SELECT job_order_id FROM invoices WHERE id = %s", (invoice_id,))
            result = cursor.fetchone()
            job_order_id = result['job_order_id'] if result else None
            
            if job_order_id:
                cursor.execute("""
                    UPDATE job_orders 
                    SET status = 'closed', closed_at = %s, closed_by = %s
                    WHERE id = %s
                """, (datetime.now(), user.get('id'), job_order_id))
        else:
            cursor.execute("""
                UPDATE invoices SET payment_status = %s WHERE id = %s
            """, (payment_status, invoice_id))
        
        db.commit()
        
        return {"message": f"Invoice status updated to {payment_status}"}
    except Exception as e:
        db.rollback()
        print(f"Error updating invoice status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, user: dict = Depends(authenticate_user)):
    """Delete an invoice"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM invoices WHERE id = %s", (invoice_id,))
        db.commit()
        return {"message": "Invoice deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/invoices/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: int, user: dict = Depends(authenticate_user)):
    """Generate a formal A4 invoice PDF"""
    try:
        from utils_pdf import generate_invoice_pdf
        pdf_bytes = generate_invoice_pdf(invoice_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=invoice_{invoice_id}.pdf"
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error generating invoice PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}/delivery-note/pdf")
def get_delivery_note_pdf(invoice_id: int, user: dict = Depends(authenticate_user)):
    """Generate a formal A4 car delivery note PDF"""
    try:
        from utils_pdf import generate_delivery_note_pdf
        pdf_bytes = generate_delivery_note_pdf(invoice_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=delivery_note_{invoice_id}.pdf"
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error generating delivery note PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))