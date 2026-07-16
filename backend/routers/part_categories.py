# backend/routers/part_categories.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional

router = APIRouter()

@router.get("/part-categories")
def get_part_categories(user: dict = Depends(authenticate_user)):
    """Get all part categories"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, name, status 
            FROM Part_Categories 
            ORDER BY name
        """)
        categories = cursor.fetchall()
        return categories
    except Exception as e:
        print(f"Error getting part categories: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.post("/part-categories")
def add_part_category(
    name: str = Form(...),
    status: str = Form("active"),
    user: dict = Depends(authenticate_user)
):
    """Add new part category"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can add part categories")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM Part_Categories WHERE name = %s", (name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Category already exists")
        
        cursor.execute("INSERT INTO Part_Categories (name, status) VALUES (%s, %s)", (name, status))
        db.commit()
        return {"message": "Category added successfully", "id": cursor.lastrowid}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/part-categories/{category_id}")
def update_part_category(
    category_id: int,
    name: str = Form(...),
    status: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Update part category"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can update part categories")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM Part_Categories WHERE id = %s", (category_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Category not found")
        
        cursor.execute("SELECT id FROM Part_Categories WHERE name = %s AND id != %s", (name, category_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Category name already exists")
        
        cursor.execute("UPDATE Part_Categories SET name = %s, status = %s WHERE id = %s", (name, status, category_id))
        db.commit()
        return {"message": "Category updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/part-categories/{category_id}")
def delete_part_category(category_id: int, user: dict = Depends(authenticate_user)):
    """Delete part category"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can delete part categories")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM Part_Categories WHERE id = %s", (category_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Category not found")
        
        cursor.execute("SELECT id FROM Parts WHERE category_id = %s LIMIT 1", (category_id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Cannot delete category because it is used in parts")
        
        cursor.execute("DELETE FROM Part_Categories WHERE id = %s", (category_id,))
        db.commit()
        return {"message": "Category deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/part-categories/active")
def get_active_part_categories(user: dict = Depends(authenticate_user)):
    """Get active part categories only"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name FROM Part_Categories WHERE status = 'active' ORDER BY name")
        categories = cursor.fetchall()
        return categories
    except Exception as e:
        print(f"Error getting active categories: {e}")
        return []
    finally:
        cursor.close()
        db.close()