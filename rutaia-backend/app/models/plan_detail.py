# app/models/plan_detail.py

import uuid
from datetime import datetime, time
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Time,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.database import Base

class PlaceItem(Base):
    __tablename__ = "place_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(String, ForeignKey("user_plans.id", ondelete="CASCADE"))

    name = Column(String(120), nullable=False)
    place_id = Column(Integer, ForeignKey("lugares.id"), nullable=True)
    day = Column(Integer, nullable=True)
    cost_clp = Column(Numeric(10, 0), nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)

    plan = relationship("UserPlan", back_populates="place_items")


class ActivityItem(Base):
    __tablename__ = "activity_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(String, ForeignKey("user_plans.id", ondelete="CASCADE"))

    description = Column(String(160), nullable=False)
    level = Column(Enum("baja", "media", "alta", name="activity_intensity"), default="media")
    day = Column(Integer, nullable=True)
    cost_clp = Column(Numeric(10, 0), nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)

    plan = relationship("UserPlan", back_populates="activity_items")


class TransportSegment(Base):
    __tablename__ = "transport_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(String, ForeignKey("user_plans.id", ondelete="CASCADE"))

    origin_name = Column(String(120), nullable=False)
    destination_name = Column(String(120), nullable=False)
    mode = Column(Enum("auto", "bus", "avion", "barco", name="transport_mode"), nullable=False)
    distance_km = Column(Numeric(8, 2), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    cost_clp = Column(Numeric(10, 0), nullable=True)

    plan = relationship("UserPlan", back_populates="transport_segments")


class LodgingItem(Base):
    __tablename__ = "lodging_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(String, ForeignKey("user_plans.id", ondelete="CASCADE"))

    name = Column(String(120), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    cost_clp = Column(Numeric(10, 0), nullable=True)

    plan = relationship("UserPlan", back_populates="lodging_items")


class TravelLog(Base):
    __tablename__ = "travel_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(String, ForeignKey("user_plans.id", ondelete="CASCADE"))
    item_type = Column(String(32), nullable=False)
    item_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(Enum("created", "updated", "deleted", name="log_action"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    plan = relationship("UserPlan", back_populates="logs")
