# app/schemas/plan_detalle.py

from pydantic import BaseModel, conint
from datetime import datetime, date
from typing import List, Optional

#
# → Esquemas de creación (payloads para POST)
#

class LugarEnPlanCreate(BaseModel):
    lugar_id: Optional[int]
    nombre_custom: Optional[str]
    ubicacion_custom: Optional[str]
    day: conint(ge=1)                             # ← NUEVO
    horario_entrada: datetime
    duracion_horas: float
    costo_final: Optional[int]

class HospedajeEnPlanCreate(BaseModel):
    hospedaje_id: Optional[int]       # FK al maestro “hospedajes”
    nombre_custom: Optional[str]      # Nombre libre si es custom
    direccion_custom: Optional[str]   # Dirección libre si es custom
    fecha_check_in: date
    fecha_check_out: date
    costo_final: Optional[int]        # Override para custom; ignored si maestro

class ActividadEnPlanCreate(BaseModel):
    actividad_id: Optional[int]    # FK al maestro “actividades”
    nombre_custom: Optional[str]   # Nombre libre si es custom
    duracion_horas: float
    costo_final: Optional[int]     # Override para custom; ignored si maestro

class TransporteEnPlanCreate(BaseModel):
    transporte_id: Optional[int]        # FK al maestro “transportes”
    tipo_custom: Optional[str]          # Tipo libre si es custom
    origen_custom: Optional[str]        # Origen libre si es custom
    destino_custom: Optional[str]       # Destino libre si es custom
    tiempo_estimado_horas: float
    costo_final: Optional[float]        # Override para custom; ignored si maestro

#
# → Esquemas de respuesta (response_model)
#

class LugarEnPlan(BaseModel):
    id: int
    plan_id: str
    lugar_id: Optional[int]
    nombre_custom: Optional[str]
    ubicacion_custom: Optional[str]
    horario_entrada: datetime
    duracion_horas: float
    precio_base: int
    costo_final: int

    class Config:
        from_attributes = True

class HospedajeEnPlan(BaseModel):
    id: int
    plan_id: str
    hospedaje_id: Optional[int]
    nombre_custom: Optional[str]
    direccion_custom: Optional[str]
    fecha_check_in: date
    fecha_check_out: date
    noches: int
    precio_base: int
    costo_calculado: int
    costo_final: int

    class Config:
        from_attributes = True

class ActividadEnPlan(BaseModel):
    id: int
    plan_id: str
    actividad_id: Optional[int]
    nombre_custom: Optional[str]
    duracion_horas: float
    costo_base: int
    costo_final: int

    class Config:
        from_attributes = True

class TransporteEnPlan(BaseModel):
    id: int
    plan_id: str
    transporte_id: Optional[int]
    tipo_custom: Optional[str]
    origen_custom: Optional[str]
    destino_custom: Optional[str]
    tiempo_estimado_horas: float
    costo_base: float
    costo_final: float

    class Config:
        from_attributes = True

class PlanDetalleResponse(BaseModel):
    lugares: List[LugarEnPlan]
    hospedaje: List[HospedajeEnPlan]
    actividades: List[ActividadEnPlan]
    transporte: List[TransporteEnPlan]

    class Config:
        from_attributes = True
