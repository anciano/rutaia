"""
Stage 8a Data Migration Script
Migrates ciudades from String PK to Integer PK, creates categorias table,
and updates all FK references in lugares and user_plans.

Run AFTER alembic upgrade head.
"""
import sys, os
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.models.database import SessionLocal, engine

CATEGORIAS_SEED = [
    ("alojamiento",  "pi-home"),
    ("cultura",      "pi-building"),
    ("naturaleza",   "pi-globe"),
    ("gastronomía",  "pi-star"),
    ("aventura",     "pi-bolt"),
    ("historia",     "pi-book"),
    ("transporte",   "pi-car"),
    ("entretenimiento", "pi-ticket"),
]

CIUDADES_SEED = [
    ("Santiago",    "Metropolitana", "Chile"),
    ("Valparaíso",  "Valparaíso",    "Chile"),
]

# Old slug → new integer id mapping
CIUDAD_SLUG_MAP = {
    "santiago":   1,
    "valparaiso": 2,
    "valparaíso": 2,
}

CATEGORIA_NAME_MAP = {}  # will be filled after insert

def run():
    db = SessionLocal()
    try:
        print("=== Stage 8a Data Migration ===")

        # 1. Insert categorias
        print("\n[1] Seeding categorias...")
        for nombre, icono in CATEGORIAS_SEED:
            existing = db.execute(text("SELECT id FROM categorias WHERE nombre = :n"), {"n": nombre}).fetchone()
            if not existing:
                db.execute(text("INSERT INTO categorias (nombre, icono) VALUES (:n, :i)"), {"n": nombre, "i": icono})
        db.commit()

        # Build categoria name → id map
        rows = db.execute(text("SELECT id, nombre FROM categorias")).fetchall()
        for row in rows:
            CATEGORIA_NAME_MAP[row[1].lower()] = row[0]
        print(f"   Categorias: {CATEGORIA_NAME_MAP}")

        # 2. Insert new ciudades with integer IDs
        print("\n[2] Seeding ciudades with integer IDs...")
        for nombre, region, pais in CIUDADES_SEED:
            existing = db.execute(text("SELECT id FROM ciudades WHERE nombre = :n AND pais = :p"), {"n": nombre, "p": pais}).fetchone()
            if not existing:
                db.execute(text("INSERT INTO ciudades (nombre, region, pais, activa) VALUES (:n, :r, :p, true)"), {"n": nombre, "r": region, "p": pais})
        db.commit()

        # Verify IDs
        rows = db.execute(text("SELECT id, nombre FROM ciudades")).fetchall()
        print(f"   Ciudades: {[(r[0], r[1]) for r in rows]}")

        # 3. Update lugares.ciudad_id (String slug → Integer)
        print("\n[3] Migrating lugares.ciudad_id...")
        lugares = db.execute(text("SELECT id, ciudad_id, categoria FROM lugares")).fetchall()
        updated = 0
        for lugar in lugares:
            lid, old_ciudad, old_cat = lugar[0], lugar[1], lugar[2]

            # Map ciudad
            new_ciudad_id = None
            if old_ciudad:
                slug = str(old_ciudad).lower().strip()
                new_ciudad_id = CIUDAD_SLUG_MAP.get(slug)

            # Map categoria
            new_cat_id = None
            if old_cat:
                cat_key = str(old_cat).lower().strip()
                # Try exact match first, then partial
                new_cat_id = CATEGORIA_NAME_MAP.get(cat_key)
                if not new_cat_id:
                    for k, v in CATEGORIA_NAME_MAP.items():
                        if k in cat_key or cat_key in k:
                            new_cat_id = v
                            break

            db.execute(
                text("UPDATE lugares SET ciudad_id = :c, categoria_id = :ci WHERE id = :id"),
                {"c": new_ciudad_id, "ci": new_cat_id, "id": lid}
            )
            updated += 1

        db.commit()
        print(f"   Updated {updated} lugares")

        # 4. Update user_plans.origen_id (String slug → Integer)
        print("\n[4] Migrating user_plans.origen_id...")
        plans = db.execute(text("SELECT id, origen_id FROM user_plans")).fetchall()
        plan_updated = 0
        for plan in plans:
            pid, old_origen = plan[0], plan[1]
            if old_origen:
                slug = str(old_origen).lower().strip()
                new_id = CIUDAD_SLUG_MAP.get(slug)
                if new_id:
                    db.execute(
                        text("UPDATE user_plans SET origen_id = :o WHERE id = :id"),
                        {"o": new_id, "id": pid}
                    )
                    plan_updated += 1

        db.commit()
        print(f"   Updated {plan_updated} user_plans")

        print("\n✅ Migration complete!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run()
