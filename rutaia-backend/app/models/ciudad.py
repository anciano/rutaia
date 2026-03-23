# app/models/ciudad.py
from sqlalchemy import Column, Integer, String, Boolean
from app.models.database import Base

class Ciudad(Base):
    __tablename__ = "ciudades"

    id     = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    region = Column(String, nullable=True)
    pais   = Column(String, nullable=False, default="Chile")
    activa = Column(Boolean, default=True)