# app/models/catalog_transport_segment.py

import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.database import Base

class CatalogTransportSegment(Base):
    """Represents a specific segment or leg of a transportation service.
    
    Example: 
        Transport 'Bus Regional' has segment 'Coyhaique -> Puyuhuapi'
    """
    __tablename__ = "catalog_transport_segments"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transport_id    = Column(Integer, ForeignKey("catalog_items.id", ondelete="CASCADE"), nullable=False)
    
    # Origins and destinations can be catalog items or localities
    origin_id       = Column(Integer, ForeignKey("catalog_items.id", ondelete="SET NULL"), nullable=True)
    destination_id  = Column(Integer, ForeignKey("catalog_items.id", ondelete="SET NULL"), nullable=True)
    
    origin_locality_id = Column(Integer, ForeignKey("localities.id", ondelete="SET NULL"), nullable=True)
    destination_locality_id = Column(Integer, ForeignKey("localities.id", ondelete="SET NULL"), nullable=True)
    
    price_clp        = Column(Numeric(12, 0), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    frequency        = Column(String(200), nullable=True)  # e.g., "Daily at 08:00", "Mon-Wed-Fri"
    schedule         = Column(JSONB, nullable=True) # {weekday: [], saturday: [], sunday_holiday: []}
    observations     = Column(String(500), nullable=True)

    # Relationships
    transport   = relationship("CatalogItem", foreign_keys=[transport_id], back_populates="segments")
    
    origin      = relationship("CatalogItem", foreign_keys=[origin_id])
    destination = relationship("CatalogItem", foreign_keys=[destination_id])
    
    origin_locality      = relationship("Locality", foreign_keys=[origin_locality_id])
    destination_locality = relationship("Locality", foreign_keys=[destination_locality_id])

    def __repr__(self):
        return f"<TransportSegment {self.id} (Transport: {self.transport_id})>"
