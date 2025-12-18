# MCP Integration Guide for TradingAgents

## Overview

This guide documents how Model Context Protocol (MCP) was successfully integrated into the TradingAgents system. Follow this guide to implement MCP for additional agents (News, Fundamentals, Social).

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Key Components](#key-components)
3. [Integration Steps](#integration-steps)
4. [Testing and Verification](#testing-and-verification)
5. [Implementing New MCP Servers](#implementing-new-mcp-servers)

---

## Architecture Overview

### Hybrid Architecture

The system now supports **two modes** for tool execution:

```
┌─────────────────────────────────────────────────────────┐
│                    TradingAgentsGraph                    │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Configuration (use_mcp flag)          │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                                │
│           ┌─────────────┴─────────────┐                │
│           │                           │                │
│      use_mcp=False              use_mcp=True           │
│           │                           │                │
│           ▼                           ▼                │
│  ┌─────────────────┐         ┌─────────────────┐      │
│  │  Direct Tool    │         │  MCPToolExecutor│      │
│  │  Calling        │         │  (via MCP)      │      │
│  │  (ToolNode)     │         │                 │      │
│  └─────────────────┘         └─────────────────┘      │
│           │                           │                │
│           ▼                           ▼                │
│  ┌─────────────────┐         ┌─────────────────┐      │
│  │  agent_utils/   │         │  MCPClient      │      │
│  │  core_stock_    │         │  (stdio)        │      │
│  │  tools.py       │         └────────┬────────┘      │
│  └─────────────────┘                  │                │
│           │                           │                │
│           │                           ▼                │
│           │                  ┌─────────────────┐      │
│           │                  │  MCP Server     │      │
│           │                  │  (FastMCP)      │      │
│           │                  │  - Stock Server │      │
│           │                  └────────┬────────┘      │
│           │                           │                │
│           └───────────┬───────────────┘                │
│                       ▼                                │
│              ┌─────────────────┐                       │
│              │  Data Vendors   │                       │
│              │  (yFinance, etc)│                       │
│              └─────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

### Why Hybrid?

- **Research**: Compare MCP overhead vs direct calling
- **Flexibility**: Switch between modes with a config flag
- **Migration**: Gradual rollout of MCP across agents

---

## Key Components

### 1. Configuration Toggle (`default_config.py`)

```python
DEFAULT_CONFIG = {
    # ... other configs ...
    
    # MCP INTEGRATION
    "use_mcp": False,  # Toggle between direct and MCP modes
    
    # MCP Server Configurations
    "mcp_servers": {
        "stock": {
            "command": "python",
            "args": ["tradingagents/mcp_servers/stock_server/server.py"]
        },
        # Add more servers here...
    }
}
```

### 2. MCP Server (`tradingagents/mcp_servers/stock_server/server.py`)

**Key Requirements:**

1. **Redirect stdout to stderr** (CRITICAL for stdio transport)
2. **Use FastMCP** for simplicity
3. **Match original tool signatures** exactly
4. **Suppress vendor stdout** to prevent JSON-RPC corruption

```python
import sys
from pathlib import Path

# CRITICAL: Redirect stdout to stderr BEFORE imports
# This prevents FastMCP banner from corrupting JSON-RPC
_original_stdout = sys.stdout
sys.stdout = sys.stderr

# Add project root to path for imports
server_dir = Path(__file__).parent
project_root = server_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastmcp import FastMCP
from tradingagents.dataflows.interface import route_to_vendor

# Create FastMCP server
mcp = FastMCP("Stock Data Server")

# Decorator to suppress stdout during vendor calls
def suppress_stdout(func):
    def wrapper(*args, **kwargs):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            return func(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
    return wrapper

# Define tools with EXACT same signatures as original
@mcp.tool()
def get_stock_data(symbol: str, start_date: str, end_date: str) -> str:
    """Get historical stock price data."""
    @suppress_stdout
    def call_vendor():
        return route_to_vendor("get_stock_data", symbol, start_date, end_date)
    return call_vendor()

@mcp.tool()
def get_indicators(
    symbol: str,
    indicator: str,
    curr_date: str,
    look_back_days: int = 30
) -> str:
    """Get technical indicators."""
    @suppress_stdout
    def call_vendor():
        return route_to_vendor("get_indicators", symbol, indicator, curr_date, look_back_days)
    return call_vendor()

if __name__ == "__main__":
    # Restore stdout for MCP JSON-RPC communication
    sys.stdout = _original_stdout
    mcp.run(transport="stdio")
```

**Critical Points:**
- ⚠️ **NEVER write to stdout** in MCP stdio servers
- ✅ Tool signatures must **exactly match** original functions
- ✅ Use `suppress_stdout` for vendor calls that print

### 3. MCP Client (`tradingagents/mcp_client/client.py`)

**Key Requirements:**

1. **Use AsyncExitStack** for proper async context management
2. **Store sessions**, not context managers
3. **Proper cleanup** via `close_all()`

```python
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.server_configs: Dict[str, StdioServerParameters] = {}
        self._initialized = False
        self._exit_stack: Optional[AsyncExitStack] = None
    
    async def connect_server(self, name: str, config: StdioServerParameters, timeout: int = 60):
        """Connect to an MCP server."""
        # Initialize exit stack if needed
        if self._exit_stack is None:
            self._exit_stack = AsyncExitStack()
            await self._exit_stack.__aenter__()
        
        async with asyncio.timeout(timeout):
            # Enter stdio client context via exit stack
            read_stream, write_stream = await self._exit_stack.enter_async_context(
                stdio_client(config)
            )
            
            # Enter session context via exit stack
            session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            
            await session.initialize()
            self.sessions[name] = session
    
    async def close_all(self):
        """Close all server connections."""
        if self._exit_stack:
            await self._exit_stack.__aexit__(None, None, None)
        self.sessions.clear()
        self._exit_stack = None
```

**Critical Points:**
- ✅ **AsyncExitStack** prevents "exit cancel scope in different task" errors
- ✅ Enter contexts via `enter_async_context()`, not manual `__aenter__`
- ✅ Single exit stack manages all connections

### 4. MCP Tool Executor (`tradingagents/mcp_client/client.py`)

**Key Requirements:**

1. **Async `__call__`** to work with LangGraph's event loop
2. **Map tools to servers**

```python
class MCPToolExecutor:
    def __init__(self, mcp_client: MCPClient, tool_to_server_mapping: Dict[str, str]):
        self.client = mcp_client
        self.mapping = tool_to_server_mapping
    
    async def __call__(self, state):
        """Execute tool calls (async for LangGraph compatibility)."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return {"messages": []}
        
        # Execute tool calls asynchronously
        tool_results = await self.execute_tool_calls(last_message.tool_calls)
        return {"messages": tool_results}
```

**Critical Points:**
- ✅ `__call__` is **async** (LangGraph supports async nodes)
- ✅ No `asyncio.run()` inside `__call__` (would cause nested event loop error)

### 5. TradingAgentsGraph Integration

**Key Requirements:**

1. **Async factory method** for MCP initialization
2. **Conditional tool nodes** based on `use_mcp` flag
3. **Async `propagate`** method
4. **Proper cleanup** method

```python
class TradingAgentsGraph:
    def __init__(self, selected_analysts=None, debug=False, config=None, mcp_client=None):
        """Synchronous init (no async operations)."""
        self.config = config or DEFAULT_CONFIG.copy()
        self.selected_analysts = selected_analysts or ["market", "social", "news", "fundamentals"]
        self.debug = debug
        self.mcp_client = mcp_client
        
        # Initialize all components synchronously
        self._initialize_sync()
        
        # Create tool nodes (MCP or direct based on config)
        self.tool_nodes = self._create_tool_nodes()
        
        # Set up the graph
        self.graph = self.graph_setup.setup_graph(self.selected_analysts)
    
    @classmethod
    async def create(cls, selected_analysts=None, debug=False, config=None):
        """Async factory method for MCP initialization."""
        # Create instance with sync init
        instance = cls(selected_analysts, debug, config, mcp_client=None)
        
        # Initialize MCP if enabled
        if instance.config.get("use_mcp", False):
            instance.mcp_client = await instance._initialize_mcp_async()
            # Recreate tool nodes with MCP
            instance.tool_nodes = instance._create_tool_nodes()
        
        return instance
    
    async def _initialize_mcp_async(self) -> MCPClient:
        """Initialize MCP client and connect to servers."""
        client = MCPClient()
        for name, config in self.config.get("mcp_servers", {}).items():
            client.register_server(name, config["command"], config.get("args", []))
        await client.connect_all()
        return client
    
    def _create_tool_nodes(self):
        """Create tool nodes (MCP or direct based on config)."""
        if self.config.get("use_mcp", False) and self.mcp_client:
            # MCP mode: Use MCPToolExecutor
            return {
                "market": MCPToolExecutor(
                    self.mcp_client,
                    {"get_stock_data": "stock", "get_indicators": "stock"}
                ),
                # Add more analysts...
            }
        else:
            # Direct mode: Use traditional ToolNode
            return {
                "market": ToolNode([get_stock_data, get_indicators]),
                # Add more analysts...
            }
    
    async def propagate(self, company_name, trade_date):
        """Run analysis (async for MCP support)."""
        init_agent_state = self.propagator.create_initial_state(company_name, trade_date)
        args = self.propagator.get_graph_args()
        
        # Use async graph methods
        final_state = await self.graph.ainvoke(init_agent_state, **args)
        return final_state, self.process_signal(final_state["final_trade_decision"])
    
    async def close(self):
        """Close MCP connections (if any)."""
        if self.mcp_client is not None:
            await self.mcp_client.close_all()
            self.mcp_client = None
```

**Critical Points:**
- ✅ **Async factory method** (`create`) handles MCP initialization
- ✅ **Sync `__init__`** for non-MCP usage (backward compatible)
- ✅ **`propagate` is async**, uses `ainvoke` instead of `invoke`
- ✅ **`close()` method** for cleanup

---

## Integration Steps

### Step 1: Create MCP Server

1. Create directory: `tradingagents/mcp_servers/{analyst_name}_server/`
2. Create `__init__.py` (empty)
3. Create `server.py`:
   - Redirect stdout to stderr
   - Import FastMCP and tools
   - Define tools matching original signatures
   - Suppress stdout in vendor calls

### Step 2: Register Server in Config

Update `default_config.py`:

```python
"mcp_servers": {
    "stock": {
        "command": "python",
        "args": ["tradingagents/mcp_servers/stock_server/server.py"]
    },
    "news": {  # NEW
        "command": "python",
        "args": ["tradingagents/mcp_servers/news_server/server.py"]
    }
}
```

### Step 3: Update Tool Mapping

In `TradingAgentsGraph._create_tool_nodes()`:

```python
if self.config.get("use_mcp", False) and self.mcp_client:
    return {
        "market": MCPToolExecutor(
            self.mcp_client,
            {"get_stock_data": "stock", "get_indicators": "stock"}
        ),
        "news": MCPToolExecutor(  # NEW
            self.mcp_client,
            {"get_news": "news", "get_global_news": "news"}
        ),
    }
```

### Step 4: Test

Create a test script:

```python
async def test_analyst():
    config = DEFAULT_CONFIG.copy()
    config["use_mcp"] = True
    
    try:
        graph = await TradingAgentsGraph.create(
            selected_analysts=["news"],
            config=config
        )
        final_state, signal = await graph.propagate("NVDA", "2024-11-01")
        print("✅ Analysis completed")
    finally:
        await graph.close()

asyncio.run(test_analyst())
```

---

## Testing and Verification

### Unit Test: MCP Server Standalone

Test the server independently:

```python
# test_news_server_standalone.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_server():
    params = StdioServerParameters(
        command="python",
        args=["tradingagents/mcp_servers/news_server/server.py"]
    )
    
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Test tool call
            result = await session.call_tool("get_news", {"symbol": "NVDA", "curr_date": "2024-11-01"})
            print(f"Result: {result.content[0].text[:200]}...")

asyncio.run(test_server())
```

### Integration Test: Full Analysis

```python
# test_mcp_simple.py (already exists)
async def run_test():
    graph = None
    try:
        graph = await TradingAgentsGraph.create(
            selected_analysts=["market", "news"],
            config={"use_mcp": True, ...}
        )
        final_state, signal = await graph.propagate("NVDA", "2024-11-01")
        return final_state
    finally:
        if graph:
            await graph.close()

asyncio.run(run_test())
```

### Comparison Test: MCP vs Direct

```python
# test_mcp_comparison.py
async def compare_modes():
    results = {}
    
    # Test DIRECT mode
    config_direct = DEFAULT_CONFIG.copy()
    config_direct["use_mcp"] = False
    graph_direct = TradingAgentsGraph(selected_analysts=["market"], config=config_direct)
    start = time.time()
    state_direct, _ = graph_direct.propagate("NVDA", "2024-11-01")
    results["direct"] = {"time": time.time() - start, "state": state_direct}
    
    # Test MCP mode
    config_mcp = DEFAULT_CONFIG.copy()
    config_mcp["use_mcp"] = True
    graph_mcp = await TradingAgentsGraph.create(selected_analysts=["market"], config=config_mcp)
    try:
        start = time.time()
        state_mcp, _ = await graph_mcp.propagate("NVDA", "2024-11-01")
        results["mcp"] = {"time": time.time() - start, "state": state_mcp}
    finally:
        await graph_mcp.close()
    
    # Compare
    print(f"Direct: {results['direct']['time']:.2f}s")
    print(f"MCP:    {results['mcp']['time']:.2f}s")
    print(f"Overhead: {results['mcp']['time'] - results['direct']['time']:.2f}s")

asyncio.run(compare_modes())
```

---

## Implementing New MCP Servers

### Template for News Server

```python
# tradingagents/mcp_servers/news_server/server.py
import sys
from pathlib import Path
from io import StringIO

# Redirect stdout to stderr BEFORE imports
_original_stdout = sys.stdout
sys.stdout = sys.stderr

# Add project root to path
server_dir = Path(__file__).parent
project_root = server_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastmcp import FastMCP
from tradingagents.dataflows.interface import route_to_vendor

mcp = FastMCP("News Data Server")

def suppress_stdout(func):
    def wrapper(*args, **kwargs):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            return func(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
    return wrapper

@mcp.tool()
def get_news(symbol: str, curr_date: str) -> str:
    """Get news for a stock."""
    @suppress_stdout
    def call_vendor():
        return route_to_vendor("get_news", symbol, curr_date)
    return call_vendor()

@mcp.tool()
def get_global_news(symbol: str, curr_date: str) -> str:
    """Get global news."""
    @suppress_stdout
    def call_vendor():
        return route_to_vendor("get_global_news", symbol, curr_date)
    return call_vendor()

if __name__ == "__main__":
    sys.stdout = _original_stdout
    mcp.run(transport="stdio")
```

### Checklist for New Servers

- [ ] Redirect stdout to stderr before all imports
- [ ] Add project root to sys.path
- [ ] Use FastMCP for server creation
- [ ] Define tools with exact same signatures as originals
- [ ] Use `suppress_stdout` for vendor calls
- [ ] Restore stdout before `mcp.run()`
- [ ] Test standalone with simple client
- [ ] Update `default_config.py` with server config
- [ ] Update `TradingAgentsGraph._create_tool_nodes()`
- [ ] Run integration test

---

## Common Issues and Solutions

### Issue 1: "exit cancel scope in different task"

**Cause:** AsyncExitStack not properly closed before `asyncio.run()` exits

**Solution:** Use `try/finally` block:

```python
async def run_test():
    graph = None
    try:
        graph = await TradingAgentsGraph.create(...)
        # ... do work ...
    finally:
        if graph:
            await graph.close()
```

### Issue 2: Tool Parameter Validation Errors

**Cause:** MCP tool signature doesn't match original function

**Solution:** Check original function signature:

```bash
grep -A 5 "^def get_news" tradingagents/agents/utils/
```

Match the signature exactly in MCP server.

### Issue 3: "asyncio.run() cannot be called from running event loop"

**Cause:** Using `asyncio.run()` inside an async function

**Solution:** Use `await` directly:

```python
# BAD
async def my_function():
    result = asyncio.run(some_async_func())  # ❌

# GOOD
async def my_function():
    result = await some_async_func()  # ✅
```

### Issue 4: MCP Server Timeout

**Cause:** Server writing to stdout, corrupting JSON-RPC

**Solution:**
1. Redirect stdout to stderr at module level
2. Use `suppress_stdout` for vendor calls
3. Check logs on stderr for debugging

### Issue 5: Import Errors in MCP Server

**Cause:** Project root not in sys.path for subprocess

**Solution:**

```python
server_dir = Path(__file__).parent
project_root = server_dir.parent.parent.parent
sys.path.insert(0, str(project_root))
```

---

## Performance Considerations

### MCP Overhead

Based on initial testing (Market Analyst only):

- **Direct Mode**: ~135s
- **MCP Mode**: ~140s
- **Overhead**: ~5s (3.7%)

The overhead includes:
- Process startup (~1.5s)
- JSON-RPC serialization
- Stdio communication
- Context switching

### When to Use MCP

**Use MCP when:**
- ✅ Building modular, reusable tool servers
- ✅ Need to share tools across multiple applications
- ✅ Want to isolate tool execution (security/sandboxing)
- ✅ Tools are long-running (startup cost amortized)

**Use Direct when:**
- ✅ Minimal latency is critical
- ✅ Tools are simple Python functions
- ✅ Single application usage
- ✅ Tight coupling is acceptable

---

## Next Steps

1. **Implement remaining servers:**
   - News Server (`get_news`, `get_global_news`, `get_insider_sentiment`, `get_insider_transactions`)
   - Fundamentals Server (`get_fundamentals`, `get_balance_sheet`, `get_cashflow`, `get_income_statement`)
   - Social Server (reuse News Server tools)

2. **Run comparison tests:**
   - Performance benchmarks (MCP vs Direct)
   - Result quality comparison
   - Resource usage analysis

3. **Production considerations:**
   - Add retry logic for MCP connections
   - Implement connection pooling
   - Add health checks for servers
   - Monitor MCP server logs

---

## References

- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://gofastmcp.com)
- [MCP Specification](https://modelcontextprotocol.io/specification/latest)

---

**Last Updated**: December 18, 2024  
**Status**: ✅ Market Analyst MCP Integration Complete  
**Next**: Implement News, Fundamentals, Social MCP Servers

