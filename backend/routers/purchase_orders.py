# backend/routers/purchase_orders.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional, List
from datetime import datetime
import json

router = APIRouter()


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
                   e.name as created_by_name,
                   r.name as received_by_name
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.id
            LEFT JOIN employees e ON po.created_by = e.id
            LEFT JOIN employees r ON po.received_by = r.id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND po.status = %s"
            params.append(status)
        
        query += " ORDER BY po.id DESC"
        
        cursor.execute(query, params)
        purchase_orders = cursor.fetchall()
        
        for po in purchase_orders:
            if po.get('order_date'):
                po['order_date'] = str(po['order_date'])
            if po.get('received_at'):
                po['received_at'] = str(po['received_at'])
        
        return purchase_orders
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
    """Get a single purchase order with its items"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Get purchase order header
        cursor.execute("""
            SELECT po.*, 
                   s.name as supplier_name,
                   e.name as created_by_name,
                   r.name as received_by_name
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.id
            LEFT JOIN employees e ON po.created_by = e.id
            LEFT JOIN employees r ON po.received_by = r.id
            WHERE po.id = %s
        """, (po_id,))
        
        purchase_order = cursor.fetchone()
        if not purchase_order:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        if purchase_order.get('order_date'):
            purchase_order['order_date'] = str(purchase_order['order_date'])
        if purchase_order.get('received_at'):
            purchase_order['received_at'] = str(purchase_order['received_at'])
        
        # Get purchase order items
        cursor.execute("""
            SELECT pi.*, p.name as part_name
            FROM purchase_items pi
            LEFT JOIN parts p ON pi.part_id = p.id
            WHERE pi.purchase_id = %s
        """, (po_id,))
        
        items = cursor.fetchall()
        purchase_order['items'] = items
        
        return purchase_order
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_purchase_order: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.post("/purchase-orders")
def create_purchase_order(
    supplier_id: int = Form(...),
    items: str = Form(...),  # JSON string of items
    user: dict = Depends(authenticate_user)
):
    """
    Create a new purchase order (Process 7.2)
    Updates: D17 (Purchase_Orders) and D18 (Purchase_Items)
    """
    db = get_db()
    cursor = db.cursor()
    try:
        # Parse items JSON
        items_list = json.loads(items)
        
        # Calculate total amount
        total_amount = sum(item.get('qty', 0) * item.get('unit_cost', 0) for item in items_list)
        
        # Generate PO number
        year = datetime.now().year
        cursor.execute("SELECT COUNT(*) as count FROM purchase_orders WHERE YEAR(order_date) = %s", (year,))
        count = cursor.fetchone()
        count_num = count[0] + 1 if count else 1
        po_no = f"PO-{year}-{count_num:04d}"
        
        # Insert purchase order (D17)
        cursor.execute("""
            INSERT INTO purchase_orders 
            (po_no, supplier_id, order_date, total_amount, status, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (po_no, supplier_id, datetime.now(), total_amount, 'ordered', user.get('id')))
        
        db.commit()
        po_id = cursor.lastrowid
        
        # Insert purchase items (D18)
        for item in items_list:
            cursor.execute("""
                INSERT INTO purchase_items 
                (purchase_id, part_id, qty, unit_cost, total_line)
                VALUES (%s, %s, %s, %s, %s)
            """, (po_id, item['part_id'], item['qty'], item['unit_cost'], 
                  item['qty'] * item['unit_cost']))
        
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
    """Update purchase order status"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if purchase order exists
        cursor.execute("SELECT id, status FROM purchase_orders WHERE id = %s", (po_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        current_status = existing[1]
        
        # Validate status transition
        valid_transitions = {
            'pending': ['ordered', 'cancelled'],
            'ordered': ['received', 'cancelled'],
            'received': [],
            'cancelled': []
        }
        
        if status not in valid_transitions.get(current_status, []):
            raise HTTPException(status_code=400, detail=f"Cannot change status from {current_status} to {status}")
        
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
    received_items: str = Form(...),  # JSON string of received items with actual quantities
    user: dict = Depends(authenticate_user)
):
    """
    Receive purchase order and update stock (Process 7.3)
    Updates: D5 (Parts stock), D15 (Stock_Movement), D17 (Purchase_Orders status)
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # Check if purchase order exists and is in 'ordered' status
        cursor.execute("SELECT id, status FROM purchase_orders WHERE id = %s", (po_id,))
        po = cursor.fetchone()
        if not po:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        if po['status'] not in ['pending', 'ordered']:
            raise HTTPException(status_code=400, detail=f"Cannot receive order with status: {po['status']}")
        
        # Parse received items
        received_list = json.loads(received_items)
        
        # Process each received item
        for item in received_list:
            part_id = item['part_id']
            received_qty = item['received_qty']
            
            # Get current stock
            cursor.execute("SELECT stock_qty FROM parts WHERE id = %s", (part_id,))
            part = cursor.fetchone()
            if not part:
                raise HTTPException(status_code=404, detail=f"Part not found (ID: {part_id})")
            
            # Update part stock (D5)
            cursor.execute("""
                UPDATE parts SET stock_qty = stock_qty + %s WHERE id = %s
            """, (received_qty, part_id))
            
            # Add stock movement log (D15)
            cursor.execute("""
                INSERT INTO stock_movement (part_id, type, qty, ref_type, ref_id, date)
                VALUES (%s, 'IN', %s, 'purchase', %s, NOW())
            """, (part_id, received_qty, po_id))
            
            # Update received quantity in purchase_items
            cursor.execute("""
                UPDATE purchase_items 
                SET received_qty = COALESCE(received_qty, 0) + %s
                WHERE purchase_id = %s AND part_id = %s
            """, (received_qty, po_id, part_id))
        
        # Update purchase order status to 'received'
        cursor.execute("""
            UPDATE purchase_orders 
            SET status = 'received', received_by = %s, received_at = NOW()
            WHERE id = %s
        """, (user.get('id'), po_id))
        
        db.commit()
        
        return {"message": "Purchase order received and stock updated successfully"}
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
def delete_purchase_order(
    po_id: int,
    user: dict = Depends(authenticate_user)
):
    """Delete a purchase order (only if status is 'pending')"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if purchase order exists and is pending
        cursor.execute("SELECT id, status FROM purchase_orders WHERE id = %s", (po_id,))
        po = cursor.fetchone()
        if not po:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        
        if po[1] != 'pending':
            raise HTTPException(status_code=400, detail="Cannot delete purchase order that is not in pending status")
        
        # Delete purchase items first (foreign key)
        cursor.execute("DELETE FROM purchase_items WHERE purchase_id = %s", (po_id,))
        
        # Delete purchase order
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


@router.get("/stock-movements")
def get_stock_movements(
    part_id: Optional[int] = None,
    limit: int = 100,
    user: dict = Depends(authenticate_user)
):
    """Get stock movement history (D15)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT sm.*, p.name as part_name
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
        
        return movements
    except Exception as e:
        print(f"Error getting stock movements: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/parts/low-stock")
def get_low_stock_parts(user: dict = Depends(authenticate_user)):
    """
    Get low stock parts for alert (Process 7.1)
    Returns parts where stock_qty <= min_stock
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.id, p.name, p.stock_qty, p.min_stock, 
                   s.name as supplier_name, s.phone as supplier_phone
            FROM parts p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.stock_qty <= p.min_stock
            ORDER BY (p.stock_qty / p.min_stock) ASC
        """)
        low_stock_parts = cursor.fetchall()
        
        return low_stock_parts
    except Exception as e:
        print(f"Error getting low stock parts: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        cursor.close()
        db.close()