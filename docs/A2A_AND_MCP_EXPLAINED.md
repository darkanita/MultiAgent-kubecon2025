# A2A Protocol in Microservices Architecture

## 🤔 The Question: Where Does A2A Fit in Phase 2?

**Short Answer**: A2A protocol stays **only in the Coordinator Service**. Agent microservices use **MCP protocol only**.

---

## 📡 A2A Protocol Role

### **What A2A Does**

A2A (Agent-to-Agent) protocol enables:
1. **Agent Discovery**: External agents find your agent via Agent Card
2. **Task Delegation**: External agents send tasks to your agent
3. **Cross-Platform Communication**: Google A2A standard for agent interop
4. **Streaming Responses**: Real-time progress updates

### **A2A Endpoints**

```
GET  /a2a/              → Agent Card (discovery)
POST /a2a/tasks/send    → Send task (synchronous)
POST /a2a/tasks/stream  → Stream task (real-time)
```

---

## 🏗️ Architecture: A2A + MCP Together

### **Phase 2 Protocol Layers**

```
External World (Other A2A Agents)
            │
            │ A2A Protocol
            │ (Agent-to-Agent Communication)
            ▼
┌───────────────────────────────────┐
│    Coordinator Service            │
│                                   │
│  ┌─────────────────────────────┐ │
│  │  A2A Server                 │ │  ◄── A2A lives here!
│  │  - Agent Card               │ │
│  │  - Task handling            │ │
│  │  - External discovery       │ │
│  └────────────┬────────────────┘ │
│               │                   │
│               ▼                   │
│  ┌─────────────────────────────┐ │
│  │  TravelManager Agent        │ │
│  │  (Semantic Kernel)          │ │
│  └────────────┬────────────────┘ │
│               │                   │
│               ▼                   │
│  ┌─────────────────────────────┐ │
│  │  MCP Coordinator (Client)   │ │  ◄── MCP client here!
│  └────────────┬────────────────┘ │
└───────────────┼───────────────────┘
                │
                │ MCP Protocol
                │ (Inter-Service Communication)
                │
        ┌───────┴────────┬──────────────┐
        │                │              │
        ▼                ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Currency     │  │ Activity     │  │ Future       │
│ Agent Svc    │  │ Agent Svc    │  │ Agents       │
│              │  │              │  │              │
│ MCP Server   │  │ MCP Server   │  │ MCP Server   │
│ (Tools)      │  │ (Tools)      │  │ (Tools)      │
└──────────────┘  └──────────────┘  └──────────────┘
      ▲                ▲                  ▲
      │                │                  │
      └────────────────┴──────────────────┘
         NO A2A exposed from agent services!
```

---

## 🔑 Key Design Principle

### **Single Entry Point Pattern**

```
External Agents
      │
      │ A2A Protocol
      ▼
┌─────────────────┐
│  Coordinator    │  ◄── Only service exposed externally
│  (Gateway)      │      Only service with A2A
└────────┬────────┘
         │
         │ MCP Protocol
         │
         ▼
    Internal Agent Services
    (Not exposed externally)
    (No A2A servers)
```

**Why?**
1. **Security**: Only one public entry point
2. **Simplicity**: Agent services focus on tools, not protocols
3. **Flexibility**: Can change internal architecture without affecting external API
4. **Consistency**: Single Agent Card represents entire system

---

## 📝 Phase 2 Implementation Details

### **Coordinator Service Responsibilities**

```python
# src/services/coordinator/main.py

# 1️⃣ A2A Server - External agent communication
a2a_server = A2AServer(httpx_client, host="0.0.0.0", port=8000)
app.mount("/a2a", a2a_server.get_starlette_app())

# 2️⃣ MCP Client - Internal agent communication
mcp_coordinator = MCPCoordinator()
await mcp_coordinator.register_agent("currency-agent", ...)
await mcp_coordinator.register_agent("activity-agent", ...)

# 3️⃣ REST API - Direct user communication
app.include_router(chat_router, prefix="/api/chat")

# 4️⃣ Web UI - Browser interface
app.mount("/static", StaticFiles(...))
```

### **Agent Service Responsibilities**

```python
# src/services/currency-agent/main.py

# ✅ MCP Server ONLY
server = CurrencyMCPServer()
await server.run()

# ❌ NO A2A Server
# NO a2a_server = A2AServer(...)
# Agent services don't handle external discovery
```

---

## 🔄 Request Flow Examples

### **Example 1: External A2A Agent → Your System**

```
1. External Agent discovers your agent
   ↓
   GET http://coordinator:80/a2a/
   (Returns Agent Card)

2. External Agent sends task
   ↓
   POST http://coordinator:80/a2a/tasks/send
   Body: {"message": "Convert 100 USD to EUR"}

3. Coordinator receives A2A task
   ↓
   A2A Server → TravelManager Agent

4. TravelManager delegates via MCP
   ↓
   MCP Client → Currency Agent Service
   POST http://currency-agent:8001/mcp/call_tool

5. Currency Agent processes
   ↓
   Returns result to Coordinator

6. Coordinator returns to External Agent
   ↓
   A2A response: {"result": "86.85 EUR"}
```

**Protocols Used**:
- External → Coordinator: **A2A**
- Coordinator → Agents: **MCP**

### **Example 2: User via Web UI → Your System**

```
1. User types in browser
   ↓
   POST http://coordinator:80/api/chat/message
   Body: {"message": "Convert 100 USD to EUR"}

2. Coordinator receives REST request
   ↓
   REST API → TravelManager Agent

3. TravelManager delegates via MCP
   ↓
   MCP Client → Currency Agent Service
   POST http://currency-agent:8001/mcp/call_tool

4. Currency Agent processes
   ↓
   Returns result to Coordinator

5. Coordinator returns to User
   ↓
   HTTP response: {"response": "86.85 EUR"}
```

**Protocols Used**:
- User → Coordinator: **REST (HTTP)**
- Coordinator → Agents: **MCP**

---

## 🎯 Why This Design?

### **Advantages**

1. **Single Agent Card**
   - External agents see one unified agent
   - Internal complexity hidden
   - Easier to maintain Agent Card

2. **Security**
   - Only coordinator exposed externally
   - Agent services are internal-only (ClusterIP)
   - Reduced attack surface

3. **Flexibility**
   - Can add/remove internal agents without updating A2A
   - Can change MCP implementation without affecting A2A
   - Protocols are decoupled

4. **Scalability**
   - Agent services can scale independently
   - Coordinator remains stable gateway
   - No need to update external agents when scaling

### **Alternative Design (Not Recommended)**

```
❌ Each agent exposes both A2A and MCP:

External Agents
    ├─ A2A → Currency Agent (has A2A server)
    ├─ A2A → Activity Agent (has A2A server)
    └─ A2A → Coordinator (has A2A server)

Problems:
- Multiple Agent Cards to maintain
- External agents confused about which to call
- More complex security (3+ public endpoints)
- Coordinator can't intercept/coordinate
```

---

## 📊 Kubernetes Service Types

```yaml
# Coordinator - Exposed Externally
apiVersion: v1
kind: Service
metadata:
  name: coordinator-service
spec:
  type: LoadBalancer  # ◄── External IP assigned
  ports:
  - port: 80
    targetPort: 8000
  # A2A available at: http://<external-ip>/a2a/

---
# Currency Agent - Internal Only
apiVersion: v1
kind: Service
metadata:
  name: currency-agent
spec:
  type: ClusterIP  # ◄── Internal only, no external IP
  ports:
  - port: 8001
  # MCP only, not accessible from outside cluster

---
# Activity Agent - Internal Only
apiVersion: v1
kind: Service
metadata:
  name: activity-agent
spec:
  type: ClusterIP  # ◄── Internal only, no external IP
  ports:
  - port: 8002
  # MCP only, not accessible from outside cluster
```

---

## 🧪 Testing A2A in Phase 2

### **Test A2A Discovery**

```bash
# Get coordinator external IP
EXTERNAL_IP=$(kubectl get svc coordinator-service -n multiagent-kubecon-simple -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Get Agent Card
curl http://${EXTERNAL_IP}/a2a/

# Expected response:
{
  "name": "SK Travel Agent",
  "description": "Semantic Kernel-based travel agent...",
  "url": "http://coordinator-service/",
  "skills": [
    {
      "id": "trip_planning_sk",
      "name": "Semantic Kernel Trip Planning",
      ...
    }
  ]
}
```

### **Test A2A Task Execution**

```bash
# Send task via A2A
curl -X POST "http://${EXTERNAL_IP}/a2a/tasks/send" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "content": "Convert 500 USD to EUR"
    }
  }'

# Watch logs - should see:
# Coordinator: 📡 [A2A] Executing request
# Coordinator: 🚀 [MCP] Calling tool on currency-agent
# Currency:    📥 Received tool call
```

### **Verify Agent Services Don't Have A2A**

```bash
# Try to access A2A on currency agent (should fail)
kubectl exec -it deployment/coordinator-service -n multiagent-kubecon-simple -- \
  curl http://currency-agent:8001/a2a/

# Expected: 404 Not Found or connection refused
# Correct behavior - agent services don't expose A2A!
```

---

## 📝 A2A Agent Executor Updates

### **Executor Needs MCP Coordinator**

The `agent_executor.py` will need to use MCP coordinator:

```python
# src/agent/agent_executor.py

from src.agent.mcp_coordinator import MCPCoordinator

class SemanticKernelTravelAgentExecutor(AgentExecutor):
    def __init__(self):
        self.agent = SemanticKernelTravelAgent()
        self.mcp_coordinator = MCPCoordinator()  # ◄── Use MCP to call agents

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        query = context.get_user_input()
        logger.info(f"📡 [A2A] Executing request: '{query}'")
        
        # Agent determines which tools to call
        # Internally, agent uses MCP coordinator to call agent services
        async for partial in self.agent.stream(query, task.contextId):
            # ... streaming logic
            logger.info(f"✅ [A2A] Task completed successfully")
```

---

## 🎓 Summary

| Protocol | Scope | Used By | Purpose |
|----------|-------|---------|---------|
| **A2A** | External | Coordinator only | Agent discovery, external task delegation |
| **MCP** | Internal | Coordinator + Agents | Inter-service tool invocation |
| **REST** | External | Coordinator only | Direct user API |
| **HTTP** | Internal | All services | Health checks, MCP wrapper |

### **Protocol Layers**

```
┌──────────────────────────────────────┐
│  External Protocols                  │
│  • A2A (Agent discovery/tasks)       │  ◄── Coordinator only
│  • REST (User API)                   │  ◄── Coordinator only
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  Internal Protocols                  │
│  • MCP (Inter-agent communication)   │  ◄── All services
│  • HTTP (Health, internal APIs)      │  ◄── All services
└──────────────────────────────────────┘
```

---

## ✅ Checklist: A2A in Phase 2

- [ ] A2A Server mounted in coordinator: `app.mount("/a2a", ...)`
- [ ] A2A endpoint accessible: `curl http://<external-ip>/a2a/`
- [ ] Agent Card returns correct info
- [ ] A2A tasks can be sent and executed
- [ ] A2A executor uses MCP coordinator internally
- [ ] Agent services do NOT expose A2A (only MCP)
- [ ] Logs show: `📡 [A2A]` in coordinator, `🚀 [MCP]` for agent calls

---

## 🚀 Next Steps

1. **Review**: Understand A2A stays in coordinator
2. **Implement**: Follow Phase 2 implementation plan
3. **Test**: Verify A2A endpoint works externally
4. **Monitor**: Watch logs for A2A → MCP flow

---

**Key Takeaway**: A2A is the **external face** of your system, while MCP is the **internal nervous system**. They work together, not separately!
