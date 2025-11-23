"""
Pydantic Models - Structured output schemas with output parser
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain.output_parsers import PydanticOutputParser


class TourismResponse(BaseModel):
    """Complete tourism response combining weather and places"""
    place: str = Field(description="Name of the location the user is asking about")
    has_weather: bool = Field(default=False, description="Whether weather information is included in response")
    has_places: bool = Field(default=False, description="Whether places/attractions information is included in response")
    
    # Weather data (optional)
    temperature: Optional[float] = Field(default=None, description="Current temperature in Celsius. Leave null if not requested or unavailable.")
    precipitation_chance: Optional[int] = Field(default=None, description="Chance of rain in percentage (0-100). Leave null if not requested or unavailable.")
    
    # Places data (optional)
    attractions: Optional[List[str]] = Field(default=None, description="List of 3-5 tourist attraction names. Leave null if not requested or unavailable.")
    
    # Display message
    message: str = Field(description="Natural language response to show the user combining weather and/or places information")
    
    # Status
    success: bool = Field(default=True, description="Whether the request was handled successfully")
    error: Optional[str] = Field(default=None, description="Error message if the place doesn't exist or other errors occurred")


# Create output parser for LangChain agent
tourism_output_parser = PydanticOutputParser(pydantic_object=TourismResponse)
