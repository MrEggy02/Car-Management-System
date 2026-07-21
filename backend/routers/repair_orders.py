# backend/routers/repair_orders.py
from fastapi import APIRouter, HTTPException, Depends, Form, Response
from database import get_db
from auth import authenticate_user
from typing import Optional
from datetime import datetime
from utils_pdf import generate_repair_work_order_pdf

router = APIRouter()


@router.get("/repair-orders")
def get_repair_orders(
    job_order_id: Optional[int] = None,
    status: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """Get all repair orders, optionally filtered by job_order_id or status"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT ro.*, 
                   jo.job_no,
                   c.name as customer_name,
                   c.phone as customer_phone,
                   v.plate_number, 
                   b.name as brand, 
                   v.model,
                   e.name as mechanic_name,
                   q.net_total as quotation_total,
                   (SELECT COUNT(*) FROM parts_usage pu WHERE pu.repair_id = ro.id) as parts_usage_count,
                   (SELECT COUNT(*) FROM quotation_items qi
                    INNER JOIN quotations q ON qi.quotation_id = q.id
                    WHERE q.job_order_id = ro.job_order_id AND q.status = 'approved' AND qi.part_id IS NOT NULL) as quotation_parts_count
            FROM repair_orders ro
            LEFT JOIN job_orders jo ON ro.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN Employees e ON ro.mechanic_id = e.id
            LEFT JOIN quotations q ON jo.id = q.job_order_id AND q.status = 'approved'
            WHERE 1=1
        """
        params = []
        
        if job_order_id:
            query += " AND ro.job_order_id = %s"
            params.append(job_order_id)
        if status:
            query += " AND ro.status = %s"
            params.append(status)
        
        query += " ORDER BY ro.id DESC"
        
        cursor.execute(query, params)
        repair_orders = cursor.fetchall()
        
        for order in repair_orders:
            if order.get('start_date'):
                order['start_date'] = str(order['start_date'])
            if order.get('end_date'):
                order['end_date'] = str(order['end_date'])
            if order.get('brand') is None:
                order['brand'] = "-"
            if order.get('quotation_total'):
                order['quotation_total'] = float(order['quotation_total'])
        
        return repair_orders
    except Exception as e:
        print(f"Error in get_repair_orders: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/repair-orders/{repair_id}")
def get_repair_order(repair_id: int, user: dict = Depends(authenticate_user)):
    """Get a single repair order with parts usage"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT ro.*, 
                   jo.job_no, jo.problem_description,
                   c.name as customer_name, c.phone as customer_phone,
                   v.plate_number, b.name as brand, v.model, v.year, v.color,
                   e.name as mechanic_name,
                   (SELECT COUNT(*) FROM quotation_items qi
                    INNER JOIN quotations q ON qi.quotation_id = q.id
                    WHERE q.job_order_id = ro.job_order_id AND q.status = 'approved' AND qi.part_id IS NOT NULL) as quotation_parts_count
            FROM repair_orders ro
            LEFT JOIN job_orders jo ON ro.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN brands b ON v.brand_id = b.id
            LEFT JOIN Employees e ON ro.mechanic_id = e.id
            WHERE ro.id = %s
        """, (repair_id,))
        
        repair_order = cursor.fetchone()
        if repair_order:
            if repair_order.get('start_date'):
                repair_order['start_date'] = str(repair_order['start_date'])
            if repair_order.get('end_date'):
                repair_order['end_date'] = str(repair_order['end_date'])
            if repair_order.get('brand') is None:
                repair_order['brand'] = "-"
            
            # Get parts usage
            cursor.execute("""
                SELECT pu.*, p.name as part_name
                FROM parts_usage pu
                LEFT JOIN parts p ON pu.part_id = p.id
                WHERE pu.repair_id = %s
            """, (repair_id,))
            parts_usage = cursor.fetchall()
            for part in parts_usage:
                if part.get('cost_price'):
                    part['cost_price'] = float(part['cost_price'])
                if part.get('qty'):
                    part['qty'] = int(part['qty'])
            repair_order['parts_usage'] = parts_usage
        
        return repair_order
    except Exception as e:
        print(f"Error in get_repair_order: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        cursor.close()
        db.close()


@router.get("/repair-orders/{repair_id}/pdf")
def get_repair_order_pdf(repair_id: int, user: dict = Depends(authenticate_user)):
    """Generate a formal A4 repair work order PDF for mechanics"""
    try:
        pdf_bytes = generate_repair_work_order_pdf(repair_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=repair_work_order_{repair_id}.pdf"
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error generating PDF endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MODIFIED: Accept quotation_id as parameter (not stored) ====================
@router.post("/repair-orders")
def create_repair_order(
    job_order_id: int = Form(...),
    mechanic_id: Optional[int] = Form(None),
    quotation_id: Optional[int] = Form(None),  # ✅ Accept quotation_id but do NOT store it
    user: dict = Depends(authenticate_user)
):
    """
    Create a new repair order from a job order
    ✅ ອະນຸຍາດໃຫ້ສ້າງຫຼາຍອັນຕໍ່ Job Order ໄດ້ (ລຶບການກວດສອບຊ້ຳອອກ)
    ✅ quotation_id ຮັບເປັນ Parameter ແຕ່ບໍ່ໄດ້ເກັບໃນ Database (ຕາມ Requirement)
    """
    db = get_db()
    cursor = db.cursor()
    try:
        # ✅ Guard: If there's already an active repair for this job, return it instead of creating duplicate
        cursor.execute(
            "SELECT id FROM repair_orders WHERE job_order_id = %s AND status IN ('working','pending') ORDER BY id DESC LIMIT 1",
            (job_order_id,)
        )
        existing = cursor.fetchone()
        if existing:
            existing_id = existing[0]
            print(f"DEBUG: Existing active repair {existing_id} found for job {job_order_id}, skipping create")
            return {
                "id": existing_id,
                "message": "Existing repair order returned",
                "is_new": False,
                "quotation_id": quotation_id
            }

        # ✅ Insert without quotation_id (not stored)
        cursor.execute("""
            INSERT INTO repair_orders (job_order_id, mechanic_id, status, start_date)
            VALUES (%s, %s, %s, %s)
        """, (job_order_id, mechanic_id, 'working', datetime.now()))
        db.commit()
        repair_id = cursor.lastrowid
        print(f"DEBUG: Created repair {repair_id} for job {job_order_id}, quotation {quotation_id} (not stored)")
        
        # Update job order status to 'repairing'
        cursor.execute("""
            UPDATE job_orders SET status = 'repairing' WHERE id = %s AND status != 'repairing'
        """, (job_order_id,))
        db.commit()
        
        return {
            "id": repair_id,
            "message": "Repair order created successfully",
            "is_new": True,
            "quotation_id": quotation_id  # return it for reference
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating repair order: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/repair-orders/{repair_id}/mechanic")
def assign_mechanic(
    repair_id: int,
    mechanic_id: int = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Assign mechanic to repair order"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE repair_orders SET mechanic_id = %s WHERE id = %s
        """, (mechanic_id, repair_id))
        db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Repair order not found")
        
        return {"message": "Mechanic assigned successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error assigning mechanic: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/repair-orders/{repair_id}/status")
def update_repair_status(
    repair_id: int,
    status: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Update repair order status"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT status, start_date, job_order_id FROM repair_orders WHERE id = %s", (repair_id,))
        current = cursor.fetchone()
        if not current:
            raise HTTPException(status_code=404, detail="Repair order not found")
        
        current_status = current[0]
        job_order_id = current[2]
        
        update_fields = ["status = %s"]
        params = [status]
        
        if status == 'working' and current_status != 'working':
            update_fields.append("start_date = %s")
            params.append(datetime.now())
        
        if status == 'completed':
            update_fields.append("end_date = %s")
            params.append(datetime.now())
        
        params.append(repair_id)
        cursor.execute(f"UPDATE repair_orders SET {', '.join(update_fields)} WHERE id = %s", params)
        db.commit()
        
        # Update job order status based on all repairs
        if job_order_id:
            # Count total and completed repairs for this job
            cursor.execute("""
                SELECT COUNT(*) as total, 
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                FROM repair_orders 
                WHERE job_order_id = %s
            """, (job_order_id,))
            counts = cursor.fetchone()
            total = counts[0] if counts else 0
            completed = counts[1] if counts else 0
            
            if total > 0 and completed == total:
                # All repairs are completed
                cursor.execute("UPDATE job_orders SET status = 'finished' WHERE id = %s", (job_order_id,))
            elif total > 0:
                # At least one repair is still in progress
                cursor.execute("UPDATE job_orders SET status = 'repairing' WHERE id = %s", (job_order_id,))
            db.commit()
        
        return {"message": f"Repair status updated to {status}"}
    except Exception as e:
        db.rollback()
        print(f"Error updating repair status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.post("/repair-orders/{repair_id}/parts-usage")
def add_part_usage(
    repair_id: int,
    part_id: int = Form(...),
    qty: int = Form(...),
    note: Optional[str] = Form(None),
    user: dict = Depends(authenticate_user)
):
    """Add part usage for repair (withdraw parts from stock)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM repair_orders WHERE id = %s", (repair_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Repair order not found")
        
        cursor.execute("SELECT id, cost_price, stock_qty FROM parts WHERE id = %s", (part_id,))
        part = cursor.fetchone()
        
        if not part:
            raise HTTPException(status_code=404, detail=f"Part not found (ID: {part_id})")
        
        if part['stock_qty'] < qty:
            raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {part['stock_qty']}")
        
        cursor.execute("""
            INSERT INTO parts_usage (repair_id, part_id, qty, cost_price, note)
            VALUES (%s, %s, %s, %s, %s)
        """, (repair_id, part['id'], qty, part['cost_price'], note))
        
        usage_id = cursor.lastrowid
        
        cursor.execute("""
            UPDATE parts SET stock_qty = stock_qty - %s WHERE id = %s
        """, (qty, part['id']))
        
        cursor.execute("""
            INSERT INTO stock_movement (part_id, type, qty, ref_type, ref_id, date)
            VALUES (%s, 'OUT', %s, 'repair', %s, NOW())
        """, (part['id'], qty, repair_id))
        
        db.commit()
        
        return {
            "id": usage_id,
            "message": "Part usage recorded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error adding part usage: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/repair-orders/{repair_id}/parts-usage/{usage_id}")
def delete_part_usage(
    repair_id: int,
    usage_id: int,
    user: dict = Depends(authenticate_user)
):
    """Delete part usage and return parts to stock"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT part_id, qty FROM parts_usage WHERE id = %s AND repair_id = %s
        """, (usage_id, repair_id))
        usage = cursor.fetchone()
        if not usage:
            raise HTTPException(status_code=404, detail="Part usage not found")
        
        cursor.execute("""
            UPDATE parts SET stock_qty = stock_qty + %s WHERE id = %s
        """, (usage['qty'], usage['part_id']))
        
        cursor.execute("""
            INSERT INTO stock_movement (part_id, type, qty, ref_type, ref_id, date)
            VALUES (%s, 'IN', %s, 'repair', %s, NOW())
        """, (usage['part_id'], usage['qty'], repair_id))
        
        cursor.execute("DELETE FROM parts_usage WHERE id = %s", (usage_id,))
        
        db.commit()
        
        return {"message": "Part usage deleted, stock updated"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting part usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


# ==================== MODIFIED: Pull parts with optional quotation_id ====================
@router.post("/repair-orders/{repair_id}/pull-quotation-parts")
def pull_quotation_parts(
    repair_id: int,
    quotation_id: Optional[int] = Form(None),  # ✅ ສາມາດສົ່ງ quotation_id ມາເປັນ Option
    user: dict = Depends(authenticate_user)
):
    """
    Retrieve spare parts data from approved quotation,
    deduct inventory stock, record stock movement as 'OUT', 
    and record in parts_usage.
    
    ✅ ຖ້າມີ quotation_id ຈະໃຊ້ quotation ນັ້ນ
    ✅ ຖ້າບໍ່ມີ ຈະໃຊ້ອັນຫຼ້າສຸດ
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # 1. Verify repair order exists and get its job_order_id
        cursor.execute("SELECT id, job_order_id FROM repair_orders WHERE id = %s", (repair_id,))
        repair = cursor.fetchone()
        if not repair:
            raise HTTPException(status_code=404, detail="Repair order not found")
        
        job_order_id = repair["job_order_id"]
        if not job_order_id:
            raise HTTPException(status_code=400, detail="Repair order is not associated with any Job Order")
        
        # 2. Find approved quotation (use specified one or most recent)
        if quotation_id:
            cursor.execute("""
                SELECT id FROM quotations 
                WHERE id = %s AND job_order_id = %s AND status = 'approved'
            """, (quotation_id, job_order_id))
            quotation = cursor.fetchone()
            if not quotation:
                raise HTTPException(status_code=404, detail="Specified quotation not found or not approved")
        else:
            cursor.execute("""
                SELECT id FROM quotations 
                WHERE job_order_id = %s AND status = 'approved' 
                ORDER BY id DESC LIMIT 1
            """, (job_order_id,))
            quotation = cursor.fetchone()
            if not quotation:
                raise HTTPException(status_code=404, detail="No approved quotation found for this Job Order")
        
        quotation_id = quotation["id"]
        
        # 3. Retrieve all quotation items where part_id is not null
        cursor.execute("""
            SELECT qi.part_id, SUM(qi.qty) as qty, p.name as part_name, p.cost_price, p.stock_qty
            FROM quotation_items qi
            LEFT JOIN parts p ON qi.part_id = p.id
            WHERE qi.quotation_id = %s AND qi.part_id IS NOT NULL
            GROUP BY qi.part_id, p.name, p.cost_price, p.stock_qty
        """, (quotation_id,))
        quoted_parts = cursor.fetchall()
        
        if not quoted_parts:
            raise HTTPException(status_code=400, detail="No parts are listed in the approved quotation")
            
        # 4. Query current parts already recorded
        cursor.execute("""
            SELECT part_id, SUM(qty) as used_qty
            FROM parts_usage
            WHERE repair_id = %s
            GROUP BY part_id
        """, (repair_id,))
        already_used_rows = cursor.fetchall()
        already_used_map = {row["part_id"]: row["used_qty"] for row in already_used_rows}
        
        # 5. Calculate what to withdraw
        to_withdraw = []
        for qp in quoted_parts:
            part_id = qp["part_id"]
            if not qp.get("part_name"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Part ID {part_id} in quotation is not found in inventory"
                )
            qty_quoted = int(qp["qty"] or 0)
            qty_used = int(already_used_map.get(part_id, 0))
            qty_to_withdraw = qty_quoted - qty_used
            
            if qty_to_withdraw > 0:
                stock_qty = int(qp["stock_qty"] or 0)
                if stock_qty < qty_to_withdraw:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for {qp['part_name']}. Required: {qty_to_withdraw}, Available: {stock_qty}"
                    )
                to_withdraw.append({
                    "part_id": part_id,
                    "qty": qty_to_withdraw,
                    "cost_price": float(qp["cost_price"] or 0),
                    "part_name": qp["part_name"]
                })
                
        if not to_withdraw:
            raise HTTPException(status_code=400, detail="All parts from quotation have already been pulled")
            
        # 6. Execute updates
        withdrawn_count = 0
        for item in to_withdraw:
            part_id = item["part_id"]
            qty = item["qty"]
            cost_price = item["cost_price"]
            
            cursor.execute("""
                INSERT INTO parts_usage (repair_id, part_id, qty, cost_price, note)
                VALUES (%s, %s, %s, %s, 'Pulled from quotation')
            """, (repair_id, part_id, qty, cost_price))
            
            cursor.execute("""
                UPDATE parts SET stock_qty = stock_qty - %s WHERE id = %s
            """, (qty, part_id))
            
            cursor.execute("""
                INSERT INTO stock_movement (part_id, type, qty, ref_type, ref_id, date)
                VALUES (%s, 'OUT', %s, 'repair', %s, NOW())
            """, (part_id, qty, repair_id))
            
            withdrawn_count += 1
            
        db.commit()
        return {
            "message": f"Successfully pulled {withdrawn_count} parts from quotation",
            "withdrawn_count": withdrawn_count
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Error pulling quotation parts: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/repair-orders/{repair_id}")
def delete_repair_order(repair_id: int, user: dict = Depends(authenticate_user)):
    """Delete a repair order and restore the job order status"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT job_order_id, status FROM repair_orders WHERE id = %s", (repair_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Repair order not found")
        job_order_id, status = row[0], row[1]
        
        if status == 'completed':
            raise HTTPException(status_code=400, detail="Cannot delete completed repair orders")
        
        # 1. Fetch parts used to restore stock
        cursor.execute("SELECT part_id, qty FROM parts_usage WHERE repair_id = %s", (repair_id,))
        usages = cursor.fetchall()
        for part_id, qty in usages:
            cursor.execute("UPDATE parts SET stock_qty = stock_qty + %s WHERE id = %s", (qty, part_id))
            cursor.execute("""
                INSERT INTO stock_movement (part_id, type, qty, ref_type, ref_id, date)
                VALUES (%s, 'IN', %s, 'repair', %s, NOW())
            """, (part_id, qty, repair_id))
            
        # 2. Delete repair order
        cursor.execute("DELETE FROM repair_orders WHERE id = %s", (repair_id,))
        
        # 3. Update job order status
        if job_order_id:
            cursor.execute("SELECT id FROM quotations WHERE job_order_id = %s AND status = 'approved'", (job_order_id,))
            has_approved_quote = cursor.fetchone()
            new_job_status = 'approved' if has_approved_quote else 'pending'
            cursor.execute("UPDATE job_orders SET status = %s WHERE id = %s", (new_job_status, job_order_id))
            
        db.commit()
        return {"message": "Repair order deleted successfully and stock restored"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting repair order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/employees/mechanics")
def get_mechanics(user: dict = Depends(authenticate_user)):
    """Get all mechanics (employees with role = mechanic)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, name as fullname, phone, role
            FROM Employees 
            WHERE role = 'mechanic' AND status = 'active'
            ORDER BY name
        """)
        mechanics = cursor.fetchall()
        print(f"DEBUG: Found mechanics: {mechanics}")
        return mechanics
    except Exception as e:
        print(f"Error getting mechanics: {e}")
        return []
    finally:
        cursor.close()
        db.close()