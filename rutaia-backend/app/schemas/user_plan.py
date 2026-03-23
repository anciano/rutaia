from pydantic import BaseModel
from typing import List
from datetime import date

class UserPlanCreate(BaseModel):
    user_id: str
    origen: str
    dias: int
    presupuesto: int
    preferencias: List[str]
    fecha_inicio: date
    fecha_fin: date
    transport_mode: str = None