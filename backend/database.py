import mysql.connector
from mysql.connector import pooling

# Create connection pool to reuse connections and bypass DNS resolution delays
db_pool = pooling.MySQLConnectionPool(
    pool_name="jp_auto_pool",
    pool_size=10,
    host="127.0.0.1",
    user="root",
    password="",
    database="jp_auto_db"
)

def get_db():
    return db_pool.get_connection()