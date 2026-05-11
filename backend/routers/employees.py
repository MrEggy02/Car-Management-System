from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/employees")
def get_employees(user: dict = Depends(authenticate_user)):
    """ดึงข้อมูลพนักงานทั้งหมด"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, name, phone, role, status, created_at 
        FROM Employees 
        ORDER BY id DESC
    """)
    employees = cursor.fetchall()
    cursor.close()
    db.close()
    return employees

@router.post("/employees")
def add_employee(
    name: str = Form(...),
    phone: str = Form(""),
    role: str = Form(...),
    status: str = Form("active"),
    user: dict = Depends(authenticate_user)
):
    """เพิ่มพนักงานใหม่ (Admin เท่านั้น)"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can add employees")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Employees (name, phone, role, status) VALUES (%s, %s, %s, %s)",
            (name, phone, role, status)
        )
        db.commit()
        return {"message": "เพิ่มพนักงานสำเร็จ", "id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding employee: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.put("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    name: str = Form(...),
    phone: str = Form(""),
    role: str = Form(...),
    status: str = Form("active"),
    user: dict = Depends(authenticate_user)
):
    """อัปเดตข้อมูลพนักงาน"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can update employees")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE Employees SET name=%s, phone=%s, role=%s, status=%s WHERE id=%s
    """, (name, phone, role, status, employee_id))
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
    # Allow deleting any employee (no special admin protection since status field exists)
    cursor.execute("DELETE FROM Employees WHERE id = %s", (employee_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ลบพนักงานสำเร็จ"}

@router.get("/employees/mechanics")
def get_mechanics(user: dict = Depends(authenticate_user)):
    """ดึงข้อมูลช่างซ่อมทั้งหมด (role = mechanic)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, name, phone, role, status 
        FROM Employees 
        WHERE role = 'mechanic' AND status = 'active'
        ORDER BY name
    """)
    mechanics = cursor.fetchall()
    cursor.close()
    db.close()
    return mechanics