from app.models.database import SessionLocal
from app.models.lugar import Lugar
from app.models.actividad import Actividad
from app.models.ciudad import Ciudad

def check_counts():
    db = SessionLocal()
    try:
        ciudades = db.query(Ciudad).count()
        lugares = db.query(Lugar).count()
        actividades = db.query(Actividad).count()
        print(f"Ciudades: {ciudades}")
        print(f"Lugares: {lugares}")
        print(f"Actividades: {actividades}")
        
        if lugares == 0:
            print("WARNING: No lugares found in database.")
    finally:
        db.close()

if __name__ == "__main__":
    check_counts()
