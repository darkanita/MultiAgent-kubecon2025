"""MCP Client for Travel Manager Coordinator.

This module provides an MCP client that the Travel Manager uses to discover
and invoke tools from MCP servers (Currency Agent, Activity Agent, etc.).
"""

import logging
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

logger = logging.getLogger(__name__)


class MCPAgentClient:
    """Client for communicating with MCP-enabled agents."""

    def __init__(self, agent_name: str, command: str, args: list[str] = None):
        """Initialize MCP client for a specific agent.
        
        Args:
            agent_name: Name of the agent (for logging)
            command: Command to start the MCP server process
            args: Arguments for the command
        """
        self.agent_name = agent_name
        self.command = command
        self.args = args or []
        self.session: ClientSession | None = None
        self._available_tools: list[Any] = []

    async def connect(self):
        """Establish connection to the MCP server."""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.command,
                args=self.args
            )
            
            # Start the MCP server process and connect
            stdio_transport = stdio_client(server_params)
            self.session = await stdio_transport.__aenter__()
            
            # Initialize the session
            await self.session.initialize()
            
            # Discover available tools
            tools_response = await self.session.list_tools()
            self._available_tools = tools_response.tools
            
            logger.info(
                f"🔌 [MCP] Connected to {self.agent_name} MCP server. "
                f"Available tools: {[t.name for t in self._available_tools]}"
            )
        except Exception as e:
            logger.error(f"❌ [MCP] Failed to connect to {self.agent_name} MCP server: {e}")
            raise

    async def disconnect(self):
        """Close the connection to the MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None
            logger.info(f"🔌 [MCP] Disconnected from {self.agent_name} MCP server")

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all available tools from this agent.
        
        Returns:
            List of tool definitions
        """
        if not self.session:
            raise RuntimeError(f"Not connected to {self.agent_name}")
        
        logger.info(f"🔧 [MCP] Getting tool definitions from {self.agent_name}: {[t.name for t in self._available_tools]}")
        
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in self._available_tools
        ]

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if not self.session:
            raise RuntimeError(f"Not connected to {self.agent_name} MCP server")
        
        logger.info(f"🚀 [MCP] Calling tool '{tool_name}' on {self.agent_name} with args: {arguments}")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            logger.info(f"✅ [MCP] Tool '{tool_name}' executed successfully on {self.agent_name}")
            return result
        except Exception as e:
            logger.error(f"❌ [MCP] Error calling tool '{tool_name}' on {self.agent_name}: {e}")
            raise


class MCPCoordinator:
    """Coordinator that manages multiple MCP agent clients."""

    def __init__(self):
        """Initialize the MCP coordinator."""
        self.clients: dict[str, MCPAgentClient] = {}
        self.python_exe = "python"  # Will be updated to correct path

    async def register_agent(
        self,
        agent_name: str,
        server_script: str,
        args: list[str] = None
    ):
        """Register a new MCP-enabled agent.
        
        Args:
            agent_name: Unique name for the agent
            server_script: Path to the MCP server script
            args: Additional arguments for the server
        """
        client = MCPAgentClient(
            agent_name=agent_name,
            command=self.python_exe,
            args=[server_script] + (args or [])
        )
        await client.connect()
        self.clients[agent_name] = client
        logger.info(f"Registered MCP agent: {agent_name}")

    async def discover_tools(self) -> dict[str, list[dict[str, Any]]]:
        """Discover all available tools from all registered agents.
        
        Returns:
            Dictionary mapping agent names to their available tools
        """
        tools_by_agent = {}
        for agent_name, client in self.clients.items():
            tools_by_agent[agent_name] = await client.list_tools()
        return tools_by_agent

    async def call_tool(
        self,
        agent_name: str,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> Any:
        """Call a tool on a specific agent.
        
        Args:
            agent_name: Name of the agent
            tool_name: Name of the tool
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if agent_name not in self.clients:
            raise ValueError(f"Agent {agent_name} not registered")
        
        return await self.clients[agent_name].call_tool(tool_name, arguments)

    async def shutdown(self):
        """Disconnect all MCP clients."""
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()
        logger.info("🔌 [MCP] MCP Coordinator shutdown complete")


# Example usage
async def example():
    """Example of using the MCP coordinator."""
    coordinator = MCPCoordinator()
    
    # Register agents
    await coordinator.register_agent(
        "currency",
        "src/agent/mcp_currency_server.py"
    )
    await coordinator.register_agent(
        "activity",
        "src/agent/mcp_activity_server.py"
    )
    
    # Discover tools
    tools = await coordinator.discover_tools()
    print("Available tools:", tools)
    
    # Call a tool
    result = await coordinator.call_tool(
        "currency",
        "get_exchange_rate",
        {"currency_from": "USD", "currency_to": "KRW"}
    )
    print("Exchange rate:", result)
    
    # Cleanup
    await coordinator.shutdown()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example())
