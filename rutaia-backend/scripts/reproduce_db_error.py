
print("hello world")
import sys
import os
sys.path.append(os.getcwd())

from app.models.database import SessionLocal
from app.models.user_plan import UserPlan
from app.models.day import PlanDay
from app.schemas.plan_detail import UserPlanResponseV2

def test_relationship():
    print("Testing relationship...")
    db = SessionLocal()
    # Plan ID from reproduce_422.py
    plan_id = "d2e0cd37-7843-45cb-af72-253053e0ae5b"
    print(f"Plan ID: {plan_id}")
    
    plan = db.get(UserPlan, plan_id)
    if not plan:
        print("Plan not found")
        return
        
    print(f"Plan Found: {plan.id}")
    print(f"Accessing days...")
    try:
        days = plan.days
        print(f"Days: {len(days)}")
        for d in days:
            print(f"- Day {d.number}: {len(d.items)} items")
            
        print("Attempting Pydantic validation...")
        try:
            # Manually trigger Pydantic
            # We need to populate ciudad_nombre manually as in route
            from app.models.ciudad import Ciudad
            ciudad = db.get(Ciudad, plan.origen_id)
            if ciudad:
                plan.ciudad_nombre = ciudad.nombre
            
            resp = UserPlanResponseV2.model_validate(plan)
            print("Validation successful")
        except Exception as e:
            print(f"Validation Error: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"Relationship Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_relationship()
