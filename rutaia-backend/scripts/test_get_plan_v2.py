
import requests
import json

# Use the plan ID from previous logs (reproduce_422.py) which was:
# d2e0cd37-7843-45cb-af72-253053e0ae5b
plan_id = "d2e0cd37-7843-45cb-af72-253053e0ae5b"
url = f"http://localhost:8000/plan/v2/{plan_id}"

print(f"GET {url}")
try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        days = data.get("days", [])
        print(f"Total Days in Response: {len(days)}")
        print(json.dumps(days, indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(e)
