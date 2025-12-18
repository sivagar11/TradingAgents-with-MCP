"""Stock MCP Server - Exposes stock data and technical indicators via MCP."""

import sys
import json
from typing import Annotated
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import existing data vendor functions
from tradingagents.dataflows.interface import route_to_vendor

# Create MCP server instance
app = Server("mcp-server-stock")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_stock_data",
            description="Get historical stock price data for a given ticker symbol. Returns OHLCV (Open, High, Low, Close, Volume) data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, NVDA, TSLA)"
                    },
                    "curr_date": {
                        "type": "string",
                        "description": "Current trading date in YYYY-MM-DD format"
                    },
                    "look_back_days": {
                        "type": "integer",
                        "description": "Number of days to look back for historical data",
                        "default": 30
                    }
                },
                "required": ["symbol", "curr_date"]
            }
        ),
        Tool(
            name="get_indicators",
            description="Get technical indicators (RSI, MACD, Bollinger Bands, etc.) for stock analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    },
                    "indicator": {
                        "type": "string",
                        "description": "Technical indicator: rsi, macd, boll (Bollinger Bands), sma, ema, volume"
                    },
                    "curr_date": {
                        "type": "string",
                        "description": "Current trading date in YYYY-MM-DD format"
                    },
                    "look_back_days": {
                        "type": "integer",
                        "description": "Number of days to look back",
                        "default": 30
                    }
                },
                "required": ["symbol", "indicator", "curr_date"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tool calls."""
    
    if name == "get_stock_data":
        # Extract parameters
        symbol = arguments.get("symbol")
        curr_date = arguments.get("curr_date")
        look_back_days = arguments.get("look_back_days", 30)
        
        # Call existing vendor routing system
        result = route_to_vendor(
            "get_stock_data",
            symbol,
            curr_date,
            look_back_days
        )
        
        return [TextContent(
            type="text",
            text=result
        )]
    
    elif name == "get_indicators":
        # Extract parameters
        symbol = arguments.get("symbol")
        indicator = arguments.get("indicator")
        curr_date = arguments.get("curr_date")
        look_back_days = arguments.get("look_back_days", 30)
        
        # Call existing vendor routing system
        result = route_to_vendor(
            "get_indicators",
            symbol,
            indicator,
            curr_date,
            look_back_days
        )
        
        return [TextContent(
            type="text",
            text=result
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


def create_stock_server():
    """Create and return the stock MCP server."""
    return app


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

