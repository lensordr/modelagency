from models import SessionLocal, Waiter, AnalyticsRecord
from datetime import datetime, timedelta
import random

def create_fake_data():
    db = SessionLocal()
    
    # Clear existing data
    db.query(AnalyticsRecord).delete()
    db.query(Waiter).delete()
    
    # Create waiters
    waiter1 = Waiter(name="Marco")
    waiter2 = Waiter(name="Sofia")
    db.add(waiter1)
    db.add(waiter2)
    db.commit()
    
    # Get waiter IDs
    marco_id = waiter1.id
    sofia_id = waiter2.id
    
    # Menu items with categories
    menu_items = [
        ("Pizza Margherita", "Food", 12.50),
        ("Caesar Salad", "Food", 9.50),
        ("Pasta Carbonara", "Food", 14.00),
        ("Grilled Chicken", "Food", 16.00),
        ("Fish & Chips", "Food", 15.50),
        ("Tiramisu", "Desserts", 6.50),
        ("Chocolate Cake", "Desserts", 7.00),
        ("Ice Cream", "Desserts", 4.50),
        ("Espresso", "Beverages", 2.50),
        ("Wine", "Beverages", 8.00)
    ]
    
    # Create data for last 10 days
    for day_offset in range(9, -1, -1):
        checkout_date = datetime.now() - timedelta(days=day_offset)
        
        # Random number of orders per day (2-8)
        num_orders = random.randint(2, 8)
        
        for order_num in range(num_orders):
            # Randomly assign to waiter
            waiter_id = random.choice([marco_id, sofia_id])
            table_number = random.randint(1, 10)
            
            # Random number of items per order (1-5)
            num_items = random.randint(1, 5)
            order_tip = random.uniform(2.0, 15.0)
            tip_per_item = order_tip / num_items
            
            for _ in range(num_items):
                item_name, category, base_price = random.choice(menu_items)
                quantity = random.randint(1, 3)
                
                # Add some price variation
                unit_price = base_price + random.uniform(-1.0, 2.0)
                total_price = unit_price * quantity
                
                analytics_record = AnalyticsRecord(
                    checkout_date=checkout_date,
                    table_number=table_number,
                    waiter_id=waiter_id,
                    item_name=item_name,
                    item_category=category,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    tip_amount=tip_per_item
                )
                db.add(analytics_record)
    
    db.commit()
    
    # Print summary
    total_records = db.query(AnalyticsRecord).count()
    marco_orders = db.query(AnalyticsRecord).filter(AnalyticsRecord.waiter_id == marco_id).count()
    sofia_orders = db.query(AnalyticsRecord).filter(AnalyticsRecord.waiter_id == sofia_id).count()
    
    print(f"Created {total_records} analytics records")
    print(f"Marco: {marco_orders} items")
    print(f"Sofia: {sofia_orders} items")
    print("Fake data created successfully!")
    
    db.close()

if __name__ == "__main__":
    create_fake_data()