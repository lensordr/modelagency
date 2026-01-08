#!/usr/bin/env python3
"""
Check and fix duplicate cities
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, City

def fix_duplicate_cities():
    db = next(get_db())
    try:
        cities = db.query(City).all()
        print("Current cities:")
        for city in cities:
            print(f'ID: {city.id}, Name: {city.name}, Active: {city.active}')
        
        # Find duplicate Marbella entries
        marbella_cities = db.query(City).filter(City.name == "Marbella").all()
        print(f"\nFound {len(marbella_cities)} Marbella entries")
        
        if len(marbella_cities) > 1:
            # Keep the first active one, deactivate others
            kept_city = None
            for city in marbella_cities:
                if city.active and not kept_city:
                    kept_city = city
                    print(f"Keeping Marbella ID: {city.id}")
                else:
                    print(f"Deactivating duplicate Marbella ID: {city.id}")
                    city.active = False
            
            db.commit()
            print("Fixed duplicate Marbella entries")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_duplicate_cities()