from models import SessionLocal, Model, City, Agency
import json

def check_models():
    db = SessionLocal()
    try:
        # Check if models exist
        models = db.query(Model).all()
        print(f"Found {len(models)} models in database:")
        
        for model in models:
            print(f"- {model.name} (ID: {model.id}, Status: {model.status})")
            
        # Check cities
        cities = db.query(City).all()
        print(f"\nFound {len(cities)} cities:")
        for city in cities:
            print(f"- {city.name}")
            
        # Update models with default values for new fields if they're None
        for model in models:
            updated = False
            if not hasattr(model, 'rates') or model.rates is None:
                model.rates = json.dumps({
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
                updated = True
                
            if updated:
                print(f"Updated {model.name} with default values")
        
        if updated:
            db.commit()
            print("✅ Updated models with default values")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_models()