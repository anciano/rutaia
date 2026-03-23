# app/models/catalog_item.py

import uuid
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    ForeignKey, Numeric, Index, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.database import Base


ITEM_TYPES = ("place", "activity", "route", "transport", "lodging", "event")


class CatalogItem(Base):
    """Unified catalog item — replaces lugares, actividades, transportes, hospedajes.

    All tourism resources live in this single table.
    The `item_type` column distinguishes the kind of resource.
    Flexible metadata is stored in `extra` (JSONB).
    """
    __tablename__ = "catalog_items"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    item_type   = Column(
        SAEnum(*ITEM_TYPES, name="catalog_item_type", create_constraint=True),
        nullable=False,
    )
    name        = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Category FK
    category_id = Column(Integer, ForeignKey("catalog_categories.id"), nullable=True)

    # Geolocation (mandatory when applicable — enforced at app level)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    # Operational fields
    estimated_duration_minutes = Column(Integer, nullable=True)         # duration in minutes
    approx_cost_clp            = Column(Numeric(12, 0), nullable=True)  # approx cost in CLP
    is_active                  = Column(Boolean, default=True, nullable=False)

    # Flexible metadata (horarios, acceso, tags, recomendaciones, etc.)
    extra = Column(JSONB, nullable=True)

    # Regional Context
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=True)

    # Relationships
    category      = relationship("CatalogCategory", back_populates="items")
    locality      = relationship("Locality") # Backrefs can be added to Locality if needed
    parent_links  = relationship("ItemLink", foreign_keys="ItemLink.child_item_id",  back_populates="child",  cascade="all, delete-orphan")
    child_links   = relationship("ItemLink", foreign_keys="ItemLink.parent_item_id", back_populates="parent", cascade="all, delete-orphan")
    
    # New: Structured segments for transport items
    segments      = relationship("CatalogTransportSegment", foreign_keys="CatalogTransportSegment.transport_id", back_populates="transport", cascade="all, delete-orphan")

    # Módulo V2: Destination Profile (Hyperlocal info for towns/cities)
    destination_profile = relationship("DestinationProfile", back_populates="item", uselist=False, cascade="all, delete-orphan")

    # Módulo V3: Local Agenda (Event info)
    event_info = relationship("CatalogEvent", back_populates="item", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_catalog_item_type", "item_type"),
        Index("idx_catalog_item_category", "category_id"),
        Index("idx_catalog_item_active", "is_active"),
    )
