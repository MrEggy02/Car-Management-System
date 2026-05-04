from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth import security
from routers import (
    employees, shop, suppliers, services, parts, promotions, customers, cars, vehicles , job_orders , quotations , repair_orders
)

app = FastAPI(title="J&P Auto Maxing API", version="2.0")

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

# Auth endpoints
@app.post("/login")
def login(user: dict = Depends(security)):
    return {"status": "success", "user": user}

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
    cursor.execute("SELECT id, username, password, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return {"users": users}