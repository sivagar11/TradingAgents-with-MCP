# TradingAgents/graph/trading_graph.py

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.dataflows.config import set_config

# Import the new abstract tool methods from agent_utils
from tradingagents.agents.utils.agent_utils import (
    get_stock_data,
    get_indicators,
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
    get_news,
    get_insider_sentiment,
    get_insider_transactions,
    get_global_news
)

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor

# MCP imports (optional, only used if use_mcp=True)
try:
    from tradingagents.mcp_client import MCPClient, MCPToolExecutor
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP: Libraries not available. Install with: pip install mcp fastmcp")


class TradingAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """Initialize the trading agents graph and components.
        
        NOTE: This is the synchronous constructor. For MCP support, use the async
        factory method `create()` instead:
            graph = await TradingAgentsGraph.create(...)

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
        """
        self.selected_analysts = selected_analysts
        self.debug = debug
        self.config = config or DEFAULT_CONFIG
        
        # MCP will be initialized asynchronously if needed
        self.mcp_client = None
        self.use_mcp = self.config.get("use_mcp", False)
        
        # These will be set by _initialize_sync() or async create()
        self.deep_thinking_llm = None
        self.quick_thinking_llm = None
        self.tool_nodes = None
        self.graph = None
        
        # If MCP is enabled, user must use create() factory method
        if self.use_mcp:
            raise RuntimeError(
                "Cannot use MCP with synchronous __init__. "
                "Use async factory method instead:\n"
                "    graph = await TradingAgentsGraph.create(..., config={'use_mcp': True})"
            )
        
        # For non-MCP mode, initialize synchronously
        self._initialize_sync()
    
    def _initialize_sync(self):
        """Synchronous initialization (non-MCP mode)."""
        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # Initialize LLMs
        if self.config["llm_provider"].lower() == "openai" or self.config["llm_provider"] == "ollama" or self.config["llm_provider"] == "openrouter":
            self.deep_thinking_llm = ChatOpenAI(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatOpenAI(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "anthropic":
            self.deep_thinking_llm = ChatAnthropic(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatAnthropic(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "google":
            self.deep_thinking_llm = ChatGoogleGenerativeAI(model=self.config["deep_think_llm"])
            self.quick_thinking_llm = ChatGoogleGenerativeAI(model=self.config["quick_think_llm"])
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config['llm_provider']}")
        
        # Initialize memories
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)

        # Create tool nodes (direct mode only)
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict

        # Set up the graph
        self.graph = self.graph_setup.setup_graph(self.selected_analysts)
    
    @classmethod
    async def create(
        cls,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """Async factory method to create TradingAgentsGraph with MCP support.
        
        Use this instead of __init__ when MCP is enabled:
            graph = await TradingAgentsGraph.create(
                selected_analysts=["market"],
                config={"use_mcp": True, ...}
            )
        
        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
            
        Returns:
            Fully initialized TradingAgentsGraph instance
        """
        # Create instance without full initialization
        instance = cls.__new__(cls)
        instance.selected_analysts = selected_analysts
        instance.debug = debug
        instance.config = config or DEFAULT_CONFIG
        instance.use_mcp = instance.config.get("use_mcp", False)
        instance.mcp_client = None
        
        # Update the interface's config
        set_config(instance.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(instance.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # Initialize LLMs
        if instance.config["llm_provider"].lower() == "openai" or instance.config["llm_provider"] == "ollama" or instance.config["llm_provider"] == "openrouter":
            instance.deep_thinking_llm = ChatOpenAI(model=instance.config["deep_think_llm"], base_url=instance.config["backend_url"])
            instance.quick_thinking_llm = ChatOpenAI(model=instance.config["quick_think_llm"], base_url=instance.config["backend_url"])
        elif instance.config["llm_provider"].lower() == "anthropic":
            instance.deep_thinking_llm = ChatAnthropic(model=instance.config["deep_think_llm"], base_url=instance.config["backend_url"])
            instance.quick_thinking_llm = ChatAnthropic(model=instance.config["quick_think_llm"], base_url=instance.config["backend_url"])
        elif instance.config["llm_provider"].lower() == "google":
            instance.deep_thinking_llm = ChatGoogleGenerativeAI(model=instance.config["deep_think_llm"])
            instance.quick_thinking_llm = ChatGoogleGenerativeAI(model=instance.config["quick_think_llm"])
        else:
            raise ValueError(f"Unsupported LLM provider: {instance.config['llm_provider']}")
        
        # Initialize memories
        instance.bull_memory = FinancialSituationMemory("bull_memory", instance.config)
        instance.bear_memory = FinancialSituationMemory("bear_memory", instance.config)
        instance.trader_memory = FinancialSituationMemory("trader_memory", instance.config)
        instance.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", instance.config)
        instance.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", instance.config)

        # Initialize MCP if enabled (ASYNC)
        if instance.use_mcp:
            if not MCP_AVAILABLE:
                raise RuntimeError("MCP is enabled but required libraries are not installed. Run: pip install mcp fastmcp")
            print("MCP: Initializing MCP client (async)...")
            instance.mcp_client = await instance._initialize_mcp_async()
            print("MCP: Client initialized successfully")

        # Create tool nodes (MCP or direct, based on config)
        instance.tool_nodes = instance._create_tool_nodes()

        # Initialize components
        instance.conditional_logic = ConditionalLogic()
        instance.graph_setup = GraphSetup(
            instance.quick_thinking_llm,
            instance.deep_thinking_llm,
            instance.tool_nodes,
            instance.bull_memory,
            instance.bear_memory,
            instance.trader_memory,
            instance.invest_judge_memory,
            instance.risk_manager_memory,
            instance.conditional_logic,
        )

        instance.propagator = Propagator()
        instance.reflector = Reflector(instance.quick_thinking_llm)
        instance.signal_processor = SignalProcessor(instance.quick_thinking_llm)

        # State tracking
        instance.curr_state = None
        instance.ticker = None
        instance.log_states_dict = {}  # date to full state dict

        # Set up the graph
        instance.graph = instance.graph_setup.setup_graph(instance.selected_analysts)
        
        return instance

    async def _initialize_mcp_async(self) -> MCPClient:
        """Initialize MCP client and connect to servers (ASYNC).
        
        This must be called from an async context to properly manage
        the MCP client connections and event loops.
        
        Returns:
            Initialized MCPClient with active server connections
        """
        # Create MCP client
        client = MCPClient()
        
        # Register servers from config
        for server_name, server_config in self.config.get("mcp_servers", {}).items():
            client.register_server(
                server_name,
                server_config["command"],
                server_config.get("args", [])
            )
        
        # Connect to all servers (ASYNC - no asyncio.run wrapper!)
        await client.connect_all()
        
        return client
    
    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources using abstract methods or MCP."""
        
        if self.use_mcp and self.mcp_client:
            # MCP MODE: Create MCP tool executors
            print("MCP: Creating MCP-powered tool nodes")
            tool_mapping = self.config.get("mcp_tool_mapping", {})
            
            return {
                "market": MCPToolExecutor(self.mcp_client, tool_mapping),
                "social": MCPToolExecutor(self.mcp_client, tool_mapping),
                "news": MCPToolExecutor(self.mcp_client, tool_mapping),
                "fundamentals": MCPToolExecutor(self.mcp_client, tool_mapping),
            }
        else:
            # DIRECT MODE: Use traditional ToolNodes (original system)
            print("DIRECT: Using traditional tool nodes (non-MCP)")
            return {
                "market": ToolNode(
                    [
                        # Core stock data tools
                        get_stock_data,
                        # Technical indicators
                        get_indicators,
                    ]
                ),
                "social": ToolNode(
                    [
                        # News tools for social media analysis
                        get_news,
                    ]
                ),
                "news": ToolNode(
                    [
                        # News and insider information
                        get_news,
                        get_global_news,
                        get_insider_sentiment,
                        get_insider_transactions,
                    ]
                ),
                "fundamentals": ToolNode(
                    [
                        # Fundamental analysis tools
                        get_fundamentals,
                        get_balance_sheet,
                        get_cashflow,
                        get_income_statement,
                    ]
                ),
            }

    def propagate(self, company_name, trade_date):
        """Run the trading agents graph for a company on a specific date."""

        self.ticker = company_name

        # Initialize state
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        args = self.propagator.get_graph_args()

        if self.debug:
            # Debug mode with tracing
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            final_state = trace[-1]
        else:
            # Standard mode without tracing
            final_state = self.graph.invoke(init_agent_state, **args)

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        self._log_state(trade_date, final_state)

        # Return decision and processed signal
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log_{trade_date}.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """Reflect on decisions and update memory based on returns."""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal)
