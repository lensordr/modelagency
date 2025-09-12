#!/usr/bin/env python3
import sqlite3
from datetime import date

# Connect to database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check analytics records for today
today = date.today().isoformat()
print(f"Checking analytics records for {today}...")

cursor.execute("""
    SELECT checkout_date, table_number, waiter_id, item_name, total_price 
    FROM analytics_records 
    WHERE date(checkout_date) = ?
    ORDER BY checkout_date DESC
""", (today,))

records = cursor.fetchall()
print(f"Found {len(records)} analytics records for today:")
for record in records:
    print(f"  {record}")

# Count unique checkouts for today
cursor.execute("""
    SELECT COUNT(DISTINCT checkout_date || '-' || table_number || '-' || waiter_id) as unique_checkouts
    FROM analytics_records 
    WHERE date(checkout_date) = ?
""", (today,))

unique_count = cursor.fetchone()[0]
print(f"\nUnique checkouts today: {unique_count}")

# Show all unique checkout combinations
cursor.execute("""
    SELECT checkout_date, table_number, waiter_id, COUNT(*) as items
    FROM analytics_records 
    WHERE date(checkout_date) = ?
    GROUP BY checkout_date, table_number, waiter_id
    ORDER BY checkout_date DESC
""", (today,))

checkouts = cursor.fetchall()
print(f"\nUnique checkout combinations:")
for checkout in checkouts:
    print(f"  {checkout}")

conn.close()