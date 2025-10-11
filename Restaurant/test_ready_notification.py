#!/usr/bin/env python3
"""
Test script to simulate marking an order ready
"""

from models import get_db, Order, Table

def test_ready_notification():
    db = next(get_db())
    
    # Find an active order
    order = db.query(Order).filter(
        Order.status == 'active', 
        Order.kitchen_completed == False
    ).first()
    
    if not order:
        print("No active orders found to test")
        db.close()
        return
    
    print(f"Testing with Order {order.id} at Table {order.table.table_number}")
    
    # Mark as ready (simulate kitchen marking ready)
    order.kitchen_completed = True
    order.table.ready_notification = True
    db.commit()
    
    print(f"✅ Order {order.id} marked as ready!")
    print(f"Table {order.table.table_number} ready_notification: {order.table.ready_notification}")
    
    db.close()

if __name__ == "__main__":
    test_ready_notification()