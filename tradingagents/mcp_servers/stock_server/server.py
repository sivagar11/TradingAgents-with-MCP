"""Stock MCP Server - Exposes stock data and technical indicators via MCP."""

import sys
import os
from pathlib import Path

# Add parent directory to Python path so we can import tradingagents
# This is needed because the MCP server runs as a separate process
server_dir = Path(__file__).parent
project_root = server_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# Use FastMCP for simpler, more reliable server
from fastmcp import FastMCP

# Import existing data vendor functions
from tradingagents.dataflows.interface import route_to_vendor

# Create FastMCP server instance
mcp = FastMCP("Stock Data Server")


@mcp.tool()
def get_stock_data(
    symbol: str,
    curr_date: str,
    look_back_days: int = 30
) -> str:
    """
    Get historical stock price data for a given ticker symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)
        curr_date: Current trading date in YYYY-MM-DD format
        look_back_days: Number of days to look back for historical data
    
    Returns:
        Historical OHLCV (Open, High, Low, Close, Volume) data
    """
    # Call existing vendor routing system
    result = route_to_vendor(
        "get_stock_data",
        symbol,
        curr_date,
        look_back_days
    )
    return result


@mcp.tool()
def get_indicators(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int = 30
) -> str:
    """
    Get technical indicators for stock analysis.
    
    Args:
        symbol: Stock ticker symbol
        indicator: Technical indicator name (rsi, macd, boll, sma, ema, volume)
        curr_date: Current trading date in YYYY-MM-DD format
        look_back_days: Number of days to look back
    
    Returns:
        Technical indicator analysis and data
    """
    # Call existing vendor routing system
    result = route_to_vendor(
        "get_indicators",
        symbol,
        indicator,
        curr_date,
        look_back_days
    )
    return result


def create_stock_server():
    """Create and return the stock MCP server."""
    return mcp


if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()

