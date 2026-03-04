

# TradingAgents with Model Context Protocol (MCP)

> 🚀 **MCP-Enhanced TradingAgents** — This is an enhanced implementation of the [TradingAgents](https://github.com/TauricResearch/TradingAgents) multi-agent LLM trading framework with full **Model Context Protocol (MCP)** integration.

## What's New in This Version

This repository extends the original TradingAgents framework with MCP support, providing:

- ✅ **Full MCP Integration**: Protocol-based tool execution using MCP SDK
- ✅ **Four Specialized MCP Servers**: Stock, News, Fundamentals, and Social Media data
- ✅ **Dual-Mode Operation**: Toggle between Direct tool calls and MCP protocol
- ✅ **Async Architecture**: Fully async implementation for better performance
- ✅ **Backward Compatible**: Works exactly like the original when MCP is disabled
- ✅ **Enhanced Interfaces**: CLI, REST API, WebSocket streaming, and Next.js frontend

<div align="center">

🚀 [Overview](#overview) | 🔧 [Installation](#installation) | 📖 [MCP Architecture](#mcp-architecture) | 💻 [Usage](#usage) | 🎯 [Dual Mode](#dual-mode-operation) | 📚 [Documentation](#documentation)

</div>

---

## Overview

### What is TradingAgents?

TradingAgents is a multi-agent LLM framework that mirrors real-world trading firms. It deploys specialized AI agents (analysts, researchers, traders, risk managers) that collaboratively analyze market conditions and make informed trading decisions through structured workflows.

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

### What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io) is an open protocol that standardizes how applications provide context to LLMs. Instead of direct function calls, tools are exposed through standardized MCP servers, enabling:

- **Modularity**: Each data source (stock, news, fundamentals) runs as an independent MCP server
- **Standardization**: All tools follow the MCP protocol specification
- **Extensibility**: Easy to add new servers without modifying core code
- **Separation of Concerns**: Data retrieval logic isolated from agent logic

### Why MCP Integration?

This implementation adds MCP support to enable:

1. **Research Comparison**: Compare performance between direct tool calls and MCP protocol
2. **Modular Architecture**: Cleanly separate data providers from agent logic
3. **Protocol Standardization**: Use industry-standard MCP for tool execution
4. **Future Extensibility**: Easily integrate with other MCP-compatible systems

> **Disclaimer**: TradingAgents is designed for research purposes. Trading performance varies based on many factors including LLM choice, market conditions, and data quality. [Not intended as financial advice.](https://tauric.ai/disclaimer/)

---

## Agent Team Structure

The framework uses specialized agents organized into teams:

### 1. Analyst Team
- **Market Analyst**: Technical indicators (RSI, MACD, Bollinger Bands, moving averages)
- **News Analyst**: Global news and macroeconomic events
- **Fundamentals Analyst**: Financial statements, balance sheets, company health metrics
- **Social Media Analyst**: Sentiment analysis from social media and Reddit

<p align="center">
  <img src="assets/analyst.png" width="100%">
</p>

### 2. Research Team
- **Bull Researcher**: Argues for bullish positions
- **Bear Researcher**: Argues for bearish positions
- **Research Manager**: Judges the debate and synthesizes consensus

<p align="center">
  <img src="assets/researcher.png" width="70%">
</p>

### 3. Trading Team
- **Trader**: Creates trading plans based on research consensus

<p align="center">
  <img src="assets/trader.png" width="70%">
</p>

### 4. Risk Management Team
- **Aggressive Debator**: Advocates for high-risk/high-reward positions
- **Conservative Debator**: Advocates for low-risk positions
- **Neutral Debator**: Provides balanced risk perspective
- **Risk Manager**: Final risk assessment and approval

<p align="center">
  <img src="assets/risk.png" width="70%">
</p>

---

## MCP Architecture

### MCP Servers

This implementation includes four specialized MCP servers:

```
tradingagents/mcp_servers/
├── stock_server/          # Stock prices and technical indicators
├── news_server/           # News and insider data
├── fundamentals_server/   # Financial statements and metrics
└── social_server/         # Social media sentiment
```

Each server:
- Runs as an independent stdio-based MCP server
- Exposes tools via JSON-RPC protocol
- Uses FastMCP framework for rapid development
- Supports the same data vendors as direct mode

### MCP Client

The MCP client (`tradingagents/mcp_client/`) manages:
- Connection lifecycle to all MCP servers
- Tool call routing through MCP protocol
- Async context management with AsyncExitStack
- Clean shutdown and error handling

### Workflow Architecture

```
User Input (CLI/API/Frontend)
    ↓
TradingAgentsGraph.propagate()
    ↓
LangGraph Multi-Agent Workflow
    ↓
┌─────────────────┬─────────────────┐
│   DIRECT MODE   │    MCP MODE     │
├─────────────────┼─────────────────┤
│  LangChain      │  MCPToolExecutor│
│  ToolNode       │       ↓         │
│      ↓          │  MCP Client     │
│  Direct Call    │       ↓         │
│      ↓          │  MCP Servers    │
│  Data Vendor    │  (stdio/JSON-RPC)│
│                 │       ↓         │
│                 │  Data Vendor    │
└─────────────────┴─────────────────┘
    ↓
Agent receives data and continues workflow
```

---

## Installation

### Prerequisites

- Python 3.10+ (Python 3.13 recommended)
- OpenAI API key
- Alpha Vantage API key (free tier available)

### Quick Start

**1. Clone the repository:**

```bash
git clone https://github.com/sivagar11/Trading-Agents.git
cd Trading-Agents
```

**2. Create virtual environment:**

```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

**3. Install dependencies:**

```bash
# Core dependencies (required)
pip install -r requirements.txt

# MCP dependencies (optional, only if using MCP mode)
pip install -r requirements-mcp.txt
```

**4. Set up API keys:**

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=your_openai_key_here
# ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

Or export them directly:

```bash
export OPENAI_API_KEY="your_openai_key"
export ALPHA_VANTAGE_API_KEY="your_alpha_vantage_key"
```

> **Note**: Get a free Alpha Vantage API key [here](https://www.alphavantage.co/support/#api-key). TradingAgents users get increased rate limits (60 requests/minute, no daily limit) through Alpha Vantage's open-source support program.

---

## Usage

### CLI Usage

Run the interactive CLI:

```bash
python -m cli.main
```

The CLI provides an interactive interface to:
- Select stock ticker and analysis date
- Choose which analysts to include
- Select LLM models (OpenAI, Anthropic, Google)
- Enable/disable MCP mode
- View real-time progress and reports

<p align="center">
  <img src="assets/cli/cli_init.png" width="100%">
</p>

<p align="center">
  <img src="assets/cli/cli_news.png" width="100%">
</p>

<p align="center">
  <img src="assets/cli/cli_transaction.png" width="100%">
</p>

### Python Usage (Direct Mode)

```python
import asyncio
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

async def main():
    # Use default configuration (Direct mode)
    config = DEFAULT_CONFIG.copy()
    ta = TradingAgentsGraph(debug=True, config=config)

    graph_result, decision = await ta.propagate("NVDA", "2024-05-10")
    print(f"Decision: {decision}")

asyncio.run(main())
```

> **Tip:** `TradingAgentsGraph.propagate()` is asynchronous in both direct and MCP modes, so wrap it with `asyncio.run` (or your own event loop) even when MCP is disabled.

### Python Usage (MCP Mode)

```python
import asyncio
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

async def main():
    # Enable MCP mode
    config = DEFAULT_CONFIG.copy()
    config["use_mcp"] = True
    
    # Create graph with async initialization
    ta = await TradingAgentsGraph.create(debug=True, config=config)
    
    try:
        # Run analysis
        graph_result, decision = await ta.propagate("NVDA", "2024-05-10")
        print(f"Decision: {decision}")
    finally:
        # Clean up MCP connections
        await ta.close()

asyncio.run(main())
```

### Custom Configuration

```python
import asyncio
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

async def main():
    config = DEFAULT_CONFIG.copy()

    # LLM Configuration
    config["deep_think_llm"] = "gpt-4o"           # Deep reasoning model
    config["quick_think_llm"] = "gpt-4o-mini"     # Fast execution model
    config["max_debate_rounds"] = 2               # Debate iterations

    # MCP Configuration
    config["use_mcp"] = True                      # Enable MCP mode

    # Data Vendor Configuration
    config["data_vendors"] = {
        "core_stock_apis": "yfinance",            # yfinance, alpha_vantage, local
        "technical_indicators": "yfinance",       # yfinance, alpha_vantage, local
        "fundamental_data": "alpha_vantage",      # openai, alpha_vantage, local
        "news_data": "alpha_vantage",             # openai, alpha_vantage, google, local
    }

    if config["use_mcp"]:
        ta = await TradingAgentsGraph.create(debug=True, config=config)
    else:
        ta = TradingAgentsGraph(debug=True, config=config)

    try:
        graph_result, decision = await ta.propagate("NVDA", "2024-05-10")
        print(decision)
    finally:
        await ta.close()

asyncio.run(main())
```

### API & Frontend

**Start backend API:**

```bash
python -m api.main
# API runs on http://localhost:8000
```

**Start Next.js frontend:**

```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

**Start both together:**

```bash
./start.sh
```

The API provides:
- REST endpoints: `/api/analyze`, `/api/health`, `/api/models`
- WebSocket streaming: `/ws/analyze` for real-time updates
- CORS enabled for local development

---

## Dual Mode Operation

### Direct Mode (Default)

Traditional LangChain ToolNode execution:

- **Pros**: Simpler, faster startup, no additional processes
- **Cons**: Tightly coupled, harder to extend with new data sources
- **Use When**: Running quick analyses, testing, or when MCP overhead isn't needed

```python
config = DEFAULT_CONFIG.copy()
config["use_mcp"] = False  # Direct mode (default)
ta = TradingAgentsGraph(debug=True, config=config)
```

### MCP Mode

Protocol-based execution through MCP servers:

- **Pros**: Modular, standardized, easy to extend, better separation of concerns
- **Cons**: Slight overhead (~3-5%), requires async pattern, more complex setup
- **Use When**: Need modularity, extending with new servers, or comparing protocols

```python
config = DEFAULT_CONFIG.copy()
config["use_mcp"] = True  # MCP mode
ta = await TradingAgentsGraph.create(debug=True, config=config)
```

### Performance Comparison

Based on testing:
- **Direct Mode**: ~135-140s for full analysis
- **MCP Mode**: ~140-145s for full analysis
- **Overhead**: ~3-5% (mostly from server startup and JSON-RPC serialization)

The overhead is minimal and acceptable for most use cases, especially given the architectural benefits.

---

## MCP Server Details

### Stock Server

**Tools:**
- `get_stock_data`: Fetch historical stock prices
- `get_indicators`: Calculate technical indicators (RSI, MACD, Bollinger Bands, etc.)

**Location:** `tradingagents/mcp_servers/stock_server/server.py`

### News Server

**Tools:**
- `get_news`: Company-specific news
- `get_global_news`: Global market news
- `get_insider_sentiment`: Insider trading sentiment
- `get_insider_transactions`: Insider trading transactions

**Location:** `tradingagents/mcp_servers/news_server/server.py`

### Fundamentals Server

**Tools:**
- `get_fundamentals`: Overview of company fundamentals
- `get_balance_sheet`: Balance sheet data
- `get_income_statement`: Income statement data
- `get_cashflow`: Cash flow statement data

**Location:** `tradingagents/mcp_servers/fundamentals_server/server.py`

### Social Server

**Tools:**
- Social sentiment analysis tools (Reddit, Twitter sentiment)

**Location:** `tradingagents/mcp_servers/social_server/server.py`

---

## Testing

The repository includes comprehensive tests:

```bash
# Test MCP integration
python tests/mcp/test_mcp_simple.py

# Test individual analysts with MCP
python tests/mcp/individual/test_mcp_news.py
python tests/mcp/individual/test_mcp_fundamentals.py
python tests/mcp/individual/test_mcp_social.py
python tests/mcp/individual/test_mcp_all_analysts.py

# Test MCP servers standalone
python tests/mcp/server/test_mcp_server_standalone.py

# Run example
python tests/examples/main.py
```

See `tests/README.md` for detailed testing documentation.

---

## Documentation

- **[MCP_README.md](MCP_README.md)**: Quick start guide for MCP features
- **[MCP_INTEGRATION_GUIDE.md](MCP_INTEGRATION_GUIDE.md)**: Comprehensive integration guide with architecture details, troubleshooting, and examples

---

## Configuration Reference

All configuration options are in `tradingagents/default_config.py`:

```python
DEFAULT_CONFIG = {
    # LLM Configuration
    "deep_think_llm": "gpt-4o",              # Model for deep reasoning
    "quick_think_llm": "gpt-4o-mini",        # Model for quick tasks
    "max_debate_rounds": 2,                   # Debate iterations
    
    # MCP Configuration
    "use_mcp": False,                         # Enable/disable MCP mode
    "mcp_servers": {                          # MCP server configurations
        "stock": {...},
        "news": {...},
        "fundamentals": {...},
        "social": {...}
    },
    
    # Data Vendors
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "alpha_vantage",
        "news_data": "alpha_vantage",
    },
    
    # Agent Configuration
    "enable_reflection": True,                # Post-trade analysis
    "enable_memory": True,                    # Learning from past trades
}
```

### Configuring paths

The default configuration now resolves every path relative to the repository, so it works on any machine out-of-the-box. You can still override them with environment variables:

| Variable | Purpose | Default |
| --- | --- | --- |
| `TRADINGAGENTS_DATA_DIR` | Location of cached market/news/fundamental datasets (used by `dataflows/local.py`) | `<repo>/tradingagents/data` |
| `TRADINGAGENTS_DATA_CACHE_DIR` | Cache directory for downloaded vendor payloads | `<repo>/tradingagents/dataflows/data_cache` |
| `TRADINGAGENTS_RESULTS_DIR` | Destination for logs + evaluation outputs | `<repo>/tradingagents/results` |
| `TRADINGAGENTS_PYTHON` | Interpreter for starting MCP stdio servers | current Python executable |

Example:

```bash
export TRADINGAGENTS_DATA_DIR=$HOME/trading-data
export TRADINGAGENTS_PYTHON=$(pyenv which python)
```

Set these before running the CLI, API, or tests to point at your own datasets or virtual environments.

---

## Project Structure

```
Trading-Agents/
├── tradingagents/              # Core package
│   ├── agents/                # Agent implementations
│   │   ├── analysts/         # Market, News, Fundamentals, Social analysts
│   │   ├── researchers/      # Bull, Bear researchers
│   │   ├── trader/           # Trader agent
│   │   ├── risk_mgmt/        # Risk management agents
│   │   └── managers/         # Research and Risk managers
│   ├── graph/                 # LangGraph orchestration
│   │   ├── trading_graph.py  # Main graph implementation
│   │   ├── setup.py          # Graph construction
│   │   └── ...               # State, routing, signal processing
│   ├── dataflows/             # Data vendor abstraction
│   ├── mcp_servers/           # MCP server implementations
│   │   ├── stock_server/
│   │   ├── news_server/
│   │   ├── fundamentals_server/
│   │   └── social_server/
│   ├── mcp_client/            # MCP client implementation
│   └── default_config.py      # Configuration
├── api/                        # FastAPI backend
├── cli/                        # Rich CLI interface
├── frontend/                   # Next.js web frontend
├── tests/                      # Test suite
│   ├── mcp/                   # MCP tests
│   ├── evaluation/            # Evaluation tests
│   └── examples/              # Example scripts
├── requirements.txt            # Core dependencies
├── requirements-mcp.txt        # MCP dependencies
└── README.md                   # This file
```

---

## Contributing

Contributions are welcome! This is an experimental fork focused on MCP integration. Feel free to:

- Report bugs or issues
- Suggest improvements to MCP integration
- Add new MCP servers
- Improve documentation
- Submit pull requests

For the original TradingAgents community, join [Tauric Research](https://tauric.ai/).

---

## Attribution

This repository is based on the excellent work by the TauricResearch team:

**Original Repository:** [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)

**Paper:** [TradingAgents: Multi-Agents LLM Financial Trading Framework (arXiv:2412.20138)](https://arxiv.org/abs/2412.20138)

**Authors:** Yijia Xiao, Edward Sun, Di Luo, Wei Wang

---

## Citation

If you use this MCP-enhanced version or the original TradingAgents framework, please cite:

```bibtex
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```

---

## License

This project maintains the same license as the original TradingAgents repository. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **TauricResearch** for the original TradingAgents framework
- **Alpha Vantage** for providing robust API support
- **Anthropic** for the Model Context Protocol specification
- **FastMCP** for the rapid MCP server development framework

---
