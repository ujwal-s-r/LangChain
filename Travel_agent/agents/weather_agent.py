"""
Weather Agent - Specialized child agent for weather queries
"""
from tools import get_weather


class WeatherAgent:
    """
    Child agent specialized in handling weather-related queries.
    Uses the get_weather tool to fetch current temperature and precipitation data.
    """
    
    def __init__(self):
        self.name = "Weather Agent"
        self.description = "Handles weather information requests for any location"
    
    def run(self, place_name: str) -> str:
        """
        Execute weather query for a given place
        
        Args:
            place_name: Name of the place to get weather for
            
        Returns:
            Formatted weather information string
        """
        try:
            result = get_weather.invoke({"place_name": place_name})
            return result
        except Exception as e:
            return f"Error getting weather information: {str(e)}"
    
    def can_handle(self, query: str) -> bool:
        """
        Determine if this agent can handle the given query
        
        Args:
            query: User's query string
            
        Returns:
            True if query is about weather
        """
        weather_keywords = [
            "weather", "temperature", "temp", "hot", "cold", 
            "rain", "precipitation", "climate", "forecast",
            "degrees", "celsius", "fahrenheit"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in weather_keywords)
