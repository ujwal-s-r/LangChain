"""
FastAPI Backend for Tourism AI Agent
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from agent import run_agent

# Create FastAPI app
app = FastAPI(
    title="Tourism AI Agent API",
    description="Multi-agent tourism system with weather and places information",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I'm going to go to Bangalore, let's plan my trip."
            }
        }


class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None


# Routes
@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("templates/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Tourism AI Agent",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for the tourism agent
    
    Args:
        request: ChatRequest containing user message
        
    Returns:
        ChatResponse with agent's response
    """
    try:
        if not request.message or request.message.strip() == "":
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Run the agent with user input
        response = run_agent(request.message)
        
        return ChatResponse(
            response=response,
            success=True,
            error=None
        )
        
    except Exception as e:
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request.",
            success=False,
            error=str(e)
        )


@app.get("/api/info")
async def get_info():
    """Get information about available capabilities"""
    return {
        "capabilities": [
            "Weather information for any location",
            "Tourist attractions and places to visit",
            "Combined trip planning with weather and places"
        ],
        "example_queries": [
            "I'm going to go to Bangalore, let's plan my trip.",
            "What is the temperature in Paris?",
            "Tell me about the weather and places to visit in Tokyo."
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
