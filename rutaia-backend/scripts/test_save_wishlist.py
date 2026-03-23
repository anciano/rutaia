from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.plan_item import PlanItem
from app.models.day import PlanDay
from app.models.user_plan import UserPlan
from app.models.catalog_item import CatalogItem
import logging

def test_create_item():
    db = SessionLocal()
    try:
        # Get a plan ID
        plan = db.query(UserPlan).first()
        if not plan:
            print("No plan found in DB")
            return
        
        # Get a catalog item ID
        cat_item = db.query(CatalogItem).first()
        if not cat_item:
            print("No catalog item found in DB. Please run seed first.")
            return
            
        print(f"Testing with plan_id: {plan.id}, catalog_item_id: {cat_item.id}")
        
        # Test Payload matching frontend wishlist save
        item_data = {
            "plan_id": str(plan.id),
            "day_id": None,
            "item_type": "place",
            "catalog_item_id": cat_item.id,
            "sort_order": 0,
            "cost_clp": 0,
            "metadata_json": {"name": f"Test {cat_item.name}"}
        }
        
        print(f"Attempting to create item: {item_data}")
        new_item = PlanItem(**item_data)
        db.add(new_item)
        db.commit()
        print("SUCCESS: Item created with catalog_item_id")
        
        # Cleanup
        db.delete(new_item)
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"DATABASE ERROR: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_create_item()
