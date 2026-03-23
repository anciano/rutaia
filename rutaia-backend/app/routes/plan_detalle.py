# app/routes/plan_detalle.py

from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from sqlalchemy.orm import Session
import logging
from typing import List, Union
from pydantic import BaseModel
from uuid import UUID
from app.models.database import get_db
from app.models.plan_lugares import PlanLugar
from app.models.plan_hospedaje import PlanHospedaje
from app.models.plan_actividades import PlanActividad
from app.models.plan_transporte import PlanTransporte
from app.models.historia_viaje import HistoriaViaje
from app.models.user_plan import UserPlan
from app.models.plan_detail import (
    ActivityItem,
    LodgingItem,
    PlaceItem,
    TransportSegment,
)
from app.schemas.plan_detalle import (
    PlanDetalleResponse,
    LugarEnPlan, LugarEnPlanCreate,
    HospedajeEnPlan, HospedajeEnPlanCreate,
    ActividadEnPlan, ActividadEnPlanCreate,
    TransporteEnPlan, TransporteEnPlanCreate,
)
from app.schemas.plan_detail import (
    ActivityItemCreate,
    ActivityItemRead,
    ActivityItemUpdate,
    LodgingItemCreate,
    LodgingItemRead,
    LodgingItemUpdate,
    PlaceItemCreate,
    PlaceItemRead,
    PlaceItemUpdate,
    PlanPatch,
    TransportSegmentCreate,
    TransportSegmentRead,
    TransportSegmentUpdate,
)
from app.engine.orchestrator import ItineraryEngine
from app.services.wishlist_service import wishlist_service
from app.models.day import PlanDay
from app.models.plan_item import PlanItem
from app.models.plan_segment import PlanSegment
from app.schemas.plan_detail import PlanSegmentUpdate
from app.services.itinerary_segment_service import ItinerarySegmentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plan", tags=["plan_detalle"])

# helper mapping para evitar repetir código (V2)
item_map = {
    "places": (PlaceItem, PlaceItemCreate, PlaceItemRead, PlaceItemUpdate),
    "activities": (ActivityItem, ActivityItemCreate, ActivityItemRead, ActivityItemUpdate),
    "transport": (TransportSegment, TransportSegmentCreate, TransportSegmentRead, TransportSegmentUpdate),
    "lodging": (LodgingItem, LodgingItemCreate, LodgingItemRead, LodgingItemUpdate),
}

def registrar_historia(
    db: Session,
    plan_id: str,
    categoria: str,
    accion: str,
    elemento_id: int
):
    evento = HistoriaViaje(
        plan_id=plan_id,
        categoria=categoria,
        accion=accion,
        elemento_id=elemento_id
    )
    db.add(evento)
    db.commit()


# ---------------- V2 Hierarchical Endpoint ----------------
from app.schemas.plan_detail import UserPlanResponseV2
from app.services.lodging_service import lodging_suggestion_service

@router.get("/v2/{plan_id}", response_model=UserPlanResponseV2, summary="Obtener detalle jerárquico (V2)")
async def get_plan_v2(plan_id: str, db: Session = Depends(get_db)):
    plan = db.query(UserPlan).filter(UserPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan non-existent")
    
    # Populate city name
    from app.models.ciudad import Ciudad
    ciudad = db.get(Ciudad, plan.origen_id)
    if ciudad:
        plan.ciudad_nombre = ciudad.nombre
        
    # Inject lodging suggestions
    for day in plan.days:
        if day.items:
            suggestion = lodging_suggestion_service.get_suggestion_for_day(db, day.items)
            if suggestion:
                day.lodging_suggestion = suggestion
        
    return plan


@router.get(
    "/{plan_id}",
    response_model=PlanDetalleResponse,
    summary="Obtener detalle completo de un plan"
)
def get_plan_detalle(
    plan_id: str = Path(..., description="ID de la planificación"),
    db: Session = Depends(get_db)
):
    lugares     = db.query(PlanLugar).filter(PlanLugar.plan_id == plan_id).all()
    hospedaje   = db.query(PlanHospedaje).filter(PlanHospedaje.plan_id == plan_id).all()
    actividades = db.query(PlanActividad).filter(PlanActividad.plan_id == plan_id).all()
    transporte  = db.query(PlanTransporte).filter(PlanTransporte.plan_id == plan_id).all()

    return {
        "lugares": lugares,
        "hospedaje": hospedaje,
        "actividades": actividades,
        "transporte": transporte
    }

# ---------------- UserPlan PATCH ----------------
@router.patch("/{plan_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def patch_plan(plan_id: UUID, payload: PlanPatch, db: Session = Depends(get_db)):
    plan = db.get(UserPlan, str(plan_id))
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if payload.budget_clp is not None:
        plan.budget_clp = payload.budget_clp
    if payload.total_days is not None:
        plan.total_days = payload.total_days

    db.add(plan)
    db.commit()
    return None



# ---------------- Stage 8b: Manual Editing Endpoints ----------------

from app.models.plan_item import PlanItem
from app.models.day import PlanDay
from app.schemas.plan_detail import PlanItemUnifiedCreate, PlanItemUnifiedUpdate, PlanItemV3Read

@router.post("/{plan_id}/days", summary="Agregar un día al plan", status_code=status.HTTP_201_CREATED)
def add_day(plan_id: str, db: Session = Depends(get_db)):
    # Find max day number
    max_day = db.query(PlanDay).filter(PlanDay.plan_id == plan_id).order_by(PlanDay.number.desc()).first()
    new_number = (max_day.number + 1) if max_day else 1
    
    new_day = PlanDay(plan_id=plan_id, number=new_number)
    db.add(new_day)
    
    # Update total_days
    plan = db.get(UserPlan, plan_id)
    if plan:
        plan.total_days = new_number
        plan.dias = new_number
        db.add(plan)
        
    db.commit()
    return {"status": "success", "day_id": str(new_day.id), "number": new_number}

@router.delete("/{plan_id}/days/{day_id}", summary="Eliminar un día del plan", status_code=status.HTTP_204_NO_CONTENT)
def delete_day(plan_id: str, day_id: UUID, db: Session = Depends(get_db)):
    day = db.get(PlanDay, day_id)
    if not day or day.plan_id != plan_id:
        raise HTTPException(404, "Day not found")
    
    deleted_number = day.number
    db.delete(day)
    
    # Reorder subsequent days
    subsequent_days = db.query(PlanDay).filter(PlanDay.plan_id == plan_id, PlanDay.number > deleted_number).all()
    for d in subsequent_days:
        d.number -= 1
        db.add(d)
        
    # Update total_days
    plan = db.get(UserPlan, plan_id)
    if plan:
        plan.total_days = max(0, (plan.total_days or 0) - 1)
        plan.dias = plan.total_days
        db.add(plan)
        
    db.commit()
    return None

# ---------------- Deterministic Generation (Stage 4) ----------------

@router.post("/{plan_id}/generate", status_code=status.HTTP_200_OK, summary="Generar itinerario determinístico (Stage 4)")
async def generate_itinerary(plan_id: str, mode: str = "replace", db: Session = Depends(get_db)):
    engine = ItineraryEngine(db)
    try:
        plan = await engine.generate(plan_id, mode=mode)
        return {"status": "success", "plan_id": str(plan.id), "version": plan.generation_version}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class OrganizePayload(BaseModel):
    pacing: str = "normal"

@router.post("/{plan_id}/organize", summary="Organizar automáticamente ítems de la bolsa")
async def organize_wishlist(
    plan_id: str, 
    payload: OrganizePayload = Body(default=OrganizePayload()), 
    db: Session = Depends(get_db)
):
    """
    Toma los ítems sin día (wishlist), los agrupa por cercanía
    y los asigna a los días disponibles de la planificación, respetando el pacing.
    Prioriza la cercanía al punto de origen (Ciudad de inicio).
    """
    # 1. Obtener plan
    plan = db.query(UserPlan).filter(UserPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan non-existent")
    
    # 1.1 Intentar obtener coordenadas del origen
    from app.models.catalog_item import CatalogItem
    from app.models.ciudad import Ciudad
    origin_coords = None
    ciudad = db.get(Ciudad, plan.origen_id)
    if ciudad:
        # Buscar un ítem en el catálogo que coincida con el nombre de la ciudad
        origin_item = db.query(CatalogItem).filter(
            CatalogItem.name.ilike(f"%{ciudad.nombre}%"),
            CatalogItem.item_type == 'place'
        ).first()
        if origin_item:
            origin_coords = {"lat": origin_item.lat, "lng": origin_item.lng}

    # 2. Obtener ítems de la bolsa (day_id is None)
    wishlist_items = db.query(PlanItem).filter(PlanItem.plan_id == plan_id, PlanItem.day_id == None).all()
    
    if not wishlist_items:
        return {"status": "ok", "message": "No hay ítems en la bolsa para organizar", "updates": 0}
    
    # 3. Calcular organización via servicio
    org_result = wishlist_service.organize(wishlist_items, plan.dias, pacing=payload.pacing, origin_coords=origin_coords)
    updates = org_result["updates"]
    suggestions = org_result["suggestions"]
    
    # 4. Mapear días (asegurar que existan en la DB)
    days = db.query(PlanDay).filter(PlanDay.plan_id == plan_id).order_by(PlanDay.number).all()
    day_map = {d.number: d.id for d in days}
    
    # Crear días faltantes si el plan dice tener N días pero no hay registros PlanDay correspondientes
    for i in range(1, plan.dias + 1):
        if i not in day_map:
            new_day = PlanDay(plan_id=plan_id, number=i)
            db.add(new_day)
            db.flush() # Para obtener el ID
            day_map[i] = new_day.id
            
    # 5. Aplicar cambios
    updated_count = 0
    for up in updates:
        # Usamos filter por si acaso, aunque db.get(PlanItem, up['item_id']) sería más rápido
        item = db.query(PlanItem).filter(PlanItem.id == up['item_id']).first()
        if item:
            item.day_id = day_map.get(up['day_number'])
            item.sort_order = up['sort_order']
            updated_count += 1
            
    db.commit()

    # 6. Recalcular segmentos para cada día afectado
    segment_service = ItinerarySegmentService(db)
    for day_id in day_map.values():
        await segment_service.generate_segments_for_day(plan_id, str(day_id))

    return {
        "status": "organized",
        "updates": updated_count,
        "message": f"Se han organizado {updated_count} ítems en los días existentes.",
        "suggestions": suggestions
    }


# ---------------- CRUD genérico (Items V2) ----------------

def _get_resources(kind: str):
    if kind not in item_map:
        raise HTTPException(404, "Resource kind not found")
    return item_map[kind]


@router.get("/{plan_id}/{kind}", response_model=Union[List[PlaceItemRead], List[ActivityItemRead], List[TransportSegmentRead], List[LodgingItemRead]])
async def list_items(plan_id: UUID, kind: str, db: Session = Depends(get_db)):
    Model, _, ReadSchema, _ = _get_resources(kind)
    items = db.query(Model).filter(Model.plan_id == plan_id).all()
    # Pydantic v2 use from_attributes/model_validate instead of from_orm
    return [ReadSchema.model_validate(i) for i in items]


@router.post("/{plan_id}/{kind}", response_model=Union[PlaceItemRead, ActivityItemRead, TransportSegmentRead, LodgingItemRead], status_code=status.HTTP_201_CREATED)
async def create_item(plan_id: UUID, kind: str, payload: Union[PlaceItemCreate, ActivityItemCreate, TransportSegmentCreate, LodgingItemCreate], db: Session = Depends(get_db)):
    Model, CreateSchema, ReadSchema, _ = _get_resources(kind)
    # assert isinstance(payload, CreateSchema)
    obj = Model(plan_id=plan_id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ReadSchema.model_validate(obj)


@router.put("/{plan_id}/{kind}/{item_id}", response_model=Union[PlaceItemRead, ActivityItemRead, TransportSegmentRead, LodgingItemRead])
async def update_item(plan_id: UUID, kind: str, item_id: UUID, payload: Union[PlaceItemUpdate, ActivityItemUpdate, TransportSegmentUpdate, LodgingItemUpdate], db: Session = Depends(get_db)):
    Model, _, ReadSchema, _ = _get_resources(kind)
    obj: Model | None = db.get(Model, item_id)
    if not obj or obj.plan_id != plan_id:
        raise HTTPException(404, "Item not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ReadSchema.model_validate(obj)


@router.delete("/{plan_id}/{kind}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(plan_id: UUID, kind: str, item_id: UUID, db: Session = Depends(get_db)):
    Model, _, _, _ = _get_resources(kind)
    obj: Model | None = db.get(Model, item_id)
    if not obj or obj.plan_id != plan_id:
        raise HTTPException(404, "Item not found")

    db.delete(obj)
    db.commit()
    return None



@router.post("/{plan_id}/unified/items", summary="Crear item unificado", response_model=PlanItemV3Read, status_code=status.HTTP_201_CREATED)
async def create_unified_item(plan_id: str, payload: PlanItemUnifiedCreate, db: Session = Depends(get_db)):
    # Verify plan exists
    plan = db.get(UserPlan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
        
    # If day_id is provided, verify it belongs to this plan
    if payload.day_id:
        day = db.get(PlanDay, payload.day_id)
        if not day or day.plan_id != plan_id:
            raise HTTPException(404, "Day not found or does not belong to plan")
            
    # Create item
    item_data = payload.model_dump()
    # Explicitly ensure plan_id matches the path
    item_data["plan_id"] = plan_id
    
    # Fallback to catalog approximate cost if 0
    if item_data.get("cost_clp", 0) == 0 and item_data.get("catalog_item_id"):
        from app.models.catalog_item import CatalogItem
        cat_item = db.get(CatalogItem, item_data["catalog_item_id"])
        if cat_item and cat_item.approx_cost_clp:
            item_data["cost_clp"] = cat_item.approx_cost_clp
    
    try:
        new_item = PlanItem(**item_data)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        # Recalcular segmentos para el día si el ítem tiene day_id
        if new_item.day_id:
            segment_service = ItinerarySegmentService(db)
            await segment_service.generate_segments_for_plan(plan_id)
            
        return PlanItemV3Read.model_validate(new_item)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating unified item: {str(e)}")
        raise HTTPException(500, f"Database error: {str(e)}")

@router.put("/{plan_id}/unified/items/{item_id}", summary="Actualizar item unificado", response_model=PlanItemV3Read)
async def update_unified_item(plan_id: str, item_id: UUID, payload: PlanItemUnifiedUpdate, db: Session = Depends(get_db)):
    item = db.get(PlanItem, item_id)
    if not item or item.plan_id != plan_id:
        raise HTTPException(404, "Item not found in this plan")
        
    # If day_id is being updated, verify it
    if payload.day_id:
        day = db.get(PlanDay, payload.day_id)
        if not day or day.plan_id != plan_id:
            raise HTTPException(400, "Invalid day_id for this plan")
            
    update_data = payload.model_dump(exclude_unset=True)
    
    # Fallback to catalog cost if user sends 0 explicitly
    if "cost_clp" in update_data and update_data["cost_clp"] == 0:
        cat_id = item.catalog_item_id
        if cat_id:
            from app.models.catalog_item import CatalogItem
            cat_item = db.get(CatalogItem, cat_id)
            if cat_item and cat_item.approx_cost_clp:
                update_data["cost_clp"] = cat_item.approx_cost_clp

    for k, v in update_data.items():
        setattr(item, k, v)
        
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Recalcular segmentos para el día (o los días afectados)
    segment_service = ItinerarySegmentService(db)
    if item.day_id:
        await segment_service.generate_segments_for_plan(plan_id)
    # Note: If day_id changed, the old day might also need regeneration, but for now we focus on the current one
    
    return PlanItemV3Read.model_validate(item)

@router.delete("/{plan_id}/unified/items/{item_id}", summary="Eliminar item unificado", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unified_item(plan_id: str, item_id: UUID, db: Session = Depends(get_db)):
    item = db.get(PlanItem, item_id)
    if not item or item.plan_id != plan_id:
        raise HTTPException(404, "Item not found in this plan")
        
    day_id = str(item.day_id) if item.day_id else None
    db.delete(item)
    db.commit()
    
    # Recalcular segmentos si estaba en un día
    if day_id:
        segment_service = ItinerarySegmentService(db)
        await segment_service.generate_segments_for_plan(plan_id)
        
    return None

class BulkInterestsPayload(BaseModel):
    catalog_item_ids: List[int]

@router.post("/{plan_id}/interests/bulk", summary="Guardar intereses masivos en la bolsa")
def save_bulk_interests(plan_id: str, payload: BulkInterestsPayload, db: Session = Depends(get_db)):
    from app.models.catalog_item import CatalogItem
    
    plan = db.get(UserPlan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
        
    inserted = 0
    for cid in payload.catalog_item_ids:
        # Check if already in plan
        exists = db.query(PlanItem).filter(PlanItem.plan_id == plan_id, PlanItem.catalog_item_id == cid).first()
        if exists: continue
        
        cat_item = db.get(CatalogItem, cid)
        if not cat_item: continue
        
        new_item = PlanItem(
            plan_id=plan_id,
            day_id=None,
            item_type=cat_item.item_type,
            catalog_item_id=cid,
            cost_clp=cat_item.approx_cost_clp or 0,
            metadata_json={
                "name": cat_item.name,
                "description": cat_item.description,
                "lat": cat_item.lat,
                "lng": cat_item.lng
            }
        )
        db.add(new_item)
        inserted += 1
        
    db.commit()
    return {"status": "success", "inserted": inserted}


@router.patch("/{plan_id}/segments/{segment_id}")
async def update_segment(
    plan_id: str,
    segment_id: str,
    update: PlanSegmentUpdate,
    db: Session = Depends(get_db)
):
    segment = db.query(PlanSegment).filter(
        PlanSegment.id == segment_id,
        PlanSegment.plan_id == plan_id
    ).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    if update.transport_mode:
        segment.transport_mode = update.transport_mode
        
        # Al cambiar el modo, debemos recalcular la ruta de este segmento específico
        from app.services.routing_service import RoutingService
        routing = RoutingService()
        
        # Obtener coordenadas de los items conectados
        from app.models.plan_item import PlanItem
        from app.services.itinerary_segment_service import get_item_coordinates
        
        from_item = db.query(PlanItem).get(segment.from_item_id)
        to_item = db.query(PlanItem).get(segment.to_item_id)
        
        if from_item and to_item:
            coords_from = get_item_coordinates(from_item)
            coords_to = get_item_coordinates(to_item)
            
            if coords_from and coords_to:
                route_data = await routing.get_route(
                    coords_from['lat'], coords_from['lng'],
                    coords_to['lat'], coords_to['lng'],
                    mode=segment.transport_mode
                )
                segment.distance_km = route_data["distance_km"]
                segment.duration_minutes = route_data["duration_minutes"]
                segment.route_geometry = route_data["geometry"]
                segment.route_provider = route_data["provider"]

    db.commit()
    return {"status": "updated", "segment_id": segment_id}



