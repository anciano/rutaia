# app/schemas/plan_detail.py

import datetime as dt
from uuid import UUID
from pydantic import BaseModel, Field, conint
from typing import List, Optional

class _BaseConfig(BaseModel):
    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2

# -------- PlaceItem --------
class PlaceItemCreate(_BaseConfig):
    name: str = Field(..., max_length=120)
    place_id: UUID | None = None
    day: conint(ge=1) | None = None
    cost_clp: int | None = None
    start_time: dt.time | None = None
    end_time: dt.time | None = None

class PlaceItemRead(PlaceItemCreate):
    id: UUID

class PlaceItemUpdate(PlaceItemCreate):
    pass

# -------- ActivityItem --------
class ActivityItemCreate(_BaseConfig):
    description: str = Field(..., max_length=160)
    # Changed regex to pattern for Pydantic v2
    level: str = Field("media", pattern="^(baja|media|alta)$")
    day: conint(ge=1) | None = None
    cost_clp: int | None = None
    start_time: dt.time | None = None
    end_time: dt.time | None = None

class ActivityItemRead(ActivityItemCreate):
    id: UUID

class ActivityItemUpdate(ActivityItemCreate):
    pass

# -------- TransportSegment --------
class TransportSegmentCreate(_BaseConfig):
    origin_name: str = Field(..., max_length=120)
    destination_name: str = Field(..., max_length=120)
    mode: str = Field(..., pattern="^(auto|bus|avion|barco)$")
    distance_km: float | None = None
    duration_minutes: int | None = None
    cost_clp: int | None = None

class TransportSegmentRead(TransportSegmentCreate):
    id: UUID

class TransportSegmentUpdate(TransportSegmentCreate):
    pass

# -------- LodgingItem --------
class LodgingItemCreate(_BaseConfig):
    name: str = Field(..., max_length=120)
    check_in: dt.date
    check_out: dt.date
    cost_clp: int | None = None

class LodgingItemRead(LodgingItemCreate):
    id: UUID

class LodgingItemUpdate(LodgingItemCreate):
    pass

# -------- TravelLog --------
class TravelLogRead(_BaseConfig):
    id: UUID
    item_type: str
    item_id: UUID
    action: str
    timestamp: dt.datetime

# -------- UserPlan patch --------
class PlanPatch(_BaseConfig):
    budget_clp: int | None = None
    total_days: conint(gt=0) | None = None

# -------- Stage 8b: Unified Item Schemas --------

class PlanItemUnifiedCreate(_BaseConfig): # Changed from BaseModel to _BaseConfig
    # plan_id is now required to know which trip it belongs to, even without a day
    plan_id: str
    # day_id is now optional. NULL = Wishlist
    day_id: Optional[UUID] = None
    item_type: str = Field(..., pattern="^(place|activity|lodging)$")
    place_id: int | None = None # Kept original field
    activity_id: int | None = None
    lodging_id: int | None = None
    transport_id: int | None = None
    catalog_item_id: Optional[int] = None # Changed type and default
    sort_order: int = 0
    start_time: dt.time | None = None
    end_time: dt.time | None = None
    cost_clp: int = 0
    metadata_json: dict | None = None

class PlanItemUnifiedUpdate(_BaseConfig):
    day_id: Optional[UUID] = None
    sort_order: int | None = None
    start_time: dt.time | None = None
    end_time: dt.time | None = None
    cost_clp: int | None = None
    metadata_json: dict | None = None

# -------- PlanSegment (Routing) --------
class PlanSegmentRead(_BaseConfig):
    id: UUID
    from_item_id: UUID
    to_item_id: UUID
    transport_mode: str
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    route_geometry: Optional[dict] = None
    route_provider: str

class PlanSegmentUpdate(_BaseConfig):
    transport_mode: Optional[str] = None

class PlanItemV3Read(_BaseConfig):
    id: UUID
    day_id: Optional[UUID] = None
    item_type: str
    place_id: int | None = None
    activity_id: int | None = None
    lodging_id: int | None = None
    transport_id: int | None = None
    catalog_item_id: int | None = None
    sort_order: int
    start_time: dt.time | None = None
    end_time: dt.time | None = None
    cost_clp: int
    metadata_json: dict | None = None

class PlanDayRead(_BaseConfig):
    id: UUID
    plan_id: str
    number: int
    date: dt.date | None = None
    notes: str | None = None
    items: List[PlanItemV3Read] = []
    day_segments: List[PlanSegmentRead] = []
    lodging_suggestion: dict | None = None

class UserPlanResponseV2(BaseModel):
    id: str
    user_id: str
    origen_id: int
    participantes: List[dict]
    preferencias: List[str]
    dias: int
    presupuesto: int
    fecha_inicio: dt.date
    fecha_fin: dt.date
    transport_mode: Optional[str] = None
    budget_clp: Optional[float] = None
    total_days: Optional[int] = None
    
    # Nested structure
    days: List[PlanDayRead] = []
    
    # All segments for whole plan view
    route_segments: List[PlanSegmentRead] = []
    
    # Flat list of all items (includes Wishlist items with day_id=None)
    all_items: List[PlanItemV3Read] = []
    
    class Config:
        from_attributes = True
