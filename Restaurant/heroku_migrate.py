from sqlalchemy import text
from models import engine
import json

def migrate_heroku():
    with engine.connect() as conn:
        # Add all new columns
        columns = [
            "ALTER TABLE models ADD COLUMN residence VARCHAR(100);",
            "ALTER TABLE models ADD COLUMN availability VARCHAR(50);", 
            "ALTER TABLE models ADD COLUMN nationality VARCHAR(50);",
            "ALTER TABLE models ADD COLUMN job VARCHAR(100);",
            "ALTER TABLE models ADD COLUMN body_measurements VARCHAR(50);",
            "ALTER TABLE models ADD COLUMN bra_size VARCHAR(20);",
            "ALTER TABLE models ADD COLUMN languages TEXT;",
            "ALTER TABLE models ADD COLUMN clothing_style TEXT;",
            "ALTER TABLE models ADD COLUMN lingerie_style TEXT;",
            "ALTER TABLE models ADD COLUMN favorite_cuisine TEXT;",
            "ALTER TABLE models ADD COLUMN favorite_perfume VARCHAR(100);",
            "ALTER TABLE models ADD COLUMN rates TEXT;"
        ]
        
        for sql in columns:
            try:
                conn.execute(text(sql))
                print(f"✅ {sql}")
            except Exception as e:
                print(f"⚠️ Skipped: {sql} - {e}")
        
        # Update all models with default rates
        conn.execute(text("""
            UPDATE models SET rates = :rates WHERE rates IS NULL
        """), {
            "rates": json.dumps({
                "short_price": "On Request",
                "gentleman_price": "1400.- / 1300.- (Member)",
                "overnight_price": "2200.- / 2000.- (Member)", 
                "luxury_price": "3200.- / 3000.- (Member)",
                "detailed": {
                    "1_short_hour": "Members Only / On Request",
                    "1_5_short_hours": "Members Only / On Request",
                    "2_hours_passion": "900.- / 800.- (Member)",
                    "3_unforgettable": "1200.- / 1100.- (Member)",
                    "4_intimate_dinner": "1400.- / 1300.- (Member)",
                    "5_intimate_dinner": "1600.- / 1500.- (Member)",
                    "short_overnight_8h": "2200.- / 2000.- (Member)",
                    "long_overnight_12h": "2400.- / 2200.- (Member)",
                    "long_overnight_18h": "2800.- / 2600.- (Member)",
                    "one_day_24h": "3200.- / 3000.- (Member)",
                    "two_days_48h": "4500.- / 4300.- (Member)",
                    "additional_day": "1400.- / 1200.- (Member)"
                }
            })
        })
        
        conn.commit()
        print("🎉 Heroku migration completed!")

if __name__ == "__main__":
    migrate_heroku()