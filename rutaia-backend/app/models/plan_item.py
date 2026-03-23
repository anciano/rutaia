# app/models/plan_item.py

import uuid
from sqlalchemy import Column, Integer, Time, Numeric, ForeignKey, String, Enum, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.database import Base

class PlanItem(Base):
    __tablename__ = "plan_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # plan_id es obligatorio para saber a qué viaje pertenece, incluso si no tiene día asignado
    plan_id = Column(String, ForeignKey("user_plans.id", ondelete="CASCADE"), nullable=False)
    
    # day_id ahora es opcional. NULL = El ítem está en la 'Bolsa de Intereses' (Wishlist)
    day_id = Column(UUID(as_uuid=True), ForeignKey("plan_days.id", ondelete="CASCADE"), nullable=True)
    
    item_type = Column(Enum("place", "activity", "transport", "lodging", "route", name="plan_item_type"), nullable=False)
    
    # Foreign Keys reales por tipo (Legacy)
    place_id    = Column(Integer, ForeignKey("lugares.id"), nullable=True)
    activity_id = Column(Integer, ForeignKey("actividades.id"), nullable=True)
    lodging_id  = Column(Integer, ForeignKey("hospedajes.id"), nullable=True)
    transport_id = Column(Integer, ForeignKey("transportes.id"), nullable=True)
    
    # New Unified Reference (Stage 9)
    catalog_item_id = Column(Integer, ForeignKey("catalog_items.id"), nullable=True)

    sort_order = Column(Integer, nullable=False, default=0)
    start_time = Column(Time, nullable=True)
    end_time   = Column(Time, nullable=True)
    
    # Numeric(12, 0) para CLP sin decimales
    cost_clp = Column(Numeric(12, 0), nullable=False, default=0)
    
    # Metadata para detalles no consultables
    metadata_json = Column(JSONB, nullable=True)

    # Relaciones
    plan = relationship("UserPlan", back_populates="all_items")
    day = relationship("PlanDay", back_populates="items")
    catalog_item = relationship("CatalogItem")

    __table_args__ = (
        # Índices para rendimiento
        Index("idx_plan_items_plan", "plan_id"),
        Index("idx_day_sort", "day_id", "sort_order"),
        Index("idx_item_type", "item_type"),
        
        # Restricción: exactamente una FK no nula según el item_type (Legacy or New)
        CheckConstraint(
            "(catalog_item_id IS NOT NULL) OR "
            "(item_type = 'place' AND place_id IS NOT NULL) OR "
            "(item_type = 'activity' AND activity_id IS NOT NULL) OR "
            "(item_type = 'lodging' AND lodging_id IS NOT NULL) OR "
            "(item_type = 'transport' AND transport_id IS NOT NULL)",
            name="check_item_type_fk_consistency_v2"
        ),
        
        # Restricción: end_time > start_time si ambos existen
        CheckConstraint(
            "end_time > start_time",
            name="check_times_order"
        ),
    )
