"""
Places Agent - Specialized child agent for tourist attractions queries
"""
from tools import get_tourist_places


class PlacesAgent:
    """
    Child agent specialized in handling tourist attractions and places queries.
    Uses the get_tourist_places tool to fetch popular attractions in any location.
    """
    
    def __init__(self):
        self.name = "Places Agent"
        self.description = "Handles tourist attractions and places to visit requests"
    
    def run(self, place_name: str) -> str:
        """
        Execute places query for a given location
        
        Args:
            place_name: Name of the place to find attractions in
            
        Returns:
            Formatted list of tourist attractions
        """
        try:
            result = get_tourist_places.invoke({"place_name": place_name})
            return result
        except Exception as e:
            return f"Error getting tourist places: {str(e)}"
    
    def can_handle(self, query: str) -> bool:
        """
        Determine if this agent can handle the given query
        
        Args:
            query: User's query string
            
        Returns:
            True if query is about places or attractions
        """
        places_keywords = [
            "place", "places", "visit", "attraction", "attractions",
            "tourist", "tourism", "sightseeing", "landmark", "landmarks",
            "trip", "travel", "destination", "go", "see", "explore",
            "tour", "palace", "museum", "park", "monument"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in places_keywords)
