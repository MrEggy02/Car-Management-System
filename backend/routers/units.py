# backend/routers/units.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional

router = APIRouter()

@router.get("/units")
def get_units(user: dict = Depends(authenticate_user)):
    """Get all units"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, name, status 
            FROM Units 
            ORDER BY name
        """)
        units = cursor.fetchall()
        return units
    except Exception as e:
        print(f"Error getting units: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.post("/units")
def add_unit(
    name: str = Form(...),
    status: str = Form("active"),
    user: dict = Depends(authenticate_user)
):
    """Add new unit"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can add units")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM Units WHERE name = %s", (name,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Unit already exists")
        
        cursor.execute("INSERT INTO Units (name, status) VALUES (%s, %s)", (name, status))
        db.commit()
        return {"message": "Unit added successfully", "id": cursor.lastrowid}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/units/{unit_id}")
def update_unit(
    unit_id: int,
    name: str = Form(...),
    status: str = Form(...),
    user: dict = Depends(authenticate_user)
):
    """Update unit"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can update units")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM Units WHERE id = %s", (unit_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Unit not found")
        
        cursor.execute("SELECT id FROM Units WHERE name = %s AND id != %s", (name, unit_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Unit name already exists")
        
        cursor.execute("UPDATE Units SET name = %s, status = %s WHERE id = %s", (name, status, unit_id))
        db.commit()
        return {"message": "Unit updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/units/{unit_id}")
def delete_unit(unit_id: int, user: dict = Depends(authenticate_user)):
    """Delete unit"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can delete units")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM Units WHERE id = %s", (unit_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Unit not found")
        
        cursor.execute("SELECT id FROM Parts WHERE unit_id = %s LIMIT 1", (unit_id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Cannot delete unit because it is used in parts")
        
        cursor.execute("DELETE FROM Units WHERE id = %s", (unit_id,))
        db.commit()
        return {"message": "Unit deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/units/active")
def get_active_units(user: dict = Depends(authenticate_user)):
    """Get active units only"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name FROM Units WHERE status = 'active' ORDER BY name")
        units = cursor.fetchall()
        return units
    except Exception as e:
        print(f"Error getting active units: {e}")
        return []
    finally:
        cursor.close()
        db.close()