# app/routes/transportes.py

from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db
from app.models.transporte import Transporte as TransporteModel
from app.schemas.transportes import Transporte

router = APIRouter(prefix="/transportes", tags=["transportes"])

@router.get(
    "/",
    response_model=List[Transporte],
    summary="Listar todos los modos de transporte"
)
def listar_transportes(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de transporte"),
    db: Session = Depends(get_db),
):
    q = db.query(TransporteModel)
    if tipo:
        q = q.filter(TransporteModel.tipo == tipo)
    return q.order_by(TransporteModel.tipo).all()

@router.get(
    "/{transporte_id}",
    response_model=Transporte,
    summary="Obtener detalle de un modo de transporte"
)
def obtener_transporte(
    transporte_id: int = Path(..., description="ID del modo de transporte"),
    db: Session = Depends(get_db),
):
    t = db.get(TransporteModel, transporte_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transporte no encontrado")
    return t