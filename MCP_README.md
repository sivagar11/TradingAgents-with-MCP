# MCP Integration for TradingAgents 🚀

## 🎯 Overview

This is a **Proof of Concept** implementation of **Model Context Protocol (MCP)** for TradingAgents. The system now supports **two modes**:

1. **DIRECT MODE** (Original): Direct tool calls to data sources
2. **MCP MODE** (New): Tool calls routed through MCP protocol

This enables **A/B comparison** for research purposes!

## 📊 Architecture Comparison

### DIRECT MODE (Original)
```
┌─────────┐    ┌──────────┐    ┌────────────┐    ┌─────────────┐
│   LLM   │ -> │ Tool Call│ -> │  ToolNode  │ -> │ Data Source │
│ (Agent) │    │          │    │ (LangGraph)│    │ (yfinance)  │
└─────────┘    └──────────┘    └────────────┘    └─────────────┘
```

### MCP MODE (New)
```
┌─────────┐    ┌──────────┐    ┌─────────────┐    ┌────────────┐    ┌─────────────┐
│   LLM   │ -> │ Tool Call│ -> │ MCP Client  │ -> │ MCP Server │ -> │ Data Source │
│ (Agent) │    │          │    │             │    │            │    │ (yfinance)  │
└─────────┘    └──────────┘    └─────────────┘    └────────────┘    └─────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Install MCP dependencies
pip install -r requirements-mcp.txt

# Or manually
pip install mcp fastmcp
```

### Running with MCP

#### Option 1: Configuration File

Edit `tradingagents/default_config.py`:

```python
DEFAULT_CONFIG = {
    # ... other config ...
    "use_mcp": True,  # Enable MCP mode
}
```

#### Option 2: Programmatic

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

config = {
    "use_mcp": True,  # Enable MCP
    # ... other config ...
}

graph = TradingAgentsGraph(
    selected_analysts=["market"],
    config=config
)

result, signal = graph.propagate("AAPL", "2024-11-01")
```

### Running Comparison Test

```bash
python test_mcp_comparison.py
```

This will run the same analysis twice (DIRECT and MCP) and compare:
- Execution time
- Latency overhead
- Result consistency

## 📁 Project Structure

```
tradingagents/
├── mcp_servers/              # MCP Servers
│   └── stock_server/
│       ├── __init__.py
│       └── server.py         # Stock data MCP server
├── mcp_client/               # MCP Client
│   ├── __init__.py
│   └── client.py             # MCP client and executor
├── graph/
│   └── trading_graph.py      # Updated to support both modes
└── default_config.py         # Added MCP configuration
```

## 🔧 Current Implementation Status

### ✅ Implemented

- **Stock MCP Server**: Exposes `get_stock_data` and `get_indicators`
- **MCP Client**: Connects to and manages MCP servers
- **MCPToolExecutor**: Routes tool calls through MCP
- **Hybrid Mode**: Switch between DIRECT and MCP via config
- **Comparison Test**: A/B testing script

### 🚧 To-Do (Future Work)

- **News MCP Server**: For `get_news`, `get_global_news`
- **Fundamentals MCP Server**: For `get_fundamentals`, `get_balance_sheet`, etc.
- **Social MCP Server**: For social sentiment analysis
- **Performance Optimization**: Reduce MCP overhead
- **Error Handling**: Better fallback mechanisms
- **Caching**: Cache MCP responses for repeated calls

## 🧪 Testing

### Test Stock MCP Server Standalone

```bash
# Start the server
python tradingagents/mcp_servers/stock_server/server.py

# In another terminal, test with MCP inspector
npx @modelcontextprotocol/inspector python tradingagents/mcp_servers/stock_server/server.py
```

### Test with Market Analyst Only

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph

config = {
    "use_mcp": True,
    "quick_think_llm": "gpt-4o-mini",
    "deep_think_llm": "gpt-4o-mini",
}

graph = TradingAgentsGraph(
    selected_analysts=["market"],  # Just market for quick test
    config=config
)

result, signal = graph.propagate("NVDA", "2024-11-01")
print(result["market_report"])
```

## 📊 Performance Expectations

### Theoretical Overhead

MCP adds Inter-Process Communication (IPC) overhead:
- **Per tool call**: ~10-50ms additional latency
- **Full analysis**: ~0.5-1 second total overhead
- **Percentage**: ~5-15% on a 3-minute analysis

### Measured Performance (from tests)

*Run `test_mcp_comparison.py` to measure on your system*

Example results:
```
Direct Mode:  52.3s
MCP Mode:     54.8s
Overhead:     +2.5s (+4.8%)
```

## 🔬 Research Value

### For Your Paper

This implementation enables several research contributions:

1. **Novel Architecture**: First trading agent system using MCP
2. **Performance Benchmarking**: Quantify MCP overhead in financial AI
3. **Standardization Benefits**: Demonstrate MCP in production-like system
4. **Modularity Analysis**: Compare tool coupling before/after MCP
5. **Reusability**: MCP servers can be used by other systems

### Metrics to Measure

- **Latency**: Compare execution times
- **Reliability**: Error rates in both modes
- **Scalability**: How does MCP handle multiple concurrent requests?
- **Maintainability**: Lines of code, coupling metrics
- **Reusability**: Can MCP servers be used in other projects?

## 🛠️ Configuration Reference

### MCP Configuration in `default_config.py`

```python
DEFAULT_CONFIG = {
    # ... other config ...
    
    # Toggle MCP mode
    "use_mcp": False,  # Set to True to enable MCP
    
    # MCP server configurations
    "mcp_servers": {
        "stock": {
            "command": "python",
            "args": ["tradingagents/mcp_servers/stock_server/server.py"]
        },
        # Add more servers here as you implement them
    },
    
    # Map tools to MCP servers
    "mcp_tool_mapping": {
        "get_stock_data": "stock",
        "get_indicators": "stock",
        # Add more mappings here
    },
}
```

## 🐛 Troubleshooting

### MCP Server Won't Start

**Error**: `ModuleNotFoundError: No module named 'mcp'`

**Solution**:
```bash
pip install mcp fastmcp
```

### MCP Client Connection Failed

**Error**: `MCP: Failed to connect to 'stock' server`

**Solution**:
1. Check server path in config
2. Test server standalone: `python tradingagents/mcp_servers/stock_server/server.py`
3. Check Python path and virtual environment

### Tools Not Available in MCP

**Error**: `Tool 'get_news' not available in MCP`

**Solution**:
- This tool hasn't been migrated to MCP yet (only `stock` server is implemented in POC)
- Either add the tool to an MCP server, or use DIRECT mode for now

## 📝 Next Steps

### For Full Implementation

1. **Implement Remaining Servers** (2-3 hours each):
   - News MCP Server
   - Fundamentals MCP Server
   - Social MCP Server

2. **Performance Optimization** (1-2 hours):
   - Add connection pooling
   - Implement response caching
   - Batch tool calls

3. **Error Handling** (1 hour):
   - Graceful fallback to DIRECT mode if MCP fails
   - Better error messages
   - Retry logic

4. **Testing** (2-3 hours):
   - Unit tests for MCP servers
   - Integration tests for full workflow
   - Performance benchmarks

### For Research Paper

1. **Run Comprehensive Benchmarks**:
   - 100+ analyses with both modes
   - Measure latency, reliability, consistency
   - Statistical analysis

2. **Document Architecture**:
   - Detailed system diagrams
   - Data flow visualizations
   - Comparison tables

3. **Write Evaluation Section**:
   - Performance results
   - Trade-off analysis
   - Future work and limitations

## 💡 Tips

- **Start Small**: Test with one analyst before full system
- **Monitor Logs**: Look for "MCP:" prefix in console output
- **Compare Results**: Always verify MCP gives same results as DIRECT
- **Measure Everything**: Use `test_mcp_comparison.py` frequently

## 📚 References

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/anthropics/python-sdk)
- [FastMCP Library](https://github.com/jlowin/fastmcp)

---

**Questions?** Check the main `MCP_INTEGRATION_PLAN.md` for detailed implementation strategy.

