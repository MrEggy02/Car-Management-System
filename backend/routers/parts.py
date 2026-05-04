from fastapi import APIRouter, HTTPException, Depends, Form
from typing import Optional
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/parts")
def get_parts(user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, s.name as supplier_name 
        FROM Parts p
        LEFT JOIN Suppliers s ON p.supplier_id = s.id
        ORDER BY p.id DESC
    """)
    parts = cursor.fetchall()
    cursor.close()
    db.close()
    return parts

@router.post("/parts")
def add_part(
    part_code: str = Form(...),
    name: str = Form(...),
    brand: str = Form(""),
    cost_price: float = Form(0),
    sell_price: float = Form(0),
    stock_qty: int = Form(0),
    min_stock: int = Form(5),
    unit: str = Form("ชิ้น"),
    supplier_id: Optional[int] = Form(None),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO Parts (part_code, name, brand, cost_price, sell_price, stock_qty, min_stock, unit, supplier_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (part_code, name, brand, cost_price, sell_price, stock_qty, min_stock, unit, supplier_id))
    db.commit()
    part_id = cursor.lastrowid
    cursor.close()
    db.close()
    return {"message": "เพิ่มอะไหล่สำเร็จ", "id": part_id}

@router.put("/parts/{part_id}")
def update_part(
    part_id: int,
    part_code: str = Form(...),
    name: str = Form(...),
    brand: str = Form(""),
    cost_price: float = Form(0),
    sell_price: float = Form(0),
    stock_qty: int = Form(0),
    min_stock: int = Form(5),
    unit: str = Form("ชิ้น"),
    supplier_id: Optional[int] = Form(None),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE Parts SET 
            part_code=%s, 
            name=%s, 
            brand=%s, 
            cost_price=%s, 
            sell_price=%s, 
            stock_qty=%s, 
            min_stock=%s, 
            unit=%s, 
            supplier_id=%s
        WHERE id=%s
    """, (part_code, name, brand, cost_price, sell_price, stock_qty, min_stock, unit, supplier_id, part_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "แก้ไขอะไหล่สำเร็จ"}

@router.delete("/parts/{part_id}")
def delete_part(part_id: int, user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Parts WHERE id=%s", (part_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ลบอะไหล่สำเร็จ"}