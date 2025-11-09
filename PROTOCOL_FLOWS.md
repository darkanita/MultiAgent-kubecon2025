# A2A vs MCP Protocol Flow Diagrams

## Overview

This document shows the **visual flow** of how **A2A** and **MCP** protocols work in the Phase 2 microservices architecture.

---

## 🌐 Flow 1: Web UI User → MCP Tool Execution

**Summary**: User interacts with Web UI, coordinator uses **MCP protocol** to call specialized agent tools.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                                │
└─────────────────────────────────────────────────────────────────────────┘

User opens browser → http://<YOUR-PUBLIC-IP>
User types: "Convert 100 USD to EUR and plan activities in Paris"
User clicks Send

                              │
                              │ (1) HTTP POST /api/chat/message
                              │     Protocol: REST API
                              ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                      COORDINATOR POD (8000)                             │
│                      service/coordinator-service (LoadBalancer)         │
│                                                                         │
│  Step 1: REST API Receives Request                                     │
│  Log: INFO: "POST /api/chat/message HTTP/1.1" 200 OK                   │
│  ───────────────────────────────────────────────────────────────────   │
│                              │                                          │
│                              │ (2) Process with Semantic Kernel         │
│                              ▼                                          │
│  Step 2: TravelManagerAgent Analyzes Query                             │
│  Log: "Processing user request with TravelManagerAgent"                │
│  ───────────────────────────────────────────────────────────────────   │
│                              │                                          │
│                              │ (3) Azure OpenAI Function Calling        │
│                              │     Determines which tools to use        │
│                              ▼                                          │
│  Step 3: MCP Client Prepares Tool Calls                                │
│  Log: "🔌 [MCP] Calling tool 'convert_amount' on currency-agent"       │
│  Log: "🔌 [MCP] Calling tool 'plan_activities' on activity-agent"      │
│                              │                                          │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              │ (4) MCP Protocol over HTTP      │
              │     JSON-RPC 2.0 Format         │
              │     POST /mcp/v1                │
              │                                 │
              ▼                                 ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│   CURRENCY AGENT (8001)     │   │   ACTIVITY AGENT (8002)     │
│   service/currency-agent    │   │   service/activity-agent    │
│         ClusterIP           │   │         ClusterIP           │
├─────────────────────────────┤   ├─────────────────────────────┤
│                             │   │                             │
│  🔧 MCP SERVER              │   │  🔧 MCP SERVER              │
│                             │   │                             │
│  Receives:                  │   │  Receives:                  │
│  POST /mcp/v1               │   │  POST /mcp/v1               │
│  {                          │   │  {                          │
│    "jsonrpc": "2.0",        │   │    "jsonrpc": "2.0",        │
│    "method": "tools/call",  │   │    "method": "tools/call",  │
│    "params": {              │   │    "params": {              │
│      "name": "convert_amt", │   │      "name": "plan_act",    │
│      "arguments": {         │   │      "arguments": {         │
│        "amount": 100,       │   │        "destination": "...", │
│        "from": "USD",       │   │        "days": 3,           │
│        "to": "EUR"          │   │        "budget": "moderate" │
│      }                      │   │      }                      │
│    }                        │   │    }                        │
│  }                          │   │  }                          │
│                             │   │                             │
│  Logs:                      │   │  Logs:                      │
│  📨 [MCP] Received request  │   │  📨 [MCP] Received request  │
│  🚀 [MCP] Calling tool      │   │  🚀 [MCP] Calling tool      │
│     convert_amount          │   │     plan_activities         │
│  💱 Calling Frankfurter API │   │  🤖 Generating suggestions  │
│  ✅ [MCP] Tool executed     │   │  ✅ [MCP] Tool executed     │
│                             │   │                             │
│  Returns:                   │   │  Returns:                   │
│  {                          │   │  {                          │
│    "content": [             │   │    "content": [             │
│      {                      │   │      {                      │
│        "type": "text",      │   │        "type": "text",      │
│        "text": "92.15 EUR"  │   │        "text": "Day 1: ..." │
│      }                      │   │      }                      │
│    ]                        │   │    ]                        │
│  }                          │   │  }                          │
└─────────────┬───────────────┘   └─────────────┬───────────────┘
              │                                 │
              │ (5) MCP Response (JSON-RPC)     │
              └────────────────┬────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      COORDINATOR POD (8000)                             │
│                                                                         │
│  Step 4: Aggregate MCP Results                                         │
│  Log: "✅ Received response from currency-agent: 92.15 EUR"             │
│  Log: "✅ Received response from activity-agent: 3-day plan"            │
│  ───────────────────────────────────────────────────────────────────   │
│                              │                                          │
│                              │ (6) Azure OpenAI Formats Response        │
│                              │     gpt-4o-mini combines results         │
│                              ▼                                          │
│  Step 5: Generate Natural Language Response                            │
│  • "100 USD equals approximately 92.15 EUR"                            │
│  • "Here's a suggested 3-day itinerary for Paris..."                   │
│  • "Day 1: Visit Eiffel Tower, Louvre Museum..."                       │
│                                                                         │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
                               │ (7) HTTP Response (JSON)
                               ▼
                       ┌──────────────┐
                       │ User Browser │
                       │ Displays:    │
                       │ "100 USD =   │
                       │  92.15 EUR   │
                       │              │
                       │ Day 1:       │
                       │ • Eiffel...  │
                       └──────────────┘
```

**Key Logs to Watch**:
```bash
# Coordinator logs show MCP calls
kubectl logs -n multiagent-microservices deployment/coordinator -f | grep "\[MCP\]"

# Currency agent shows MCP tool execution
kubectl logs -n multiagent-microservices deployment/currency-agent -f

# Activity agent shows MCP tool execution  
kubectl logs -n multiagent-microservices deployment/activity-agent -f
```

---

## 📡 Flow 2: External A2A Agent → Service Discovery & Delegation

**Summary**: External A2A agent discovers your service, delegates a task, coordinator uses **MCP internally** to execute.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL A2A AGENT                                   │
│                  (Running on another platform)                          │
│                  Example: Google Gemini Agent, Copilot Agent            │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ "I need a travel agent to help plan a trip"
                               │
                               │ (1) GET /a2a/
                               │     Protocol: A2A Discovery
                               │     Purpose: Find available agents
                               ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                      COORDINATOR POD (8000)                             │
│                      http://<YOUR-PUBLIC-IP>/a2a/                          │
│                                                                         │
│  📡 A2A SERVER                                                          │
│                                                                         │
│  Step 1: Agent Card Discovery                                          │
│  Log: "📡 [A2A] Agent Card requested"                                   │
│  Log: "🌐 Agent Card available at http://0.0.0.0:8000/a2a/"            │
│                                                                         │
│  Returns Agent Card (A2A JSON Format):                                 │
│  {                                                                      │
│    "name": "SK Travel Agent",                                          │
│    "description": "Multi-agent travel planning system with             │
│                    currency conversion and activity planning",          │
│    "capabilities": {                                                    │
│      "streaming": true,                                                │
│      "async": true                                                     │
│    },                                                                   │
│    "skills": [                                                         │
│      {                                                                  │
│        "id": "trip_planning_sk",                                       │
│        "name": "Semantic Kernel Trip Planning",                        │
│        "description": "Plan trips with currency and activities",       │
│        "tags": ["trip", "planning", "currency", "activities"]          │
│      }                                                                  │
│    ]                                                                    │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ External agent reads the card
                               │ "Perfect! This agent can help with trip planning"
                               │
                               │ (2) POST /a2a/tasks/send
                               │     Protocol: A2A Task Delegation
                               │     Body: Task description + parameters
                               ▼

┌─────────────────────────────────────────────────────────────────────────┐
│                      COORDINATOR POD (8000)                             │
│                                                                         │
│  📡 A2A SERVER                                                          │
│                                                                         │
│  Step 2: Receive A2A Task                                              │
│  Log: "📥 [A2A] Task received: trip_planning_sk"                        │
│  Log: "📋 [A2A] Task description: Plan a 3-day trip to Tokyo"          │
│  Log: "💰 [A2A] Task parameters: budget=$200/day, dates=Nov 15-17"     │
│  ───────────────────────────────────────────────────────────────────   │
│                              │                                          │
│                              │ (3) A2A → Internal Processing            │
│                              │     Convert A2A task to SK prompt        │
│                              ▼                                          │
│  Step 3: Process with TravelManagerAgent                               │
│  Log: "🤖 Processing A2A task with Semantic Kernel"                    │
│  Log: "🔌 [MCP] Calling tool 'convert_amount' on currency-agent"       │
│  Log: "🔌 [MCP] Calling tool 'plan_activities' on activity-agent"      │
│                              │                                          │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              │ (4) MCP Protocol                │
              │     (Internal Tool Execution)   │
              │     Same as Flow 1 above        │
              ▼                                 ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│  CURRENCY AGENT (8001)      │   │  ACTIVITY AGENT (8002)      │
│  🔧 MCP SERVER              │   │  🔧 MCP SERVER              │
│                             │   │                             │
│  Logs:                      │   │  Logs:                      │
│  📨 [MCP] Received request  │   │  📨 [MCP] Received request  │
│  🚀 [MCP] Calling tool      │   │  🚀 [MCP] Calling tool      │
│  ✅ [MCP] Tool executed     │   │  ✅ [MCP] Tool executed     │
│                             │   │                             │
│  Returns: 200 USD = 30,000  │   │  Returns: Day 1: Shibuya    │
│           JPY               │   │           Day 2: Asakusa... │
└─────────────┬───────────────┘   └─────────────┬───────────────┘
              │                                 │
              │ (5) MCP Results                 │
              └────────────────┬────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      COORDINATOR POD (8000)                             │
│                                                                         │
│  Step 4: Format A2A Task Result                                        │
│  Log: "✅ [A2A] Task completed successfully"                            │
│  Log: "📤 [A2A] Returning result to external agent"                    │
│                                                                         │
│  Returns A2A Response:                                                 │
│  {                                                                      │
│    "taskId": "task-abc-123",                                           │
│    "status": "completed",                                              │
│    "result": {                                                         │
│      "trip_plan": {                                                    │
│        "destination": "Tokyo",                                         │
│        "duration": "3 days",                                           │
│        "budget_breakdown": {                                           │
│          "total_usd": 600,                                             │
│          "total_jpy": 90000,                                           │
│          "per_day": 30000                                              │
│        },                                                              │
│        "itinerary": [                                                  │
│          {"day": 1, "activities": ["Shibuya", "Meiji Shrine"]},       │
│          {"day": 2, "activities": ["Asakusa", "Tokyo Tower"]},        │
│          {"day": 3, "activities": ["Akihabara", "Imperial Palace"]}   │
│        ]                                                               │
│      }                                                                 │
│    },                                                                  │
│    "metadata": {                                                       │
│      "processing_time_ms": 3500,                                       │
│      "tools_called": ["convert_amount", "plan_activities"]            │
│    }                                                                   │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ (6) HTTP Response (A2A Format)
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL A2A AGENT                                   │
│                                                                         │
│  Receives structured task result                                       │
│  Can now present to its user or delegate further                       │
│                                                                         │
│  "I received a detailed Tokyo trip plan from SK Travel Agent!"         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Logs to Watch**:
```bash
# A2A discovery logs
kubectl logs -n multiagent-microservices deployment/coordinator -f | grep "\[A2A\]"

# You'll see BOTH A2A and MCP logs together
kubectl logs -n multiagent-microservices deployment/coordinator -f | grep -E "\[A2A\]|\[MCP\]"
```

---

## 🔑 Key Protocol Differences

| Aspect | A2A Protocol 📡 | MCP Protocol 🔧 |
|--------|----------------|-----------------|
| **Purpose** | Agent discovery & task delegation | Tool/function execution |
| **Direction** | External → Coordinator | Coordinator → Internal Agents |
| **Endpoint** | `/a2a/`, `/a2a/tasks/send` | `/mcp/v1` (internal) |
| **Format** | A2A JSON schema (agent cards, tasks) | JSON-RPC 2.0 (tools/call) |
| **Log Prefix** | `[A2A]` 📡 | `[MCP]` 🔧 |
| **When Used** | Other agents discover your service | Your coordinator needs specific tools |
| **Example Request** | "Discover available agents" | "Call convert_amount tool" |
| **Network** | External (LoadBalancer, public IP) | Internal (ClusterIP, K8s DNS) |
| **Visibility** | Internet-facing (http://<YOUR-PUBLIC-IP>/a2a/) | Private cluster (http://currency-agent:8001) |
| **Authentication** | Could use API keys, OAuth (not implemented) | No auth needed (internal network) |
| **Use Case** | Multi-platform agent collaboration | Microservices tool orchestration |

---

## 🧪 Testing Commands

### **Test Flow 1: Web UI → MCP**

```bash
# Open browser
open http://<YOUR-PUBLIC-IP>

# Or use curl
curl -X POST http://<YOUR-PUBLIC-IP>/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Convert 100 USD to EUR and suggest Paris activities",
    "session_id": "test-123"
  }'

# Watch MCP logs (3 terminals)
kubectl logs -n multiagent-microservices deployment/coordinator -f | grep "\[MCP\]"
kubectl logs -n multiagent-microservices deployment/currency-agent -f
kubectl logs -n multiagent-microservices deployment/activity-agent -f
```

### **Test Flow 2: A2A Discovery**

```bash
# Get Agent Card (A2A discovery)
curl http://<YOUR-PUBLIC-IP>/a2a/ | jq

# Expected response: Agent Card JSON with skills

# Send A2A task
curl -X POST http://<YOUR-PUBLIC-IP>/a2a/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "id": "test-task-456",
      "skill": "trip_planning_sk",
      "description": "Plan a 3-day trip to Tokyo with $200/day budget"
    }
  }' | jq

# Watch A2A logs
kubectl logs -n multiagent-microservices deployment/coordinator -f | grep "\[A2A\]"
```

---

## 📊 Summary

### **When You'll See Each Protocol:**

1. **User opens Web UI** → REST API → **MCP** (internal tools)
   - Log pattern: `POST /api/chat/message` → `[MCP] Calling tool`

2. **External agent queries `/a2a/`** → **A2A** (discovery)
   - Log pattern: `GET /a2a/` → `[A2A] Agent Card requested`

3. **External agent sends task** → **A2A** (delegation) → **MCP** (internal execution)
   - Log pattern: `POST /a2a/tasks/send` → `[A2A] Task received` → `[MCP] Calling tool`

### **The Big Picture:**

```
External World          Coordinator           Internal Agents
─────────────          ───────────          ───────────────

  Web UI    ──REST──▶   [REST API]
                           │
                           ▼
                        [SK Agent] ──MCP──▶ [Currency Agent]
                           │                [Activity Agent]
                           ▼
                        [OpenAI]

External Agent ─A2A──▶  [A2A Server]
                           │
                           ▼
                        [SK Agent] ──MCP──▶ [Currency Agent]
                           │                [Activity Agent]
                           ▼
                        [OpenAI]
```

**Both flows converge** on the Semantic Kernel agent, which always uses **MCP internally** to call specialized tools! 🎯
