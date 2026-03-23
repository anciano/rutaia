
import sys
import os
sys.path.append(os.getcwd())

print("Checking imports...")
try:
    from app.models.plan_item import PlanItem
    print("PlanItem imported")
    from app.models.day import PlanDay
    print("PlanDay imported")
    from app.routes.plan_detalle import router
    print("Router imported")
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
