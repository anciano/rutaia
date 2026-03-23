# scripts/seed_aysen_services.py
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.database import SessionLocal
from app.models.catalog_item import CatalogItem
from app.models.catalog_category import CatalogCategory

def seed_aysen_services():
    db: Session = SessionLocal()
    try:
        # Helper to find category by name
        def get_cat_id(name):
            cat = db.query(CatalogCategory).filter_by(name=name).first()
            return cat.id if cat else None

        # Critical services to seed
        services = [
            # COYHAIQUE
            {
                "name": "Hospital Regional Coyhaique",
                "category": "Hospital",
                "lat": -45.5745, "lng": -72.0620,
                "extra": {"service_code": "hospital", "is_critical": True, "phone": "+56 67 226 2000", "emergency_24h": True}
            },
            {
                "name": "Copec Coyhaique",
                "category": "Gasolinera",
                "lat": -45.5720, "lng": -72.0710,
                "extra": {"service_code": "gas_station", "fuel_types": ["93", "95", "97", "Diesel"]}
            },
            {
                "name": "Banco Estado Coyhaique",
                "category": "Banco",
                "lat": -45.5705, "lng": -72.0680,
                "extra": {"service_code": "bank", "withdrawal_limit": 400000}
            },
            
            # PUERTO RÍO TRANQUILO
            {
                "name": "Posta de Salud Rural Río Tranquilo",
                "category": "Posta de Salud Rural",
                "lat": -46.6235, "lng": -72.6720,
                "extra": {"service_code": "rural_health_post", "is_critical": True, "emergency_24h": True}
            },
            {
                "name": "Punto de Combustible Tranquilo",
                "category": "Punto de Combustible Rural",
                "lat": -46.6220, "lng": -72.6700,
                "extra": {"service_code": "rural_fuel_point", "fuel_types": ["95", "Diesel"]}
            },
            
            # COCHRANE
            {
                "name": "Hospital de Cochrane",
                "category": "Hospital",
                "lat": -47.2555, "lng": -72.5680,
                "extra": {"service_code": "hospital", "is_critical": True, "emergency_24h": True, "ambulance": True}
            },
            {
                "name": "Supermercado El Arriero Cochrane",
                "category": "Supermercado",
                "lat": -47.2540, "lng": -72.5710,
                "extra": {"service_code": "supermarket"}
            },
            {
                "name": "Terminal de Buses Cochrane",
                "category": "Terminal de Buses",
                "lat": -47.2560, "lng": -72.5730,
                "extra": {"service_code": "bus_terminal"}
            },

            # VILLA O'HIGGINS
            {
                "name": "Posta Villa O'Higgins",
                "category": "Posta de Salud Rural",
                "lat": -48.4675, "lng": -72.5510,
                "extra": {"service_code": "rural_health_post", "is_critical": True}
            },
            {
                "name": "Rampa Villa O'Higgins (Ferry)",
                "category": "Terminal de Ferry / Rampa",
                "lat": -48.5130, "lng": -72.5350,
                "extra": {"service_code": "ferry_terminal"}
            }
        ]

        for s in services:
            cat_id = get_cat_id(s["category"])
            if not cat_id:
                print(f"Skipping {s['name']}, category '{s['category']}' not found.")
                continue
            
            # Check if exists
            exists = db.query(CatalogItem).filter_by(name=s["name"]).first()
            if not exists:
                svc = CatalogItem(
                    item_type="place",
                    name=s["name"],
                    category_id=cat_id,
                    lat=s["lat"],
                    lng=s["lng"],
                    extra={**s["extra"], "place_subtype": "service"}
                )
                db.add(svc)
        
        db.commit()
        print("Aysén Level 1 services seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding services: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_aysen_services()
