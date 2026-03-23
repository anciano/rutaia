# scripts/fix_duplicates.py
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
with engine.begin() as conn:
    # Merge Villa O'Higgins
    conn.execute(text("UPDATE catalog_items SET locality_id = 18 WHERE locality_id = 152"))
    conn.execute(text("DELETE FROM localities WHERE id = 152"))
    print("Cleaned up Villa O'Higgins duplicate.")
