# app/models/user.py

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.models.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id             = Column(String, primary_key=True, index=True)
    nombre         = Column(String, nullable=False)
    correo         = Column(String, unique=True, nullable=False)
    password_hash  = Column(String, nullable=True)    # para auth local
    role           = Column(String, default="user")   # "user" o "admin"
    provider       = Column(String, nullable=True)    # "local", "google", "facebook", etc.
    provider_id    = Column(String, nullable=True)    # id que retorna el proveedor OAuth
    creado_en      = Column(DateTime, default=datetime.utcnow)
    extra          = Column(JSONB, nullable=True)     # para datos extra del perfil