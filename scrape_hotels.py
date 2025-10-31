#!/usr/bin/env python3
"""
Hotel Email Scraper for Barcelona Hotels with Room Service
Scrapes Google search results and extracts email addresses from hotel websites
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import csv
from urllib.parse import urljoin, urlparse
import random

class HotelEmailScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.emails = set()
        self.hotels = []

    def search_google_hotels(self, query, max_results=50):
        """Search Google for hotels"""
        print(f"Searching Google: {query}")
        
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        try:
            response = self.session.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract search result links
            links = []
            for result in soup.find_all('div', class_='g'):
                link_elem = result.find('a')
                if link_elem and link_elem.get('href'):
                    url = link_elem['href']
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    # Filter for hotel websites
                    if any(keyword in url.lower() for keyword in ['hotel', 'resort', 'accommodation']):
                        title_elem = result.find('h3')
                        title = title_elem.text if title_elem else 'Unknown Hotel'
                        links.append({'url': url, 'title': title})
            
            return links[:max_results]
            
        except Exception as e:
            print(f"Error searching Google: {e}")
            return []

    def extract_emails_from_page(self, url):
        """Extract email addresses from a webpage"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Email regex pattern
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            
            # Search in text content
            text = soup.get_text()
            emails = re.findall(email_pattern, text)
            
            # Search in mailto links
            mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
            for link in mailto_links:
                email = link['href'].replace('mailto:', '').split('?')[0]
                emails.append(email)
            
            # Filter out common non-business emails
            filtered_emails = []
            exclude_domains = ['example.com', 'test.com', 'noreply', 'no-reply']
            
            for email in emails:
                email = email.lower().strip()
                if not any(domain in email for domain in exclude_domains):
                    filtered_emails.append(email)
            
            return list(set(filtered_emails))
            
        except Exception as e:
            print(f"Error extracting emails from {url}: {e}")
            return []

    def scrape_hotel_emails(self):
        """Main scraping function"""
        
        # Search queries for Barcelona hotels with room service
        queries = [
            "Barcelona hotels room service contact email",
            "Barcelona luxury hotels room service email",
            "Barcelona hotel reservations email room service",
            "Barcelona 4 star hotels room service contact",
            "Barcelona 5 star hotels room service email"
        ]
        
        all_hotel_links = []
        
        # Collect hotel links from all queries
        for query in queries:
            links = self.search_google_hotels(query, max_results=20)
            all_hotel_links.extend(links)
            time.sleep(random.uniform(2, 4))  # Random delay
        
        # Remove duplicates
        unique_links = {}
        for link in all_hotel_links:
            domain = urlparse(link['url']).netloc
            if domain not in unique_links:
                unique_links[domain] = link
        
        print(f"Found {len(unique_links)} unique hotel websites")
        
        # Extract emails from each hotel website
        for i, (domain, link) in enumerate(unique_links.items(), 1):
            print(f"[{i}/{len(unique_links)}] Scraping: {link['title']}")
            
            emails = self.extract_emails_from_page(link['url'])
            
            if emails:
                hotel_data = {
                    'name': link['title'],
                    'website': link['url'],
                    'domain': domain,
                    'emails': emails
                }
                self.hotels.append(hotel_data)
                print(f"  Found emails: {', '.join(emails)}")
            else:
                print(f"  No emails found")
            
            # Random delay between requests
            time.sleep(random.uniform(1, 3))
        
        return self.hotels

    def save_results(self, filename='barcelona_hotels_emails.csv'):
        """Save results to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Hotel Name', 'Website', 'Email', 'Domain']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for hotel in self.hotels:
                for email in hotel['emails']:
                    writer.writerow({
                        'Hotel Name': hotel['name'],
                        'Website': hotel['website'],
                        'Email': email,
                        'Domain': hotel['domain']
                    })
        
        print(f"\nResults saved to {filename}")
        print(f"Total hotels found: {len(self.hotels)}")
        print(f"Total emails extracted: {sum(len(h['emails']) for h in self.hotels)}")

def main():
    scraper = HotelEmailScraper()
    
    print("🏨 Barcelona Hotel Email Scraper")
    print("Searching for hotels with room service...")
    print("-" * 50)
    
    try:
        hotels = scraper.scrape_hotel_emails()
        
        if hotels:
            scraper.save_results()
            
            # Display summary
            print("\n📊 SUMMARY:")
            for hotel in hotels[:10]:  # Show first 10
                print(f"🏨 {hotel['name']}")
                print(f"   📧 {', '.join(hotel['emails'])}")
                print(f"   🌐 {hotel['website']}")
                print()
        else:
            print("No hotel emails found.")
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()