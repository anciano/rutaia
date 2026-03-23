from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.preferencia import Preferencia

router = APIRouter()

@router.get("/preferencias")
def obtener_preferencias(db: Session = Depends(get_db)):
    return db.query(Preferencia).filter_by(activa="true").all()