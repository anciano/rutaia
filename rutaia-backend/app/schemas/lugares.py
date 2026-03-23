# app/schemas/lugares.py

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class LugarBase(BaseModel):
    ciudad_id: Optional[int] = None
    categoria_id: Optional[int] = None
    categoria: Optional[str] = None  # kept for legacy/display
    nombre: str
    descripcion_breve: Optional[str] = None
    precio_aprox: Optional[int] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    calificacion: Optional[float] = None
    duracion_estimada_horas: Optional[float] = None
    estimated_duration_minutes: Optional[int] = None
    rango_etario: Optional[str] = None
    accesibilidad: Optional[str] = None
    direccion: Optional[str] = None

class Lugar(LugarBase):
    id: int

    class Config:
        from_attributes = True

class LugarCreate(LugarBase):
    pass

class LugarUpdate(BaseModel):
    ciudad_id: Optional[int] = None
    categoria_id: Optional[int] = None
    categoria: Optional[str] = None
    nombre: Optional[str] = None
    descripcion_breve: Optional[str] = None
    precio_aprox: Optional[int] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    calificacion: Optional[float] = None
    duracion_estimada_horas: Optional[float] = None
    estimated_duration_minutes: Optional[int] = None
    rango_etario: Optional[str] = None
    accesibilidad: Optional[str] = None
    direccion: Optional[str] = None

    class Config:
        from_attributes = True