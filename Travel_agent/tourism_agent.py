"""
Tourism Agent with LangChain Tools and Structured Output
"""
import os
import json
import requests
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain.prompts import PromptTemplate
from tools import get_weather, get_tourist_places
from schemas import TourismResponse, tourism_output_parser

load_dotenv()


class MistralLLM(LLM):
    """Custom LLM wrapper for Mistral API"""
    
    api_key: str = os.getenv("mistral_api_key", "")
    model: str = "openai/gpt-oss-20b"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    @property
    def _llm_type(self) -> str:
        return "mistral_gpt_oss"
    
    def _call(
        self,
        prompt: str,
        stop: List[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> str:
        """Call Mistral API with SSE streaming support"""
        url = "https://platform.qubrid.com/api/v1/qubridai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            # Handle SSE streaming
            if 'text/event-stream' in response.headers.get('Content-Type', ''):
                full_content = ""
                for line in response.text.split('\n'):
                    if line.startswith('data: '):
                        data_str = line[6:].strip()
                        if data_str and data_str != '[DONE]':
                            try:
                                chunk = json.loads(data_str)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    content = chunk["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        full_content += content
                            except json.JSONDecodeError:
                                continue
                return full_content if full_content else "No response generated"
            else:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                return "No response generated"
                
        except Exception as e:
            return f"Error: {str(e)}"


class TourismAgentWithTools:
    """Tourism agent that uses tools and returns structured output"""
    
    def __init__(self):
        self.llm = MistralLLM()
        self.output_parser = tourism_output_parser
        
        # Create prompt template with format instructions
        self.prompt_template = PromptTemplate(
            template="""You are a helpful Tourism AI Assistant. Help users plan their trips by providing weather and tourist attraction information.

You have access to these tools:
1. get_weather(place_name) - Gets current temperature and precipitation chance for a location
2. get_tourist_places(place_name) - Gets list of tourist attractions for a location

User Query: {query}

Instructions:
1. Identify the place name from the query
2. Determine if user wants weather info, places info, or both
3. Call the appropriate tools
4. Format your response according to the schema below

{format_instructions}

Your response:""",
            input_variables=["query"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )
    
    def extract_place_name(self, query: str) -> str:
        """Extract place name from query"""
        patterns = [
            r"(?:go(?:ing)? to|visit(?:ing)?|in|at|for)\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*\?|\s*\.|\s+let|\s+what|\s+and|$)",
            r"([A-Z][a-zA-Z\s]+?)(?:\s+let\'s|\s+what|\s+temperature|\s+weather|\s+places)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        # Fallback: find capitalized words
        words = query.split()
        for i, word in enumerate(words):
            if word and word[0].isupper() and word.lower() not in ['i', 'what', 'and', 'the', 'is', 'are']:
                place_parts = [word]
                for next_word in words[i+1:]:
                    if next_word and next_word[0].isupper():
                        place_parts.append(next_word)
                    else:
                        break
                return ' '.join(place_parts).strip()
        
        return ""
    
    def determine_intent(self, query: str) -> Dict[str, bool]:
        """Determine what information user wants"""
        query_lower = query.lower()
        
        weather_kw = ["weather", "temperature", "temp", "hot", "cold", "rain", "precipitation", "climate", "degrees"]
        places_kw = ["place", "places", "visit", "attraction", "tourist", "sightseeing", "trip", "plan", "go", "see", "explore"]
        
        needs_weather = any(kw in query_lower for kw in weather_kw)
        needs_places = any(kw in query_lower for kw in places_kw)
        
        if not needs_weather and not needs_places:
            needs_places = True
        
        return {"weather": needs_weather, "places": needs_places}
    
    def run(self, user_query: str) -> TourismResponse:
        """Process query and return structured response"""
        try:
            place_name = self.extract_place_name(user_query)
            
            if not place_name:
                return TourismResponse(
                    place="Unknown",
                    success=False,
                    message="I couldn't identify which place you're asking about. Please specify the location.",
                    error="No place name found"
                )
            
            intent = self.determine_intent(user_query)
            
            # Initialize response
            response = TourismResponse(
                place=place_name,
                has_weather=intent["weather"],
                has_places=intent["places"],
                success=True,
                message=""
            )
            
            message_parts = []
            
            # Get weather if needed
            if intent["weather"]:
                weather_result = get_weather.invoke({"place_name": place_name})
                
                if "°C" in weather_result:
                    temp_match = re.search(r'(\d+\.?\d*)°C', weather_result)
                    precip_match = re.search(r'(\d+)%', weather_result)
                    
                    if temp_match:
                        response.temperature = float(temp_match.group(1))
                    if precip_match:
                        response.precipitation_chance = int(precip_match.group(1))
                    
                    message_parts.append(weather_result)
                elif "don't know" in weather_result.lower():
                    response.success = False
                    response.error = weather_result
                    return response
            
            # Get places if needed
            if intent["places"]:
                places_result = get_tourist_places.invoke({"place_name": place_name})
                
                if "these are the places you can go" in places_result:
                    lines = places_result.split('\n')[1:]
                    response.attractions = [line.strip() for line in lines if line.strip()]
                    message_parts.append(places_result)
                elif "don't know" in places_result.lower():
                    response.success = False
                    response.error = places_result
                    return response
                elif "couldn't find" in places_result.lower():
                    response.attractions = []
                    message_parts.append(places_result)
            
            # Combine messages
            if len(message_parts) == 2:
                response.message = f"{message_parts[0]} And {message_parts[1]}"
            elif len(message_parts) == 1:
                response.message = message_parts[0]
            else:
                response.message = f"Information for {place_name}"
            
            return response
            
        except Exception as e:
            return TourismResponse(
                place=place_name if 'place_name' in locals() else "Unknown",
                success=False,
                message="I encountered an error processing your request.",
                error=str(e)
            )


def create_tourism_agent_with_tools():
    """Create tourism agent instance"""
    return TourismAgentWithTools()
