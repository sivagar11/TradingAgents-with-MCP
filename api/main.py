"""
TradingAgents FastAPI Backend
Real-time streaming API for the TradingAgents framework
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from api.services.trading_service import TradingService
from api.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AgentUpdate,
    HealthResponse,
)


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 TradingAgents API Starting...")
    yield
    # Shutdown
    print("👋 TradingAgents API Shutting down...")


app = FastAPI(
    title="TradingAgents API",
    description="Real-time streaming API for multi-agent stock analysis",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize trading service
trading_service = TradingService()


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="TradingAgents API is running",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """API health check"""
    return HealthResponse(
        status="healthy",
        message="API is operational",
        timestamp=datetime.now().isoformat(),
    )


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest):
    """
    Run a full stock analysis (non-streaming).
    For streaming, use the WebSocket endpoint.
    """
    try:
        result = await trading_service.analyze(
            ticker=request.ticker,
            date=request.date,
            analysts=request.analysts,
            config=request.config,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming analysis.
    
    Client sends: {"ticker": "NVDA", "date": "2024-11-01", "analysts": [...]}
    Server streams: {"type": "agent_update", "data": {...}}
    """
    await websocket.accept()
    
    try:
        # Receive analysis request
        data = await websocket.receive_json()
        
        ticker = data.get("ticker", "SPY")
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        analysts = data.get("analysts", ["market", "social", "news", "fundamentals"])
        config = data.get("config", {})
        
        # Send acknowledgment
        await websocket.send_json({
            "type": "status",
            "data": {
                "message": f"Starting analysis for {ticker} on {date}",
                "status": "started"
            }
        })
        
        # Run analysis with streaming updates
        async for update in trading_service.analyze_stream(
            ticker=ticker,
            date=date,
            analysts=analysts,
            config=config,
        ):
            await websocket.send_json(update)
        
        # Send completion
        await websocket.send_json({
            "type": "status",
            "data": {
                "message": "Analysis complete",
                "status": "completed"
            }
        })
        
    except WebSocketDisconnect:
        print(f"Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": {"message": str(e)}
        })
        await websocket.close()


@app.get("/api/models")
async def get_available_models():
    """Get list of available LLM models"""
    return {
        "providers": {
            "openai": {
                "quick_think": ["gpt-4o-mini", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4o"],
                "deep_think": ["gpt-4o-mini", "gpt-4o", "o4-mini", "o3-mini", "o1"],
            },
            "anthropic": {
                "quick_think": ["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest"],
                "deep_think": ["claude-3-5-sonnet-latest", "claude-sonnet-4-0"],
            },
        },
        "default": {
            "provider": "openai",
            "quick_think": "gpt-4o-mini",
            "deep_think": "o4-mini",
        }
    }


@app.get("/api/analysts")
async def get_available_analysts():
    """Get list of available analyst types"""
    return {
        "analysts": [
            {
                "id": "market",
                "name": "Market Analyst",
                "description": "Technical indicators and price analysis",
                "icon": "📈"
            },
            {
                "id": "social",
                "name": "Social Media Analyst", 
                "description": "Social sentiment and public opinion",
                "icon": "💬"
            },
            {
                "id": "news",
                "name": "News Analyst",
                "description": "Current events and macroeconomics",
                "icon": "📰"
            },
            {
                "id": "fundamentals",
                "name": "Fundamentals Analyst",
                "description": "Financial statements and company health",
                "icon": "📊"
            },
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

