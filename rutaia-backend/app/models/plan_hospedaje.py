# app/models/plan_hospedaje.py

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

class PlanHospedaje(Base):
    __tablename__ = "plan_hospedaje"

    id               = Column(Integer, primary_key=True, index=True)
    plan_id          = Column(String, ForeignKey("user_plans.id"),   nullable=False)
    # FK opcional al maestro
    hospedaje_id     = Column(Integer, ForeignKey("hospedajes.id"), nullable=True)
    # Campos custom para alojamientos fuera de catálogo
    nombre_custom    = Column(String, nullable=True)
    direccion_custom = Column(String, nullable=True)
    # Fechas para calcular noches
    fecha_check_in   = Column(Date, nullable=False)
    fecha_check_out  = Column(Date, nullable=False)
    noches           = Column(Integer, nullable=False)
    # Snapshot del precio y cálculos
    precio_base      = Column(Integer, nullable=False, default=0)  # precio_noche al reservar
    costo_calculado  = Column(Integer, nullable=False, default=0)  # precio_base * noches
    costo_final      = Column(Integer, nullable=False, default=0)  # igual a calculado o override
    # Relaciones
    hospedaje        = relationship("Hospedaje", back_populates="plan_hospedajes")
    plan             = relationship("UserPlan",  back_populates="hospedajes")