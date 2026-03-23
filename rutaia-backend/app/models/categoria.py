# app/models/categoria.py
from sqlalchemy import Column, Integer, String
from app.models.database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id     = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)
    icono  = Column(String, nullable=True)   # e.g. "pi-globe", "pi-tree"
