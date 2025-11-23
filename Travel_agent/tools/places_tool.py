"""
Places/Tourism Tool - Finds tourist attractions using Overpass API (OpenStreetMap)
"""
import requests
from langchain.tools import tool
from typing import List, Dict
from .geocoding_tool import get_coordinates


@tool
def get_tourist_places(place_name: str) -> str:
    """
    Get up to 5 tourist attractions and points of interest for a given place.
    
    This tool finds popular tourist attractions, landmarks, parks, museums, and other
    interesting places to visit in the specified location using OpenStreetMap data.
    
    Args:
        place_name: The name of the place/city to find attractions in (e.g., "Bangalore", "Paris", "Tokyo")
    
    Returns:
        A formatted string listing tourist attractions or an error message.
        Format: "In [Place] these are the places you can go,\n[Place1]\n[Place2]\n..."
        
    Example:
        get_tourist_places("Bangalore")
        Returns: "In Bangalore these are the places you can go, 
        Lalbagh
        Sri Chamarajendra Park
        Bangalore Palace
        Bannerghatta National Park
        Jawaharlal Nehru Planetarium"
    """
    try:
        # First, get coordinates for the place
        geo_result = get_coordinates.invoke({"place_name": place_name})
        
        if not geo_result["success"]:
            return f"I don't know if the place '{place_name}' exists. {geo_result['error']}"
        
        latitude = geo_result["latitude"]
        longitude = geo_result["longitude"]
        place_display = geo_result["place"].split(",")[0]  # Get just the city name
        
        # Overpass API endpoint
        url = "https://overpass-api.de/api/interpreter"
        
        # Search radius in meters (approximately 10km)
        radius = 10000
        
        # Overpass QL query to find tourist attractions with center points for ways
        # Searches for tourism=* tags (attractions, museums, viewpoints, etc.)
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"](around:{radius},{latitude},{longitude});
          way["tourism"](around:{radius},{latitude},{longitude});
          node["leisure"="park"](around:{radius},{latitude},{longitude});
          way["leisure"="park"](around:{radius},{latitude},{longitude});
          node["historic"](around:{radius},{latitude},{longitude});
          way["historic"](around:{radius},{latitude},{longitude});
        );
        out body center;
        >;
        out skel qt;
        """
        
        # Make request
        response = requests.post(url, data={"data": query}, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        elements = data.get("elements", [])
        
        # Extract place names with coordinates
        places = []
        places_with_coords = []
        seen_names = set()
        
        for element in elements:
            tags = element.get("tags", {})
            name = tags.get("name")
            
            if name and name not in seen_names:
                places.append(name)
                seen_names.add(name)
                
                # Get coordinates (handle both nodes and ways)
                lat = element.get("lat")
                lon = element.get("lon")
                
                # For ways, calculate center point
                if lat is None or lon is None:
                    if element.get("type") == "way" and "center" in element:
                        lat = element["center"].get("lat")
                        lon = element["center"].get("lon")
                
                if lat and lon:
                    places_with_coords.append(f"{name}|{lat}|{lon}")
                
                # Stop after finding 5 places
                if len(places) >= 5:
                    break
        
        # Format response
        if places:
            places_list = "\n".join(places)
            coords_list = "\n".join(places_with_coords)
            return f"In {place_display} these are the places you can go,\n{places_list}\nCOORDS:\n{coords_list}"
        else:
            return f"I couldn't find specific tourist attractions in {place_display} in the database, but it may still be a great place to visit!"
            
    except requests.exceptions.Timeout:
        return "Tourist places service timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error fetching tourist places: {str(e)}"
    except Exception as e:
        return f"Unexpected error getting tourist places: {str(e)}"
