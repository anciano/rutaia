# app/seeds/hospedajes.py
from app.models.database import SessionLocal
from app.models.hospedaje import Hospedaje

DATA = [
    {
        "nombre": "Hostal Patagonia",
        "ubicacion": "Coyhaique centro",
        "precio_noche": 45000,
        "rating": 4.2,
        "descripcion": "Hostal acogedor en el corazón de la ciudad",
        "fotos_url": ["https://.../foto1.jpg", "https://.../foto2.jpg"]
    },
    {
        "nombre": "Cabañas Lago Verde",
        "ubicacion": "Lago General Carrera",
        "precio_noche": 80000,
        "rating": 4.8,
        "descripcion": "Cabañas frente al lago con vistas panorámicas",
        "fotos_url": ["https://.../cabaña1.jpg"]
    },
    # … otros alojamientos …
]

def seed_hospedajes():
    session = SessionLocal()
    for item in DATA:
        obj = Hospedaje(**item)
        session.merge(obj)
    session.commit()
    session.close()
    print("Seed hospedajes completada.")

if __name__ == "__main__":
    seed_hospedajes()