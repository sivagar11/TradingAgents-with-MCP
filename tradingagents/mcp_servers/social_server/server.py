"""Social MCP Server - Exposes social media and news tools via MCP.

Note: Social analyst uses the same tools as news analyst (get_news, etc.)
This is a separate server for organizational purposes.

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
mcp = FastMCP("Social Media Data Server")


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
def get_news(
    ticker: str,
    start_date: str,
    end_date: str
) -> str:
    """
    Get news articles for a specific stock ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, NVDA, TSLA)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        News articles and social media sentiment for the given ticker
    """
    logger.info(f"MCP Tool: get_news({ticker}, {start_date}, {end_date})")
    
    # Suppress stdout to prevent corruption of MCP communication
    @suppress_stdout
    def call_vendor():
        return route_to_vendor(
            "get_news",
            ticker,
            start_date,
            end_date
        )
    
    result = call_vendor()
    logger.info(f"MCP Tool: get_news completed")
    return result


if __name__ == "__main__":
    # Restore stdout for MCP JSON-RPC communication
    # (we redirected it earlier to suppress the banner)
    sys.stdout = _original_stdout
    
    # Run the FastMCP server with stdio transport
    logger.info("Starting Social Media MCP Server...")
    mcp.run(transport="stdio")

