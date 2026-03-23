# app/models/actividad.py

from sqlalchemy import Column, Integer, String, Float, Text, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.database import Base

class Actividad(Base):
    __tablename__ = "actividades"

    id                      = Column(Integer, primary_key=True, index=True)
    ciudad_id               = Column(String,  ForeignKey("ciudades.id"), nullable=True)
    nombre                  = Column(String, nullable=False)
    descripcion             = Column(Text, nullable=True)
    duracion_estimada_horas   = Column(Float, nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True) # Stage 4
    nivel_intensidad        = Column(String, nullable=True)   # p.ej. "bajo"|"medio"|"alto"
    costo_aprox             = Column(Integer, nullable=True)  # precio aproximado de la actividad
    latitud                 = Column(Numeric(9,6), nullable=True)
    longitud                = Column(Numeric(9,6), nullable=True)
    fotos_url               = Column(JSONB, nullable=True)    # lista de URLs para fotos
    rating_promedio         = Column(Float, nullable=True)
    # Relación inversa para poder navegar desde PlanActividad
    plan_actividades = relationship(
        "PlanActividad",
        back_populates="actividad",
        cascade="all, delete-orphan"
    )