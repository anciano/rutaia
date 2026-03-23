# app/seeds/actividades.py
from app.models.database import SessionLocal
from app.models.actividad import Actividad

DATA = [
    {
        "nombre": "Trekking al Valle Exploradores",
        "descripcion": "Caminata de día completo por senderos glaciares",
        "duracion_estimada_horas": 8.0,
        "nivel_intensidad": "alto",
        "costo_aprox": 30000,
        "latitud": -46.1671,
        "longitud": -72.5695,
        "fotos_url": ["https://.../trek1.jpg"],
        "rating_promedio": 4.9
    },
    {
        "nombre": "Kayak en Río Simpson",
        "descripcion": "Paseo en kayak suave por aguas cristalinas",
        "duracion_estimada_horas": 2.5,
        "nivel_intensidad": "medio",
        "costo_aprox": 20000,
        "latitud": -45.5833,
        "longitud": -72.0667,
        "fotos_url": ["https://.../kayak1.jpg"],
        "rating_promedio": 4.7
    },
    # … más actividades …
]

def seed_actividades():
    session = SessionLocal()
    for item in DATA:
        obj = Actividad(**item)
        session.merge(obj)
    session.commit()
    session.close()
    print("Seed actividades completada.")

if __name__ == "__main__":
    seed_actividades()