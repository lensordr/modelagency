#!/usr/bin/env python3
"""
Database migration script for Heroku
Adds admin_email column if it doesn't exist
"""

import os
import psycopg2
from urllib.parse import urlparse

def migrate_database():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("No DATABASE_URL found")
        return
    
    # Fix postgres:// to postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Check if admin_email column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='restaurants' AND column_name='admin_email';
        """)
        
        if not cur.fetchone():
            print("Adding admin_email column...")
            cur.execute("ALTER TABLE restaurants ADD COLUMN admin_email VARCHAR(255);")
            conn.commit()
            print("admin_email column added successfully")
        else:
            print("admin_email column already exists")
        
        cur.close()
        conn.close()
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_database()