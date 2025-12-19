#!/usr/bin/env python3
"""
Migration script to fix field length issues in models table
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
            print("Fixing field lengths in models table...")
            
            if "postgresql" in DATABASE_URL:
                # PostgreSQL - alter column types
                alterations = [
                    "ALTER TABLE models ALTER COLUMN residence TYPE VARCHAR(200)",
                    "ALTER TABLE models ALTER COLUMN nationality TYPE VARCHAR(100)", 
                    "ALTER TABLE models ALTER COLUMN job TYPE VARCHAR(200)",
                    "ALTER TABLE models ALTER COLUMN favorite_perfume TYPE VARCHAR(200)",
                    "ALTER TABLE models ALTER COLUMN body_measurements TYPE VARCHAR(100)",
                    "ALTER TABLE models ALTER COLUMN bra_size TYPE VARCHAR(50)"
                ]
                
                for alteration in alterations:
                    try:
                        conn.execute(text(alteration))
                        print(f"✅ {alteration}")
                    except Exception as e:
                        print(f"⚠️  {alteration} - {e}")
                        
            else:
                # SQLite - need to recreate table with new schema
                print("SQLite detected - creating new table with updated schema...")
                
                # Create new table with updated schema
                conn.execute(text("""
                    CREATE TABLE models_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agency_id INTEGER NOT NULL,
                        city_id INTEGER,
                        name VARCHAR(100) NOT NULL,
                        age INTEGER,
                        height INTEGER,
                        hair_color VARCHAR(50),
                        eye_color VARCHAR(50),
                        gender VARCHAR(10) DEFAULT 'female',
                        bio TEXT,
                        photos TEXT,
                        status VARCHAR(20) DEFAULT 'pending',
                        available BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        residence VARCHAR(200),
                        availability VARCHAR(50),
                        nationality VARCHAR(100),
                        job VARCHAR(200),
                        body_measurements VARCHAR(100),
                        bra_size VARCHAR(50),
                        languages TEXT,
                        clothing_style TEXT,
                        lingerie_style TEXT,
                        favorite_cuisine TEXT,
                        favorite_perfume VARCHAR(200),
                        rates TEXT,
                        FOREIGN KEY (agency_id) REFERENCES agencies (id),
                        FOREIGN KEY (city_id) REFERENCES cities (id)
                    )
                """))
                
                # Copy data from old table
                conn.execute(text("""
                    INSERT INTO models_new 
                    SELECT * FROM models
                """))
                
                # Drop old table and rename new one
                conn.execute(text("DROP TABLE models"))
                conn.execute(text("ALTER TABLE models_new RENAME TO models"))
                
                print("✅ Table recreated with updated field lengths")
                
            conn.commit()
            print("✅ Field length migration completed successfully!")
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()