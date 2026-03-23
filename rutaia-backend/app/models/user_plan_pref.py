# app/models/user_plan_preferencia.py
from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID            # 👈
from app.models.database import Base

user_plan_pref = Table(
    "user_plan_preferencias",
    Base.metadata,
    Column("plan_id",        String, ForeignKey("user_plans.id"),      primary_key=True),
    Column("preferencia_id", UUID(as_uuid=True),                       # 👈 mismo tipo que preferencias.id
           ForeignKey("preferencias.id"), primary_key=True),
)