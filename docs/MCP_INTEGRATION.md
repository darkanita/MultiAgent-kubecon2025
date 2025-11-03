# MCP Integration Guide

## Overview

This document explains how Model Context Protocol (MCP) has been integrated into the Travel Agent system alongside the existing A2A protocol.

## Architecture

```
┌─────────────────────────────────────────┐
│     Travel Manager (Coordinator)        │
│  ┌────────────────────────────────┐    │
│  │  Semantic Kernel               │    │
│  │  + A2A Client (Discovery)      │    │
│  │  + MCP Client (Tool Execution) │    │
│  └────────────────────────────────┘    │
└──────────┬──────────────┬───────────────┘
           │              │
   A2A     │      MCP     │      MCP
Discovery  │    Protocol  │    Protocol
           ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Currency │   │ Activity │   │  Future  │
    │  Agent   │   │  Agent   │   │  Agents  │
    ├──────────┤   ├──────────┤   ├──────────┤
    │ A2A Card │   │ A2A Card │   │ A2A Card │
    │ MCP      │   │ MCP      │   │ MCP      │
    │ Server   │   │ Server   │   │ Server   │
    └──────────┘   └──────────┘   └──────────┘
```

## Protocol Roles

### A2A Protocol (Agent-to-Agent)
- **Purpose**: Agent discovery and metadata
- **Features**:
  - Agent Cards for service advertisement
  - Capability discovery
  - Session management
  - Agent routing

### MCP Protocol (Model Context Protocol)
- **Purpose**: Tool invocation and execution
- **Features**:
  - Tool/function discovery
  - Structured input/output
  - Resource access
  - Prompt templates

## Why Both Protocols?

1. **A2A for Discovery** 🔍
   - Agents announce their existence
   - Coordinators find available services
   - Metadata about agent capabilities

2. **MCP for Execution** ⚡
   - Standardized tool invocation
   - Type-safe function calling
   - Rich tool descriptions
   - Better integration with AI models

## Implementation

### MCP Server (Agent Side)

Each agent exposes an MCP server:

```python
# src/agent/mcp_currency_server.py
class CurrencyMCPServer:
    def __init__(self):
        self.server = Server("currency-exchange-agent")
        
    @self.server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="get_exchange_rate",
                description="Get exchange rate between currencies",
                inputSchema={...}
            )
        ]
    
    @self.server.call_tool()
    async def call_tool(name: str, arguments: dict):
        # Execute the tool
        ...
```

### MCP Client (Coordinator Side)

The coordinator uses MCP clients to invoke tools:

```python
# src/agent/mcp_coordinator.py
class MCPCoordinator:
    async def register_agent(self, agent_name, server_script):
        client = MCPAgentClient(agent_name, "python", [server_script])
        await client.connect()
        self.clients[agent_name] = client
    
    async def call_tool(self, agent_name, tool_name, arguments):
        return await self.clients[agent_name].call_tool(tool_name, arguments)
```

## Files Created

1. **`src/agent/mcp_currency_server.py`**
   - MCP server for Currency Exchange Agent
   - Tools: `get_exchange_rate`, `convert_amount`

2. **`src/agent/mcp_activity_server.py`**
   - MCP server for Activity Planner Agent
   - Tools: `plan_activities`, `suggest_restaurants`, `suggest_attractions`

3. **`src/agent/mcp_coordinator.py`**
   - MCP client coordinator
   - Manages connections to multiple MCP servers
   - Tool discovery and invocation

## Current Status

✅ **Phase 1 Complete: MCP Added to Monolithic System**
- MCP SDK installed
- MCP servers created for Currency and Activity agents
- MCP coordinator client implemented
- Both A2A and MCP protocols coexist

## Next Steps

### Phase 2: Split into Microservices
- Create separate services for each agent
- Each service runs its own MCP server
- Each service exposes A2A endpoint
- Deploy as separate pods in Kubernetes

### Phase 3: Add New Agents (e.g., HR Agent)
- Create new MCP server for HR tools
- Expose A2A endpoint for discovery
- Register with coordinator
- Deploy as new microservice

## Testing MCP Integration

### Test Currency MCP Server
```bash
python src/agent/mcp_currency_server.py
```

### Test Activity MCP Server
```bash
python src/agent/mcp_activity_server.py
```

### Test MCP Coordinator
```bash
python src/agent/mcp_coordinator.py
```

## Benefits

1. **Standardization**: Industry-standard protocol for AI tool use
2. **Flexibility**: Easy to add new tools and agents
3. **Type Safety**: Structured schemas for inputs/outputs
4. **Discoverability**: Agents can discover each other's capabilities
5. **Scalability**: Each agent can be deployed independently

## Resources

- MCP Specification: https://modelcontextprotocol.io/
- A2A Protocol: https://a2a.googl eapis.dev/
- Semantic Kernel: https://learn.microsoft.com/semantic-kernel/

---

**Status**: ✅ MCP Integration Complete - Ready for Microservices Split
