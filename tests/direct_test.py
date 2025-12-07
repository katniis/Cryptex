import mysql.connector
from datetime import datetime

# Direct connection - no pooling
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='cryptex'
)

cursor = conn.cursor()

try:
    # Test with actual API values
    cursor.execute("""
        INSERT INTO price (crypto_id, datetime, price, volume, market_cap, source)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (1, datetime.now(), 89501.7062399054, 60475283451.810394, 1786292326965.3362, 'Test'))
    
    conn.commit()
    print("✅ SUCCESS! Direct insert worked!")
    
    # Check it
    cursor.execute("SELECT * FROM price ORDER BY datetime DESC LIMIT 1")
    result = cursor.fetchone()
    print(f"Inserted: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()