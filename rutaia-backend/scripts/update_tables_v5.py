# scripts/update_tables_v5.py
import os
import sys

# Agrega la ruta base del proyecto para poder importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.database import engine, Base
# Ensures all models are imported so their tables are registered with Base.metadata
from app.models.catalog_category import CatalogCategory
from app.models.catalog_item import CatalogItem
from app.models.item_link import ItemLink
from app.models.catalog_transport_segment import CatalogTransportSegment
from app.models.destination_profile import DestinationProfile

def create_destination_profiles_table():
    print("Creating destination_profiles table if it does not exist...")
    # This will create any missing tables that are defined in Base.metadata
    Base.metadata.create_all(bind=engine)
    print("Table synchronization completed.")

if __name__ == "__main__":
    create_destination_profiles_table()
