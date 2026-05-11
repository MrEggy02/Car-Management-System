from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional, List
from datetime import datetime
import json

router = APIRouter()


# ========== Purchase Orders ==========

@router.get("/purchase-orders")
def get_purchase_orders(
    status: Optional[str] = None,
    user: dict = Depends(authenticate_user)
):
    """Get all purchase orders, optionally filtered by status"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT po.*, 
                   s.name as supplier_name,
                   u.fullname as created_by_name,
                   ru.fullname as received_by_name
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.id
            LEFT JOIN users u ON po.created_by = u.id
            LEFT JOIN users ru ON po.received_by = ru.id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND po.status = %s"
            params.append(status)
        
        query += " ORDER BY po.id DESC"
        
        cursor.execute(query, params)
        orders = cursor.fetchall()
        
        for order in orders:
            if order.get('order_date'):
                order['order_date'] = str(order['order_date'])
            if order.get('received_at'):
                order['received_at'] = str(order['received_at'])
            if order.get('total_amount'):
                order['total_amount'] = float(order['total_amount'])
        
        return orders
    except Exception as e:
        print(f"Error in get_purchase_orders: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/purchase-orders/{po_id}")
def get_purchase_order(po_id: int, user: dict = Depends(authenticate_user)):
    """Get a single purchase order with items"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        print(f"DEBUG: Fetching purchase order with ID: {po_id}")
        
        cursor.execute("""
            SELECT po.*, 
                   s.name as supplier_name,
                   u.fullname as created_by_name,
                   ru.fullname as received_by_name
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.id
            LEFT JOIN users u ON po.created_by = u.id
            LEFT JOIN users ru ON po.received_by = ru.id
            WHERE po.id = %s
        """, (po_id,))
        
        order = cursor.fetchone()
        
        if order:
            print(f"DEBUG: Found order: {order.get('po_no')}")
            
            # Convert dates to string
            if order.get('order_date'):
                order['order_date'] = str(order['order_date'])
            if order.get('received_at'):
                order['received_at'] = str(order['received_at'])
            
            # Convert Decimal to float
            if order.get('total_amount'):
                order['total_amount'] = float(order['total_amount'])
            
            # Get items - removed part_code since it doesn't exist
            cursor.execute("""
                SELECT pi.*, p.name as part_name, p.unit
                FROM purchase_items pi
                LEFT JOIN parts p ON pi.part_id = p.id
                WHERE pi.purchase_id = %s
            """, (po_id,))
            
            items = cursor.fetchall()
            
            # Convert items data
            for item in items:
                if item.get('unit_cost'):
                    item['unit_cost'] = float(item['unit_cost'])
                if item.get('total_line'):
                    item['total_line'] = float(item['total_line'])
                if item.get('received_qty') is None:
                    item['received_qty'] = 0
                # Ensure part_name has a value
                if not item.get('part_name'):
                    item['part_name'] = f"Part ID: {item.get('part_id')}"
            
            order['items'] = items
            print(f"DEBUG: Found {len(items)} items")
        else:
            print(f"DEBUG: No order found with ID: {po_id}")
        
        return order
    except Exception as e:
        print(f"Error in get_purchase_order: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        cursor.close()
        db.close()


@router.post("/purchase-orders")
def create_purchase_order(
    supplier_id: int = Form(...),
    items: str = Form(...),  # JSON string of items: [{"part_id": 1, "qty": 5, "unit_cost": 100}]
    user: dict = Depends(authenticate_user)
):
    """Create a new purchase order"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Generate PO number
        year = datetime.now().year
        cursor.execute("SELECT COUNT(*) as count FROM purchase_orders WHERE YEAR(order_date) = %s", (year,))
        count = cursor.fetchone()
        count_num = count[0] + 1 if count else 1
        po_no = f"PO-{year}-{count_num:04d}"
        
        # Parse items
        items_list = json.loads(items)
        
        # Calculate total amount
        total_amount = sum(item.get('qty', 0) * item.get('unit_cost', 0) for item in items_list)
        
        # Insert purchase order
        cursor.execute("""
            INSERT INTO purchase_orders 
            (po_no, supplier_id, total_amount, status, created_by, order_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (po_no, supplier_id, total_amount, 'pending', user.get('id'), datetime.now()))
        
        db.commit()
        po_id = cursor.lastrowid
        
        # Insert items
        for item in items_list:
            cursor.execute("""
                INSERT INTO purchase_items 
                (purchase_id, part_id, qty, unit_cost, total_line, received_qty)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (po_id, item.get('part_id'), item.get('qty'), 
                  item.get('unit_cost'), item.get('qty') * item.get('unit_cost'), 0))
        
        db.commit()
        
        return {
            "id": po_id,
            "po_no": po_no,
            "message": "Purchase order created successfully"
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating purchase order: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/purchase-orders/{po_id}/status")
def update_purchase_order_status(
    po_id: int,
    status: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Update purchase order status (pending/ordered/received/cancelled)"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if order exists
        cursor.execute("SELECT id FROM purchase_orders WHERE id = %s", (po_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        cursor.execute("""
            UPDATE purchase_orders SET status = %s WHERE id = %s
        """, (status, po_id))
        db.commit()
        
        return {"message": f"Purchase order status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating purchase order status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.post("/purchase-orders/{po_id}/receive")
def receive_purchase_order(
    po_id: int,
    received_items: str = Form(...),  # JSON: [{"item_id": 1, "received_qty": 5}]
    user: dict = Depends(authenticate_user)
):
    """Receive items from purchase order and update stock"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Check if purchase order exists
        cursor.execute("SELECT status FROM purchase_orders WHERE id = %s", (po_id,))
        po = cursor.fetchone()
        if not po:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        if po['status'] == 'received':
            raise HTTPException(status_code=400, detail="Purchase order already received")
        
        received_items_list = json.loads(received_items)
        
        # Update each item
        for item in received_items_list:
            # Update purchase item received_qty
            cursor.execute("""
                UPDATE purchase_items 
                SET received_qty = received_qty + %s 
                WHERE id = %s AND purchase_id = %s
            """, (item.get('received_qty'), item.get('item_id'), po_id))
            
            # Get part_id and unit_cost
            cursor.execute("""
                SELECT part_id, unit_cost FROM purchase_items WHERE id = %s
            """, (item.get('item_id'),))
            pi = cursor.fetchone()
            
            if pi:
                # Update stock quantity in parts
                cursor.execute("""
                    UPDATE parts 
                    SET stock_qty = stock_qty + %s 
                    WHERE id = %s
                """, (item.get('received_qty'), pi['part_id']))
                
                # Record stock movement
                cursor.execute("""
                    INSERT INTO stock_movement 
                    (part_id, type, qty, ref_type, ref_id, date)
                    VALUES (%s, 'IN', %s, 'purchase', %s, %s)
                """, (pi['part_id'], item.get('received_qty'), po_id, datetime.now()))
        
        # Update purchase order status
        cursor.execute("""
            UPDATE purchase_orders 
            SET status = 'received', received_by = %s, received_at = %s
            WHERE id = %s
        """, (user.get('id'), datetime.now(), po_id))
        
        db.commit()
        
        return {"message": "Purchase order received successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error receiving purchase order: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/purchase-orders/{po_id}")
def delete_purchase_order(po_id: int, user: dict = Depends(authenticate_user)):
    """Delete a purchase order"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if order exists
        cursor.execute("SELECT id FROM purchase_orders WHERE id = %s", (po_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        # First delete items
        cursor.execute("DELETE FROM purchase_items WHERE purchase_id = %s", (po_id,))
        # Then delete order
        cursor.execute("DELETE FROM purchase_orders WHERE id = %s", (po_id,))
        db.commit()
        return {"message": "Purchase order deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting purchase order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


# ========== Stock Movement ==========

@router.get("/stock-movements")
def get_stock_movements(
    part_id: Optional[int] = None,
    limit: int = 100,
    user: dict = Depends(authenticate_user)
):
    """Get stock movements history"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT sm.*, 
                   p.name as part_name
            FROM stock_movement sm
            LEFT JOIN parts p ON sm.part_id = p.id
            WHERE 1=1
        """
        params = []
        
        if part_id:
            query += " AND sm.part_id = %s"
            params.append(part_id)
        
        query += " ORDER BY sm.date DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        movements = cursor.fetchall()
        
        for movement in movements:
            if movement.get('date'):
                movement['date'] = str(movement['date'])
            if movement.get('qty'):
                movement['qty'] = int(movement['qty'])
        
        return movements
    except Exception as e:
        print(f"Error getting stock movements: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()