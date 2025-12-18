"""
Timing test with only 2 analysts - Target: 1.5-2 minutes
"""

import time
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("🧪 TIMING TEST - 2 Analysts Only (Market + News)")
print("=" * 70)

config = DEFAULT_CONFIG.copy()
print("\n📊 Configuration:")
print(f"   Deep Think LLM: {config['deep_think_llm']}")
print(f"   Quick Think LLM: {config['quick_think_llm']}")
print(f"   Max Debate Rounds: {config['max_debate_rounds']}")
print(f"   Max Risk Rounds: {config['max_risk_discuss_rounds']}")
print()

# Only 2 analysts for speed
selected_analysts = ["market", "news"]  # Remove social & fundamentals
print(f"🎯 Testing with: {', '.join(selected_analysts)}")
print(f"   ⚡ Expected: 1.5-2 minutes")
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
print()

analysis_start = time.time()
final_state, decision = ta.propagate(ticker, date)
analysis_time = time.time() - analysis_start

total_time = init_time + analysis_time
print()
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

if total_time <= 120:
    print("✅ SUCCESS! Under 2 minutes with 2 analysts!")
elif total_time <= 150:
    print("✅ GOOD! Under 2.5 minutes")
else:
    print("⚠️  Still slow. Check internet connection and API limits")

