# debug_api.py
import os, sys
sys.path.insert(0, os.getcwd())

from app.models.database import SessionLocal
from app.models.catalog_item import CatalogItem
from app.routes.admin import _enrich_item_read
from app.schemas.catalog import CatalogItemRead

from pydantic import ValidationError

def test_list():
    db = SessionLocal()
    try:
        items = db.query(CatalogItem).all()
        print(f"Found {len(items)} items.")
        for item in items:
            try:
                # This mirrors the API logic
                read = _enrich_item_read(item, db)
            except ValidationError as e:
                print(f"\n❌ VALIDATION ERROR in item: {item.name} (ID: {item.id}, Type: {item.item_type})")
                print(e)
                break # Just see the first one
            except Exception as e:
                print(f"\n❌ OTHER ERROR in item: {item.name}: {e}")
                break
    finally:
        db.close()

if __name__ == "__main__":
    test_list()
