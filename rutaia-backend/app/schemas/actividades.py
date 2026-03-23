# app/schemas/actividades.py

from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

class Actividad(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    duracion_estimada_horas: Optional[float]
    nivel_intensidad: Optional[str]
    costo_aprox: Optional[int]
    latitud: Optional[Decimal]
    longitud: Optional[Decimal]
    fotos_url: Optional[List[str]]
    rating_promedio: Optional[float]

    class Config:
        orm_mode = True