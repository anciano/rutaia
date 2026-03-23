# scripts/seed_localities_v1.py
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def slugify(name):
    return name.lower().replace(' ', '-').replace("'", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")

def seed():
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        print("Commencing territorial data seeding...")

        # 1. Migrar desde ciudades
        res_ciudades = session.execute(text("SELECT id, nombre, region FROM ciudades WHERE id >= 3"))
        for cid, name, region in res_ciudades:
            slug = slugify(name)
            
            # Determinar tipo
            ltype = 'village'
            if name in ['Coyhaique', 'Puerto Aysén']: ltype = 'city'
            elif name in ['Cochrane', 'Chile Chico', 'Caleta Tortel', "Villa O'Higgins"]: ltype = 'town'
            elif name in ['Puerto Chacabuco']: ltype = 'port'
            elif name in ['Puyuhuapi', 'Puerto Guadal', 'La Junta', 'Balmaceda']: ltype = 'village'

            # Obtener coordenadas aproximadas si existen en ciudades (no existen en el modelo actual visto, pero busquemos si hay algo en catalog_items)
            res_item = session.execute(text("SELECT lat, lng, description FROM catalog_items WHERE name ILIKE :name LIMIT 1"), {"name": f"%{name}%"}).fetchone()
            lat = res_item[0] if res_item and res_item[0] else -45.57
            lng = res_item[1] if res_item and res_item[1] else -72.06
            desc = res_item[2] if res_item else None

            session.execute(text("""
                INSERT INTO localities (name, slug, type, region, lat, lng, description, legacy_city_id)
                VALUES (:name, :slug, :type, :region, :lat, :lng, :description, :legacy_id)
                ON CONFLICT (slug) DO NOTHING
            """), {"name": name, "slug": slug, "type": ltype, "region": region, "lat": lat, "lng": lng, "description": desc, "legacy_id": cid})
            print(f"Migrated city: {name}")

        # 2. Casos especiales desde catalog_items
        # Puyuhuapi Pueblo (ID 95)
        res_puyuhuapi = session.execute(text("SELECT id, name, description, lat, lng FROM catalog_items WHERE id = 95")).fetchone()
        if res_puyuhuapi:
            session.execute(text("""
                UPDATE localities SET legacy_item_id = :item_id, description = :desc, lat = :lat, lng = :lng
                WHERE slug = 'puyuhuapi'
            """), {"item_id": res_puyuhuapi[0], "desc": res_puyuhuapi[2], "lat": res_puyuhuapi[3], "lng": res_puyuhuapi[4]})
            
            # Migrar Destination Profile
            session.execute(text("""
                UPDATE destination_profiles SET locality_id = (SELECT id FROM localities WHERE slug = 'puyuhuapi')
                WHERE catalog_item_id = 95
            """))
            print("Updated Puyuhuapi from Catalog Item and migrated Profile.")

        # Coyhaique Centro (ID 94)
        res_coy = session.execute(text("SELECT id, name, description, lat, lng FROM catalog_items WHERE id = 94")).fetchone()
        if res_coy:
            session.execute(text("""
                UPDATE localities SET legacy_item_id = :item_id, description = :desc, lat = :lat, lng = :lng
                WHERE slug = 'coyhaique'
            """), {"item_id": res_coy[0], "desc": res_coy[2], "lat": res_coy[3], "lng": res_coy[4]})
            
            # Migrar Destination Profile
            session.execute(text("""
                UPDATE destination_profiles SET locality_id = (SELECT id FROM localities WHERE slug = 'coyhaique')
                WHERE catalog_item_id = 94
            """))
            print("Updated Coyhaique from Catalog Item and migrated Profile.")

        # 3. Vincular catalog_items existentes a sus localidades por nombre
        session.execute(text("""
            UPDATE catalog_items ci
            SET locality_id = l.id
            FROM localities l
            WHERE ci.name ILIKE '%' || l.name || '%'
              AND ci.locality_id IS NULL
              AND ci.item_type != 'event'
        """))
        
        session.commit()
        print("Seeding and basic linking completed.")

if __name__ == "__main__":
    seed()
