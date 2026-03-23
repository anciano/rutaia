# app/routes/hospedajes.py

from fastapi import APIRouter, Depends, Path, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db
from app.models.hospedaje import Hospedaje as HospedajeModel
from app.schemas.hospedajes import Hospedaje

router = APIRouter(prefix="/hospedajes", tags=["hospedajes"])

@router.get(
    "/",
    response_model=List[Hospedaje],
    summary="Listar todos los hospedajes"
)
def listar_hospedajes(
    min_precio: Optional[int] = Query(None, description="Filtrar por precio mínimo por noche"),
    max_precio: Optional[int] = Query(None, description="Filtrar por precio máximo por noche"),
    db: Session = Depends(get_db),
):
    q = db.query(HospedajeModel)
    if min_precio is not None:
        q = q.filter(HospedajeModel.precio_noche >= min_precio)
    if max_precio is not None:
        q = q.filter(HospedajeModel.precio_noche <= max_precio)
    return q.order_by(HospedajeModel.nombre).all()


@router.get(
    "/{hospedaje_id}",
    response_model=Hospedaje,
    summary="Obtener detalle de un hospedaje"
)
def obtener_hospedaje(
    hospedaje_id: int = Path(..., description="ID del hospedaje"),
    db: Session = Depends(get_db),
):
    h = db.get(HospedajeModel, hospedaje_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hospedaje no encontrado")
    return h