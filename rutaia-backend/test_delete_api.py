import sys
import uuid
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import SessionLocal
from app.models.plan_item import PlanItem

client = TestClient(app)
db = SessionLocal()
item = db.query(PlanItem).first()
if item:
    # app/main.py Includes plan_detalle_router with prefix "/api/v1" or whatever is configured.
    # Typically it's /api/v1/plan or just /plan. Let's look at main.py or just use the router path.
    # The route is @router.delete("/{plan_id}/unified/items/{item_id}") under prefix "/plan".
    # Assume main.py mounts it on /api/v1. Actually we can print all routes.
    
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    delete_route = next((r for r in routes if 'unified/items' in r and 'DELETE' in [m for rt in app.routes if getattr(rt, 'path', '') == r for m in getattr(rt, 'methods', [])]), None)
    
    url = f"/api/v1/plan/{item.plan_id}/unified/items/{item.id}"
    print(f"Testing DELETE {url}")
    response = client.delete(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    url2 = f"/plan/{item.plan_id}/unified/items/{item.id}"
    print(f"Testing DELETE {url2}")
    response2 = client.delete(url2)
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text}")
else:
    print("No items to test")
