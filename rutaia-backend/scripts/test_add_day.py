
import sys
import os
import uuid
# Agregar el directorio raíz al path
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.models.database import SessionLocal, engine, Base
from app.models.user_plan import UserPlan
from app.models.day import PlanDay
from app.models.ciudad import Ciudad
from app.models.user import User
from datetime import date

def test_add_day():
    db = SessionLocal()
    try:
        # 1. Crear usuario si no existe
        user = db.query(User).filter(User.correo == "test@example.com").first()
        if not user:
            print("Creating test user")
            user = User(
                id="test_user_id",
                correo="test@example.com",
                nombre="Test User",
                provider="google"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 2. Crear un plan dummy
        plan_id = str(uuid.uuid4())
        
        # Buscar una ciudad existente
        ciudad = db.query(Ciudad).first()
        if not ciudad:
            print("No cities found, creating one")
            ciudad = Ciudad(id=1, nombre="Test City", region="Test Region", pais="Chile")
            db.add(ciudad)
            db.commit()
            db.refresh(ciudad)
            
        print(f"Using city_id: {ciudad.id}")

        new_plan = UserPlan(
            id=plan_id,
            user_id="test_user_id", 
            origen_id=ciudad.id,
            dias=5,
            presupuesto=100000,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            estado="borrador",
            participantes=[],
            preferencias=[]
        )
        db.add(new_plan)
        db.commit()
        print(f"Plan created: {plan_id}")

        # 3. Simular add_day logic
        max_day = db.query(PlanDay).filter(PlanDay.plan_id == plan_id).order_by(PlanDay.number.desc()).first()
        new_number = (max_day.number + 1) if max_day else 1
        
        print(f"Adding day number: {new_number}")
        
        new_day = PlanDay(plan_id=plan_id, number=new_number)
        db.add(new_day)
        
        # Update plan
        plan = db.get(UserPlan, plan_id)
        plan.total_days = new_number
        plan.dias = new_number
        db.add(plan)
        
        db.commit()
        print("Day added successfully")
        
        # Verify
        saved_day = db.query(PlanDay).filter(PlanDay.plan_id == plan_id).first()
        if saved_day:
            print(f"Verified day in DB: ID={saved_day.id}, Number={saved_day.number}")
        else:
            print("ERROR: Day not found in DB")

        # Cleanup
        # Borrar items antes del dia si hubiera (aqui no hay)
        db.delete(saved_day) # Borrar dia
        db.delete(plan)      # Borrar plan
        # No borramos user ni ciudad
        db.commit()
        print("Cleanup done")

    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_add_day()
