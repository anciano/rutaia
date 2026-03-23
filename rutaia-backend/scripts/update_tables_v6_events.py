# scripts/update_tables_v6_events.py
import sys
import os
from sqlalchemy import text

# Add the project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.database import engine, Base
from app.models.catalog_item import CatalogItem
from app.models.catalog_category import CatalogCategory
from app.models.catalog_event import CatalogEvent  # New model

def update_database():
    print("Updating database to support events...")
    
    with engine.begin() as conn:
        # 1. Update the ENUM type for catalog_item_type if it exists
        print("Checking catalog_item_type enum...")
        try:
            conn.execute(text("ALTER TYPE catalog_item_type ADD VALUE 'event'"))
            print("Added 'event' to catalog_item_type enum.")
        except Exception as e:
            # If it already exists, PostgreSQL will raise an error
            print(f"Note: Enum update might have already been done or skipped: {e}")

        # 2. Create the new catalog_events table
        print("Creating catalog_events table...")
        CatalogEvent.__table__.create(conn, checkfirst=True)
        print("Table catalog_events created or already exists.")

    print("Database update complete.")

if __name__ == "__main__":
    update_database()
