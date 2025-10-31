#!/usr/bin/env python3
"""
Generate offline QR codes with restaurant's local IP
"""

def generate_offline_qr_codes(restaurant_subdomain, local_ip):
    """Generate QR codes that work offline with specific local IP"""
    
    qr_codes = []
    for table_num in range(1, 11):
        # Create dual-URL QR code
        online_url = f"https://tablelink.space/r/{restaurant_subdomain}/table/{table_num}"
        offline_url = f"http://{local_ip}:8000/r/{restaurant_subdomain}/table/{table_num}"
        
        # Smart URL that tries both
        smart_url = f"https://tablelink.space/connect/{restaurant_subdomain}/table/{table_num}?local_ip={local_ip}"
        
        qr_codes.append({
            'table': table_num,
            'online_url': online_url,
            'offline_url': offline_url,
            'smart_url': smart_url
        })
    
    return qr_codes

# Example usage
if __name__ == "__main__":
    # Restaurant owner provides their local IP
    restaurant_ip = input("Enter your restaurant's local IP (e.g., 192.168.1.100): ")
    subdomain = input("Enter restaurant subdomain: ")
    
    qr_codes = generate_offline_qr_codes(subdomain, restaurant_ip)
    
    print(f"\n📱 QR Codes for {subdomain}:")
    for qr in qr_codes:
        print(f"Table {qr['table']}: {qr['smart_url']}")