# routers/brands.py
from fastapi import APIRouter, Depends
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/brands")
def get_brands(user: dict = Depends(authenticate_user)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM brands WHERE status = 'active' ORDER BY name")
    brands = cursor.fetchall()
    cursor.close()
    db.close()
    return brands