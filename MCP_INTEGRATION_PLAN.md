# MCP Integration Plan for TradingAgents

## 🎯 Goal
Integrate **Model Context Protocol (MCP)** to replace direct tool calls with standardized MCP server communication for better modularity, reusability, and research contributions.

## 📊 Current vs. Target Architecture

### Current Architecture
```
┌─────────┐    ┌──────────┐    ┌────────────┐    ┌─────────────┐
│   LLM   │ -> │ Tool Call│ -> │  ToolNode  │ -> │ Data Source │
│ (Agent) │    │          │    │ (LangGraph)│    │ (yfinance)  │
└─────────┘    └──────────┘    └────────────┘    └─────────────┘
```

**Issues:**
- Tight coupling between agents and data sources
- Hard to reuse tools across different systems
- Limited standardization
- Difficult to swap data providers

### Target Architecture with MCP
```
┌─────────┐    ┌──────────┐    ┌─────────────┐    ┌────────────┐    ┌─────────────┐
│   LLM   │ -> │ Tool Call│ -> │ MCP Client  │ -> │ MCP Server │ -> │ Data Source │
│ (Agent) │    │          │    │             │    │            │    │ (yfinance)  │
└─────────┘    └──────────┘    └─────────────┘    └────────────┘    └─────────────┘
```

**Benefits:**
- ✅ Standardized protocol (Anthropic MCP spec)
- ✅ Reusable MCP servers across projects
- ✅ Easy to add/swap data sources
- ✅ Better separation of concerns
- ✅ Contribution to MCP ecosystem
- ✅ Research paper material

## 🏗️ Implementation Strategy

### Phase 1: MCP Server Development

Create **4 MCP Servers** (one for each data category):

#### 1. **Stock Data MCP Server** (`mcp-server-stock`)
**Tools Exposed:**
- `get_stock_data` - Historical price data
- `get_indicators` - Technical indicators (RSI, MACD, Bollinger Bands)

**Data Sources:**
- Primary: yfinance
- Fallback: alpha_vantage

**Server Location:** `tradingagents/mcp_servers/stock_server/`

#### 2. **News MCP Server** (`mcp-server-news`)
**Tools Exposed:**
- `get_news` - Company-specific news
- `get_global_news` - Market-wide news
- `get_insider_sentiment` - Insider trading sentiment
- `get_insider_transactions` - Insider transaction history

**Data Sources:**
- Primary: alpha_vantage
- Fallback: openai, google

**Server Location:** `tradingagents/mcp_servers/news_server/`

#### 3. **Fundamentals MCP Server** (`mcp-server-fundamentals`)
**Tools Exposed:**
- `get_fundamentals` - Company fundamentals
- `get_balance_sheet` - Balance sheet data
- `get_income_statement` - Income statement
- `get_cashflow` - Cash flow statement

**Data Sources:**
- Primary: yfinance
- Fallback: alpha_vantage, openai

**Server Location:** `tradingagents/mcp_servers/fundamentals_server/`

#### 4. **Social Media MCP Server** (`mcp-server-social`)
**Tools Exposed:**
- `get_social_sentiment` - Social media sentiment analysis
- `get_news` - Social/news aggregation

**Data Sources:**
- Primary: alpha_vantage
- Fallback: openai, google

**Server Location:** `tradingagents/mcp_servers/social_server/`

### Phase 2: MCP Client Integration

#### 2.1 MCP Client Wrapper
Create: `tradingagents/mcp_client/client.py`

```python
class MCPClient:
    """Client for communicating with MCP servers."""
    
    def __init__(self, server_configs):
        self.servers = {}  # server_name -> connection
        self.initialize_connections(server_configs)
    
    async def call_tool(self, server_name, tool_name, arguments):
        """Call a tool on an MCP server."""
        server = self.servers[server_name]
        response = await server.call_tool(tool_name, arguments)
        return response
    
    def list_tools(self, server_name):
        """Get available tools from a server."""
        return self.servers[server_name].list_tools()
```

#### 2.2 Replace ToolNode with MCP Tool Executor
Create: `tradingagents/graph/mcp_tool_node.py`

```python
class MCPToolNode:
    """Custom tool node that routes to MCP servers instead of direct execution."""
    
    def __init__(self, mcp_client, tool_to_server_mapping):
        self.client = mcp_client
        self.mapping = tool_to_server_mapping
    
    def __call__(self, state):
        """Execute tool calls via MCP."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if not last_message.tool_calls:
            return {"messages": []}
        
        tool_results = []
        for tool_call in last_message.tool_calls:
            # Route to appropriate MCP server
            server = self.mapping[tool_call["name"]]
            result = await self.client.call_tool(
                server, 
                tool_call["name"], 
                tool_call["args"]
            )
            tool_results.append(result)
        
        return {"messages": tool_results}
```

### Phase 3: Integration with Existing Analysts

#### 3.1 Update Trading Graph
Modify: `tradingagents/graph/trading_graph.py`

```python
from tradingagents.mcp_client import MCPClient
from tradingagents.graph.mcp_tool_node import MCPToolNode

class TradingAgentsGraph:
    def __init__(self, ...):
        # Initialize MCP client
        self.mcp_client = MCPClient({
            "stock": "stdio:mcp-server-stock",
            "news": "stdio:mcp-server-news",
            "fundamentals": "stdio:mcp-server-fundamentals",
            "social": "stdio:mcp-server-social",
        })
        
        # Create MCP tool nodes instead of regular ToolNodes
        self.tool_nodes = self._create_mcp_tool_nodes()
    
    def _create_mcp_tool_nodes(self):
        """Create MCP-powered tool nodes."""
        tool_mapping = {
            "get_stock_data": "stock",
            "get_indicators": "stock",
            "get_news": "news",
            "get_fundamentals": "fundamentals",
            # ... etc
        }
        
        return {
            "market": MCPToolNode(self.mcp_client, tool_mapping),
            "social": MCPToolNode(self.mcp_client, tool_mapping),
            "news": MCPToolNode(self.mcp_client, tool_mapping),
            "fundamentals": MCPToolNode(self.mcp_client, tool_mapping),
        }
```

#### 3.2 Keep Analyst Code Unchanged
**Important:** Analysts don't need to change! They still use:
```python
chain = prompt | llm.bind_tools(tools)
```

The MCP integration is **transparent** to the LLM - it still thinks it's calling tools normally.

## 📦 Dependencies

Add to `requirements.txt`:
```
mcp>=1.0.0
fastmcp>=0.2.0
```

## 🗂️ Project Structure

```
tradingagents/
├── mcp_servers/              # NEW: MCP servers
│   ├── stock_server/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools.py
│   ├── news_server/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools.py
│   ├── fundamentals_server/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools.py
│   └── social_server/
│       ├── __init__.py
│       ├── server.py
│       └── tools.py
├── mcp_client/               # NEW: MCP client
│   ├── __init__.py
│   ├── client.py
│   └── config.py
├── graph/
│   ├── trading_graph.py      # MODIFIED: Use MCP client
│   ├── mcp_tool_node.py      # NEW: MCP tool executor
│   └── setup.py              # MODIFIED: Use MCPToolNode
├── agents/                   # UNCHANGED
│   └── analysts/
│       ├── market_analyst.py
│       ├── news_analyst.py
│       └── ...
└── dataflows/                # MODIFIED: Move to MCP servers
    ├── vendors/              # These become MCP server implementations
    └── interface.py          # Deprecated (replaced by MCP)
```

## 🎯 Implementation Steps

### Step 1: Create Stock MCP Server (Proof of Concept)
- [ ] Create `mcp-server-stock` directory
- [ ] Implement `get_stock_data` tool
- [ ] Implement `get_indicators` tool
- [ ] Test server standalone

### Step 2: Create MCP Client
- [ ] Implement `MCPClient` class
- [ ] Add connection management
- [ ] Add error handling and fallbacks

### Step 3: Create MCPToolNode
- [ ] Replace LangGraph ToolNode
- [ ] Route tool calls to MCP servers
- [ ] Handle tool responses

### Step 4: Integrate with One Analyst (Market Analyst)
- [ ] Update `trading_graph.py` to use MCP client
- [ ] Test Market Analyst with MCP
- [ ] Verify it works end-to-end

### Step 5: Extend to All Analysts
- [ ] Create remaining MCP servers (news, fundamentals, social)
- [ ] Update tool mappings
- [ ] Test all 4 analysts

### Step 6: Documentation & Testing
- [ ] Document MCP server APIs
- [ ] Write integration tests
- [ ] Performance benchmarks (MCP vs direct calls)

## 🔬 Research Contributions

This integration enables several research contributions:

1. **Novel Architecture**: First trading agent system using MCP
2. **Benchmarking**: Compare MCP vs direct tool calling (latency, reliability)
3. **Reusability**: MCP servers can be used in other AI trading systems
4. **Standardization**: Demonstrate MCP benefits in financial AI domain

## 📊 Performance Considerations

**Potential Overhead:**
- MCP adds IPC (Inter-Process Communication) overhead
- Each tool call: Python → MCP Client → MCP Server → Data Source

**Optimizations:**
1. **Connection Pooling**: Reuse MCP connections
2. **Caching**: Cache MCP responses
3. **Batching**: Batch multiple tool calls
4. **Local Servers**: Run MCP servers on same machine (stdio transport)

**Expected Performance:**
- Additional latency: ~10-50ms per tool call
- Total impact: ~0.5-1 second on full analysis (negligible vs 3-minute runtime)

## 🚀 Next Steps

**Option 1: Full Implementation**
- Implement all 4 MCP servers
- Complete integration
- Best for: Complete research project

**Option 2: Proof of Concept**
- Start with Stock MCP server only
- Integrate with Market Analyst
- Validate approach before full implementation
- Best for: Quick validation

**Option 3: Hybrid Approach**
- Keep existing tool system
- Add MCP as optional alternative
- Allow A/B comparison for research
- Best for: Research paper with comparisons

## 💡 Recommendation

Start with **Option 2 (Proof of Concept)**:
1. Create Stock MCP server (1-2 hours)
2. Implement MCP client (1 hour)
3. Create MCPToolNode (1 hour)
4. Test with Market Analyst (30 min)

**Total: ~4-5 hours for working proof of concept**

Then decide if full implementation is worth it based on results.

---

**Ready to start?** I can help implement any of these steps!

