# KubeCon 2025 Presentation Guide
## Demonstrating A2A + MCP in Multi-Agent Systems

---

## 🎯 Presentation Objective

Show how **Agent-to-Agent (A2A)** and **Model Context Protocol (MCP)** enable scalable, interoperable multi-agent systems on Kubernetes.

**Key Message**: *"Building production-ready AI agent systems requires standardized protocols for both external discovery (A2A) and internal tool execution (MCP)."*

---

## 📊 Demo Flow (15-20 minutes)

### Part 1: The Problem (2 min)

**Slide**: Traditional challenges in multi-agent systems
- Agent discovery: How do agents find each other?
- Protocol standardization: How do they communicate?
- Tool execution: How do agents use external capabilities?
- Scalability: How do we deploy this in production?

**Message**: "We need industry standards for agent collaboration"

---

### Part 2: The Solution - Dual Protocol Architecture (3 min)

**Slide**: Architecture diagram

```
External Agents (Internet)
        ↓
    A2A Protocol ←── Agent Discovery & Task Delegation
        ↓
  Coordinator Service (AKS)
        ↓
    MCP Protocol ←── Internal Tool Execution  
        ↓
Specialized Agents (Currency, Activity, Future: HR, Flight, Hotel)
```

**Key Points**:
1. **A2A Protocol** (Google): For external agent interoperability
2. **MCP Protocol** (Anthropic): For internal tool invocation
3. **Kubernetes**: For production deployment and scaling

---

### Part 3: Live Demo - A2A Discovery (5 min)

**Terminal 1**: Run the demo script
```bash
python demo_a2a_mcp_flow.py
```

**What to show**:
1. **Agent Card Discovery** ✅ 
   - Show the JSON response with agent capabilities
   - Explain: "Any A2A-compliant agent can discover this service"
   - Point out: Skills, capabilities, protocols supported

2. **What the Agent Card Contains**:
   ```json
   {
     "name": "SK Travel Agent",
     "skills": [
       {
         "id": "trip_planning_sk",
         "name": "Semantic Kernel Trip Planning",
         "tags": ["trip", "planning", "currency"]
       }
     ],
     "capabilities": {
       "streaming": true
     }
   }
   ```

**Talking Points**:
- "This is like a business card for AI agents"
- "Other agents can discover what we do without human intervention"
- "Follows Google's A2A specification for interoperability"

---

### Part 4: Live Demo - Working Multi-Agent System (5 min)

**Terminal 2**: Show the REST API in action
```bash
curl -X POST http://<YOUR-PUBLIC-IP>/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Plan a 3-day trip to Tokyo with $150/day budget. Convert to JPY",
    "session_id": "kubecon-demo"
  }'
```

**What to show**:
1. **Real-time response** with:
   - Currency conversion (USD → JPY via Frankfurter API)
   - Day-by-day itinerary for Tokyo
   - Budget-appropriate recommendations

2. **Behind the scenes** (show logs):
   ```bash
   kubectl logs -f coordinator-5c99866c54-stp4z -n multiagent-microservices
   ```

**Key Log Lines to Point Out**:
- `Calling CurrencyExchangeAgent-CurrencyExchangeAgent`
- `Calling CurrencyPlugin-get_exchange_rate`
- `HTTP Request: GET https://api.frankfurter.app/latest`
- `Function succeeded`

**Talking Points**:
- "TravelManager analyzes the request"
- "Delegates to CurrencyExchangeAgent for conversion"
- "Delegates to ActivityPlannerAgent for itinerary"
- "All orchestrated through Semantic Kernel"

---

### Part 5: MCP Architecture Explanation (3 min)

**Slide**: MCP Tool Definitions

Show the code structure:
```
src/agent/
├── mcp_currency_server.py   ← Currency tools
├── mcp_activity_server.py   ← Activity planning tools
└── mcp_coordinator.py       ← MCP client
```

**MCP Tools Available**:

🔧 **Currency Agent**:
- `get_exchange_rate(from, to, date)` - Get current rates
- `convert_amount(amount, from, to)` - Convert money

🔧 **Activity Agent**:
- `plan_activities(destination, days, budget)` - Create itinerary
- `suggest_restaurants(location, cuisine, budget)` - Dining recommendations
- `suggest_attractions(location, category)` - Tourist spots

**Talking Points**:
- "MCP provides type-safe tool definitions"
- "Each agent is an independent microservice"
- "Easy to add new agents (HR, Flight, Hotel)"
- "Follows Anthropic's Model Context Protocol spec"

---

### Part 6: Kubernetes Deployment (2 min)

**Terminal 3**: Show the pods
```bash
kubectl get pods -n multiagent-microservices
```

**Output**:
```
NAME                              READY   STATUS    RESTARTS   AGE
coordinator-5c99866c54-stp4z      1/1     Running   0          5d7h
currency-agent-778fcddd7c-vhxxs   1/1     Running   0          5d8h
activity-agent-6dc6b6f455-zmmtr   1/1     Running   0          5d8h
```

**Show Services**:
```bash
kubectl get svc -n multiagent-microservices
```

**Talking Points**:
- "Each agent runs in its own pod"
- "Independent scaling and deployment"
- "Service discovery via Kubernetes DNS"
- "Production-ready architecture on Azure AKS"

---

## 🎓 Educational Moments

### Moment 1: Protocol Complementarity

**Question**: "Why do we need BOTH A2A and MCP?"

**Answer**:
- **A2A**: For external interoperability (like HTTP for the web)
  - Agent discovery
  - Cross-organization delegation
  - Platform-independent

- **MCP**: For internal capabilities (like function calling for LLMs)
  - Standardized tool interface
  - Type-safe schemas
  - Optimized for AI model consumption

**Analogy**: "A2A is like DNS (finding services), MCP is like REST APIs (using services)"

---

### Moment 2: Current State vs. Vision

**Be Honest About Implementation**:

**Current State** ✅:
- Multi-agent system fully operational
- A2A discovery working
- Semantic Kernel orchestration working
- Kubernetes deployment working
- REST API working

**In Progress** ⚠️:
- A2A task delegation (method `tasks.send`)
- MCP HTTP communication (currently in-process)

**Vision** 🎯:
- Complete dual-protocol integration
- True microservices with MCP HTTP
- Dynamic agent registration

**Message**: "This shows the real-world journey of implementing emerging protocols"

---

### Moment 3: Why This Matters

**For the Industry**:
1. **Interoperability**: Agents from different vendors can work together
2. **Standardization**: No vendor lock-in
3. **Scalability**: Cloud-native deployment patterns
4. **Composability**: Mix and match capabilities

**For Developers**:
1. **Clear separation of concerns**: Discovery vs. Execution
2. **Type safety**: MCP provides schemas for tools
3. **Testing**: Can test agents independently
4. **Evolution**: Can upgrade protocols without breaking agents

---

## 🎬 Demo Script (Detailed)

### Opening (30 seconds)

> "Today I'll show you how we built a production multi-agent travel planning system using two emerging protocols: Google's A2A for agent discovery and Anthropic's MCP for tool execution. This is deployed on Azure Kubernetes Service and demonstrates how standardized protocols enable scalable AI agent systems."

### Demo Section 1: Discovery (2 min)

> "First, let's see how external agents discover our service..."

[Run `python demo_a2a_mcp_flow.py`]

> "The Agent Card tells other agents exactly what we can do. Notice it lists our 'trip planning' skill and mentions we support streaming responses. This follows the A2A specification, so any A2A-compliant agent can understand this."

### Demo Section 2: Execution (3 min)

> "Now let's see the agents in action with a real travel query..."

[Run curl command or show in browser]

> "Watch what happens: The coordinator receives the request, analyzes that we need both currency conversion and activity planning, delegates to specialized agents, and returns a unified response. All of this is happening across multiple pods in Kubernetes."

[Show logs]

> "In the logs, you can see the exact function calls: calling the CurrencyExchangeAgent, then the Frankfurter API for live rates, then generating the Tokyo itinerary."

### Demo Section 3: Architecture (2 min)

> "Let's look at how this is structured..."

[Show pods]

> "Three independent services: coordinator, currency agent, activity agent. Each can scale independently. The coordinator handles A2A requests from external agents and coordinates MCP tool calls to the specialized agents."

### Closing (1 min)

> "This demonstrates how emerging protocols like A2A and MCP are making multi-agent systems production-ready. We're seeing standardization across the industry, similar to how HTTP standardized the web. The code is open source, and I'm happy to answer questions about our implementation journey."

---

## 💡 Handling Questions

### Q: "Is this all working right now?"

**A**: "The multi-agent system is fully operational - you saw it working. We have A2A discovery working. The task delegation method needs completion, which shows the real-world challenges of implementing new protocols. The value is in understanding how these protocols work together."

### Q: "Why not just use REST APIs?"

**A**: "REST works great for request/response, but A2A adds agent discovery and cross-platform delegation. MCP adds type-safe tool schemas that LLMs can understand directly. Together they create a complete ecosystem for agent collaboration."

### Q: "How do you handle authentication?"

**A**: "Great question! A2A supports authenticated agent cards and push notifications. For internal MCP, we rely on Kubernetes network policies. In production, you'd add mTLS between services."

### Q: "Can you add a new agent easily?"

**A**: "Absolutely! Create an MCP server with your tools, deploy it as a pod, register it with the coordinator. The coordinator can then invoke those tools. We're planning to add HR, flight booking, and hotel agents next."

### Q: "What about error handling?"

**A**: "Each protocol has error codes. A2A uses JSON-RPC error codes, MCP returns structured error responses. We also have Kubernetes health checks and automatic pod restarts."

---

## 📁 Required Materials

### On Your Laptop:
1. ✅ Terminal with `kubectl` configured
2. ✅ Demo script: `demo_a2a_mcp_flow.py`
3. ✅ Browser with http://<YOUR-PUBLIC-IP> ready
4. ✅ VS Code with project open (to show code if asked)

### Backup Plans:
- If pods are down: Show architecture diagrams and code
- If network fails: Use recorded video of working demo
- If time is short: Focus on A2A discovery + REST API only

---

## 🎯 Key Takeaways for Audience

1. **Standardized protocols enable agent interoperability**
2. **A2A handles discovery, MCP handles execution**
3. **Kubernetes provides production deployment**
4. **Semantic Kernel orchestrates multi-agent workflows**
5. **Real-world implementation teaches valuable lessons**

---

## 📊 Success Metrics

✅ **Minimal Success**: Show A2A discovery + working REST API  
✅✅ **Good Success**: Above + explain MCP architecture + show pods  
✅✅✅ **Great Success**: Above + live coding to add a new tool  

---

## 🚀 Post-Presentation

**Call to Action**:
- "Code is on GitHub: darkanita/MultiAgent-kubecon2025"
- "Try it yourself with Azure Developer CLI: `azd up`"
- "Join the conversation about agent protocols"

**Follow-up Materials**:
- Link to A2A specification
- Link to MCP specification
- Link to Semantic Kernel docs
- Your contact for questions

---

**Good luck at KubeCon! 🎉**
