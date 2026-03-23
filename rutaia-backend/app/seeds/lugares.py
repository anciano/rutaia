# app/seeds/lugares.py
from app.models.database import SessionLocal
from app.models.lugar import Lugar

DATA = [
    {
        "categoria": "naturaleza",
        "nombre": "Cascada Río de Los Ciervos",
        "descripcion_breve": "Impresionante salto de agua en entorno bosque nativo",
        "precio_aprox": 0,
        "latitud": -45.4132,
        "longitud": -72.7391,
        "calificacion": 4.7,
        "duracion_estimada_horas": 1.5,
    },
    {
        "categoria": "histórico",
        "nombre": "Fuerte Borgoño",
        "descripcion_breve": "Ruinas de una antigua fortificación colonial",
        "precio_aprox": 2000,
        "latitud": -45.4230,
        "longitud": -72.3678,
        "calificacion": 4.3,
        "duracion_estimada_horas": 2.0,
    },
    # … añade el resto de tus 63 lugares …
]

def seed_lugares():
    session = SessionLocal()
    for item in DATA:
        obj = Lugar(**item)
        session.merge(obj)
    session.commit()
    session.close()
    print("Seed lugares completada.")

if __name__ == "__main__":
    seed_lugares()