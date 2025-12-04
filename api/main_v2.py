"""
TradingAgents FastAPI Backend with Timing Tracking
Real-time streaming API with performance metrics
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG


# Pydantic Models
class AnalysisRequest(BaseModel):
    ticker: str
    analysis_date: str
    analysts: List[str] = ["market", "social", "news", "fundamentals"]
    research_depth: int = 1
    llm_provider: str = "openai"
    backend_url: str = "https://api.openai.com/v1"
    shallow_thinker: str = "gpt-4o-mini"
    deep_thinker: str = "gpt-4o-mini"


class AnalysisResult(BaseModel):
    ticker: str
    analysis_date: str
    final_decision: str
    full_report: Dict[str, Any]
    agent_timings: Dict[str, float]
    total_duration: float


# Global storage for analysis results
analysis_results: Dict[str, AnalysisResult] = {}
agent_timings: Dict[str, Dict[str, float]] = {}


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 TradingAgents API Starting...")
    yield
    print("👋 TradingAgents API Shutting down...")


app = FastAPI(
    title="TradingAgents API",
    description="Real-time streaming API for multi-agent stock analysis with timing metrics",
    version="2.0.0",
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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "TradingAgents API is running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/results/{session_id}")
async def get_results(session_id: str):
    """Get full analysis results for a session"""
    if session_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis_results[session_id]


@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """WebSocket endpoint for real-time analysis streaming with timing"""
    await websocket.accept()
    session_id = f"session_{int(time.time())}"
    timings = {}
    
    try:
        # Receive analysis request
        data = await websocket.receive_text()
        request_data = json.loads(data)
        request = AnalysisRequest(**request_data)
        
        # Track total time
        analysis_start_time = time.time()
        
        # Configure TradingAgents
        config = DEFAULT_CONFIG.copy()
        config.update({
            "analysts": request.analysts,
            "max_debate_rounds": request.research_depth,
            "max_risk_discuss_rounds": request.research_depth,
            "quick_think_llm": request.shallow_thinker,
            "deep_think_llm": request.deep_thinker,
            "llm_provider": request.llm_provider,
            "backend_url": request.backend_url,
        })
        
        graph_instance = TradingAgentsGraph(
            selected_analysts=request.analysts,
            config=config,
            debug=True
        )
        
        # Agent order for tracking
        agent_order = [
            "Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst",
            "Bull Researcher", "Bear Researcher", "Research Manager",
            "Trader",
            "Risky Analyst", "Safe Analyst", "Neutral Analyst",
            "Portfolio Manager"
        ]
        
        # Send initial status
        for agent in agent_order:
            await websocket.send_json({
                "type": "status",
                "agent": agent,
                "status": "pending"
            })
        
        # Start analysis streaming
        init_agent_state = graph_instance.propagator.create_initial_state(
            request.ticker, request.analysis_date
        )
        args = graph_instance.propagator.get_graph_args()
        
        current_agent = None
        agent_start_time = None
        
        async for chunk in graph_instance.graph.astream(init_agent_state, **args):
            # Track which agent is currently active based on chunk content
            new_agent = None
            
            if "market_report" in chunk and chunk["market_report"]:
                new_agent = "Market Analyst"
                await websocket.send_json({
                    "type": "report",
                    "report_section": "market_report",
                    "content": chunk["market_report"]
                })
                
            elif "sentiment_report" in chunk and chunk["sentiment_report"]:
                new_agent = "Social Analyst"
                await websocket.send_json({
                    "type": "report",
                    "report_section": "sentiment_report",
                    "content": chunk["sentiment_report"]
                })
                
            elif "news_report" in chunk and chunk["news_report"]:
                new_agent = "News Analyst"
                await websocket.send_json({
                    "type": "report",
                    "report_section": "news_report",
                    "content": chunk["news_report"]
                })
                
            elif "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                new_agent = "Fundamentals Analyst"
                await websocket.send_json({
                    "type": "report",
                    "report_section": "fundamentals_report",
                    "content": chunk["fundamentals_report"]
                })
                
            elif "investment_plan" in chunk and chunk["investment_plan"]:
                new_agent = "Research Manager"
                await websocket.send_json({
                    "type": "report",
                    "report_section": "investment_plan",
                    "content": chunk["investment_plan"]
                })
                
            elif "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
                new_agent = "Trader"
                await websocket.send_json({
                    "type": "report",
                    "report_section": "trader_investment_plan",
                    "content": chunk["trader_investment_plan"]
                })
                
            elif "final_trade_decision" in chunk and chunk["final_trade_decision"]:
                new_agent = "Portfolio Manager"
                await websocket.send_json({
                    "type": "report",
                    "report_section": "final_trade_decision",
                    "content": chunk["final_trade_decision"]
                })
            
            # Track timing when agent changes
            if new_agent and new_agent != current_agent:
                # Complete previous agent timing
                if current_agent and agent_start_time:
                    duration = time.time() - agent_start_time
                    timings[current_agent] = duration
                    await websocket.send_json({
                        "type": "status",
                        "agent": current_agent,
                        "status": "completed",
                        "duration": f"{duration:.2f}s"
                    })
                
                # Start new agent timing
                current_agent = new_agent
                agent_start_time = time.time()
                await websocket.send_json({
                    "type": "status",
                    "agent": current_agent,
                    "status": "in_progress"
                })
        
        # Complete final agent timing
        if current_agent and agent_start_time:
            duration = time.time() - agent_start_time
            timings[current_agent] = duration
            await websocket.send_json({
                "type": "status",
                "agent": current_agent,
                "status": "completed",
                "duration": f"{duration:.2f}s"
            })
        
        # Get final decision
        final_state = await asyncio.to_thread(
            graph_instance.graph.invoke, init_agent_state, **args
        )
        decision = graph_instance.process_signal(final_state.get("final_trade_decision", "HOLD"))
        
        # Calculate total duration
        total_duration = time.time() - analysis_start_time
        
        # Send final decision with timing summary
        await websocket.send_json({
            "type": "final_decision",
            "decision": decision,
            "total_duration": f"{total_duration:.2f}s",
            "agent_timings": {k: f"{v:.2f}s" for k, v in timings.items()}
        })
        
        # Store results
        analysis_results[session_id] = AnalysisResult(
            ticker=request.ticker,
            analysis_date=request.analysis_date,
            final_decision=decision,
            full_report=final_state,
            agent_timings=timings,
            total_duration=total_duration
        )
        
        await websocket.send_json({
            "type": "complete",
            "session_id": session_id
        })
        
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

