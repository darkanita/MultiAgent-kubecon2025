# Monitoring Guide: A2A vs MCP Protocol Usage

##  How to See When Each Protocol is Active

### **Protocol Overview**

| Protocol | When It's Used | Log Prefix | Purpose |
|----------|---------------|------------|---------|
| **A2A** | External agents discover/delegate to your service | `[A2A]` | Agent-to-Agent communication |
| **MCP** | Coordinator calls currency/activity agents | `[MCP]` | Model Context Protocol tool execution |
| **REST** | Web UI user interactions | No prefix | Direct user chat |

---

##  Log Monitoring Commands

### **1. Watch All Protocols in Real-Time**

```bash
# Tail coordinator logs (shows A2A, MCP, and user requests)
kubectl logs -n multiagent-microservices deployment/coordinator -f

# Watch for MCP activity only
kubectl logs -n multiagent-microservices deployment/coordinator -f | grep "\[MCP\]"

# Watch for A2A activity only
kubectl logs -n multiagent-microservices deployment/coordinator -f | grep "\[A2A\]"
```

### **2. See MCP Tool Calls on Agent Services**

```bash
# Currency agent MCP calls
kubectl logs -n multiagent-microservices deployment/currency-agent -f | grep "\[MCP\]"

# Activity agent MCP calls
kubectl logs -n multiagent-microservices deployment/activity-agent -f | grep "\[MCP\]"
```

### **3. Multi-Pod View (All Services)**

```bash
# Watch all pods simultaneously (requires stern or kubetail)
kubectl logs -n multiagent-microservices -l app=coordinator --tail=50 -f
kubectl logs -n multiagent-microservices -l app=currency-agent --tail=50 -f
kubectl logs -n multiagent-microservices -l app=activity-agent --tail=50 -f
```

---

## �� Example Scenarios

### **Scenario 1: User Sends Travel Query via Web UI**

**User Action**: Opens http://<YOUR-PUBLIC-IP> and asks: *"Convert $100 to EUR and plan activities in Paris"*

**Expected Log Flow**:

1. **Coordinator** receives user request (REST API):
   ```
   INFO:     10.224.0.4:50328 - "POST /api/chat/message HTTP/1.1" 200 OK
   ```

2. **Coordinator** decides to call MCP tools:
   ```
   2025-11-03 21:30:00 - agent - INFO -  [MCP] Calling tool 'convert_amount' on currency-agent
   ```

3. **Currency Agent** receives MCP call:
   ```
   2025-11-03 21:30:00 - __main__ - INFO - �� [MCP] Received request: tools/call
   2025-11-03 21:30:00 - __main__ - INFO -  [MCP] Calling tool 'convert_amount' with args: {"amount": 100, "from_currency": "USD", "to_currency": "EUR"}
   2025-11-03 21:30:01 - __main__ - INFO - ✅ [MCP] Tool 'convert_amount' executed successfully
   ```

4. **Coordinator** calls activity agent:
   ```
   2025-11-03 21:30:02 - agent - INFO -  [MCP] Calling tool 'plan_activities' on activity-agent
   ```

5. **Activity Agent** receives MCP call:
   ```
   2025-11-03 21:30:02 - __main__ - INFO -  [MCP] Received request: tools/call
   2025-11-03 21:30:02 - __main__ - INFO -  [MCP] Calling tool 'plan_activities' with args: {"destination": "Paris", ...}
   2025-11-03 21:30:03 - __main__ - INFO - ✅ [MCP] Tool 'plan_activities' executed successfully
   ```

**Protocol Used**: REST (user) → **MCP** (coordinator ↔ agents)

---

### **Scenario 2: External A2A Agent Discovers Your Service**

**External Action**: Another A2A-compliant agent queries your Agent Card

**Expected Log Flow**:

1. **A2A Discovery Request**:
   ```
   INFO:     20.30.40.50:12345 - "GET /a2a/ HTTP/1.1" 200 OK
   2025-11-03 21:35:00 - agent.a2a_server - INFO -  [A2A] Agent Card requested
   ```

2. **A2A Task Delegation**:
   ```
   INFO:     20.30.40.50:12345 - "POST /a2a/tasks/send HTTP/1.1" 200 OK
   2025-11-03 21:35:10 - agent.a2a_server - INFO -  [A2A] Task received: trip_planning_sk
   2025-11-03 21:35:10 - agent.a2a_server - INFO -  [A2A] Task description: Plan a trip to Tokyo
   ```

3. **Coordinator processes A2A task and uses MCP internally**:
   ```
   2025-11-03 21:35:11 - agent - INFO -  [MCP] Calling tool 'convert_amount' on currency-agent
   2025-11-03 21:35:12 - agent - INFO -  [MCP] Calling tool 'plan_activities' on activity-agent
   ```

**Protocol Used**: **A2A** (external agent → coordinator) → **MCP** (coordinator → internal agents)

---

##  Key Log Patterns to Look For

### **MCP Communication**

| Log Message | Meaning |
|-------------|---------|
| ` [MCP] Currency Agent: http://currency-agent:8001` | Coordinator knows MCP agent URL |
| ` [MCP] Received request: tools/call` | MCP agent received tool execution request |
| ` [MCP] Calling tool 'convert_amount'` | MCP tool is being executed |
| `✅ [MCP] Tool 'convert_amount' executed successfully` | MCP tool completed |
| `❌ [MCP] Error processing request` | MCP call failed |

### **A2A Communication**

| Log Message | Meaning |
|-------------|---------|
| ` [A2A] Server configured for 0.0.0.0:8000` | A2A server started |
| `✅ [A2A] A2A server mounted at /a2a` | A2A endpoints available |
| ` [A2A] Agent Card requested` | External agent discovered your service |
| ` [A2A] Task received` | External agent delegated a task |
| ` [A2A] Streaming task updates` | A2A streaming response in progress |

### **REST API (Web UI)**

| Log Message | Meaning |
|-------------|---------|
| `INFO: ... "GET / HTTP/1.1" 200 OK` | User opened Web UI |
| `INFO: ... "POST /api/chat/message HTTP/1.1" 200 OK` | User sent chat message |
| `INFO: ... "GET /health HTTP/1.1" 200 OK` | Health check (K8s probes) |

---

##  Testing Each Protocol

### **Test MCP** (Internal Tool Execution)

```bash
# Send a travel query that requires currency and activity tools
curl -X POST http://<YOUR-PUBLIC-IP>/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Convert 100 USD to JPY and suggest activities in Tokyo",
    "session_id": "test-session"
  }'

# Watch logs
kubectl logs -n multiagent-microservices deployment/coordinator -f | grep "\[MCP\]"
```

### **Test A2A** (Agent Discovery)

```bash
# Get Agent Card (A2A discovery)
curl http://<YOUR-PUBLIC-IP>/a2a/

# Send A2A task
curl -X POST http://<YOUR-PUBLIC-IP>/a2a/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "id": "test-task-123",
      "skill": "trip_planning_sk",
      "description": "Plan a 3-day trip to Seoul"
    }
  }'

# Watch logs
kubectl logs -n multiagent-microservices deployment/coordinator -f | grep "\[A2A\]"
```

---

##  Visual Log Flow Diagram

```
┌─────────────┐
│   User      │
│   Browser   │
└──────┬──────┘
       │ HTTP (Web UI)
       ▼
┌──────────────────────────────────────────┐
│        Coordinator Pod                   │
│  ┌────────────────────────────────────┐  │
│  │  [REST] User request received      │  │  ← Log: "POST /api/chat/message"
│  └────────┬───────────────────────────┘  │
│           │                               │
│           ▼                               │
│  ┌────────────────────────────────────┐  │
│  │  [MCP] Decide which tools to call  │  │  ← Log: " [MCP] Calling tool..."
│  └────────┬───────────────────────────┘  │
│           │                               │
│           ├────────────────┬─────────────┤
│           ▼                ▼              │
│  HTTP to currency:8001  HTTP to activity:8002
└───────────┼────────────────┼──────────────┘
            │                │
            ▼                ▼
    ┌────────────┐   ┌────────────┐
    │ Currency   │   │ Activity   │
    │   Agent    │   │   Agent    │
    ├────────────┤   ├────────────┤
    │ [MCP]      │   │ [MCP]      │  ← Logs: " [MCP] Received request"
    │ Received   │   │ Received   │          "✅ [MCP] Tool executed"
    │ tools/call │   │ tools/call │
    └────────────┘   └────────────┘


Separate Flow - External A2A Agent:

┌─────────────┐
│  External   │
│  A2A Agent  │
└──────┬──────┘
       │ HTTP (A2A Protocol)
       ▼
┌──────────────────────────────────────────┐
│        Coordinator Pod                   │
│  ┌────────────────────────────────────┐  │
│  │  [A2A] Agent Card / Task received  │  │  ← Logs: " [A2A] Agent Card requested"
│  └────────┬───────────────────────────┘  │          " [A2A] Task received"
│           │                               │
│           ▼ (internally uses MCP)         │
│  Same flow as above...                   │
└──────────────────────────────────────────┘
```

---

##  Quick Reference

### **To see MCP in action:**
1. Open Web UI: http://<YOUR-PUBLIC-IP>
2. Ask: "Convert 500 USD to EUR and plan Paris activities"
3. Watch: `kubectl logs -n multiagent-microservices deployment/coordinator -f | grep MCP`

### **To see A2A in action:**
1. From terminal: `curl http://<YOUR-PUBLIC-IP>/a2a/`
2. Watch: `kubectl logs -n multiagent-microservices deployment/coordinator -f | grep A2A`

### **To see everything:**
```bash
kubectl logs -n multiagent-microservices deployment/coordinator -f
```

---

##  Summary

- **MCP = Internal communication** between coordinator and specialized agents (currency, activity)
- **A2A = External communication** for agent discovery and task delegation
- **Web UI = User-facing** REST API for direct chat interaction
- **All protocols can work together** in a single request flow!

