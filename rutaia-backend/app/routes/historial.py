# app/routes/historial.py

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db
from app.models.message import Message
from app.models.historia_viaje import HistoriaViaje
from app.schemas.message import MessageResponse
from app.schemas.historia import HistoriaEvento  # Schema que definiremos abajo

router = APIRouter(
    prefix="/historial",
    tags=["historial"],
)

@router.get(
    "/chat",
    response_model=List[MessageResponse],
    summary="Obtener historial de chat"
)
def get_chat_history(db: Session = Depends(get_db)):
    """
    Devuelve todos los mensajes de chat guardados.
    """
    return db.query(Message).all()


@router.get(
    "/plan/{plan_id}",
    response_model=List[HistoriaEvento],
    summary="Obtener bitácora de un plan de viaje"
)
def get_plan_history(
    plan_id: str = Path(..., description="ID de la planificación"),
    db: Session = Depends(get_db)
):
    """
    Devuelve todos los eventos de historia (añadidos/eliminados)
    para la planificación indicada, ordenados por fecha.
    """
    eventos = (
        db.query(HistoriaViaje)
          .filter(HistoriaViaje.plan_id == plan_id)
          .order_by(HistoriaViaje.timestamp)
          .all()
    )
    return eventos
