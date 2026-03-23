# scripts/analyze_towns.py
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def analyze():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("--- CIUDADES (Legacy) ---")
        res = conn.execute(text("SELECT id, nombre, region FROM ciudades"))
        for row in res:
            print(f"ID: {row[0]} | Name: {row[1]} | Region: {row[2]}")
            
        print("\n--- CATALOG ITEMS (Potential Localities) ---")
        # Find items that look like towns/cities in metadata or name
        res = conn.execute(text("""
            SELECT id, name, extra->>'place_subtype' as subtype, lat, lng 
            FROM catalog_items 
            WHERE item_type = 'place' 
              AND (extra->>'place_subtype' IN ('town', 'city', 'village') 
                   OR name ILIKE 'Puerto%' 
                   OR name ILIKE 'Villa%' 
                   OR name ILIKE 'Caleta%')
        """))
        for row in res:
            print(f"ID: {row[0]} | Name: {row[1]} | Subtype: {row[2]} | Lat: {row[3]} | Lng: {row[4]}")

if __name__ == "__main__":
    analyze()
