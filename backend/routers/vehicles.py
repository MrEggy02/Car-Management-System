# routers/vehicles.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional

router = APIRouter()

# ========== Vehicle Endpoints ==========

@router.get("/vehicles")
def get_vehicles(customer_id: Optional[int] = None, user: dict = Depends(authenticate_user)):
    """Get all vehicles or filter by customer_id"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if customer_id:
            cursor.execute(
                "SELECT id, customer_id, plate_number, brand, model, year, color FROM vehicles WHERE customer_id = %s ORDER BY id DESC",
                (customer_id,)
            )
        else:
            cursor.execute("SELECT id, customer_id, plate_number, brand, model, year, color FROM vehicles ORDER BY id DESC")
        
        vehicles = cursor.fetchall()
        return vehicles
    except Exception as e:
        print(f"Error in get_vehicles: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/vehicles/{vehicle_id}")
def get_vehicle(vehicle_id: int, user: dict = Depends(authenticate_user)):
    """Get a single vehicle by ID"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, customer_id, plate_number, brand, model, year, color FROM vehicles WHERE id = %s",
            (vehicle_id,)
        )
        vehicle = cursor.fetchone()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return vehicle
    finally:
        cursor.close()
        db.close()


@router.post("/vehicles")
def add_vehicle(
    customer_id: int = Form(...),
    plate_number: str = Form(...),
    brand: str = Form(""),
    model: str = Form(""),
    year: int = Form(0),
    color: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """Add a new vehicle for a customer"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if customer exists
        cursor.execute("SELECT id FROM customers WHERE id = %s", (customer_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Insert vehicle
        cursor.execute("""
            INSERT INTO vehicles (customer_id, plate_number, brand, model, year, color)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer_id, plate_number, brand, model, year, color))
        
        db.commit()
        vehicle_id = cursor.lastrowid
        
        return {
            "id": vehicle_id,
            "customer_id": customer_id,
            "plate_number": plate_number,
            "message": "Vehicle added successfully"
        }
    except Exception as e:
        db.rollback()
        print(f"Error adding vehicle: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: int,
    plate_number: str = Form(...),
    brand: str = Form(""),
    model: str = Form(""),
    year: int = Form(0),
    color: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """Update a vehicle"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE vehicles SET 
                plate_number=%s, brand=%s, model=%s, year=%s, color=%s
            WHERE id=%s
        """, (plate_number, brand, model, year, color, vehicle_id))
        db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        return {"message": "Vehicle updated successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error updating vehicle: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int, user: dict = Depends(authenticate_user)):
    """Delete a vehicle"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM vehicles WHERE id = %s", (vehicle_id,))
        db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        return {"message": "Vehicle deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting vehicle: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()