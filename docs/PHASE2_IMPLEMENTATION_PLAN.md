# Phase 2: Microservices Implementation - Step-by-Step Guide

## 🎯 Goal

Transform the monolithic application into a **microservices architecture** where each agent runs as an independent service communicating via the **MCP protocol**.

---

## 📊 Current vs Target Architecture

### Current (Phase 1 - Monolithic)
```
┌─────────────────────────────────────────────┐
│         Single Pod (FastAPI)                │
│                                             │
│  ┌────────────────────────────────────────┐ │
│  │  TravelManagerAgent                    │ │
│  │  (Semantic Kernel Orchestrator)        │ │
│  └──────┬─────────────────────────────────┘ │
│         │ Internal Function Calls           │
│         ▼                                    │
│  ┌──────────────┐    ┌──────────────────┐  │
│  │ Currency     │    │ Activity         │  │
│  │ Agent        │    │ Agent            │  │
│  └──────────────┘    └──────────────────┘  │
└─────────────────────────────────────────────┘
```

### Target (Phase 2 - Microservices)
```
┌──────────────────────┐
│  Coordinator Service │
│  (Pod 1)             │
│  - TravelManager     │
│  - MCP Client        │
│  - Web UI            │
│  - REST API          │
│  - A2A Server        │
└──────┬───────────────┘
       │
       │ MCP Protocol (stdio over K8s service)
       │
       ├─────────────────┬──────────────────┐
       ▼                 ▼                  ▼
┌────────────────┐ ┌──────────────┐  ┌──────────────┐
│ Currency Svc   │ │ Activity Svc │  │ Future       │
│ (Pod 2)        │ │ (Pod 3)      │  │ Agents       │
│ - MCP Server   │ │ - MCP Server │  │ (Pod N)      │
│ - 2 Tools      │ │ - 3 Tools    │  │              │
└────────────────┘ └──────────────┘  └──────────────┘
```

---

## 📋 Prerequisites

- ✅ Phase 1 complete (MCP infrastructure deployed)
- ✅ Current deployment on AKS working
- ✅ MCP servers already created (`mcp_currency_server.py`, `mcp_activity_server.py`)
- ✅ MCP coordinator client created (`mcp_coordinator.py`)
- ✅ kubectl access to AKS cluster
- ✅ Docker and ACR access

---

## 🚀 Implementation Steps

## **Step 1: Restructure Code for Microservices**

### 1.1 Create Service Directories

```bash
mkdir -p src/services/coordinator
mkdir -p src/services/currency-agent
mkdir -p src/services/activity-agent
```

### 1.2 Move Coordinator Components

**Create**: `src/services/coordinator/main.py`

```python
"""Coordinator Service - Main orchestrator with MCP client."""
import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

from src.api.chat import router as chat_router
from src.agent.a2a_server import A2AServer
from src.agent.mcp_coordinator import MCPCoordinator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Travel Coordinator Service")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize MCP Coordinator
mcp_coordinator = MCPCoordinator()

@app.on_event("startup")
async def startup_event():
    """Initialize MCP connections to agent services."""
    logger.info("🚀 Starting Coordinator Service...")
    
    # Register Currency Agent (via K8s service)
    currency_service = os.getenv("CURRENCY_SERVICE_URL", "currency-agent:8001")
    await mcp_coordinator.register_agent(
        agent_name="currency-agent",
        server_script="python",
        args=["-m", "src.services.currency-agent.server"],
        service_url=currency_service
    )
    
    # Register Activity Agent (via K8s service)
    activity_service = os.getenv("ACTIVITY_SERVICE_URL", "activity-agent:8002")
    await mcp_coordinator.register_agent(
        agent_name="activity-agent",
        server_script="python",
        args=["-m", "src.services.activity-agent.server"],
        service_url=activity_service
    )
    
    logger.info("✅ All MCP agents registered")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup MCP connections."""
    await mcp_coordinator.shutdown()

# Include API routes
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

# Mount A2A server
httpx_client = httpx.AsyncClient()
a2a_server = A2AServer(httpx_client, host="0.0.0.0", port=8000)
app.mount("/a2a", a2a_server.get_starlette_app())

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return templates.TemplateResponse("index.html", {"request": {}})
```

### 1.3 Create Currency Agent Service

**Create**: `src/services/currency-agent/main.py`

```python
"""Currency Agent Service - Standalone MCP server."""
import asyncio
import logging
from src.agent.mcp_currency_server import CurrencyMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run the Currency MCP server."""
    logger.info("🚀 Starting Currency Agent MCP Server...")
    
    server = CurrencyMCPServer()
    
    # Run MCP server via stdio
    async with server.server.stdio_server() as (read_stream, write_stream):
        logger.info("✅ Currency Agent ready - listening on stdio")
        await server.server.run(
            read_stream=read_stream,
            write_stream=write_stream,
            initialization_options={}
        )

if __name__ == "__main__":
    asyncio.run(main())
```

**Create**: `src/services/currency-agent/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose MCP port (for potential HTTP wrapper)
EXPOSE 8001

# Run MCP server
CMD ["python", "-m", "src.services.currency-agent.main"]
```

### 1.4 Create Activity Agent Service

**Create**: `src/services/activity-agent/main.py`

```python
"""Activity Agent Service - Standalone MCP server."""
import asyncio
import logging
from src.agent.mcp_activity_server import ActivityMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Run the Activity MCP server."""
    logger.info("🚀 Starting Activity Agent MCP Server...")
    
    server = ActivityMCPServer()
    
    # Run MCP server via stdio
    async with server.server.stdio_server() as (read_stream, write_stream):
        logger.info("✅ Activity Agent ready - listening on stdio")
        await server.server.run(
            read_stream=read_stream,
            write_stream=write_stream,
            initialization_options={}
        )

if __name__ == "__main__":
    asyncio.run(main())
```

**Create**: `src/services/activity-agent/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose MCP port
EXPOSE 8002

# Run MCP server
CMD ["python", "-m", "src.services.activity-agent.main"]
```

---

## **Step 2: Update MCP Coordinator for Remote Calls**

### 2.1 Add HTTP Wrapper for MCP (Optional but Recommended)

MCP uses stdio, but for Kubernetes services, we need HTTP. Create a simple HTTP wrapper:

**Create**: `src/services/currency-agent/http_wrapper.py`

```python
"""HTTP wrapper for MCP stdio protocol."""
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.agent.mcp_currency_server import CurrencyMCPServer

app = FastAPI(title="Currency Agent HTTP Wrapper")
mcp_server = CurrencyMCPServer()

class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict

@app.post("/mcp/call_tool")
async def call_tool(request: ToolRequest):
    """HTTP endpoint to call MCP tools."""
    try:
        # Get the tool handler
        for tool in mcp_server.server._request_handlers["tools/call"]:
            if tool.name == request.tool_name:
                result = await tool.fn(request.arguments)
                return {"result": result}
        
        raise HTTPException(status_code=404, detail=f"Tool {request.tool_name} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/list_tools")
async def list_tools():
    """List available MCP tools."""
    tools = []
    for tool in mcp_server._available_tools:
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        })
    return {"tools": tools}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "currency-agent"}
```

### 2.2 Update MCP Coordinator for HTTP Communication

**Modify**: `src/agent/mcp_coordinator.py`

Add HTTP client support:

```python
import httpx

class MCPAgentClient:
    """Client for communicating with MCP-enabled agents."""

    def __init__(self, agent_name: str, service_url: str = None, command: str = None, args: list[str] = None):
        """Initialize MCP client.
        
        Args:
            agent_name: Name of the agent
            service_url: HTTP URL for remote agent (K8s service)
            command: Command for local stdio (fallback)
            args: Arguments for the command
        """
        self.agent_name = agent_name
        self.service_url = service_url
        self.command = command
        self.args = args or []
        self.session: ClientSession | None = None
        self.http_client = httpx.AsyncClient() if service_url else None
        self._available_tools: list[Any] = []

    async def connect(self):
        """Establish connection to the MCP server."""
        try:
            if self.service_url:
                # HTTP mode - for K8s microservices
                logger.info(f"🔌 [MCP] Connecting to {self.agent_name} via HTTP: {self.service_url}")
                response = await self.http_client.get(f"{self.service_url}/mcp/list_tools")
                tools_data = response.json()
                self._available_tools = tools_data["tools"]
            else:
                # Stdio mode - for local development
                server_params = StdioServerParameters(
                    command=self.command,
                    args=self.args
                )
                stdio_transport = stdio_client(server_params)
                self.session = await stdio_transport.__aenter__()
                await self.session.initialize()
                tools_response = await self.session.list_tools()
                self._available_tools = tools_response.tools
            
            logger.info(
                f"🔌 [MCP] Connected to {self.agent_name} MCP server. "
                f"Available tools: {[t['name'] if isinstance(t, dict) else t.name for t in self._available_tools]}"
            )
        except Exception as e:
            logger.error(f"❌ [MCP] Failed to connect to {self.agent_name} MCP server: {e}")
            raise

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a tool on the MCP server."""
        logger.info(f"🚀 [MCP] Calling tool '{tool_name}' on {self.agent_name} with args: {arguments}")
        
        try:
            if self.http_client:
                # HTTP mode
                response = await self.http_client.post(
                    f"{self.service_url}/mcp/call_tool",
                    json={"tool_name": tool_name, "arguments": arguments}
                )
                result = response.json()["result"]
            else:
                # Stdio mode
                response = await self.session.call_tool(tool_name, arguments)
                result = response.content[0].text if response.content else None
            
            logger.info(f"✅ [MCP] Tool '{tool_name}' executed successfully on {self.agent_name}")
            return result
        except Exception as e:
            logger.error(f"❌ [MCP] Error calling tool '{tool_name}' on {self.agent_name}: {e}")
            raise
```

---

## **Step 3: Create Dockerfiles**

### 3.1 Coordinator Dockerfile

**Create**: `src/services/coordinator/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run coordinator
CMD ["uvicorn", "src.services.coordinator.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.2 Currency Agent Dockerfile

Already created in Step 1.3

### 3.3 Activity Agent Dockerfile

Already created in Step 1.4

---

## **Step 4: Create Kubernetes Manifests**

### 4.1 Coordinator Deployment & Service

**Create**: `manifests/microservices/coordinator-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coordinator-service
  labels:
    app: coordinator
    component: orchestrator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: coordinator
  template:
    metadata:
      labels:
        app: coordinator
    spec:
      containers:
      - name: coordinator
        image: acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/coordinator:latest
        ports:
        - containerPort: 8000
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: AZURE_OPENAI_ENDPOINT
        - name: AZURE_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: AZURE_OPENAI_API_KEY
        - name: AZURE_OPENAI_DEPLOYMENT_NAME
          value: "gpt-4o-mini"
        - name: AZURE_OPENAI_API_VERSION
          value: "2024-08-01-preview"
        - name: CURRENCY_SERVICE_URL
          value: "http://currency-agent:8001"
        - name: ACTIVITY_SERVICE_URL
          value: "http://activity-agent:8002"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: coordinator-service
  labels:
    app: coordinator
spec:
  selector:
    app: coordinator
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
  type: LoadBalancer
```

### 4.2 Currency Agent Deployment & Service

**Create**: `manifests/microservices/currency-agent-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: currency-agent
  labels:
    app: currency-agent
    component: agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: currency-agent
  template:
    metadata:
      labels:
        app: currency-agent
    spec:
      containers:
      - name: currency-agent
        image: acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/currency-agent:latest
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 20
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: currency-agent
  labels:
    app: currency-agent
spec:
  selector:
    app: currency-agent
  ports:
  - protocol: TCP
    port: 8001
    targetPort: 8001
    name: mcp
  type: ClusterIP
```

### 4.3 Activity Agent Deployment & Service

**Create**: `manifests/microservices/activity-agent-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: activity-agent
  labels:
    app: activity-agent
    component: agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: activity-agent
  template:
    metadata:
      labels:
        app: activity-agent
    spec:
      containers:
      - name: activity-agent
        image: acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/activity-agent:latest
        ports:
        - containerPort: 8002
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 20
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: activity-agent
  labels:
    app: activity-agent
spec:
  selector:
    app: activity-agent
  ports:
  - protocol: TCP
    port: 8002
    targetPort: 8002
    name: mcp
  type: ClusterIP
```

---

## **Step 5: Build and Push Docker Images**

### 5.1 Build Images

```bash
# Build Coordinator
docker build -f src/services/coordinator/Dockerfile \
  -t acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/coordinator:latest .

# Build Currency Agent
docker build -f src/services/currency-agent/Dockerfile \
  -t acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/currency-agent:latest .

# Build Activity Agent
docker build -f src/services/activity-agent/Dockerfile \
  -t acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/activity-agent:latest .
```

### 5.2 Push to ACR

```bash
# Login to ACR
az acr login --name acrmakubeconagent5h4hjd6w

# Push all images
docker push acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/coordinator:latest
docker push acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/currency-agent:latest
docker push acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/activity-agent:latest
```

---

## **Step 6: Deploy to Kubernetes**

### 6.1 Deploy All Services

```bash
# Deploy Currency Agent
kubectl apply -f manifests/microservices/currency-agent-deployment.yaml -n multiagent-kubecon-simple

# Deploy Activity Agent
kubectl apply -f manifests/microservices/activity-agent-deployment.yaml -n multiagent-kubecon-simple

# Deploy Coordinator (depends on agents being ready)
kubectl apply -f manifests/microservices/coordinator-deployment.yaml -n multiagent-kubecon-simple
```

### 6.2 Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n multiagent-kubecon-simple

# Expected output:
# NAME                                 READY   STATUS    RESTARTS   AGE
# coordinator-service-xxxxx            1/1     Running   0          2m
# currency-agent-xxxxx                 1/1     Running   0          3m
# activity-agent-xxxxx                 1/1     Running   0          3m

# Check services
kubectl get svc -n multiagent-kubecon-simple

# Check logs
kubectl logs -f deployment/coordinator-service -n multiagent-kubecon-simple
kubectl logs -f deployment/currency-agent -n multiagent-kubecon-simple
kubectl logs -f deployment/activity-agent -n multiagent-kubecon-simple
```

---

## **Step 7: Test MCP Communication**

### 7.1 Watch Logs for MCP Activity

```bash
# Terminal 1 - Coordinator logs
kubectl logs -f deployment/coordinator-service -n multiagent-kubecon-simple | grep "MCP"

# Terminal 2 - Currency Agent logs
kubectl logs -f deployment/currency-agent -n multiagent-kubecon-simple

# Terminal 3 - Activity Agent logs
kubectl logs -f deployment/activity-agent -n multiagent-kubecon-simple
```

### 7.2 Send Test Request

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc coordinator-service -n multiagent-kubecon-simple -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Send test message
curl -X POST "http://${EXTERNAL_IP}/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Convert 500 USD to EUR and suggest activities in Paris",
    "session_id": "test-microservices"
  }'
```

### 7.3 Expected Log Output

**Coordinator logs**:
```log
🚀 Starting Coordinator Service...
🔌 [MCP] Connecting to currency-agent via HTTP: http://currency-agent:8001
🔌 [MCP] Connected to currency-agent MCP server. Available tools: ['get_exchange_rate', 'convert_amount']
🔌 [MCP] Connecting to activity-agent via HTTP: http://activity-agent:8002
🔌 [MCP] Connected to activity-agent MCP server. Available tools: ['plan_activities', 'suggest_restaurants', 'suggest_attractions']
✅ All MCP agents registered

💬 [CHAT API] Received message: 'Convert 500 USD to EUR and suggest activities in Paris...'
🚀 [MCP] Calling tool 'convert_amount' on currency-agent with args: {'amount': 500, 'from_currency': 'USD', 'to_currency': 'EUR'}
✅ [MCP] Tool 'convert_amount' executed successfully on currency-agent
🚀 [MCP] Calling tool 'suggest_attractions' on activity-agent with args: {'destination': 'Paris', 'budget': 'moderate'}
✅ [MCP] Tool 'suggest_attractions' executed successfully on activity-agent
```

**Currency Agent logs**:
```log
🚀 Starting Currency Agent MCP Server...
✅ Currency Agent ready - listening on HTTP port 8001
📥 Received tool call: convert_amount
📤 Returning result: 434.25 EUR
```

**Activity Agent logs**:
```log
🚀 Starting Activity Agent MCP Server...
✅ Activity Agent ready - listening on HTTP port 8002
📥 Received tool call: suggest_attractions
📤 Returning result: [Eiffel Tower, Louvre Museum...]
```

---

## **Step 8: Update Travel Agent to Use MCP Coordinator**

**Modify**: `src/agent/travel_agent.py`

```python
from src.agent.mcp_coordinator import MCPCoordinator

class SemanticKernelTravelAgent:
    def __init__(self):
        self.kernel = Kernel()
        self.mcp_coordinator = MCPCoordinator()  # Use MCP for agent communication
        
        # ... rest of initialization
        
    async def _call_currency_agent(self, query: str):
        """Call currency agent via MCP instead of direct plugin."""
        result = await self.mcp_coordinator.call_tool(
            agent_name="currency-agent",
            tool_name="get_exchange_rate",
            arguments={"currency_from": "USD", "currency_to": "EUR"}
        )
        return result
```

---

## **Step 9: Rollback Strategy (If Needed)**

If Phase 2 deployment fails, rollback to Phase 1:

```bash
# Delete microservices
kubectl delete -f manifests/microservices/ -n multiagent-kubecon-simple

# Redeploy monolithic version
kubectl apply -f manifests/deployment.yaml -n multiagent-kubecon-simple
```

---

## **Step 10: Validation Checklist**

- [ ] All 3 pods running (coordinator, currency-agent, activity-agent)
- [ ] Coordinator can connect to both agents via MCP
- [ ] MCP logs show tool calls with 🔌🚀✅ emojis
- [ ] Currency conversion works end-to-end
- [ ] Activity planning works end-to-end
- [ ] Web UI accessible via external IP
- [ ] A2A endpoint still works (`/a2a/`)
- [ ] Performance is acceptable (latency < 2s)

---

## 🎯 Success Criteria

When Phase 2 is complete, you should see:

1. **3 separate pods** running independently
2. **MCP protocol logs** showing inter-service communication
3. **Same functionality** as Phase 1 but distributed
4. **Scalable architecture** - can add more agents easily
5. **Clear separation** - each agent is independently deployable

---

## 📚 Next Steps: Phase 3

After Phase 2 is stable:

1. Add **HR Agent** as a new microservice
2. Implement **dynamic agent registration**
3. Add **Flight Booking Agent**
4. Add **Hotel Reservation Agent**
5. Implement **service mesh** (Istio) for advanced traffic management

---

## 🆘 Troubleshooting

### Issue: Coordinator can't connect to agents

**Check**:
```bash
# Verify services exist
kubectl get svc -n multiagent-kubecon-simple

# Test connectivity from coordinator pod
kubectl exec -it deployment/coordinator-service -n multiagent-kubecon-simple -- curl http://currency-agent:8001/health
```

### Issue: No MCP logs appearing

**Check**:
```bash
# Verify MCP coordinator is initialized
kubectl logs deployment/coordinator-service -n multiagent-kubecon-simple | grep "MCP"

# Check agent logs
kubectl logs deployment/currency-agent -n multiagent-kubecon-simple
```

### Issue: High latency

**Solution**: Increase replicas for agent services:
```bash
kubectl scale deployment currency-agent --replicas=2 -n multiagent-kubecon-simple
kubectl scale deployment activity-agent --replicas=2 -n multiagent-kubecon-simple
```

---

## 📊 Monitoring

### View All Logs Together

```bash
# Install stern (if not already)
# brew install stern

# Watch all microservices logs
stern -n multiagent-kubecon-simple ".*" --tail 10
```

### Prometheus Metrics (Future)

Add metrics endpoints to track:
- MCP call latency
- Tool invocation count
- Error rates per agent

---

## 🎓 Key Learning Points

1. **MCP over HTTP**: We wrap stdio MCP protocol in HTTP for K8s communication
2. **Service Discovery**: Use K8s DNS (e.g., `http://currency-agent:8001`)
3. **Gradual Migration**: Keep Phase 1 deployment while testing Phase 2
4. **Independent Scaling**: Each agent can scale independently
5. **Clear Boundaries**: Each service has single responsibility

---

**Estimated Time**: 4-6 hours for full implementation
**Difficulty**: Intermediate to Advanced
**Prerequisites**: Docker, Kubernetes, Python async programming

Good luck with Phase 2! 🚀
