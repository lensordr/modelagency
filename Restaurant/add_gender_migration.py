#!/usr/bin/env python3
"""
Migration script to add gender column to models table
"""
import os
import sys
from sqlalchemy import create_engine, text

def migrate_database():
    # Use PostgreSQL on Heroku, SQLite locally
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    if not DATABASE_URL:
        DATABASE_URL = "sqlite:///./agency.db"
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if gender column exists
            if "postgresql" in DATABASE_URL:
                result = conn.execute(text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'models' AND column_name = 'gender'
                """))
                has_gender = len(result.fetchall()) > 0
            else:
                result = conn.execute(text("PRAGMA table_info(models)"))
                columns = [row[1] for row in result.fetchall()]
                has_gender = 'gender' in columns
            
            if not has_gender:
                print("Adding gender column to models table...")
                
                # Add gender column
                conn.execute(text("ALTER TABLE models ADD COLUMN gender VARCHAR(10) DEFAULT 'female'"))
                
                # Update existing models to female (default)
                conn.execute(text("UPDATE models SET gender = 'female' WHERE gender IS NULL"))
                
                conn.commit()
                print("✅ Gender column added successfully!")
            else:
                print("✅ Gender column already exists!")
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()