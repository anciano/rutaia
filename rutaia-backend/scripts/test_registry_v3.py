# scripts/test_registry_v3.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import configure_mappers
from app.models.database import Base

print("Importing models...")
import app.models as models

print("Registry keys:", sorted(list(Base.registry._class_registry.keys())))

try:
    print("Configuring mappers...")
    configure_mappers()
    print("SUCCESS!")
except Exception as e:
    print(f"FAILED: {e}")
    # Inspect the failing class
    if "UserPlan" in Base.registry._class_registry:
        cls = Base.registry._class_registry["UserPlan"]
        print(f"UserPlan class: {cls}")
        # print(f"UserPlan relationships: {cls.__mapper__.relationships.keys()}")
