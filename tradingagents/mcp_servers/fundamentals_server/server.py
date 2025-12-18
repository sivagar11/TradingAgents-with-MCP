"""Fundamentals MCP Server - Exposes fundamental data tools via MCP.

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

# CRITICAL: Redirect stdout to stderr BEFORE any imports
# This prevents ANY output from corrupting MCP JSON-RPC messages
_original_stdout = sys.stdout
sys.stdout = sys.stderr

# Add parent directory to Python path so we can import tradingagents
# This is needed because the MCP server runs as a separate process
server_dir = Path(__file__).parent
project_root = server_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

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
mcp = FastMCP("Fundamentals Data Server")


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
def get_fundamentals(
    ticker: str,
    curr_date: str
) -> str:
    """
    Get comprehensive fundamental data for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)
        curr_date: Current date in YYYY-MM-DD format
    
    Returns:
        Comprehensive fundamental analysis including key metrics and ratios
    """
    logger.info(f"MCP Tool: get_fundamentals({ticker}, {curr_date})")
    
    # Suppress stdout to prevent corruption of MCP communication
    @suppress_stdout
    def call_vendor():
        return route_to_vendor(
            "get_fundamentals",
            ticker,
            curr_date
        )
    
    result = call_vendor()
    logger.info(f"MCP Tool: get_fundamentals completed")
    return result


@mcp.tool()
def get_balance_sheet(
    ticker: str,
    freq: str = "quarterly",
    curr_date: str = None
) -> str:
    """
    Get balance sheet data for a stock.
    
    Args:
        ticker: Stock ticker symbol
        freq: Reporting frequency ("annual" or "quarterly")
        curr_date: Current date in YYYY-MM-DD format (optional)
    
    Returns:
        Balance sheet data and analysis
    """
    logger.info(f"MCP Tool: get_balance_sheet({ticker}, {freq}, {curr_date})")
    
    # Suppress stdout to prevent corruption of MCP communication
    @suppress_stdout
    def call_vendor():
        return route_to_vendor(
            "get_balance_sheet",
            ticker,
            freq,
            curr_date
        )
    
    result = call_vendor()
    logger.info(f"MCP Tool: get_balance_sheet completed")
    return result


@mcp.tool()
def get_cashflow(
    ticker: str,
    freq: str = "quarterly",
    curr_date: str = None
) -> str:
    """
    Get cash flow statement data for a stock.
    
    Args:
        ticker: Stock ticker symbol
        freq: Reporting frequency ("annual" or "quarterly")
        curr_date: Current date in YYYY-MM-DD format (optional)
    
    Returns:
        Cash flow statement data and analysis
    """
    logger.info(f"MCP Tool: get_cashflow({ticker}, {freq}, {curr_date})")
    
    # Suppress stdout to prevent corruption of MCP communication
    @suppress_stdout
    def call_vendor():
        return route_to_vendor(
            "get_cashflow",
            ticker,
            freq,
            curr_date
        )
    
    result = call_vendor()
    logger.info(f"MCP Tool: get_cashflow completed")
    return result


@mcp.tool()
def get_income_statement(
    ticker: str,
    freq: str = "quarterly",
    curr_date: str = None
) -> str:
    """
    Get income statement data for a stock.
    
    Args:
        ticker: Stock ticker symbol
        freq: Reporting frequency ("annual" or "quarterly")
        curr_date: Current date in YYYY-MM-DD format (optional)
    
    Returns:
        Income statement data and analysis
    """
    logger.info(f"MCP Tool: get_income_statement({ticker}, {freq}, {curr_date})")
    
    # Suppress stdout to prevent corruption of MCP communication
    @suppress_stdout
    def call_vendor():
        return route_to_vendor(
            "get_income_statement",
            ticker,
            freq,
            curr_date
        )
    
    result = call_vendor()
    logger.info(f"MCP Tool: get_income_statement completed")
    return result


if __name__ == "__main__":
    # Restore stdout for MCP JSON-RPC communication
    # (we redirected it earlier to suppress the banner)
    sys.stdout = _original_stdout
    
    # Run the FastMCP server with stdio transport
    logger.info("Starting Fundamentals MCP Server...")
    mcp.run(transport="stdio")

