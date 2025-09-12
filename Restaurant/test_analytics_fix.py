#!/usr/bin/env python3
import sqlite3
from datetime import date

# Test the SQL query directly
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

today = date.today().isoformat()

# Test the new counting method
cursor.execute("""
    SELECT COUNT(DISTINCT checkout_date || '-' || table_number || '-' || waiter_id) as unique_checkouts
    FROM analytics_records 
    WHERE date(checkout_date) = ?
""", (today,))

count = cursor.fetchone()[0]
print(f"Unique checkouts using new method: {count}")

conn.close()