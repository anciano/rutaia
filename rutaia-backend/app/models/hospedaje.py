# app/models/hospedaje.py

from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.database import Base

class Hospedaje(Base):
    __tablename__ = "hospedajes"

    id           = Column(Integer, primary_key=True, index=True)
    nombre       = Column(String, nullable=False)
    ubicacion    = Column(String, nullable=True)       # dirección o descripción breve
    precio_noche = Column(Integer, nullable=True)      # valor aproximado por noche
    rating       = Column(Float,   nullable=True)
    descripcion  = Column(Text,    nullable=True)
    fotos_url    = Column(JSONB,   nullable=True)     # lista de URLs
    # Relación inversa para poder navegar desde PlanHospedaje
    plan_hospedajes = relationship(
        "PlanHospedaje",
        back_populates="hospedaje",
        cascade="all, delete-orphan"
    )