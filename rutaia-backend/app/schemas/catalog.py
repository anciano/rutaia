# app/schemas/catalog.py
"""Pydantic schemas for the unified catalog (Stage 9)."""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class _Base(BaseModel):
    class Config:
        from_attributes = True


# ───────────── Categories ─────────────

class CategoryCreate(_Base):
    name: str = Field(..., max_length=120)
    slug: str = Field(..., max_length=120)
    parent_id: int | None = None
    root_block: str | None = None
    icon: str | None = None
    sort_order: int = 0
    is_active: bool = True

class CategoryUpdate(_Base):
    name: str | None = None
    slug: str | None = None
    parent_id: int | None = None
    root_block: str | None = None
    icon: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None

class CategoryRead(_Base):
    id: int
    name: str
    slug: str
    parent_id: int | None = None
    root_block: str | None = None
    icon: str | None = None
    sort_order: int
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    children: List["CategoryRead"] = []


# ───────────── Localities (Stage 12) ─────────────

class LocalityBase(_Base):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    type: str = Field(..., pattern="^(city|town|village|hamlet|port|sector|destination)$")
    region: str = "Aysén"
    comuna: str | None = None
    lat: float
    lng: float
    description: str | None = None
    is_active: bool = True

class LocalityCreate(LocalityBase):
    legacy_city_id: int | None = None
    legacy_item_id: int | None = None

class LocalityUpdate(_Base):
    name: str | None = None
    slug: str | None = None
    type: str | None = None
    region: str | None = None
    comuna: str | None = None
    lat: float | None = None
    lng: float | None = None
    description: str | None = None
    is_active: bool | None = None

class LocalityRead(LocalityBase):
    id: int
    legacy_city_id: int | None = None
    legacy_item_id: int | None = None


# ───────────── Transport Segments ─────────────

class TransportSegmentBase(_Base):
    origin_id: int | None = None
    destination_id: int | None = None
    origin_locality_id: int | None = None
    destination_locality_id: int | None = None
    price_clp: int | None = None
    duration_minutes: int | None = None
    frequency: str | None = None
    schedule: dict | None = None
    observations: str | None = None

class TransportSegmentCreate(TransportSegmentBase):
    pass

class TransportSegmentRead(TransportSegmentBase):
    origin_name: str | None = None
    destination_name: str | None = None
    origin_locality_name: str | None = None
    destination_locality_name: str | None = None

# ───────────── Catalog Items ─────────────

class CatalogItemCreate(_Base):
    item_type: str = Field(..., pattern="^(place|activity|route|transport|lodging|event)$")
    name: str = Field(..., max_length=200)
    description: str | None = None
    category_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    locality_id: int | None = None
    estimated_duration_minutes: int | None = None
    approx_cost_clp: int | None = None
    is_active: bool = True
    extra: dict | None = None
    
    # Optional: Allow creating segments along with the transport item
    segments: List[TransportSegmentCreate] = []
    
    # Optional: Allow creating event info along with the event item
    event_info: Optional["CatalogEventCreate"] = None

class CatalogItemUpdate(_Base):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    lat: float | None = None
    lng: float | None = None
    locality_id: int | None = None
    estimated_duration_minutes: int | None = None
    approx_cost_clp: int | None = None
    is_active: bool | None = None
    extra: dict | None = None
    segments: List[TransportSegmentCreate] | None = None
    event_info: Optional["CatalogEventUpdate"] = None

class CatalogItemRead(_Base):
    id: int
    item_type: str
    name: str
    description: str | None = None
    category_id: int | None = None
    category_name: str | None = None
    lat: float | None = None
    lng: float | None = None
    locality_id: int | None = None
    locality_name: str | None = None
    estimated_duration_minutes: int | None = None
    approx_cost_clp: int | None = None
    is_active: bool
    extra: dict | None = None
    segments: List[TransportSegmentRead] = []
    event_info: Optional["CatalogEventRead"] = None


# ───────────── Item Links ─────────────

class ItemLinkCreate(_Base):
    parent_item_id: int
    child_item_id: int
    relation_type: str = Field(..., pattern="^(contains|near|requires)$")
    sort_order: int = 0

class ItemLinkRead(_Base):
    id: UUID
    parent_item_id: int
    child_item_id: int
    relation_type: str
    sort_order: int


# ───────────── Destination Profile (Contexto Territorial) ─────────────

class DestinationProfileBase(_Base):
    description_cultural: str | None = None
    local_rules: list | None = None
    emergency_contacts: dict | None = None

class DestinationProfileCreate(DestinationProfileBase):
    pass

class DestinationProfileUpdate(DestinationProfileBase):
    pass

class DestinationProfileRead(DestinationProfileBase):
    id: int
    locality_id: int | None = None
    catalog_item_id: int | None = None

# ───────────── Events ─────────────

class CatalogEventBase(_Base):
    start_date: Optional[datetime] = None # ISO Format
    end_date: Optional[datetime] = None
    is_recurring: bool = False

class CatalogEventCreate(CatalogEventBase):
    pass

class CatalogEventUpdate(CatalogEventBase):
    pass

class CatalogEventRead(CatalogEventBase):
    id: int
    locality_id: int | None = None
    catalog_item_id: int | None = None
