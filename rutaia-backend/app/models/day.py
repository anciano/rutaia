# app/models/day.py

import uuid
from sqlalchemy import Column, Integer, Date, Text, ForeignKey, String, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.database import Base

class PlanDay(Base):
    __tablename__ = "plan_days"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(String, ForeignKey("user_plans.id", ondelete="CASCADE"), nullable=False)
    number = Column(Integer, nullable=False)
    date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Relaciones
    plan = relationship("UserPlan", back_populates="days")
    items = relationship("PlanItem", back_populates="day", cascade="all, delete-orphan", order_by="PlanItem.sort_order")
    day_segments = relationship("PlanSegment", back_populates="day", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("plan_id", "number", name="uq_plan_day_number"),
        Index("idx_day_plan_id", "plan_id"),
    )
