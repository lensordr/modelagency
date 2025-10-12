import os
from models import *
from sqlalchemy.orm import sessionmaker

# Create engine and session
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
db = Session()

try:
    # Find grand-hotel-test restaurant
    restaurant = db.query(Restaurant).filter(Restaurant.subdomain == 'grand-hotel-test').first()
    if restaurant:
        print(f'Found restaurant: {restaurant.name}')
        print(f'Current business_type: {getattr(restaurant, "business_type", "None")}')
        print(f'Current room_prefix: {getattr(restaurant, "room_prefix", "None")}')
        
        # Update to hotel
        restaurant.business_type = 'hotel'
        restaurant.room_prefix = 'RM'
        db.commit()
        print('Updated to hotel business type with RM prefix')
    else:
        print('Restaurant not found')
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()
