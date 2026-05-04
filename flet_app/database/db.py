import mysql.connector
from mysql.connector import Error

# การตั้งค่าเชื่อมต่อ MySQL (ปรับตาม Laragon ของคุณ)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',      # ของ Laragon ปกติคือ root
    'password': '',      # ของ Laragon ปกติคือ ว่างเปล่า
    'database': 'jp_auto_system'
}

def get_connection():
    """รับการเชื่อมต่อ MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ เชื่อมต่อฐานข้อมูลไม่ได้: {e}")
        return None

def init_database():
    """สร้างตารางทั้งหมดใน MySQL"""
    conn = get_connection()
    if conn is None:
        print("❌ ไม่สามารถเชื่อมต่อ MySQL ได้")
        return
    
    cursor = conn.cursor()
    
    # D1: ข้อมูลพนักงาน
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(200) NOT NULL,
            position VARCHAR(100),
            phone VARCHAR(20),
            salary DECIMAL(10,2),
            hire_date DATE
        )
    ''')
    
    # D2: ข้อมูลร้าน
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_info (
            id INT PRIMARY KEY AUTO_INCREMENT,
            shop_name VARCHAR(200) NOT NULL,
            address TEXT,
            phone VARCHAR(20),
            email VARCHAR(100),
            tax_id VARCHAR(50)
        )
    ''')
    
    # D3: ข้อมูลผู้สะໜອງ (Supplier)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(200) NOT NULL,
            contact_person VARCHAR(100),
            phone VARCHAR(20),
            address TEXT,
            email VARCHAR(100)
        )
    ''')
    
    # D4: ข้อมูลรายการบริการ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INT PRIMARY KEY AUTO_INCREMENT,
            service_name VARCHAR(200) NOT NULL,
            description TEXT,
            price DECIMAL(10,2),
            duration_minutes INT
        )
    ''')
    
    # D5: ข้อมูลอะไหล่
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spare_parts (
            id INT PRIMARY KEY AUTO_INCREMENT,
            part_name VARCHAR(200) NOT NULL,
            brand VARCHAR(100),
            price DECIMAL(10,2),
            stock_quantity INT DEFAULT 0,
            supplier_id INT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
        )
    ''')
    
    # D6: ข้อมูลโปรโมชัน
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promotions (
            id INT PRIMARY KEY AUTO_INCREMENT,
            promo_name VARCHAR(200) NOT NULL,
            discount_percent DECIMAL(5,2),
            start_date DATE,
            end_date DATE,
            service_id INT,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL
        )
    ''')
    
    # D7: ข้อมูลลูกค้า
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INT PRIMARY KEY AUTO_INCREMENT,
            customer_id VARCHAR(50) UNIQUE NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20),
            email VARCHAR(100),
            address TEXT,
            register_date DATE
        )
    ''')
    
    # D8: ข้อมูลรถ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INT PRIMARY KEY AUTO_INCREMENT,
            customer_id VARCHAR(50) NOT NULL,
            license_plate VARCHAR(20) UNIQUE NOT NULL,
            brand VARCHAR(100),
            model VARCHAR(100),
            year INT,
            color VARCHAR(50),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ สร้างตารางใน MySQL เรียบร้อย")

# เพิ่มฟังก์ชันทดสอบการเชื่อมต่อ
def test_connection():
    """ทดสอบว่าเชื่อมต่อ MySQL ได้หรือไม่"""
    conn = get_connection()
    if conn:
        print("✅ เชื่อมต่อ MySQL สำเร็จ")
        conn.close()
        return True
    else:
        print("❌ เชื่อมต่อ MySQL ไม่ได้")
        return False