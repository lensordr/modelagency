from models import SessionLocal, Agency

def update_agency():
    db = SessionLocal()
    try:
        agency = db.query(Agency).first()
        if agency:
            agency.address = "Marbella, Spain"
            agency.phone = "+34 64 232 8671"
            agency.name = "Elite Models Marbella"
            db.commit()
            print("✅ Updated agency details to Marbella")
        else:
            print("❌ No agency found")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_agency()