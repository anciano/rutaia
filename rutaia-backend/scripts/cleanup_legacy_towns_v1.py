# scripts/cleanup_legacy_towns_v1.py
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def cleanup():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Starting legacy town cleanup...")
        
        # Identify items that are already localities
        # Rules: 
        # 1. Items with name ILIKE '%Pueblo%' or '%Centro%' that are now linked to a locality
        # 2. Deactivate them so they don't clutter the resource list as 'interest' points
        
        res = conn.execute(text("""
            UPDATE catalog_items 
            SET is_active = FALSE 
            WHERE id IN (
                SELECT ci.id 
                FROM catalog_items ci
                JOIN localities l ON ci.locality_id = l.id
                WHERE ci.name ILIKE l.name || '%'
                  AND ci.item_type = 'place'
                  AND (ci.extra->>'place_subtype' = 'town' OR ci.name ILIKE '%Pueblo%' OR ci.name ILIKE '%Centro%')
            )
            RETURNING id, name
        """))
        
        for row in res:
            print(f"Deactivated legacy item: {row[1]} (ID: {row[0]})")
            
        conn.commit()
        print("Cleanup completed.")

if __name__ == "__main__":
    cleanup()
