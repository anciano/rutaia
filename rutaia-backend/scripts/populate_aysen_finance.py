# scripts/populate_aysen_finance.py
import os
import sys
import json
from sqlalchemy import create_engine, text
from slugify import slugify
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Categories Mapping
CAT_BANCO = 247
CAT_ATM = 246
CAT_CAJAVECINA = 248
CAT_CAMBIO = 249

dataset = [
    # SUCURSALES BANCARIAS
    {"name": "BancoEstado Coyhaique", "category": "bank_branch", "locality": "Coyhaique", "address": "José de Moraleda 502", "lat": -45.573, "lng": -72.066},
    {"name": "BancoEstado Puerto Aysén", "category": "bank_branch", "locality": "Puerto Aysén", "address": "Carrera 799", "lat": -45.402, "lng": -72.699},
    {"name": "BancoEstado Chile Chico", "category": "bank_branch", "locality": "Chile Chico", "address": "Pedro A. González 112", "lat": -46.538, "lng": -71.725},
    {"name": "BancoEstado Cochrane", "category": "bank_branch", "locality": "Cochrane", "address": "Esmeralda 460", "lat": -47.256, "lng": -72.570},
    {"name": "BancoEstado Puerto Cisnes", "category": "bank_branch", "locality": "Puerto Cisnes", "lat": -44.740, "lng": -72.702},
    {"name": "Banco BCI Coyhaique", "category": "bank_branch", "locality": "Coyhaique", "address": "Arturo Prat 387", "lat": -45.571, "lng": -72.066},
    {"name": "Banco de Chile Puerto Aysén", "category": "bank_branch", "locality": "Puerto Aysén", "address": "Arturo Prat 420", "lat": -45.403, "lng": -72.699},
    
    # SERVIESTADO / EXPRESS
    {"name": "ServiEstado Coyhaique", "category": "bank_express", "locality": "Coyhaique"},
    {"name": "ServiEstado Puerto Aysén", "category": "bank_express", "locality": "Puerto Aysén"},
    {"name": "ServiEstado Chile Chico", "category": "bank_express", "locality": "Chile Chico"},
    {"name": "ServiEstado Cochrane", "category": "bank_express", "locality": "Cochrane"},
    
    # CAJEROS (ATM)
    {"name": "ATM BancoEstado Coyhaique Centro", "category": "atm", "locality": "Coyhaique"},
    {"name": "ATM BancoEstado Coyhaique Mall", "category": "atm", "locality": "Coyhaique"},
    {"name": "ATM BancoEstado Puerto Aysén", "category": "atm", "locality": "Puerto Aysén"},
    {"name": "ATM BancoEstado Chile Chico", "category": "atm", "locality": "Chile Chico"},
    {"name": "ATM BancoEstado Cochrane", "category": "atm", "locality": "Cochrane"},
    {"name": "ATM BancoEstado Puerto Cisnes", "category": "atm", "locality": "Puerto Cisnes"},
    {"name": "ATM BancoEstado Villa O'Higgins", "category": "atm", "locality": "Villa O'Higgins"},
    {"name": "ATM BancoEstado Melinka", "category": "atm", "locality": "Melinka"},
    {"name": "ATM BancoEstado La Junta", "category": "atm", "locality": "La Junta"},
    
    # CAJAVECINA
    {"name": "CajaVecina Puerto Río Tranquilo", "category": "caja_vecina", "locality": "Puerto Río Tranquilo"},
    {"name": "CajaVecina Puerto Guadal", "category": "caja_vecina", "locality": "Puerto Guadal"},
    {"name": "CajaVecina Villa Cerro Castillo", "category": "caja_vecina", "locality": "Villa Cerro Castillo"},
    {"name": "CajaVecina Bahía Murta", "category": "caja_vecina", "locality": "Bahía Murta"},
    {"name": "CajaVecina Lago Verde", "category": "caja_vecina", "locality": "Lago Verde"},
    {"name": "CajaVecina Puerto Bertrand", "category": "caja_vecina", "locality": "Puerto Bertrand"},
    {"name": "CajaVecina Caleta Tortel", "category": "caja_vecina", "locality": "Caleta Tortel"},
    {"name": "CajaVecina Villa Amengual", "category": "caja_vecina", "locality": "Villa Amengual"},
    
    # CASAS DE CAMBIO
    {"name": "Casa de Cambio Coyhaique Centro", "category": "money_exchange", "locality": "Coyhaique"},
]

def setup_categories(conn):
    # Ensure ServiEstado Express category exists as subcategory of Banco
    res = conn.execute(text("SELECT id FROM catalog_categories WHERE slug = 'bancoestado-express'"))
    row = res.fetchone()
    if row:
        return row.id
    else:
        print("Creating BancoEstado Express category...")
        res = conn.execute(text("""
            INSERT INTO catalog_categories (name, slug, parent_id, is_active)
            VALUES ('BancoEstado Express', 'bancoestado-express', 247, true)
            RETURNING id
        """))
        return res.fetchone().id

def setup_locality(conn, name):
    norm_name = name.replace("’", "'").replace("‘", "'").strip()
    slug = slugify(norm_name)
    
    # 1. Safely check existence first
    res = conn.execute(text("SELECT id FROM localities WHERE slug = :slug"), {"slug": slug})
    row = res.fetchone()
    if row:
        return row.id
    
    # 2. If missing, insert with defaults (Aysén region defaults or 0,0)
    # We use 0,0 because lat/lng are NOT NULL
    print(f"Seeding missing locality: {norm_name}")
    res = conn.execute(text("""
        INSERT INTO localities (name, slug, type, region, comuna, lat, lng, is_active)
        VALUES (:name, :slug, 'village', 'Aysén', 'Coyhaique', 0, 0, true)
        ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name
        RETURNING id
    """), {"name": norm_name, "slug": slug})
    return res.fetchone().id

def populate_finance():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        try:
            print(f"Starting population of Aysén finance items ({len(dataset)} items)...")
            
            id_express = setup_categories(conn)
            
            cat_map = {
                "bank_branch": CAT_BANCO,
                "bank_express": id_express,
                "atm": CAT_ATM,
                "caja_vecina": CAT_CAJAVECINA,
                "money_exchange": CAT_CAMBIO
            }
            
            inserted = 0
            updated = 0
            
            for item in dataset:
                loc_id = setup_locality(conn, item["locality"])
                cat_id = cat_map[item["category"]]
                
                res = conn.execute(text("SELECT id FROM catalog_items WHERE name = :name AND locality_id = :loc_id"), 
                                   {"name": item["name"], "loc_id": loc_id})
                existing = res.fetchone()
                
                extra_data = {
                    "source_type": "official",
                    "verification_status": "verified",
                    "last_verified_at": "2024-03-09"
                }
                if "address" in item:
                    extra_data["address"] = item["address"]
                
                lat = item.get("lat")
                lng = item.get("lng")
                
                if existing:
                    print(f"Updating: {item['name']}")
                    conn.execute(text("""
                        UPDATE catalog_items 
                        SET item_type = 'place', category_id = :cat_id, 
                            lat = :lat, lng = :lng, extra = :extra, locality_id = :loc_id
                        WHERE id = :id
                    """), {
                        "cat_id": cat_id,
                        "lat": lat,
                        "lng": lng,
                        "extra": json.dumps(extra_data),
                        "loc_id": loc_id,
                        "id": existing.id
                    })
                    updated += 1
                else:
                    print(f"Creating: {item['name']}")
                    conn.execute(text("""
                        INSERT INTO catalog_items (item_type, name, category_id, lat, lng, extra, locality_id, is_active)
                        VALUES ('place', :name, :cat_id, :lat, :lng, :extra, :loc_id, true)
                    """), {
                        "name": item["name"],
                        "cat_id": cat_id,
                        "lat": lat,
                        "lng": lng,
                        "extra": json.dumps(extra_data),
                        "loc_id": loc_id
                    })
                    inserted += 1
            
            print(f"Finanzas Completed. {inserted} inserted, {updated} updated.")
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
            raise e

if __name__ == "__main__":
    populate_finance()
