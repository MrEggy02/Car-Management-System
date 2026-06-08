# backend/routers/brands.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional

router = APIRouter()

@router.get("/brands")
def get_brands(
    user: dict = Depends(authenticate_user)
):
    """Get all brands"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, name, status 
            FROM Brands 
            ORDER BY name
        """)
        brands = cursor.fetchall()
        return brands
    except Exception as e:
        print(f"Error getting brands: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.post("/brands")
def add_brand(
    name: str = Form(...),
    status: str = Form("active"),
    user: dict = Depends(authenticate_user)
):
    """Add new brand"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can add brands")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM Brands WHERE name = %s", (name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Brand already exists")
        
        cursor.execute("INSERT INTO Brands (name, status) VALUES (%s, %s)", (name, status))
        db.commit()
        return {"message": "Brand added successfully", "id": cursor.lastrowid}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/brands/{brand_id}")
def update_brand(
    brand_id: int,
    name: str = Form(...),
    status: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Update brand"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can update brands")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM Brands WHERE id = %s", (brand_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Brand not found")
        
        cursor.execute("SELECT id FROM Brands WHERE name = %s AND id != %s", (name, brand_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Brand name already exists")
        
        cursor.execute("UPDATE Brands SET name = %s, status = %s WHERE id = %s", (name, status, brand_id))
        db.commit()
        return {"message": "Brand updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/brands/{brand_id}")
def delete_brand(
    brand_id: int,
    user: dict = Depends(authenticate_user)
):
    """Delete brand"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can delete brands")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM Brands WHERE id = %s", (brand_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Brand not found")
        
        cursor.execute("SELECT id FROM Vehicles WHERE brand_id = %s LIMIT 1", (brand_id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Cannot delete brand because it is used in vehicles")
        
        cursor.execute("DELETE FROM Brands WHERE id = %s", (brand_id,))
        db.commit()
        return {"message": "Brand deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/brands/active")
def get_active_brands(user: dict = Depends(authenticate_user)):
    """Get only active brands"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name FROM Brands WHERE status = 'active' ORDER BY name")
        brands = cursor.fetchall()
        return brands
    except Exception as e:
        print(f"Error getting active brands: {e}")
        return []
    finally:
        cursor.close()
        db.close()