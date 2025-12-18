"""Stock MCP Server - Exposes stock data and technical indicators via MCP.

CRITICAL: This server uses stdio transport. 
- NEVER use print() or write to stdout
- All logging must go to stderr
- stdout is reserved for MCP JSON-RPC messages
"""

import sys
import os
import logging
from pathlib import Path
from io import StringIO

# Add parent directory to Python path so we can import tradingagents
# This is needed because the MCP server runs as a separate process
server_dir = Path(__file__).parent
project_root = server_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# CRITICAL FIX: Redirect stdout to stderr BEFORE any imports
# This prevents FastMCP banner and any other stdout output from corrupting JSON-RPC
_original_stdout = sys.stdout
sys.stdout = sys.stderr

# Configure logging to stderr ONLY (never stdout for MCP stdio servers)
logging.basicConfig(
    level=logging.ERROR,  # Reduce noise
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Must be stderr, not stdout!
)
logger = logging.getLogger(__name__)

# Use FastMCP for simpler, more reliable server
from fastmcp import FastMCP

# Import existing data vendor functions
# WARNING: route_to_vendor prints to stdout by default!
# We need to suppress that
from tradingagents.dataflows.interface import route_to_vendor

# Create FastMCP server instance (banner will go to stderr now)
mcp = FastMCP("Stock Data Server")


def suppress_stdout(func):
    """Decorator to suppress stdout during function execution.
    
    This is CRITICAL for MCP stdio servers - any stdout output
    will corrupt the JSON-RPC communication.
    """
    def wrapper(*args, **kwargs):
        # Redirect stdout to nowhere
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Restore stdout
            sys.stdout = old_stdout
    return wrapper


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
    logger.info(f"MCP Tool: get_stock_data({symbol}, {curr_date}, {look_back_days})")
    
    # Suppress stdout to prevent corruption of MCP communication
    @suppress_stdout
    def call_vendor():
        return route_to_vendor(
            "get_stock_data",
            symbol,
            curr_date,
            look_back_days
        )
    
    result = call_vendor()
    logger.info(f"MCP Tool: get_stock_data completed")
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
    logger.info(f"MCP Tool: get_indicators({symbol}, {indicator}, {curr_date})")
    
    # Suppress stdout to prevent corruption of MCP communication
    @suppress_stdout
    def call_vendor():
        return route_to_vendor(
            "get_indicators",
            symbol,
            indicator,
            curr_date,
            look_back_days
        )
    
    result = call_vendor()
    logger.info(f"MCP Tool: get_indicators completed")
    return result


def create_stock_server():
    """Create and return the stock MCP server."""
    return mcp


if __name__ == "__main__":
    # Restore stdout for MCP JSON-RPC communication
    # (we redirected it earlier to suppress the banner)
    sys.stdout = _original_stdout
    
    # Run the FastMCP server with stdio transport
    logger.info("Starting Stock MCP Server...")
    mcp.run(transport="stdio")

