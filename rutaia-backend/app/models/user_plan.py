# app/models/user_plan.py

from sqlalchemy import Column, String, Integer, Date, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.database import Base
import uuid

class UserPlan(Base):
    __tablename__ = "user_plans"

    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id       = Column(String,  ForeignKey("users.id"),    nullable=False)
    origen_id     = Column(Integer, ForeignKey("ciudades.id"), nullable=False)  # Stage 8: Integer FK
    participantes = Column(JSONB, nullable=False)
    preferencias  = Column(JSONB, nullable=False)
    dias          = Column(Integer, nullable=False)
    presupuesto   = Column(Integer, nullable=False)
    fecha_inicio  = Column(Date,    nullable=False)
    fecha_fin     = Column(Date,    nullable=False)
    transport_mode = Column(String,  nullable=True) # auto_propio, arrendar_auto, transporte_publico, movilidad_local
    estado        = Column(String,  default="activo")
    
    budget_clp    = Column(Numeric(12, 0), nullable=True)
    total_days    = Column(Integer, nullable=True)

    # Legacy Relationships
    lugares       = relationship("PlanLugar", back_populates="plan", cascade="all, delete-orphan")
    hospedajes    = relationship("PlanHospedaje", back_populates="plan", cascade="all, delete-orphan")
    actividades   = relationship("PlanActividad", back_populates="plan", cascade="all, delete-orphan")
    transportes   = relationship("PlanTransporte", back_populates="plan", cascade="all, delete-orphan")

    # Tracking de generación (Stage 4)
    generated_at       = Column(DateTime, nullable=True)
    generation_version = Column(Integer,  nullable=True, default=1)

    # NUEVAS Relaciones del Refactor (Stage 3)
    days = relationship("PlanDay", back_populates="plan", cascade="all, delete-orphan", order_by="asc(plan_days.c.number)")
    place_items = relationship("PlaceItem", back_populates="plan", cascade="all, delete-orphan")
    activity_items = relationship("ActivityItem", back_populates="plan", cascade="all, delete-orphan")
    transport_segments = relationship("TransportSegment", back_populates="plan", cascade="all, delete-orphan")
    lodging_items = relationship("LodgingItem", back_populates="plan", cascade="all, delete-orphan")
    logs = relationship("TravelLog", back_populates="plan", cascade="all, delete-orphan")
    route_segments = relationship("PlanSegment", back_populates="plan", cascade="all, delete-orphan")
    all_items = relationship("PlanItem", back_populates="plan", cascade="all, delete-orphan")