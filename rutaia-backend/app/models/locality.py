# app/models/locality.py
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Enum
from app.models.database import Base

LOCALITY_TYPES = ('city', 'town', 'village', 'hamlet', 'port', 'sector', 'destination')

class Locality(Base):
    """
    Official territorial anchor for the system.
    Represents populated centers or base destinations.
    """
    __tablename__ = "localities"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(100), nullable=False)
    slug        = Column(String(100), unique=True, nullable=False)
    type        = Column(Enum(*LOCALITY_TYPES, name='locality_type'), nullable=False)
    region      = Column(String(100), default="Aysén")
    comuna      = Column(String(100), nullable=True)
    lat         = Column(Float, nullable=False)
    lng         = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    is_active   = Column(Boolean, default=True, nullable=False)
    
    # Traceability
    legacy_city_id = Column(Integer, nullable=True)
    legacy_item_id = Column(Integer, nullable=True)
