# scripts/unify_taxonomy.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.database import SessionLocal
from app.models.catalog_category import CatalogCategory
from app.models.catalog_item import CatalogItem

def unify():
    db = SessionLocal()
    try:
        print("🛠️ Unificando Taxonomía (v3)...")
        
        # 1. Definir/Asegurar Raíces (Mapeo de item_type)
        # Usaremos nombres descriptivos para las raíces
        roots_config = {
            "place": "Lugar",
            "activity": "Actividad",
            "lodging": "Hospedaje",
            "transport": "Transporte",
            "route": "Ruta"
        }
        
        root_ids = {}
        for itype, name in roots_config.items():
            cat = db.query(CatalogCategory).filter_by(name=name).first()
            if not cat:
                cat = CatalogCategory(name=name, parent_id=None)
                db.add(cat)
                db.flush()
            else:
                cat.parent_id = None # Asegurar que es raíz
            root_ids[itype] = cat.id
            # Guardamos el item_type original en un metadato si fuera necesario, 
            # pero por ahora lo mapearemos por nombre en el frontend.

        # 2. Re-mapear categorías existentes como hijos
        mappings = {
            "Glaciares": "place",
            "Parques Nacionales": "place",
            "Restaurantes": "place",
            "Gasolineras": "place",
            "Comida": "place",
            "Lugar": "place", # Si ya existe uno llamado Lugar que no es la raíz, lo movemos
            
            "Kayak": "activity",
            "Escalada": "activity",
            "Paseos": "activity",
            "Actividades": "activity",
            
            "Camping": "lodging",
            "Campings": "lodging",
            "Alojamiento": "lodging",
            
            "Buses": "transport",
            "Barco": "transport",
            "Transporte": "transport"
        }

        all_cats = db.query(CatalogCategory).all()
        for cat in all_cats:
            if cat.name in root_ids.values(): continue # Saltar las raíces que acabamos de asegurar
            
            target_type = mappings.get(cat.name)
            if target_type:
                cat.parent_id = root_ids[target_type]
            elif cat.name not in roots_config.values():
                # Si no tiene mapeo y no es raíz, lo dejamos como hijo de "Lugar" por defecto
                cat.parent_id = root_ids["place"]

        # 3. Limpieza de duplicados obvios (opcional pero recomendado)
        # 'Camping' vs 'Campings'
        c1 = db.query(CatalogCategory).filter_by(name="Camping").first()
        c2 = db.query(CatalogCategory).filter_by(name="Campings").first()
        if c1 and c2:
            db.query(CatalogItem).filter_by(category_id=c2.id).update({"category_id": c1.id})
            db.delete(c2)

        db.commit()
        print("✅ Taxonomía unificada exitosamente.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error en unificación: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    unify()
