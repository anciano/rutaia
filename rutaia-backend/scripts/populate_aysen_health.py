# scripts/populate_aysen_health.py
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
CAT_HOSPITAL = 235
CAT_CESFAM = 237
CAT_POSTA = 238
# CECOSF doesn't exist yet, we'll create it if missing or map it.
# We'll handle it in a setup function.

dataset = [
    # HOSPITALES
    {"name": "Hospital Regional Coyhaique", "category": "hospital", "locality": "Coyhaique", "lat": -45.5756, "lng": -72.0663, "desc": "Principal hospital de alta complejidad de la Región de Aysén y centro de referencia para toda la red asistencial regional.", "extra": {"service_level": "regional", "source_type": "official", "verification_status": "verified"}},
    {"name": "Hospital de Puerto Aysén", "category": "hospital", "locality": "Puerto Aysén", "lat": -45.4037, "lng": -72.7010, "desc": "Hospital de mediana complejidad que atiende a la población del norte de la región y la zona costera.", "extra": {"service_level": "regional", "source_type": "official", "verification_status": "verified"}},
    {"name": "Hospital Dr. Leopoldo Ortega Rodríguez", "category": "hospital", "locality": "Chile Chico", "lat": -46.5387, "lng": -71.7233, "desc": "Hospital comunitario que presta servicios a la zona sur del Lago General Carrera.", "extra": {"service_level": "community", "source_type": "official", "verification_status": "verified"}},
    {"name": "Hospital Lord Cochrane", "category": "hospital", "locality": "Cochrane", "lat": -47.2567, "lng": -72.5700, "desc": "Hospital comunitario que atiende a la población del sur de la región.", "extra": {"service_level": "community", "source_type": "official", "verification_status": "verified"}},
    {"name": "Hospital Jorge Ibar Bruce", "category": "hospital", "locality": "Puerto Cisnes", "lat": -44.7390, "lng": -72.7020, "desc": "Hospital comunitario que atiende a las localidades costeras del norte de Aysén.", "extra": {"service_level": "community", "source_type": "official", "verification_status": "verified"}},
    
    # CESFAM / CENTROS
    {"name": "CESFAM Puerto Aysén", "category": "cesfam", "locality": "Puerto Aysén", "lat": -45.4032, "lng": -72.7004, "desc": "Centro de atención primaria que cubre gran parte de la comuna de Aysén.", "extra": {"service_level": "urban", "source_type": "official", "verification_status": "verified"}},
    {"name": "CESFAM Alejandro Gutiérrez", "category": "cesfam", "locality": "Coyhaique", "lat": -45.5690, "lng": -72.0640, "desc": "Centro de salud familiar urbano que atiende población del sector alto de Coyhaique.", "extra": {"service_level": "urban", "source_type": "official", "verification_status": "verified"}},
    {"name": "CESFAM Víctor Domingo Silva", "category": "cesfam", "locality": "Coyhaique", "lat": -45.5720, "lng": -72.0670, "desc": "Centro de salud familiar que presta atención primaria a la comunidad de Coyhaique.", "extra": {"service_level": "urban", "source_type": "official", "verification_status": "verified"}},
    {"name": "CECOF Ribera Sur", "category": "cecosf", "locality": "Puerto Aysén", "lat": -45.4050, "lng": -72.7020, "desc": "Centro comunitario de salud familiar dependiente de la red primaria de Puerto Aysén.", "extra": {"service_level": "urban", "source_type": "official", "verification_status": "pending"}},
    
    # POSTAS RURALES
    {"name": "Posta Rural Puerto Bertrand", "category": "posta_rural", "locality": "Puerto Bertrand", "lat": -46.8350, "lng": -72.7020, "desc": "Posta de Salud Rural en la localidad de Puerto Bertrand.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Puerto Guadal", "category": "posta_rural", "locality": "Puerto Guadal", "lat": -46.7900, "lng": -72.0000, "desc": "Posta de Salud Rural en la localidad de Puerto Guadal.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Mallín Grande", "category": "posta_rural", "locality": "Mallín Grande", "lat": -46.6200, "lng": -71.9000, "desc": "Posta de Salud Rural en la localidad de Mallín Grande.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Puerto Río Tranquilo", "category": "posta_rural", "locality": "Puerto Río Tranquilo", "lat": -46.6200, "lng": -72.6700, "desc": "Posta de Salud Rural en la localidad de Puerto Río Tranquilo.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Puerto Sánchez", "category": "posta_rural", "locality": "Puerto Sánchez", "lat": -46.4100, "lng": -72.3000, "desc": "Posta de Salud Rural en la localidad de Puerto Sánchez.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Bahía Murta", "category": "posta_rural", "locality": "Bahía Murta", "lat": -46.5200, "lng": -72.6700, "desc": "Posta de Salud Rural en la localidad de Bahía Murta.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Puerto Ibáñez", "category": "posta_rural", "locality": "Puerto Ingeniero Ibáñez", "lat": -46.2900, "lng": -71.9400, "desc": "Posta de Salud Rural en la localidad de Puerto Ibáñez.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Cerro Castillo", "category": "posta_rural", "locality": "Villa Cerro Castillo", "lat": -46.1200, "lng": -72.1200, "desc": "Posta de Salud Rural en la localidad de Villa Cerro Castillo.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Balmaceda", "category": "posta_rural", "locality": "Balmaceda", "lat": -45.9167, "lng": -71.6890, "desc": "Posta de Salud Rural en la localidad de Balmaceda.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural El Blanco", "category": "posta_rural", "locality": "El Blanco", "lat": -45.6000, "lng": -72.2000, "desc": "Posta de Salud Rural en la localidad de El Blanco.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Valle Simpson", "category": "posta_rural", "locality": "Valle Simpson", "lat": -45.5200, "lng": -72.3000, "desc": "Posta de Salud Rural en la localidad de Valle Simpson.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Lago Atravesado", "category": "posta_rural", "locality": "Lago Atravesado", "lat": -45.5500, "lng": -72.1000, "desc": "Posta de Salud Rural en la localidad de Lago Atravesado.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Villa Ortega", "category": "posta_rural", "locality": "Villa Ortega", "lat": -45.5400, "lng": -71.9000, "desc": "Posta de Salud Rural en la localidad de Villa Ortega.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Ñireguao", "category": "posta_rural", "locality": "Ñireguao", "lat": -45.4300, "lng": -71.9500, "desc": "Posta de Salud Rural en la localidad de Ñireguao.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Puerto Aguirre", "category": "posta_rural", "locality": "Puerto Aguirre", "lat": -45.1660, "lng": -73.5300, "desc": "Posta de Salud Rural en la localidad de Puerto Aguirre.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Villa O’Higgins", "category": "posta_rural", "locality": "Villa O’Higgins", "lat": -48.4700, "lng": -72.5600, "desc": "Posta de Salud Rural en la localidad de Villa O'Higgins.", "extra": {"source_type": "official", "verification_status": "verified"}},
    {"name": "Posta Rural Caleta Tortel", "category": "posta_rural", "locality": "Caleta Tortel", "lat": -47.8000, "lng": -73.5300, "desc": "Posta de Salud Rural en la localidad de Caleta Tortel.", "extra": {"source_type": "official", "verification_status": "verified"}},
]

def setup_categories(conn):
    # Ensure CECOSF exists
    res = conn.execute(text("SELECT id FROM catalog_categories WHERE name = 'CECOSF'"))
    row = res.fetchone()
    if row:
        return row.id
    else:
        # Create under 'Salud y emergencias' (234)
        print("Creating CECOSF category...")
        res = conn.execute(text("""
            INSERT INTO catalog_categories (name, slug, parent_id, is_active)
            VALUES ('CECOSF', 'cecosf', 234, true)
            RETURNING id
        """))
        return res.fetchone().id

def setup_locality(conn, name, lat, lng):
    # Normalize name to handle smart quotes and other variations
    norm_name = name.replace("’", "'").replace("‘", "'").strip()
    slug = slugify(norm_name)
    
    # Check existence by slug
    res = conn.execute(text("SELECT id FROM localities WHERE slug = :slug"), {"slug": slug})
    row = res.fetchone()
    if row:
        return row.id
    else:
        # Create as village/seed
        print(f"Seeding locality: {norm_name} (slug: {slug})")
        res = conn.execute(text("""
            INSERT INTO localities (name, slug, type, region, comuna, lat, lng, is_active)
            VALUES (:name, :slug, 'village', 'Aysén', 'Coyhaique', :lat, :lng, true)
            RETURNING id
        """), {"name": norm_name, "slug": slug, "lat": lat, "lng": lng})
        return res.fetchone().id

def populate_health():
    engine = create_engine(DATABASE_URL)
    # Using engine.begin() provides a transaction that commits automatically if no exception occurs
    with engine.begin() as conn:
        try:
            print(f"Starting population of Aysén health centers ({len(dataset)} items)...")
            
            id_cecosf = setup_categories(conn)
            
            cat_map = {
                "hospital": CAT_HOSPITAL,
                "cesfam": CAT_CESFAM,
                "cecosf": id_cecosf,
                "posta_rural": CAT_POSTA
            }
            
            inserted = 0
            updated = 0
            
            for item in dataset:
                # Setup locality if needed
                loc_id = setup_locality(conn, item["locality"], item["lat"], item["lng"])
                cat_id = cat_map[item["category"]]
                
                # Check existence of catalog item by name and locality
                res = conn.execute(text("SELECT id FROM catalog_items WHERE name = :name AND locality_id = :loc_id"), 
                                   {"name": item["name"], "loc_id": loc_id})
                existing = res.fetchone()
                
                # Prepare extra with defaults + item specializations
                extra_data = {
                    "source_type": "official",
                    "verification_status": "verified",
                    "last_verified_at": "2024-03-09"
                }
                extra_data.update(item.get("extra", {}))
                
                if existing:
                    print(f"Updating catalog item: {item['name']}")
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
                    print(f"Creating catalog item: {item['name']}")
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
            
            print(f"Lote 2 Completed. {inserted} inserted, {updated} updated.")
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
            raise e # Re-raise to trigger rollback by engine.begin()

if __name__ == "__main__":
    populate_health()
