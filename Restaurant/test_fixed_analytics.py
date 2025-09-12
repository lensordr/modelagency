#!/usr/bin/env python3
import sqlite3
from datetime import date

# Test the new analytics logic directly with SQL
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

today = date.today().isoformat()

# Test the new distinct counting method
cursor.execute("""
    SELECT COUNT(*) FROM (
        SELECT DISTINCT checkout_date, table_number, waiter_id
        FROM analytics_records 
        WHERE date(checkout_date) = ?
    )
""", (today,))

count = cursor.fetchone()[0]
print(f"Unique checkouts using new distinct method: {count}")

# Test waiter performance counting
cursor.execute("""
    SELECT waiter_id, COUNT(*) as orders FROM (
        SELECT DISTINCT checkout_date, table_number, waiter_id
        FROM analytics_records 
        WHERE date(checkout_date) = ?
    ) GROUP BY waiter_id
""", (today,))

waiter_counts = cursor.fetchall()
print(f"Waiter order counts: {waiter_counts}")

conn.close()