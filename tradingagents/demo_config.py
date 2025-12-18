"""
DEMO MODE Configuration - Optimized for speed over accuracy
Use this for live demos where speed is more important than exhaustive analysis
"""

DEMO_CONFIG = {
    "project_dir": "/Users/sivagar/Desktop/LMS/sem3/Trading_agent/TradingAgents",
    "results_dir": "./results",
    "data_cache_dir": "./tradingagents/dataflows/data_cache",
    
    # LLM settings - FAST models only
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",  # Fast model
    "quick_think_llm": "gpt-4o-mini",  # Fast model
    "backend_url": "https://api.openai.com/v1",
    
    # Debate settings - SKIP for demo
    "max_debate_rounds": 0,  # No debates
    "max_risk_discuss_rounds": 0,  # No risk debates
    "max_recur_limit": 100,
    
    # Data vendor configuration
    "data_vendors": {
        "core_stock_apis": "yfinance",  # Fast and free
        "technical_indicators": "yfinance",  # Fast and free
        "fundamental_data": "yfinance",  # CHANGED: Use yfinance to avoid Alpha Vantage rate limits
        "news_data": "yfinance",  # CHANGED: Skip news to save time
    },
    
    # DEMO MODE specific settings
    "demo_mode": True,
    "max_tools_per_analyst": 2,  # Limit tool calls
    "skip_redundant_calls": True,  # Skip duplicate data fetching
    "use_cache_aggressively": True,  # Reuse data when possible
}

