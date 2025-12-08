from sqlalchemy import text
from models import engine

# Add new columns to existing models table
migration_sql = """
ALTER TABLE models ADD COLUMN residence VARCHAR(100);
ALTER TABLE models ADD COLUMN availability VARCHAR(50);
ALTER TABLE models ADD COLUMN nationality VARCHAR(50);
ALTER TABLE models ADD COLUMN job VARCHAR(100);
ALTER TABLE models ADD COLUMN body_measurements VARCHAR(50);
ALTER TABLE models ADD COLUMN bra_size VARCHAR(20);
ALTER TABLE models ADD COLUMN languages TEXT;
ALTER TABLE models ADD COLUMN clothing_style TEXT;
ALTER TABLE models ADD COLUMN lingerie_style TEXT;
ALTER TABLE models ADD COLUMN favorite_cuisine TEXT;
ALTER TABLE models ADD COLUMN favorite_perfume VARCHAR(100);
"""

def migrate():
    with engine.connect() as conn:
        for statement in migration_sql.strip().split(';'):
            if statement.strip():
                try:
                    conn.execute(text(statement))
                    print(f"✅ Executed: {statement.strip()}")
                except Exception as e:
                    print(f"⚠️ Skipped (may already exist): {statement.strip()}")
        conn.commit()
    print("🎉 Migration completed!")

if __name__ == "__main__":
    migrate()