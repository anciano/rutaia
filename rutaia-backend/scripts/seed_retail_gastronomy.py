# scripts/seed_retail_gastronomy.py
import sys
import os
import json
from sqlalchemy import text
from decimal import Decimal

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.database import SessionLocal

def seed_retail_gastronomy():
    db = SessionLocal()
    try:
        # 1. Get Categories Mapping
        res = db.execute(text("SELECT id, name FROM catalog_categories"))
        cat_map = {r[1]: r[0] for r in res}

        # 2. Data to seed
        data = [
            # --- COYHAIQUE ---
            {
                "name": "Restaurante Mamma Gaucha", "category": "Restaurante", "lat": -45.5712, "lng": -72.0685,
                "extra": {"address": "Paseo Horn 47", "phone": "+56 67 223 1107", "description_short": "Pizzas artesanales y pastas en el corazón de Coyhaique."}
            },
            {
                "name": "Café de Mayo", "category": "Cafetería", "lat": -45.5698, "lng": -72.0672,
                "extra": {"address": "21 de Mayo 432", "phone": "+56 67 221 1122", "description_short": "Café de especialidad y tortas caseras."}
            },
            {
                "name": "Cervecería D'Olbek", "category": "Cervecería artesanal", "lat": -45.5780, "lng": -72.0615,
                "extra": {"address": "Camino a Baquedano km 1.5", "phone": "+56 67 223 1133", "description_short": "Tradición cervecera belga en la Patagonia."}
            },
            {
                "name": "Supermercado Unimarc Coyhaique", "category": "Supermercado", "lat": -45.5725, "lng": -72.0730,
                "extra": {"address": "Lautaro 450", "phone": "+56 67 223 1144"}
            },
            {
                "name": "Tienda Patagonia Outdoor", "category": "Tienda de Outdoor", "lat": -45.5708, "lng": -72.0690,
                "extra": {"address": "Prat 234", "description_short": "Equipamiento técnico para expediciones."}
            },

            # --- PUERTO RÍO TRANQUILO ---
            {
                "name": "Restaurante La Cuenca", "category": "Restaurante", "lat": -46.6230, "lng": -72.6715,
                "extra": {"address": "Av. Costanera s/n", "description_short": "Comida casera con vista al Lago General Carrera."}
            },
            {
                "name": "Minimarket El Puestero", "category": "Minimarket / Almacén", "lat": -46.6215, "lng": -72.6705,
                "extra": {"address": "Calle Principal", "description_short": "Abastecimiento general para viajeros."}
            },
            {
                "name": "Panadería Don Juan", "category": "Panadería", "lat": -46.6225, "lng": -72.6725,
                "extra": {"address": "Pasaje 1", "description_short": "Pan fresco y empanadas calientes."}
            },

            # --- COCHRANE ---
            {
                "name": "Restaurante El Arriero", "category": "Restaurante", "lat": -47.2545, "lng": -72.5715,
                "extra": {"address": "San Valentín 342", "description_short": "Parrilladas y comida típica patagona."}
            },
            {
                "name": "Almacén Los Canales", "category": "Minimarket / Almacén", "lat": -47.2530, "lng": -72.5700,
                "extra": {"address": "O'Higgins 123", "description_short": "Variedad de productos y provisiones."}
            },

            # --- VILLA O'HIGGINS ---
            {
                "name": "Café El Pantano", "category": "Cafetería", "lat": -48.4680, "lng": -72.5520,
                "extra": {"address": "Lago Christie s/n", "description_short": "Un oasis de calidez al final de la carretera."}
            },
            {
                "name": "Supermercado Las Nieves", "category": "Supermercado", "lat": -48.4665, "lng": -72.5505,
                "extra": {"address": "Calle Principal", "description_short": "El supermercado más austral de la región."}
            },

            # --- CALETA TORTEL ---
            {
                "name": "Restaurante Sabores del Baker", "category": "Restaurante", "lat": -47.7960, "lng": -73.5340,
                "extra": {"address": "Pasarela Sector Playa", "description_short": "Gastronomía local basada en productos del mar."}
            }
        ]

        count = 0
        for item in data:
            cat_id = cat_map.get(item["category"])
            if not cat_id:
                print(f"Skipping {item['name']}, category '{item['category']}' not found.")
                continue
            
            # Check if exists (using raw SQL)
            res = db.execute(text("SELECT id FROM catalog_items WHERE name = :name"), {"name": item["name"]}).first()
            if not res:
                # Insert using raw SQL
                extra_json = json.dumps({**item["extra"], "place_subtype": "service"})
                db.execute(text("""
                    INSERT INTO catalog_items (item_type, name, category_id, lat, lng, extra, is_active)
                    VALUES ('place', :name, :cat_id, :lat, :lng, :extra, true)
                """), {
                    "name": item["name"],
                    "cat_id": cat_id,
                    "lat": item["lat"],
                    "lng": item["lng"],
                    "extra": extra_json
                })
                count += 1
        
        db.commit()
        print(f"Successfully seeded {count} retail and gastronomy items via SQL.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_retail_gastronomy()
