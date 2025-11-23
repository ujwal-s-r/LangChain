"""
Geocoding Tool - Converts place names to geographic coordinates using Nominatim API
"""
import requests
from langchain.tools import tool
from typing import Dict, Optional


@tool
def get_coordinates(place_name: str) -> Dict[str, any]:
    """
    Get geographic coordinates (latitude, longitude) for a given place name.
    
    This tool converts a place name into geographic coordinates using the Nominatim API.
    Use this tool whenever you need to find the location of a place before getting weather
    or tourist information.
    
    Args:
        place_name: The name of the place/city/location to geocode (e.g., "Bangalore", "Paris", "New York")
    
    Returns:
        Dictionary containing:
        - success: Boolean indicating if the place was found
        - place: The full display name of the place
        - latitude: Latitude coordinate
        - longitude: Longitude coordinate
        - error: Error message if place not found
    
    Example:
        get_coordinates("Bangalore") 
        Returns: {"success": True, "place": "Bangalore, Karnataka, India", "latitude": 12.9716, "longitude": 77.5946}
    """
    try:
        # Nominatim API endpoint
        url = "https://nominatim.openstreetmap.org/search"
        
        # Headers with user agent (required by Nominatim)
        headers = {
            "User-Agent": "TourismAIAgent/1.0"
        }
        
        # Query parameters
        params = {
            "q": place_name,
            "format": "json",
            "limit": 1
        }
        
        # Make request
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if place was found
        if not data or len(data) == 0:
            return {
                "success": False,
                "error": f"Place '{place_name}' not found. Please check the spelling or try a different name.",
                "place": None,
                "latitude": None,
                "longitude": None
            }
        
        # Extract coordinates
        place_data = data[0]
        latitude = float(place_data["lat"])
        longitude = float(place_data["lon"])
        display_name = place_data["display_name"]
        
        return {
            "success": True,
            "place": display_name,
            "latitude": latitude,
            "longitude": longitude,
            "error": None
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Geocoding service timed out. Please try again.",
            "place": None,
            "latitude": None,
            "longitude": None
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error connecting to geocoding service: {str(e)}",
            "place": None,
            "latitude": None,
            "longitude": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error during geocoding: {str(e)}",
            "place": None,
            "latitude": None,
            "longitude": None
        }
