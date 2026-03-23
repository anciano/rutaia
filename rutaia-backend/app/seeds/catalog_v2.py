# rutaia-backend/app/seeds/catalog_v2.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.models.database import SessionLocal
from app.models.catalog_category import CatalogCategory
from app.models.catalog_item import CatalogItem
from app.models.catalog_transport_segment import CatalogTransportSegment

def seed_catalog_v2():
    db = SessionLocal()
    try:
        print("🌱 Sembrando Catálogo v2...")
        
        # 1. Categorías Base
        cats = [
            {"name": "Glaciares"},
            {"name": "Parques Nacionales"},
            {"name": "Restaurantes"},
            {"name": "Gasolineras"},
            {"name": "Buses"},
            {"name": "Campings"},
        ]
        
        cat_map = {}
        for c in cats:
            existing = db.query(CatalogCategory).filter_by(name=c["name"]).first()
            if not existing:
                new_cat = CatalogCategory(name=c["name"])
                db.add(new_cat)
                db.flush()
                cat_map[c["name"]] = new_cat.id
            else:
                cat_map[c["name"]] = existing.id

        # 2. Lugares de Interés
        lps = [
            {
                "item_type": "place",
                "name": "Glaciar Grey",
                "description": "Impresionante glaciar en el PN Torres del Paine",
                "category_id": cat_map["Glaciares"],
                "lat": -51.045, "lng": -73.155,
                "extra": {"place_subtype": "interest"}
            },
            {
                "item_type": "place",
                "name": "Coyhaique Centro",
                "description": "Hub principal de la región",
                "lat": -45.5752, "lng": -72.0662,
                "extra": {"place_subtype": "interest"}
            },
            {
                "item_type": "place",
                "name": "Puyuhuapi Pueblo",
                "description": "Famoso por sus termas y ventisquero",
                "lat": -44.3275, "lng": -72.5644,
                "extra": {"place_subtype": "interest"}
            }
        ]
        
        item_map = {}
        for lp in lps:
            item = db.query(CatalogItem).filter_by(name=lp["name"]).first()
            if not item:
                item = CatalogItem(**lp)
                db.add(item)
                db.flush()
            item_map[lp["name"]] = item.id

        # 3. Servicios (Lugar de Apoyo)
        servs = [
            {
                "item_type": "place",
                "name": "Copec Coyhaique",
                "description": "Combustible y servicios 24h",
                "category_id": cat_map["Gasolineras"],
                "lat": -45.571, "lng": -72.068,
                "extra": {"place_subtype": "service"}
            }
        ]
        for s in servs:
            if not db.query(CatalogItem).filter_by(name=s["name"]).first():
                db.add(CatalogItem(**s))

        # 4. Transporte con Segmentos
        bus = db.query(CatalogItem).filter_by(name="Bus Regional Aysén").first()
        if not bus:
            bus = CatalogItem(
                item_type="transport",
                name="Bus Regional Aysén",
                description="Servicio diario norte-sur",
                category_id=cat_map["Buses"],
                is_active=True
            )
            db.add(bus)
            db.flush()
        
        # Segmentos
        segments = [
            {
                "transport_id": bus.id,
                "origin_id": item_map["Coyhaique Centro"],
                "destination_id": item_map["Puyuhuapi Pueblo"],
                "price_clp": 15000,
                "duration_minutes": 240,
                "frequency": "Diario 08:00"
            }
        ]
        for seg_data in segments:
            # Check if segment exists (approx check)
            exists = db.query(CatalogTransportSegment).filter_by(
                transport_id=seg_data["transport_id"],
                origin_id=seg_data["origin_id"],
                destination_id=seg_data["destination_id"]
            ).first()
            if not exists:
                db.add(CatalogTransportSegment(**seg_data))

        db.commit()
        print("✅ Catálogo v2 sembrado con éxito.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error sembrando: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_catalog_v2()
