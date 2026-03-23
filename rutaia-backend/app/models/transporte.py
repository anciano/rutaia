# app/models/transporte.py

from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from app.models.database import Base

class Transporte(Base):
    __tablename__ = "transportes"

    id                     = Column(Integer, primary_key=True, index=True)
    tipo                   = Column(String,  nullable=False)   # e.g. "auto", "bus", "taxi", "transfer privado"
    descripcion            = Column(Text,    nullable=True)    # detalles adicionales
    costo_estandar_por_km  = Column(Float,   nullable=True)    # si aplica
    costo_estandar_por_tramo = Column(Float, nullable=True)    # p.ej. tarifa fija
    velocidad_promedio_kmh = Column(Float,   nullable=True)    # para estimar tiempo según distancia
    # Relación inversa
    plan_transportes       = relationship(
        "PlanTransporte",
        back_populates="transporte",
        cascade="all, delete-orphan"
    )
