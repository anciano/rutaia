# scripts/update_tables_v4.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.database import engine, Base
from app.models.catalog_transport_segment import CatalogTransportSegment
from sqlalchemy import text

def update():
    with engine.connect() as conn:
        print("🔍 Comprobando columna 'schedule' en 'catalog_transport_segments'...")
        # Check if column exists
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='catalog_transport_segments' AND column_name='schedule'"))
        if not res.fetchone():
            print("🚀 Agregando columna 'schedule'...")
            conn.execute(text("ALTER TABLE catalog_transport_segments ADD COLUMN schedule JSONB"))
            conn.commit()
            print("✅ Columna agregada.")
        else:
            print("✨ La columna ya existe.")

if __name__ == "__main__":
    update()
