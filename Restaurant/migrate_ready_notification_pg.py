#!/usr/bin/env python3
"""
Migration script to add ready_notification column to tables (PostgreSQL)
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def migrate_database():
    # Load environment variables
    if os.path.exists('.env.local'):
        load_dotenv('.env.local')
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    if not DATABASE_URL:
        print("No DATABASE_URL found, using SQLite")
        DATABASE_URL = "sqlite:///./database.db"
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if column exists
            if 'postgresql' in DATABASE_URL:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'tables' AND column_name = 'ready_notification'
                """))
                
                if not result.fetchone():
                    print("Adding ready_notification column to tables (PostgreSQL)...")
                    conn.execute(text("ALTER TABLE tables ADD COLUMN ready_notification BOOLEAN DEFAULT FALSE"))
                    conn.commit()
                    print("✅ Migration completed successfully")
                else:
                    print("✅ ready_notification column already exists")
            else:
                # SQLite
                result = conn.execute(text("PRAGMA table_info(tables)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'ready_notification' not in columns:
                    print("Adding ready_notification column to tables (SQLite)...")
                    conn.execute(text("ALTER TABLE tables ADD COLUMN ready_notification BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("✅ Migration completed successfully")
                else:
                    print("✅ ready_notification column already exists")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_database()