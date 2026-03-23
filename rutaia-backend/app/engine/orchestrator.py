# app/engine/orchestrator.py

import datetime
from sqlalchemy.orm import Session
from app.models import (
    UserPlan, PlanDay, PlanItem, CatalogItem, CatalogCategory
)
from app.engine.models import GenerationContext, BudgetPolicy, TimePolicy, ScoredItem
from app.engine.filters import HardBudgetFilter, DuplicateFilter
from app.engine.rankers import ScoringPipeline, PreferenceScorer, PopularityScorer, DiversityScorer
from app.engine.allocator import SmartAllocator
from app.services.itinerary_segment_service import ItinerarySegmentService

class ItineraryEngine:
    def __init__(self, db: Session):
        self.db = db

    async def generate(self, plan_id: str, mode: str = "replace"):
        plan = self.db.query(UserPlan).filter(UserPlan.id == plan_id).first()
        if not plan:
            raise ValueError("Plan not found")

        if plan.dias < 1:
            raise ValueError("Plan must have at least 1 day for generation")

        # 1. Setup Context
        context = GenerationContext(
            plan_id=plan.id,
            city_id=plan.origen_id,
            num_days=plan.dias,
            start_date=plan.fecha_inicio,
            budget_policy=BudgetPolicy(
                daily_budget_clp=plan.presupuesto // plan.dias,
                max_item_cost_ratio=0.8 # More flexible for manual items
            ),
            time_policy=TimePolicy(),
            mode=mode
        )

        # 2. Fetch Candidates (Optimized fetch)
        candidates = self._fetch_candidates(context)

        # Duplicate filter: find scheduled items (day_id NOT NULL)
        scheduled_items = self.db.query(PlanItem.catalog_item_id).filter(
            PlanItem.plan_id == plan.id,
            PlanItem.catalog_item_id.isnot(None),
            PlanItem.day_id.isnot(None)
        ).all()
        scheduled_ids = [row[0] for row in scheduled_items]

        # Wishlist items (day_id IS NULL) - we want to KEEP these
        wishlist_ids = [c.item_id for c in candidates if c.score >= 500.0]
        
        filters = [
            HardBudgetFilter(),
            DuplicateFilter(scheduled_ids, ignore_ids=wishlist_ids)
        ]
        for f in filters:
            candidates = f.apply(candidates, context)

        # 4. Rank
        pref_data = plan.preferencias if isinstance(plan.preferencias, dict) else {}
        user_tags = pref_data.get("tags", [])
        pipeline = ScoringPipeline([
            PreferenceScorer(user_tags),
            PopularityScorer(),
            DiversityScorer([]) # Start with empty categories
        ])
        ranked_items = pipeline.run(candidates, context)

        # 5. Allocate
        allocator = SmartAllocator(context)
        allocator.allocate(ranked_items)
        allocation_result = allocator.get_result()

        # 6. Persist
        self._persist_results(plan, allocation_result, mode)
        
        # 7. Recalcular segmentos para todo el plan (incluyendo inter-día)
        segment_service = ItinerarySegmentService(self.db)
        await segment_service.generate_segments_for_plan(plan.id)
        
        return plan

    def _fetch_candidates(self, context: GenerationContext) -> list[ScoredItem]:
        scored_items = []
        
        # A. Fetch Wishlist Items (Interests)
        interests = self.db.query(PlanItem).filter(
            PlanItem.plan_id == context.plan_id,
            PlanItem.day_id == None,
            PlanItem.catalog_item_id.isnot(None)
        ).all()
        
        for wish in interests:
            # Puntuación máxima para intereses manuales
            scored_items.append(ScoredItem(
                item_id=wish.catalog_item_id,
                item_type=wish.item_type,
                score=1000.0, # Prioridad máxima
                cost_clp=float(wish.cost_clp),
                duration_minutes=90, # Default
                metadata={
                    "name": wish.metadata_json.get("name") if wish.metadata_json else "Interés",
                    "lat": wish.metadata_json.get("lat") if wish.metadata_json else None,
                    "lng": wish.metadata_json.get("lng") if wish.metadata_json else None,
                    "tags": ["wishlist"]
                }
            ))

        # B. Fetch CatalogItems (Places and Activities)
        # Avoid redundant candidates if already in interests
        interest_cids = {w.catalog_item_id for w in interests}
        
        items = self.db.query(CatalogItem).filter(
            CatalogItem.is_active == True,
            CatalogItem.item_type.in_(['place', 'activity']),
            CatalogItem.locality_id == context.city_id
        ).all()

        for item in items:
            if item.id in interest_cids: continue
            
            duration = item.estimated_duration_minutes or 90
            tags = [item.category.name] if item.category else []
            
            scored_items.append(ScoredItem(
                item_id=item.id,
                item_type=item.item_type,
                score=0.0,
                cost_clp=float(item.approx_cost_clp or 0),
                duration_minutes=duration,
                metadata={
                    "tags": tags,
                    "rating": 4.0,
                    "category": item.category.name if item.category else "Uncategorized",
                    "lat": item.lat,
                    "lng": item.lng,
                    "name": item.name
                }
            ))
            
        return scored_items

    def _persist_results(self, plan: UserPlan, allocation: dict, mode: str):
        if mode == "replace":
            # Clear existing hierarchy
            for day in plan.days:
                self.db.delete(day)
            self.db.flush()

        # Create new hierarchy
        for day_num, items in allocation.items():
            db_day = self.db.query(PlanDay).filter(PlanDay.plan_id == plan.id, PlanDay.number == day_num).first()
            if not db_day:
                db_day = PlanDay(
                    plan_id=plan.id,
                    number=day_num,
                    date=plan.fecha_inicio + datetime.timedelta(days=day_num-1) if plan.fecha_inicio else None
                )
                self.db.add(db_day)
                self.db.flush()

            for it in items:
                item_data = it["item"]
                db_item = PlanItem(
                    day_id=db_day.id,
                    item_type=item_data.item_type,
                    sort_order=it["sort_order"],
                    start_time=it["start_time"].time(),
                    end_time=it["end_time"].time(),
                    cost_clp=item_data.cost_clp,
                    plan_id=plan.id,
                    catalog_item_id=item_data.item_id,
                    metadata_json={
                        "name": item_data.metadata.get("name"),
                        "lat": item_data.metadata.get("lat"),
                        "lng": item_data.metadata.get("lng")
                    }
                )
                self.db.add(db_item)

        plan.generated_at = datetime.datetime.now()
        plan.generation_version = (plan.generation_version or 0) + 1
        self.db.commit()
