#!/usr/bin/env python3
"""
Migration script to add bill split functionality
Adds 'paid' column to order_items table
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db

def migrate_bill_split():
    """Add paid column to order_items table"""
    
    # Get database connection
    db = next(get_db())
    
    try:
        # Check if column already exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='order_items' AND column_name='paid'
        """))
        
        if result.fetchone():
            print("✅ Column 'paid' already exists in order_items table")
            return
        
        # Add the paid column
        print("🔄 Adding 'paid' column to order_items table...")
        db.execute(text("ALTER TABLE order_items ADD COLUMN paid BOOLEAN DEFAULT FALSE"))
        db.commit()
        print("✅ Successfully added 'paid' column to order_items table")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting bill split migration...")
    migrate_bill_split()
    print("✅ Migration completed successfully!")