from fastapi import APIRouter, HTTPException, Depends, Form
from typing import Optional
from database import get_db
from auth import authenticate_user

router = APIRouter()

@router.get("/parts")
def get_parts(user: dict = Depends(authenticate_user)):
    """ດຶງຂໍ້ມູນອາໄຫຼ່ທັງໝົດ"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, s.name as supplier_name 
        FROM Parts p
        LEFT JOIN Suppliers s ON p.supplier_id = s.id
        ORDER BY p.id DESC
    """)
    parts = cursor.fetchall()
    cursor.close()
    db.close()
    return parts

@router.post("/parts")
def add_part(
    name: str = Form(...),
    cost_price: float = Form(0),
    sell_price: float = Form(0),
    stock_qty: int = Form(0),
    min_stock: int = Form(5),
    unit: str = Form("ຊິ້ນ"),
    supplier_id: Optional[int] = Form(None),
    user: dict = Depends(authenticate_user)
):
    """ເພີ່ມອາໄຫຼ່ໃໝ່"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO Parts (name, cost_price, sell_price, stock_qty, min_stock, unit, supplier_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, cost_price, sell_price, stock_qty, min_stock, unit, supplier_id))
        db.commit()
        part_id = cursor.lastrowid
        return {"message": "ເພີ່ມອາໄຫຼ່ສຳເລັດ", "id": part_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.put("/parts/{part_id}")
def update_part(
    part_id: int,
    name: str = Form(...),
    cost_price: float = Form(0),
    sell_price: float = Form(0),
    stock_qty: int = Form(0),
    min_stock: int = Form(5),
    unit: str = Form("ຊິ້ນ"),
    supplier_id: Optional[int] = Form(None),
    user: dict = Depends(authenticate_user)
):
    """ອັບເດດຂໍ້ມູນອາໄຫຼ່"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if part exists
    cursor.execute("SELECT id FROM Parts WHERE id = %s", (part_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="ບໍ່ພົບອາໄຫຼ່")
    
    try:
        cursor.execute("""
            UPDATE Parts SET 
                name=%s, 
                cost_price=%s, 
                sell_price=%s, 
                stock_qty=%s, 
                min_stock=%s, 
                unit=%s, 
                supplier_id=%s
            WHERE id=%s
        """, (name, cost_price, sell_price, stock_qty, min_stock, unit, supplier_id, part_id))
        db.commit()
        return {"message": "ແກ້ໄຂອາໄຫຼ່ສຳເລັດ"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.delete("/parts/{part_id}")
def delete_part(part_id: int, user: dict = Depends(authenticate_user)):
    """ລຶບອາໄຫຼ່"""
    db = get_db()
    cursor = db.cursor()
    
    # Check if part exists
    cursor.execute("SELECT id FROM Parts WHERE id = %s", (part_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="ບໍ່ພົບອາໄຫຼ່")
    
    try:
        cursor.execute("DELETE FROM Parts WHERE id=%s", (part_id,))
        db.commit()
        return {"message": "ລຶບອາໄຫຼ່ສຳເລັດ"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.get("/parts/low-stock")
def get_low_stock_parts(user: dict = Depends(authenticate_user)):
    """ດຶງຂໍ້ມູນອາໄຫຼ່ທີ່ສະຕ໋ອກໃກ້ໝົດ"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, s.name as supplier_name 
        FROM Parts p
        LEFT JOIN Suppliers s ON p.supplier_id = s.id
        WHERE p.stock_qty <= p.min_stock
        ORDER BY (p.stock_qty / p.min_stock) ASC
    """)
    parts = cursor.fetchall()
    cursor.close()
    db.close()
    return parts

@router.get("/search-parts")
def search_parts(keyword: str = "", user: dict = Depends(authenticate_user)):
    """ຄົ້ນຫາອາໄຫຼ່"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if keyword:
        cursor.execute("""
            SELECT p.*, s.name as supplier_name 
            FROM Parts p
            LEFT JOIN Suppliers s ON p.supplier_id = s.id
            WHERE p.name LIKE %s OR p.id LIKE %s
            ORDER BY p.name
            LIMIT 20
        """, (f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("""
            SELECT p.*, s.name as supplier_name 
            FROM Parts p
            LEFT JOIN Suppliers s ON p.supplier_id = s.id
            ORDER BY p.name
            LIMIT 20
        """)
    
    parts = cursor.fetchall()
    cursor.close()
    db.close()
    return parts