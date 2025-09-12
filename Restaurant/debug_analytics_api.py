#!/usr/bin/env python3
import requests
from datetime import date

# Test the analytics API directly
today = date.today().isoformat()

try:
    # Test the analytics dashboard endpoint
    response = requests.get(f'http://localhost:8000/business/analytics/dashboard?target_date={today}&period=day')
    
    if response.status_code == 200:
        data = response.json()
        print("Analytics API Response:")
        print(f"Total Orders: {data['summary']['total_orders']}")
        print(f"Total Sales: €{data['summary']['total_sales']:.2f}")
        print(f"Total Tips: €{data['summary']['total_tips']:.2f}")
        print("\nWaiter Performance:")
        for waiter in data['waiters']:
            print(f"  {waiter['name']}: {waiter['total_orders']} orders")
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Connection error: {e}")
    print("Make sure the server is running on localhost:8000")