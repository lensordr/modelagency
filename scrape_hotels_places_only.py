#!/usr/bin/env python3
"""
Barcelona Hotel Email Scraper - Places API Only
Since Custom Search is blocked, using only Places API + web scraping
"""

import requests
import re
import csv
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class PlacesHotelScraper:
    def __init__(self):
        self.places_api_key = "AIzaSyCstM_d8niDBj0-EQnJa2hhYlalARjEero"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.hotels = []

    def search_places_api(self, query, next_page_token=None):
        """Search Places API for hotels"""
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'key': self.places_api_key,
            'type': 'lodging',
            'location': '41.3851,2.1734',
            'radius': 20000
        }
        
        if next_page_token:
            params['pagetoken'] = next_page_token
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            hotels = []
            for place in data.get('results', []):
                if place.get('rating', 0) >= 3.0:  # Lower threshold for more results
                    hotels.append({
                        'name': place.get('name'),
                        'place_id': place.get('place_id'),
                        'rating': place.get('rating'),
                        'address': place.get('formatted_address'),
                        'price_level': place.get('price_level')
                    })
            
            return hotels, data.get('next_page_token')
            
        except Exception as e:
            print(f"Places API error: {e}")
            return [], None

    def get_place_details(self, place_id):
        """Get hotel website and contact info"""
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,website,formatted_phone_number,international_phone_number,url',
            'key': self.places_api_key
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json().get('result', {})
        except Exception as e:
            print(f"Place details error: {e}")
            return {}

    def extract_emails_from_url(self, url):
        """Extract emails from website"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            
            # Search in page text
            text = soup.get_text()
            emails = re.findall(email_pattern, text)
            
            # Search in mailto links
            for link in soup.find_all('a', href=re.compile(r'^mailto:')):
                email = link['href'].replace('mailto:', '').split('?')[0]
                emails.append(email)
            
            # Search in contact/reservation pages
            contact_links = soup.find_all('a', href=True)
            for link in contact_links:
                href = link['href'].lower()
                if any(word in href for word in ['contact', 'reservation', 'book']):
                    try:
                        full_url = requests.compat.urljoin(url, link['href'])
                        contact_response = self.session.get(full_url, timeout=10)
                        contact_soup = BeautifulSoup(contact_response.content, 'html.parser')
                        contact_emails = re.findall(email_pattern, contact_soup.get_text())
                        emails.extend(contact_emails)
                    except:
                        pass
            
            # Filter valid emails
            valid_emails = []
            exclude = ['noreply', 'no-reply', 'example.com', 'test.com', 'privacy', 'unsubscribe']
            
            for email in set(emails):
                email = email.lower().strip()
                if (not any(ex in email for ex in exclude) and 
                    '@' in email and 
                    len(email) > 5 and
                    '.' in email.split('@')[1]):
                    valid_emails.append(email)
            
            return valid_emails
            
        except Exception as e:
            print(f"  Error scraping {url}: {e}")
            return []

    def scrape_barcelona_hotels(self):
        """Main scraping function"""
        
        # Multiple search queries to get comprehensive results
        queries = [
            "hotels Barcelona room service",
            "luxury hotels Barcelona",
            "4 star hotels Barcelona",
            "5 star hotels Barcelona", 
            "boutique hotels Barcelona",
            "business hotels Barcelona"
        ]
        
        all_hotels = []
        
        # Search with different queries
        for query in queries:
            print(f"🔍 Searching: {query}")
            hotels, next_token = self.search_places_api(query)
            all_hotels.extend(hotels)
            
            # Get next page if available
            if next_token:
                time.sleep(2)  # Required delay for next page
                more_hotels, _ = self.search_places_api(query, next_token)
                all_hotels.extend(more_hotels)
            
            time.sleep(1)
        
        # Remove duplicates by place_id
        unique_hotels = {}
        for hotel in all_hotels:
            unique_hotels[hotel['place_id']] = hotel
        
        print(f"Found {len(unique_hotels)} unique hotels")
        
        # Process each hotel
        for i, (place_id, hotel) in enumerate(unique_hotels.items(), 1):
            print(f"[{i}/{len(unique_hotels)}] {hotel['name']}")
            
            # Get website
            details = self.get_place_details(place_id)
            website = details.get('website')
            
            hotel_data = {
                'name': hotel['name'],
                'address': hotel['address'],
                'rating': hotel['rating'],
                'price_level': hotel.get('price_level'),
                'website': website,
                'phone': details.get('formatted_phone_number'),
                'emails': []
            }
            
            # Extract emails from website
            if website:
                print(f"  🌐 Scraping: {website}")
                emails = self.extract_emails_from_url(website)
                hotel_data['emails'] = emails
                
                if emails:
                    print(f"  ✅ Found: {', '.join(emails)}")
                else:
                    print(f"  ❌ No emails found")
            else:
                print(f"  ❌ No website")
            
            self.hotels.append(hotel_data)
            time.sleep(2)  # Be respectful to websites
        
        return self.hotels

    def save_results(self, filename='barcelona_hotels_emails.csv'):
        """Save to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Hotel Name', 'Email', 'Website', 'Phone', 'Rating', 'Price Level', 'Address']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for hotel in self.hotels:
                if hotel.get('emails'):  # Only save hotels with emails
                    for email in hotel['emails']:
                        writer.writerow({
                            'Hotel Name': hotel['name'],
                            'Email': email,
                            'Website': hotel.get('website', ''),
                            'Phone': hotel.get('phone', ''),
                            'Rating': hotel.get('rating', ''),
                            'Price Level': hotel.get('price_level', ''),
                            'Address': hotel.get('address', '')
                        })
        
        hotels_with_emails = [h for h in self.hotels if h.get('emails')]
        total_emails = sum(len(h['emails']) for h in hotels_with_emails)
        
        print(f"\n✅ Results saved to {filename}")
        print(f"🏨 Hotels with emails: {len(hotels_with_emails)}")
        print(f"📧 Total emails found: {total_emails}")

def main():
    print("🏨 Barcelona Hotel Email Scraper (Places API Only)")
    print("=" * 55)
    
    scraper = PlacesHotelScraper()
    
    try:
        hotels = scraper.scrape_barcelona_hotels()
        scraper.save_results()
        
        # Show results summary
        hotels_with_emails = [h for h in hotels if h.get('emails')]
        print(f"\n📊 SUMMARY:")
        print(f"Total hotels found: {len(hotels)}")
        print(f"Hotels with emails: {len(hotels_with_emails)}")
        
        # Show top results
        print(f"\n🎯 TOP RESULTS:")
        for hotel in hotels_with_emails[:10]:
            print(f"🏨 {hotel['name']} ({hotel['rating']}⭐)")
            print(f"   📧 {', '.join(hotel['emails'])}")
            print(f"   📞 {hotel.get('phone', 'No phone')}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()