from pydantic import BaseModel, field_validator
from datetime import date
from typing import List, Optional

class Participante(BaseModel):
    edad: int
    discapacidad: bool = False
    tipo_discapacidad: Optional[str] = None   # “motora”, “visual”, …

    @field_validator("tipo_discapacidad")
    def tipo_if_discapacidad(cls, v, info):
        if info.data.get("discapacidad") and not v:
            raise ValueError("Debe indicar tipo de discapacidad")
        return v

class PlanInput(BaseModel):
    user_id: str
    origen_id: int  # Stage 8: Integer ID
    dias: int
    presupuesto: int
    participantes: List[Participante]
    preferencias: List[str]
    fecha_inicio: date
    fecha_fin: date
    transport_mode: Optional[str] = None

class PlanOutput(BaseModel):
    id: str
    origen_id: Optional[int] = None
    origen: Optional[str] = None        # nombre de la ciudad
    participantes: List[Participante]
    preferencias: List[str]             # UUIDs de preferencias
    dias: int
    presupuesto: int
    fecha_inicio: date
    fecha_fin: date
    transport_mode: Optional[str] = None
    estado: str

    class Config:
        from_attributes = True