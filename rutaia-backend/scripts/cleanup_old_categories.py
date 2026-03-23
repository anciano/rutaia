# scripts/cleanup_old_categories.py
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.database import SessionLocal
from app.models.catalog_category import CatalogCategory
from app.models.catalog_item import CatalogItem

def cleanup():
    db: Session = SessionLocal()
    try:
        # First, find the root categories to delete
        roots = db.query(CatalogCategory).filter(CatalogCategory.name.in_(["Servicios", "Infraestructura"])).all()
        
        for root in roots:
            print(f"Cleaning up {root.name} and its descendants...")
            # We need to handle this recursively or just delete and let the DB handle it if CASCADE is set.
            # But CatalogItem depends on categories. If an item uses a category we're deleting, 
            # we should probably set its category_id to NULL.
            
            # 1. Get all descendant IDs
            descendant_ids = []
            groups = db.query(CatalogCategory).filter_by(parent_id=root.id).all()
            for g in groups:
                cats = db.query(CatalogCategory).filter_by(parent_id=g.id).all()
                descendant_ids.extend([c.id for c in cats])
                descendant_ids.append(g.id)
            descendant_ids.append(root.id)
            
            # 2. Nullify CatalogItem category_ids
            db.query(CatalogItem).filter(CatalogItem.category_id.in_(descendant_ids)).update({CatalogItem.category_id: None}, synchronize_session=False)
            
            # 3. Delete categories (starting from children)
            for g in groups:
                db.query(CatalogCategory).filter_by(parent_id=g.id).delete()
            db.query(CatalogCategory).filter_by(parent_id=root.id).delete()
            db.delete(root)
            
        db.commit()
        print("Cleanup successful.")
    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
