#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, User, Restaurant
from sqlalchemy.orm import Session

def check_production_db():
    db = next(get_db())
    try:
        # Check all users
        users = db.query(User).all()
        print(f"Total users in database: {len(users)}")
        
        for user in users:
            restaurant = db.query(Restaurant).filter(Restaurant.id == user.restaurant_id).first()
            print(f"User: {user.username} | Restaurant: {restaurant.name if restaurant else 'DELETED'} | Active: {restaurant.active if restaurant else 'N/A'}")
        
        # Check all restaurants
        restaurants = db.query(Restaurant).all()
        print(f"\nTotal restaurants: {len(restaurants)}")
        
        for r in restaurants:
            print(f"Restaurant: {r.name} | Subdomain: {r.subdomain} | Active: {r.active}")
        
        # Specifically check for dublin
        dublin_users = db.query(User).filter(User.username.ilike('%dublin%')).all()
        print(f"\nUsers with 'dublin' in username: {len(dublin_users)}")
        for u in dublin_users:
            print(f"  - {u.username} (ID: {u.id})")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_production_db()