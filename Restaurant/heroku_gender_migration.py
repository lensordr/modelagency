#!/usr/bin/env python3
"""
Heroku PostgreSQL migration script to add gender column
"""
import os
import sys
from sqlalchemy import create_engine, text

def migrate_heroku_database():
    # Get Heroku PostgreSQL URL
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found. Make sure you're running this on Heroku or have the env var set.")
        sys.exit(1)
    
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if gender column exists
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'models' AND column_name = 'gender'
            """))
            
            if not result.fetchall():
                print("Adding gender column to models table...")
                
                # Add gender column
                conn.execute(text("ALTER TABLE models ADD COLUMN gender VARCHAR(10) DEFAULT 'female'"))
                
                # Update existing models to female (default)
                conn.execute(text("UPDATE models SET gender = 'female' WHERE gender IS NULL"))
                
                conn.commit()
                print("✅ Gender column added successfully to Heroku database!")
            else:
                print("✅ Gender column already exists in Heroku database!")
                
    except Exception as e:
        print(f"❌ Error during Heroku migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_heroku_database()