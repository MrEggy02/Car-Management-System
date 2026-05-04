from fastapi import APIRouter, HTTPException, Depends, Form
from typing import Optional
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/cars")
def get_cars(customer_id: Optional[int] = None, user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if customer_id:
        cursor.execute("SELECT * FROM cars WHERE customer_id = %s ORDER BY id DESC", (customer_id,))
    else:
        cursor.execute("""
            SELECT c.*, cust.name as customer_name 
            FROM cars c 
            JOIN customers cust ON c.customer_id = cust.id 
            ORDER BY c.id DESC
        """)
    
    cars = cursor.fetchall()
    cursor.close()
    db.close()
    return cars

@router.get("/cars/{car_id}")
def get_car(car_id: int, user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
    car = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@router.post("/add_car")
def add_car_only(
    customer_id: int = Form(...),
    license_plate: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(0),
    color: str = Form(""),
    engine_no: str = Form(""),
    chassis_no: str = Form(""),
    notes: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO cars (customer_id, license_plate, brand, model, year, color, engine_no, chassis_no, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (customer_id, license_plate, brand, model, year, color, engine_no, chassis_no, notes))
    db.commit()
    car_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"message": "เพิ่มรถสำเร็จ", "car_id": car_id}

@router.put("/cars/{car_id}")
def update_car_full(
    car_id: int,
    customer_id: int = Form(...),
    license_plate: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(0),
    color: str = Form(""),
    engine_no: str = Form(""),
    chassis_no: str = Form(""),
    notes: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE cars SET 
            customer_id=%s, license_plate=%s, brand=%s, model=%s, year=%s, 
            color=%s, engine_no=%s, chassis_no=%s, notes=%s
        WHERE id=%s
    """, (customer_id, license_plate, brand, model, year, color, engine_no, chassis_no, notes, car_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "แก้ไขรถสำเร็จ"}

@router.put("/update_car/{car_id}")
def update_car_info(
    car_id: int,
    license_plate: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(0),
    color: str = Form(""),
    engine_no: str = Form(""),
    chassis_no: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE cars SET 
            license_plate=%s, brand=%s, model=%s, year=%s, color=%s, engine_no=%s, chassis_no=%s
        WHERE id=%s
    """, (license_plate, brand, model, year, color, engine_no, chassis_no, car_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "แก้ไขข้อมูลรถสำเร็จ"}

@router.delete("/cars/{car_id}")
def delete_car(car_id: int, user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM cars WHERE id=%s", (car_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ลบรถสำเร็จ"}