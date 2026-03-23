# app/models/catalog_event.py

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.models.database import Base

class CatalogEvent(Base):
    """Temporal data for localities or specific catalog items."""
    __tablename__ = "catalog_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # FKs
    locality_id     = Column(Integer, ForeignKey("localities.id"), unique=True, nullable=True)
    catalog_item_id = Column(Integer, ForeignKey("catalog_items.id"), unique=True, nullable=True)
    
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # For recurring events (e.g. every Saturday) - simplified for now
    is_recurring = Column(Boolean, default=False)
    
    # Relationships
    locality = relationship("Locality")
    item     = relationship("CatalogItem", back_populates="event_info")
