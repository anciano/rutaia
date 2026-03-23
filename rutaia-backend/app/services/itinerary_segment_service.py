# app/services/itinerary_segment_service.py

from sqlalchemy.orm import Session
from app.models.plan_item import PlanItem
from app.models.plan_segment import PlanSegment
from app.services.routing_service import RoutingService
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def get_item_coordinates(item: PlanItem) -> Optional[dict]:
    """Extract coordinates from PlanItem metadata or catalog."""
    lat = item.metadata_json.get('lat') if item.metadata_json else None
    lng = item.metadata_json.get('lng') if item.metadata_json else None
    
    if lat is not None and lng is not None:
        return {'lat': lat, 'lng': lng}
        
    if item.catalog_item:
        return {'lat': item.catalog_item.lat, 'lng': item.catalog_item.lng}
        
    return None

class ItinerarySegmentService:
    def __init__(self, db: Session):
        self.db = db
        self.routing_service = RoutingService()

    async def generate_segments_for_plan(self, plan_id: str):
        """
        Generates or updates segments for the entire itinerary sequence, including inter-day transitions.
        """
        from app.models.day import PlanDay
        
        # Fetch all items that are assigned to a day, ordered by day number and sort_order
        items = self.db.query(PlanItem).join(
            PlanItem.day
        ).filter(
            PlanItem.plan_id == plan_id,
            PlanItem.day_id.isnot(None)
        ).order_by(
            PlanDay.number,
            PlanItem.sort_order
        ).all()

        if len(items) < 2:
            # Clear existing segments
            self.db.query(PlanSegment).filter(PlanSegment.plan_id == plan_id).delete()
            self.db.commit()
            return []

        # Get existing segments to avoid redundant API calls
        existing_segments = {
            (str(s.from_item_id), str(s.to_item_id)): s 
            for s in self.db.query(PlanSegment).filter(PlanSegment.plan_id == plan_id).all()
        }
        
        segments = []
        for i in range(len(items) - 1):
            from_item = items[i]
            to_item = items[i+1]
            
            # Get coordinates
            from_coords = get_item_coordinates(from_item)
            to_coords = get_item_coordinates(to_item)
            
            if not from_coords or not to_coords:
                continue

            # Check if segment already exists
            pair = (str(from_item.id), str(to_item.id))
            if pair in existing_segments:
                seg = existing_segments[pair]
                # Optional: check if transport mode needs update or if geometry is missing
                # For now we keep it and move to next
                segments.append(seg)
                continue

            # Calculate new route
            try:
                route_data = await self.routing_service.get_route(
                    from_coords['lat'], from_coords['lng'],
                    to_coords['lat'], to_coords['lng'],
                    mode="car" # Default
                )

                new_seg = PlanSegment(
                    plan_id=plan_id,
                    day_id=from_item.day_id, # Always link to the "departure" day
                    from_item_id=from_item.id,
                    to_item_id=to_item.id,
                    transport_mode="car",
                    distance_km=route_data['distance_km'],
                    duration_minutes=route_data['duration_minutes'],
                    route_geometry=route_data['geometry'],
                    route_provider=route_data['provider']
                )
                self.db.add(new_seg)
                segments.append(new_seg)
            except Exception as e:
                logger.error(f"Error calculating route between {from_item.id} and {to_item.id}: {e}")

        # Cleanup segments that are no longer valid
        valid_ids = [s.id for s in segments if s.id]
        if valid_ids:
            self.db.query(PlanSegment).filter(
                PlanSegment.plan_id == plan_id,
                PlanSegment.id.notin_(valid_ids)
            ).delete(synchronize_session=False)
        else:
            self.db.query(PlanSegment).filter(PlanSegment.plan_id == plan_id).delete()

        self.db.commit()
        return segments

    async def generate_segments_for_day(self, plan_id: str, day_id: str):
        # Legacy/Compatibility: Redirect to plan-wide generation
        return await self.generate_segments_for_plan(plan_id)


itinerary_segment_service = ItinerarySegmentService(None) # Instance to be used with db injection pattern
