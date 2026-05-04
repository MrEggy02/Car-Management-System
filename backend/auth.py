# auth.py (ฉบับสมบูรณ์)
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import get_db

security = HTTPBasic()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return plain_password == hashed_password

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    print(f"🔍 Login attempt: username={credentials.username}")
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE username = %s", (credentials.username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Username not found")
    
    if not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Wrong password")
    
    print(f"✅ Login success: {credentials.username}")
    return {
        "id": user['id'],
        "username": user['username'],
        "role": user['role'],
        "fullname": user['fullname']
    }