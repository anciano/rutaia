# scripts/data_migration_v2.py

import os
import sys
from datetime import timedelta
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Attempt to initialize through app to get all mappers configured
try:
    from app.main import app
except Exception as e:
    print(f"Warning importing app: {e}")

from app.models.database import SessionLocal, engine
import app.models as models

def migrate():
    load_dotenv()
    db = SessionLocal()
    try:
        plans = db.query(models.UserPlan).all()
        print(f"Found {len(plans)} plans to migrate.")

        for plan in plans:
            print(f"Migrating plan: {plan.id}")
            # 1. Create days 1..N
            days_count = plan.dias or 1
            day_map = {} # map day_number -> PlanDay.id
            
            for i in range(1, days_count + 1):
                # Calculate date if possible
                current_date = plan.fecha_inicio + timedelta(days=i-1) if plan.fecha_inicio else None
                
                # Check for existing day to be idempotent
                existing_day = db.query(models.PlanDay).filter_by(plan_id=plan.id, number=i).first()
                if not existing_day:
                    day_obj = models.PlanDay(
                        plan_id=plan.id,
                        number=i,
                        date=current_date
                    )
                    db.add(day_obj)
                    db.flush() # get ID
                    day_map[i] = day_obj.id
                else:
                    day_map[i] = existing_day.id

            # 2. Migrate Lugares
            lugares = db.query(models.PlanLugar).filter_by(plan_id=plan.id).all()
            for idx, item in enumerate(lugares):
                day_num = item.day if item.day in day_map else 1
                new_item = models.PlanItem(
                    day_id=day_map[day_num],
                    item_type="place",
                    place_id=item.lugar_id,
                    sort_order=idx,
                    cost_clp=item.costo_final or 0,
                    metadata_json={"nombre_custom": item.nombre_custom, "ubicacion_custom": item.ubicacion_custom}
                )
                db.add(new_item)

            # 3. Migrate Actividades
            actividades = db.query(models.PlanActividad).filter_by(plan_id=plan.id).all()
            for idx, item in enumerate(actividades):
                day_num = 1 
                new_item = models.PlanItem(
                    day_id=day_map[day_num],
                    item_type="activity",
                    activity_id=item.actividad_id,
                    sort_order=idx + 100,
                    cost_clp=item.costo_final or 0,
                    metadata_json={"nombre_custom": item.nombre_custom}
                )
                db.add(new_item)

            # 4. Migrate Hospedaje
            hospedajes = db.query(models.PlanHospedaje).filter_by(plan_id=plan.id).all()
            for idx, item in enumerate(hospedajes):
                day_num = 1
                if plan.fecha_inicio and item.fecha_check_in:
                    day_num = (item.fecha_check_in - plan.fecha_inicio).days + 1
                    if day_num < 1: day_num = 1
                    if day_num > days_count: day_num = days_count

                new_item = models.PlanItem(
                    day_id=day_map[day_num],
                    item_type="lodging",
                    lodging_id=item.hospedaje_id,
                    sort_order=idx + 200,
                    cost_clp=item.costo_final or 0,
                    metadata_json={"fecha_check_in": str(item.fecha_check_in), "fecha_check_out": str(item.fecha_check_out)}
                )
                db.add(new_item)

            # 5. Migrate Transporte
            transportes = db.query(models.PlanTransporte).filter_by(plan_id=plan.id).all()
            for idx, item in enumerate(transportes):
                day_num = 1
                new_item = models.PlanItem(
                    day_id=day_map[day_num],
                    item_type="transport",
                    transport_id=item.transporte_id,
                    sort_order=idx + 300,
                    cost_clp=int(item.costo_final or 0),
                    metadata_json={"origen_custom": item.origen_custom, "destino_custom": item.destino_custom}
                )
                db.add(new_item)

        db.commit()
        print("Migration completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
