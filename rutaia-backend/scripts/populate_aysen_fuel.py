# scripts/populate_aysen_fuel.py
import os
import sys
import json
from sqlalchemy import create_engine, text
from slugify import slugify
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Categories Mapping (IDs found previously)
CAT_GASOLINERA = 206
CAT_FUEL_RURAL = 207
# CAT_FUEL_EMERGENCY will be setup dynamically if missing

dataset = [
    # ESTACIONES URBANAS
    {
        "name": "Copec Balmaceda Coyhaique",
        "category": "fuel_station",
        "brand": "Copec",
        "locality": "Coyhaique",
        "lat": -45.5689,
        "lng": -72.0696,
        "desc": "Estación de servicio urbana con tienda y combustible completo.",
        "extra": {
            "service_level": "urban",
            "fuel_types": ["93", "95", "97", "diesel"],
            "source_type": "official",
            "verification_status": "verified"
        }
    },
    {
        "name": "Shell Ogana Coyhaique",
        "category": "fuel_station",
        "brand": "Shell",
        "locality": "Coyhaique",
        "lat": -45.5670,
        "lng": -72.0700,
        "desc": "Estación Shell 24 horas en Coyhaique.",
        "extra": {
            "service_level": "urban",
            "fuel_types": ["93", "95", "diesel"],
            "source_type": "open_data",
            "verification_status": "verified"
        }
    },
    {
        "name": "Shell Carrera Coyhaique",
        "category": "fuel_station",
        "brand": "Shell",
        "locality": "Coyhaique",
        "lat": -45.5689,
        "lng": -72.0696,
        "desc": "Estación Shell céntrica de Coyhaique.",
        "extra": {
            "service_level": "urban",
            "fuel_types": ["93", "95", "diesel"],
            "source_type": "open_data",
            "verification_status": "verified"
        }
    },
    {
        "name": "Copec Puerto Aysén",
        "category": "fuel_station",
        "brand": "Copec",
        "locality": "Puerto Aysén",
        "lat": -45.4020,
        "lng": -72.6980,
        "desc": "Principal estación de servicio de Puerto Aysén.",
        "extra": {
            "service_level": "urban",
            "fuel_types": ["93", "95", "97", "diesel"],
            "source_type": "official",
            "verification_status": "verified"
        }
    },
    {
        "name": "Copec Chile Chico",
        "category": "fuel_station",
        "brand": "Copec",
        "locality": "Chile Chico",
        "lat": -46.5400,
        "lng": -71.7200,
        "desc": "Estación urbana que abastece el sector sur del Lago General Carrera.",
        "extra": {
            "service_level": "urban",
            "fuel_types": ["93", "95", "diesel"],
            "source_type": "open_data",
            "verification_status": "verified"
        }
    },
    {
        "name": "Copec Cochrane",
        "category": "fuel_station",
        "brand": "Copec",
        "locality": "Cochrane",
        "lat": -47.2560,
        "lng": -72.5700,
        "desc": "Principal estación de combustible del sur de la región.",
        "extra": {
            "service_level": "urban",
            "fuel_types": ["93", "95", "diesel"],
            "source_type": "open_data",
            "verification_status": "verified"
        }
    },
    {
        "name": "Copec Puerto Cisnes",
        "category": "fuel_station",
        "brand": "Copec",
        "locality": "Puerto Cisnes",
        "lat": -44.7390,
        "lng": -72.7030,
        "desc": "Estación de servicio del litoral norte de Aysén.",
        "extra": {
            "service_level": "urban",
            "fuel_types": ["93", "95", "diesel"],
            "source_type": "open_data",
            "verification_status": "pending"
        }
    },
    {
        "name": "Copec Villa Cerro Castillo",
        "category": "fuel_station",
        "brand": "Copec",
        "locality": "Villa Cerro Castillo",
        "lat": -46.1200,
        "lng": -72.1200,
        "desc": "Estación inaugurada recientemente para apoyar el turismo de la zona.",
        "extra": {
            "service_level": "rural",
            "fuel_types": ["93", "95", "diesel"],
            "source_type": "official",
            "verification_status": "verified"
        }
    },
    # RURALES
    {
        "name": "Estación Combustible La Junta",
        "category": "fuel_station",
        "brand": "Copec",
        "locality": "La Junta",
        "lat": -43.9701,
        "lng": -72.4000,
        "desc": "Estación que abastece la zona norte de la región.",
        "extra": {
            "service_level": "rural",
            "fuel_types": ["93", "95", "diesel"],
            "source_type": "open_data",
            "verification_status": "approximate"
        }
    },
    {
        "name": "Estación Combustible Puyuhuapi",
        "category": "fuel_station",
        "brand": "local",
        "locality": "Puyuhuapi",
        "lat": -44.3200,
        "lng": -72.5600,
        "desc": "Punto de abastecimiento limitado en la localidad.",
        "extra": {
            "service_level": "rural",
            "fuel_types": ["diesel"],
            "source_type": "open_data",
            "verification_status": "approximate"
        }
    },
    {
        "name": "Estación Combustible Puerto Río Tranquilo",
        "category": "fuel_rural",
        "brand": "local",
        "locality": "Puerto Río Tranquilo",
        "lat": -46.6200,
        "lng": -72.6700,
        "desc": "Punto de venta de combustible para vehículos y embarcaciones.",
        "extra": {
            "service_level": "rural",
            "fuel_types": ["93", "diesel"],
            "source_type": "open_data",
            "verification_status": "approximate"
        }
    },
    {
        "name": "Estación Combustible Puerto Guadal",
        "category": "fuel_rural",
        "brand": "local",
        "locality": "Puerto Guadal",
        "lat": -46.7900,
        "lng": -72.0000,
        "desc": "Punto rural de abastecimiento cercano al Lago General Carrera.",
        "extra": {
            "service_level": "rural",
            "fuel_types": ["diesel"],
            "source_type": "open_data",
            "verification_status": "approximate"
        }
    },
    {
        "name": "Estación Combustible Villa O’Higgins",
        "category": "fuel_station",
        "brand": "local",
        "locality": "Villa O’Higgins",
        "lat": -48.4700,
        "lng": -72.5600,
        "desc": "Punto de abastecimiento para el extremo sur de la Carretera Austral.",
        "extra": {
            "service_level": "rural",
            "fuel_types": ["93", "diesel"],
            "source_type": "open_data",
            "verification_status": "approximate"
        }
    },
    # ESPECIAL
    {
        "name": "Estación Puerto Chacabuco",
        "category": "fuel_emergency",
        "brand": "maritime",
        "locality": "Puerto Chacabuco",
        "lat": -45.4600,
        "lng": -72.8000,
        "desc": "Punto de abastecimiento para embarcaciones y transporte marítimo.",
        "extra": {
            "service_level": "port",
            "fuel_types": ["diesel"],
            "source_type": "open_data",
            "verification_status": "pending"
        }
    }
]

def setup_categories(conn):
    # Ensure Combustible de Emergencia exists
    res = conn.execute(text("SELECT id FROM catalog_categories WHERE slug = 'combustible-emergencia'"))
    row = res.fetchone()
    if row:
        return row.id
    else:
        print("Creating Combustible Emergencia category...")
        res = conn.execute(text("""
            INSERT INTO catalog_categories (name, slug, parent_id, is_active)
            VALUES ('Combustible de Emergencia', 'combustible-emergencia', 205, true)
            RETURNING id
        """))
        return res.fetchone().id

def setup_locality(conn, name, lat, lng):
    norm_name = name.replace("’", "'").replace("‘", "'").strip()
    slug = slugify(norm_name)
    res = conn.execute(text("SELECT id FROM localities WHERE slug = :slug"), {"slug": slug})
    row = res.fetchone()
    if row:
        return row.id
    else:
        print(f"Seeding locality: {norm_name}")
        res = conn.execute(text("""
            INSERT INTO localities (name, slug, type, region, comuna, lat, lng, is_active)
            VALUES (:name, :slug, 'village', 'Aysén', 'Coyhaique', :lat, :lng, true)
            RETURNING id
        """), {"name": norm_name, "slug": slug, "lat": lat, "lng": lng})
        return res.fetchone().id

def populate_fuel():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        try:
            print(f"Starting population of Aysén fuel stations ({len(dataset)} items)...")
            
            id_fuel_emergency = setup_categories(conn)
            
            cat_map = {
                "fuel_station": CAT_GASOLINERA,
                "fuel_rural": CAT_FUEL_RURAL,
                "fuel_emergency": id_fuel_emergency
            }
            
            inserted = 0
            updated = 0
            
            for item in dataset:
                loc_id = setup_locality(conn, item["locality"], item["lat"], item["lng"])
                cat_id = cat_map[item["category"]]
                
                res = conn.execute(text("SELECT id FROM catalog_items WHERE name = :name AND locality_id = :loc_id"), 
                                   {"name": item["name"], "loc_id": loc_id})
                existing = res.fetchone()
                
                extra_data = {
                    "brand": item["brand"],
                    "last_verified_at": "2024-03-09"
                }
                extra_data.update(item.get("extra", {}))
                
                if existing:
                    print(f"Updating: {item['name']}")
                    conn.execute(text("""
                        UPDATE catalog_items 
                        SET item_type = 'place', category_id = :cat_id, 
                            description = :desc, lat = :lat, lng = :lng, 
                            extra = :extra, locality_id = :loc_id
                        WHERE id = :id
                    """), {
                        "cat_id": cat_id,
                        "desc": item["desc"],
                        "lat": item["lat"],
                        "lng": item["lng"],
                        "extra": json.dumps(extra_data),
                        "loc_id": loc_id,
                        "id": existing.id
                    })
                    updated += 1
                else:
                    print(f"Creating: {item['name']}")
                    conn.execute(text("""
                        INSERT INTO catalog_items (item_type, name, description, category_id, lat, lng, extra, locality_id, is_active)
                        VALUES ('place', :name, :desc, :cat_id, :lat, :lng, :extra, :loc_id, true)
                    """), {
                        "name": item["name"],
                        "desc": item["desc"],
                        "cat_id": cat_id,
                        "lat": item["lat"],
                        "lng": item["lng"],
                        "extra": json.dumps(extra_data),
                        "loc_id": loc_id
                    })
                    inserted += 1
            
            print(f"Lote 3 Completed. {inserted} inserted, {updated} updated.")
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
            raise e

if __name__ == "__main__":
    populate_fuel()
