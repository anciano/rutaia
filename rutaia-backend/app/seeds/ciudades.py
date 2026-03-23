from app.models.database import SessionLocal
from app.models.ciudad import Ciudad

def cargar_ciudades():
    ciudades = [
        'Coyhaique', 'Puerto Aysén', 'Chile Chico', 'Cochrane', 'Puerto Cisnes',
        'Puerto Ibáñez', 'Villa O’Higgins', 'Caleta Tortel', 'Río Ibáñez',
        'Puerto Guadal', 'Bahía Murta', 'Puerto Bertrand', 'Lago Verde',
        'Puerto Tranquilo', 'Villa Cerro Castillo', 'La Junta', 'Puyuhuapi',
        'Raúl Marín Balmaceda'
    ]

    db = SessionLocal()
    for nombre in ciudades:
        if not db.query(Ciudad).filter_by(nombre=nombre).first():
            db.add(Ciudad(nombre=nombre, region='Aysén'))
    db.commit()
    db.close()