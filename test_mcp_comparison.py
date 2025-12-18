#!/usr/bin/env python3
"""
Test script to compare MCP vs Direct tool calling approaches.

This script runs the same analysis twice:
1. With MCP enabled (use_mcp=True)
2. With direct tool calls (use_mcp=False)

And measures:
- Execution time
- Success rate
- Output quality

For research paper comparison.
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

# Test configuration
TICKER = "NVDA"
DATE = "2024-11-01"
ANALYSTS = ["market"]  # Start with just market analyst for POC


def run_analysis(use_mcp: bool, run_name: str):
    """Run analysis with specified configuration."""
    
    print("=" * 80)
    print(f"🧪 {run_name}")
    print("=" * 80)
    print()
    
    # Configure
    config = DEFAULT_CONFIG.copy()
    config.update({
        "use_mcp": use_mcp,
        "llm_provider": "openai",
        "deep_think_llm": "gpt-4o-mini",
        "quick_think_llm": "gpt-4o-mini",
        "max_debate_rounds": 0,
        "max_risk_discuss_rounds": 0,
    })
    
    print(f"📊 Configuration:")
    print(f"   Mode: {'MCP' if use_mcp else 'DIRECT'}")
    print(f"   Ticker: {TICKER}")
    print(f"   Date: {DATE}")
    print(f"   Analysts: {ANALYSTS}")
    print()
    
    # Initialize
    print("⚙️  Initializing...")
    init_start = time.time()
    try:
        graph = TradingAgentsGraph(
            selected_analysts=ANALYSTS,
            debug=False,
            config=config
        )
        init_time = time.time() - init_start
        print(f"   ✅ Initialized in {init_time:.2f}s")
        print()
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return None
    
    # Run analysis
    print("🚀 Running analysis...")
    analysis_start = time.time()
    try:
        final_state, signal = graph.propagate(TICKER, DATE)
        analysis_time = time.time() - analysis_start
        print(f"   ✅ Completed in {analysis_time:.2f}s")
        print()
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Results
    total_time = init_time + analysis_time
    
    results = {
        "mode": "MCP" if use_mcp else "DIRECT",
        "init_time": init_time,
        "analysis_time": analysis_time,
        "total_time": total_time,
        "decision": final_state.get("final_trade_decision", "N/A"),
        "market_report": final_state.get("market_report", "N/A"),
        "success": True
    }
    
    print("=" * 80)
    print("📊 RESULTS")
    print("=" * 80)
    print(f"   Mode: {results['mode']}")
    print(f"   Initialization: {results['init_time']:.2f}s")
    print(f"   Analysis: {results['analysis_time']:.2f}s")
    print(f"   TOTAL: {results['total_time']:.2f}s")
    print(f"   Decision: {results['decision']}")
    print()
    print(f"   Market Report Preview:")
    report = results['market_report']
    if report and len(report) > 200:
        print(f"   {report[:200]}...")
    else:
        print(f"   {report}")
    print("=" * 80)
    print()
    
    return results


def main():
    """Run comparison test."""
    
    print()
    print("🔬 MCP vs DIRECT Tool Calling Comparison Test")
    print("=" * 80)
    print()
    print("This test will run the same analysis twice:")
    print("  1. With MCP (Model Context Protocol)")
    print("  2. With DIRECT tool calls (original system)")
    print()
    print("And compare performance, latency, and results.")
    print()
    input("Press Enter to start...")
    print()
    
    # Run both approaches
    results = {}
    
    # Test 1: Direct mode (original)
    results["direct"] = run_analysis(use_mcp=False, run_name="TEST 1: DIRECT MODE (Original System)")
    
    if not results["direct"]:
        print("❌ Direct mode failed. Cannot continue comparison.")
        return
    
    print()
    input("Press Enter to continue to MCP test...")
    print()
    
    # Test 2: MCP mode
    results["mcp"] = run_analysis(use_mcp=True, run_name="TEST 2: MCP MODE (New System)")
    
    if not results["mcp"]:
        print("❌ MCP mode failed.")
        print()
    
    # Comparison
    print()
    print("=" * 80)
    print("📊 COMPARISON SUMMARY")
    print("=" * 80)
    print()
    
    if results["mcp"]:
        direct_time = results["direct"]["total_time"]
        mcp_time = results["mcp"]["total_time"]
        overhead = mcp_time - direct_time
        overhead_pct = (overhead / direct_time) * 100
        
        print(f"⏱️  TIMING:")
        print(f"   Direct Mode:  {direct_time:.2f}s")
        print(f"   MCP Mode:     {mcp_time:.2f}s")
        print(f"   Overhead:     {overhead:+.2f}s ({overhead_pct:+.1f}%)")
        print()
        
        print(f"🎯 DECISIONS:")
        print(f"   Direct: {results['direct']['decision']}")
        print(f"   MCP:    {results['mcp']['decision']}")
        print(f"   Match:  {'✅ Yes' if results['direct']['decision'] == results['mcp']['decision'] else '❌ No'}")
        print()
        
        print(f"📝 ANALYSIS:")
        if overhead_pct < 10:
            print(f"   ✅ MCP overhead is minimal ({overhead_pct:.1f}%)")
        elif overhead_pct < 25:
            print(f"   ⚠️  MCP adds moderate overhead ({overhead_pct:.1f}%)")
        else:
            print(f"   ❌ MCP adds significant overhead ({overhead_pct:.1f}%)")
        print()
        
        print(f"💡 RECOMMENDATION:")
        if overhead_pct < 15 and results['direct']['decision'] == results['mcp']['decision']:
            print(f"   ✅ MCP is production-ready!")
            print(f"   The overhead is acceptable and results are consistent.")
        else:
            print(f"   🔬 MCP is good for research but needs optimization for production")
        
    else:
        print("❌ MCP test failed - no comparison available")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()

