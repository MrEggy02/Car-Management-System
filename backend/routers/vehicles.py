# routers/vehicles.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional

router = APIRouter()

@router.get("/vehicles")
def get_vehicles(customer_id: Optional[int] = None, user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if customer_id:
            cursor.execute("""
                SELECT v.*, b.name as brand_name 
                FROM vehicles v
                LEFT JOIN brands b ON v.brand_id = b.id
                WHERE v.customer_id = %s 
                ORDER BY v.id DESC
            """, (customer_id,))
        else:
            cursor.execute("""
                SELECT v.*, b.name as brand_name 
                FROM vehicles v
                LEFT JOIN brands b ON v.brand_id = b.id
                ORDER BY v.id DESC
            """)
        vehicles = cursor.fetchall()
        
        # Convert None brand_id to empty string for frontend
        for vehicle in vehicles:
            if vehicle.get('brand_id') is None:
                vehicle['brand_id'] = 0
            if vehicle.get('brand_name') is None:
                vehicle['brand_name'] = ""
        
        return vehicles
    except Exception as e:
        print(f"Error in get_vehicles: {e}")
        import traceback
        traceback.print_exc()
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
        cursor.execute("""
            SELECT v.*, b.name as brand_name 
            FROM vehicles v
            LEFT JOIN brands b ON v.brand_id = b.id
            WHERE v.id = %s
        """, (vehicle_id,))
        
        vehicle = cursor.fetchone()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        if vehicle.get('brand_id') is None:
            vehicle['brand_id'] = 0
        if vehicle.get('brand_name') is None:
            vehicle['brand_name'] = ""
        
        return vehicle
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_vehicle: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.post("/vehicles")
def add_vehicle(
    customer_id: int = Form(...),
    plate_number: str = Form(...),
    brand_id: Optional[int] = Form(None),
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
        
        # If brand_id is 0 or None, set to None
        if brand_id == 0:
            brand_id = None
        
        # Check if brand exists if provided
        if brand_id:
            cursor.execute("SELECT id FROM brands WHERE id = %s", (brand_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Brand not found")
        
        cursor.execute("""
            INSERT INTO vehicles (customer_id, plate_number, brand_id, model, year, color)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer_id, plate_number, brand_id, model, year, color))
        
        db.commit()
        vehicle_id = cursor.lastrowid
        
        return {
            "id": vehicle_id, 
            "customer_id": customer_id,
            "plate_number": plate_number,
            "message": "Vehicle added successfully"
        }
    except HTTPException:
        raise
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
    brand_id: Optional[int] = Form(None),
    model: str = Form(""),
    year: int = Form(0),
    color: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """Update a vehicle"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Check if vehicle exists
        cursor.execute("SELECT id FROM vehicles WHERE id = %s", (vehicle_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        # If brand_id is 0 or None, set to None
        if brand_id == 0:
            brand_id = None
        
        # Check if brand exists if provided
        if brand_id:
            cursor.execute("SELECT id FROM brands WHERE id = %s", (brand_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Brand not found")
        
        cursor.execute("""
            UPDATE vehicles SET 
                plate_number = %s, 
                brand_id = %s, 
                model = %s, 
                year = %s, 
                color = %s
            WHERE id = %s
        """, (plate_number, brand_id, model, year, color, vehicle_id))
        
        db.commit()
        return {"message": "Vehicle updated successfully"}
    except HTTPException:
        raise
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
        cursor.execute("SELECT id FROM vehicles WHERE id = %s", (vehicle_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        cursor.execute("DELETE FROM vehicles WHERE id = %s", (vehicle_id,))
        db.commit()
        return {"message": "Vehicle deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting vehicle: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.get("/vehicles/customer/{customer_id}/count")
def count_vehicles_by_customer(customer_id: int, user: dict = Depends(authenticate_user)):
    """Get number of vehicles for a customer"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COUNT(*) as count FROM vehicles WHERE customer_id = %s", (customer_id,))
        result = cursor.fetchone()
        count = result[0] if result else 0
        return {"count": count}
    except Exception as e:
        print(f"Error counting vehicles: {e}")
        return {"count": 0}
    finally:
        cursor.close()
        db.close()