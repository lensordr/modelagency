#!/usr/bin/env python3
"""
Reset database to empty state for fresh testing
"""
import os
import sqlite3
from models import create_tables, get_db
from crud import init_sample_data

def reset_database():
    """Remove existing database and create fresh one"""
    db_path = "database.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✓ Removed existing database")
    
    # Create fresh tables
    create_tables()
    print("✓ Created fresh database tables")
    
    # Initialize with sample data only (no test orders)
    db = next(get_db())
    init_sample_data(db)
    db.close()
    print("✓ Added sample menu items and tables")
    
    print("\n🎉 Database reset complete!")
    print("📋 Available:")
    print("   - 10 tables with codes")
    print("   - Sample menu items")
    print("   - No orders (clean slate)")
    print("\n🚀 You can now test with fresh orders")

if __name__ == "__main__":
    reset_database()