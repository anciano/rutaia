# app/models/destination_profile.py

from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.database import Base


class DestinationProfile(Base):
    """
    Hyperlocal information for localities or specific catalog items.
    """
    __tablename__ = "destination_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # FKs (at least one should be present)
    locality_id     = Column(Integer, ForeignKey("localities.id", ondelete="CASCADE"), unique=True, nullable=True)
    catalog_item_id = Column(Integer, ForeignKey("catalog_items.id", ondelete="CASCADE"), unique=True, nullable=True)
    
    description_cultural = Column(Text, nullable=True)
    local_rules = Column(JSONB, nullable=True) # e.g. ["Water is drinkable", "Shops close 13-15"]
    emergency_contacts = Column(JSONB, nullable=True) # e.g. {"Posta": "123"}

    # Relationships
    locality = relationship("Locality")
    item     = relationship("CatalogItem", back_populates="destination_profile")
