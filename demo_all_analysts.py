"""
Demo with All 4 Analysts - Optimized for ~1.5-2 minutes
All analysts enabled but with optimized settings
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

print("🚀 Starting Full Analysis Demo (All 4 Analysts)")
print("=" * 70)

# Create optimized config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"  # Fast model
config["quick_think_llm"] = "gpt-4o-mini"  # Fast model
config["max_debate_rounds"] = 0  # Skip research debate - HUGE time saver
config["max_risk_discuss_rounds"] = 0  # Skip risk debate - HUGE time saver

# Configure data vendors
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage",
}

print("\n📊 Configuration:")
print(f"   ✅ Analysts: ALL 4 (Market, Social, News, Fundamentals)")
print(f"   ✅ LLM Model: {config['quick_think_llm']} (fast)")
print(f"   ✅ Research Debate: {config['max_debate_rounds']} rounds (SKIPPED)")
print(f"   ✅ Risk Debate: {config['max_risk_discuss_rounds']} rounds (SKIPPED)")
print(f"\n   💡 Time Savings:")
print(f"      • No debates: -60-90 seconds")
print(f"      • Fast models: -30-60 seconds")
print(f"      • Target time: 1.5-2 minutes")
print()

# Initialize with ALL analysts
selected_analysts = ["market", "social", "news", "fundamentals"]
print(f"🎯 Enabled Analysts:")
print(f"   📈 Market Analyst - Technical indicators (MACD, RSI, etc.)")
print(f"   💬 Social Analyst - Sentiment analysis")
print(f"   📰 News Analyst - Current events & macro trends")
print(f"   📊 Fundamentals Analyst - Financial health & metrics")
print()

start_time = time.time()

# Initialize trading graph
print("⚙️  Initializing TradingAgents graph...")
ta = TradingAgentsGraph(
    selected_analysts=selected_analysts,
    debug=True,  # Show detailed output
    config=config
)

# Run analysis
ticker = "NVDA"
analysis_date = "2024-11-01"

print(f"\n🎯 Analyzing {ticker} for {analysis_date}")
print("-" * 70)
print()

try:
    _, decision = ta.propagate(ticker, analysis_date)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print()
    print("=" * 70)
    print(f"✅ Analysis Complete!")
    print(f"📈 Final Decision: {decision}")
    print(f"⏱️  Total Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print("=" * 70)
    
    # Performance analysis
    print()
    print("📊 Performance Analysis:")
    if duration <= 90:
        print("   🎉 EXCELLENT! Under 1.5 minutes with all 4 analysts!")
    elif duration <= 120:
        print("   ✅ GOOD! Under 2 minutes - perfect for demos")
    elif duration <= 180:
        print("   ⚠️  ACCEPTABLE. Under 3 minutes - still much faster than original")
    else:
        print("   ⚠️  Consider checking:")
        print("      • Internet connection speed")
        print("      • API rate limits")
        print("      • Debate rounds are actually 0")
    
    # Time breakdown estimate
    print()
    print("⏱️  Estimated Time Breakdown:")
    analyst_time = duration * 0.6  # ~60% on analysts
    other_time = duration * 0.4    # ~40% on other agents
    print(f"   📊 Analysts (4): ~{analyst_time:.1f}s (~{analyst_time/4:.1f}s each)")
    print(f"   🤖 Other Agents: ~{other_time:.1f}s (Trader, Portfolio Manager)")
    
except Exception as e:
    print()
    print(f"❌ Error during analysis: {e}")
    import traceback
    traceback.print_exc()

print()
print("💡 Tips for Even Faster Demos:")
print("   • Run same ticker twice (data cached)")
print("   • Use popular tickers (NVDA, AAPL, TSLA)")
print("   • Ensure stable internet connection")
print("   • Keep debate_rounds = 0")

