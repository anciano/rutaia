from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.models.database import Base
import uuid

class Preferencia(Base):
    __tablename__ = "preferencias"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre      = Column(String, unique=True, nullable=False)
    descripcion = Column(String)
    activa      = Column(Boolean, default=True)