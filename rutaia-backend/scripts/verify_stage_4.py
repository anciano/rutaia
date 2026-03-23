# scripts/verify_stage_4.py

import sys
import os
from datetime import date, time

# Add project root to sys.path
sys.path.append(os.getcwd())

import app.models # Load all models
from app.models.database import Base, SessionLocal
from app.models import Ciudad, Lugar, Actividad, UserPlan, User
from app.engine.orchestrator import ItineraryEngine

# Debug registry
print("Registered models:", Base.registry.mappers)

def verify():
    db = SessionLocal()
    try:
        # 1. Create Test City
        v_city = db.query(Ciudad).filter(Ciudad.nombre == "Valparaíso").first()
        if not v_city:
            v_city = Ciudad(nombre="Valparaíso", region="Valparaíso")
            db.add(v_city)
            db.flush()
        
        # 2. Create Test Items
        l1 = db.query(Lugar).filter(Lugar.nombre == "Cerro Alegre").first()
        if not l1:
            l1 = Lugar(
                nombre="Cerro Alegre", 
                ciudad_id=v_city.id, 
                categoria="turismo", 
                precio_aprox=5000,
                estimated_duration_minutes=120,
                calificacion=4.8
            )
            db.add(l1)

        a1 = db.query(Actividad).filter(Actividad.nombre == "Tour de Graffitis").first()
        if not a1:
            a1 = Actividad(
                nombre="Tour de Graffitis",
                ciudad_id=v_city.id,
                costo_aprox=15000,
                estimated_duration_minutes=180,
                rating_promedio=4.9
            )
            db.add(a1)
        
        # 3. Create Test User & Plan
        user = db.query(User).first()
        if not user:
            print("No user found in DB. Please run seeds first.")
            return

        plan = UserPlan(
            user_id=user.id,
            origen_id=v_city.id,
            dias=2,
            presupuesto=50000,
            fecha_inicio=date(2025, 10, 1),
            fecha_fin=date(2025, 10, 3),
            participantes={},
            preferencias={"tags": ["turismo"]},
            budget_clp=50000,
            total_days=2
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        
        print(f"Test Plan created: {plan.id}")

        # 4. Trigger Generation
        engine = ItineraryEngine(db)
        engine.generate(plan.id, mode="replace")
        
        # 5. Verify Results
        db.refresh(plan)
        print(f"Generation Version: {plan.generation_version}")
        print(f"Days generated: {len(plan.days)}")
        
        for d in plan.days:
            print(f"  Day {d.number}: {len(d.items)} items")
            for item in d.items:
                print(f"    - [{item.item_type}] start: {item.start_time}, end: {item.end_time}, order: {item.sort_order}")

    except Exception as e:
        db.rollback()
        print(f"Verification FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify()
