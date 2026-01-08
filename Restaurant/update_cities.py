#!/usr/bin/env python3
"""
Update cities in the database to match new locations
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, City, Agency

def update_cities():
    db = next(get_db())
    try:
        agency = db.query(Agency).first()
        if not agency:
            print("No agency found")
            return
        
        # New cities to add
        new_cities = [
            {"name": "Estepona", "country": "Spain"},
            {"name": "Fuengirola", "country": "Spain"},
            {"name": "Torremolinos", "country": "Spain"},
            {"name": "Malaga", "country": "Spain"}
        ]
        
        # Cities to remove (set inactive)
        old_cities = ["Barcelona", "Madrid", "Valencia", "Sevilla"]
        
        # Deactivate old cities
        for city_name in old_cities:
            city = db.query(City).filter(City.name == city_name).first()
            if city:
                city.active = False
                print(f"Deactivated city: {city_name}")
        
        # Add new cities
        for city_data in new_cities:
            existing = db.query(City).filter(City.name == city_data["name"]).first()
            if not existing:
                city = City(
                    agency_id=agency.id,
                    name=city_data["name"],
                    country=city_data["country"],
                    active=True
                )
                db.add(city)
                print(f"Added city: {city_data['name']}")
            else:
                existing.active = True
                print(f"Activated existing city: {city_data['name']}")
        
        db.commit()
        print("Cities updated successfully!")
        
    except Exception as e:
        print(f"Error updating cities: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_cities()