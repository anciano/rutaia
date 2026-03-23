# app/routes/actividades.py

from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db
from app.models.actividad import Actividad as ActividadModel
from app.schemas.actividades import Actividad

router = APIRouter(prefix="/actividades", tags=["actividades"])

@router.get(
    "/",
    response_model=List[Actividad],
    summary="Listar todas las actividades"
)
def listar_actividades(
    nivel_intensidad: Optional[str] = Query(
        None, description="Filtrar por nivel de intensidad (bajo, medio, alto)"
    ),
    max_duracion: Optional[float] = Query(
        None, description="Duración máxima en horas"
    ),
    db: Session = Depends(get_db),
):
    q = db.query(ActividadModel)
    if nivel_intensidad:
        q = q.filter(ActividadModel.nivel_intensidad == nivel_intensidad)
    if max_duracion is not None:
        q = q.filter(ActividadModel.duracion_estimada_horas <= max_duracion)
    return q.order_by(ActividadModel.nombre).all()


@router.get(
    "/{actividad_id}",
    response_model=Actividad,
    summary="Obtener detalle de una actividad"
)
def obtener_actividad(
    actividad_id: int = Path(..., description="ID de la actividad"),
    db: Session = Depends(get_db),
):
    a = db.get(ActividadModel, actividad_id)
    if not a:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return a