#!/usr/bin/env python3
import sqlite3
from datetime import date

# Test the new order counting logic
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

today = date.today().isoformat()

# Count distinct checkout timestamps (each checkout = one order)
cursor.execute("""
    SELECT COUNT(DISTINCT checkout_date) as total_orders
    FROM analytics_records 
    WHERE date(checkout_date) = ?
""", (today,))

total_orders = cursor.fetchone()[0]
print(f"Total orders today (distinct checkout timestamps): {total_orders}")

# Count orders per waiter
cursor.execute("""
    SELECT waiter_id, COUNT(DISTINCT checkout_date) as orders
    FROM analytics_records 
    WHERE date(checkout_date) = ?
    GROUP BY waiter_id
""", (today,))

waiter_orders = cursor.fetchall()
print(f"Orders per waiter: {waiter_orders}")

conn.close()