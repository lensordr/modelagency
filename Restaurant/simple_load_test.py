#!/usr/bin/env python3
"""
Simple Load Test - Tests existing demo restaurant
"""

import asyncio
import aiohttp
import time
import random

BASE_URL = "http://localhost:8000"  # Change this to your server URL
CONCURRENT_ORDERS = 100  # Simulate 100 simultaneous orders

async def place_demo_order(session, order_id):
    """Place order on test-restaurant"""
    try:
        # Get menu first from demo restaurant
        async with session.get(f'{BASE_URL}/r/demo/client/menu?table=1&lang=en') as response:
            if response.status != 200:
                return False, f"Menu fetch failed: {response.status}"
            
            menu_data = await response.json()
            menu_items = []
            for category, items in menu_data.get('menu', {}).items():
                menu_items.extend(items)
            
            if not menu_items:
                return False, "No menu items"

        # Create order
        selected_items = random.sample(menu_items, min(2, len(menu_items)))
        order_items = []
        for item in selected_items:
            order_items.append({
                'product_id': item['id'],
                'qty': random.randint(1, 2)
            })

        # Use actual table codes from demo restaurant
        table_codes = ['123', '456', '789', '321', '654', '987', '147', '258', '369', '741']
        table_num = (order_id % 10) + 1  # Use tables 1-10
        table_code = table_codes[table_num - 1]
        
        order_data = {
            'table_number': table_num,
            'code': table_code,
            'items': str(order_items).replace("'", '"')
        }

        start_time = time.time()
        async with session.post(f'{BASE_URL}/r/demo/client/order', data=order_data) as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                return True, response_time
            else:
                error_text = await response.text()
                return False, f"HTTP {response.status}: {error_text[:50]}"

    except Exception as e:
        return False, str(e)[:50]

async def check_server():
    """Check if server is running"""
    try:
        connector = aiohttp.TCPConnector()
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(f'{BASE_URL}/test') as response:
                return response.status == 200
    except:
        return False

async def run_simple_test():
    """Run simple load test on test-restaurant"""
    print(f"🚀 Testing {CONCURRENT_ORDERS} simultaneous orders on demo restaurant")
    
    # Check if server is running
    if not await check_server():
        print(f"❌ Server not running on {BASE_URL}")
        print("💡 Make sure to:")
        print("   1. cd Restaurant")
        print("   2. python main.py")
        print("   3. Wait for 'TableLink started successfully'")
        return
    
    connector = aiohttp.TCPConnector(limit=200)
    async with aiohttp.ClientSession(connector=connector) as session:
        
        start_time = time.time()
        
        # Create all order tasks
        tasks = []
        for i in range(CONCURRENT_ORDERS):
            task = place_demo_order(session, i)
            tasks.append(task)
        
        # Execute all orders simultaneously
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Analyze results
        success_count = 0
        failed_count = 0
        response_times = []
        errors = []
        
        for result in results:
            if isinstance(result, tuple):
                success, data = result
                if success:
                    success_count += 1
                    response_times.append(data)
                else:
                    failed_count += 1
                    errors.append(data)
            else:
                failed_count += 1
                errors.append(str(result))
        
        # Print results
        success_rate = (success_count / CONCURRENT_ORDERS * 100)
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        print(f"\n{'='*50}")
        print(f"📊 RESULTS")
        print(f"{'='*50}")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"✅ Success: {success_count}/{CONCURRENT_ORDERS}")
        print(f"❌ Failed: {failed_count}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⚡ Avg Response: {avg_response_time:.3f}s")
        print(f"🚀 Requests/sec: {CONCURRENT_ORDERS/total_time:.1f}")
        
        if errors:
            print(f"\n🚨 Sample Errors:")
            for error in errors[:3]:
                print(f"   • {error}")
        
        # Assessment
        if success_rate >= 95:
            print(f"\n🟢 EXCELLENT: System handles {CONCURRENT_ORDERS} concurrent orders!")
        elif success_rate >= 80:
            print(f"\n🟡 GOOD: System mostly handles the load")
        else:
            print(f"\n🔴 ISSUES: System struggles with {CONCURRENT_ORDERS} concurrent orders")

if __name__ == "__main__":
    print("🧪 Simple TableLink Load Test")
    print("Testing test-restaurant with concurrent orders")
    print(f"Server URL: {BASE_URL}")
    print("Starting test automatically...")
    
    asyncio.run(run_simple_test())