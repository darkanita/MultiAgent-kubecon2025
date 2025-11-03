# Logging Guide: Distinguishing MCP vs A2A Interactions

## Overview

The application now has **enhanced logging** with emoji prefixes to clearly distinguish between different protocol interactions.

## Log Prefixes

### 💬 `[CHAT API]` - User Interactions
Logs when users send messages through the web interface or REST API.

**Example:**
```
INFO:src.api.chat:💬 [CHAT API] Received message: 'I need currency exchange from USD to EUR'
INFO:src.api.chat:💬 [CHAT API] Streaming message: 'Plan a trip to Seoul with $100 budget'
```

### 📡 `[A2A]` - Agent-to-Agent Protocol
Logs A2A protocol operations including:
- Server configuration
- Task execution
- Status updates

**Example:**
```
INFO:src.agent.a2a_server:📡 [A2A] Server configured for 0.0.0.0:8000
INFO:src.agent.agent_executor:📡 [A2A] Executing request: 'Convert 500 USD to KRW...'
INFO:src.agent.agent_executor:✅ [A2A] Task completed successfully
```

### 🔌 `[MCP]` - Model Context Protocol
Logs MCP client/server operations including:
- Server connections
- Tool discovery
- Tool invocations

**Example:**
```
INFO:src.agent.mcp_coordinator:🔌 [MCP] Connected to currency-agent MCP server. Available tools: ['get_exchange_rate', 'convert_amount']
INFO:src.agent.mcp_coordinator:🚀 [MCP] Calling tool 'convert_amount' on currency-agent with args: {'amount': 500, 'from_currency': 'USD', 'to_currency': 'KRW'}
INFO:src.agent.mcp_coordinator:✅ [MCP] Tool 'convert_amount' executed successfully on currency-agent, result: 650000...
```

### 🔧 `[MCP]` - Tool Operations
Logs tool-specific operations:
```
INFO:src.agent.mcp_coordinator:🔧 [MCP] Listing tools for activity-agent: ['plan_activities', 'suggest_restaurants', 'suggest_attractions']
INFO:src.agent.mcp_coordinator:🔧 [MCP] Getting tool definitions from currency-agent: ['get_exchange_rate', 'convert_amount']
```

## How to View Logs

### 1. Real-time Log Streaming

Watch logs as they happen:
```bash
kubectl logs -f deployment/multiagent-app -n multiagent-kubecon-simple
```

### 2. Recent Logs (Last 50 lines)

```bash
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple --tail=50
```

### 3. Filter for Specific Protocol

**MCP interactions only:**
```bash
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep "\[MCP\]"
```

**A2A interactions only:**
```bash
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep "\[A2A\]"
```

**Chat API interactions only:**
```bash
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep "\[CHAT API\]"
```

### 4. Filter by Emoji

**All MCP logs (connection + tools):**
```bash
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep "🔌\|🚀\|🔧"
```

**All A2A logs:**
```bash
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep "📡"
```

**User messages:**
```bash
kubectl logs deployment/multiagent-app -n multiagent-kubecon-simple | grep "💬"
```

## Triggering Interactions

### Currently: Only Health Checks

If you only see health check logs like this:
```
INFO:     10.244.0.1:52638 - "GET /health HTTP/1.1" 200 OK
```

This means **no one has used the application yet**. The MCP and A2A protocols are idle.

### How to Trigger Real Interactions

#### Option 1: Use the Web Interface

1. Get the external IP:
   ```bash
   kubectl get service multiagent-service -n multiagent-kubecon-simple
   ```

2. Open in browser: `http://<EXTERNAL-IP>`

3. Send a message like:
   - "Convert 500 USD to Korean Won"
   - "Plan a 2-day trip to Seoul with $100 budget"
   - "What's the exchange rate from EUR to JPY?"

4. Watch logs in real-time:
   ```bash
   kubectl logs -f deployment/multiagent-app -n multiagent-kubecon-simple
   ```

#### Option 2: Use cURL to Test REST API

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get service multiagent-service -n multiagent-kubecon-simple -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Send a chat message
curl -X POST "http://${EXTERNAL_IP}/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Convert 500 USD to Korean Won",
    "session_id": "test-session-123"
  }'
```

#### Option 3: Test A2A Protocol Endpoint

```bash
# Get Agent Card (A2A discovery)
curl "http://${EXTERNAL_IP}/a2a/"

# Send A2A task
curl -X POST "http://${EXTERNAL_IP}/a2a/tasks/send" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "I need to convert 1000 USD to EUR and get restaurant recommendations"
    }
  }'
```

## What You'll See in Logs

### Example Complete Flow

When a user sends: **"Convert 100 USD to EUR and suggest activities"**

```log
INFO:src.api.chat:💬 [CHAT API] Received message: 'Convert 100 USD to EUR and suggest activities'
INFO:src.agent.agent_executor:📡 [A2A] Executing request: 'Convert 100 USD to EUR and suggest activities...'
INFO:src.agent.mcp_coordinator:🚀 [MCP] Calling tool 'convert_amount' on currency-agent with args: {'amount': 100, 'from_currency': 'USD', 'to_currency': 'EUR'}
INFO:src.agent.mcp_coordinator:✅ [MCP] Tool 'convert_amount' executed successfully on currency-agent, result: 92.5...
INFO:src.agent.mcp_coordinator:🚀 [MCP] Calling tool 'suggest_attractions' on activity-agent with args: {'destination': 'Europe', 'budget': 'moderate'}
INFO:src.agent.mcp_coordinator:✅ [MCP] Tool 'suggest_attractions' executed successfully on activity-agent, result: Top attractions...
INFO:src.agent.agent_executor:✅ [A2A] Task completed successfully
```

### Flow Breakdown

1. **💬 [CHAT API]** - User message received via REST API
2. **📡 [A2A]** - A2A executor starts processing the request
3. **🚀 [MCP]** - MCP coordinator calls currency tool
4. **✅ [MCP]** - Currency tool returns result
5. **🚀 [MCP]** - MCP coordinator calls activity tool
6. **✅ [MCP]** - Activity tool returns result
7. **✅ [A2A]** - A2A executor completes the task

## Status Indicators

| Emoji | Meaning |
|-------|---------|
| ✅ | Success / Completed |
| ❌ | Error / Failed |
| 🔌 | Connection (MCP server) |
| 🚀 | Execution (MCP tool call) |
| 🔧 | Configuration (Tool discovery) |
| 📡 | A2A Protocol operation |
| 💬 | User interaction |
| ⚠️ | Warning |

## Troubleshooting

### No MCP Logs Appearing?

**Reason:** MCP servers are only started when tools are actually needed. In the current monolithic deployment, MCP is available but not actively used because agents are embedded.

**When will you see MCP logs?**
- **Phase 2 (Microservices)**: When agents become separate services, you'll see MCP logs for inter-service communication
- **Current Phase**: MCP infrastructure is deployed but dormant until microservices split

### No A2A Logs Appearing?

**Reason:** A2A protocol is used when:
1. External agents discover your agent via Agent Card
2. Tasks are sent through A2A endpoints (`/a2a/tasks/send`)
3. The web interface internally uses A2A for task execution

**Solution:** Send messages through the web UI at `http://<EXTERNAL-IP>` or use the cURL examples above.

### Only Seeing Health Checks?

**Reason:** Kubernetes health probes run every 5-10 seconds. This is normal when no users are active.

**Solution:** Send a test message using one of the methods above.

## Log Levels

The application uses Python's logging module with these levels:

- **INFO**: Normal operations (most MCP/A2A logs)
- **DEBUG**: Detailed streaming chunks (verbose)
- **WARNING**: Issues that don't stop execution
- **ERROR**: Failures that need attention

To see DEBUG logs, modify the log level in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # Change from INFO to DEBUG
```

## Next Steps

1. **Try it now**: Open http://172.168.108.4 and send a message
2. **Watch logs**: `kubectl logs -f deployment/multiagent-app -n multiagent-kubecon-simple`
3. **Filter protocols**: Use grep to focus on MCP or A2A
4. **Phase 2**: When we split into microservices, you'll see heavy MCP usage for inter-service communication

---

**Current External IP**: http://172.168.108.4  
**Test Command**: `curl -X POST "http://172.168.108.4/api/chat/message" -H "Content-Type: application/json" -d '{"message": "Convert 100 USD to EUR", "session_id": "test"}'`
