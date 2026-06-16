# backend/routers/customers.py
from fastapi import APIRouter, HTTPException, Depends, Form
from database import get_db
from auth import authenticate_user
from typing import Optional

router = APIRouter()


@router.get("/customers")
def get_customers(user: dict = Depends(authenticate_user)):
    """Get all customers"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, phone, address, created_at FROM customers ORDER BY id DESC")
        customers = cursor.fetchall()
        return customers
    except Exception as e:
        print(f"Error in get_customers: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/customers-with-vehicles")
def get_customers_with_vehicles(user: dict = Depends(authenticate_user)):
    """Get all customers with vehicle count in one query (FASTER)"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                c.id,
                c.name,
                c.phone,
                c.address,
                c.created_at,
                COUNT(v.id) as vehicle_count
            FROM customers c
            LEFT JOIN vehicles v ON c.id = v.customer_id
            GROUP BY c.id
            ORDER BY c.id DESC
        """)
        customers = cursor.fetchall()
        for customer in customers:
            if customer.get('created_at'):
                customer['created_at'] = str(customer['created_at'])
        return customers
    except Exception as e:
        print(f"Error in get_customers_with_vehicles: {e}")
        return []
    finally:
        cursor.close()
        db.close()


@router.get("/customers/{customer_id}")
def get_customer(customer_id: int, user: dict = Depends(authenticate_user)):
    """Get a single customer by ID"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, phone, address, created_at FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            return None
        return customer
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        cursor.close()
        db.close()


@router.post("/customers")
def add_customer(
    name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """Add a new customer"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO customers (name, phone, address) VALUES (%s, %s, %s)",
            (name, phone, address)
        )
        db.commit()
        customer_id = cursor.lastrowid
        return {"id": customer_id, "message": "Customer added successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error adding customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.put("/customers/{customer_id}")
def update_customer(
    customer_id: int,
    name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """Update customer"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            UPDATE customers SET name=%s, phone=%s, address=%s
            WHERE id=%s
        """, (name, phone, address, customer_id))
        db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {"message": "Customer updated successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error updating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, user: dict = Depends(authenticate_user)):
    """Delete customer"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
        db.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {"message": "Customer deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()


@router.post("/register_customer")
def register_customer(
    name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(""),
    plate_number: str = Form(...),
    brand_id: int = Form(None),
    model: str = Form(""),
    year: int = Form(0),
    color: str = Form(""),
    user: dict = Depends(authenticate_user)
):
    """Register customer and vehicle together with brand_id"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO customers (name, phone, address)
            VALUES (%s, %s, %s)
        """, (name, phone, address))
        
        customer_id = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO vehicles (customer_id, plate_number, brand_id, model, year, color)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (customer_id, plate_number, brand_id, model, year, color))
        
        vehicle_id = cursor.lastrowid
        db.commit()
        
        return {
            "message": "Registration successful",
            "customer_id": customer_id,
            "vehicle_id": vehicle_id,
            "customer_name": name,
            "plate_number": plate_number
        }
    except Exception as e:
        db.rollback()
        print(f"Error in register_customer: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()