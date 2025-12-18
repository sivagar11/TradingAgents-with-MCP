# TradingAgents Test Suite

This directory contains all test scripts for the TradingAgents system.

## Directory Structure

```
tests/
├── mcp/                          # MCP (Model Context Protocol) integration tests
│   ├── individual/               # Individual agent tests
│   │   ├── test_mcp_news.py      # News analyst MCP test
│   │   ├── test_mcp_fundamentals.py  # Fundamentals analyst MCP test
│   │   ├── test_mcp_social.py    # Social analyst MCP test
│   │   └── test_mcp_all_analysts.py  # All 4 analysts MCP test
│   ├── comparison/               # MCP vs Direct mode comparison tests
│   │   ├── test_mcp_comparison.py    # Basic comparison test
│   │   └── test_mcp_full_comparison.py  # Comprehensive comparison with detailed metrics
│   ├── server/                   # MCP server tests
│   │   └── test_mcp_server_standalone.py  # Standalone server test
│   └── test_mcp_simple.py        # Simple MCP integration test
├── examples/                     # Example usage scripts
│   └── main.py                   # Basic usage example
└── README.md                     # This file
```

## Running Tests

### Quick Start

From the project root directory:

```bash
# Run the comprehensive MCP vs Direct comparison (recommended for research)
python tests/mcp/comparison/test_mcp_full_comparison.py

# Run a simple MCP test
python tests/mcp/test_mcp_simple.py

# Run individual agent tests
python tests/mcp/individual/test_mcp_news.py
python tests/mcp/individual/test_mcp_fundamentals.py
python tests/mcp/individual/test_mcp_social.py
python tests/mcp/individual/test_mcp_all_analysts.py
```

### Test Types

#### 1. Individual Agent Tests (`mcp/individual/`)
- Test each analyst agent separately with MCP integration
- Verify MCP server functionality for specific data domains
- Useful for debugging and validating individual components

#### 2. Comparison Tests (`mcp/comparison/`)
- Compare MCP vs Direct tool calling approaches
- Measure performance overhead
- Generate detailed metrics for research analysis
- **`test_mcp_full_comparison.py`**: Most comprehensive test with per-agent metrics

#### 3. Server Tests (`mcp/server/`)
- Test MCP servers in isolation
- Verify server startup and subprocess management
- Debug server-side issues

#### 4. Simple Tests (`mcp/`)
- Quick sanity checks for MCP integration
- Minimal setup for rapid testing

## Configuration

All tests use the default configuration from `tradingagents/default_config.py`:

- **Data Vendors**: Alpha Vantage (primary) with OpenAI fallback
- **LLM Models**: `gpt-4o-mini` for both deep and quick thinking
- **Debate Rounds**: 0 (optimized for demo speed)
- **MCP Toggle**: Tests automatically set `use_mcp: True` when needed

## Environment Setup

Ensure you have all required API keys in your `.env` file:

```bash
OPENAI_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-mcp.txt
```

## Research Notes

For research on MCP overhead and performance:

1. Use `tests/mcp/comparison/test_mcp_full_comparison.py`
2. This provides:
   - Overall system metrics (execution time, success rates)
   - Per-agent metrics (individual timing and performance)
   - Side-by-side comparison (Direct vs MCP)
   - Research analysis and conclusions
3. Results are saved with timestamps for reproducibility

## Troubleshooting

If tests fail:

1. Check environment variables are set
2. Verify API keys are valid
3. Ensure all dependencies are installed
4. Review logs in test output
5. Check `MCP_TESTING_GUIDE.md` in the project root for detailed troubleshooting

## Additional Documentation

- `../MCP_INTEGRATION_GUIDE.md` - Complete MCP integration documentation
- `../MCP_TESTING_GUIDE.md` - Detailed testing procedures
- `../MCP_STATUS.md` - Current implementation status
- `../COMPARISON_RESULTS.md` - Previous comparison test results

