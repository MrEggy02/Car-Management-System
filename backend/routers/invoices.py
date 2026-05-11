# backend/routers/invoices.py
from fastapi import APIRouter, HTTPException, Depends, Form
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
    """Get all invoices, optionally filtered by job_order_id or payment_status"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT i.*, 
                   jo.job_no,
                   c.name as customer_name,
                   c.phone as customer_phone,
                   v.plate_number, v.brand, v.model,
                   q.total_price as quotation_total
            FROM invoices i
            LEFT JOIN job_orders jo ON i.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN quotations q ON jo.id = q.job_order_id AND q.status = 'approved'
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
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, user: dict = Depends(authenticate_user)):
    """Get a single invoice by ID"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT i.*, 
                   jo.job_no, jo.problem_description,
                   c.name as customer_name, c.phone as customer_phone, c.address,
                   v.plate_number, v.brand, v.model, v.year, v.color,
                   q.total_price as quotation_total
            FROM invoices i
            LEFT JOIN job_orders jo ON i.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN quotations q ON jo.id = q.job_order_id AND q.status = 'approved'
            WHERE i.id = %s
        """, (invoice_id,))
        
        invoice = cursor.fetchone()
        if invoice:
            if invoice.get('paid_date'):
                invoice['paid_date'] = str(invoice['paid_date'])
        
        return invoice
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
    """Create a new invoice - if exists, return existing"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if invoice already exists for this job order
        cursor.execute("SELECT id FROM invoices WHERE job_order_id = %s", (job_order_id,))
        existing = cursor.fetchone()
        
        if existing:
            existing_id = existing[0]
            print(f"DEBUG: Invoice already exists for job_order_id={job_order_id}, id={existing_id}")
            return {
                "id": existing_id,
                "message": "Invoice already exists for this job order",
                "existing": True
            }
        
        # Create new invoice
        cursor.execute("""
            INSERT INTO invoices 
            (job_order_id, total_amount, total_discount, final_total, 
             payment_method, payment_status, received_amount, change_amount, paid_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (job_order_id, total_amount, total_discount, final_total, 
              payment_method, payment_status, received_amount, change_amount, datetime.now()))
        
        db.commit()
        invoice_id = cursor.lastrowid
        print(f"DEBUG: Created new invoice id={invoice_id}")
        
        # Update job order status
        if payment_status == 'paid':
            cursor.execute("""
                UPDATE job_orders SET status = 'completed' WHERE id = %s
            """, (job_order_id,))
            db.commit()
        
        return {
            "id": invoice_id,
            "message": "Invoice created successfully",
            "existing": False
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error creating invoice: {e}")
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
    """Record payment for an invoice"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if invoice exists
        cursor.execute("SELECT job_order_id FROM invoices WHERE id = %s", (invoice_id,))
        invoice = cursor.fetchone()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        job_order_id = invoice[0]
        
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
        
        # Update job order status to completed
        cursor.execute("""
            UPDATE job_orders SET status = 'completed' WHERE id = %s
        """, (job_order_id,))
        db.commit()
        
        return {"message": "Payment recorded successfully"}
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
    cursor = db.cursor()
    try:
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