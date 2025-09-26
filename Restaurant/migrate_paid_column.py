#!/usr/bin/env python3
"""
Migration script to add 'paid' column to order_items table
Run this on production to enable bill splitting feature
"""

import os
import sys
from sqlalchemy import create_engine, text

def migrate_database():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    # Fix postgres:// to postgresql:// for SQLAlchemy 2.0
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'order_items' AND column_name = 'paid'
            """))
            
            if result.fetchone():
                print("✅ 'paid' column already exists in order_items table")
                return True
            
            # Add the paid column
            print("🔄 Adding 'paid' column to order_items table...")
            conn.execute(text("ALTER TABLE order_items ADD COLUMN paid BOOLEAN DEFAULT FALSE"))
            conn.commit()
            
            print("✅ Successfully added 'paid' column to order_items table")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running database migration for bill splitting feature...")
    success = migrate_database()
    sys.exit(0 if success else 1)