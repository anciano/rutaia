# app/schemas/historia.py

from pydantic import BaseModel
from datetime import datetime

class HistoriaEvento(BaseModel):
    id: int
    plan_id: str
    categoria: str
    accion: str
    elemento_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
