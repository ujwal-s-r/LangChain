"""
Tourism AI Agent - Main agent configuration using Mistral API with GPT-OSS-20B model
"""
import os
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from tools import get_weather, get_tourist_places

# Load environment variables
load_dotenv()


class MistralGPTOSS(LLM):
    """Custom LLM wrapper for Mistral API with openai/gpt-oss-20b model"""
    
    api_key: str = os.getenv("mistral_api_key", "")
    model: str = "openai/gpt-oss-20b"
    temperature: float = 0.7
    max_tokens: int = 500
    
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
        """Call the Mistral API with GPT-OSS-20B model and handle SSE streaming"""
        url = "https://platform.qubrid.com/api/v1/qubridai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            # Handle SSE streaming response (API always streams)
            if 'text/event-stream' in response.headers.get('Content-Type', ''):
                full_content = ""
                lines = response.text.split('\n')
                
                for line in lines:
                    if line.startswith('data: '):
                        data_str = line[6:].strip()
                        if data_str and data_str != '[DONE]':
                            try:
                                chunk = json.loads(data_str)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_content += content
                            except json.JSONDecodeError:
                                continue
                
                return full_content if full_content else "I apologize, but I couldn't generate a response."
            else:
                # Handle regular JSON response (if ever supported)
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return "I apologize, but I couldn't generate a response."
                
        except requests.exceptions.RequestException as e:
            return f"Error connecting to AI service: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


# Create the agent prompt template
TOURISM_AGENT_PROMPT = """You are a helpful Tourism AI Assistant. Your job is to help users plan their trips by providing weather information and tourist attractions.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT GUIDELINES:
1. When a user asks about weather, use the get_weather tool
2. When a user asks about places to visit or tourist attractions, use the get_tourist_places tool
3. If asked about both weather AND places, use BOTH tools
4. Always provide natural, friendly responses
5. If a place doesn't exist, politely inform the user
6. Format your final answers in a clear, easy-to-read way

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


def create_tourism_agent():
    """Create and return the tourism agent executor"""
    
    # Initialize the LLM
    llm = MistralGPTOSS()
    
    # Define tools
    tools = [get_weather, get_tourist_places]
    
    # Create prompt
    prompt = PromptTemplate.from_template(TOURISM_AGENT_PROMPT)
    
    # Create agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent_executor


def run_agent(user_input: str) -> str:
    """Run the agent with user input and return the response"""
    try:
        agent_executor = create_tourism_agent()
        result = agent_executor.invoke({"input": user_input})
        return result.get("output", "I couldn't process your request.")
    except Exception as e:
        return f"Error processing request: {str(e)}"
