#!/usr/bin/env python3
"""
Load Test Script for TableLink
Simulates 40 restaurants with 10 tables each placing orders simultaneously
"""

import asyncio
import aiohttp
import time
import random
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"  # Change to your server URL
NUM_RESTAURANTS = 40
TABLES_PER_RESTAURANT = 10
ORDERS_PER_TABLE = 2  # Number of orders each table will place

class LoadTester:
    def __init__(self):
        self.session = None
        self.restaurants = []
        self.results = {
            'success': 0,
            'failed': 0,
            'errors': [],
            'response_times': []
        }

    async def setup_session(self):
        """Create HTTP session with connection pooling"""
        connector = aiohttp.TCPConnector(
            limit=200,  # Total connection pool size
            limit_per_host=50  # Connections per host
        )
        self.session = aiohttp.ClientSession(connector=connector)

    async def cleanup(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    async def create_test_restaurants(self):
        """Create 40 test restaurants"""
        print("🏗️  Creating test restaurants...")
        
        for i in range(1, NUM_RESTAURANTS + 1):
            restaurant_data = {
                'restaurant_name': f'Test Restaurant {i}',
                'admin_email': f'test{i}@example.com',
                'admin_username': f'admin{i}',
                'admin_password': 'testpass123',
                'table_count': TABLES_PER_RESTAURANT,
                'plan_type': 'trial',
                'business_type': 'restaurant'
            }
            
            try:
                async with self.session.post(f'{BASE_URL}/onboard', data=restaurant_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            self.restaurants.append({
                                'id': i,
                                'subdomain': result.get('subdomain', f'test-restaurant-{i}'),
                                'username': f'admin{i}',
                                'password': 'testpass123'
                            })
                            print(f"✅ Created restaurant {i}")
                        else:
                            print(f"❌ Failed to create restaurant {i}: {result.get('error')}")
                    else:
                        print(f"❌ HTTP {response.status} creating restaurant {i}")
            except Exception as e:
                print(f"❌ Error creating restaurant {i}: {e}")

        print(f"📊 Created {len(self.restaurants)} restaurants")

    async def get_menu_items(self, restaurant_subdomain):
        """Get menu items for a restaurant"""
        try:
            url = f'{BASE_URL}/r/{restaurant_subdomain}/client/menu?table=1&lang=en'
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    menu_items = []
                    for category, items in data.get('menu', {}).items():
                        menu_items.extend(items)
                    return menu_items
        except Exception as e:
            print(f"Error getting menu for {restaurant_subdomain}: {e}")
        return []

    async def place_order(self, restaurant, table_number):
        """Place an order for a specific table"""
        start_time = time.time()
        
        try:
            # Get menu items
            menu_items = await self.get_menu_items(restaurant['subdomain'])
            if not menu_items:
                raise Exception("No menu items found")

            # Select random items for order
            selected_items = random.sample(menu_items, min(3, len(menu_items)))
            order_items = []
            
            for item in selected_items:
                order_items.append({
                    'product_id': item['id'],
                    'qty': random.randint(1, 3)
                })

            # Place order
            order_data = {
                'table_number': table_number,
                'code': f'{table_number:03d}',  # Simple code: 001, 002, etc.
                'items': str(order_items).replace("'", '"')  # Convert to JSON string
            }

            url = f'{BASE_URL}/r/{restaurant["subdomain"]}/client/order'
            async with self.session.post(url, data=order_data) as response:
                response_time = time.time() - start_time
                self.results['response_times'].append(response_time)
                
                if response.status == 200:
                    self.results['success'] += 1
                    return True
                else:
                    error_text = await response.text()
                    self.results['failed'] += 1
                    self.results['errors'].append(f"HTTP {response.status}: {error_text[:100]}")
                    return False

        except Exception as e:
            response_time = time.time() - start_time
            self.results['response_times'].append(response_time)
            self.results['failed'] += 1
            self.results['errors'].append(str(e)[:100])
            return False

    async def simulate_restaurant_load(self, restaurant):
        """Simulate all tables in a restaurant placing orders"""
        tasks = []
        
        for table_num in range(1, TABLES_PER_RESTAURANT + 1):
            for order_num in range(ORDERS_PER_TABLE):
                task = self.place_order(restaurant, table_num)
                tasks.append(task)
        
        # Execute all orders for this restaurant simultaneously
        await asyncio.gather(*tasks, return_exceptions=True)

    async def run_load_test(self):
        """Run the complete load test"""
        print("🚀 Starting TableLink Load Test")
        print(f"📊 Testing: {NUM_RESTAURANTS} restaurants × {TABLES_PER_RESTAURANT} tables × {ORDERS_PER_TABLE} orders")
        print(f"📊 Total concurrent orders: {NUM_RESTAURANTS * TABLES_PER_RESTAURANT * ORDERS_PER_TABLE}")
        
        await self.setup_session()
        
        # Create test restaurants
        await self.create_test_restaurants()
        
        if not self.restaurants:
            print("❌ No restaurants created. Exiting.")
            return
        
        print(f"\n🔥 Starting load test with {len(self.restaurants)} restaurants...")
        start_time = time.time()
        
        # Create tasks for all restaurants
        restaurant_tasks = []
        for restaurant in self.restaurants:
            task = self.simulate_restaurant_load(restaurant)
            restaurant_tasks.append(task)
        
        # Execute all restaurant loads simultaneously
        await asyncio.gather(*restaurant_tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Print results
        self.print_results(total_time)
        
        await self.cleanup()

    def print_results(self, total_time):
        """Print load test results"""
        total_requests = self.results['success'] + self.results['failed']
        success_rate = (self.results['success'] / total_requests * 100) if total_requests > 0 else 0
        
        avg_response_time = sum(self.results['response_times']) / len(self.results['response_times']) if self.results['response_times'] else 0
        
        print(f"\n{'='*60}")
        print(f"🎯 LOAD TEST RESULTS")
        print(f"{'='*60}")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        print(f"📊 Total Requests: {total_requests}")
        print(f"✅ Successful: {self.results['success']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⚡ Avg Response Time: {avg_response_time:.3f}s")
        print(f"🚀 Requests/Second: {total_requests/total_time:.1f}")
        
        if self.results['errors']:
            print(f"\n🚨 Sample Errors:")
            for error in self.results['errors'][:5]:  # Show first 5 errors
                print(f"   • {error}")
        
        # Performance assessment
        print(f"\n🎯 PERFORMANCE ASSESSMENT:")
        if success_rate >= 95 and avg_response_time < 2.0:
            print("🟢 EXCELLENT: System handles high load very well!")
        elif success_rate >= 80 and avg_response_time < 5.0:
            print("🟡 GOOD: System handles load with some delays")
        else:
            print("🔴 NEEDS IMPROVEMENT: System struggles under high load")

async def main():
    """Main function"""
    tester = LoadTester()
    await tester.run_load_test()

if __name__ == "__main__":
    print("🧪 TableLink Load Testing Tool")
    print("Make sure your server is running on http://localhost:8000")
    input("Press Enter to start the load test...")
    
    asyncio.run(main())