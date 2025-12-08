from sqlalchemy import text
from models import engine
import json

# Update existing models with detailed rates structure
def migrate():
    with engine.connect() as conn:
        # Get all models
        result = conn.execute(text("SELECT id, rates FROM models"))
        models = result.fetchall()
        
        for model in models:
            model_id, current_rates = model
            
            # Create detailed rates structure
            detailed_rates = {
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
            }
            
            # If model already has rates, preserve the main ones
            if current_rates:
                try:
                    existing = json.loads(current_rates)
                    if isinstance(existing, dict):
                        detailed_rates.update(existing)
                except:
                    pass
            
            # Update the model
            conn.execute(
                text("UPDATE models SET rates = :rates WHERE id = :id"),
                {"rates": json.dumps(detailed_rates), "id": model_id}
            )
        
        conn.commit()
        print("✅ Updated all models with detailed rates structure")
    print("🎉 Detailed rates migration completed!")

if __name__ == "__main__":
    migrate()