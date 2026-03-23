import math
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.catalog_item import CatalogItem

class LodgingSuggestionService:
    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def get_suggestion_for_day(self, db: Session, day_items: List[Any], city_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Calculates the geographic centroid of the day's activities and returns
        the closest available lodging from the catalog.
        """
        if not day_items:
            return None

        # 1. Calculate centroid
        lats = []
        lngs = []
        
        for item in day_items:
            meta = item.metadata_json or {}
            
            lat = meta.get('lat')
            lng = meta.get('lng')
            
            if (lat is None or lng is None) and item.catalog_item:
                lat = item.catalog_item.lat
                lng = item.catalog_item.lng

            if lat is not None and lng is not None:
                lats.append(float(lat))
                lngs.append(float(lng))

        if not lats:
            # If no items have coordinates, we could fallback to generic city lodgings if city_id was provided
            return None

        centroid_lat = sum(lats) / len(lats)
        centroid_lng = sum(lngs) / len(lngs)

        # 2. Get all lodgings
        lodgings = db.query(CatalogItem).filter(
            CatalogItem.item_type == 'lodging',
            CatalogItem.is_active == True
        ).all()

        if not lodgings:
            return None

        # 3. Find closest
        closest_lodging = None
        min_distance = float('inf')

        for lodging in lodgings:
            if lodging.lat is not None and lodging.lng is not None:
                dist = self.haversine(centroid_lat, centroid_lng, lodging.lat, lodging.lng)
                if dist < min_distance:
                    min_distance = dist
                    closest_lodging = lodging

        if closest_lodging:
            return {
                "catalog_item_id": closest_lodging.id,
                "name": closest_lodging.name,
                "description": closest_lodging.description,
                "distance_km": round(min_distance, 1),
                "lat": closest_lodging.lat,
                "lng": closest_lodging.lng,
                "approx_cost_clp": closest_lodging.approx_cost_clp
            }

        return None

lodging_suggestion_service = LodgingSuggestionService()
