#!/usr/bin/env python3
"""
Create a test order for testing the ready notification system
"""

from models import get_db, Order, OrderItem, Table, MenuItem, Restaurant
from datetime import datetime

def create_test_order():
    db = next(get_db())
    
    # Find test-restaurant
    restaurant = db.query(Restaurant).filter(Restaurant.subdomain == 'test-restaurant').first()
    if not restaurant:
        print("test-restaurant not found")
        db.close()
        return
    
    print(f"Using restaurant: {restaurant.name} (ID: {restaurant.id})")
    
    # Find a table
    table = db.query(Table).filter(
        Table.restaurant_id == restaurant.id,
        Table.table_number == 3
    ).first()
    
    if not table:
        print("Table 3 not found")
        db.close()
        return
    
    # Find a menu item
    menu_item = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant.id,
        MenuItem.active == True
    ).first()
    
    if not menu_item:
        print("No active menu items found")
        db.close()
        return
    
    # Create order
    order = Order(
        restaurant_id=restaurant.id,
        table_id=table.id,
        created_at=datetime.utcnow(),
        status='active',
        kitchen_completed=False
    )
    db.add(order)
    db.flush()  # Get the order ID
    
    # Add order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=menu_item.id,
        qty=2
    )
    db.add(order_item)
    
    # Update table status
    table.status = 'occupied'
    table.ready_notification = False  # Reset notification
    
    db.commit()
    
    print(f"✅ Created test order {order.id} for Table {table.table_number}")
    print(f"   - Item: {menu_item.name} x2")
    print(f"   - Kitchen completed: {order.kitchen_completed}")
    print(f"   - Ready notification: {table.ready_notification}")
    
    db.close()

if __name__ == "__main__":
    create_test_order()