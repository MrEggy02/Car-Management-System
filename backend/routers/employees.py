from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user, hash_password, verify_password

router = APIRouter()

@router.get("/employees")
def get_employees(user: dict = Depends(authenticate_user)):
    """ดึงข้อมูลพนักงานทั้งหมด"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, name, phone, role, status, can_login, username, created_at 
        FROM Employees 
        ORDER BY id DESC
    """)
    employees = cursor.fetchall()
    # ไม่แสดงรหัสผ่าน
    for emp in employees:
        emp.pop('password', None)
    cursor.close()
    db.close()
    return employees

@router.post("/employees")
def add_employee(
    name: str = Form(...),
    phone: str = Form(""),
    role: str = Form(...),
    status: str = Form("active"),
    can_login: bool = Form(False),
    username: str = Form(None),
    password: str = Form(None),
    user: dict = Depends(authenticate_user)
):
    """เพิ่มพนักงานใหม่ (Admin เท่านั้น)"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can add employees")
    
    db = get_db()
    cursor = db.cursor()
    try:
        # ถ้าสามารถ login ได้ ต้องมี username และ password
        hashed_password = None
        final_username = None
        
        if can_login:
            if not username or not password:
                raise HTTPException(status_code=400, detail="Username and password required for login access")
            # ตรวจสอบ username ซ้ำ
            cursor.execute("SELECT id FROM Employees WHERE username = %s", (username,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username already exists")
            final_username = username
            hashed_password = hash_password(password)
        
        cursor.execute(
            """INSERT INTO Employees (name, phone, role, status, can_login, username, password) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (name, phone, role, status, can_login, final_username, hashed_password)
        )
        db.commit()
        return {"message": "เพิ่มพนักงานสำเร็จ", "id": cursor.lastrowid}
    except HTTPException:
        raise
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
    can_login: bool = Form(False),
    username: str = Form(None),
    password: str = Form(None),
    user: dict = Depends(authenticate_user)
):
    """อัปเดตข้อมูลพนักงาน"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can update employees")
    
    db = get_db()
    cursor = db.cursor()
    try:
        # สร้าง query แบบ dynamic
        update_fields = []
        params = []
        
        update_fields.append("name = %s")
        params.append(name)
        update_fields.append("phone = %s")
        params.append(phone)
        update_fields.append("role = %s")
        params.append(role)
        update_fields.append("status = %s")
        params.append(status)
        update_fields.append("can_login = %s")
        params.append(can_login)
        
        if can_login and username:
            # ตรวจสอบ username ซ้ำ (ยกเว้นตัวเอง)
            cursor.execute("SELECT id FROM Employees WHERE username = %s AND id != %s", (username, employee_id))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username already exists")
            update_fields.append("username = %s")
            params.append(username)
        elif not can_login:
            # ถ้าไม่ให้ login ให้ล้าง username
            update_fields.append("username = %s")
            params.append(None)
        
        if can_login and password:
            # ถ้ามีการเปลี่ยนรหัสผ่าน
            update_fields.append("password = %s")
            params.append(hash_password(password))
        
        params.append(employee_id)
        
        query = f"UPDATE Employees SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, params)
        db.commit()
        return {"message": "อัปเดตพนักงานสำเร็จ"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating employee: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, user: dict = Depends(authenticate_user)):
    """ลบพนักงาน (Admin เท่านั้น)"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can delete employees")
    
    db = get_db()
    cursor = db.cursor()
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

@router.post("/employees/change-password")
def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """เปลี่ยนรหัสผ่านของตัวเอง"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # ตรวจสอบรหัสผ่านปัจจุบัน
    cursor.execute("SELECT password FROM Employees WHERE id = %s", (user['id'],))
    emp = cursor.fetchone()
    
    if not verify_password(current_password, emp['password']):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # อัปเดตรหัสผ่านใหม่
    hashed_new = hash_password(new_password)
    cursor.execute("UPDATE Employees SET password = %s WHERE id = %s", (hashed_new, user['id']))
    db.commit()
    cursor.close()
    db.close()
    
    return {"message": "Password changed successfully"}