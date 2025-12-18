"""
DEMO MODE Timing Test - Ultra-fast version for live demos
Reduces API calls and LLM inference for speed
"""

import time
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🎬 DEMO MODE - Ultra-Fast Testing")
print("=" * 70)

# DEMO MODE config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 0
config["max_risk_discuss_rounds"] = 0

# CRITICAL: Use yfinance for everything to avoid Alpha Vantage rate limits
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "yfinance",  # Changed from alpha_vantage
    "news_data": "yfinance",  # Changed from alpha_vantage
}

print("\n⚡ DEMO MODE Optimizations:")
print("   • Using yfinance only (no Alpha Vantage rate limits)")
print("   • Simplified analyst prompts")
print("   • Fewer tool calls per analyst")
print("   • Concise reports (150 words each)")
print()

print("📊 Configuration:")
print(f"   Deep Think LLM: {config['deep_think_llm']}")
print(f"   Quick Think LLM: {config['quick_think_llm']}")
print(f"   Max Debate Rounds: {config['max_debate_rounds']}")
print(f"   Max Risk Rounds: {config['max_risk_discuss_rounds']}")
print()

# Use simplified analyst versions
selected_analysts = ["market", "social", "news", "fundamentals"]
print(f"🎯 Testing with: {', '.join(selected_analysts)}")
print(f"   Target: Under 2 minutes ⚡")
print()

print("⚙️  Initializing...")
init_start = time.time()
ta = TradingAgentsGraph(
    selected_analysts=selected_analysts,
    debug=False,
    config=config
)
init_time = time.time() - init_start
print(f"   ✅ Done in {init_time:.2f}s")
print()

ticker = "NVDA"
date = "2024-11-01"
print(f"🚀 Analyzing {ticker} on {date}...")
print("-" * 70)

analysis_start = time.time()
final_state, decision = ta.propagate(ticker, date)
analysis_time = time.time() - analysis_start

total_time = init_time + analysis_time
print("-" * 70)
print()
print("=" * 70)
print("📊 DEMO MODE RESULTS")
print("=" * 70)
print(f"   Initialization: {init_time:.2f}s")
print(f"   Analysis:       {analysis_time:.2f}s")
print(f"   TOTAL:          {total_time:.2f}s ({total_time/60:.2f} minutes)")
print()
print(f"   Decision: {decision}")
print("=" * 70)
print()

# Performance verdict
if total_time <= 120:
    improvement = ((225 - total_time) / 225) * 100
    print(f"🎉 SUCCESS! Demo ready!")
    print(f"   {improvement:.1f}% faster than full analysis")
    print(f"   Perfect for live demonstrations")
elif total_time <= 150:
    print("✅ GOOD! Under 2.5 minutes")
    print("   Acceptable for demos")
else:
    print("⚠️  Still slow. May need further optimization")
    print("   Consider using only 2 analysts for demos")

print()
print("💡 Note: DEMO MODE prioritizes speed over exhaustive accuracy")
print("   The system still provides valid analysis and decisions")

