# scripts/populate_aysen_batch.py
import os
import sys
import json
import pandas as pd
from sqlalchemy import create_engine, text
from slugify import slugify
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

EXCEL_DIR = r"c:\Proyectos\asesor"
LOCALITIES_FILE = "rutaia_archivo1_localidades_aysen.xlsx"
CATALOG_FILES = [
    "rutaia_archivo2_salud_emergencia_aysen.xlsx",
    "rutaia_archivo3_combustible_aysen.xlsx",
    "rutaia_archivo4_finanzas_aysen.xlsx",
    "rutaia_archivo5_abastecimiento_aysen.xlsx",
    "rutaia_archivo7_hospedajes_aysen.xlsx",
    "rutaia_archivo8_atractivos_naturales_aysen.xlsx",
    "rutaia_transporte_aysen.xlsx"
]

# Mapping Excel slugs to DB slugs
SLUG_MAPPING = {
    # Salud
    "hospital": "hospital",
    "cesfam": "cesfam",
    "cecosf": "cecosf",
    "posta_rural": "posta-rural",
    "bomberos": "bomberos",
    "carabineros": "carabineros",
    "urgencia": "urgencia",
    
    # Combustible
    "fuel_station": "gasolinera",
    "fuel_rural": "punto-de-combustible-rural",
    "fuel_emergency": "combustible-emergencia",
    
    # Finanzas
    "bank_branch": "banco",
    "bank_express": "bancoestado-express",
    "atm": "cajero-automático-atm",
    "caja_vecina": "punto-de-pago-local-cajavecina",
    "money_exchange": "casa-de-cambio",
    
    # Abastecimiento (Supply)
    "supply_market": "minimarket---almacén",
    "supply_bakery": "panadería",
    "supply_outdoor": "tienda-de-outdoor",
    "supply_hardware": "ferretería",
    "supermercado": "minimarket---almacén",
    "almacen": "minimarket---almacén",
    "panaderia": "panadería",
    
    # Hospedaje (Lodging)
    "lodging_hotel": "hotel",
    "lodging_lodge": "lodge",
    "lodging_camping": "camping",
    "lodging_cabin": "cabaña",
    "lodging_hostel": "hostal",
    "hotel": "hotel",
    "lodge": "lodge",
    "camping": "camping",
    "cabaña": "cabaña",
    "hostal": "hostal",
    
    # Atractivos (Attraction)
    "attraction_park": "naturaleza-parques-nacionales",
    "attraction_viewpoint": "mirador",
    "attraction_waterfall": "salto-de-agua",
    "park": "naturaleza-parques-nacionales",
    "viewpoint": "mirador",
    "waterfall": "salto-de-agua",
    "island": "isla",
    "forest": "naturaleza", # Fallback
    "mountain": "naturaleza", # Fallback
    "national_park": "naturaleza-parques-nacionales",
    "river": "naturaleza",
    
    # Transporte (Transport)
    "transport_terminal": "terminal-de-buses",
    "transport_agency": "oficina-de-transporte---ventas",
    "transport_stop": "parada-de-bus",
    "bus_terminal": "terminal-de-buses",
    "bus_stop": "parada-de-bus",
    "airport": "aeropuerto",
    "aerodrome": "aeródromo",
}

def setup_locality(conn, name, lat=0, lng=0, type='village', comuna='Desconocida', description=''):
    if pd.isna(name) or str(name).strip() == "":
        return None
    norm_name = str(name).replace("’", "'").replace("‘", "'").strip()
    slug = slugify(norm_name)
    
    res = conn.execute(text("SELECT id FROM localities WHERE slug = :slug"), {"slug": slug})
    row = res.fetchone()
    
    params = {
        "name": norm_name, # keep original casing or norm
        "slug": slug, 
        "lat": float(lat) if not pd.isna(lat) else 0.0, 
        "lng": float(lng) if not pd.isna(lng) else 0.0,
        "type": str(type) if not pd.isna(type) else 'village',
        "comuna": str(comuna) if not pd.isna(comuna) else 'Desconocida',
        "description": str(description) if not pd.isna(description) else ''
    }

    if row:
        conn.execute(text("""
            UPDATE localities 
            SET name = :name, type = :type, region = 'Aysén', comuna = :comuna, 
                lat = :lat, lng = :lng, description = :description, is_active = true
            WHERE id = :id
        """), {**params, "id": row.id})
        return row.id
    else:
        res = conn.execute(text("""
            INSERT INTO localities (name, slug, type, region, comuna, lat, lng, description, is_active)
            VALUES (:name, :slug, :type, 'Aysén', :comuna, :lat, :lng, :description, true)
            RETURNING id
        """), params)
        return res.fetchone().id

def get_category_id(conn, raw_slug):
    db_slug = SLUG_MAPPING.get(raw_slug, raw_slug)
    res = conn.execute(text("SELECT id FROM catalog_categories WHERE slug = :slug"), {"slug": db_slug})
    row = res.fetchone()
    if not row:
        # Second try, maybe it's just a raw slug that exists
        res = conn.execute(text("SELECT id FROM catalog_categories WHERE slug = :slug"), {"slug": slugify(str(raw_slug))})
        row = res.fetchone()
    return row.id if row else None

def populate():
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        print("Starting batch population...")
        
        # 1. Localities
        loc_path = os.path.join(EXCEL_DIR, LOCALITIES_FILE)
        if os.path.exists(loc_path):
            print(f"Populating localities...")
            df_loc = pd.read_excel(loc_path)
            for _, row in df_loc.iterrows():
                setup_locality(conn, row.get('name'), row.get('lat'), row.get('lng'), row.get('type'), row.get('comuna'), row.get('description'))
        
        counts = {"inserted": 0, "skipped": 0}
        
        # 2. Catalog Items
        for file_name in CATALOG_FILES:
            path = os.path.join(EXCEL_DIR, file_name)
            if not os.path.exists(path): continue
            
            print(f"Processing {file_name}...")
            df = pd.read_excel(path)
            
            # Identify categories to cleanup
            unique_cat_slugs = df['category'].dropna().unique()
            for raw_cat_slug in unique_cat_slugs:
                cat_id = get_category_id(conn, raw_cat_slug)
                if cat_id:
                    print(f"  Cleanup: {raw_cat_slug} (DB: {SLUG_MAPPING.get(raw_cat_slug, raw_cat_slug)})")
                    conn.execute(text("DELETE FROM catalog_items WHERE category_id = :cat_id"), {"cat_id": cat_id})
                else:
                    print(f"  Warning: Category '{raw_cat_slug}' not found.")

            # Insert
            for _, row in df.iterrows():
                try:
                    name = row.get('name')
                    if pd.isna(name): continue
                    
                    loc_id = setup_locality(conn, row.get('locality'), row.get('lat', 0), row.get('lng', 0))
                    cat_id = get_category_id(conn, row.get('category'))
                    
                    if not cat_id:
                        counts["skipped"] += 1
                        continue
                    
                    extra = {
                        "source_type": row.get('source_type', 'official') if not pd.isna(row.get('source_type')) else 'official',
                        "verification_status": row.get('verification_status', 'verified') if not pd.isna(row.get('verification_status')) else 'verified',
                        "last_verified_at": "2024-03-10"
                    }
                    
                    # Merge all columns except core ones into extra
                    core_cols = ['name', 'description', 'lat', 'lng', 'category', 'locality', 'source_type', 'verification_status', 'desc']
                    for col in df.columns:
                        if col not in core_cols:
                            val = row[col]
                            if not pd.isna(val):
                                # Try to parse json
                                if isinstance(val, str) and val.strip().startswith('[') and val.strip().endswith(']'):
                                    try:
                                        val = json.loads(val.replace("'", '"'))
                                    except: pass
                                extra[col] = val
                    
                    desc = row.get('description', row.get('desc', ''))
                    if pd.isna(desc): desc = ''
                    
                    conn.execute(text("""
                        INSERT INTO catalog_items (item_type, name, description, category_id, lat, lng, extra, locality_id, is_active)
                        VALUES ('place', :name, :desc, :cat_id, :lat, :lng, :extra, :loc_id, true)
                    """), {
                        "name": str(name),
                        "desc": str(desc),
                        "cat_id": cat_id,
                        "lat": float(row.get('lat', 0)) if not pd.isna(row.get('lat')) else 0.0,
                        "lng": float(row.get('lng', 0)) if not pd.isna(row.get('lng')) else 0.0,
                        "extra": json.dumps(extra),
                        "loc_id": loc_id
                    })
                    counts["inserted"] += 1
                except Exception as e:
                    print(f"  Error in {name}: {e}")
                    counts["skipped"] += 1

        print(f"\nBatch Completed. Total inserted: {counts['inserted']}, Skipped: {counts['skipped']}")

if __name__ == "__main__":
    populate()
