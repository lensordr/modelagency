#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Restaurant, User, Table, MenuItem, Order, OrderItem, Waiter
from sqlalchemy.orm import Session

def clear_all_data():
    db = next(get_db())
    try:
        print("🗑️  Clearing entire database...")
        
        # Delete in correct order to avoid FK constraints
        from models import AnalyticsRecord
        
        print("Deleting analytics records...")
        db.query(AnalyticsRecord).delete()
        
        print("Deleting order items...")
        db.query(OrderItem).delete()
        
        print("Deleting orders...")
        db.query(Order).delete()
        
        print("Deleting menu items...")
        db.query(MenuItem).delete()
        
        print("Deleting waiters...")
        db.query(Waiter).delete()
        
        print("Deleting tables...")
        db.query(Table).delete()
        
        print("Deleting users...")
        db.query(User).delete()
        
        print("Deleting restaurants...")
        db.query(Restaurant).delete()
        
        db.commit()
        print("✅ Database cleared successfully!")
        
        # Reinitialize with sample data
        print("🔄 Reinitializing with sample data...")
        from crud import init_sample_data
        init_sample_data(db)
        print("✅ Sample data restored!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_data()