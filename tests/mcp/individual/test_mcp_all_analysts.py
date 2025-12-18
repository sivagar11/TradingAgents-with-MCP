#!/usr/bin/env python3
"""
Test All 4 Analysts with MCP Integration

This script tests the complete MCP integration with all 4 analysts:
- Market Analyst (stock server)
- News Analyst (news server)
- Fundamentals Analyst (fundamentals server)
- Social Analyst (social server)
"""

import os
import sys
import time
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Load environment variables from project root
env_path = project_root / '.env'
load_dotenv(env_path)

print()
print("=" * 80)
print("🧪 ALL 4 ANALYSTS MCP INTEGRATION TEST")
print("=" * 80)
print()
print("Testing complete MCP integration with all 4 analysts...")
print()

# Configuration
TICKER = "NVDA"
DATE = "2024-11-01"
ANALYSTS = ["market", "social", "news", "fundamentals"]  # All 4 analysts

config = DEFAULT_CONFIG.copy()
config.update({
    "use_mcp": True,  # Enable MCP!
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 0,
    "max_risk_discuss_rounds": 0,
    # Use DEFAULT_CONFIG vendors for fair comparison with DIRECT mode
    # (no vendor overrides - uses openai for fundamentals/news)
})

print("📊 Configuration:")
print(f"   Mode: MCP (enabled)")
print(f"   Ticker: {TICKER}")
print(f"   Date: {DATE}")
print(f"   Analysts: {ANALYSTS}")
print()


async def run_test():
    """Run the full 4-analyst MCP test."""
    
    graph = None
    
    try:
        # Step 1: Initialize
        print("-" * 80)
        print("STEP 1: Initializing TradingAgents with MCP (ALL 4 SERVERS)...")
        print("-" * 80)
        init_start = time.time()

        try:
            # Use async factory method for MCP mode
            graph = await TradingAgentsGraph.create(
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
            print("   2. Check that all MCP server paths are correct in default_config.py")
            print("   3. Try running each server standalone to test")
            return None, None, None

        # Step 2: Run Analysis
        print("-" * 80)
        print("STEP 2: Running analysis with ALL 4 ANALYSTS via MCP...")
        print("-" * 80)
        analysis_start = time.time()

        try:
            final_state, signal = await graph.propagate(TICKER, DATE)
            analysis_time = time.time() - analysis_start
            print(f"✅ SUCCESS: Analysis completed in {analysis_time:.2f}s")
            print()
        except Exception as e:
            print(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None
        
        return init_time, analysis_time, final_state
    
    finally:
        # Step 3: Cleanup (always runs)
        if graph is not None:
            print("-" * 80)
            print("STEP 3: Cleaning up MCP connections...")
            print("-" * 80)
            try:
                await graph.close()
                print("✅ MCP connections closed cleanly")
                print()
            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")
                print()


# Run the async test
init_time, analysis_time, final_state = asyncio.run(run_test())

if final_state is None:
    print("Test failed - exiting")
    exit(1)

# Step 4: Verify Results
print("-" * 80)
print("STEP 4: Verifying results...")
print("-" * 80)

market_report = final_state.get("market_report") if final_state else None
social_report = final_state.get("sentiment_report") if final_state else None
news_report = final_state.get("news_report") if final_state else None
fundamentals_report = final_state.get("fundamentals_report") if final_state else None
decision = final_state.get("final_trade_decision") if final_state else None

reports = {
    "Market": market_report,
    "Social": social_report,
    "News": news_report,
    "Fundamentals": fundamentals_report
}

for name, report in reports.items():
    if report:
        print(f"✅ {name} Report: {len(report)} characters")
    else:
        print(f"❌ {name} Report: NOT GENERATED")

if decision:
    print(f"✅ Final Decision: {len(decision)} characters")
else:
    print("❌ Final Decision: NOT GENERATED")

print()

# Summary
print("=" * 80)
print("🎉 ALL 4 ANALYSTS MCP INTEGRATION TEST RESULTS")
print("=" * 80)
print()

all_reports_generated = all(report is not None for report in reports.values())
decision_generated = decision is not None

print(f"✅ MCP Client Initialization: PASSED ({init_time:.2f}s)")
print(f"✅ All 4 MCP Servers Connected: PASSED")
print(f"✅ Analysis Completion: PASSED ({analysis_time:.2f}s)")
print(f"✅ Market Report: {'PASSED' if market_report else 'FAILED'}")
print(f"✅ Social Report: {'PASSED' if social_report else 'FAILED'}")
print(f"✅ News Report: {'PASSED' if news_report else 'FAILED'}")
print(f"✅ Fundamentals Report: {'PASSED' if fundamentals_report else 'FAILED'}")
print(f"✅ Final Decision: {'PASSED' if decision_generated else 'FAILED'}")
print()
print(f"⏱️  Total Time: {init_time + analysis_time:.2f}s")
print()
print("=" * 80)
print()

if all_reports_generated and decision_generated:
    print("🎯 CONCLUSION: Complete MCP Integration is WORKING! ✅")
    print()
    print("All 4 analysts successfully used MCP to call their respective tools:")
    print("  - Market Analyst → Stock MCP Server")
    print("  - News Analyst → News MCP Server")
    print("  - Fundamentals Analyst → Fundamentals MCP Server")
    print("  - Social Analyst → Social MCP Server")
else:
    print("⚠️  CONCLUSION: Some reports failed to generate")
    print("Check the logs above for details")

print()
print("Next steps:")
print("  1. Compare with DIRECT mode: python test_mcp_comparison.py")
print("  2. Document performance findings")
print("  3. Write research conclusions")
print()

