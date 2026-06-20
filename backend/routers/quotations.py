# backend/routers/quotations.py
from fastapi import APIRouter, HTTPException, Depends, Form, Response
from database import get_db
from auth import authenticate_user
from typing import Optional

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
                       e.name as created_by_name,
                       app.name as approved_by_name
                FROM quotations q
                LEFT JOIN job_orders jo ON q.job_order_id = jo.id
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN brands b ON v.brand_id = b.id
                LEFT JOIN employees e ON q.created_by = e.id
                LEFT JOIN employees app ON q.approved_by = app.id
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
                       e.name as created_by_name,
                       app.name as approved_by_name
                FROM quotations q
                LEFT JOIN job_orders jo ON q.job_order_id = jo.id
                LEFT JOIN customers c ON jo.customer_id = c.id
                LEFT JOIN vehicles v ON jo.vehicle_id = v.id
                LEFT JOIN brands b ON v.brand_id = b.id
                LEFT JOIN employees e ON q.created_by = e.id
                LEFT JOIN employees app ON q.approved_by = app.id
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
            # Convert decimal to float
            if quote.get('sub_total'):
                quote['sub_total'] = float(quote['sub_total'])
            if quote.get('discount_amount'):
                quote['discount_amount'] = float(quote['discount_amount'])
            if quote.get('net_total'):
                quote['net_total'] = float(quote['net_total'])
        
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
                   e.name as created_by_name,
                   app.name as approved_by_name
            FROM quotations q
            LEFT JOIN job_orders jo ON q.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN employees e ON q.created_by = e.id
            LEFT JOIN employees app ON q.approved_by = app.id
            WHERE q.id = %s
        """, (quotation_id,))
        
        quotation = cursor.fetchone()
        if not quotation:
            return None
        
        if quotation.get('created_at'):
            quotation['created_at'] = str(quotation['created_at'])
        if quotation.get('brand') is None:
            quotation['brand'] = ""
        
        # Convert decimal to float
        for field in ('sub_total', 'discount_amount', 'net_total'):
            if quotation.get(field) is not None:
                quotation[field] = float(quotation[field])
        
        # Get quotation items — JOIN parts/services to get name and price
        cursor.execute("""
            SELECT
                qi.id,
                qi.quotation_id,
                qi.part_id,
                qi.service_id,
                qi.qty,
                qi.unit_price,
                qi.discount_amount,
                qi.total,
                CASE
                    WHEN qi.part_id IS NOT NULL THEN 'part'
                    WHEN qi.service_id IS NOT NULL THEN 'service'
                    ELSE 'custom'
                END AS item_type,
                COALESCE(qi.part_id, qi.service_id) AS ref_id,
                COALESCE(p.name, s.name, qi.custom_name) AS name
            FROM quotation_items qi
            LEFT JOIN parts p ON qi.part_id = p.id
            LEFT JOIN services s ON qi.service_id = s.id
            WHERE qi.quotation_id = %s
            ORDER BY qi.id
        """, (quotation_id,))
        
        items = cursor.fetchall()
        for item in items:
            for field in ('unit_price', 'total', 'discount_amount'):
                if item.get(field) is not None:
                    item[field] = float(item[field])
        
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


@router.get("/quotations/{quotation_id}/items")
def get_quotation_items(
    quotation_id: int, 
    user: dict = Depends(authenticate_user)
):
    """Get all items for a quotation"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                qi.id,
                qi.part_id,
                qi.service_id,
                qi.qty,
                qi.unit_price,
                qi.discount_amount,
                qi.total,
                CASE
                    WHEN qi.part_id IS NOT NULL THEN 'part'
                    WHEN qi.service_id IS NOT NULL THEN 'service'
                    ELSE 'custom'
                END AS item_type,
                COALESCE(qi.part_id, qi.service_id) AS ref_id,
                COALESCE(p.name, s.name, qi.custom_name) AS name
            FROM quotation_items qi
            LEFT JOIN parts p ON qi.part_id = p.id
            LEFT JOIN services s ON qi.service_id = s.id
            WHERE qi.quotation_id = %s
            ORDER BY qi.id
        """, (quotation_id,))
        items = cursor.fetchall()
        for item in items:
            for field in ('unit_price', 'total', 'discount_amount'):
                if item.get(field) is not None:
                    item[field] = float(item[field])
        return items
    except Exception as e:
        print(f"Error getting quotation items: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()


@router.post("/quotations")
def create_quotation(
    job_order_id: int = Form(...),
    promotion_id: Optional[int] = Form(None),
    user: dict = Depends(authenticate_user)
):
    """Create a new quotation"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO quotations 
            (job_order_id, promotion_id, status, created_by, sub_total, discount_amount, net_total)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (job_order_id, promotion_id, 'draft', user.get('id'), 0, 0, 0))
        
        db.commit()
        quotation_id = cursor.lastrowid
        
        # Update job order status to 'quoting'
        cursor.execute("UPDATE job_orders SET status = 'quoting' WHERE id = %s", (job_order_id,))
        db.commit()
        
        return {
            "id": quotation_id,
            "message": "Quotation created successfully"
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating quotation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.post("/quotations/{quotation_id}/items")
def add_quotation_item(
    quotation_id: int,
    item_type: str = Form(...),
    ref_id: Optional[int] = Form(None),
    qty: int = Form(1),
    discount_amount: float = Form(0),
    custom_name: Optional[str] = Form(None),
    unit_price: Optional[float] = Form(None),
    user: dict = Depends(authenticate_user)
):
    """Add item to quotation (part, service, or custom)"""
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
        
        # Fetch item price based on type
        part_id, service_id = None, None
        if item_type == 'part':
            if not ref_id:
                raise HTTPException(status_code=400, detail="ref_id is required for parts")
            cursor.execute("SELECT sell_price FROM parts WHERE id = %s", (ref_id,))
            part = cursor.fetchone()
            if not part:
                raise HTTPException(status_code=404, detail="Part not found")
            unit_price = float(part['sell_price'])
            part_id = ref_id
        elif item_type == 'service':
            if not ref_id:
                raise HTTPException(status_code=400, detail="ref_id is required for services")
            cursor.execute("SELECT price FROM services WHERE id = %s", (ref_id,))
            service = cursor.fetchone()
            if not service:
                raise HTTPException(status_code=404, detail="Service not found")
            unit_price = float(service['price'])
            service_id = ref_id
        elif item_type == 'custom':
            if unit_price is None:
                raise HTTPException(status_code=400, detail="Price is required for custom items")
            if not custom_name:
                raise HTTPException(status_code=400, detail="Name is required for custom items")
            unit_price = float(unit_price)
        else:
            raise HTTPException(status_code=400, detail="item_type must be 'part', 'service', or 'custom'")
        
        total = qty * unit_price  # gross total before per-item discount
        
        cursor.execute("""
            INSERT INTO quotation_items 
            (quotation_id, part_id, service_id, qty, unit_price, discount_amount, total, custom_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (quotation_id, part_id, service_id, qty, unit_price, discount_amount, total, custom_name))
        
        db.commit()
        
        # Recalculate totals
        calculate_quotation_total(quotation_id, user)
        
        return {
            "id": cursor.lastrowid,
            "message": "Item added successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error adding item: {e}")
        import traceback
        traceback.print_exc()
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
        
        unit_price = float(item['unit_price'])
        total = (qty * unit_price) - discount_amount
        if total < 0:
            total = 0
        
        cursor.execute("""
            UPDATE quotation_items 
            SET qty = %s, discount_amount = %s, total = %s
            WHERE id = %s AND quotation_id = %s
        """, (qty, discount_amount, total, item_id, quotation_id))
        
        db.commit()
        
        # Recalculate totals
        calculate_quotation_total(quotation_id, user)
        
        return {"message": "Item updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating item: {e}")
        import traceback
        traceback.print_exc()
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
        
        # Recalculate totals
        calculate_quotation_total(quotation_id, user)
        
        return {"message": "Item deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting item: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/quotations/{quotation_id}/calculate")
def calculate_quotation_total(
    quotation_id: int,
    user: dict = Depends(authenticate_user)
):
    """Calculate and update quotation totals (sub_total, net_total)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Calculate sum of all items
        cursor.execute("""
            SELECT SUM(total) as total_amount 
            FROM quotation_items 
            WHERE quotation_id = %s
        """, (quotation_id,))
        
        result = cursor.fetchone()
        sub_total = float(result['total_amount']) if result['total_amount'] else 0.0
        
        # Get discount amount from quotation
        cursor.execute("""
            SELECT discount_amount FROM quotations WHERE id = %s
        """, (quotation_id,))
        quote = cursor.fetchone()
        discount_amount = float(quote['discount_amount']) if quote and quote['discount_amount'] else 0.0
        
        # Calculate net total
        net_total = sub_total - discount_amount
        if net_total < 0:
            net_total = 0
        
        # Update quotation with new totals
        cursor.execute("""
            UPDATE quotations 
            SET sub_total = %s, net_total = %s 
            WHERE id = %s
        """, (sub_total, net_total, quotation_id))
        
        db.commit()
        
        return {
            "sub_total": sub_total,
            "discount_amount": discount_amount,
            "net_total": net_total,
            "message": "Total calculated successfully"
        }
    except Exception as e:
        db.rollback()
        print(f"Error calculating total: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/quotations/{quotation_id}/promotion")
def update_quotation_promotion(
    quotation_id: int,
    promotion_id: int = Form(...),
    discount_amount: float = Form(0),
    user: dict = Depends(authenticate_user)
):
    """Apply a promotion to a quotation: set promotion_id and discount_amount, then recalculate totals"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE quotations
            SET promotion_id = %s, discount_amount = %s
            WHERE id = %s
        """, (promotion_id, discount_amount, quotation_id))
        db.commit()

        # Recalculate net total after promotion discount is stored
        calculate_quotation_total(quotation_id, user)

        return {"message": f"Promotion {promotion_id} applied. Discount: {discount_amount}"}
    except Exception as e:
        db.rollback()
        print(f"Error applying promotion: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/quotations/{quotation_id}/discount")
def update_quotation_discount(
    quotation_id: int,
    discount_amount: float = Form(0),
    user: dict = Depends(authenticate_user)
):
    """Update quotation discount amount"""
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
        
        # Update discount
        cursor.execute("""
            UPDATE quotations SET discount_amount = %s WHERE id = %s
        """, (discount_amount, quotation_id))
        db.commit()
        
        # Recalculate totals
        calculate_quotation_total(quotation_id, user)
        
        return {"message": "Discount updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating discount: {e}")
        import traceback
        traceback.print_exc()
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
        if status == 'approved':
            cursor.execute("""
                UPDATE quotations 
                SET status = %s, approved_by = %s 
                WHERE id = %s
            """, (status, user.get('id'), quotation_id))
        else:
            cursor.execute("""
                UPDATE quotations 
                SET status = %s, approved_by = NULL 
                WHERE id = %s
            """, (status, quotation_id))
        db.commit()
        
        # If status is 'approved', update the job order status
        if status == 'approved':
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
        import traceback
        traceback.print_exc()
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
        # Get job_order_id before deleting
        cursor.execute("SELECT job_order_id FROM quotations WHERE id = %s", (quotation_id,))
        result = cursor.fetchone()
        job_order_id = result[0] if result else None
        
        # Delete quotation (items will cascade)
        cursor.execute("DELETE FROM quotations WHERE id = %s", (quotation_id,))
        db.commit()
        
        # Update job order status back to 'pending' or keep as is
        if job_order_id:
            cursor.execute("""
                UPDATE job_orders 
                SET status = 'pending' 
                WHERE id = %s AND status = 'quoting'
            """, (job_order_id,))
            db.commit()
        
        return {"message": "Quotation deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting quotation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/search-parts")
def search_parts(
    keyword: str = "",
    user: dict = Depends(authenticate_user)
):
    """Search for parts by name"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
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
        for r in results:
            if r.get('sell_price'):
                r['sell_price'] = float(r['sell_price'])
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
        for r in results:
            if r.get('price'):
                r['price'] = float(r['price'])
        return results
    except Exception as e:
        print(f"Error searching services: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/quotations/{quotation_id}/pdf")
def get_quotation_pdf(quotation_id: int, user: dict = Depends(authenticate_user)):
    """Generate a formal A4 quotation PDF"""
    try:
        from utils_pdf import generate_quotation_pdf
        pdf_bytes = generate_quotation_pdf(quotation_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=quotation_{quotation_id}.pdf"
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error generating quotation PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))