
import requests

url = "http://localhost:8000/plan/d2e0cd37-7843-45cb-af72-253053e0ae5b/days"
print(f"POST {url}")
try:
    response = requests.post(url)
    print(f"Status: {response.status_code}")
    try:
        print(f"Body: {response.json()}")
    except:
        print(f"Text: {response.text}")
except Exception as e:
    print(e)
