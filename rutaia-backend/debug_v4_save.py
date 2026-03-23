# debug_v4_save.py
import os, sys
sys.path.insert(0, os.getcwd())

from app.models.database import SessionLocal
from app.models.catalog_item import CatalogItem
from app.models.catalog_transport_segment import CatalogTransportSegment
from app.schemas.catalog import CatalogItemCreate, TransportSegmentCreate

def test_save_schedule():
    db = SessionLocal()
    try:
        # 1. Buscar o crear item de transporte "Bus Suray"
        bus = db.query(CatalogItem).filter_by(name="Bus Suray").first()
        if not bus:
            bus = CatalogItem(
                name="Bus Suray",
                item_type="transport",
                description="Prueba Suray",
                is_active=True
            )
            db.add(bus)
            db.flush()
        
        # 2. Add a segment with schedule
        schedule_data = {
            "weekday": ["06:50", "07:30", "08:30"],
            "saturday": ["08:30", "09:50"],
            "sunday_holiday": ["08:40"]
        }
        
        segment = CatalogTransportSegment(
            transport_id=bus.id,
            origin_id=None, # Just for test
            destination_id=None,
            price_clp=5000,
            duration_minutes=60,
            schedule=schedule_data
        )
        db.add(segment)
        db.commit()
        
        print(f"✅ Segmento guardado para {bus.name} con ID: {segment.id}")
        
        # 3. Read back
        db.refresh(segment)
        print(f"📋 Horarios leídos: {segment.schedule}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_save_schedule()
