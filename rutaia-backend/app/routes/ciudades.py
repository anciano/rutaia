from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.ciudad import Ciudad

router = APIRouter()

@router.get("/ciudades")
def obtener_ciudades(db: Session = Depends(get_db)):
    ciudades = db.query(Ciudad).filter(Ciudad.activa == True).order_by(Ciudad.nombre).all()
    return [{"id": c.id, "nombre": c.nombre, "region": c.region} for c in ciudades]