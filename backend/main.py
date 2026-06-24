from fastapi import FastAPI, Depends, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
import os
from auth import security, authenticate_user
from routers import (
    employees,
    shop,
    suppliers, 
    services,
    parts, 
    promotions,
    customers, 
    cars,
    vehicles ,
    job_orders , 
    quotations ,
    repair_orders , 
    invoices , 
    purchase_orders ,
    promotion_items,
    reports,
    brands,
    units, 
    part_categories,
)

app = FastAPI(title="J&P Auto Maxing API", version="2.0")

# Mount uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(employees.router)
app.include_router(shop.router)
app.include_router(suppliers.router)
app.include_router(services.router)
app.include_router(parts.router)
app.include_router(promotions.router)
app.include_router(customers.router)
app.include_router(cars.router)
app.include_router(vehicles.router)
app.include_router(job_orders.router)
app.include_router(quotations.router)
app.include_router(repair_orders.router)
app.include_router(invoices.router)
app.include_router(purchase_orders.router)
app.include_router(promotion_items.router)
app.include_router(reports.router)
app.include_router(brands.router)
app.include_router(units.router)
app.include_router(part_categories.router)

# ✅ FIXED: Auth endpoints
@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """Login endpoint - returns user data with id, role, fullname"""
    credentials = HTTPBasicCredentials(username=username, password=password)
    
    try:
        user = authenticate_user(credentials)
        # ✅ Return user data directly with id, role, fullname
        return {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "fullname": user["fullname"]
        }
    except HTTPException as e:
        raise e

@app.get("/")
def home():
    return {
        "message": "J&P Auto Maxing API is working!",
        "version": "2.0",
        "processes": ["Process 1: Data Management", "Process 2: Registration"]
    }

@app.get("/debug/users")
def debug_users():
    from database import get_db
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, password, role FROM employees WHERE can_login = TRUE")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return {"users": users}