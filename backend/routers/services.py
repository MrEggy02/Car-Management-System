from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/services")
def get_services(user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM services ORDER BY id DESC")
    services = cursor.fetchall()
    cursor.close()
    db.close()
    return services

@router.post("/services")
def add_service(
    service_name: str = Form(...),
    description: str = Form(""),
    price: float = Form(0),
    estimated_hours: int = Form(1),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO services (service_name, description, price, estimated_hours)
        VALUES (%s, %s, %s, %s)
    """, (service_name, description, price, estimated_hours))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "เพิ่มบริการสำเร็จ", "id": cursor.lastrowid}

@router.put("/services/{service_id}")
def update_service(
    service_id: int,
    service_name: str = Form(...),
    description: str = Form(""),
    price: float = Form(0),
    estimated_hours: int = Form(1),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE services SET 
            service_name=%s, description=%s, price=%s, estimated_hours=%s
        WHERE id=%s
    """, (service_name, description, price, estimated_hours, service_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "แก้ไขบริการสำเร็จ"}

@router.delete("/services/{service_id}")
def delete_service(service_id: int, user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM services WHERE id=%s", (service_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ลบบริการสำเร็จ"}