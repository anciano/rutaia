import os
import sys
from decimal import Decimal

# Add current directory to path
sys.path.append(os.getcwd())

from app.models.database import SessionLocal
from app.models.ciudad import Ciudad
from app.models.lugar import Lugar

def seed_data():
    db = SessionLocal()
    try:
        print("Seeding cities and places...")
        
        # 1. Cities
        stgo = db.query(Ciudad).filter(Ciudad.id == 'santiago').first()
        if not stgo:
            stgo = Ciudad(id='santiago', nombre='Santiago', region='Metropolitana', activa=True)
            db.add(stgo)
        
        valpo = db.query(Ciudad).filter(Ciudad.id == 'valparaiso').first()
        if not valpo:
            valpo = Ciudad(id='valparaiso', nombre='Valparaíso', region='Valparaíso', activa=True)
            db.add(valpo)
        
        db.commit()
        db.refresh(stgo)
        db.refresh(valpo)

        # 2. Places - Santiago
        lugares_stgo = [
            ("Cerro Santa Lucía", "Hito histórico y jardín panorámico en el centro.", "naturaleza", -33.4411, -70.6439, 0, 90),
            ("Museo Nacional de Bellas Artes", "Cultura y arquitectura neoclásica.", "cultura", -33.4348, -70.6445, 2000, 120),
            ("Parque Metropolitano (Teleférico)", "Vistas increíbles de la ciudad y senderos.", "naturaleza", -33.4225, -70.6322, 8000, 180),
            ("Mercado Central", "Gastronomía típica y pescados frescos.", "gastronomía", -33.4339, -70.6508, 15000, 90),
            ("Barrio Lastarria", "Caminata cultural, cafés y pequeñas tiendas.", "cultura", -33.4369, -70.6405, 0, 120),
            ("Sky Costanera", "El mirador más alto de Sudamérica.", "aventura", -33.4170, -70.6065, 18000, 90),
            ("Palacio de La Moneda", "Centro cívico e histórico de Chile.", "historia", -33.4429, -70.6538, 0, 60),
            ("Centro Cultural La Moneda", "Exposiciones internacionales de alto nivel.", "cultura", -33.4430, -70.6539, 3000, 120),
        ]

        # Places - Valparaíso
        lugares_valpo = [
            ("Cerro Alegre", "Famoso por sus murales y ascensores antiguos.", "cultura", -33.0401, -71.6288, 0, 150),
            ("La Sebastiana (Casa Neruda)", "Hogar del poeta Pablo Neruda con vista al mar.", "cultura", -33.0522, -71.6139, 7000, 90),
            ("Paseo 21 de Mayo", "El mejor mirador del puerto y la bahía.", "naturaleza", -33.0315, -71.6268, 0, 60),
            ("Ascensor Artillería", "Patrimonio histórico para subir al mirador.", "historia", -33.0319, -71.6282, 500, 30),
            ("Muelle Prat", "Botes turísticos y vida portuaria.", "aventura", -33.0375, -71.6275, 5000, 60),
            ("Puerto Deportivo Barón", "Kayaks y actividades acuáticas.", "aventura", -33.0425, -71.6095, 25000, 120),
        ]

        for nombre, desc, cat, lat, lng, precio, dur in lugares_stgo:
            if not db.query(Lugar).filter(Lugar.nombre == nombre).first():
                db.add(Lugar(
                    ciudad_id='santiago',
                    nombre=nombre,
                    descripcion_breve=desc,
                    categoria=cat,
                    latitud=Decimal(str(lat)),
                    longitud=Decimal(str(lng)),
                    precio_aprox=precio,
                    estimated_duration_minutes=dur,
                    calificacion=4.5
                ))

        for nombre, desc, cat, lat, lng, precio, dur in lugares_valpo:
            if not db.query(Lugar).filter(Lugar.nombre == nombre).first():
                db.add(Lugar(
                    ciudad_id='valparaiso',
                    nombre=nombre,
                    descripcion_breve=desc,
                    categoria=cat,
                    latitud=Decimal(str(lat)),
                    longitud=Decimal(str(lng)),
                    precio_aprox=precio,
                    estimated_duration_minutes=dur,
                    calificacion=4.8
                ))

        db.commit()
        print("Success: Cities and places seeded.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
