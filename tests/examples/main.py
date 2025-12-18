#!/usr/bin/env python3
"""
Example: Basic Usage of TradingAgents

This script demonstrates how to use the TradingAgents framework
with custom configuration.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

# Load environment variables from project root
env_path = project_root / '.env'
load_dotenv(env_path)


async def main():
    """Main async function to run the trading analysis."""
    
    # Create a custom config
    config = DEFAULT_CONFIG.copy()
    config["deep_think_llm"] = "gpt-4o-mini"  # Use a different model
    config["quick_think_llm"] = "gpt-4o-mini"  # Use a different model
    config["max_debate_rounds"] = 0  # Skip debate rounds for faster demo
    config["max_risk_discuss_rounds"] = 0  # Skip risk debate for faster demo

    # Configure data vendors (default uses yfinance and alpha_vantage)
    config["data_vendors"] = {
        "core_stock_apis": "yfinance",           # Options: yfinance, alpha_vantage, local
        "technical_indicators": "yfinance",      # Options: yfinance, alpha_vantage, local
        "fundamental_data": "alpha_vantage",     # Options: openai, alpha_vantage, local
        "news_data": "alpha_vantage",            # Options: openai, alpha_vantage, google, local
    }

    # Initialize with custom config (async for MCP support)
    ta = await TradingAgentsGraph.create(debug=True, config=config)

    try:
        # Forward propagate (now async)
        _, decision = await ta.propagate("NVDA", "2024-05-10")
        print(decision)

        # Memorize mistakes and reflect (if needed)
        # ta.reflect_and_remember(1000)  # parameter is the position returns
    
    finally:
        # Clean up MCP connections if any
        await ta.close()


if __name__ == "__main__":
    asyncio.run(main())
