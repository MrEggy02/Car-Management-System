from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/employees")
def get_employees(user: dict = Depends(authenticate_user)):
    """ดึงข้อมูลพนักงานทั้งหมด"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, fullname, role, phone, created_at FROM users ORDER BY id DESC")
    employees = cursor.fetchall()
    cursor.close()
    db.close()
    return employees

@router.post("/employees")
def add_employee(
    username: str = Form(...),
    password: str = Form(...),
    fullname: str = Form(...),
    role: str = Form(...),
    phone: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """เพิ่มพนักงานใหม่ (Admin เท่านั้น)"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can add employees")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, fullname, role, phone) VALUES (%s, %s, %s, %s, %s)",
            (username, password, fullname, role, phone)
        )
        db.commit()
        return {"message": "เพิ่มพนักงานสำเร็จ", "id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        cursor.close()
        db.close()

@router.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    fullname: str = Form(...),
    phone: str = Form(""),
    role: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """อัปเดตข้อมูลพนักงาน"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can update employees")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE users SET fullname=%s, phone=%s, role=%s WHERE id=%s
    """, (fullname, phone, role, employee_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "อัปเดตพนักงานสำเร็จ"}

@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, user: dict = Depends(authenticate_user)):
    """ลบพนักงาน (Admin เท่านั้น)"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can delete employees")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s AND role != 'admin'", (employee_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ลบพนักงานสำเร็จ"}