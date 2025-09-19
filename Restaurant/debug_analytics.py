#!/usr/bin/env python3

from models import get_db, AnalyticsRecord, Restaurant

def debug_analytics():
    db = next(get_db())
    
    print("=== All Analytics Records ===")
    records = db.query(AnalyticsRecord).all()
    for r in records:
        print(f'ID: {r.id}, Restaurant: {r.restaurant_id}, Sales: {r.total_price}, Date: {r.checkout_date}')
    
    print("\n=== All Restaurants ===")
    restaurants = db.query(Restaurant).all()
    for r in restaurants:
        print(f'ID: {r.id}, Name: {r.name}, Subdomain: {r.subdomain}')
    
    db.close()

if __name__ == "__main__":
    debug_analytics()