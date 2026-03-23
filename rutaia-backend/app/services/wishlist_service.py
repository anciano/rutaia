# app/services/wishlist_service.py
import math
from typing import List, Dict, Any, Optional
from uuid import UUID

class WishlistOrganizationService:
    """
    Engine for automatic spatial clustering and day distribution of wishlist items.
    """
    
    EPSILON_KM = 20.0
    
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0 # Earth radius
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
        c = 2 * math.asin(math.sqrt(a))
        return R * c

    def organize(self, items: List[Any], total_days: int, pacing: str = "normal", origin_coords: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        if not items:
            return []

        viable_items = []
        unmappable_items = []
        for it in items:
            meta = it.metadata_json or {}
            
            # 1. Try metadata
            lat = meta.get('lat')
            lng = meta.get('lng')
            
            # 2. Fallback to catalog_item
            if (lat is None or lng is None) and it.catalog_item:
                lat = it.catalog_item.lat
                lng = it.catalog_item.lng

            if lat is not None and lng is not None:
                viable_items.append({
                    'id': it.id,
                    'lat': float(lat),
                    'lng': float(lng),
                    'item': it
                })
            else:
                unmappable_items.append(it)
        
        # If no items have coordinates, just distribute all evenly
        if not viable_items:
            updates = []
            for idx, it in enumerate(unmappable_items):
                day_num = (idx % total_days) + 1
                updates.append({
                    'item_id': it.id,
                    'day_number': day_num,
                    'sort_order': (idx // total_days) * 10
                })
            return {
                "updates": updates,
                "suggestions": None
            }

        # Adjust the clustering radius based on pacing preference
        if pacing == "compact":
            radius_km = self.EPSILON_KM * 2.0  # Willing to travel further to pack more in
        elif pacing == "relaxed":
            radius_km = self.EPSILON_KM * 0.5  # Prefer things very close by
        else:
            radius_km = self.EPSILON_KM

        clusters = []
        visited = set()

        for i, core in enumerate(viable_items):
            if core['id'] in visited:
                continue
            
            current_cluster = [core]
            visited.add(core['id'])
            
            for j, candidate in enumerate(viable_items):
                if candidate['id'] in visited:
                    continue
                
                dist = self.haversine(core['lat'], core['lng'], candidate['lat'], candidate['lng'])
                if dist <= radius_km:
                    current_cluster.append(candidate)
                    visited.add(candidate['id'])
            
            clusters.append(current_cluster)

        # Sort clusters by proximity to origin if available
        if origin_coords and origin_coords.get('lat') is not None:
            def get_cluster_dist(cluster):
                # Distance from origin to the centroid or just the first item
                # Using the closest item in the cluster to the origin as a proxy for the cluster's "start"
                min_dist = float('inf')
                for item in cluster:
                    d = self.haversine(origin_coords['lat'], origin_coords['lng'], item['lat'], item['lng'])
                    if d < min_dist: min_dist = d
                return min_dist
            
            clusters.sort(key=get_cluster_dist)
        else:
            # Sort clusters by size descending to prioritize assigning the largest clusters (Legacy)
            clusters.sort(key=len, reverse=True)
        
        assigned_clusters = clusters[:total_days]
        overflow_clusters = clusters[total_days:]

        updates = []
        current_reference = origin_coords
        
        for day_idx, cluster in enumerate(assigned_clusters):
            day_number = day_idx + 1
            
            # Sort items in cluster using nearest-neighbor from current_reference
            sorted_cluster = []
            remaining_in_cluster = list(cluster)
            
            while remaining_in_cluster:
                if current_reference and current_reference.get('lat') is not None:
                    # Find closest to current_reference
                    closest = min(
                        remaining_in_cluster, 
                        key=lambda x: self.haversine(current_reference['lat'], current_reference['lng'], x['lat'], x['lng'])
                    )
                else:
                    # No reference, just take first
                    closest = remaining_in_cluster[0]
                
                sorted_cluster.append(closest)
                remaining_in_cluster.remove(closest)
                current_reference = {'lat': closest['lat'], 'lng': closest['lng']}
            
            for sort_idx, item_data in enumerate(sorted_cluster):
                updates.append({
                    'item_id': item_data['id'],
                    'day_number': day_number,
                    'sort_order': sort_idx * 10
                })
        
        overflow_item_ids = []
        for cluster in overflow_clusters:
            for item_data in cluster:
                overflow_item_ids.append(item_data['id'])
        
        # Handle unmappable items by distributing them evenly across all days
        for idx, it in enumerate(unmappable_items):
            day_num = (idx % total_days) + 1
            # Put them at the end of the day's current sort order
            # approximate by just using a large number or 100 + idx
            updates.append({
                'item_id': it.id,
                'day_number': day_num,
                'sort_order': 100 + idx
            })
            
        suggestions = None
        if overflow_item_ids:
            suggestions = {
                "message": f"Estas {len(overflow_item_ids)} actividades están en otra zona. ¿Quieres extender tu viaje {len(overflow_clusters)} día(s)?",
                "days_to_add": len(overflow_clusters),
                "unassigned_count": len(overflow_item_ids)
            }
            
        return {
            "updates": updates,
            "suggestions": suggestions
        }

wishlist_service = WishlistOrganizationService()
