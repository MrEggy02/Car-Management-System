# backend/routers/quotations.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/quotations")
def get_quotations(
    job_order_id: Optional[int] = None,
    user: dict = Depends(authenticate_user)
):
    """Get all quotations, optionally filtered by job_order_id"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if job_order_id:
            cursor.execute("""
                SELECT q.*, 
                       jo.job_no,
                       c.name as customer_name,
                       v.plate_number,
                       b.name as brand,
                       u.fullname as created_by_name
                FROM quotations q
                LEFT JOIN job_orders jo ON q.job_order_id = jo.id
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN brands b ON v.brand_id = b.id
                LEFT JOIN users u ON q.created_by = u.id
                WHERE q.job_order_id = %s
                ORDER BY q.id DESC
            """, (job_order_id,))
        else:
            cursor.execute("""
                SELECT q.*, 
                       jo.job_no,
                       c.name as customer_name,
                       v.plate_number,
                       b.name as brand,
                       u.fullname as created_by_name
                FROM quotations q
                LEFT JOIN job_orders jo ON q.job_order_id = jo.id
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN brands b ON v.brand_id = b.id
                LEFT JOIN users u ON q.created_by = u.id
                ORDER BY q.id DESC
            """)
        
        quotations = cursor.fetchall()
        
        for quote in quotations:
            if quote.get('created_at'):
                quote['created_at'] = str(quote['created_at'])
            if quote.get('valid_until'):
                quote['valid_until'] = str(quote['valid_until'])
            if quote.get('brand') is None:
                quote['brand'] = ""
        
        return quotations
    except Exception as e:
        print(f"Error in get_quotations: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/quotations/{quotation_id}")
def get_quotation(quotation_id: int, user: dict = Depends(authenticate_user)):
    """Get a single quotation with its items"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Fixed: Changed v.brand to b.name as brand
        cursor.execute("""
            SELECT q.*, 
                   jo.job_no,
                   jo.problem_description,
                   c.name as customer_name,
                   c.phone as customer_phone,
                   c.address,
                   v.plate_number,
                   b.name as brand,
                   v.model,
                   v.year,
                   v.color,
                   u.fullname as created_by_name
            FROM quotations q
            LEFT JOIN job_orders jo ON q.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN users u ON q.created_by = u.id
            WHERE q.id = %s
        """, (quotation_id,))
        
        quotation = cursor.fetchone()
        if not quotation:
            return None
        
        if quotation.get('created_at'):
            quotation['created_at'] = str(quotation['created_at'])
        if quotation.get('valid_until'):
            quotation['valid_until'] = str(quotation['valid_until'])
        if quotation.get('brand') is None:
            quotation['brand'] = ""
        
        # Get quotation items
        cursor.execute("""
            SELECT id, item_type, ref_id, name, qty, unit_price, discount_amount, total
            FROM quotation_items
            WHERE quotation_id = %s
            ORDER BY item_type, id
        """, (quotation_id,))
        
        items = cursor.fetchall()
        quotation['items'] = items
        
        return quotation
    except Exception as e:
        print(f"Error in get_quotation: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        cursor.close()
        db.close()


@router.post("/quotations")
def create_quotation(
    job_order_id: int = Form(...),
    valid_until: str = Form(None),
    notes: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """Create a new quotation"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Set valid_until to 7 days from now if not provided
        if not valid_until:
            valid_until = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO quotations (job_order_id, status, valid_until, notes, created_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (job_order_id, 'draft', valid_until, notes, user.get('id')))
        
        db.commit()
        quotation_id = cursor.lastrowid
        
        return {
            "id": quotation_id,
            "message": "Quotation created successfully"
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating quotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.post("/quotations/{quotation_id}/items")
def add_quotation_item(
    quotation_id: int,
    item_type: str = Form(...),
    ref_id: int = Form(...),
    qty: int = Form(1),
    user: dict = Depends(authenticate_user)
):
    """Add item to quotation (part or service)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Check if quotation exists and is draft
        cursor.execute("SELECT status FROM quotations WHERE id = %s", (quotation_id,))
        quote = cursor.fetchone()
        if not quote:
            raise HTTPException(status_code=404, detail="Quotation not found")
        if quote['status'] != 'draft':
            raise HTTPException(status_code=400, detail="Can only modify draft quotations")
        
        # Get item details based on type
        name = ""
        unit_price = 0
        
        if item_type == 'part':
            cursor.execute("SELECT name, sell_price FROM parts WHERE id = %s", (ref_id,))
            part = cursor.fetchone()
            if part:
                name = part['name']
                unit_price = part['sell_price']
        elif item_type == 'service':
            cursor.execute("SELECT name, price FROM services WHERE id = %s", (ref_id,))
            service = cursor.fetchone()
            if service:
                name = service['name']
                unit_price = service['price']
        
        if not name:
            raise HTTPException(status_code=404, detail=f"{item_type} not found")
        
        total = qty * unit_price
        
        cursor.execute("""
            INSERT INTO quotation_items 
            (quotation_id, item_type, ref_id, name, qty, unit_price, discount_amount, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (quotation_id, item_type, ref_id, name, qty, unit_price, 0, total))
        
        db.commit()
        
        return {
            "id": cursor.lastrowid,
            "message": "Item added successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error adding item: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/quotations/{quotation_id}/items/{item_id}")
def update_quotation_item(
    quotation_id: int,
    item_id: int,
    qty: int = Form(...),
    discount_amount: float = Form(0),
    user: dict = Depends(authenticate_user)
):
    """Update quotation item quantity or discount"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Check if quotation is draft
        cursor.execute("SELECT status FROM quotations WHERE id = %s", (quotation_id,))
        quote = cursor.fetchone()
        if not quote:
            raise HTTPException(status_code=404, detail="Quotation not found")
        if quote['status'] != 'draft':
            raise HTTPException(status_code=400, detail="Can only modify draft quotations")
        
        cursor.execute("""
            SELECT unit_price FROM quotation_items 
            WHERE id = %s AND quotation_id = %s
        """, (item_id, quotation_id))
        item = cursor.fetchone()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        total = qty * item['unit_price'] - discount_amount
        
        cursor.execute("""
            UPDATE quotation_items 
            SET qty = %s, discount_amount = %s, total = %s
            WHERE id = %s AND quotation_id = %s
        """, (qty, discount_amount, total, item_id, quotation_id))
        
        db.commit()
        
        return {"message": "Item updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating item: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/quotations/{quotation_id}/items/{item_id}")
def delete_quotation_item(
    quotation_id: int,
    item_id: int,
    user: dict = Depends(authenticate_user)
):
    """Delete item from quotation"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if quotation is draft
        cursor.execute("SELECT status FROM quotations WHERE id = %s", (quotation_id,))
        quote = cursor.fetchone()
        if quote and quote[0] != 'draft':
            raise HTTPException(status_code=400, detail="Can only modify draft quotations")
        
        cursor.execute("DELETE FROM quotation_items WHERE id = %s AND quotation_id = %s", (item_id, quotation_id))
        db.commit()
        
        return {"message": "Item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting item: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/quotations/{quotation_id}/calculate")
def calculate_quotation_total(
    quotation_id: int,
    user: dict = Depends(authenticate_user)
):
    """Calculate and update quotation total price"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT SUM(total) as total_price 
            FROM quotation_items 
            WHERE quotation_id = %s
        """, (quotation_id,))
        
        result = cursor.fetchone()
        total_price = result['total_price'] if result['total_price'] else 0
        
        cursor.execute("""
            UPDATE quotations SET total_price = %s WHERE id = %s
        """, (total_price, quotation_id))
        
        db.commit()
        
        return {"total_price": total_price, "message": "Total calculated successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error calculating total: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/quotations/{quotation_id}/status")
def update_quotation_status(
    quotation_id: int,
    status: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Update quotation status"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE quotations SET status = %s WHERE id = %s", (status, quotation_id))
        db.commit()
        
        # If status is 'approved', update the job order status to 'approved' as well
        if status == 'approved':
            # Get job_order_id from quotation
            cursor.execute("SELECT job_order_id FROM quotations WHERE id = %s", (quotation_id,))
            result = cursor.fetchone()
            if result:
                job_order_id = result[0]
                cursor.execute("UPDATE job_orders SET status = 'approved' WHERE id = %s", (job_order_id,))
                db.commit()
        
        return {"message": f"Quotation status updated to {status}"}
    except Exception as e:
        db.rollback()
        print(f"Error updating status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/quotations/{quotation_id}")
def delete_quotation(
    quotation_id: int,
    user: dict = Depends(authenticate_user)
):
    """Delete a quotation"""
    db = get_db()
    cursor = db.cursor()
    try:
        # First delete quotation items (cascade should handle this)
        cursor.execute("DELETE FROM quotations WHERE id = %s", (quotation_id,))
        db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        return {"message": "Quotation deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting quotation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/search-parts")
def search_parts(
    keyword: str = "",
    user: dict = Depends(authenticate_user)
):
    """Search for parts by name or code"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Remove part_code since it doesn't exist in your parts table
        query = """
            SELECT id, name, sell_price, stock_qty
            FROM parts
            WHERE name LIKE %s
            ORDER BY name
            LIMIT 20
        """
        search_term = f"%{keyword}%" if keyword else "%"
        cursor.execute(query, (search_term,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error searching parts: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/search-services")
def search_services(
    keyword: str = "",
    user: dict = Depends(authenticate_user)
):
    """Search for services by name"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Fixed: services table has 'name' column, not 'service_name'
        query = """
            SELECT id, name, description, price
            FROM services
            WHERE name LIKE %s
            ORDER BY name
            LIMIT 20
        """
        search_term = f"%{keyword}%" if keyword else "%"
        cursor.execute(query, (search_term,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error searching services: {e}")
        return []
    finally:
        cursor.close()
        db.close()