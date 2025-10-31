#!/usr/bin/env python3
"""
Hotel Email Campaign Sender using Gmail API
Sends personalized TableLink pitches to Barcelona hotels
"""

import csv
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

class HotelEmailSender:
    def __init__(self):
        # Gmail SMTP settings
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
        self.sender_password = os.getenv('SENDER_APP_PASSWORD', 'your-app-password')
        self.sender_name = "TableLink Team"
        
    def create_email_template(self, hotel_name):
        """Create personalized email for hotel"""
        
        subject = f"Revolutionize {hotel_name}'s Room Service with TableLink"
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px; max-width: 600px; margin: 0 auto; }}
        .highlight {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0; }}
        .cta {{ background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏨 TableLink</h1>
        <p>Digital Room Service Revolution</p>
    </div>
    
    <div class="content">
        <h2>Dear {hotel_name} Management,</h2>
        
        <p>I hope this email finds you well. I'm reaching out because <strong>{hotel_name}</strong> has caught our attention as a premier Barcelona hotel that values exceptional guest experience.</p>
        
        <div class="highlight">
            <h3>🚀 What is TableLink?</h3>
            <p>TableLink is a <strong>QR code-based digital ordering platform</strong> that transforms how guests order food and services. Perfect for <strong>hotel room service</strong> and <strong>restaurant table ordering</strong> - guests simply scan QR codes to order instantly.</p>
        </div>
        
        <h3>✨ Why Barcelona Hotels Choose TableLink:</h3>
        <ul>
            <li><strong>📱 Contactless Ordering</strong> - Guests scan QR codes to order instantly</li>
            <li><strong>💰 Increase Revenue</strong> - 35% average increase in room service orders</li>
            <li><strong>⚡ Faster Service</strong> - Orders go directly to kitchen, no phone delays</li>
            <li><strong>📊 Real-time Analytics</strong> - Track performance, popular items, revenue</li>
            <li><strong>🌍 Multi-language Support</strong> - Perfect for international guests</li>
            <li><strong>💳 Integrated Payments</strong> - Seamless checkout with tips</li>
        </ul>
        
        <div class="highlight">
            <h3>🎯 Perfect for {hotel_name}:</h3>
            <p>• <strong>No app downloads</strong> - Works instantly via QR codes<br>
            • <strong>Easy setup</strong> - Ready in 24 hours<br>
            • <strong>Staff training</strong> - Simple dashboard, minimal learning curve<br>
            • <strong>Custom branding</strong> - Matches your hotel's style</p>
        </div>
        
        <p><strong>🎁 Special Launch Offer for {hotel_name}:</strong></p>
        <ul>
            <li>✅ <strong>FREE 15-day trial</strong></li>
            <li>✅ <strong>FREE setup and training</strong></li>
            <li>✅ <strong>FREE custom QR codes for all rooms</strong></li>
        </ul>
        
        <div class="highlight">
            <h3>🎯 Try TableLink Live Demo - Grand Hotel Test:</h3>
            
            <p><strong>🏨 STEP 1: Hotel Management Dashboard</strong><br>
            <a href="https://tablelink.space/r/grand-hotel-test/business/login">https://tablelink.space/r/grand-hotel-test/business/login</a><br>
            Username: <code>hoteladmin</code> | Password: <code>hotel123</code><br>
            <em>→ Click login, view orders, manage menu, see analytics</em></p>
            
            <p><strong>📱 STEP 2: Guest Room Service Experience</strong><br>
            <a href="https://tablelink.space/r/grand-hotel-test/table/101">https://tablelink.space/r/grand-hotel-test/table/101</a><br>
            <em>→ Browse menu, add items, customize orders, checkout with tip</em></p>
            
            <p><strong>🔄 STEP 3: See Orders in Real-Time</strong><br>
            After placing guest order, refresh hotel dashboard to see it appear instantly!</p>
        </div>
        
        <center>
            <a href="https://tablelink.space/r/grand-hotel-test/business/login" class="cta">🚀 Login to Hotel Dashboard</a>
        </center>
        
        <p><strong>How to test:</strong> Open both links in separate tabs. Place an order as a guest (Room 101), then switch to hotel dashboard to see the order appear in real-time. Process the order and see the complete workflow!</p>
        
        <p>I'd love to show you how TableLink can enhance {hotel_name}'s guest experience and boost your room service revenue.</p>
        
        <p><strong>Available for a quick 15-minute call this week?</strong></p>
        
        <p>Best regards,<br>
        <strong>The TableLink Team</strong><br>
        📧 lens.ordr@gmail.com<br>
        📱 +34 617867354<br>
        🌐 <a href="https://tablelink.space">tablelink.space</a></p>
        
        <p><em>P.S. We're currently onboarding select Barcelona hotels. {hotel_name} would be a perfect fit for our premium service.</em></p>
    </div>
    
    <div class="footer">
        <p>TableLink - Digital Ordering Platform<br>
        Barcelona, Spain | <a href="mailto:lens.ordr@gmail.com">lens.ordr@gmail.com</a></p>
        <p><small>This email was sent to promote TableLink's room service solution. Reply STOP to unsubscribe.</small></p>
    </div>
</body>
</html>
        """
        
        return subject, html_body

    def send_email(self, to_email, hotel_name):
        """Send personalized email to hotel"""
        try:
            subject, html_body = self.create_email_template(hotel_name)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Cc'] = self.sender_email  # CC yourself to track sent emails
            msg['Subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send to {to_email}: {e}")
            return False

    def send_campaign(self, csv_file='barcelona_hotels_emails.csv', delay=30, limit=50):
        """Send email campaign to all hotels in CSV with tracking"""
        
        print("📧 TableLink Hotel Email Campaign")
        print("=" * 40)
        
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            print(f"💡 First run: python scrape_hotels_places_only.py")
            return
        
        # Read hotel data from CSV
        hotels = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            if 'Sent' not in fieldnames:
                fieldnames.append('Sent')
            
            for row in reader:
                hotels.append({
                    'name': row['Hotel Name'],
                    'email': row['Email'],
                    'website': row.get('Website', ''),
                    'rating': row.get('Rating', ''),
                    'sent': (row.get('Sent') or '').lower() == 'yes'
                })
        
        # Filter unsent emails and remove duplicates
        unique_hotels = {}
        for hotel in hotels:
            email = hotel['email'].lower()
            if email not in unique_hotels and not hotel['sent']:
                unique_hotels[email] = hotel
        
        unsent_hotels = list(unique_hotels.values())[:limit]
        print(f"📊 Found {len(unsent_hotels)} unsent emails (limit: {limit})")
        
        # Send emails and track results
        sent_count = 0
        failed_count = 0
        sent_emails = set()
        
        for i, hotel in enumerate(unsent_hotels, 1):
            print(f"[{i}/{len(unsent_hotels)}] Sending to {hotel['name']}")
            print(f"  📧 {hotel['email']}")
            
            success = self.send_email(hotel['email'], hotel['name'])
            
            if success:
                sent_count += 1
                sent_emails.add(hotel['email'].lower())
                print(f"  ✅ Sent successfully")
            else:
                failed_count += 1
                print(f"  ❌ Failed to send")
            
            if i < len(unsent_hotels):
                print(f"  ⏳ Waiting {delay} seconds...")
                time.sleep(delay)
        
        # Update CSV with sent status
        self.update_csv_sent_status(csv_file, sent_emails)
        
        print(f"\n📊 CAMPAIGN SUMMARY:")
        print(f"✅ Sent: {sent_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📧 Processed: {len(unsent_hotels)}")
        print(f"📝 CSV updated with sent status")
    
    def update_csv_sent_status(self, csv_file, sent_emails):
        """Update CSV to mark sent emails"""
        rows = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = list(reader.fieldnames)
            if 'Sent' not in fieldnames:
                fieldnames.append('Sent')
            
            for row in reader:
                if row['Email'].lower() in sent_emails:
                    row['Sent'] = 'Yes'
                elif 'Sent' not in row:
                    row['Sent'] = 'No'
                rows.append(row)
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

def main():
    print("🏨 TableLink Hotel Email Campaign")
    print("=" * 40)
    
    sender = HotelEmailSender()
    
    # Check credentials
    if 'your-email' in sender.sender_email:
        print("⚠️  Please set your Gmail credentials:")
        print("export SENDER_EMAIL='your-gmail@gmail.com'")
        print("export SENDER_APP_PASSWORD='your-16-char-app-password'")
        print("\n📝 Setup Gmail App Password:")
        print("1. Go to Google Account settings")
        print("2. Security > 2-Step Verification > App passwords")
        print("3. Generate password for 'Mail'")
        return
    
    # Confirm before sending
    response = input("🚀 Ready to send TableLink campaign? (y/N): ")
    if response.lower() != 'y':
        print("Campaign cancelled.")
        return
    
    # Send campaign (50 email limit)
    sender.send_campaign(limit=50)

if __name__ == "__main__":
    main()