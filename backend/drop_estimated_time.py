import mysql.connector
import sys

def drop_column():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="jp_auto_db"
        )
        cursor = conn.cursor()
        
        # Check if column exists before dropping to avoid errors
        cursor.execute("SHOW COLUMNS FROM Services LIKE 'estimated_time'")
        result = cursor.fetchone()
        
        if result:
            print("Dropping column 'estimated_time' from 'Services' table...")
            cursor.execute("ALTER TABLE Services DROP COLUMN estimated_time;")
            conn.commit()
            print("Column dropped successfully.")
        else:
            print("Column 'estimated_time' does not exist in 'Services' table.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    drop_column()
