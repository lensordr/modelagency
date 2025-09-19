#!/usr/bin/env python3

from models import get_db, Restaurant, create_tables
from crud import init_sample_data

def setup_production():
    print("Setting up production database...")
    
    # Create tables
    create_tables()
    print("Tables created")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create demo restaurant if it doesn't exist
        demo_restaurant = db.query(Restaurant).filter(Restaurant.subdomain == 'demo').first()
        if not demo_restaurant:
            demo_restaurant = Restaurant(
                name='Demo Restaurant',
                subdomain='demo',
                plan_type='trial',
                active=True
            )
            db.add(demo_restaurant)
            db.commit()
            db.refresh(demo_restaurant)
            print(f'Created demo restaurant with ID: {demo_restaurant.id}')
        else:
            print(f'Demo restaurant already exists with ID: {demo_restaurant.id}')
        
        # Initialize sample data for demo restaurant
        init_sample_data(db, demo_restaurant.id)
        print('Sample data initialized')
        
    finally:
        db.close()
    
    print('Production setup complete!')

if __name__ == "__main__":
    setup_production()