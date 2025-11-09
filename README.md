# Multi-Agent AI System on Azure Kubernetes Service (AKS)

> **🎯 KubeCon 2025 Demo**  
> Production-ready Multi-Agent AI system with dual-protocol support (A2A + MCP), deployed on Azure Kubernetes Service.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/darkanita/MultiAgent-kubecon2025)
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template)

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Azure](https://img.shields.io/badge/Azure-AKS-0078D4?logo=microsoftazure)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-326CE5?logo=kubernetes)
![Semantic Kernel](https://img.shields.io/badge/Semantic%20Kernel-1.30-512BD4)
![MCP](https://img.shields.io/badge/MCP-1.0-green)
![A2A](https://img.shields.io/badge/A2A-0.2.9-orange)

---

## ⚠️ Important: Configuration Required

**This repository does not contain sensitive Azure credentials or public IPs.**

Before deploying, you must configure your own Azure resources:

1. **Quick Setup** (recommended):
   ```bash
   python setup_project.py
   ```

2. **Manual Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure values
   ```

Required Azure resources:
- Azure Kubernetes Service (AKS) cluster
- Azure OpenAI service
- Azure Container Registry (ACR)

See [Configuration Guide](#-configuration) below for details.

---

## 📖 About

A cloud-native multi-agent travel assistant combining Microsoft Semantic Kernel with **dual protocol support**:
- **A2A Protocol** (Agent-to-Agent) for service discovery
- **MCP Protocol** (Model Context Protocol) for tool execution

**Two deployment options available**:
- **Phase 1**: Monolithic application (main branch) - ✅ Deployed at http://<YOUR-PHASE1-PUBLIC-IP>
- **Phase 2**: Microservices architecture (microservices branch) - ✅ Deployed at http://<YOUR-PUBLIC-IP>

---

## 🏗️ Architecture Overview

### **Phase 1: Monolithic + MCP Integration** (✅ Deployed at <YOUR-PHASE1-PUBLIC-IP>)

```
┌───────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL WORLD                                 │
│  • Web Browser Users  • Other A2A Agents  • API Clients              │
└───────────────────────┬───────────────────────────────────────────────┘
                        │
                        │ 📡 A2A PROTOCOL
                        │  - GET /a2a/ (Agent Card)
                        │  - POST /a2a/tasks/send (Task Delegation)
                        │  - POST /api/chat/message (REST API)
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Application (Single Pod)                    │
│              LoadBalancer: http://<YOUR-PHASE1-PUBLIC-IP>                  │
├─────────────────────────────────────────────────────────────────┤
│  📡 A2A SERVER (Port 8000)                                      │
│     • GET /a2a/ - Agent Card discovery                          │
│     • POST /a2a/tasks/send - Task delegation                    │
│                                                                 │
│  🌐 WEB UI (Port 8000)                                          │
│     • Chat Interface (HTML/CSS/JavaScript)                      │
│     • Real-time streaming responses                             │
│     • Session management                                        │
│                                                                 │
│  🤖 SEMANTIC KERNEL ORCHESTRATION                               │
│     ┌─────────────────────────────────────────────────────┐    │
│     │  TravelManagerAgent (Coordinator)                   │    │
│     │  • Analyzes user requests                           │    │
│     │  • Delegates to specialized agents (in-process)     │    │
│     │  • Aggregates responses                             │    │
│     └───────────┬──────────────────┬──────────────────────┘    │
│                 │                  │                            │
│                 │ (In-Process      │ (In-Process                │
│                 │  Function Call)  │  Function Call)            │
│                 ▼                  ▼                            │
│     ┌───────────────────┐  ┌─────────────────────────┐         │
│     │ CurrencyExchange  │  │  ActivityPlanner Agent  │         │
│     │     Agent         │  │                         │         │
│     │                   │  │                         │         │
│     │ 🔧 MCP Tools:     │  │ 🔧 MCP Tools:           │         │
│     │  • exchange_rate  │  │  • plan_activities      │         │
│     │  • convert_amount │  │  • suggest_restaurants  │         │
│     │                   │  │  • suggest_attractions  │         │
│     │                   │  │                         │         │
│     │ 🌐 Frankfurter API│  │ 💡 AI-powered planning  │         │
│     └───────────────────┘  └─────────────────────────┘         │
│                                                                 │
│  ⚡ AZURE OPENAI INTEGRATION                                    │
│     • Model: gpt-4o-mini                                        │
│     • Function calling for tool execution                       │
│     • Managed Identity authentication                           │
└─────────────────────────────────────────────────────────────────┘

─────────────────────────────────────────────────────────────────────────
🔑 Protocol Notes:
  📡 A2A Protocol = ✅ ACTIVE (external agents can discover and delegate tasks)
  🔧 MCP Protocol = ⚠️  DEFINED but NOT used (tools called as in-process Python functions)
  📁 MCP Files = ✅ Exist (mcp_currency_server.py, mcp_activity_server.py, mcp_coordinator.py)
  🔄 MCP Usage = ❌ Protocol not active (no HTTP JSON-RPC, no stdio transport)
  ⚙️  Architecture = All agents in same pod (monolithic)
  
📊 Deployment: Single pod on AKS, namespace: multiagent-kubecon-simple

💡 Key Difference from Phase 2:
   • Phase 1: MCP tools DEFINED ✅ but communication is in-process Python calls ❌
   • Phase 2: MCP protocol ACTIVE ✅ with HTTP JSON-RPC communication ✅
```

### **Phase 2: Microservices Architecture** (✅ DEPLOYED!)

```
┌───────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL WORLD                                 │
│  • Web Browser Users  • Other A2A Agents  • API Clients              │
└───────────────────────┬───────────────────────────────────────────────┘
                        │
                        │ (1) 📡 A2A PROTOCOL
                        │     - Agent Discovery (GET /a2a/)
                        │     - Task Delegation (POST /a2a/tasks/send)
                        │     - REST API (POST /api/chat/message)
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│               COORDINATOR SERVICE (Pod 1) 🎯                    │
│              LoadBalancer: http://<YOUR-PUBLIC-IP>                 │
├─────────────────────────────────────────────────────────────────┤
│  📡 A2A SERVER (Port 8000)                                      │
│     • Agent Card Discovery                                      │
│     • Task Reception & Delegation                               │
│                                                                 │
│  🌐 WEB UI (Port 8000)                                          │
│     • Chat Interface                                            │
│     • REST API Endpoints                                        │
│                                                                 │
│  🤖 TRAVEL MANAGER AGENT (Semantic Kernel)                      │
│     • Analyzes Requests                                         │
│     • Determines Required Tools                                 │
│     • Aggregates Results                                        │
│                                                                 │
│  🔌 MCP CLIENT                                                  │
│     • Connects to internal agents via HTTP                      │
│     • Sends JSON-RPC 2.0 tool calls                            │
└───────────┬──────────────────────────┬──────────────────────────┘
            │                          │
            │ (2) 🔧 MCP PROTOCOL      │ (3) 🔧 MCP PROTOCOL
            │     over HTTP            │     over HTTP
            │     POST /mcp/v1         │     POST /mcp/v1
            │     JSON-RPC 2.0         │     JSON-RPC 2.0
            ▼                          ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌────────────────┐
│ 💰 CURRENCY AGENT     │  │ 🎨 ACTIVITY AGENT     │  │ 🔮 FUTURE      │
│     (Pod 2)           │  │     (Pod 3)           │  │    AGENTS      │
│ Port: 8001 (ClusterIP)│  │ Port: 8002 (ClusterIP)│  │    (Pod N)     │
├───────────────────────┤  ├───────────────────────┤  ├────────────────┤
│ 🔧 MCP SERVER         │  │ 🔧 MCP SERVER         │  │ • HR Agent     │
│                       │  │                       │  │ • Flight Agent │
│ Tools:                │  │ Tools:                │  │ • Hotel Agent  │
│  • get_exchange_rate  │  │  • plan_activities    │  │                │
│  • convert_amount     │  │  • suggest_restaurants│  │                │
│                       │  │  • suggest_attractions│  │                │
│                       │  │                       │  │                │
│ 🌐 Frankfurter API    │  │ 💡 AI-powered planning│  │                │
└───────────────────────┘  └───────────────────────┘  └────────────────┘
      Internal Only             Internal Only            Coming Soon
   http://currency-agent:8001  http://activity-agent:8002

─────────────────────────────────────────────────────────────────────────
⚠️  **IMPORTANT NOTE - Current Implementation Status:**
  
  📊 **What's Working:**
  • ✅ Microservices deployed on separate pods
  • ✅ A2A Protocol active for external communication
  • ✅ MCP Servers running (currency-agent:8001, activity-agent:8002)
  • ✅ Web UI and REST API functional
  
  🚧 **What's NOT Working (In Progress):**
  • ❌ Coordinator uses in-process Semantic Kernel calls
  • ❌ MCP HTTP protocol not active between coordinator and agents
  • ❌ No JSON-RPC 2.0 communication over HTTP
  
  📝 **Current Architecture:**
  Coordinator → Semantic Kernel (in-process) → Tools
  
  🎯 **Target Architecture:**
  Coordinator → MCP Client (HTTP) → MCP Servers (currency/activity)

─────────────────────────────────────────────────────────────────────────
📊 Deployment Details:
  • AKS Cluster: aks-qfapkj24vye7a (rg-kubecon-micro)
  • Namespace: multiagent-microservices
  • Container Registry: <YOUR-ACR>.azurecr.io
  • Azure OpenAI: <YOUR-OPENAI-RESOURCE> (gpt-4o-mini)
  
🔑 Protocol Distinction:
  📡 A2A = External communication (Internet → Coordinator)
  🔧 MCP = Internal communication (Coordinator → Agents)
  
📖 Detailed Flow Diagrams: See PROTOCOL_FLOWS.md
```

---

## ✨ Key Features

### 🤖 **Dual Protocol Support** (NEW!)
- **A2A Protocol**: Agent discovery and service registration
- **MCP Protocol**: Standardized tool invocation and execution
- **5 MCP Tools**: Currency (2) + Activity Planning (3)
- **Seamless Integration**: Both protocols work together harmoniously

### 💱 **Currency Exchange Agent**
- Real-time exchange rates via Frankfurter API
- Support for 30+ currencies
- Amount conversion with live rates
- **MCP Tools**:
  - `get_exchange_rate` - Get current exchange rate
  - `convert_amount` - Convert specific amounts

### 🗺️ **Activity Planning Agent**
- Personalized trip itineraries
- Restaurant recommendations by cuisine and budget
- Tourist attraction suggestions by category
- **MCP Tools**:
  - `plan_activities` - Generate day-by-day itineraries
  - `suggest_restaurants` - Dining recommendations
  - `suggest_attractions` - Sightseeing suggestions

### 🌐 **Modern Web Interface**
- Responsive chat UI
- Real-time streaming responses
- Session management
- Mobile-friendly design

### ☁️ **Azure-Native Deployment**
- Azure Kubernetes Service (AKS)
- Azure OpenAI Service
- Azure Container Registry (ACR)
- Azure Developer CLI (AZD) automation
- Managed Identity authentication

---

## 📁 Project Structure

```
MultiAgent-kubecon2025/
├── src/
│   ├── agent/                       # Agent implementation
│   │   ├── travel_agent.py          # Semantic Kernel multi-agent orchestration
│   │   ├── agent_executor.py        # A2A protocol executor
│   │   ├── a2a_server.py            # A2A server integration
│   │   ├── mcp_currency_server.py   # 🆕 MCP server for currency agent
│   │   ├── mcp_activity_server.py   # 🆕 MCP server for activity agent
│   │   └── mcp_coordinator.py       # 🆕 MCP client coordinator
│   ├── api/
│   │   └── chat.py                  # REST API endpoints
│   └── services/                    # 🆕 Microservices (Phase 2)
│       ├── coordinator/             # Main coordinator service
│       │   └── main.py              # A2A server + Web UI + MCP client
│       ├── currency_agent/          # Currency exchange service
│       │   └── main.py              # MCP server over HTTP
│       └── activity_agent/          # Activity planning service
│           └── main.py              # MCP server over HTTP
├── templates/
│   └── index.html                   # Modern web chat interface
├── static/
│   ├── css/style.css                # Responsive styling
│   └── js/chat.js                   # Real-time chat functionality
├── manifests/                       # Kubernetes deployment files
│   ├── simple/                      # Phase 1: Monolithic deployment
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── namespace.yaml
│   └── microservices/               # Phase 2: Microservices deployment
│       ├── coordinator/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── currency-agent/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── activity-agent/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── configmap.yaml
│       └── namespace.yaml
├── infra/                           # Azure infrastructure (Bicep)
│   ├── main.bicep                   # Main infrastructure template
│   └── modules/
│       ├── core-resources.bicep     # AKS, ACR, OpenAI resources
│       ├── aks-acr-pull.bicep       # ACR pull RBAC
│       └── openai-user.bicep        # OpenAI user RBAC
├── docs/                            # 📚 Documentation
│   ├── A2A_AND_MCP_EXPLAINED.md     # Protocol comparison guide
│   ├── MCP_INTEGRATION.md           # MCP protocol integration guide
│   └── PHASE1_TEST_RESULTS.md       # Phase 1 testing results
├── test_mcp_simple.py               # 🧪 MCP integration tests
├── azure.yaml                       # Azure Developer CLI config (Phase 2)
├── pyproject.toml                   # Python dependencies (includes MCP!)
├── requirements-minimal.txt         # 🆕 Docker build dependencies
├── Dockerfile.coordinator           # 🆕 Coordinator service image
├── Dockerfile.currency              # 🆕 Currency/Activity agent image
├── MONITORING_GUIDE.md              # 📊 Monitoring and logs guide
├── PROTOCOL_FLOWS.md                # 🔄 Detailed protocol flow diagrams
├── PROJECT_STRUCTURE.md             # 📖 Complete structure documentation
└── README.md                        # This file
```

---

## 🎯 Example Scenario

This implementation demonstrates a practical travel planning scenario using Semantic Kernel with A2A protocol integration:

### 🎯 **User Journey**
Imagine a user wants a budget-friendly trip plan with currency conversion:

1. **User Request**: "I am traveling to Seoul, South Korea for 2 days. I have a budget of $100 USD a day. How much is that in South Korean Won? What sort of things can I do and eat?"

2. **TravelManager Analysis**: The main agent receives the request and detects both currency and activity planning needs

3. **Multi-Agent Delegation**: 
   - **CurrencyExchangeAgent** is invoked to fetch live USD→KRW rates from Frankfurter API
   - **ActivityPlannerAgent** generates budget-friendly activity and dining recommendations

4. **Response Compilation**: The TravelManager combines results from both specialized agents

5. **Structured Output**: User receives a complete response with:
   - Current exchange rate ($100 USD = ~130,000 KRW)
   - Daily budget breakdown in Korean Won
   - Recommended activities within budget
   - Restaurant suggestions with price ranges

### 🔄 **Integration Flow**
![Semantic Kernel + A2A Integration](https://devblogs.microsoft.com/foundry/wp-content/uploads/sites/89/2025/04/1_mermaid_a2a.png)

*Source: [Microsoft DevBlogs - Semantic Kernel A2A Integration](https://devblogs.microsoft.com/foundry/semantic-kernel-a2a-integration/)*

### 🤝 **A2A Protocol Benefits**
- **Agent Discovery**: Other A2A agents can discover and delegate travel tasks to your agent
- **Task Coordination**: Seamless handoffs between specialized agents across different platforms
- **Streaming Support**: Real-time progress updates during complex multi-agent workflows
- **Cross-Cloud Compatibility**: Works with any A2A-compliant agent regardless of hosting platform

## Quick Start

### 🚀 Option 1: GitHub Codespaces (Recommended)

**The fastest way to get started - no local setup required!**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/darkanita/MultiAgent-kubecon2025/codespaces)

1. Click the badge above or the **Code** button → **Codespaces** → **Create codespace**
2. Wait 3-5 minutes for the container to build
3. Follow the authentication steps in the terminal
4. Deploy with `azd up`

**Everything is pre-installed**: Python 3.11, Azure CLI, azd, kubectl, Docker, and all VS Code extensions!

See [.devcontainer/README.md](.devcontainer/README.md) for detailed Codespaces instructions.

---

### 💻 Option 2: Local Development

### Prerequisites

- Python 3.10 or higher
- Azure CLI (for deployment)
- Azure Developer CLI (azd)
- kubectl (for Kubernetes management)
- Docker (for container operations)
- **For local development**: Your own OpenAI or Azure OpenAI resource with API access
- **For Azure deployment**: OpenAI resource is automatically created when deploying with `azd`

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd semantic-kernel-travel-agent
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Authenticate with Azure** (for Azure OpenAI without API key):
   ```bash
   az login
   ```

4. **Run the application**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open your browser** to `http://localhost:8000`

### Azure Deployment

**✅ Ready to Deploy**: This application includes a complete Azure Developer CLI (AZD) template for one-command deployment.

1. **Authenticate with Azure Developer CLI**:
    ```bash
    azd auth login
    ```

2. **Initialize and deploy**:
   ```bash
   azd up
   ```

3. **Configure API key** (optional for local development):
   - For **Azure deployment**: Authentication uses managed identity automatically (no manual configuration needed)
   - For **local development**: Optionally add `AZURE_OPENAI_API_KEY` to your local `.env` file
   - If no API key is provided locally, Azure CLI credentials will be used for authentication

4. **Access your deployed application**:
   - The AZD template will output your application URL
   - Example: `https://appweb-xxxxxxxxx.azurewebsites.net`

**What gets deployed**:
- ✅ Azure App Service Plan (P0V3 for production readiness)
- ✅ Azure App Service with Python 3.11 runtime and managed identity
- ✅ Azure OpenAI resource with `gpt-4.1-mini` model
- ✅ Role assignment for secure managed identity authentication
- ✅ All necessary environment variables pre-configured
- ✅ Automatic build and deployment from source code

## Implementation Details

### 🧠 Semantic Kernel Multi-Agent Architecture

The application uses a sophisticated multi-agent architecture powered by Semantic Kernel:

- **TravelManagerAgent**: Main orchestrator that analyzes requests and delegates to specialized agents
- **CurrencyExchangeAgent**: Handles all currency-related queries with live Frankfurter API integration
- **ActivityPlannerAgent**: Creates detailed travel itineraries and activity recommendations

### 🔄 **How A2A Integration Works**

- **Task Routing and Delegation**: The TravelManager dynamically routes tasks to specialized agents, which are configured as plugins within the TravelManager itself. Leveraging context awareness and automatic function calling, the underlying model intelligently determines the most suitable agent to handle each request.

- **Agent Discovery**: Agents advertise their capabilities through a structured "Agent Card," enabling client agents to efficiently identify and select the most suitable agent for a given task, facilitating seamless communication through the A2A protocol.

- **Conversational Memory**: Semantic Kernel maintains context using its chat history across multi-turn interactions, providing a seamless user experience. Session history is maintained throughout the conversation flow.

### 🔧 Technical Stack

- **Framework**: FastAPI with async/await support
- **AI Engine**: Microsoft Semantic Kernel with Azure OpenAI/OpenAI integration
- **Protocol**: Google's Agent-to-Agent (A2A) for multi-agent coordination
- **Database**: SQLite with A2A SDK for task persistence
- **Frontend**: Modern HTML5/CSS3/JavaScript with real-time chat
- **Deployment**: Azure App Service with Bicep infrastructure as code

### 🌟 Key Features

- **Real-time Currency Conversion**: Live exchange rates via Frankfurter API
- **Function Calling**: Semantic Kernel plugins for external API integration
- **Streaming Responses**: Progressive response delivery for better UX
- **Session Management**: Persistent conversation history across interactions
- **Error Handling**: Graceful degradation with comprehensive error recovery

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint | Yes (if using Azure OpenAI) |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | No (uses managed identity in Azure, optional for local dev) |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI deployment name | Yes (if using Azure OpenAI) |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | Yes (if using Azure OpenAI) |
| `OPENAI_API_KEY` | OpenAI API key | Yes (if using OpenAI) |
| `OPENAI_MODEL_ID` | OpenAI model ID (e.g., gpt-4) | Yes (if using OpenAI) |
| `HOST` | Application host (default: 0.0.0.0) | No |
| `PORT` | Application port (default: 8000) | No |
| `DEBUG` | Enable debug mode (default: false) | No |

### Authentication

This application uses **managed identity authentication** for Azure OpenAI when deployed to Azure, providing enhanced security without the need to manage API keys.

**Authentication Methods**:
- **Azure Deployment**: Uses system-assigned managed identity with automatic role assignment to "Cognitive Services OpenAI User"
- **Local Development**: 
  - Option 1: Use Azure CLI credentials (`az login`) for keyless authentication
  - Option 2: Set `AZURE_OPENAI_API_KEY` in your local `.env` file for traditional API key authentication

**For Azure OpenAI**:
- Ensure your Azure OpenAI resource has the `gpt-4.1-mini` model deployed
- API version `2025-01-01-preview` is recommended for latest features
- The deployment automatically configures the necessary role assignments

### Switching Between OpenAI Services

To use **OpenAI** instead of Azure OpenAI, modify `src/agent/travel_agent.py`:

```python
# Change this line:
chat_service = get_chat_completion_service(ChatServices.AZURE_OPENAI)

# To this:
chat_service = get_chat_completion_service(ChatServices.OPENAI)
```

## API Endpoints

### Web Interface
- `GET /` - Main chat interface
- `GET /health` - Health check endpoint

### Chat API
- `POST /chat/message` - Send a message to the agent
- `POST /chat/stream` - Stream a conversation with the agent
- `GET /chat/sessions` - Get active chat sessions
- `DELETE /chat/sessions/{session_id}` - Clear a chat session

### A2A Protocol
- `GET /a2a/` - Agent discovery and capabilities
- `POST /a2a/tasks/send` - Send tasks to the agent
- `POST /a2a/tasks/stream` - Stream tasks with real-time updates

## 📁 Project Structure

```
MultiAgent-kubecon2025/
├── src/
│   ├── agent/                       # Agent implementation
│   │   ├── travel_agent.py          # Semantic Kernel multi-agent orchestration
│   │   ├── agent_executor.py        # A2A protocol executor
│   │   ├── a2a_server.py            # A2A server integration
│   │   ├── mcp_currency_server.py   # 🆕 MCP server for currency agent
│   │   ├── mcp_activity_server.py   # 🆕 MCP server for activity agent
│   │   └── mcp_coordinator.py       # 🆕 MCP client coordinator
│   ├── api/
│   │   └── chat.py                  # REST API endpoints
│   └── storage/
│       └── cosmos_storage.py        # (Removed - using in-memory)
├── templates/
│   └── index.html                   # Modern web chat interface
├── static/
│   ├── css/style.css                # Responsive styling
│   └── js/chat.js                   # Real-time chat functionality
├── manifests/                       # Kubernetes deployment files
│   └── deployment.yaml              # AKS deployment configuration
├── infra/                           # Azure infrastructure (Bicep)
│   ├── main.bicep                   # Main infrastructure template
│   └── modules/
│       └── core-resources.bicep     # AKS, ACR, OpenAI resources
├── docs/                            # 🆕 Documentation
│   ├── MCP_INTEGRATION.md           # MCP protocol integration guide
│   └── PHASE1_TEST_RESULTS.md       # Phase 1 testing results
├── test_mcp_simple.py               # 🆕 MCP integration tests
├── test_mcp_local.py                # 🆕 Full MCP test suite (WIP)
├── main.py                          # FastAPI application entry point
├── azure.yaml                       # Azure Developer CLI config
├── pyproject.toml                   # Python dependencies (includes MCP!)
├── Dockerfile                       # Container image definition
└── README.md                        # This file
```

---

## � Configuration

### Option 1: Interactive Setup (Recommended)

Run the interactive setup script that will guide you through configuration:

```bash
python setup_project.py
```

This will:
- Prompt for your Azure resource information
- Create a `.env` file with your configuration
- Validate your inputs
- Show next steps for deployment

### Option 2: Manual Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Azure values:
   ```bash
   # Required values
   PUBLIC_IP=<your-aks-loadbalancer-ip>
   AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
   ACR_NAME=<your-acr-name>
   ```

3. Never commit `.env` to version control (already in `.gitignore`)

### Required Azure Resources

| Resource | Purpose | Configuration |
|----------|---------|---------------|
| **Azure Kubernetes Service (AKS)** | Host multi-agent system | Public LoadBalancer IP required |
| **Azure OpenAI** | LLM for agents | gpt-4o-mini deployment |
| **Azure Container Registry (ACR)** | Store Docker images | Integrated with AKS |
| **Managed Identity** | Authentication | Assigned to AKS nodes |

### Security Best Practices

- ✅ `.env` files are git-ignored
- ✅ Use managed identities (not service principals)
- ✅ Store secrets in Azure Key Vault (production)
- ✅ Enable RBAC on AKS cluster
- ❌ Never commit IPs, endpoints, or credentials
- ❌ Don't use default credentials

---

## �🚀 Quick Start

### Prerequisites
- Python 3.10+
- Azure subscription
- Azure CLI
- Azure Developer CLI (azd)
- kubectl

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/darkanita/MultiAgent-kubecon2025.git
cd MultiAgent-kubecon2025

# Choose your branch
git checkout main              # Stable monolithic version (deployed)
# OR
git checkout microservices     # MCP-enabled version (development)
```

### 2. Deploy to Azure

```bash
# Login to Azure
azd auth login

# Provision and deploy
azd up

# Get the external IP
kubectl get service -n multiagent-kubecon-simple
```

### 3. Test Locally (MCP Branch)

```bash
# Activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run MCP integration tests
python test_mcp_simple.py

# Start the application
uvicorn main:app --reload
```

---

## 💬 Example Queries

Try these in the chat interface:

1. **Currency + Planning**:  
   *"I'm traveling to Seoul for 2 days with $100/day. Convert to KRW and suggest activities."*

2. **Restaurant Recommendations**:  
   *"Find budget-friendly Korean restaurants in Gangnam district."*

3. **Activity Planning**:  
   *"Plan a cultural 3-day itinerary for Kyoto with moderate budget."*

4. **Currency Conversion**:  
   *"What's 500 USD in Japanese Yen?"*

---

## 🔧 MCP Tools Available

### Currency Exchange Agent
| Tool | Description |
|------|-------------|
| `get_exchange_rate` | Get current exchange rate between two currencies |
| `convert_amount` | Convert a specific amount from one currency to another |

### Activity Planner Agent
| Tool | Description |
|------|-------------|
| `plan_activities` | Generate day-by-day activity itinerary |
| `suggest_restaurants` | Dining recommendations by cuisine/budget |
| `suggest_attractions` | Tourist attractions by category |

---

## 🌐 Protocol Integration

### A2A Protocol (Agent-to-Agent)
- ✅ Agent discovery via Agent Cards
- ✅ Task coordination and delegation
- ✅ Streaming support
- ✅ Session management
- 📍 Endpoint: `/a2a/`

### MCP Protocol (Model Context Protocol) 🆕
- ✅ Standardized tool definitions
- ✅ Type-safe function calling
- ✅ Stdio-based communication
- ✅ 5 tools across 2 agents
- 📖 Docs: `docs/MCP_INTEGRATION.md`

---

## 🧪 Testing

### Run MCP Integration Tests
```bash
# Basic validation (recommended)
python test_mcp_simple.py

# Full integration test (WIP)
python test_mcp_local.py
```

### Expected Output
```
✅ PASSED: Module Imports
✅ PASSED: Tool Definitions
✅ PASSED: Currency Server
✅ PASSED: Activity Server
```

See `docs/PHASE1_TEST_RESULTS.md` for detailed results.

---

## 📊 Branches & Deployments

| Branch | Status | Description | External IP |
|--------|--------|-------------|-------------|
| `main` | ✅ Deployed | Stable monolithic app on AKS (Phase 1) | http://<YOUR-PHASE1-PUBLIC-IP> |
| `microservices` | ✅ Deployed | MCP-enabled microservices on AKS (Phase 2) | http://<YOUR-PUBLIC-IP> |

---

## 🗺️ Roadmap

- [x] **Phase 1**: Monolithic with MCP Integration (✅ Deployed at <YOUR-PHASE1-PUBLIC-IP>)
  - [x] Add MCP SDK
  - [x] Create MCP servers for agents
  - [x] Define 5 MCP tools
  - [x] Testing and documentation
  - [x] Deploy to AKS with azd

- [x] **Phase 2**: Microservices Architecture (⚠️  PARTIALLY DEPLOYED at <YOUR-PUBLIC-IP>)
  - [x] Split into separate services (coordinator, currency-agent, activity-agent)
  - [x] Independent Dockerfiles for each service
  - [x] Kubernetes multi-service deployment
  - [x] Service discovery via K8s DNS
  - [ ] MCP communication over HTTP ⚠️  **NOT ACTIVE** (using in-process Semantic Kernel)
  - [x] Azure OpenAI integration with gpt-4o-mini
  - [ ] **TODO**: Implement HTTP MCP client in coordinator to call MCP servers

- [ ] **Phase 3**: Add New Agents (Planned 📅)
  - [ ] HR Agent (human resources)
  - [ ] Flight Booking Agent
  - [ ] Hotel Reservation Agent
  - [ ] Dynamic agent registration

---

## 📚 Documentation

- [MCP Integration Guide](docs/MCP_INTEGRATION.md)
- [Phase 1 Test Results](docs/PHASE1_TEST_RESULTS.md)
- [Azure Setup Guide](AZURE_SETUP.md)
- [Security Guidelines](SECURITY.md)

---

### Agent Card Example

```json
{
  "name": "SK Travel Agent",
  "description": "Semantic Kernel-based travel agent...",
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "trip_planning_sk",
      "name": "Semantic Kernel Trip Planning",
      "description": "Handles comprehensive trip planning...",
      "tags": ["trip", "planning", "travel", "currency"]
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Create an issue in the repository
- Check the [Semantic Kernel documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- Review the [A2A protocol specification](https://google.github.io/A2A/)

---

**Built with ❤️ using Semantic Kernel, FastAPI, and Azure**
