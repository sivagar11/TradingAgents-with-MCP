import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
DEFAULT_RESULTS_DIR = os.path.join(PROJECT_DIR, "results")
DEFAULT_DATA_DIR = os.path.join(PROJECT_DIR, "data")
DEFAULT_DATA_CACHE_DIR = os.path.join(PROJECT_DIR, "dataflows/data_cache")
PYTHON_CMD = os.getenv("TRADINGAGENTS_PYTHON", sys.executable)

DEFAULT_CONFIG = {
    "project_dir": PROJECT_DIR,
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", DEFAULT_RESULTS_DIR),
    "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", DEFAULT_DATA_DIR),
    "data_cache_dir": os.getenv("TRADINGAGENTS_DATA_CACHE_DIR", DEFAULT_DATA_CACHE_DIR),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",  # Use fast model instead of o4-mini
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 0,  # Skip debate for faster demo
    "max_risk_discuss_rounds": 0,  # Skip risk debate for faster demo
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: yfinance, alpha_vantage, local
        "technical_indicators": "yfinance",  # Options: yfinance, alpha_vantage, local
        "fundamental_data": "alpha_vantage", # Options: openai, alpha_vantage, local (primary: alpha_vantage, fallback: openai)
        "news_data": "alpha_vantage",        # Options: openai, alpha_vantage, google, local (primary: alpha_vantage, fallback: openai)
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
        # Example: "get_news": "openai",               # Override category default
    },
    # MCP (Model Context Protocol) Configuration
    "use_mcp": False,  # Toggle to use MCP servers instead of direct tool calls (for research comparison)
    "mcp_servers": {
        # MCP server configurations (only used if use_mcp=True)
        "stock": {
            "command": PYTHON_CMD,
            "args": [
                os.path.join(
                    PROJECT_DIR,
                    "mcp_servers/stock_server/server.py"
                )
            ]
        },
        "news": {
            "command": PYTHON_CMD,
            "args": [
                os.path.join(
                    PROJECT_DIR,
                    "mcp_servers/news_server/server.py"
                )
            ]
        },
        "fundamentals": {
            "command": PYTHON_CMD,
            "args": [
                os.path.join(
                    PROJECT_DIR,
                    "mcp_servers/fundamentals_server/server.py"
                )
            ]
        },
        "social": {
            "command": PYTHON_CMD,
            "args": [
                os.path.join(
                    PROJECT_DIR,
                    "mcp_servers/social_server/server.py"
                )
            ]
        },
    },
    "mcp_tool_mapping": {
        # Maps tool names to MCP server names
        # Stock tools
        "get_stock_data": "stock",
        "get_indicators": "stock",
        # News tools
        "get_news": "news",
        "get_global_news": "news",
        "get_insider_sentiment": "news",
        "get_insider_transactions": "news",
        # Fundamentals tools
        "get_fundamentals": "fundamentals",
        "get_balance_sheet": "fundamentals",
        "get_cashflow": "fundamentals",
        "get_income_statement": "fundamentals",
        # Social tools (uses news server)
        # Note: social analyst uses get_news, already mapped above
    },
}
