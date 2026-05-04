from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from fastapi.responses import Response
from database import get_db
from auth import authenticate_user
from utils import save_uploaded_file, delete_file
import os

router = APIRouter()

@router.get("/shop")
def get_shop_info(user: dict = Depends(authenticate_user)):
    """ดึงข้อมูลร้าน"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shop_info LIMIT 1")
    shop = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not shop:
        return {
            "id": 1,
            "shop_name": "J&P Auto Maxing",
            "address": "",
            "phone": "",
            "email": "",
            "tax_id": "",
            "logo_path": None
        }
    return shop

@router.put("/shop")
def update_shop_info(
    shop_name: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...),
    email: str = Form(""),
    tax_id: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """อัปเดตข้อมูลร้าน (Admin เท่านั้น)"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can edit shop info")
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM shop_info WHERE id = 1")
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute("""
            UPDATE shop_info SET 
                shop_name=%s, address=%s, phone=%s, email=%s, tax_id=%s 
            WHERE id=1
        """, (shop_name, address, phone, email, tax_id))
    else:
        cursor.execute("""
            INSERT INTO shop_info (id, shop_name, address, phone, email, tax_id) 
            VALUES (1, %s, %s, %s, %s, %s)
        """, (shop_name, address, phone, email, tax_id))
    
    db.commit()
    cursor.close()
    db.close()
    return {"message": "อัปเดตข้อมูลร้านสำเร็จ"}

@router.post("/shop/logo")
async def upload_shop_logo(
    logo: UploadFile = File(...),
    user: dict = Depends(authenticate_user)
):
    """อัปโหลดโลโก้ร้าน (Admin เท่านั้น)"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can upload logo")
    
    try:
        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp']
        file_extension = logo.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"ไฟล์ต้องเป็น {', '.join(allowed_extensions)}")
        
        filename = f"shop_logo.{file_extension}"
        file_path = save_uploaded_file(logo.file, filename)
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT id FROM shop_info WHERE id = 1")
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("UPDATE shop_info SET logo_path = %s WHERE id = 1", (file_path,))
        else:
            cursor.execute("INSERT INTO shop_info (id, logo_path) VALUES (1, %s)", (file_path,))
        
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "อัปโหลดโลโก้สำเร็จ", "logo_path": file_path, "filename": filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shop/logo")
def get_shop_logo(user: dict = Depends(authenticate_user)):
    """ดาวน์โหลดโลโก้ร้าน"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT logo_path FROM shop_info WHERE id = 1")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        
        if result and result.get('logo_path') and os.path.exists(result['logo_path']):
            with open(result['logo_path'], "rb") as f:
                return Response(content=f.read(), media_type="image/png")
        else:
            raise HTTPException(status_code=404, detail="Logo not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/shop/logo")
def delete_shop_logo(user: dict = Depends(authenticate_user)):
    """ลบโลโก้ร้าน (Admin เท่านั้น)"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can delete logo")
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT logo_path FROM shop_info WHERE id = 1")
        result = cursor.fetchone()
        
        if result and result.get('logo_path'):
            delete_file(result['logo_path'])
        
        cursor.execute("UPDATE shop_info SET logo_path = NULL WHERE id = 1")
        db.commit()
        cursor.close()
        db.close()
        
        return {"message": "ลบโลโก้สำเร็จ"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))