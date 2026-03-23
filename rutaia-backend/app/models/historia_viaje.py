from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .database import Base
from datetime import datetime

class HistoriaViaje(Base):
    __tablename__ = "historia_viaje"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String, ForeignKey("user_plans.id"))
    categoria = Column(String)
    accion = Column(String)
    elemento_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)