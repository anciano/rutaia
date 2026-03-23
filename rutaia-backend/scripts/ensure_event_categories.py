# scripts/ensure_event_categories.py
import sys
import os

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.database import SessionLocal
from app.models.catalog_category import CatalogCategory
from app.models.catalog_item import CatalogItem
from app.models.catalog_transport_segment import CatalogTransportSegment
from app.models.catalog_event import CatalogEvent
from app.models.destination_profile import DestinationProfile
from app.models.item_link import ItemLink

def ensure_categories():
    db = SessionLocal()
    try:
        # Check if Agenda Local exists
        root = db.query(CatalogCategory).filter_by(name="Agenda Local", parent_id=None).first()
        if not root:
            root = CatalogCategory(name="Agenda Local", icon="pi-calendar")
            db.add(root)
            db.commit()
            db.refresh(root)
            print(f"Created root category: {root.name}")
        else:
            print(f"Root category {root.name} already exists.")

        # Ensure some subcategories
        subs = ["Feria Costumbrista", "Mercado Local", "Festival / Concierto", "Actividad Deportiva"]
        for s_name in subs:
            exists = db.query(CatalogCategory).filter_by(name=s_name, parent_id=root.id).first()
            if not exists:
                s = CatalogCategory(name=s_name, parent_id=root.id)
                db.add(s)
                print(f"Created subcategory: {s_name}")
        
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ensure_categories()
