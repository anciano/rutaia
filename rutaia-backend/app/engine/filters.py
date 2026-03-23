# app/engine/filters.py

from typing import List, Any, Optional
from app.engine.models import GenerationContext, ScoredItem
from abc import ABC, abstractmethod

class BaseFilter(ABC):
    @abstractmethod
    def apply(self, items: List[ScoredItem], context: GenerationContext) -> List[ScoredItem]:
        pass

class CityFilter:
    """
    Note: City filtering is typically done at the DB query level for performance.
    This class can be used to hold the SQL filter logic.
    """
    @staticmethod
    def get_query_filter(model: Any, city_id: str):
        return model.ciudad_id == city_id

class HardBudgetFilter(BaseFilter):
    """
    Filters out items that exceed a certain percentage of the DAILY budget.
    """
    def apply(self, items: List[ScoredItem], context: GenerationContext) -> List[ScoredItem]:
        limit = context.budget_policy.daily_budget_clp * context.budget_policy.max_item_cost_ratio
        return [item for item in items if item.cost_clp <= limit]

class DuplicateFilter(BaseFilter):
    """
    Filter out items already present in the existing plan or current generation.
    """
    def __init__(self, existing_place_ids: List[int], ignore_ids: Optional[List[int]] = None):
        self.existing_place_ids = set(existing_place_ids)
        self.ignore_ids = set(ignore_ids or [])

    def apply(self, items: List[ScoredItem], context: GenerationContext) -> List[ScoredItem]:
        return [item for item in items if item.item_id not in self.existing_place_ids or item.item_id in self.ignore_ids]
