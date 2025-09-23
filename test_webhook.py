#!/usr/bin/env python3
"""
Test script for Square webhook
Run this to simulate a Square payment webhook
"""

import requests
import json

# Test webhook payload (simulates Square payment.created event)
webhook_payload = {
    "type": "payment.created",
    "data": {
        "object": {
            "buyer_email_address": "test@example.com",
            "amount_money": {
                "amount": 4900,  # €49 in cents
                "currency": "EUR"
            },
            "custom_fields": {
                "restaurant_name": "Mario's Pizza",
                "email": "mario@pizza.com",
                "table_count": "15",
                "username": "mario",
                "password": "pizza123"
            }
        }
    }
}

def test_webhook():
    url = "http://localhost:8000/webhooks/square"
    
    try:
        response = requests.post(
            url,
            json=webhook_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Square webhook...")
    test_webhook()