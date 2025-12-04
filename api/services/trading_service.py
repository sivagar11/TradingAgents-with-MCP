"""
Trading Service - Wraps TradingAgentsGraph with streaming support
"""

import os
import sys
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List, AsyncGenerator, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.agent_states import InvestDebateState, RiskDebateState

from api.models.schemas import (
    AnalysisConfig,
    AnalysisResponse,
    AgentUpdate,
    AgentStatus,
)


class TradingService:
    """Service for running TradingAgents analysis with streaming support"""
    
    def __init__(self):
        self.analysis_history: List[Dict] = []
    
    def _create_config(self, config: Optional[AnalysisConfig] = None) -> Dict:
        """Create configuration from request or defaults"""
        base_config = DEFAULT_CONFIG.copy()
        
        if config:
            base_config["llm_provider"] = config.llm_provider
            base_config["quick_think_llm"] = config.quick_think_llm
            base_config["deep_think_llm"] = config.deep_think_llm
            base_config["max_debate_rounds"] = config.max_debate_rounds
            base_config["max_risk_discuss_rounds"] = config.max_risk_discuss_rounds
        else:
            # Use cheaper defaults for testing
            base_config["quick_think_llm"] = "gpt-4o-mini"
            base_config["deep_think_llm"] = "gpt-4o-mini"
            base_config["max_debate_rounds"] = 1
            base_config["max_risk_discuss_rounds"] = 1
        
        return base_config
    
    async def analyze(
        self,
        ticker: str,
        date: str,
        analysts: List[str],
        config: Optional[AnalysisConfig] = None,
    ) -> AnalysisResponse:
        """Run analysis synchronously and return complete result"""
        
        start_time = time.time()
        graph_config = self._create_config(config)
        
        # Initialize graph
        ta = TradingAgentsGraph(
            selected_analysts=analysts,
            debug=False,
            config=graph_config,
        )
        
        # Run analysis
        final_state, decision = ta.propagate(ticker, date)
        
        duration = time.time() - start_time
        
        # Build response
        response = AnalysisResponse(
            ticker=ticker,
            date=date,
            market_report=final_state.get("market_report"),
            sentiment_report=final_state.get("sentiment_report"),
            news_report=final_state.get("news_report"),
            fundamentals_report=final_state.get("fundamentals_report"),
            investment_debate=final_state.get("investment_debate_state"),
            investment_plan=final_state.get("investment_plan"),
            trader_plan=final_state.get("trader_investment_plan"),
            risk_debate=final_state.get("risk_debate_state"),
            final_decision=final_state.get("final_trade_decision", ""),
            decision_action=decision,
            duration_seconds=duration,
        )
        
        # Save to history
        self.analysis_history.append({
            "ticker": ticker,
            "date": date,
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
        })
        
        return response
    
    async def analyze_stream(
        self,
        ticker: str,
        date: str,
        analysts: List[str],
        config: Optional[Dict] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run analysis with streaming updates.
        Yields updates as agents complete their work.
        """
        
        start_time = time.time()
        
        # Build config
        graph_config = self._create_config(
            AnalysisConfig(**config) if config else None
        )
        
        # Map analyst IDs to display names
        analyst_names = {
            "market": "Market Analyst",
            "social": "Social Analyst",
            "news": "News Analyst",
            "fundamentals": "Fundamentals Analyst",
        }
        
        # Initialize all agents as pending
        all_agents = [
            # Analyst Team
            *[analyst_names.get(a, a) for a in analysts],
            # Research Team
            "Bull Researcher",
            "Bear Researcher", 
            "Research Manager",
            # Trading Team
            "Trader",
            # Risk Team
            "Risky Analyst",
            "Safe Analyst",
            "Neutral Analyst",
            # Final
            "Portfolio Manager",
        ]
        
        # Send initial agent list
        yield {
            "type": "init",
            "data": {
                "agents": all_agents,
                "ticker": ticker,
                "date": date,
            }
        }
        
        # Small delay for UI to initialize
        await asyncio.sleep(0.1)
        
        # Initialize graph
        try:
            ta = TradingAgentsGraph(
                selected_analysts=analysts,
                debug=True,
                config=graph_config,
            )
        except Exception as e:
            yield {
                "type": "error",
                "data": {"message": f"Failed to initialize: {str(e)}"}
            }
            return
        
        # Create initial state
        init_agent_state = ta.propagator.create_initial_state(ticker, date)
        args = ta.propagator.get_graph_args()
        
        # Track which agents have completed
        completed_agents = set()
        current_agent = None
        
        # Stream through the graph
        try:
            for chunk in ta.graph.stream(init_agent_state, **args):
                if len(chunk.get("messages", [])) == 0:
                    continue
                
                # Determine current agent from chunk content
                # Market Analyst
                if "market_report" in chunk and chunk["market_report"] and "Market Analyst" not in completed_agents:
                    yield {
                        "type": "agent_update",
                        "data": {
                            "agent": "Market Analyst",
                            "status": "completed",
                            "report": chunk["market_report"],
                        }
                    }
                    completed_agents.add("Market Analyst")
                    
                    # Signal next agent starting
                    if "social" in analysts:
                        yield {"type": "agent_update", "data": {"agent": "Social Analyst", "status": "in_progress"}}
                
                # Social Analyst
                if "sentiment_report" in chunk and chunk["sentiment_report"] and "Social Analyst" not in completed_agents:
                    yield {
                        "type": "agent_update",
                        "data": {
                            "agent": "Social Analyst",
                            "status": "completed",
                            "report": chunk["sentiment_report"],
                        }
                    }
                    completed_agents.add("Social Analyst")
                    
                    if "news" in analysts:
                        yield {"type": "agent_update", "data": {"agent": "News Analyst", "status": "in_progress"}}
                
                # News Analyst
                if "news_report" in chunk and chunk["news_report"] and "News Analyst" not in completed_agents:
                    yield {
                        "type": "agent_update",
                        "data": {
                            "agent": "News Analyst",
                            "status": "completed",
                            "report": chunk["news_report"],
                        }
                    }
                    completed_agents.add("News Analyst")
                    
                    if "fundamentals" in analysts:
                        yield {"type": "agent_update", "data": {"agent": "Fundamentals Analyst", "status": "in_progress"}}
                
                # Fundamentals Analyst
                if "fundamentals_report" in chunk and chunk["fundamentals_report"] and "Fundamentals Analyst" not in completed_agents:
                    yield {
                        "type": "agent_update",
                        "data": {
                            "agent": "Fundamentals Analyst",
                            "status": "completed",
                            "report": chunk["fundamentals_report"],
                        }
                    }
                    completed_agents.add("Fundamentals Analyst")
                    
                    # Research team starts
                    yield {"type": "agent_update", "data": {"agent": "Bull Researcher", "status": "in_progress"}}
                    yield {"type": "agent_update", "data": {"agent": "Bear Researcher", "status": "in_progress"}}
                
                # Investment Debate
                if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
                    debate_state = chunk["investment_debate_state"]
                    
                    # Bull history update
                    if debate_state.get("bull_history") and "Bull Researcher" not in completed_agents:
                        yield {
                            "type": "debate_update",
                            "data": {
                                "speaker": "bull",
                                "content": debate_state["bull_history"].split("\n")[-1] if debate_state["bull_history"] else "",
                                "debate_type": "investment",
                            }
                        }
                    
                    # Bear history update
                    if debate_state.get("bear_history") and "Bear Researcher" not in completed_agents:
                        yield {
                            "type": "debate_update",
                            "data": {
                                "speaker": "bear",
                                "content": debate_state["bear_history"].split("\n")[-1] if debate_state["bear_history"] else "",
                                "debate_type": "investment",
                            }
                        }
                    
                    # Judge decision
                    if debate_state.get("judge_decision"):
                        completed_agents.add("Bull Researcher")
                        completed_agents.add("Bear Researcher")
                        completed_agents.add("Research Manager")
                        
                        yield {
                            "type": "agent_update",
                            "data": {
                                "agent": "Bull Researcher",
                                "status": "completed",
                            }
                        }
                        yield {
                            "type": "agent_update",
                            "data": {
                                "agent": "Bear Researcher", 
                                "status": "completed",
                            }
                        }
                        yield {
                            "type": "agent_update",
                            "data": {
                                "agent": "Research Manager",
                                "status": "completed",
                                "report": debate_state["judge_decision"],
                            }
                        }
                        yield {"type": "agent_update", "data": {"agent": "Trader", "status": "in_progress"}}
                
                # Trader
                if "trader_investment_plan" in chunk and chunk["trader_investment_plan"] and "Trader" not in completed_agents:
                    yield {
                        "type": "agent_update",
                        "data": {
                            "agent": "Trader",
                            "status": "completed",
                            "report": chunk["trader_investment_plan"],
                        }
                    }
                    completed_agents.add("Trader")
                    
                    # Risk team starts
                    yield {"type": "agent_update", "data": {"agent": "Risky Analyst", "status": "in_progress"}}
                
                # Risk Debate
                if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                    risk_state = chunk["risk_debate_state"]
                    
                    # Risky analyst
                    if risk_state.get("current_risky_response"):
                        yield {
                            "type": "debate_update",
                            "data": {
                                "speaker": "risky",
                                "content": risk_state["current_risky_response"],
                                "debate_type": "risk",
                            }
                        }
                        if "Risky Analyst" not in completed_agents:
                            yield {"type": "agent_update", "data": {"agent": "Safe Analyst", "status": "in_progress"}}
                    
                    # Safe analyst
                    if risk_state.get("current_safe_response"):
                        yield {
                            "type": "debate_update",
                            "data": {
                                "speaker": "safe",
                                "content": risk_state["current_safe_response"],
                                "debate_type": "risk",
                            }
                        }
                        if "Safe Analyst" not in completed_agents:
                            yield {"type": "agent_update", "data": {"agent": "Neutral Analyst", "status": "in_progress"}}
                    
                    # Neutral analyst
                    if risk_state.get("current_neutral_response"):
                        yield {
                            "type": "debate_update",
                            "data": {
                                "speaker": "neutral",
                                "content": risk_state["current_neutral_response"],
                                "debate_type": "risk",
                            }
                        }
                    
                    # Final judge decision
                    if risk_state.get("judge_decision"):
                        completed_agents.update(["Risky Analyst", "Safe Analyst", "Neutral Analyst", "Portfolio Manager"])
                        
                        yield {"type": "agent_update", "data": {"agent": "Risky Analyst", "status": "completed"}}
                        yield {"type": "agent_update", "data": {"agent": "Safe Analyst", "status": "completed"}}
                        yield {"type": "agent_update", "data": {"agent": "Neutral Analyst", "status": "completed"}}
                        yield {
                            "type": "agent_update",
                            "data": {
                                "agent": "Portfolio Manager",
                                "status": "completed",
                                "report": risk_state["judge_decision"],
                            }
                        }
                
                # Final decision
                if "final_trade_decision" in chunk and chunk["final_trade_decision"]:
                    # Extract decision (BUY/SELL/HOLD)
                    decision_text = chunk["final_trade_decision"]
                    decision_action = ta.process_signal(decision_text)
                    
                    yield {
                        "type": "decision",
                        "data": {
                            "action": decision_action,
                            "reasoning": decision_text,
                            "ticker": ticker,
                            "date": date,
                        }
                    }
            
            # Send completion with timing
            duration = time.time() - start_time
            yield {
                "type": "complete",
                "data": {
                    "duration_seconds": round(duration, 2),
                    "ticker": ticker,
                    "date": date,
                }
            }
            
            # Save to history
            self.analysis_history.append({
                "ticker": ticker,
                "date": date,
                "timestamp": datetime.now().isoformat(),
            })
            
        except Exception as e:
            yield {
                "type": "error",
                "data": {"message": str(e)}
            }
    
    def get_history(self) -> List[Dict]:
        """Get analysis history"""
        return self.analysis_history

