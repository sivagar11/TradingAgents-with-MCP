"""
Quick timing test - Check actual backend performance
"""

import time
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🧪 TIMING TEST - Backend Performance")
print("=" * 70)

# Show current config
config = DEFAULT_CONFIG.copy()
print("\n📊 Current Configuration:")
print(f"   Deep Think LLM: {config['deep_think_llm']}")
print(f"   Quick Think LLM: {config['quick_think_llm']}")
print(f"   Max Debate Rounds: {config['max_debate_rounds']}")
print(f"   Max Risk Rounds: {config['max_risk_discuss_rounds']}")
print()

# Test with all 4 analysts
selected_analysts = ["market", "social", "news", "fundamentals"]
print(f"🎯 Testing with: {', '.join(selected_analysts)}")
print()

# Initialize
print("⚙️  Initializing TradingAgentsGraph...")
init_start = time.time()
ta = TradingAgentsGraph(
    selected_analysts=selected_analysts,
    debug=False,  # Turn off debug for cleaner output
    config=config
)
init_time = time.time() - init_start
print(f"   ✅ Initialized in {init_time:.2f}s")
print()

# Run analysis
ticker = "NVDA"
date = "2024-11-01"

print(f"🚀 Starting analysis for {ticker} on {date}...")
print("-" * 70)

analysis_start = time.time()
final_state, decision = ta.propagate(ticker, date)
analysis_time = time.time() - analysis_start

print("-" * 70)
print()

# Results
total_time = init_time + analysis_time
print("=" * 70)
print("📊 TIMING RESULTS")
print("=" * 70)
print(f"   Initialization: {init_time:.2f}s")
print(f"   Analysis:       {analysis_time:.2f}s")
print(f"   TOTAL:          {total_time:.2f}s ({total_time/60:.2f} minutes)")
print()
print(f"   Decision: {decision}")
print("=" * 70)
print()

# Performance verdict
if total_time <= 90:
    print("✅ EXCELLENT! Under 1.5 minutes")
elif total_time <= 120:
    print("✅ GOOD! Under 2 minutes - optimizations working!")
elif total_time <= 180:
    print("⚠️  ACCEPTABLE. Under 3 minutes but could be better")
else:
    print("❌ SLOW. Over 3 minutes - optimizations may not be applied")
    print("\n🔍 Check these:")
    print("   1. Are you on FE branch? (git branch)")
    print("   2. Is max_debate_rounds = 0?")
    print("   3. Is deep_think_llm = 'gpt-4o-mini'?")

print()

