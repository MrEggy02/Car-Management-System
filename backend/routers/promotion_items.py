from fastapi import APIRouter, HTTPException, Depends, Form
from typing import Optional, List
from database import get_db
from auth import authenticate_user

router = APIRouter()

# ========== Promotion Items CRUD ==========

@router.get("/promotions/{promotion_id}/items")
def get_promotion_items(
    promotion_id: int,
    user: dict = Depends(authenticate_user)
):
    """ດຶງຂໍ້ມູນລາຍການທັງໝົດຂອງໂປຣໂມຊັນ"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get items with their details
    cursor.execute("""
        SELECT pi.*, 
            CASE 
                WHEN pi.item_type = 'part' THEN p.name
                WHEN pi.item_type = 'service' THEN s.name
            END as item_name,
            CASE 
                WHEN pi.item_type = 'part' THEN p.sell_price
                WHEN pi.item_type = 'service' THEN s.price
            END as item_price
        FROM Promotion_Items pi
        LEFT JOIN Parts p ON pi.item_type = 'part' AND pi.item_id = p.id
        LEFT JOIN Services s ON pi.item_type = 'service' AND pi.item_id = s.id
        WHERE pi.promotion_id = %s
        ORDER BY pi.item_type, pi.id
    """, (promotion_id,))
    
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return items

@router.post("/promotions/{promotion_id}/items")
def add_promotion_item(
    promotion_id: int,
    item_type: str = Form(...),
    item_id: int = Form(...),
    user: dict = Depends(authenticate_user)
):
    """ເພີ່ມລາຍການໃສ່ໂປຣໂມຊັນ"""
    
    # Validate item_type
    if item_type not in ['part', 'service']:
        raise HTTPException(status_code=400, detail="ປະເພດຕ້ອງເປັນ 'part' ຫຼື 'service'")
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if promotion exists
    cursor.execute("SELECT id FROM Promotions WHERE id = %s", (promotion_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="ບໍ່ພົບໂປຣໂມຊັນ")
    
    # Check if item exists
    if item_type == 'part':
        cursor.execute("SELECT id FROM Parts WHERE id = %s", (item_id,))
    else:
        cursor.execute("SELECT id FROM Services WHERE id = %s", (item_id,))
    
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"ບໍ່ພົບ {item_type} ນີ້")
    
    try:
        cursor.execute("""
            INSERT INTO Promotion_Items (promotion_id, item_type, item_id)
            VALUES (%s, %s, %s)
        """, (promotion_id, item_type, item_id))
        db.commit()
        return {"message": "ເພີ່ມລາຍການສຳເລັດ", "id": cursor.lastrowid}
    except Exception as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="ລາຍການນີ້ມີໃນໂປຣໂມຊັນແລ້ວ")
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@router.delete("/promotions/{promotion_id}/items/{item_id}")
def delete_promotion_item(
    promotion_id: int,
    item_id: int,
    user: dict = Depends(authenticate_user)
):
    """ລຶບລາຍການອອກຈາກໂປຣໂມຊັນ"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        DELETE FROM Promotion_Items 
        WHERE id = %s AND promotion_id = %s
    """, (item_id, promotion_id))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="ບໍ່ພົບລາຍການ")
    
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ລຶບລາຍການສຳເລັດ"}

@router.delete("/promotions/{promotion_id}/items")
def clear_promotion_items(
    promotion_id: int,
    user: dict = Depends(authenticate_user)
):
    """ລຶບທຸກລາຍການອອກຈາກໂປຣໂມຊັນ"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("DELETE FROM Promotion_Items WHERE promotion_id = %s", (promotion_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "ລຶບທຸກລາຍການສຳເລັດ"}

# ========== Helper endpoints ==========

@router.get("/promotions/{promotion_id}/available-parts")
def get_available_parts_for_promotion(
    promotion_id: int,
    user: dict = Depends(authenticate_user),
    search: str = ""
):
    """ດຶງຂໍ້ມູນ Parts ທີ່ຍັງບໍ່ໄດ້ເພີ່ມໃສ່ໂປຣໂມຊັນ"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get IDs of parts already in this promotion
    cursor.execute("""
        SELECT item_id FROM Promotion_Items 
        WHERE promotion_id = %s AND item_type = 'part'
    """, (promotion_id,))
    existing_ids = [row['item_id'] for row in cursor.fetchall()]
    
    # Build query
    query = """
        SELECT id, name, sell_price 
        FROM Parts 
        WHERE 1=1
    """
    params = []
    
    if existing_ids:
        query += " AND id NOT IN ({})".format(','.join(['%s'] * len(existing_ids)))
        params.extend(existing_ids)
    
    if search:
        query += " AND name LIKE %s"
        params.append(f"%{search}%")
    
    query += " ORDER BY name LIMIT 50"
    
    cursor.execute(query, params)
    parts = cursor.fetchall()
    cursor.close()
    db.close()
    return parts

@router.get("/promotions/{promotion_id}/available-services")
def get_available_services_for_promotion(
    promotion_id: int,
    user: dict = Depends(authenticate_user),
    search: str = ""
):
    """ດຶງຂໍ້ມູນ Services ທີ່ຍັງບໍ່ໄດ້ເພີ່ມໃສ່ໂປຣໂມຊັນ"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get IDs of services already in this promotion
    cursor.execute("""
        SELECT item_id FROM Promotion_Items 
        WHERE promotion_id = %s AND item_type = 'service'
    """, (promotion_id,))
    existing_ids = [row['item_id'] for row in cursor.fetchall()]
    
    # Build query
    query = """
        SELECT id, name, price 
        FROM Services 
        WHERE 1=1
    """
    params = []
    
    if existing_ids:
        query += " AND id NOT IN ({})".format(','.join(['%s'] * len(existing_ids)))
        params.extend(existing_ids)
    
    if search:
        query += " AND name LIKE %s"
        params.append(f"%{search}%")
    
    query += " ORDER BY name LIMIT 50"
    
    cursor.execute(query, params)
    services = cursor.fetchall()
    cursor.close()
    db.close()
    return services

# ========== Validate promotion for specific items ==========

@router.post("/promotions/validate-for-items")
def validate_promotion_for_items(
    promotion_id: int = Form(...),
    item_ids: str = Form(...),  # JSON string like '{"parts":[1,2], "services":[3,4]}'
    user: dict = Depends(authenticate_user)
):
    """ກວດສອບວ່າໂປຣໂມຊັນໃຊ້ກັບລາຍການທີ່ລະບຸໄດ້ຫຼືບໍ່"""
    import json
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get promotion details
    cursor.execute("SELECT * FROM Promotions WHERE id = %s", (promotion_id,))
    promotion = cursor.fetchone()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="ບໍ່ພົບໂປຣໂມຊັນ")
    
    # Parse item IDs
    items = json.loads(item_ids)
    part_ids = items.get('parts', [])
    service_ids = items.get('services', [])
    
    # If promotion has no specific items, it applies to everything
    cursor.execute("SELECT COUNT(*) as count FROM Promotion_Items WHERE promotion_id = %s", (promotion_id,))
    has_specific_items = cursor.fetchone()['count'] > 0
    
    if not has_specific_items:
        # Promotion applies to all items
        cursor.close()
        db.close()
        return {
            "valid": True,
            "promotion": promotion,
            "applicable_parts": part_ids,
            "applicable_services": service_ids,
            "non_applicable_parts": [],
            "non_applicable_services": []
        }
    
    # Check which parts are applicable
    applicable_parts = []
    non_applicable_parts = []
    
    if part_ids:
        placeholders = ','.join(['%s'] * len(part_ids))
        cursor.execute(f"""
            SELECT item_id FROM Promotion_Items 
            WHERE promotion_id = %s AND item_type = 'part' AND item_id IN ({placeholders})
        """, [promotion_id] + part_ids)
        applicable_parts = [row['item_id'] for row in cursor.fetchall()]
        non_applicable_parts = [pid for pid in part_ids if pid not in applicable_parts]
    
    # Check which services are applicable
    applicable_services = []
    non_applicable_services = []
    
    if service_ids:
        placeholders = ','.join(['%s'] * len(service_ids))
        cursor.execute(f"""
            SELECT item_id FROM Promotion_Items 
            WHERE promotion_id = %s AND item_type = 'service' AND item_id IN ({placeholders})
        """, [promotion_id] + service_ids)
        applicable_services = [row['item_id'] for row in cursor.fetchall()]
        non_applicable_services = [sid for sid in service_ids if sid not in applicable_services]
    
    cursor.close()
    db.close()
    
    return {
        "valid": len(applicable_parts) > 0 or len(applicable_services) > 0,
        "promotion": promotion,
        "applicable_parts": applicable_parts,
        "applicable_services": applicable_services,
        "non_applicable_parts": non_applicable_parts,
        "non_applicable_services": non_applicable_services
    }