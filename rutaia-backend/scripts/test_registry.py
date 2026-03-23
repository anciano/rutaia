# scripts/test_registry.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import Base
from app.models.day import PlanDay
from app.models.user_plan import UserPlan
from sqlalchemy.orm import configure_mappers

print("Base registry classes:", Base.registry._class_registry.keys())
try:
    configure_mappers()
    print("Mappers configured successfully!")
except Exception as e:
    print(f"FAILED: {e}")
