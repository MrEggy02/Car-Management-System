from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional
from datetime import date

router = APIRouter()

@router.get("/promotions")
def get_promotions(user: dict = Depends(authenticate_user)):
    """ດຶງຂໍ້ມູນໂປຣໂມຊັນທັງໝົດ"""
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
    min_qty: int = Form(1),
    min_amount: float = Form(0),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    status: str = Form("active"),
    user: dict = Depends(authenticate_user)
):
    """ເພີ່ມໂປຣໂມຊັນໃໝ່"""
    # Validate discount_type
    if discount_type not in ['percent', 'amount']:
        raise HTTPException(status_code=400, detail="ປະເພດສ່ວນຫຼຸດຕ້ອງເປັນ 'percent' ຫຼື 'amount'")
    
    # Validate status
    if status not in ['active', 'inactive']:
        raise HTTPException(status_code=400, detail="ສະຖານະຕ້ອງເປັນ 'active' ຫຼື 'inactive'")
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO Promotions (name, discount_type, value, min_qty, min_amount, start_date, end_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, discount_type, value, min_qty, min_amount, start_date, end_date, status))
        db.commit()
        return {"message": "ເພີ່ມໂປຣໂມຊັນສຳເລັດ", "id": cursor.lastrowid}
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
    min_qty: int = Form(1),
    min_amount: float = Form(0),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    status: str = Form("active"),
    user: dict = Depends(authenticate_user)
):
    """ອັບເດດຂໍ້ມູນໂປຣໂມຊັນ"""
    # Validate discount_type
    if discount_type not in ['percent', 'amount']:
        raise HTTPException(status_code=400, detail="ປະເພດສ່ວນຫຼຸດຕ້ອງເປັນ 'percent' ຫຼື 'amount'")
    
    # Validate status
    if status not in ['active', 'inactive']:
        raise HTTPException(status_code=400, detail="ສະຖານະຕ້ອງເປັນ 'active' ຫຼື 'inactive'")
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if promotion exists
    cursor.execute("SELECT id FROM Promotions WHERE id = %s", (promo_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="ບໍ່ພົບໂປຣໂມຊັນ")
    
    try:
        cursor.execute("""
            UPDATE Promotions SET 
                name = %s,
                discount_type = %s,
                value = %s,
                min_qty = %s,
                min_amount = %s,
                start_date = %s,
                end_date = %s,
                status = %s
            WHERE id = %s
        """, (name, discount_type, value, min_qty, min_amount, start_date, end_date, status, promo_id))
        db.commit()
        return {"message": "ແກ້ໄຂໂປຣໂມຊັນສຳເລັດ"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.delete("/promotions/{promo_id}")
def delete_promotion(promo_id: int, user: dict = Depends(authenticate_user)):
    """ລຶບໂປຣໂມຊັນ"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if promotion exists
    cursor.execute("SELECT id FROM Promotions WHERE id = %s", (promo_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="ບໍ່ພົບໂປຣໂມຊັນ")
    
    try:
        cursor.execute("DELETE FROM Promotions WHERE id = %s", (promo_id,))
        db.commit()
        return {"message": "ລຶບໂປຣໂມຊັນສຳເລັດ"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.get("/promotions/active")
def get_active_promotions(user: dict = Depends(authenticate_user)):
    """ດຶງຂໍ້ມູນໂປຣໂມຊັນທີ່ຍັງໃຊ້ງານໄດ້ (ຍັງບໍ່ໝົດອາຍຸ)"""
    from datetime import date
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

@router.post("/promotions/validate")
def validate_promotion(
    promo_code: str = Form(...),
    total_amount: float = Form(...),
    quantity: int = Form(1),
    user: dict = Depends(authenticate_user)
):
    """ກວດສອບຄວາມຖືກຕ້ອງຂອງໂປຣໂມຊັນ ແລະ ຄຳນວນສ່ວນຫຼຸດ"""
    from datetime import date
    today = date.today()
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Find promotion by name (as promo code)
    cursor.execute("""
        SELECT * FROM Promotions 
        WHERE name = %s 
        AND status = 'active'
        AND (start_date IS NULL OR start_date <= %s)
        AND (end_date IS NULL OR end_date >= %s)
    """, (promo_code, today, today))
    
    promotion = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not promotion:
        return {
            "valid": False,
            "message": "ລະຫັດສ່ວນຫຼຸດບໍ່ຖືກຕ້ອງ ຫຼື ໝົດອາຍຸແລ້ວ"
        }
    
    # Check min quantity
    if quantity < promotion['min_qty']:
        return {
            "valid": False,
            "message": f"ຕ້ອງຊື້ຢ່າງໜ້ອຍ {promotion['min_qty']} ລາຍການ"
        }
    
    # Check min amount
    if total_amount < promotion['min_amount']:
        return {
            "valid": False,
            "message": f"ຕ້ອງຊື້ຢ່າງໜ້ອຍ {int(promotion['min_amount']):,} KIP"
        }
    
    # Calculate discount
    discount_amount = 0
    if promotion['discount_type'] == 'percent':
        discount_amount = total_amount * (promotion['value'] / 100)
    else:  # amount
        discount_amount = promotion['value']
    
    # Ensure discount doesn't exceed total
    discount_amount = min(discount_amount, total_amount)
    
    return {
        "valid": True,
        "discount_amount": discount_amount,
        "discount_type": promotion['discount_type'],
        "discount_value": promotion['value'],
        "final_amount": total_amount - discount_amount,
        "message": f"ສ່ວນຫຼຸດ {int(discount_amount):,} KIP"
    }