# Real Log Examples: MCP vs A2A

## What We Just Saw

When you sent the test message **"Convert 100 USD to EUR"**, here's what appeared in the logs:

### 1. Chat API Entry Point (User Interaction)
```log
INFO:src.api.chat:💬 [CHAT API] Received message: 'Convert 100 USD to EUR...'
```
**What it means**: The REST API received your HTTP request. This is the entry point.

---

### 2. Semantic Kernel Function Calling (NOT MCP!)
```log
INFO:semantic_kernel.kernel:Calling CurrencyExchangeAgent-CurrencyExchangeAgent function with args: {"messages":"Convert 100 USD to EUR."}
INFO:semantic_kernel.functions.kernel_function:Function CurrencyExchangeAgent-CurrencyExchangeAgent invoking.
```
**What it means**: Semantic Kernel's built-in agent system is routing the request to the Currency agent **using Semantic Kernel plugins**, not MCP protocol.

---

### 3. Currency Plugin Execution (Semantic Kernel Plugin)
```log
INFO:semantic_kernel.kernel:Calling CurrencyPlugin-get_exchange_rate function with args: {"currency_from":"USD","currency_to":"EUR"}
INFO:semantic_kernel.functions.kernel_function:Function CurrencyPlugin-get_exchange_rate invoking.
INFO:httpx:HTTP Request: GET https://api.frankfurter.app/latest?from=USD&to=EUR "HTTP/1.1 200 OK"
INFO:semantic_kernel.functions.kernel_function:Function CurrencyPlugin-get_exchange_rate succeeded.
```
**What it means**: The Currency agent is calling the Frankfurter API directly through a Semantic Kernel plugin.

---

## Why No MCP Logs Yet?

**Important**: In the current **monolithic deployment**, the MCP infrastructure is **deployed but not active** because:

1. **All agents are embedded** in the same process (TravelManager, CurrencyAgent, ActivityAgent)
2. **Semantic Kernel's internal function calling** is used instead of MCP protocol
3. **MCP servers exist** (`mcp_currency_server.py`, `mcp_activity_server.py`) but aren't started

### When Will You See MCP Logs?

**Phase 2 - Microservices Architecture:**
- Currency Agent runs as **separate Pod** with MCP server
- Activity Agent runs as **separate Pod** with MCP server
- Coordinator calls agents via **MCP protocol over stdio**

**Example future logs (Phase 2):**
```log
INFO:src.agent.mcp_coordinator:🔌 [MCP] Connected to currency-agent MCP server. Available tools: ['get_exchange_rate', 'convert_amount']
INFO:src.agent.mcp_coordinator:🚀 [MCP] Calling tool 'convert_amount' on currency-agent with args: {'amount': 100, 'from_currency': 'USD', 'to_currency': 'EUR'}
INFO:src.agent.mcp_coordinator:✅ [MCP] Tool 'convert_amount' executed successfully on currency-agent
```

---

## Current Architecture (Phase 1 - Monolithic)

```
┌─────────────────────────────────────────┐
│         Single FastAPI Pod              │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │     TravelManagerAgent            │  │
│  │  (Semantic Kernel Orchestrator)   │  │
│  └──────────┬────────────────────────┘  │
│             │                            │
│             │ Semantic Kernel            │
│             │ Function Calling           │
│             │ (NOT MCP)                  │
│             ▼                            │
│  ┌──────────────────┐  ┌──────────────┐ │
│  │ CurrencyAgent    │  │ ActivityAgent│ │
│  │ (SK Plugin)      │  │ (SK Plugin)  │ │
│  └──────────────────┘  └──────────────┘ │
│                                         │
│  📂 MCP Files Present But Inactive:     │
│     • mcp_currency_server.py           │
│     • mcp_activity_server.py           │
│     • mcp_coordinator.py               │
└─────────────────────────────────────────┘
```

---

## Future Architecture (Phase 2 - Microservices)

```
┌─────────────────────┐         ┌─────────────────────┐
│  Coordinator Pod    │         │  Currency Agent Pod │
│                     │         │                     │
│  TravelManager      │◄────────┤  MCP Server         │
│  + MCP Client       │  MCP    │  (stdio protocol)   │
│                     │────────►│  • get_exchange_rate│
└─────────────────────┘         │  • convert_amount   │
         │                      └─────────────────────┘
         │
         │  MCP Protocol         ┌─────────────────────┐
         └──────────────────────►│  Activity Agent Pod │
                                 │                     │
                                 │  MCP Server         │
                                 │  (stdio protocol)   │
                                 │  • plan_activities  │
                                 │  • suggest_dining   │
                                 └─────────────────────┘
```

In Phase 2, you'll see:
```log
🔌 [MCP] Connected to currency-agent
🚀 [MCP] Calling tool 'convert_amount'
✅ [MCP] Tool executed successfully
```

---

## What About A2A Protocol?

### A2A is Active (Server Side)

You saw this at startup:
```log
INFO:src.agent.a2a_server:📡 [A2A] Server configured for 0.0.0.0:8000
```

**What it means**: The A2A server is running and ready to:
- Serve Agent Cards at `/a2a/`
- Accept tasks from other A2A agents at `/a2a/tasks/send`
- Stream task updates

### Why No A2A Execution Logs?

Because you called the **REST API** (`/api/chat/message`), not the **A2A API** (`/a2a/tasks/send`).

### To See A2A Logs

Test the A2A task endpoint:
```bash
curl -X POST "http://172.168.108.4/a2a/tasks/send" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user", 
      "content": "Convert 500 USD to JPY"
    }
  }'
```

You'll see:
```log
INFO:src.agent.agent_executor:📡 [A2A] Executing request: 'Convert 500 USD to JPY...'
INFO:src.agent.agent_executor:✅ [A2A] Task completed successfully
```

---

## Summary Table

| Protocol | Current Status | When You See Logs |
|----------|---------------|-------------------|
| **💬 Chat API** | ✅ Active | Always (when users send messages) |
| **📡 A2A** | ✅ Active (Server) | When tasks sent to `/a2a/tasks/send` |
| **🔌 MCP** | ⏸️ Deployed but Dormant | Phase 2 (Microservices) |
| **Semantic Kernel** | ✅ Active | Always (internal agent routing) |

---

## Key Insight

**Currently**: Your logs show **Semantic Kernel function calling**, which looks like this:
```
semantic_kernel.kernel → Calling CurrencyExchangeAgent
semantic_kernel.functions.kernel_function → Function invoking
```

**Phase 2**: Your logs will show **MCP protocol**, which looks like this:
```
mcp_coordinator → 🚀 [MCP] Calling tool 'convert_amount'
mcp_coordinator → ✅ [MCP] Tool executed successfully
```

---

## How to Verify Enhanced Logging

### Test 1: Chat API (Shows Chat + Semantic Kernel)
```bash
curl -X POST "http://172.168.108.4/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 200 EUR in USD?", "session_id": "demo"}'

# Then check logs:
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple --tail=50 | grep "CHAT API"
```

**Expected**:
```
💬 [CHAT API] Received message: 'What is 200 EUR in USD?...'
```

### Test 2: A2A Protocol (Shows A2A Execution)
```bash
curl -X POST "http://172.168.108.4/a2a/tasks/send" \
  -H "Content-Type: application/json" \
  -d '{"message": {"role": "user", "content": "Convert 1000 USD to GBP"}}'

# Then check logs:
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple --tail=50 | grep "A2A"
```

**Expected**:
```
📡 [A2A] Server configured for 0.0.0.0:8000
📡 [A2A] Executing request: 'Convert 1000 USD to GBP...'
✅ [A2A] Task completed successfully
```

### Test 3: MCP Protocol (Phase 2 Only)
Not available until microservices split.

---

## Quick Reference Commands

### Watch all logs live:
```bash
kubectl logs -f deployment/multiagent-app -n multiagent-kubecon-simple
```

### Filter by protocol:
```bash
# Chat API only
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep "CHAT API"

# A2A only
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep "A2A"

# MCP only (Phase 2)
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep "MCP"

# Exclude health checks
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep -v "health"
```

---

**Current Deployment**: http://172.168.108.4  
**Logs**: `kubectl logs -f deployment/multiagent-app -n multiagent-kubecon-simple`  
**Phase**: 1 (Monolithic with MCP infrastructure deployed)
