# backend/routers/promotions.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional, List
from datetime import date
import json

router = APIRouter()

# ========== Promotions CRUD ==========

@router.get("/promotions")
def get_promotions(user: dict = Depends(authenticate_user)):
    """Get all promotions"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Promotions ORDER BY id DESC")
    promotions = cursor.fetchall()
    cursor.close()
    db.close()
    return promotions

@router.post("/promotions")
def add_promotion(
    name: str = Form(...),
    discount_type: str = Form(...),
    value: float = Form(...),
    min_amount: float = Form(0),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    status: str = Form("active"),
    user: dict = Depends(authenticate_user)
):
    """Add new promotion"""
    if discount_type not in ['percent', 'amount']:
        raise HTTPException(status_code=400, detail="Discount type must be 'percent' or 'amount'")
    if status not in ['active', 'inactive']:
        raise HTTPException(status_code=400, detail="Status must be 'active' or 'inactive'")
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO Promotions (name, discount_type, value, min_amount, start_date, end_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, discount_type, value, min_amount, start_date, end_date, status))
        db.commit()
        return {"message": "Promotion added successfully", "id": cursor.lastrowid}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.put("/promotions/{promo_id}")
def update_promotion(
    promo_id: int,
    name: str = Form(...),
    discount_type: str = Form(...),
    value: float = Form(...),
    min_amount: float = Form(0),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    status: str = Form("active"),
    user: dict = Depends(authenticate_user)
):
    """Update promotion"""
    if discount_type not in ['percent', 'amount']:
        raise HTTPException(status_code=400, detail="Discount type must be 'percent' or 'amount'")
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM Promotions WHERE id = %s", (promo_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    try:
        cursor.execute("""
            UPDATE Promotions SET 
                name = %s, discount_type = %s, value = %s, min_amount = %s,
                start_date = %s, end_date = %s, status = %s
            WHERE id = %s
        """, (name, discount_type, value, min_amount, start_date, end_date, status, promo_id))
        db.commit()
        return {"message": "Promotion updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.delete("/promotions/{promo_id}")
def delete_promotion(promo_id: int, user: dict = Depends(authenticate_user)):
    """Delete promotion"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM Promotions WHERE id = %s", (promo_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    try:
        # Delete related parts and services first (cascade should handle)
        cursor.execute("DELETE FROM Promotion_Parts WHERE promotion_id = %s", (promo_id,))
        cursor.execute("DELETE FROM Promotion_Services WHERE promotion_id = %s", (promo_id,))
        cursor.execute("DELETE FROM Promotions WHERE id = %s", (promo_id,))
        db.commit()
        return {"message": "Promotion deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.get("/promotions/active")
def get_active_promotions(user: dict = Depends(authenticate_user)):
    """Get active promotions (not expired)"""
    today = date.today()
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM Promotions 
        WHERE status = 'active' 
        AND (start_date IS NULL OR start_date <= %s)
        AND (end_date IS NULL OR end_date >= %s)
        ORDER BY id DESC
    """, (today, today))
    promotions = cursor.fetchall()
    cursor.close()
    db.close()
    return promotions

# ========== Promotion Parts ==========

@router.get("/promotions/{promotion_id}/parts")
def get_promotion_parts(promotion_id: int, user: dict = Depends(authenticate_user)):
    """Get all parts in a promotion"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT pp.id, pp.part_id, pp.qty, p.name as part_name, p.part_code, p.sell_price
            FROM Promotion_Parts pp
            LEFT JOIN Parts p ON pp.part_id = p.id
            WHERE pp.promotion_id = %s
            ORDER BY p.name
        """, (promotion_id,))
        items = cursor.fetchall()
        return items
    except Exception as e:
        print(f"Error getting promotion parts: {e}")
        return []
    finally:
        cursor.close()
        db.close()

@router.post("/promotions/{promotion_id}/parts")
def add_promotion_part(
    promotion_id: int,
    part_id: int = Form(...),
    qty: int = Form(1),
    user: dict = Depends(authenticate_user)
):
    """Add part to promotion"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check if promotion exists
        cursor.execute("SELECT id FROM Promotions WHERE id = %s", (promotion_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Promotion not found")
        
        # Check if part exists
        cursor.execute("SELECT id FROM Parts WHERE id = %s", (part_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Part not found")
        
        # Check if already exists
        cursor.execute("SELECT id FROM Promotion_Parts WHERE promotion_id = %s AND part_id = %s", (promotion_id, part_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Part already in this promotion")
        
        cursor.execute("""
            INSERT INTO Promotion_Parts (promotion_id, part_id, qty)
            VALUES (%s, %s, %s)
        """, (promotion_id, part_id, qty))
        db.commit()
        return {"message": "Part added to promotion successfully", "id": cursor.lastrowid}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.delete("/promotions/{promotion_id}/parts/{item_id}")
def delete_promotion_part(
    promotion_id: int,
    item_id: int,
    user: dict = Depends(authenticate_user)
):
    """Remove part from promotion"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("DELETE FROM Promotion_Parts WHERE id = %s AND promotion_id = %s", (item_id, promotion_id))
        db.commit()
        return {"message": "Part removed from promotion successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.delete("/promotions/{promotion_id}/parts")
def clear_promotion_parts(promotion_id: int, user: dict = Depends(authenticate_user)):
    """Remove all parts from promotion"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("DELETE FROM Promotion_Parts WHERE promotion_id = %s", (promotion_id,))
        db.commit()
        return {"message": "All parts removed from promotion successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

# ========== Promotion Services ==========

@router.get("/promotions/{promotion_id}/services")
def get_promotion_services(promotion_id: int, user: dict = Depends(authenticate_user)):
    """Get all services in a promotion"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT ps.id, ps.service_id, ps.qty, s.name as service_name, s.price
            FROM Promotion_Services ps
            LEFT JOIN Services s ON ps.service_id = s.id
            WHERE ps.promotion_id = %s
            ORDER BY s.name
        """, (promotion_id,))
        items = cursor.fetchall()
        return items
    except Exception as e:
        print(f"Error getting promotion services: {e}")
        return []
    finally:
        cursor.close()
        db.close()

@router.post("/promotions/{promotion_id}/services")
def add_promotion_service(
    promotion_id: int,
    service_id: int = Form(...),
    qty: int = Form(1),
    user: dict = Depends(authenticate_user)
):
    """Add service to promotion"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT id FROM Promotions WHERE id = %s", (promotion_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Promotion not found")
        
        cursor.execute("SELECT id FROM Services WHERE id = %s", (service_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Service not found")
        
        cursor.execute("SELECT id FROM Promotion_Services WHERE promotion_id = %s AND service_id = %s", (promotion_id, service_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Service already in this promotion")
        
        cursor.execute("""
            INSERT INTO Promotion_Services (promotion_id, service_id, qty)
            VALUES (%s, %s, %s)
        """, (promotion_id, service_id, qty))
        db.commit()
        return {"message": "Service added to promotion successfully", "id": cursor.lastrowid}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.delete("/promotions/{promotion_id}/services/{item_id}")
def delete_promotion_service(
    promotion_id: int,
    item_id: int,
    user: dict = Depends(authenticate_user)
):
    """Remove service from promotion"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("DELETE FROM Promotion_Services WHERE id = %s AND promotion_id = %s", (item_id, promotion_id))
        db.commit()
        return {"message": "Service removed from promotion successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.delete("/promotions/{promotion_id}/services")
def clear_promotion_services(promotion_id: int, user: dict = Depends(authenticate_user)):
    """Remove all services from promotion"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("DELETE FROM Promotion_Services WHERE promotion_id = %s", (promotion_id,))
        db.commit()
        return {"message": "All services removed from promotion successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

# ========== Validation ==========

@router.post("/promotions/validate")
def validate_promotion(
    promo_name: str = Form(...),
    total_amount: float = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Validate promotion and calculate discount"""
    today = date.today()
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM Promotions 
        WHERE name = %s AND status = 'active'
        AND (start_date IS NULL OR start_date <= %s)
        AND (end_date IS NULL OR end_date >= %s)
    """, (promo_name, today, today))
    
    promotion = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not promotion:
        return {"valid": False, "message": "Invalid or expired promotion code"}
    
    if total_amount < promotion['min_amount']:
        return {
            "valid": False,
            "message": f"Minimum purchase amount is {int(promotion['min_amount']):,} KIP"
        }
    
    if promotion['discount_type'] == 'percent':
        discount_amount = total_amount * (promotion['value'] / 100)
    else:
        discount_amount = promotion['value']
    
    discount_amount = min(discount_amount, total_amount)
    
    return {
        "valid": True,
        "discount_amount": discount_amount,
        "discount_type": promotion['discount_type'],
        "discount_value": promotion['value'],
        "final_amount": total_amount - discount_amount,
        "promotion_id": promotion['id']
    }

# ========== Available Items for Promotion ==========

@router.get("/promotions/{promotion_id}/available-parts")
def get_available_parts_for_promotion(
    promotion_id: int,
    search: str = "",
    user: dict = Depends(authenticate_user)
):
    """Get parts not yet in this promotion"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        search_param = f"%{search}%" if search else "%"
        cursor.execute("""
            SELECT p.id, p.name, p.sell_price
            FROM Parts p
            WHERE p.id NOT IN (
                SELECT part_id FROM Promotion_Parts WHERE promotion_id = %s
            )
            AND (p.name LIKE %s OR %s = '%%')
            ORDER BY p.name
            LIMIT 50
        """, (promotion_id, search_param, search_param))
        
        parts = cursor.fetchall()
        return parts
    except Exception as e:
        print(f"Error getting available parts: {e}")
        return []
    finally:
        cursor.close()
        db.close()

@router.get("/promotions/{promotion_id}/available-services")
def get_available_services_for_promotion(
    promotion_id: int,
    search: str = "",
    user: dict = Depends(authenticate_user)
):
    """Get services not yet in this promotion"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    try:
        search_param = f"%{search}%" if search else "%"
        cursor.execute("""
            SELECT s.id, s.name, s.price
            FROM Services s
            WHERE s.id NOT IN (
                SELECT service_id FROM Promotion_Services WHERE promotion_id = %s
            )
            AND (s.name LIKE %s OR %s = '%%')
            ORDER BY s.name
            LIMIT 50
        """, (promotion_id, search_param, search_param))
        
        services = cursor.fetchall()
        return services
    except Exception as e:
        print(f"Error getting available services: {e}")
        return []
    finally:
        cursor.close()
        db.close()