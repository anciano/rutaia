# app/engine/models.py

from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional, List
from uuid import UUID

class BudgetPolicy(BaseModel):
    daily_budget_clp: int
    max_item_cost_ratio: float = 0.5  # Max cost of single item relative to daily budget

class TimePolicy(BaseModel):
    day_start: time = time(9, 0)
    day_end: time = time(21, 0)
    default_item_duration_minutes: int = 60

class GenerationContext(BaseModel):
    plan_id: str
    city_id: str
    num_days: int
    start_date: Optional[date] = None
    
    budget_policy: BudgetPolicy
    time_policy: TimePolicy
    
    # Metadata for the generation run
    mode: str = "replace"  # "replace" or "append"
    engine_version: str = "1.0.0"
    
    class Config:
        from_attributes = True

class ScoredItem(BaseModel):
    item_id: int
    item_type: str
    score: float
    cost_clp: int
    duration_minutes: int
    metadata: dict = {}
