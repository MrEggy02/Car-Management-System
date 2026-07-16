from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/services")
def get_services(user: dict = Depends(authenticate_user)):
    """ດຶງຂໍ້ມູນບໍລິການທັງໝົດ"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name, price, description FROM Services ORDER BY id DESC")
    services = cursor.fetchall()
    cursor.close()
    db.close()
    return services

@router.post("/services")
def add_service(
    name: str = Form(...),
    price: float = Form(0),
    description: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """ເພີ່ມບໍລິການໃໝ່"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO Services (name, price, description)
        VALUES (%s, %s, %s)
    """, (name, price, description))
    db.commit()
    service_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"message": "ເພີ່ມບໍລິການສຳເລັດ", "id": service_id}

@router.put("/services/{service_id}")
def update_service(
    service_id: int,
    name: str = Form(...),
    price: float = Form(0),
    description: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """ອັບເດດຂໍ້ມູນບໍລິການ"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE Services SET 
            name=%s, price=%s, description=%s
        WHERE id=%s
    """, (name, price, description, service_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ແກ້ໄຂບໍລິການສຳເລັດ"}

@router.delete("/services/{service_id}")
def delete_service(service_id: int, user: dict = Depends(authenticate_user)):
    """ລຶບບໍລິການ"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Services WHERE id=%s", (service_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ລຶບບໍລິການສຳເລັດ"}