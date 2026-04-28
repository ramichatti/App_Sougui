#!/usr/bin/env python
"""Check if backend is running with latest code"""
import requests
import json

try:
    # Test forgot password endpoint with correct email
    response = requests.post(
        'http://localhost:5000/api/auth/forgot-password',
        json={'email': 'ramichatti14@gmail.com'},
        headers={'Content-Type': 'application/json'}
    )
    
    print("=" * 60)
    print("Backend Response Check")
    print("=" * 60)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("=" * 60)
    
    if response.status_code == 200:
        data = response.json()
        if 'debug_code' in data:
            print("✅ Backend has latest code!")
            print(f"🔢 Debug Code: {data['debug_code']}")
            print("\nNow check:")
            print("1. Backend terminal for the code")
            print("2. Gmail inbox: ramichatti14@gmail.com")
        else:
            print("⚠️ Backend needs restart - debug_code not in response")
            print("\nRestart backend:")
            print("1. Stop with Ctrl+C")
            print("2. Run: python app.py")
    else:
        print("❌ Error:", response.json())
        
except requests.exceptions.ConnectionError:
    print("❌ Backend is not running!")
    print("Start it with: python app.py")
except Exception as e:
    print(f"❌ Error: {str(e)}")
