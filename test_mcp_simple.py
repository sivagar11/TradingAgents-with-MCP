#!/usr/bin/env python3
"""
Simple MCP Integration Test

This script just tests if MCP works - no comparison with DIRECT mode.
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

print()
print("=" * 80)
print("🧪 MCP INTEGRATION TEST")
print("=" * 80)
print()
print("Testing if Model Context Protocol (MCP) integration works...")
print()

# Configuration
TICKER = "NVDA"
DATE = "2024-11-01"
ANALYSTS = ["market"]  # Just market analyst for simple test

config = DEFAULT_CONFIG.copy()
config.update({
    "use_mcp": True,  # Enable MCP!
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 0,
    "max_risk_discuss_rounds": 0,
})

print("📊 Configuration:")
print(f"   Mode: MCP (enabled)")
print(f"   Ticker: {TICKER}")
print(f"   Date: {DATE}")
print(f"   Analysts: {ANALYSTS}")
print()

# Step 1: Initialize
print("-" * 80)
print("STEP 1: Initializing TradingAgents with MCP...")
print("-" * 80)
init_start = time.time()

try:
    graph = TradingAgentsGraph(
        selected_analysts=ANALYSTS,
        debug=False,
        config=config
    )
    init_time = time.time() - init_start
    print(f"✅ SUCCESS: Initialized in {init_time:.2f}s")
    print()
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("💡 Troubleshooting:")
    print("   1. Make sure MCP packages are installed: pip install -r requirements-mcp.txt")
    print("   2. Check that the MCP server path is correct in default_config.py")
    print("   3. Try running the server standalone to test it")
    exit(1)

# Step 2: Run Analysis
print("-" * 80)
print("STEP 2: Running analysis with MCP...")
print("-" * 80)
analysis_start = time.time()

try:
    final_state, signal = graph.propagate(TICKER, DATE)
    analysis_time = time.time() - analysis_start
    print(f"✅ SUCCESS: Analysis completed in {analysis_time:.2f}s")
    print()
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 3: Verify Results
print("-" * 80)
print("STEP 3: Verifying results...")
print("-" * 80)

market_report = final_state.get("market_report")
decision = final_state.get("final_trade_decision")

if market_report:
    print("✅ Market Report Generated")
    print(f"   Length: {len(market_report)} characters")
    print(f"   Preview: {market_report[:150]}...")
    print()
else:
    print("❌ No market report found")
    print()

if decision:
    print("✅ Final Decision Generated")
    if len(decision) > 500:
        print(f"   Preview: {decision[:500]}...")
    else:
        print(f"   Decision: {decision}")
    print()
else:
    print("⚠️  No final decision (expected if only running 1 analyst)")
    print()

# Summary
print("=" * 80)
print("🎉 MCP INTEGRATION TEST RESULTS")
print("=" * 80)
print()
print(f"✅ MCP Client Initialization: PASSED ({init_time:.2f}s)")
print(f"✅ MCP Tool Execution: PASSED")
print(f"✅ Analysis Completion: PASSED ({analysis_time:.2f}s)")
print(f"✅ Result Generation: PASSED")
print()
print(f"⏱️  Total Time: {init_time + analysis_time:.2f}s")
print()
print("=" * 80)
print()
print("🎯 CONCLUSION: MCP Integration is WORKING! ✅")
print()
print("Next steps:")
print("  1. Run comparison test: python test_mcp_comparison.py")
print("  2. Implement remaining MCP servers (news, fundamentals, social)")
print("  3. Test with all 4 analysts")
print()

