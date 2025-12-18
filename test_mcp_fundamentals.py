#!/usr/bin/env python3
"""
Test Fundamentals Analyst with MCP Integration

This script tests the Fundamentals MCP server independently.
"""

import os
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

print()
print("=" * 80)
print("🧪 FUNDAMENTALS ANALYST MCP INTEGRATION TEST")
print("=" * 80)
print()

# Configuration
TICKER = "NVDA"
DATE = "2024-11-01"
ANALYSTS = ["fundamentals"]  # Only Fundamentals analyst

config = DEFAULT_CONFIG.copy()
config.update({
    "use_mcp": True,  # Enable MCP!
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 0,
    "max_risk_discuss_rounds": 0,
    # Use yfinance for fundamentals (no API key needed)
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",
        "news_data": "yfinance",
    },
})

print("📊 Configuration:")
print(f"   Mode: MCP")
print(f"   Ticker: {TICKER}")
print(f"   Date: {DATE}")
print(f"   Analyst: Fundamentals only")
print(f"   Fundamentals Vendor: yfinance")
print()

async def run_test():
    """Run the Fundamentals analyst MCP test."""
    
    graph = None
    
    try:
        # Step 1: Initialize
        print("-" * 80)
        print("STEP 1: Initializing TradingAgents with MCP (Fundamentals Server)...")
        print("-" * 80)
        init_start = time.time()

        try:
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
            return None, None, None

        # Step 2: Run Analysis
        print("-" * 80)
        print("STEP 2: Running Fundamentals analysis via MCP...")
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
print("Starting test...")
print()
init_time, analysis_time, final_state = asyncio.run(run_test())

if final_state is None:
    print()
    print("=" * 80)
    print("❌ TEST FAILED")
    print("=" * 80)
    print()
    print("💡 Troubleshooting:")
    print("   1. Check OPENAI_API_KEY in .env file")
    print("   2. Verify yfinance can fetch data for ticker")
    print("   3. Try running with DIRECT mode: config['use_mcp'] = False")
    print()
    exit(1)

# Step 4: Verify Results
print("-" * 80)
print("STEP 4: Verifying results...")
print("-" * 80)

fundamentals_report = final_state.get("fundamentals_report") if final_state else None
decision = final_state.get("final_trade_decision") if final_state else None

if fundamentals_report:
    print(f"✅ Fundamentals Report: {len(fundamentals_report)} characters")
    print()
    print("📈 Fundamentals Report Preview:")
    print("-" * 80)
    print(fundamentals_report[:500] + "..." if len(fundamentals_report) > 500 else fundamentals_report)
    print("-" * 80)
else:
    print("❌ Fundamentals Report: NOT GENERATED")

print()

if decision:
    print(f"✅ Final Decision: {len(decision)} characters")
else:
    print("❌ Final Decision: NOT GENERATED")

print()

# Summary
print("=" * 80)
print("📊 FUNDAMENTALS ANALYST MCP TEST SUMMARY")
print("=" * 80)
print()

if fundamentals_report and decision:
    print("🎉 TEST PASSED! ✅")
    print()
    print(f"⏱️  Initialization: {init_time:.2f}s")
    print(f"⏱️  Analysis: {analysis_time:.2f}s")
    print(f"⏱️  Total: {init_time + analysis_time:.2f}s")
    print()
    print("✅ MCP Integration Status:")
    print("   - Fundamentals MCP Server: WORKING")
    print("   - Tool Routing: WORKING")
    print("   - Data Fetching: WORKING")
    print("   - Report Generation: WORKING")
    print()
    print("Next: Test social analyst")
else:
    print("⚠️  TEST INCOMPLETE")
    print()
    print("Some components failed. Check the logs above.")

print()
print("=" * 80)
print()

