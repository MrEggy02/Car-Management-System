# backend/routers/repair_orders.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional
from datetime import datetime

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
                   v.plate_number, v.brand, v.model,
                   u.fullname as mechanic_name,
                   q.total_price as quotation_total
            FROM repair_orders ro
            LEFT JOIN job_orders jo ON ro.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN users u ON ro.mechanic_id = u.id
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
        
        return repair_orders
    except Exception as e:
        print(f"Error in get_repair_orders: {e}")
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
                   v.plate_number, v.brand, v.model, v.year, v.color,
                   u.fullname as mechanic_name
            FROM repair_orders ro
            LEFT JOIN job_orders jo ON ro.job_order_id = jo.id
            LEFT JOIN customers c ON jo.customer_id = c.id
            LEFT JOIN vehicles v ON jo.vehicle_id = v.id
            LEFT JOIN users u ON ro.mechanic_id = u.id
            WHERE ro.id = %s
        """, (repair_id,))
        
        repair_order = cursor.fetchone()
        if repair_order:
            if repair_order.get('start_date'):
                repair_order['start_date'] = str(repair_order['start_date'])
            if repair_order.get('end_date'):
                repair_order['end_date'] = str(repair_order['end_date'])
            
            # Get parts usage
            cursor.execute("""
                SELECT pu.*, p.name as part_name, p.part_code, p.brand
                FROM parts_usage pu
                LEFT JOIN parts p ON pu.part_id = p.id
                WHERE pu.repair_id = %s
            """, (repair_id,))
            repair_order['parts_usage'] = cursor.fetchall()
        
        return repair_order
    finally:
        cursor.close()
        db.close()


@router.post("/repair-orders")
def create_repair_order(
    job_order_id: int = Form(...),
    mechanic_id: int = Form(None),
    user: dict = Depends(authenticate_user)
):
    """Create a new repair order from a job order (can only create once per job order)"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if repair order already exists for this job order
        cursor.execute("SELECT id, mechanic_id, status FROM repair_orders WHERE job_order_id = %s", (job_order_id,))
        existing = cursor.fetchone()
        
        if existing:
            # If exists, return existing repair order info (cannot create new)
            existing_id = existing[0]
            existing_mechanic_id = existing[1]
            existing_status = existing[2]
            
            print(f"DEBUG: Repair order already exists for job_order_id={job_order_id}, id={existing_id}")
            
            raise HTTPException(
                status_code=400, 
                detail=f"Repair order already exists for this job order (ID: {existing_id}). Please use existing repair order."
            )
        
        # Create new repair order
        cursor.execute("""
            INSERT INTO repair_orders (job_order_id, mechanic_id, status, start_date)
            VALUES (%s, %s, %s, %s)
        """, (job_order_id, mechanic_id, 'waiting', datetime.now()))
        
        db.commit()
        repair_id = cursor.lastrowid
        
        print(f"DEBUG: Created new repair order id={repair_id} for job_order_id={job_order_id}")
        
        return {
            "id": repair_id,
            "message": "Repair order created successfully",
            "is_new": True
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error creating repair order: {e}")
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
    """Update repair order status (waiting/working/paused/completed)"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Get current status and start date
        cursor.execute("SELECT status, start_date FROM repair_orders WHERE id = %s", (repair_id,))
        current = cursor.fetchone()
        if not current:
            raise HTTPException(status_code=404, detail="Repair order not found")
        
        update_fields = ["status = %s"]
        params = [status]
        
        # If starting work, set start_date
        if status == 'working' and current[0] != 'working':
            update_fields.append("start_date = %s")
            params.append(datetime.now())
        
        # If completed, set end_date
        if status == 'completed':
            update_fields.append("end_date = %s")
            params.append(datetime.now())
        
        params.append(repair_id)
        cursor.execute(f"UPDATE repair_orders SET {', '.join(update_fields)} WHERE id = %s", params)
        db.commit()
        
        # Also update job order status if completed
        if status == 'completed':
            cursor.execute("""
                UPDATE job_orders SET status = 'finished' 
                WHERE id = (SELECT job_order_id FROM repair_orders WHERE id = %s)
            """, (repair_id,))
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
    user: dict = Depends(authenticate_user)
):
    """Add part usage for repair (withdraw parts from stock)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Check repair order exists
        cursor.execute("SELECT id FROM repair_orders WHERE id = %s", (repair_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Repair order not found")
        
        # Get part cost price
        cursor.execute("SELECT cost_price, stock_qty FROM parts WHERE id = %s", (part_id,))
        part = cursor.fetchone()
        if not part:
            raise HTTPException(status_code=404, detail="Part not found")
        
        # Check stock
        if part['stock_qty'] < qty:
            raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {part['stock_qty']}")
        
        # Add to parts usage
        cursor.execute("""
            INSERT INTO parts_usage (repair_id, part_id, qty, cost_price)
            VALUES (%s, %s, %s, %s)
        """, (repair_id, part_id, qty, part['cost_price']))
        
        # Update stock
        cursor.execute("""
            UPDATE parts SET stock_qty = stock_qty - %s WHERE id = %s
        """, (qty, part_id))
        
        db.commit()
        
        return {
            "id": cursor.lastrowid,
            "message": "Part usage recorded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error adding part usage: {e}")
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
        # Get part usage details
        cursor.execute("""
            SELECT part_id, qty FROM parts_usage WHERE id = %s AND repair_id = %s
        """, (usage_id, repair_id))
        usage = cursor.fetchone()
        if not usage:
            raise HTTPException(status_code=404, detail="Part usage not found")
        
        # Return parts to stock
        cursor.execute("""
            UPDATE parts SET stock_qty = stock_qty + %s WHERE id = %s
        """, (usage['qty'], usage['part_id']))
        
        # Delete usage record
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


@router.get("/employees/mechanics")
def get_mechanics(user: dict = Depends(authenticate_user)):
    """Get all mechanics (employees with role = technician)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, username, fullname, phone 
            FROM users 
            WHERE role = 'technician'
            ORDER BY fullname
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