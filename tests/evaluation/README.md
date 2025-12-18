# TradingAgents Evaluation Suite

This directory contains the evaluation framework for the TradingAgents MSc dissertation research.

## 🎯 Evaluation Goals

The evaluation answers two key questions:
1. **Does the system work end-to-end as a trading system?**
2. **What changes when MCP replaces direct tool calls?**

This is **not** about proving "best performance in the world" - it's about proving **architectural impact and feasibility**.

## 📁 Directory Structure

```
tests/evaluation/
├── README.md                     # This file
├── backtest.py                   # Backtesting engine
├── run_functional_test.py        # TEST SET 1: Functional Trading Test
└── results/                      # Test outputs (generated)
    ├── direct_trades_*.csv
    ├── direct_daily_log_*.csv
    ├── direct_summary_*.txt
    ├── mcp_trades_*.csv
    ├── mcp_daily_log_*.csv
    ├── mcp_summary_*.txt
    └── functional_test_comparison_*.txt
```

## 🧪 Test Sets

### TEST SET 1: Functional Trading Test ⭐ (MANDATORY)

**Purpose:** Show that both systems actually work as trading systems.

**What it does:**
- Runs identical backtest for Direct and MCP modes
- Same asset (NVDA)
- Same time window (10 trading days in Nov 2024)
- Same initial capital ($10,000)
- Same decision logic

**What it proves:**
- ✅ Your system is functional
- ✅ MCP does not break trading logic

**How to run:**
```bash
cd /Users/sivagar/Desktop/LMS/sem3/Trading_agent/TradingAgents
python tests/evaluation/run_functional_test.py
```

**Output:**
- Trade logs (CSV)
- Daily portfolio logs (CSV)
- Summary statistics (TXT)
- Comparison report (TXT)

**Time:** ~15-30 minutes (depending on LLM response times)

---

### TEST SET 2: Trading Performance Comparison (Coming Soon)

**Purpose:** Show relative behavior, not optimization.

**Metrics:**
- Cumulative Return (%)
- Win Rate (%)
- Maximum Drawdown
- Directional Accuracy

---

### TEST SET 3: MCP Communication Tests (Coming Soon)

**Purpose:** This is your novelty - prove MCP's value.

**Sub-tests:**
- 3.1: Protocol Correctness (JSON-RPC examples)
- 3.2: Tool Call Reliability (success rates)
- 3.3: Traceability & Logging (audit trail demo)

---

### TEST SET 4: Qualitative Comparison (Coming Soon)

**Purpose:** Explain differences without heavy math.

**Comparison aspects:**
- Communication structure
- Logging
- Debugging
- Governance
- Extensibility

---

## 🚀 Quick Start

### Prerequisites

1. Environment setup:
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-mcp.txt

# Ensure .env file has API keys
OPENAI_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
```

2. Switch to evaluation branch:
```bash
git checkout MCP-evaluation
```

### Running TEST SET 1

```bash
cd /Users/sivagar/Desktop/LMS/sem3/Trading_agent/TradingAgents
python tests/evaluation/run_functional_test.py
```

The test will:
1. Run Direct mode backtest first
2. Pause for review
3. Run MCP mode backtest
4. Generate comparison report
5. Save all results to `results/` directory

### Understanding the Results

**Trade Logs** (`*_trades_*.csv`):
- Every buy/sell/hold decision
- Prices, shares, portfolio values
- Reasoning for each decision

**Daily Logs** (`*_daily_log_*.csv`):
- Daily portfolio state
- Cash, shares, total value
- Decision made each day

**Summary** (`*_summary_*.txt`):
- High-level metrics
- Total return
- Number of trades
- Final portfolio value

**Comparison Report** (`functional_test_comparison_*.txt`):
- Side-by-side comparison
- Key findings
- Conclusion

---

## 📊 What the Evaluation Proves

### After TEST SET 1 ✅
- Your system is a working trading system
- Both architectures produce real decisions
- MCP does not break functionality

This alone **passes many MSc dissertations**.

### After TEST SET 2 ✅
- Performance is comparable between modes
- MCP introduces minor overhead
- No optimization was performed (honest approach)

### After TEST SET 3 ✅✅✅ (NOVELTY)
- MCP enables structured communication
- Full traceability and auditability
- Better governance than direct calls
- This is your **unique contribution**

### After TEST SET 4 ✅
- Qualitative benefits documented
- Software engineering improvements shown
- Extensibility and maintainability advantages clear

---

## 🎓 Dissertation Usage

### What to include in your dissertation:

**Chapter: Evaluation**

1. **Methodology** (TEST SET 1):
   - Backtest configuration
   - Test environment
   - Fair comparison setup

2. **Results** (TEST SET 1 & 2):
   - Trading outcomes table
   - Performance metrics comparison
   - Trade logs excerpts

3. **MCP Analysis** (TEST SET 3):
   - Protocol correctness evidence
   - Reliability comparison
   - Traceability example (THIS IS GOLD)

4. **Discussion** (TEST SET 4):
   - Qualitative comparison table
   - Software engineering benefits
   - Governance improvements

### What NOT to claim:
- ❌ "Best trading performance"
- ❌ "Statistically significant results"
- ❌ "Production-ready system"

### What TO claim:
- ✅ "Functional trading system"
- ✅ "Comparable performance"
- ✅ "MCP improves traceability"
- ✅ "Architectural feasibility demonstrated"

---

## 📝 Test Configuration

### Current Settings

```python
# Asset & Period
SYMBOL = "NVDA"
START_DATE = "2024-11-01"
END_DATE = "2024-11-14"  # ~10 trading days

# Portfolio
INITIAL_CAPITAL = 10000.0
SHARES_PER_TRADE = 10

# Agents
ANALYSTS = ["market", "social", "news", "fundamentals"]

# LLM
MODEL = "gpt-4o-mini"
DEBATE_ROUNDS = 0  # Optimized for speed
```

### Why These Settings?

- **10 days**: Enough to show behavior, not too long to run
- **$10,000**: Realistic starting capital
- **10 shares/trade**: Simple, consistent position sizing
- **4 analysts**: Full system functionality
- **gpt-4o-mini**: Fast, cost-effective
- **0 debates**: Optimized for demo/eval

---

## 🔧 Troubleshooting

### Test hangs or times out
- Check API keys in `.env`
- Verify MCP servers start correctly
- Review logs for errors

### Different results between runs
- This is expected (LLM non-determinism)
- Focus on: "Both produce decisions" not "Identical decisions"

### MCP connection errors
- Ensure `requirements-mcp.txt` installed
- Check MCP server logs in stderr
- Verify environment variables passed to subprocesses

---

## 📚 References

- Main README: `../../README.md`
- MCP Integration Guide: `../../MCP_INTEGRATION_GUIDE.md`
- MCP Testing Guide: `../../MCP_TESTING_GUIDE.md`

---

## 💡 Tips for Success

1. **Run TEST SET 1 first** - It's the foundation
2. **Save all outputs** - You'll need them for the dissertation
3. **Focus on MCP novelty** - That's your contribution
4. **Be honest about limitations** - It's stronger than overpromising
5. **Document everything** - Future you will thank present you

---

## ✅ Acceptance Criteria

Your evaluation is successful if it shows:

1. ✅ Both systems execute trades
2. ✅ Both systems maintain portfolio state
3. ✅ MCP doesn't break functionality
4. ✅ Performance is comparable
5. ✅ MCP provides better traceability

**You don't need perfect performance. You need working systems and clear comparison.**

---

## 🎯 Next Steps

1. Run TEST SET 1 ✅
2. Review results
3. Implement TEST SET 2 (performance metrics)
4. Implement TEST SET 3 (MCP communication tests) ⭐⭐⭐
5. Write TEST SET 4 (qualitative comparison)
6. Compile results for dissertation

---

**Good luck! 🚀**

