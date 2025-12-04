"""
Pydantic models for API request/response schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AnalystType(str, Enum):
    MARKET = "market"
    SOCIAL = "social"
    NEWS = "news"
    FUNDAMENTALS = "fundamentals"


class AgentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


class AnalysisConfig(BaseModel):
    """Configuration for analysis"""
    llm_provider: str = "openai"
    quick_think_llm: str = "gpt-4o-mini"
    deep_think_llm: str = "gpt-4o-mini"
    max_debate_rounds: int = 1
    max_risk_discuss_rounds: int = 1


class AnalysisRequest(BaseModel):
    """Request model for stock analysis"""
    ticker: str = Field(..., description="Stock ticker symbol", example="NVDA")
    date: str = Field(..., description="Analysis date in YYYY-MM-DD format", example="2024-11-01")
    analysts: List[str] = Field(
        default=["market", "social", "news", "fundamentals"],
        description="List of analyst types to use"
    )
    config: Optional[AnalysisConfig] = None


class AgentUpdate(BaseModel):
    """Real-time update from an agent"""
    agent_name: str
    status: AgentStatus
    message: Optional[str] = None
    report: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class DebateUpdate(BaseModel):
    """Update from debate between researchers"""
    speaker: str  # "bull", "bear", "judge"
    content: str
    round: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class RiskDebateUpdate(BaseModel):
    """Update from risk management debate"""
    speaker: str  # "risky", "safe", "neutral", "judge"
    content: str
    round: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class FinalDecision(BaseModel):
    """Final trading decision"""
    action: str  # "BUY", "SELL", "HOLD"
    confidence: Optional[float] = None
    reasoning: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    ticker: str
    date: str
    
    # Reports from analysts
    market_report: Optional[str] = None
    sentiment_report: Optional[str] = None
    news_report: Optional[str] = None
    fundamentals_report: Optional[str] = None
    
    # Investment debate
    investment_debate: Optional[Dict[str, Any]] = None
    investment_plan: Optional[str] = None
    
    # Trader decision
    trader_plan: Optional[str] = None
    
    # Risk debate
    risk_debate: Optional[Dict[str, Any]] = None
    
    # Final decision
    final_decision: str
    decision_action: str  # "BUY", "SELL", "HOLD"
    
    # Metadata
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    duration_seconds: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    timestamp: str


class StreamMessage(BaseModel):
    """Generic streaming message wrapper"""
    type: str  # "agent_update", "debate_update", "risk_update", "decision", "error", "status"
    data: Dict[str, Any]

