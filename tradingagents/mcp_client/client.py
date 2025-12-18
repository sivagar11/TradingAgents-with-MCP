"""MCP Client - Connects to and communicates with MCP servers."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from contextlib import AsyncExitStack

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    # Fallback for different MCP package structure
    try:
        from mcp.client import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        print("ERROR: MCP package not found. Install with: pip install mcp")
from langchain_core.messages import ToolMessage

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for managing connections to multiple MCP servers."""
    
    def __init__(self):
        """Initialize MCP client."""
        self.sessions: Dict[str, ClientSession] = {}  # name -> session
        self.server_configs: Dict[str, StdioServerParameters] = {}
        self._initialized = False
        self._exit_stack: Optional[AsyncExitStack] = None
    
    def register_server(self, name: str, command: str, args: List[str] = None):
        """
        Register an MCP server.
        
        Args:
            name: Server identifier (e.g., 'stock', 'news')
            command: Command to start server (e.g., 'python')
            args: Command arguments (e.g., ['path/to/server.py'])
        """
        import os
        
        # Pass parent process environment to subprocess so it has access to API keys
        self.server_configs[name] = StdioServerParameters(
            command=command,
            args=args or [],
            env=os.environ.copy()  # ✅ FIX: Inherit environment variables
        )
    
    async def connect_all(self):
        """Connect to all registered servers."""
        for name, config in self.server_configs.items():
            await self.connect_server(name, config)
        self._initialized = True
    
    async def connect_server(self, name: str, config: StdioServerParameters, timeout: int = 60):
        """Connect to a specific MCP server with timeout."""
        try:
            logger.info(f"MCP: Connecting to '{name}' server (timeout: {timeout}s)...")
            
            # Initialize exit stack if needed (for proper async context management)
            if self._exit_stack is None:
                self._exit_stack = AsyncExitStack()
                await self._exit_stack.__aenter__()
            
            # Wrap connection in timeout
            async with asyncio.timeout(timeout):
                logger.info(f"MCP: Starting '{name}' server process...")
                
                # Enter stdio client context via exit stack
                # This properly manages the async context for the server connection
                read_stream, write_stream = await self._exit_stack.enter_async_context(
                    stdio_client(config)
                )
                
                logger.info(f"MCP: Creating session for '{name}'...")
                # Enter session context via exit stack
                session = await self._exit_stack.enter_async_context(
                    ClientSession(read_stream, write_stream)
                )
                
                logger.info(f"MCP: Initializing '{name}' session...")
                init_result = await session.initialize()
                
                # Store session (exit stack will handle cleanup)
                self.sessions[name] = session
                
                logger.info(f"MCP: Listing tools for '{name}'...")
                # List available tools (for debugging)
                tools_result = await session.list_tools()
                logger.info(f"MCP: ✅ Connected to '{name}' with {len(tools_result.tools)} tools")
                for tool in tools_result.tools:
                    logger.info(f"MCP:    - {tool.name}")
            
        except asyncio.TimeoutError:
            logger.error(f"MCP: ❌ Timeout connecting to '{name}' after {timeout}s")
            logger.error("MCP: Server may not be responding - check server logs on stderr")
            raise
        except Exception as e:
            logger.error(f"MCP: ❌ Connection failed for '{name}': {e}", exc_info=True)
            raise
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool on an MCP server.
        
        Args:
            server_name: Name of the server to call
            tool_name: Name of the tool to invoke
            arguments: Tool arguments as dictionary
        
        Returns:
            Tool response as string
        """
        if not self._initialized:
            raise RuntimeError("MCP client not initialized. Call connect_all() first.")
        
        if server_name not in self.sessions:
            raise ValueError(f"Server '{server_name}' not connected")
        
        session = self.sessions[server_name]
        
        try:
            # Call tool on server
            result = await session.call_tool(tool_name, arguments)
            
            # Extract text content from result
            if result.content and len(result.content) > 0:
                return result.content[0].text
            else:
                return f"No response from {tool_name}"
            
        except Exception as e:
            error_msg = f"MCP tool call failed: {tool_name} on {server_name}: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg
    
    async def list_tools(self, server_name: str) -> List[str]:
        """List available tools on a server."""
        if server_name not in self.sessions:
            return []
        
        session = self.sessions[server_name]
        tools_result = await session.list_tools()
        return [tool.name for tool in tools_result.tools]
    
    async def close_all(self):
        """Close all server connections."""
        if self._exit_stack:
            try:
                # Exit stack will properly close all contexts in reverse order
                await self._exit_stack.__aexit__(None, None, None)
                logger.info("MCP: Closed all server connections")
            except Exception as e:
                logger.error(f"MCP: Error closing connections: {e}", exc_info=True)
        
        self.sessions.clear()
        self._exit_stack = None
        self._initialized = False


class MCPToolExecutor:
    """
    Tool executor that routes calls through MCP.
    
    This replaces LangGraph's ToolNode for MCP-enabled tools.
    LangGraph supports async node functions, so this provides an async __call__.
    """
    
    def __init__(self, mcp_client: MCPClient, tool_to_server_mapping: Dict[str, str]):
        """
        Initialize MCP tool executor.
        
        Args:
            mcp_client: Connected MCP client instance
            tool_to_server_mapping: Maps tool names to server names
                Example: {"get_stock_data": "stock", "get_news": "news"}
        """
        self.client = mcp_client
        self.mapping = tool_to_server_mapping
    
    async def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[ToolMessage]:
        """
        Execute multiple tool calls via MCP.
        
        Args:
            tool_calls: List of tool calls from LLM
        
        Returns:
            List of ToolMessage objects with results
        """
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            tool_id = tool_call.get("id")
            
            # Route to appropriate server
            server_name = self.mapping.get(tool_name)
            
            if not server_name:
                # Tool not in MCP mapping - return error
                result = ToolMessage(
                    content=f"Tool '{tool_name}' not available in MCP",
                    tool_call_id=tool_id
                )
            else:
                try:
                    # Call tool via MCP
                    response = await self.client.call_tool(
                        server_name,
                        tool_name,
                        tool_args
                    )
                    
                    result = ToolMessage(
                        content=response,
                        tool_call_id=tool_id
                    )
                except Exception as e:
                    result = ToolMessage(
                        content=f"MCP error calling {tool_name}: {str(e)}",
                        tool_call_id=tool_id
                    )
            
            results.append(result)
        
        return results
    
    async def __call__(self, state):
        """
        Execute tool calls from agent state (compatible with LangGraph).
        
        This is an async method that LangGraph can call directly within its event loop.
        
        Args:
            state: Agent state containing messages
        
        Returns:
            Updated state with tool results
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return {"messages": []}
        
        # Execute tool calls asynchronously within the existing event loop
        tool_results = await self.execute_tool_calls(last_message.tool_calls)
        
        return {"messages": tool_results}


# Helper function to create and initialize MCP client
async def create_mcp_client(server_configs: Dict[str, Dict[str, Any]]) -> MCPClient:
    """
    Create and initialize MCP client with servers.
    
    Args:
        server_configs: Dictionary of server configurations
            Example:
            {
                "stock": {
                    "command": "python",
                    "args": ["tradingagents/mcp_servers/stock_server/server.py"]
                }
            }
    
    Returns:
        Initialized MCPClient
    """
    client = MCPClient()
    
    # Register all servers
    for name, config in server_configs.items():
        client.register_server(
            name,
            config["command"],
            config.get("args", [])
        )
    
    # Connect to all servers
    await client.connect_all()
    
    return client

