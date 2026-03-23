# app/engine/allocator.py

from datetime import datetime, timedelta, time, date
from typing import List, Dict, Optional
from app.engine.models import GenerationContext, ScoredItem

class SmartAllocator:
    """
    Allocates items to days and time slots, respecting budget and time constraints.
    """
    def __init__(self, context: GenerationContext):
        self.context = context
        self.days: Dict[int, List[dict]] = {i: [] for i in range(1, context.num_days + 1)}
        self.daily_balances: Dict[int, int] = {i: 0 for i in range(1, context.num_days + 1)}

    def _get_start_time_for_day(self, day_number: int) -> datetime:
        # Dummy date for time calculation
        base_date = self.context.start_date or date(2025, 1, 1)
        current_date = base_date + timedelta(days=day_number - 1)
        return datetime.combine(current_date, self.context.time_policy.day_start)

    def allocate(self, ranked_items: List[ScoredItem]):
        """
        Greedy allocation: Fill days sequentially or spread items?
        Based on user intent, we'll try to fill slots within the day_start/day_end window.
        """
        for item in ranked_items:
            allocated = False
            for day_num in range(1, self.context.num_days + 1):
                if self._can_fit_in_day(day_num, item):
                    self._add_to_day(day_num, item)
                    allocated = True
                    break
            if not allocated:
                # Log or handle unallocated item if necessary
                pass

    def _can_fit_in_day(self, day_num: int, item: ScoredItem) -> bool:
        # Check daily budget balance
        if self.daily_balances[day_num] + item.cost_clp > self.context.budget_policy.daily_budget_clp:
            return False

        # Check time window
        last_end = self._get_last_end_time(day_num)
        new_end = last_end + timedelta(minutes=item.duration_minutes)
        day_end_dt = datetime.combine(last_end.date(), self.context.time_policy.day_end)
        
        if new_end > day_end_dt:
            return False

        return True

    def _get_last_end_time(self, day_num: int) -> datetime:
        if not self.days[day_num]:
            return self._get_start_time_for_day(day_num)
        return self.days[day_num][-1]["end_time"]

    def _add_to_day(self, day_num: int, item: ScoredItem):
        start_time = self._get_last_end_time(day_num)
        end_time = start_time + timedelta(minutes=item.duration_minutes)
        
        self.days[day_num].append({
            "item": item,
            "start_time": start_time,
            "end_time": end_time,
            "sort_order": len(self.days[day_num]) + 1  # 1..N convention
        })
        self.daily_balances[day_num] += item.cost_clp

    def get_result(self):
        return self.days
