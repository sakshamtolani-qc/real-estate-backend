#!/usr/bin/env python
import requests
import json

print("\n" + "="*60)
print("API Images Test")
print("="*60)

try:
    # Test the properties list API
    response = requests.get('http://localhost:8000/api/properties/list/')
    
    if response.status_code == 200:
        data = response.json()
        properties = data if isinstance(data, list) else data.get('results', [])
        
        print(f"\n✓ API Response: {response.status_code} OK")
        print(f"✓ Properties returned: {len(properties)}")
        
        # Check first few properties for images
        print("\nFirst 3 properties:")
        for i, prop in enumerate(properties[:3]):
            print(f"\n  {i+1}. {prop.get('title', 'No title')}")
            print(f"     Image: {prop.get('image', 'No image')}")
            print(f"     Location: {prop.get('location', 'No location')}")
            print(f"     Price: {prop.get('price', 'No price')}")
            
    else:
        print(f"\n✗ API Error: {response.status_code}")
        print(f"  Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n✗ Connection Error: Make sure Django server is running")
    print("  Run: python manage.py runserver")

except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*60 + "\n")
