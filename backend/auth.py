# auth.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import get_db
import hashlib

security = HTTPBasic()

def hash_password(password: str) -> str:
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return hash_password(plain_password) == hashed_password

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Authenticate user from Employees table"""
    print(f"Login attempt: username={credentials.username}")
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Search from Employees table
    cursor.execute("""
        SELECT id, name, username, password, role, status, can_login 
        FROM Employees 
        WHERE username = %s AND can_login = TRUE AND status = 'active'
    """, (credentials.username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Username not found or cannot login")
    
    if not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Wrong password")
    
    print(f"Login success: {credentials.username}")
    
    # ✅ Return user data with correct format
    return {
        "id": user['id'],
        "username": user['username'],
        "role": user['role'],
        "fullname": user['name']
    }