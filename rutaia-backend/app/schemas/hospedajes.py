# app/schemas/hospedajes.py

from pydantic import BaseModel
from typing import Optional, List

class Hospedaje(BaseModel):
    id: int
    nombre: str
    ubicacion: Optional[str]
    precio_noche: Optional[int]
    rating: Optional[float]
    descripcion: Optional[str]
    fotos_url: Optional[List[str]]

    class Config:
        orm_mode = True