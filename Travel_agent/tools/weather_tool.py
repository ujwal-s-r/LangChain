"""
Weather Tool - Fetches current weather information using Open-Meteo API
"""
import requests
from langchain.tools import tool
from typing import Dict
from .geocoding_tool import get_coordinates


@tool
def get_weather(place_name: str) -> str:
    """
    Get current weather information for a given place including temperature and precipitation.
    
    This tool fetches real-time weather data including current temperature and chance of rain
    for any location in the world. It automatically handles geocoding the place name.
    
    Args:
        place_name: The name of the place/city to get weather for (e.g., "Bangalore", "Paris", "Tokyo")
    
    Returns:
        A formatted string with weather information or an error message.
        Format: "In [Place] it's currently [X]°C with a chance of [Y]% to rain."
        
    Example:
        get_weather("Bangalore")
        Returns: "In Bangalore it's currently 24°C with a chance of 35% to rain."
    """
    try:
        # First, get coordinates for the place
        geo_result = get_coordinates.invoke({"place_name": place_name})
        
        if not geo_result["success"]:
            return f"I don't know if the place '{place_name}' exists. {geo_result['error']}"
        
        latitude = geo_result["latitude"]
        longitude = geo_result["longitude"]
        place_display = geo_result["place"].split(",")[0]  # Get just the city name
        
        # Open-Meteo API endpoint
        url = "https://api.open-meteo.com/v1/forecast"
        
        # Query parameters for current weather
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "precipitation_probability"],
            "temperature_unit": "celsius"
        }
        
        # Make request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract weather information
        current = data.get("current", {})
        temperature = current.get("temperature_2m")
        precipitation_prob = current.get("precipitation_probability", 0)
        
        # Format response
        if temperature is not None:
            weather_info = f"In {place_display} it's currently {temperature}°C with a chance of {precipitation_prob}% to rain."
            return weather_info
        else:
            return f"Weather data is currently unavailable for {place_display}."
            
    except requests.exceptions.Timeout:
        return "Weather service timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}"
    except Exception as e:
        return f"Unexpected error getting weather: {str(e)}"
