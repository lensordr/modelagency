#!/usr/bin/env python3
"""
Migration script to add featured column to models table
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import engine
from sqlalchemy import text

def add_featured_column():
    """Add featured column to models table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='models' AND column_name='featured'
            """))
            
            if not result.fetchone():
                # Add the column
                conn.execute(text("ALTER TABLE models ADD COLUMN featured BOOLEAN DEFAULT FALSE"))
                conn.commit()
                print("✅ Added featured column to models table")
            else:
                print("ℹ️  Featured column already exists")
                
    except Exception as e:
        print(f"❌ Error adding featured column: {e}")

if __name__ == "__main__":
    add_featured_column()