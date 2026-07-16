from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/shop")
def get_shop_info(user: dict = Depends(authenticate_user)):
    """ດຶງຂໍ້ມູນຮ້ານ"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name, address, phone FROM Shop LIMIT 1")
    shop = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not shop:
        return {
            "id": 1,
            "name": "J&P Auto Maxing",
            "address": "",
            "phone": ""
        }
    return shop

@router.put("/shop")
def update_shop_info(
    name: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """ອັບເດດຂໍ້ມູນຮ້ານ (Admin ເທົ່ານັ້ນ)"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can edit shop info")
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM Shop WHERE id = 1")
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute("""
            UPDATE Shop SET name=%s, address=%s, phone=%s WHERE id=1
        """, (name, address, phone))
    else:
        cursor.execute("""
            INSERT INTO Shop (id, name, address, phone) VALUES (1, %s, %s, %s)
        """, (name, address, phone))
    
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ອັບເດດຂໍ້ມູນຮ້ານສຳເລັດ"}