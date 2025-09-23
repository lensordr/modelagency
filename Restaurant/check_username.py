#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, User, Restaurant
from sqlalchemy.orm import Session

def check_username_in_db(username):
    db = next(get_db())
    try:
        # Check if username exists
        users = db.query(User).filter(User.username == username).all()
        
        print(f"Checking username: '{username}'")
        print(f"Found {len(users)} users with this username:")
        
        for user in users:
            restaurant = db.query(Restaurant).filter(Restaurant.id == user.restaurant_id).first()
            print(f"  - User ID: {user.id}")
            print(f"  - Restaurant ID: {user.restaurant_id}")
            print(f"  - Restaurant Name: {restaurant.name if restaurant else 'DELETED'}")
            print(f"  - Restaurant Active: {restaurant.active if restaurant else 'N/A'}")
            print(f"  - Role: {user.role}")
            print("  ---")
        
        return len(users) > 0
        
    finally:
        db.close()

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "dublin"
    exists = check_username_in_db(username)
    print(f"\nResult: Username '{username}' {'EXISTS' if exists else 'AVAILABLE'}")