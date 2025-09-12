import qrcode
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def generate_table_qr_codes():
    """Generate QR codes for all tables"""
    local_ip = get_local_ip()
    port = 8001
    
    for table_num in range(1, 11):
        url = f"http://{local_ip}:{port}/client?table={table_num}"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        filename = f"table_{table_num}_qr.png"
        img.save(filename)
        print(f"Generated QR code for Table {table_num}: {filename}")
        print(f"URL: {url}")
        print("-" * 50)

if __name__ == "__main__":
    print("Generating QR codes for restaurant tables...")
    print(f"Local IP: {get_local_ip()}")
    print("=" * 50)
    generate_table_qr_codes()
    print("QR codes generated successfully!")