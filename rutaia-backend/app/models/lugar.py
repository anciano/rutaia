# app/models/lugar.py

from sqlalchemy import Column, Integer, String, Float, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

class Lugar(Base):
    __tablename__ = "lugares"

    id                         = Column(Integer, primary_key=True, index=True)
    ciudad_id                  = Column(Integer, ForeignKey("ciudades.id"), nullable=True)   # Stage 8: Integer FK
    categoria_id               = Column(Integer, ForeignKey("categorias.id"), nullable=True) # Stage 8: normalized
    categoria                  = Column(String,  nullable=True)   # kept for legacy/fallback
    nombre                     = Column(String,  nullable=False)
    descripcion_breve          = Column(Text,    nullable=True)
    precio_aprox               = Column(Integer, nullable=True)
    latitud                    = Column(Numeric(9,6), nullable=True)
    longitud                   = Column(Numeric(9,6), nullable=True)
    calificacion               = Column(Float,    nullable=True)
    duracion_estimada_horas    = Column(Float,    nullable=True)
    estimated_duration_minutes = Column(Integer,  nullable=True)

    # Stage 7 - Excel Sync Fields
    rango_etario  = Column(String, nullable=True)
    accesibilidad = Column(Text,   nullable=True)
    direccion     = Column(String, nullable=True)

    # Relationships
    ciudad    = relationship("Ciudad")
    categoria_rel = relationship("Categoria")
    plan_lugares  = relationship("PlanLugar", back_populates="lugar", cascade="all, delete-orphan")
