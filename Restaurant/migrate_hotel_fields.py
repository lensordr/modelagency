#!/usr/bin/env python3
"""
Safe migration script to add hotel support fields to the Restaurant table.
This script adds business_type and room_prefix columns safely.
"""

import os
import sys
from sqlalchemy import text, inspect
from models import engine, get_db

def check_column_exists(table_name, column_name):
    """Check if a column exists in the table"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        print(f"Error checking column {column_name}: {e}")
        return False

def add_hotel_fields():
    """Add hotel fields to restaurants table if they don't exist"""
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check if business_type column exists
                if not check_column_exists('restaurants', 'business_type'):
                    print("Adding business_type column...")
                    conn.execute(text("""
                        ALTER TABLE restaurants 
                        ADD COLUMN business_type VARCHAR(20) DEFAULT 'restaurant'
                    """))
                    print("✓ business_type column added")
                else:
                    print("✓ business_type column already exists")
                
                # Check if room_prefix column exists
                if not check_column_exists('restaurants', 'room_prefix'):
                    print("Adding room_prefix column...")
                    conn.execute(text("""
                        ALTER TABLE restaurants 
                        ADD COLUMN room_prefix VARCHAR(10) DEFAULT ''
                    """))
                    print("✓ room_prefix column added")
                else:
                    print("✓ room_prefix column already exists")
                
                # Commit the transaction
                trans.commit()
                print("✅ Migration completed successfully!")
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    try:
        db = next(get_db())
        
        # Try to query with new columns
        result = db.execute(text("""
            SELECT id, name, business_type, room_prefix 
            FROM restaurants 
            LIMIT 1
        """))
        
        row = result.fetchone()
        if row:
            print(f"✅ Verification successful - Sample: ID={row[0]}, Name={row[1]}, Type={row[2]}, Prefix={row[3]}")
        else:
            print("✅ Migration verified - No data to display")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting hotel fields migration...")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'Local SQLite')}")
    
    # Run migration
    if add_hotel_fields():
        # Verify migration
        if verify_migration():
            print("🎉 Hotel support migration completed successfully!")
            sys.exit(0)
        else:
            print("⚠️ Migration completed but verification failed")
            sys.exit(1)
    else:
        print("💥 Migration failed!")
        sys.exit(1)