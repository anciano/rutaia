# app/models/plan_actividades.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

class PlanActividad(Base):
    __tablename__ = "plan_actividades"

    id               = Column(Integer, primary_key=True, index=True)
    plan_id          = Column(String,  ForeignKey("user_plans.id"), nullable=False)
    actividad_id     = Column(Integer, ForeignKey("actividades.id"), nullable=True)
    # Custom
    nombre_custom    = Column(String, nullable=True)
    # Siempre obligatorio
    duracion_horas   = Column(Float, nullable=False)
    # Snapshots y overrides
    costo_base       = Column(Integer, nullable=False, default=0)
    costo_final      = Column(Integer, nullable=False, default=0)
    # Relaciones ORM (opcionales)
    actividad        = relationship("Actividad", back_populates="plan_actividades")
    plan             = relationship("UserPlan",    back_populates="actividades")