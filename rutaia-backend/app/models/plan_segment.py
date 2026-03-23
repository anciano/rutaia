# app/models/plan_segment.py

import uuid
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.database import Base

TRANSPORT_MODES = ("car", "walk", "bus", "ferry", "flight", "unknown")
ROUTE_PROVIDERS = ("osrm", "manual", "direct_line")

class PlanSegment(Base):
    """
    Represents a travel leg between two PlanItems in an itinerary.
    Stores real-world routing geometry, distance, and duration.
    """
    __tablename__ = "plan_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    plan_id = Column(String, ForeignKey("user_plans.id", ondelete="CASCADE"), nullable=False)
    day_id  = Column(UUID(as_uuid=True), ForeignKey("plan_days.id", ondelete="CASCADE"), nullable=True)
    
    # Connection between items
    from_item_id = Column(UUID(as_uuid=True), ForeignKey("plan_items.id", ondelete="CASCADE"), nullable=False)
    to_item_id   = Column(UUID(as_uuid=True), ForeignKey("plan_items.id", ondelete="CASCADE"), nullable=False)
    
    # Movement data
    transport_mode = Column(
        Enum(*TRANSPORT_MODES, name="transport_mode_type"), 
        nullable=False, 
        default="car"
    )
    
    distance_km      = Column(Numeric(10, 2), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Geometry and Sourcing
    route_geometry = Column(JSONB, nullable=True) # GeoJSON LineString
    route_provider = Column(
        Enum(*ROUTE_PROVIDERS, name="route_provider_type"), 
        nullable=False, 
        default="osrm"
    )
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    plan      = relationship("UserPlan", back_populates="route_segments")
    day       = relationship("PlanDay", back_populates="day_segments")
    from_item = relationship("PlanItem", foreign_keys=[from_item_id])
    to_item   = relationship("PlanItem", foreign_keys=[to_item_id])
