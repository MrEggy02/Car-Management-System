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
    """Get all invoices"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT i.*, 
                   jo.job_no,
                   c.name as customer_name,
                   v.plate_number,
                   b.name as brand,
                   v.model
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
            if invoice.get('brand') is None:
                invoice['brand'] = ""
            if invoice.get('model') is None:
                invoice['model'] = ""
        
        return invoices
    except Exception as e:
        print(f"Error in get_invoices: {e}")
        import traceback
        traceback.print_exc()
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
                   jo.job_no,
                   c.name as customer_name, c.phone as customer_phone,
                   v.plate_number,
                   b.name as brand,
                   v.model
            FROM invoices i
            LEFT JOIN job_orders jo ON i.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            WHERE i.id = %s
        """, (invoice_id,))
        
        invoice = cursor.fetchone()
        if invoice:
            if invoice.get('paid_date'):
                invoice['paid_date'] = str(invoice['paid_date'])
            if invoice.get('brand') is None:
                invoice['brand'] = ""
            if invoice.get('model') is None:
                invoice['model'] = ""
        
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
    """Get invoice information for a job order - simplified version"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Get job order basic info with brand from brands table
        cursor.execute("""
            SELECT 
                jo.id, jo.job_no, jo.problem_description, jo.mileage, jo.fuel_level,
                c.id as customer_id, c.name as customer_name, c.phone as customer_phone,
                v.id as vehicle_id, v.plate_number, v.model, v.year,
                b.name as brand
            FROM job_orders jo
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            WHERE jo.id = %s
        """, (job_order_id,))
        
        job_info = cursor.fetchone()
        if not job_info:
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
        
        # Get parts usage from repair_orders (actual parts used)
        parts_list = []
        try:
            cursor.execute("""
                SELECT pu.part_id, pu.qty, pu.cost_price, p.name as part_name
                FROM parts_usage pu
                LEFT JOIN parts p ON pu.part_id = p.id
                LEFT JOIN repair_orders ro ON pu.repair_id = ro.id
                WHERE ro.job_order_id = %s
            """, (job_order_id,))
            parts = cursor.fetchall()
            
            for part in parts:
                parts_list.append({
                    'name': part.get('part_name', '-'),
                    'qty': part.get('qty', 0),
                    'unit_price': part.get('cost_price', 0),
                    'total': (part.get('qty', 0) * part.get('cost_price', 0)),
                    'discount_amount': 0
                })
        except Exception as e:
            print(f"Error getting parts usage: {e}")
        
        # Get services from quotation (labor charges)
        services_list = []
        try:
            cursor.execute("""
                SELECT qi.name, qi.qty, qi.unit_price, qi.total
                FROM quotation_items qi
                LEFT JOIN quotations q ON qi.quotation_id = q.id
                WHERE q.job_order_id = %s AND qi.item_type = 'service'
            """, (job_order_id,))
            services = cursor.fetchall()
            
            for service in services:
                services_list.append({
                    'name': service.get('name', '-'),
                    'qty': service.get('qty', 1),
                    'unit_price': service.get('unit_price', 0),
                    'total': service.get('total', 0),
                    'discount_amount': 0
                })
        except Exception as e:
            print(f"Error getting services: {e}")
        
        # Calculate totals
        total_amount = sum(p['total'] for p in parts_list) + sum(s['total'] for s in services_list)
        
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
            "services": services_list if services_list else [
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
                "total_amount": total_amount,
                "total_discount": 0,
                "final_total": total_amount
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
    """Create a new invoice and close job order if paid"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if invoice already exists
        cursor.execute("SELECT id FROM invoices WHERE job_order_id = %s", (job_order_id,))
        existing = cursor.fetchone()
        
        if existing:
            return {
                "id": existing[0],
                "message": "Invoice already exists",
                "existing": True
            }
        
        # Create new invoice
        paid_date = datetime.now() if payment_status == 'paid' else None
        cursor.execute("""
            INSERT INTO invoices 
            (job_order_id, total_amount, total_discount, final_total, 
             payment_method, payment_status, received_amount, change_amount, paid_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (job_order_id, total_amount, total_discount, final_total, 
              payment_method, payment_status, received_amount, change_amount, paid_date))
        
        db.commit()
        invoice_id = cursor.lastrowid
        
        # If paid, close the job order (D10 - ສົ່ງມອບລົດຄືນລູກຄ້າ)
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
    cursor = db.cursor()
    try:
        # Get job_order_id from invoice
        cursor.execute("SELECT job_order_id FROM invoices WHERE id = %s", (invoice_id,))
        result = cursor.fetchone()
        job_order_id = result[0] if result else None
        
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
        
        # Close the job order (D10 - ສົ່ງມອບລົດຄືນລູກຄ້າ)
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
    cursor = db.cursor()
    try:
        # If status is being changed to paid, also update paid_date
        if payment_status == 'paid':
            cursor.execute("""
                UPDATE invoices 
                SET payment_status = %s, paid_date = %s
                WHERE id = %s
            """, (payment_status, datetime.now(), invoice_id))
            
            # Also get job_order_id and close it
            cursor.execute("SELECT job_order_id FROM invoices WHERE id = %s", (invoice_id,))
            result = cursor.fetchone()
            job_order_id = result[0] if result else None
            
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