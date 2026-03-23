# app/routes/admin.py
"""Admin API for managing the unified catalog (Stage 9)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, cast, Float, Numeric
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db
from app.models.catalog_category import CatalogCategory
from app.models.catalog_item import CatalogItem
from app.models.item_link import ItemLink
from app.models.locality import Locality
from app.schemas.catalog import (
    CategoryCreate, CategoryUpdate, CategoryRead,
    CatalogItemCreate, CatalogItemUpdate, CatalogItemRead,
    ItemLinkCreate, ItemLinkRead,
    TransportSegmentRead,
    DestinationProfileRead, DestinationProfileUpdate,
    CatalogEventRead, CatalogEventUpdate,
    LocalityRead, LocalityCreate, LocalityUpdate
)
from app.models.catalog_transport_segment import CatalogTransportSegment
from app.models.destination_profile import DestinationProfile
from app.models.catalog_event import CatalogEvent

router = APIRouter(prefix="/admin", tags=["admin"])

# ═══════════════ Categories ═══════════════

@router.get("/categories", response_model=List[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    """List all categories (flat list, frontend can build tree from parent_id)."""
    return db.query(CatalogCategory).order_by(CatalogCategory.name).all()

@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    cat = CatalogCategory(**payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

# ───────────── Localities (Stage 12) ─────────────

@router.get("/localities", response_model=List[LocalityRead])
def list_localities(db: Session = Depends(get_db)):
    return db.query(Locality).all()

@router.post("/localities", response_model=LocalityRead)
def create_locality(obj_in: LocalityCreate, db: Session = Depends(get_db)):
    db_obj = Locality(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/localities/{id}", response_model=LocalityRead)
def get_locality(id: int, db: Session = Depends(get_db)):
    obj = db.query(Locality).get(id)
    if not obj:
        raise HTTPException(404, "Locality not found")
    return obj

@router.put("/localities/{id}", response_model=LocalityRead)
def update_locality(id: int, obj_in: LocalityUpdate, db: Session = Depends(get_db)):
    db_obj = db.query(Locality).get(id)
    if not db_obj:
        raise HTTPException(404, "Locality not found")
    
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/localities/{id}")
def delete_locality(id: int, db: Session = Depends(get_db)):
    db_obj = db.query(Locality).get(id)
    if not db_obj:
        raise HTTPException(404, "Locality not found")
    db.delete(db_obj)
    db.commit()
    return {"message": "Locality deleted"}

@router.put("/categories/{cat_id}", response_model=CategoryRead)
def update_category(cat_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.get(CatalogCategory, cat_id)
    if not cat:
        raise HTTPException(404, "Category not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return cat

@router.get("/categories/tree", response_model=List[CategoryRead])
def get_categories_tree(db: Session = Depends(get_db)):
    """Return a hierarchical tree of all active categories."""
    roots = db.query(CatalogCategory).filter(
        CatalogCategory.parent_id == None,
        CatalogCategory.is_active == True
    ).order_by(CatalogCategory.sort_order, CatalogCategory.name).all()
    return roots

@router.get("/categories/stats")
def get_categories_stats(db: Session = Depends(get_db)):
    """Get count of items for each category."""
    counts = db.query(
        CatalogItem.category_id, 
        func.count(CatalogItem.id).label("count")
    ).group_by(CatalogItem.category_id).all()
    return {c.category_id: c.count for c in counts if c.category_id}

@router.put("/categories/{cat_id}/move", response_model=CategoryRead)
def move_category(cat_id: int, parent_id: Optional[int], sort_order: int = 0, db: Session = Depends(get_db)):
    cat = db.get(CatalogCategory, cat_id)
    if not cat:
        raise HTTPException(404, "Category not found")
    
    # Check for circular dependency if changing parent
    if parent_id:
        if parent_id == cat_id:
            raise HTTPException(400, "Cannot move a category to itself")
        # Simple depth-limited check (could be more robust)
        p = db.get(CatalogCategory, parent_id)
        while p and p.parent_id:
            if p.parent_id == cat_id:
                raise HTTPException(400, "Circular dependency detected")
            p = p.parent
            
    cat.parent_id = parent_id
    cat.sort_order = sort_order
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/categories/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.get(CatalogCategory, cat_id)
    if not cat:
        raise HTTPException(404, "Category not found")
    
    # Check if has children
    if db.query(CatalogCategory).filter_by(parent_id=cat_id).first():
        raise HTTPException(400, "Category has children and cannot be deleted")
        
    db.delete(cat)
    db.commit()
    return None


# ═══════════════ Catalog Items ═══════════════

@router.get("/items", response_model=List[CatalogItemRead])
def list_items(
    item_type: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """List catalog items with optional filters."""
    query = db.query(CatalogItem).outerjoin(CatalogCategory, CatalogItem.category_id == CatalogCategory.id).outerjoin(Locality, CatalogItem.locality_id == Locality.id)
    if active_only:
        query = query.filter(CatalogItem.is_active == True)
    if item_type:
        query = query.filter(CatalogItem.item_type == item_type)
    if category_id:
        # Get all subcategory IDs recursively
        all_cat_ids = [category_id]
        def get_subs(pid):
            subs = db.query(CatalogCategory.id).filter(CatalogCategory.parent_id == pid).all()
            for s in subs:
                all_cat_ids.append(s[0])
                get_subs(s[0])
        get_subs(category_id)
        query = query.filter(CatalogItem.category_id.in_(all_cat_ids))
    
    if search:
        query = query.filter(CatalogItem.name.ilike(f"%{search}%"))
    
    items = query.order_by(CatalogItem.name).all()
    
    # Enrich and validate
    result = []
    for it in items:
        # Pre-resolve name to avoid multiple queries
        cat_name = it.category.name if it.category else None
        loc_name = it.locality.name if it.locality else None
        
        # Read the item data (Pydantic will handle the rest)
        read_obj = CatalogItemRead.model_validate(it)
        read_obj.category_name = cat_name
        read_obj.locality_name = loc_name
        
        # Resolve names for segments if any
        if it.item_type == "transport":
            enriched_segments = []
            for seg in it.segments:
                s_read = TransportSegmentRead.model_validate(seg)
                if seg.origin:
                    s_read.origin_name = seg.origin.name
                if seg.destination:
                    s_read.destination_name = seg.destination.name
                enriched_segments.append(s_read)
            read_obj.segments = enriched_segments
        
        # Resolve event info if any
        if it.item_type == "event" and it.event_info:
            read_obj.event_info = CatalogEventRead.model_validate(it.event_info)

        result.append(read_obj)
        
    return result

def _enrich_item_read(item: CatalogItem, db: Session) -> CatalogItemRead:
    read = CatalogItemRead.model_validate(item)
    if item.category:
        read.category_name = item.category.name
    
    # Resolve names for segments if any
    if item.item_type == "transport":
        enriched_segments = []
        for seg in item.segments:
            s_read = TransportSegmentRead.model_validate(seg)
            if seg.origin:
                s_read.origin_name = seg.origin.name
            if seg.destination:
                s_read.destination_name = seg.destination.name
            enriched_segments.append(s_read)
        read.segments = enriched_segments
    
    # Resolve event info if any
    if item.item_type == "event" and item.event_info:
        read.event_info = CatalogEventRead.model_validate(item.event_info)
    
    return read


@router.get("/items/{item_id}", response_model=CatalogItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(CatalogItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return _enrich_item_read(item, db)


@router.post("/items", response_model=CatalogItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: CatalogItemCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"segments", "event_info"})
    item = CatalogItem(**data)
    db.add(item)
    db.flush() # Get ID
    
    # Handle segments
    if payload.item_type == "transport" and payload.segments:
        for seg_data in payload.segments:
            seg = CatalogTransportSegment(**seg_data.model_dump(), transport_id=item.id)
            db.add(seg)
    
    # Handle event info
    if payload.item_type == "event" and payload.event_info:
        from datetime import datetime
        evt_data = payload.event_info.model_dump()
        for field in ["start_date", "end_date"]:
            val = evt_data.get(field)
            if val and isinstance(val, str):
                try:
                    iso_str = val.replace('Z', '+00:00')
                    evt_data[field] = datetime.fromisoformat(iso_str)
                except (ValueError, TypeError):
                    # Fallback or silent skip
                    pass
        
        event = CatalogEvent(**evt_data, catalog_item_id=item.id)
        db.add(event)
    
    db.commit()
    db.refresh(item)
    return _enrich_item_read(item, db)


@router.put("/items/{item_id}", response_model=CatalogItemRead)
def update_item(item_id: int, payload: CatalogItemUpdate, db: Session = Depends(get_db)):
    item = db.get(CatalogItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    
    data = payload.model_dump(exclude={"segments", "event_info"}, exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)
    
    # Handle segments if provided (full replacement for simplicity in admin)
    if payload.segments is not None and item.item_type == "transport":
        # Clear existing
        db.query(CatalogTransportSegment).filter_by(transport_id=item.id).delete()
        for seg_data in payload.segments:
            seg = CatalogTransportSegment(**seg_data.model_dump(), transport_id=item.id)
            db.add(seg)
            
    # Handle event info if provided
    if payload.event_info is not None and item.item_type == "event":
        from datetime import datetime
        evt_data = payload.event_info.model_dump()
        for field in ["start_date", "end_date"]:
            val = evt_data.get(field)
            if val and isinstance(val, str):
                try:
                    iso_str = val.replace('Z', '+00:00')
                    evt_data[field] = datetime.fromisoformat(iso_str)
                except (ValueError, TypeError):
                    pass

        if not item.event_info:
            event = CatalogEvent(**evt_data, catalog_item_id=item.id)
            db.add(event)
        else:
            for k, v in evt_data.items():
                setattr(item.event_info, k, v)

    db.commit()
    db.refresh(item)
    return _enrich_item_read(item, db)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(CatalogItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    db.delete(item)
    db.commit()
    return None


# ═══════════════ Item Links ═══════════════

@router.get("/items/{item_id}/links", response_model=List[ItemLinkRead])
def list_item_links(item_id: int, db: Session = Depends(get_db)):
    """List all links where this item is either parent or child."""
    links = db.query(ItemLink).filter(
        (ItemLink.parent_item_id == item_id) | (ItemLink.child_item_id == item_id)
    ).order_by(ItemLink.sort_order).all()
    return [ItemLinkRead.model_validate(l) for l in links]


@router.post("/links", response_model=ItemLinkRead, status_code=status.HTTP_201_CREATED)
def create_link(payload: ItemLinkCreate, db: Session = Depends(get_db)):
    # Validate both items exist
    if not db.get(CatalogItem, payload.parent_item_id):
        raise HTTPException(404, "Parent item not found")
    if not db.get(CatalogItem, payload.child_item_id):
        raise HTTPException(404, "Child item not found")
    link = ItemLink(**payload.model_dump())
    db.add(link)
    db.commit()
    db.refresh(link)
    return ItemLinkRead.model_validate(link)


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(link_id: str, db: Session = Depends(get_db)):
    from uuid import UUID
    link = db.get(ItemLink, UUID(link_id))
    if not link:
        raise HTTPException(404, "Link not found")
    db.delete(link)
    db.commit()
    return None

# ═══════════════ Destination Profile (Info Hiperlocal) ═══════════════

@router.get("/items/{item_id}/destination-profile", response_model=DestinationProfileRead)
def get_destination_profile(item_id: int, db: Session = Depends(get_db)):
    item = db.get(CatalogItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    if not item.destination_profile:
        raise HTTPException(404, "Destination profile not found for this item")
    return item.destination_profile

@router.put("/items/{item_id}/destination-profile", response_model=DestinationProfileRead)
def update_destination_profile(item_id: int, payload: DestinationProfileUpdate, db: Session = Depends(get_db)):
    item = db.get(CatalogItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    
    profile = item.destination_profile
    if not profile:
        profile = DestinationProfile(catalog_item_id=item_id, **payload.model_dump())
        db.add(profile)
    else:
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(profile, k, v)
    
    db.commit()
    db.refresh(profile)
    return profile


# ═══════════════ Dynamic Explorer (Radar) ═══════════════

@router.get("/explorer/nearby", response_model=List[dict])
def get_nearby_items(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(10.0),
    item_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Find items nearby using Haversine formula.
    Returns items with an extra field 'distance_km'.
    """
    # Formula Haversine: d = 2 * r * asin(sqrt(sin^2((lat2-lat1)/2) + cos(lat1)*cos(lat2)*sin^2((lng2-lng1)/2)))
    # For PostgreSQL:
    # 6371 * acos(cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(lng2) - radians(lng1)) + sin(radians(lat1)) * sin(radians(lat2)))
    
    r_lat = func.radians(lat)
    r_lng = func.radians(lng)
    
    # Distance calculation in KM
    distance_expr = (
        6371 * func.acos(
            func.cos(r_lat) * func.cos(func.radians(CatalogItem.lat)) *
            func.cos(func.radians(CatalogItem.lng) - r_lng) +
            func.sin(r_lat) * func.sin(func.radians(CatalogItem.lat))
        )
    ).label("distance_km")

    q = db.query(CatalogItem, distance_expr).filter(CatalogItem.is_active == True)
    
    if item_type:
        q = q.filter(CatalogItem.item_type == item_type)
    
    # Filter by radius and order by distance
    items_with_dist = q.filter(distance_expr <= radius_km).order_by(distance_expr).all()
    
    result = []
    for item, dist in items_with_dist:
        # We enrich the item read-model with the distance
        read = _enrich_item_read(item, db)
        item_dict = read.model_dump()
        item_dict["distance_km"] = float(dist)
        result.append(item_dict)
        
    return result
