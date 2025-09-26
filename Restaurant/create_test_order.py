#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Order, Table, OrderItem, MenuItem, Restaurant, Waiter
from datetime import datetime

def create_test_order():
    db = next(get_db())
    
    print("Creating test data for receipt...")
    
    # Create restaurant if not exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == 1).first()
    if not restaurant:
        restaurant = Restaurant(id=1, name="Test Restaurant", subdomain="demo", active=True)
        db.add(restaurant)
        db.commit()
        print("Created restaurant")
    
    # Create table if not exists
    table = db.query(Table).filter(Table.table_number == 1, Table.restaurant_id == 1).first()
    if not table:
        table = Table(table_number=1, code="ABC", status="occupied", restaurant_id=1, tip_amount=5.0)
        db.add(table)
        db.commit()
        print("Created table 1")
    
    # Create menu items if not exist
    pizza = db.query(MenuItem).filter(MenuItem.name == "Pizza Margherita", MenuItem.restaurant_id == 1).first()
    if not pizza:
        pizza = MenuItem(name="Pizza Margherita", price=12.0, category="Food", restaurant_id=1)
        db.add(pizza)
    
    coke = db.query(MenuItem).filter(MenuItem.name == "Coca Cola", MenuItem.restaurant_id == 1).first()
    if not coke:
        coke = MenuItem(name="Coca Cola", price=3.5, category="Drinks", restaurant_id=1)
        db.add(coke)
    
    db.commit()
    print("Created menu items")
    
    # Create order if not exists
    order = db.query(Order).filter(Order.table_id == table.id).first()
    if not order:
        order = Order(table_id=table.id, restaurant_id=1, status="active", created_at=datetime.now())
        db.add(order)
        db.commit()
        
        # Add order items
        pizza_item = OrderItem(order_id=order.id, product_id=pizza.id, qty=2)
        coke_item = OrderItem(order_id=order.id, product_id=coke.id, qty=1)
        
        db.add(pizza_item)
        db.add(coke_item)
        db.commit()
        print(f"Created order {order.id} with 2 items")
    
    print("Test data created successfully!")
    print("Now try the receipt for table 1")
    
    db.close()

if __name__ == "__main__":
    create_test_order()