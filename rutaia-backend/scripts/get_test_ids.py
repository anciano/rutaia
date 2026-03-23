from app.models.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    row = conn.execute(text("SELECT id, origen_id FROM user_plans LIMIT 1")).fetchone()
    if row:
        print(f"PLAN_ID={row[0]}")
        print(f"CITY_ID={row[1]}")
    else:
        print("NO_PLANS_FOUND")
