from sqlalchemy import text
from models import engine, SessionLocal
from models import City, Agency

def add_marbella():
    db = SessionLocal()
    try:
        # Get the agency
        agency = db.query(Agency).first()
        if agency:
            # Check if Marbella already exists
            existing = db.query(City).filter(City.name == "Marbella").first()
            if not existing:
                # Add Marbella city
                marbella = City(
                    agency_id=agency.id,
                    name="Marbella",
                    country="Spain",
                    active=True
                )
                db.add(marbella)
                db.commit()
                print("✅ Added Marbella to cities")
            else:
                print("⚠️ Marbella already exists")
        else:
            print("❌ No agency found")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_marbella()