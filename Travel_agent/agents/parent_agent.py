"""
Parent Tourism Agent - Orchestrates child agents based on user intent
"""
import re
from agents.weather_agent import WeatherAgent
from agents.places_agent import PlacesAgent


class TourismAgent:
    """
    Parent agent that orchestrates the tourism system.
    Routes user queries to appropriate child agents (Weather Agent and Places Agent).
    """
    
    def __init__(self):
        self.name = "Tourism AI Agent"
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()
    
    def extract_place_name(self, query: str) -> str:
        """
        Extract the place name from user query
        
        Args:
            query: User's query string
            
        Returns:
            Extracted place name
        """
        # Common patterns to extract place names
        patterns = [
            r"(?:go(?:ing)? to|visit(?:ing)?|in|at|for)\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*\?|\s*\.|\s+let|\s+what|\s+and|$)",
            r"([A-Z][a-zA-Z\s]+?)(?:\s+let\'s plan|\s+what is|\s+temperature|\s+weather)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, look for capitalized words
        words = query.split()
        for i, word in enumerate(words):
            if word[0].isupper() and word.lower() not in ['i', 'what', 'and', 'the']:
                # Get consecutive capitalized words
                place_parts = [word]
                for next_word in words[i+1:]:
                    if next_word[0].isupper() or next_word.lower() in ['and', 'the']:
                        place_parts.append(next_word)
                    else:
                        break
                return ' '.join(place_parts).strip()
        
        return ""
    
    def run(self, user_query: str) -> str:
        """
        Process user query and route to appropriate child agents
        
        Args:
            user_query: User's input query
            
        Returns:
            Response from child agent(s)
        """
        try:
            # Extract place name from query
            place_name = self.extract_place_name(user_query)
            
            if not place_name:
                return "I couldn't identify which place you're asking about. Could you please specify the location?"
            
            # Determine which agents to invoke
            needs_weather = self.weather_agent.can_handle(user_query)
            needs_places = self.places_agent.can_handle(user_query)
            
            # If neither agent matches, default to places for trip planning
            if not needs_weather and not needs_places:
                needs_places = True
            
            responses = []
            
            # Get weather information if needed
            if needs_weather:
                weather_response = self.weather_agent.run(place_name)
                responses.append(weather_response)
            
            # Get places information if needed
            if needs_places:
                places_response = self.places_agent.run(place_name)
                responses.append(places_response)
            
            # Combine responses naturally
            if len(responses) == 1:
                return responses[0]
            else:
                # Both weather and places
                return f"{responses[0]} And {responses[1].split(place_name)[1] if place_name in responses[1] else responses[1]}"
        
        except Exception as e:
            return f"I encountered an error processing your request: {str(e)}"


def create_tourism_agent():
    """Create and return the tourism agent"""
    return TourismAgent()
