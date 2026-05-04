from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/suppliers")
def get_suppliers(user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM suppliers ORDER BY id DESC")
    suppliers = cursor.fetchall()
    cursor.close()
    db.close()
    return suppliers

@router.post("/suppliers")
def add_supplier(
    name: str = Form(...),
    contact_person: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    address: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO suppliers (name, contact_person, phone, email, address)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, contact_person, phone, email, address))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "เพิ่มผู้สะໜອງสำเร็จ", "id": cursor.lastrowid}

@router.put("/suppliers/{supplier_id}")
def update_supplier(
    supplier_id: int,
    name: str = Form(...),
    contact_person: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    address: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE suppliers SET 
            name=%s, contact_person=%s, phone=%s, email=%s, address=%s
        WHERE id=%s
    """, (name, contact_person, phone, email, address, supplier_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "แก้ไขผู้สะໜອງสำเร็จ"}

@router.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM suppliers WHERE id=%s", (supplier_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ลบผู้สะໜອງสำเร็จ"}