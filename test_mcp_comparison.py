#!/usr/bin/env python3
"""
MCP vs Direct Mode Comparison Test

This script compares the performance and results of:
1. DIRECT mode: Traditional tool calling via LangGraph ToolNode
2. MCP mode: Tool calling via Model Context Protocol

Purpose: Measure MCP overhead for research purposes
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
print("🔬 MCP vs DIRECT MODE COMPARISON TEST")
print("=" * 80)
print()
print("This test compares MCP and Direct tool calling for research purposes")
print()

# Configuration
TICKER = "NVDA"
DATE = "2024-11-01"
ANALYSTS = ["market"]  # Start with one analyst for fair comparison

print("📊 Test Configuration:")
print(f"   Ticker: {TICKER}")
print(f"   Date: {DATE}")
print(f"   Analysts: {ANALYSTS}")
print()


def run_direct_mode():
    """Run analysis in DIRECT mode (traditional tool calling)."""
    print()
    print("=" * 80)
    print("TEST 1: DIRECT MODE (Traditional Tool Calling)")
    print("=" * 80)
    print()
    
    config = DEFAULT_CONFIG.copy()
    config.update({
        "use_mcp": False,  # DIRECT mode
        "llm_provider": "openai",
        "deep_think_llm": "gpt-4o-mini",
        "quick_think_llm": "gpt-4o-mini",
        "max_debate_rounds": 0,
        "max_risk_discuss_rounds": 0,
    })
    
    print("⚙️  Mode: DIRECT (use_mcp=False)")
    print()
    
    # Initialize
    print("-" * 80)
    print("STEP 1: Initializing TradingAgents (DIRECT mode)...")
    print("-" * 80)
    init_start = time.time()
    
    try:
        # DIRECT mode uses synchronous initialization
        graph = TradingAgentsGraph(
            selected_analysts=ANALYSTS,
            debug=False,
            config=config
        )
        init_time = time.time() - init_start
        print(f"✅ Initialized in {init_time:.2f}s")
        print()
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Run Analysis
    print("-" * 80)
    print("STEP 2: Running analysis (DIRECT mode)...")
    print("-" * 80)
    analysis_start = time.time()
    
    try:
        # DIRECT mode uses synchronous propagate
        final_state, signal = graph.propagate(TICKER, DATE)
        analysis_time = time.time() - analysis_start
        print(f"✅ Analysis completed in {analysis_time:.2f}s")
        print()
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Results
    market_report = final_state.get("market_report")
    decision = final_state.get("final_trade_decision")
    
    print("-" * 80)
    print("RESULTS (DIRECT mode):")
    print("-" * 80)
    print(f"✅ Market Report: {len(market_report) if market_report else 0} characters")
    print(f"✅ Final Decision: {len(decision) if decision else 0} characters")
    print(f"✅ Signal: {signal}")
    print()
    
    return {
        "mode": "DIRECT",
        "init_time": init_time,
        "analysis_time": analysis_time,
        "total_time": init_time + analysis_time,
        "report_length": len(market_report) if market_report else 0,
        "decision_length": len(decision) if decision else 0,
        "signal": signal,
        "state": final_state
    }


async def run_mcp_mode():
    """Run analysis in MCP mode."""
    print()
    print("=" * 80)
    print("TEST 2: MCP MODE (Model Context Protocol)")
    print("=" * 80)
    print()
    
    config = DEFAULT_CONFIG.copy()
    config.update({
        "use_mcp": True,  # MCP mode
        "llm_provider": "openai",
        "deep_think_llm": "gpt-4o-mini",
        "quick_think_llm": "gpt-4o-mini",
        "max_debate_rounds": 0,
        "max_risk_discuss_rounds": 0,
    })
    
    print("⚙️  Mode: MCP (use_mcp=True)")
    print()
    
    graph = None
    
    try:
        # Initialize
        print("-" * 80)
        print("STEP 1: Initializing TradingAgents (MCP mode)...")
        print("-" * 80)
        init_start = time.time()
        
        try:
            # MCP mode uses async factory method
            graph = await TradingAgentsGraph.create(
                selected_analysts=ANALYSTS,
                debug=False,
                config=config
            )
            init_time = time.time() - init_start
            print(f"✅ Initialized in {init_time:.2f}s")
            print()
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Run Analysis
        print("-" * 80)
        print("STEP 2: Running analysis (MCP mode)...")
        print("-" * 80)
        analysis_start = time.time()
        
        try:
            # MCP mode uses async propagate
            final_state, signal = await graph.propagate(TICKER, DATE)
            analysis_time = time.time() - analysis_start
            print(f"✅ Analysis completed in {analysis_time:.2f}s")
            print()
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # Results
        market_report = final_state.get("market_report")
        decision = final_state.get("final_trade_decision")
        
        print("-" * 80)
        print("RESULTS (MCP mode):")
        print("-" * 80)
        print(f"✅ Market Report: {len(market_report) if market_report else 0} characters")
        print(f"✅ Final Decision: {len(decision) if decision else 0} characters")
        print(f"✅ Signal: {signal}")
        print()
        
        return {
            "mode": "MCP",
            "init_time": init_time,
            "analysis_time": analysis_time,
            "total_time": init_time + analysis_time,
            "report_length": len(market_report) if market_report else 0,
            "decision_length": len(decision) if decision else 0,
            "signal": signal,
            "state": final_state
        }
    
    finally:
        # Cleanup
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


async def main():
    """Run comparison test."""
    results = {}
    
    # Test 1: DIRECT mode
    direct_result = run_direct_mode()
    if direct_result:
        results["direct"] = direct_result
    
    # Small delay between tests
    print()
    print("⏳ Waiting 5 seconds before MCP test...")
    print()
    await asyncio.sleep(5)
    
    # Test 2: MCP mode
    mcp_result = await run_mcp_mode()
    if mcp_result:
        results["mcp"] = mcp_result
    
    # Comparison
    if "direct" in results and "mcp" in results:
        print()
        print("=" * 80)
        print("📊 COMPARISON RESULTS")
        print("=" * 80)
        print()
        
        direct = results["direct"]
        mcp = results["mcp"]
        
        # Timing Comparison
        print("⏱️  TIMING COMPARISON:")
        print("-" * 80)
        print(f"{'Metric':<25} {'DIRECT':<15} {'MCP':<15} {'Difference':<15}")
        print("-" * 80)
        print(f"{'Initialization':<25} {direct['init_time']:<15.2f}s {mcp['init_time']:<15.2f}s {mcp['init_time'] - direct['init_time']:+.2f}s")
        print(f"{'Analysis':<25} {direct['analysis_time']:<15.2f}s {mcp['analysis_time']:<15.2f}s {mcp['analysis_time'] - direct['analysis_time']:+.2f}s")
        print(f"{'Total':<25} {direct['total_time']:<15.2f}s {mcp['total_time']:<15.2f}s {mcp['total_time'] - direct['total_time']:+.2f}s")
        print()
        
        # Calculate overhead
        overhead_seconds = mcp['total_time'] - direct['total_time']
        overhead_percent = (overhead_seconds / direct['total_time']) * 100
        print(f"🔍 MCP Overhead: {overhead_seconds:+.2f}s ({overhead_percent:+.1f}%)")
        print()
        
        # Output Comparison
        print("📄 OUTPUT COMPARISON:")
        print("-" * 80)
        print(f"{'Metric':<25} {'DIRECT':<15} {'MCP':<15} {'Difference':<15}")
        print("-" * 80)
        print(f"{'Report Length (chars)':<25} {direct['report_length']:<15} {mcp['report_length']:<15} {mcp['report_length'] - direct['report_length']:+d}")
        print(f"{'Decision Length (chars)':<25} {direct['decision_length']:<15} {mcp['decision_length']:<15} {mcp['decision_length'] - direct['decision_length']:+d}")
        print(f"{'Signal':<25} {direct['signal']:<15} {mcp['signal']:<15} {'✅ Same' if direct['signal'] == mcp['signal'] else '⚠️  Different'}")
        print()
        
        # Analysis
        print("=" * 80)
        print("🎯 ANALYSIS")
        print("=" * 80)
        print()
        
        if abs(overhead_percent) < 5:
            print("✅ MCP overhead is MINIMAL (<5%)")
            print("   → MCP is viable for production use")
        elif abs(overhead_percent) < 10:
            print("⚠️  MCP overhead is MODERATE (5-10%)")
            print("   → MCP is acceptable for most use cases")
        else:
            print("❌ MCP overhead is SIGNIFICANT (>10%)")
            print("   → Consider optimizations or use DIRECT mode for latency-critical tasks")
        
        print()
        
        if direct['signal'] == mcp['signal']:
            print("✅ Both modes produced the SAME trading signal")
            print("   → MCP maintains decision consistency")
        else:
            print("⚠️  Modes produced DIFFERENT trading signals")
            print("   → May be due to LLM non-determinism or data timing")
        
        print()
        
        report_diff_percent = abs(mcp['report_length'] - direct['report_length']) / direct['report_length'] * 100 if direct['report_length'] > 0 else 0
        if report_diff_percent < 10:
            print(f"✅ Report lengths are SIMILAR (±{report_diff_percent:.1f}%)")
            print("   → Both modes generate comparable output")
        else:
            print(f"⚠️  Report lengths DIFFER significantly (±{report_diff_percent:.1f}%)")
            print("   → Check for differences in LLM behavior or tool responses")
        
        print()
        print("=" * 80)
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print()
        print("Based on these results:")
        print()
        
        if overhead_percent < 5:
            print("1. ✅ MCP integration is highly efficient")
            print("2. ✅ Safe to use MCP for all analysts")
            print("3. ✅ MCP provides modularity without significant performance cost")
        elif overhead_percent < 10:
            print("1. ✅ MCP integration is reasonably efficient")
            print("2. ⚙️  Consider MCP for analysts with longer execution times")
            print("3. ⚙️  Profile individual analyst overhead for optimization")
        else:
            print("1. ⚠️  MCP has noticeable overhead")
            print("2. ⚙️  Consider hybrid approach: MCP for some, DIRECT for others")
            print("3. 🔧 Investigate MCP server optimizations (connection pooling, caching)")
        
        print()
        print("=" * 80)
        
    else:
        print()
        print("❌ Comparison incomplete - one or both tests failed")
        print()


if __name__ == "__main__":
    asyncio.run(main())
