"""
Quick Demo Script - Runs in ~1 minute
Optimized for fast demonstration with minimal agents and no debates
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

print("🚀 Starting Quick Demo (Target: ~1 minute)")
print("=" * 60)

# Create optimized config for quick demo
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"  # Fast model
config["quick_think_llm"] = "gpt-4o-mini"  # Fast model
config["max_debate_rounds"] = 0  # Skip research debate
config["max_risk_discuss_rounds"] = 0  # Skip risk debate

# Configure data vendors
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage",
}

print("\n📊 Configuration:")
print(f"   - Analysts: Market only")
print(f"   - LLM Model: {config['quick_think_llm']}")
print(f"   - Debate Rounds: {config['max_debate_rounds']}")
print(f"   - Risk Debate: {config['max_risk_discuss_rounds']}")
print()

# Initialize with only market analyst (fastest option)
selected_analysts = ["market"]  # Only technical analysis
print(f"✅ Selected Analysts: {', '.join(selected_analysts)}")
print()

start_time = time.time()

# Initialize trading graph
ta = TradingAgentsGraph(
    selected_analysts=selected_analysts,
    debug=True,
    config=config
)

# Run analysis
ticker = "NVDA"
analysis_date = "2024-11-01"

print(f"🎯 Analyzing {ticker} for {analysis_date}")
print("-" * 60)
print()

_, decision = ta.propagate(ticker, analysis_date)

end_time = time.time()
duration = end_time - start_time

print()
print("=" * 60)
print(f"✅ Analysis Complete!")
print(f"📈 Decision: {decision}")
print(f"⏱️  Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
print("=" * 60)

if duration <= 60:
    print("🎉 SUCCESS! Under 1 minute!")
elif duration <= 90:
    print("⚠️  Close! Consider removing more analysts or using cached data")
else:
    print("⚠️  Still too slow. Try with debate_rounds=0 and single analyst")

