# app/models/plan_transporte.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

class PlanTransporte(Base):
    __tablename__ = "plan_transporte"

    id                      = Column(Integer, primary_key=True, index=True)
    plan_id                 = Column(String,  ForeignKey("user_plans.id"), nullable=False)
    # FK opcional al maestro
    transporte_id           = Column(Integer, ForeignKey("transportes.id"), nullable=True)
    # Campos custom para casos ad-hoc
    tipo_custom             = Column(String, nullable=True)
    origen_custom           = Column(String, nullable=True)
    destino_custom          = Column(String, nullable=True)
    # Siempre obligatorios
    tiempo_estimado_horas   = Column(Float, nullable=False)
    # Snapshots y overrides de costo
    costo_base              = Column(Float, nullable=False, default=0.0)  # p.ej. tarifa calculada
    costo_final             = Column(Float, nullable=False, default=0.0)  # override o igual a base
    # Relaciones
    transporte              = relationship("Transporte", back_populates="plan_transportes")
    plan                    = relationship("UserPlan",    back_populates="transportes")