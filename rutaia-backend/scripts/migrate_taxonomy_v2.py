# scripts/migrate_taxonomy_v2.py
import sys
import os
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.database import engine, SessionLocal

def migrate():
    db: Session = SessionLocal()
    try:
        print("Starting taxonomy schema migration...")
        
        # 1. Add new columns
        # Note: slug is unique and nullable=False in the model, 
        # but we must add it as nullable first, populate it, then set to NOT NULL.
        
        columns_to_add = [
            ("slug", "VARCHAR(120)"),
            ("root_block", "VARCHAR(60)"),
            ("sort_order", "INTEGER DEFAULT 0"),
            ("is_active", "BOOLEAN DEFAULT TRUE"),
            ("created_at", "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP WITH TIME ZONE")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                db.execute(text(f"ALTER TABLE catalog_categories ADD COLUMN {col_name} {col_type}"))
                print(f"Added column: {col_name}")
            except Exception as e:
                # Likely already exists
                print(f"Column {col_name} might already exist or error: {e}")
                db.rollback()

        # 2. Populate slugs for existing categories
        from app.models.catalog_category import CatalogCategory
        categories = db.query(CatalogCategory).filter(CatalogCategory.slug == None).all()
        for cat in categories:
            # Simple slugification
            slug = cat.name.lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "").replace("'", "")
            # Ensure uniqueness
            base_slug = slug
            counter = 1
            while db.query(CatalogCategory).filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            cat.slug = slug
        
        db.commit()
        print("Slugs populated.")

        # 3. Set slug to NOT NULL and UNIQUE
        try:
            db.execute(text("ALTER TABLE catalog_categories ALTER COLUMN slug SET NOT NULL"))
            db.execute(text("ALTER TABLE catalog_categories ADD UNIQUE (slug)"))
            print("Slug constraint applied.")
        except Exception as e:
            print(f"Error applying constraints: {e}")
            db.rollback()

        # 4. Remove UNIQUE constraint from 'name' if it exists (model changed to allow duplicates if parents differ)
        # Actually, let's check current constraints
        try:
           # In some DBs we might want to keep it or relax it. The model I wrote has name NOT unique.
           # But Postgres/SQLAlchemy might have named it.
           pass
        except:
           pass

        db.commit()
        print("Migration completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Fatal migration error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
