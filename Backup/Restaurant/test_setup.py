import requests
import time
import subprocess
import sys

def test_setup_route():
    try:
        # Test if server is running
        response = requests.get("http://localhost:8000/setup", timeout=5)
        print(f"Setup route status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Setup route is working!")
            print("Content preview:", response.text[:200])
        else:
            print(f"❌ Setup route returned {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_setup_route()