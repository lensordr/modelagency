import sqlite3
import os

def migrate_database():
    """Add missing columns to existing database"""
    db_path = "database.db"
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet, no migration needed")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if has_extra_order column exists
    cursor.execute("PRAGMA table_info(tables)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'has_extra_order' not in columns:
        print("Adding has_extra_order column to tables...")
        cursor.execute("ALTER TABLE tables ADD COLUMN has_extra_order BOOLEAN DEFAULT 0")
        conn.commit()
        print("✓ Added has_extra_order column")
    
    if 'checkout_requested' not in columns:
        print("Adding checkout_requested column to tables...")
        cursor.execute("ALTER TABLE tables ADD COLUMN checkout_requested BOOLEAN DEFAULT 0")
        conn.commit()
        print("✓ Added checkout_requested column")
    
    if 'checkout_method' not in columns:
        print("Adding checkout_method column to tables...")
        cursor.execute("ALTER TABLE tables ADD COLUMN checkout_method TEXT")
        conn.commit()
        print("✓ Added checkout_method column")
    
    if 'tip_amount' not in columns:
        print("Adding tip_amount column to tables...")
        cursor.execute("ALTER TABLE tables ADD COLUMN tip_amount REAL DEFAULT 0.0")
        conn.commit()
        print("✓ Added tip_amount column")
    
    conn.close()
    print("Database migration completed!")

if __name__ == "__main__":
    migrate_database()