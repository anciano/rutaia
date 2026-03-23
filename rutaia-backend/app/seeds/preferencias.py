from sqlalchemy import Column, Integer, String, Boolean
from app.models.database import Base, SessionLocal
from app.models.preferencia import Preferencia
from uuid import uuid4

# Carga inicial (seed)
preferencias = [
    {"id": str(uuid4()),"nombre": "Exploración aventurera", "descripcion": "Dispuesto a asumir desafíos físicos, explorar lugares remotos o con acceso difícil.", "activa": True},
    {"id": str(uuid4()),"nombre": "Conexión con la naturaleza", "descripcion": "Interés por ambientes naturales tranquilos, caminatas, observación de flora y fauna.", "activa": True},
    {"id": str(uuid4()),"nombre": "Confort y descanso", "descripcion": "Prefiere alojamientos cómodos, evitar traslados complejos, valora el descanso.", "activa": True},
    {"id": str(uuid4()),"nombre": "Autenticidad local", "descripcion": "Busca experiencias locales reales: comida típica, contacto con comunidades.", "activa": True},
    {"id": str(uuid4()),"nombre": "Actividades acuáticas", "descripcion": "A gusto con kayak, navegación, pesca o simplemente estar cerca del agua.", "activa": True},
    {"id": str(uuid4()),"nombre": "Espíritu fotográfico", "descripcion": "Le motiva capturar paisajes, amaneceres, arquitectura, cultura visual del viaje.", "activa": True},
    {"id": str(uuid4()),"nombre": "Alta movilidad", "descripcion": "Prefiere itinerarios con múltiples destinos, no le molesta cambiar de lugar seguido.", "activa": True},
    {"id": str(uuid4()),"nombre": "Bajo impacto ambiental", "descripcion": "Prefiere opciones sostenibles, evita actividades invasivas o con impacto ecológico considerable.", "activa": True},
    {"id": str(uuid4()),"nombre": "Flexibilidad en horarios", "descripcion": "No requiere itinerarios estrictos; cómodo con cambios, demoras o actividades espontáneas.", "activa": True},
    {"id": str(uuid4()),"nombre": "Interés cultural", "descripcion": "Busca museos, historia local, arquitectura patrimonial o centros culturales.", "activa": True},
    {"id": str(uuid4()),"nombre": "Gastronomía regional", "descripcion": "Disfruta descubrir platos típicos, productos locales, mercados o rutas gastronómicas.", "activa": True},
    {"id": str(uuid4()),"nombre": "Minimalismo logístico", "descripcion": "Prefiere viajes livianos, evita llevar mucho equipaje o depender de múltiples reservas.", "activa": True},
    {"id": str(uuid4()),"nombre": "Desconexión digital", "descripcion": "Busca lugares con poca conectividad, silencio, ideal para desconectar del celular e internet.", "activa": True},
    {"id": str(uuid4()),"nombre": "Sensibilidad climática", "descripcion": "Evita condiciones climáticas extremas como lluvia, viento o frío excesivo.", "activa": True}
]

def cargar_preferencias():
    db = SessionLocal()
    for pref in preferencias:
        existe = db.query(Preferencia).filter_by(nombre=pref["nombre"]).first()
        if not existe:
            db.add(Preferencia(**pref))
    db.commit()
    db.close()
