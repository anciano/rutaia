# app/models/plan_lugares.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.models.database import Base

class PlanLugar(Base):
    __tablename__ = "plan_lugares"

    id              = Column(Integer, primary_key=True, index=True)
    plan_id         = Column(String, ForeignKey("user_plans.id"), nullable=False)
    lugar_id        = Column(Integer, ForeignKey("lugares.id"), nullable=True)
    # NUEVO ► día relativo (1 … n)
    day             = Column(Integer, nullable=False, default=1)
    nombre_custom    = Column(String,  nullable=True)
    ubicacion_custom = Column(String,  nullable=True)
    horario_entrada  = Column(DateTime, nullable=False)
    duracion_horas   = Column(Float,    nullable=False)
    precio_base      = Column(Integer, nullable=False, default=0)
    costo_final      = Column(Integer, nullable=False, default=0)
    lugar = relationship("Lugar",    back_populates="plan_lugares")
    plan  = relationship("UserPlan", back_populates="lugares")
