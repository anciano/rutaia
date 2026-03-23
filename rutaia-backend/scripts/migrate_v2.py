# scripts/migrate_v2.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.database import Base, engine
# Import all models to ensure they are registered with Base.metadata
from app.models.catalog_category import CatalogCategory
from app.models.catalog_item import CatalogItem
from app.models.catalog_transport_segment import CatalogTransportSegment
from app.models.item_link import ItemLink

def migrate():
    print("🚀 Creando nuevas tablas para el catálogo v2...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas.")

if __name__ == "__main__":
    migrate()
