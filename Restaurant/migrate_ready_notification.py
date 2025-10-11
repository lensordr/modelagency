#!/usr/bin/env python3
"""
Migration script to add ready_notification column to tables
"""

import sqlite3
import os

def migrate_database():
    db_path = "database.db"
    
    if not os.path.exists(db_path):
        print("Database file not found, skipping migration")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(tables)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'ready_notification' not in columns:
            print("Adding ready_notification column to tables...")
            cursor.execute("ALTER TABLE tables ADD COLUMN ready_notification BOOLEAN DEFAULT 0")
            conn.commit()
            print("✅ Migration completed successfully")
        else:
            print("✅ ready_notification column already exists")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_database()