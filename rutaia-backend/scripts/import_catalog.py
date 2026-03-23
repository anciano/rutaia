"""
scripts/import_catalog.py

Import data from 'lista y categorias.xlsx' into the new unified catalog tables.
Run:  python scripts/import_catalog.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from app.models.database import SessionLocal
from app.models.catalog_category import CatalogCategory
from app.models.catalog_item import CatalogItem

EXCEL_PATH = r"C:\Proyectos\asesor\lista y categorias.xlsx"

# Mapping from Excel 'categoria' column to our item_type enum
CATEGORY_TO_TYPE = {
    "Lugar":        "place",
    "Ruta":         "route",
    "Hospedaje":    "lodging",
    "Camping":      "lodging",
    "Actividades":  "activity",
    "Escalada":     "activity",
    "Kayak":        "activity",
    "Barco":        "activity",
    "Transporte":   "transport",
}


def parse_cost(val):
    """Try to extract a numeric cost from text like '$25.000' or '25000'."""
    if pd.isna(val):
        return None
    s = str(val).replace("$", "").replace(".", "").replace(",", "").strip()
    try:
        return int(s)
    except ValueError:
        return None


def parse_duration(val):
    """Try to extract duration in minutes from text like '2 horas', '30 min', '1 día'."""
    if pd.isna(val):
        return None
    s = str(val).lower().strip()
    # Try "X horas"
    import re
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:hora|hrs|hr|h)', s)
    if m:
        return int(float(m.group(1).replace(",", ".")) * 60)
    m = re.search(r'(\d+)\s*(?:min)', s)
    if m:
        return int(m.group(1))
    m = re.search(r'(\d+)\s*(?:día|dia|d)', s)
    if m:
        return int(m.group(1)) * 480  # 8h per day
    return None


def run():
    db = SessionLocal()
    try:
        # ---- 1. Read Excel ----
        df = pd.read_excel(EXCEL_PATH, sheet_name="Master_v2")
        print(f"Read {len(df)} rows from Excel")

        # ---- 2. Create Categories ----
        unique_cats = df["categoria"].dropna().unique()
        cat_map = {}  # name -> CatalogCategory.id

        for cat_name in unique_cats:
            existing = db.query(CatalogCategory).filter(CatalogCategory.name == cat_name).first()
            if existing:
                cat_map[cat_name] = existing.id
            else:
                new_cat = CatalogCategory(name=cat_name)
                db.add(new_cat)
                db.flush()
                cat_map[cat_name] = new_cat.id
                print(f"  + Category: {cat_name} (id={new_cat.id})")

        db.commit()
        print(f"Categories created/found: {len(cat_map)}")

        # ---- 3. Import Items ----
        created = 0
        skipped = 0
        for _, row in df.iterrows():
            nombre = str(row.get("nombre", "")).strip()
            if not nombre:
                skipped += 1
                continue

            cat_name = str(row.get("categoria", "")).strip()
            item_type = CATEGORY_TO_TYPE.get(cat_name, "place")
            category_id = cat_map.get(cat_name)

            # Check for duplicate
            exists = db.query(CatalogItem).filter(
                CatalogItem.name == nombre,
                CatalogItem.item_type == item_type
            ).first()
            if exists:
                skipped += 1
                continue

            # Build extra metadata
            extra = {}
            for col in ["ubicacion", "horarios", "acceso_como_llegar", "recomendaciones", "tags"]:
                val = row.get(col)
                if pd.notna(val) and str(val).strip():
                    extra[col] = str(val).strip()

            item = CatalogItem(
                item_type=item_type,
                name=nombre,
                description=str(row.get("descripcion", "")).strip() if pd.notna(row.get("descripcion")) else None,
                category_id=category_id,
                lat=None,                                         # To be set via admin map picker
                lng=None,
                estimated_duration_minutes=parse_duration(row.get("duracion_aprox_clp")),
                approx_cost_clp=parse_cost(row.get("duracion_aprox_clp")),  # Column may contain cost data too
                is_active=True,
                extra=extra if extra else None,
            )
            db.add(item)
            created += 1

        db.commit()
        print(f"\nImport complete: {created} items created, {skipped} skipped (empty/duplicate)")

        # ---- 4. Summary ----
        total = db.query(CatalogItem).count()
        print(f"Total items in catalog_items: {total}")
        for t in ["place", "activity", "route", "transport", "lodging"]:
            count = db.query(CatalogItem).filter(CatalogItem.item_type == t).count()
            if count:
                print(f"  {t}: {count}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    run()
