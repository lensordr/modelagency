#!/usr/bin/env python3
"""
Barcelona Hotel Email Scraper using Google Cloud APIs
Uses Custom Search API and Places API for better results
"""

import requests
import re
import csv
import time
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse

class GoogleCloudHotelScraper:
    def __init__(self):
        # Set your Google Cloud API credentials
        self.search_api_key = os.getenv('GOOGLE_SEARCH_API_KEY', 'YOUR_SEARCH_API_KEY')
        self.places_api_key = os.getenv('GOOGLE_PLACES_API_KEY', 'YOUR_PLACES_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID', 'YOUR_SEARCH_ENGINE_ID')
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.hotels = []

    def search_places_api(self, query="hotels in Barcelona with room service", radius=50000):
        """Use Google Places API to find hotels"""
        print(f"Searching Places API: {query}")
        
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'key': self.places_api_key,
            'type': 'lodging',
            'location': '41.3851,2.1734',  # Barcelona coordinates
            'radius': radius
        }
        
        hotels = []
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            for place in data.get('results', []):
                if place.get('rating', 0) >= 3.5:  # Filter quality hotels
                    hotel_info = {
                        'name': place.get('name'),
                        'place_id': place.get('place_id'),
                        'rating': place.get('rating'),
                        'address': place.get('formatted_address')
                    }
                    hotels.append(hotel_info)
            
            return hotels
            
        except Exception as e:
            print(f"Places API error: {e}")
            return []

    def get_place_details(self, place_id):
        """Get detailed info including website from Places API"""
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,website,formatted_phone_number,formatted_address,rating',
            'key': self.places_api_key
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json().get('result', {})
        except Exception as e:
            print(f"Place details error: {e}")
            return {}

    def search_custom_search_api(self, query, num_results=10):
        """Use Google Custom Search API for hotel websites"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.search_api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': num_results
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'snippet': item.get('snippet')
                })
            
            return results
            
        except Exception as e:
            print(f"Custom Search API error: {e}")
            return []

    def extract_emails_from_url(self, url):
        """Extract emails from website"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Email patterns
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            
            # Get all text and search for emails
            text = soup.get_text()
            emails = re.findall(email_pattern, text)
            
            # Check mailto links
            for link in soup.find_all('a', href=re.compile(r'^mailto:')):
                email = link['href'].replace('mailto:', '').split('?')[0]
                emails.append(email)
            
            # Filter valid business emails
            valid_emails = []
            exclude = ['noreply', 'no-reply', 'example.com', 'test.com', 'privacy']
            
            for email in set(emails):
                email = email.lower().strip()
                if not any(ex in email for ex in exclude) and '@' in email:
                    valid_emails.append(email)
            
            return valid_emails
            
        except Exception as e:
            print(f"Error extracting emails from {url}: {e}")
            return []

    def scrape_barcelona_hotels(self):
        """Main scraping function using Google Cloud APIs"""
        
        # Step 1: Get hotels from Places API
        print("🔍 Finding Barcelona hotels with room service...")
        places_hotels = self.search_places_api()
        
        # Step 2: Get additional hotels from Custom Search
        search_queries = [
            "Barcelona luxury hotels room service email contact",
            "Barcelona 4 star hotels reservations email",
            "Barcelona boutique hotels contact information"
        ]
        
        search_results = []
        for query in search_queries:
            results = self.search_custom_search_api(query, 5)
            search_results.extend(results)
            time.sleep(1)
        
        print(f"Found {len(places_hotels)} hotels from Places API")
        print(f"Found {len(search_results)} results from Custom Search")
        
        # Step 3: Process Places API results
        for i, hotel in enumerate(places_hotels, 1):
            print(f"[{i}/{len(places_hotels)}] Processing: {hotel['name']}")
            
            # Get detailed info including website
            details = self.get_place_details(hotel['place_id'])
            website = details.get('website')
            
            hotel_data = {
                'name': hotel['name'],
                'address': hotel['address'],
                'rating': hotel['rating'],
                'website': website,
                'phone': details.get('formatted_phone_number'),
                'emails': []
            }
            
            # Extract emails from website
            if website:
                emails = self.extract_emails_from_url(website)
                hotel_data['emails'] = emails
                if emails:
                    print(f"  📧 Found: {', '.join(emails)}")
                else:
                    print(f"  ❌ No emails found")
            else:
                print(f"  ❌ No website available")
            
            self.hotels.append(hotel_data)
            time.sleep(1)
        
        # Step 4: Process Custom Search results
        for result in search_results:
            if any(keyword in result['link'].lower() for keyword in ['hotel', 'resort']):
                print(f"Checking: {result['title']}")
                emails = self.extract_emails_from_url(result['link'])
                
                if emails:
                    hotel_data = {
                        'name': result['title'],
                        'website': result['link'],
                        'emails': emails,
                        'source': 'custom_search'
                    }
                    self.hotels.append(hotel_data)
                    print(f"  📧 Found: {', '.join(emails)}")
                
                time.sleep(1)
        
        return self.hotels

    def save_results(self, filename='barcelona_hotels_gcloud.csv'):
        """Save results to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Hotel Name', 'Email', 'Website', 'Phone', 'Rating', 'Address']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for hotel in self.hotels:
                for email in hotel.get('emails', []):
                    writer.writerow({
                        'Hotel Name': hotel.get('name'),
                        'Email': email,
                        'Website': hotel.get('website', ''),
                        'Phone': hotel.get('phone', ''),
                        'Rating': hotel.get('rating', ''),
                        'Address': hotel.get('address', '')
                    })
        
        total_emails = sum(len(h.get('emails', [])) for h in self.hotels)
        print(f"\n✅ Results saved to {filename}")
        print(f"📊 Hotels found: {len(self.hotels)}")
        print(f"📧 Total emails: {total_emails}")

def main():
    print("🏨 Barcelona Hotel Email Scraper (Google Cloud)")
    print("=" * 50)
    
    # Check API keys
    scraper = GoogleCloudHotelScraper()
    
    if 'YOUR_' in scraper.search_api_key:
        print("⚠️  Please set your Google Cloud API keys:")
        print("export GOOGLE_SEARCH_API_KEY='your_key'")
        print("export GOOGLE_PLACES_API_KEY='your_key'")
        print("export GOOGLE_SEARCH_ENGINE_ID='your_engine_id'")
        return
    
    try:
        hotels = scraper.scrape_barcelona_hotels()
        scraper.save_results()
        
        # Show sample results
        print("\n🎯 SAMPLE RESULTS:")
        for hotel in hotels[:5]:
            if hotel.get('emails'):
                print(f"🏨 {hotel['name']}")
                print(f"   📧 {', '.join(hotel['emails'])}")
                print(f"   ⭐ {hotel.get('rating', 'N/A')}")
                print()
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()