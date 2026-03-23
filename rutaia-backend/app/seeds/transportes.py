# app/seeds/transportes.py
from app.models.database import SessionLocal
from app.models.transporte import Transporte

DATA = [
    {
        "tipo": "auto",
        "descripcion": "Alquiler de automóvil compacto",
        "costo_estandar_por_km": 250,
        "velocidad_promedio_kmh": 60.0
    },
    {
        "tipo": "bus_interurbano",
        "descripcion": "Bus local entre ciudades principales",
        "costo_estandar_por_tramo": 10000,
        "velocidad_promedio_kmh": 80.0
    },
    {
        "tipo": "transfer_privado",
        "descripcion": "Servicio de transfer privado puerta a puerta",
        "costo_estandar_por_tramo": 40000,
        "velocidad_promedio_kmh": 70.0
    },
    # … otros modos …
]

def seed_transportes():
    session = SessionLocal()
    for item in DATA:
        obj = Transporte(**item)
        session.merge(obj)
    session.commit()
    session.close()
    print("Seed transportes completada.")

if __name__ == "__main__":
    seed_transportes()