
import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.ciudad import Ciudad

def seed_aysen():
    db = SessionLocal()
    try:
        ciudades_aysen = [
            # Principales
            {"nombre": "Coyhaique", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Puerto Aysén", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Puerto Chacabuco", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Balmaceda", "region": "Aysén", "pais": "Chile"},
            
            # Carretera Austral Norte
            {"nombre": "La Junta", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Puyuhuapi", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Puerto Raúl Marín Balmaceda", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Lago Verde", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Puerto Cisnes", "region": "Aysén", "pais": "Chile"},
            
            # Carretera Austral Sur
            {"nombre": "Villa Cerro Castillo", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Puerto Ingeniero Ibáñez", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Chile Chico", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Bahía Murta", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Puerto Río Tranquilo", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Puerto Guadal", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Cochrane", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Caleta Tortel", "region": "Aysén", "pais": "Chile"},
            {"nombre": "Villa O'Higgins", "region": "Aysén", "pais": "Chile"},
        ]
        
        print("Seeding Aysén cities...")
        count = 0
        for c in ciudades_aysen:
            exists = db.query(Ciudad).filter(Ciudad.nombre == c["nombre"]).first()
            if not exists:
                new_city = Ciudad(**c)
                db.add(new_city)
                count += 1
                
        db.commit()
        print(f"Added {count} cities.")
        
    except Exception as e:
        print(f"Error seeding cities: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_aysen()
