# app/schemas/transportes.py

from pydantic import BaseModel
from typing import Optional

class Transporte(BaseModel):
    id: int
    tipo: str
    descripcion: Optional[str]
    costo_estandar_por_km: Optional[float]
    costo_estandar_por_tramo: Optional[float]
    velocidad_promedio_kmh: Optional[float]

    class Config:
        orm_mode = True