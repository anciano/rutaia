import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.models.database import SessionLocal
from app.models.user_plan import UserPlan
from app.models.day import PlanDay
from app.models.plan_item import PlanItem
from app.models.plan_detail import PlaceItem, ActivityItem, TransportSegment, LodgingItem, TravelLog
from app.models.plan_lugares import PlanLugar
from app.models.plan_hospedaje import PlanHospedaje
from app.models.plan_actividades import PlanActividad
from app.models.plan_transporte import PlanTransporte
from app.models.historia_viaje import HistoriaViaje

def clean_db():
    db = SessionLocal()
    try:
        print("Cleaning up planning data...")
        
        # Order matters for foreign keys - delete children first
        db.query(PlanItem).delete()
        db.query(PlaceItem).delete()
        db.query(ActivityItem).delete()
        db.query(TransportSegment).delete()
        db.query(LodgingItem).delete()
        db.query(TravelLog).delete()
        
        db.query(PlanDay).delete()
        
        # Legacy items
        db.query(PlanLugar).delete()
        db.query(PlanHospedaje).delete()
        db.query(PlanActividad).delete()
        db.query(PlanTransporte).delete()
        
        # Logs and core plans
        db.query(HistoriaViaje).delete()
        db.query(UserPlan).delete()
        
        db.commit()
        print("Success: All planning data has been cleared.")
    except Exception as e:
        db.rollback()
        print(f"Error during clean-up: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_db()
