#!/usr/bin/env python3
"""
Script to fix existing analytics records with 'Mixed' category
by updating them with proper categories from menu items
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, AnalyticsRecord, MenuItem
from sqlalchemy.orm import Session

def fix_analytics_categories():
    """Fix analytics records with Mixed category"""
    db = next(get_db())
    
    try:
        # Get all Mixed category records
        mixed_records = db.query(AnalyticsRecord).filter(
            AnalyticsRecord.item_category == "Mixed"
        ).all()
        
        print(f"Found {len(mixed_records)} Mixed category records to fix")
        
        # For each Mixed record, try to find the actual category
        for record in mixed_records:
            # Extract item name from "Order #123" format
            if record.item_name.startswith("Order #"):
                # This is an old order-level record, we'll delete it
                # since we now create item-level records
                print(f"Deleting old order-level record: {record.item_name}")
                db.delete(record)
            else:
                # Try to find the menu item to get the correct category
                menu_item = db.query(MenuItem).filter(
                    MenuItem.name == record.item_name,
                    MenuItem.restaurant_id == record.restaurant_id
                ).first()
                
                if menu_item:
                    old_category = record.item_category
                    record.item_category = menu_item.category
                    print(f"Updated {record.item_name}: {old_category} -> {menu_item.category}")
                else:
                    print(f"Could not find menu item for: {record.item_name}")
        
        db.commit()
        print("Analytics categories fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing analytics: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_analytics_categories()