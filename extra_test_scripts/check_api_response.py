import requests
import json

print("\n" + "="*60)
print("API Response Structure Check")
print("="*60)

try:
    r = requests.get('http://localhost:8000/api/properties/list/')
    data = r.json()
    
    print(f"\nStatus Code: {r.status_code}")
    print(f"Response Type: {type(data)}")
    print(f"Is List: {isinstance(data, list)}")
    
    if isinstance(data, dict):
        print(f"Dictionary Keys: {list(data.keys())}")
        if 'results' in data:
            print(f"Results count: {len(data['results'])}")
            print(f"\nFirst property:")
            print(json.dumps(data['results'][0], indent=2))
        else:
            print("\n⚠ No 'results' key found in response!")
    elif isinstance(data, list):
        print(f"List length: {len(data)}")
        if len(data) > 0:
            print(f"\nFirst property:")
            print(json.dumps(data[0], indent=2))
    
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*60 + "\n")
