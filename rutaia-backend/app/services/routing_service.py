# app/services/routing_service.py

import httpx
import logging
import math
from typing import Optional, List, Dict, Any
from app.settings import OSRM_BASE_URL

logger = logging.getLogger(__name__)

class RoutingService:
    """
    Service for calculating routes between two points using OSRM or direct lines.
    """

    @staticmethod
    def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate the great circle distance in kilometers."""
        R = 6371.0 # Earth radius in km
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (math.sin(d_lat / 2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(d_lng / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    async def get_route(
        self, 
        from_lat: float, 
        from_lng: float, 
        to_lat: float, 
        to_lng: float, 
        mode: str = "car"
    ) -> Dict[str, Any]:
        """
        Main entry point for routing. Handles mode-specific logic.
        """
        if mode in ("car", "bus"):
            return await self._get_osrm_route(from_lat, from_lng, to_lat, to_lng, profile="driving")
        elif mode == "walk":
            return await self._get_osrm_route(from_lat, from_lng, to_lat, to_lng, profile="foot")
        else:
            # ferry, flight, unknown -> direct line
            return self._get_direct_route(from_lat, from_lng, to_lat, to_lng, mode=mode)

    async def _get_osrm_route(
        self, 
        from_lat: float, 
        from_lng: float, 
        to_lat: float, 
        to_lng: float, 
        profile: str = "driving"
    ) -> Dict[str, Any]:
        """
        Calls OSRM API for road routing.
        """
        url = f"{OSRM_BASE_URL}/route/v1/{profile}/{from_lng},{from_lat};{to_lng},{to_lat}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()

                if data.get("code") == "Ok" and data.get("routes"):
                    route = data["routes"][0]
                    return {
                        "distance_km": round(route["distance"] / 1000, 2),
                        "duration_minutes": round(route["duration"] / 60),
                        "geometry": route["geometry"],
                        "provider": "osrm"
                    }
                else:
                    logger.warning(f"OSRM returned no route: {data.get('code')}")
        except Exception as e:
            logger.error(f"Error calling OSRM: {str(e)}")

        # Fallback to direct line if OSRM fails
        return self._get_direct_route(from_lat, from_lng, to_lat, to_lng, mode="unknown (failed osrm)")

    def _get_direct_route(
        self, 
        from_lat: float, 
        from_lng: float, 
        to_lat: float, 
        to_lng: float, 
        mode: str
    ) -> Dict[str, Any]:
        """
        Generates a direct line (Great Circle) between two points.
        """
        dist = self.haversine(from_lat, from_lng, to_lat, to_lng)
        
        # Estimate duration based on mode
        speed_map = {
            "car": 60,
            "walk": 5,
            "ferry": 20,
            "flight": 400,
            "bus": 50,
            "unknown": 50
        }
        speed = speed_map.get(mode.split(" ")[0], 50)
        duration = round((dist / speed) * 60) + 5 # +5 mins overhead
        
        return {
            "distance_km": round(dist, 2),
            "duration_minutes": duration,
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [from_lng, from_lat],
                    [to_lng, to_lat]
                ]
            },
            "provider": "direct_line"
        }
