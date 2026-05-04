from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/promotions")
def get_promotions(user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM promotions ORDER BY id DESC")
    promotions = cursor.fetchall()
    cursor.close()
    db.close()
    return promotions

@router.post("/promotions")
def add_promotion(
    promo_code: str = Form(...),
    promo_name: str = Form(...),
    discount_type: str = Form("percentage"),
    discount_value: float = Form(0),
    start_date: str = Form(...),
    end_date: str = Form(...),
    is_active: bool = Form(True),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO promotions (promo_code, promo_name, discount_type, discount_value, start_date, end_date, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (promo_code, promo_name, discount_type, discount_value, start_date, end_date, is_active))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "เพิ่มโปรโมชันสำเร็จ", "id": cursor.lastrowid}

@router.delete("/promotions/{promo_id}")
def delete_promotion(promo_id: int, user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM promotions WHERE id=%s", (promo_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ลบโปรโมชันสำเร็จ"}