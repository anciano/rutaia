# scripts/test_registry_v2.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import Base
print("Current registry keys (Pre-models):", list(Base.registry._class_registry.keys()))

import app.models.day as day
print("Current registry keys (After Day):", list(Base.registry._class_registry.keys()))

import app.models.user_plan as user_plan
print("Current registry keys (After UserPlan):", list(Base.registry._class_registry.keys()))

from sqlalchemy.orm import configure_mappers
try:
    configure_mappers()
    print("Mappers configured successfully!")
except Exception as e:
    print(f"FAILED: {e}")
