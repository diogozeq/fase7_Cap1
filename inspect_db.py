import sqlite3
import pandas as pd
import os

db_path = "farmtech.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"Found {len(tables)} tables:")
for table in tables:
    table_name = table[0]
    print(f"\n--- Table: {table_name} ---")
    
    # Get schema
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
        
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  Rows: {count}")
    
    # Get sample data
    if count > 0:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
        print("  Sample Data:")
        print(df.to_string())

conn.close()
