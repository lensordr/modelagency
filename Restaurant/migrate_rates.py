from sqlalchemy import text
from models import engine

# Add rates column to existing models table
migration_sql = "ALTER TABLE models ADD COLUMN rates TEXT;"

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text(migration_sql))
            conn.commit()
            print("✅ Added rates column to models table")
        except Exception as e:
            print(f"⚠️ Rates column may already exist: {e}")
    print("🎉 Rates migration completed!")

if __name__ == "__main__":
    migrate()