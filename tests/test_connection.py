import mysql.connector
from config.database import DB_CONFIG

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    print("✅ Connected to MySQL successfully!")
    print(f"Database: {conn.database}")
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print("\n📋 Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")