#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Order, Table, OrderItem, MenuItem
from crud import get_order_details

def test_receipt_data():
    db = next(get_db())
    
    print("=== TESTING RECEIPT DATA ===")
    
    # Check tables
    tables = db.query(Table).filter(Table.restaurant_id == 1).all()
    print(f"Tables found: {len(tables)}")
    for table in tables:
        print(f"  Table {table.table_number}: status={table.status}")
    
    # Check orders
    orders = db.query(Order).filter(Order.restaurant_id == 1).all()
    print(f"Orders found: {len(orders)}")
    for order in orders:
        table_num = order.table.table_number if order.table else "Unknown"
        print(f"  Order {order.id}: table={table_num}, status={order.status}, items={len(order.order_items)}")
    
    # Test get_order_details for table 1
    print(f"\n=== TESTING get_order_details for table 1 ===")
    details = get_order_details(db, 1, 1)
    if details:
        print(f"Order details found: {details}")
    else:
        print("No order details found for table 1")
    
    # Test other tables
    for i in range(2, 6):
        details = get_order_details(db, i, 1)
        if details:
            print(f"Table {i} has order: {len(details.get('items', []))} items")
    
    db.close()

if __name__ == "__main__":
    test_receipt_data()