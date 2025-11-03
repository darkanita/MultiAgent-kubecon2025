# Multi-Agent KubeCon 2025 Demo

A Multi-Agent AI System deployed on Azure Kubernetes Service (AKS) with Semantic Kernel, featuring A2A (Agent-to-Agent) and MCP (Model Context Protocol) integration.

## 🎯 Architecture

- **Platform**: Azure Kubernetes Service (AKS)
- **AI Framework**: Microsoft Semantic Kernel
- **Protocols**: A2A (Agent-to-Agent), MCP (Model Context Protocol)
- **Backend**: FastAPI with Python 3.11
- **Frontend**: Modern HTML/CSS/JavaScript web interface
- **Infrastructure**: Azure (AKS, ACR, OpenAI, Cosmos DB, VNet, Log Analytics)

## 🚀 Quick Start

### Prerequisites

- Azure CLI (`az`)
- Azure Developer CLI (`azd`)
- Docker Desktop
- kubectl

### Deploy Infrastructure and Application

1. **Login to Azure**:
   ```bash
   azd auth login
   ```

2. **Deploy everything**:
   ```bash
   azd up
   ```
   
   This will:
   - Create resource group: `rg-{environmentName}`
   - Deploy AKS cluster
   - Deploy Azure Container Registry (ACR)
   - Deploy Azure OpenAI with gpt-4o-mini model
   - Deploy Cosmos DB
   - Create Virtual Network and Log Analytics
   - Build and push container image
   - Deploy application to AKS

3. **Get the LoadBalancer IP**:
   ```bash
   kubectl get svc -n multiagent-kubecon-simple
   ```

4. **Access the application**:
   Open browser to `http://<EXTERNAL-IP>`

## 📁 Project Structure

```
MultiAgent-kubecon2025/
├── .azure/                    # AZD environment configuration
├── infra/                     # Infrastructure as Code
│   ├── main.bicep            # Main Bicep template (resource group scope)
│   └── modules/
│       └── core-resources.bicep  # Core Azure resources
├── manifests/                 # Kubernetes manifests
│   ├── configmap.yaml        # Application configuration
│   └── deployment.yaml       # K8s deployment and service
├── src/                       # Application source code
│   ├── agent/                # Semantic Kernel agents
│   │   ├── travel_agent.py   # Travel agent implementation
│   │   ├── a2a_server.py     # A2A protocol server
│   │   └── agent_executor.py # Agent executor
│   └── api/
│       └── chat.py           # REST API endpoints
├── static/                    # Frontend assets
│   ├── css/
│   └── js/
├── templates/                 # HTML templates
│   └── index.html            # Main web interface
├── main.py                    # FastAPI application entry point
├── Dockerfile                 # Container image definition
├── azure.yaml                 # AZD configuration
└── requirements.txt           # Python dependencies
```

## 🔧 Infrastructure Components

### Azure Resources

| Resource | Purpose |
|----------|---------|
| **AKS** | Kubernetes cluster for running multi-agent application |
| **ACR** | Private container registry for Docker images |
| **Azure OpenAI** | AI services with gpt-4o-mini deployment |
| **Cosmos DB** | Serverless NoSQL database for agent state |
| **Virtual Network** | Network isolation and security |
| **Log Analytics** | Monitoring and logging |

### Kubernetes Resources

- **Namespace**: `multiagent-kubecon-simple`
- **Deployment**: `multiagent-app` (1 replica)
- **Service**: `multiagent-service` (LoadBalancer)
- **ConfigMap**: `app-config` (environment variables)
- **Secret**: `openai-secret` (API credentials)

## 🧪 Testing

### Health Check
```bash
curl http://<EXTERNAL-IP>/health
```

### Test Currency Exchange Agent
```bash
curl -X POST http://<EXTERNAL-IP>/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the USD to EUR exchange rate?"}'
```

### Test Trip Planning Agent
```bash
curl -X POST http://<EXTERNAL-IP>/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Plan a 3-day trip to Tokyo with a $500 budget"}'
```

### A2A Agent Card
```bash
curl http://<EXTERNAL-IP>/a2a/
```

## 📊 Monitoring

### View Application Logs
```bash
kubectl logs -n multiagent-kubecon-simple -l app=multiagent-app -f
```

### View Pod Status
```bash
kubectl get pods -n multiagent-kubecon-simple
```

### Scale Application
```bash
kubectl scale deployment multiagent-app -n multiagent-kubecon-simple --replicas=3
```

## 🔐 Security

- API keys stored in Kubernetes Secrets
- Network isolation via Virtual Network
- RBAC enabled on AKS cluster
- ACR with admin user for simplified authentication

## 🎨 Features

### Multi-Agent System
- **TravelManagerAgent**: Main orchestrator
- **CurrencyExchangeAgent**: Real-time currency conversion
- **ActivityPlannerAgent**: Trip planning and recommendations

### Protocols
- **A2A (Agent-to-Agent)**: Multi-agent communication
- **MCP (Model Context Protocol)**: Model integration

### Web Interface
- Real-time chat interface
- Streaming responses
- Session management
- Mobile-responsive design

## 🛠️ Development

### Update Kubernetes Manifests
```bash
# Edit manifests/deployment.yaml
kubectl apply -f manifests/ -n multiagent-kubecon-simple
```

### Build and Push New Image
```bash
# Build
docker build -t <ACR_NAME>.azurecr.io/multiagent-kubecon-simple/app:v2 .

# Push
docker push <ACR_NAME>.azurecr.io/multiagent-kubecon-simple/app:v2

# Update deployment
kubectl set image deployment/multiagent-app \
  app=<ACR_NAME>.azurecr.io/multiagent-kubecon-simple/app:v2 \
  -n multiagent-kubecon-simple
```

## 🗑️ Cleanup

To delete all resources:

```bash
azd down
```

Or manually:

```bash
# Delete resource group
az group delete --name rg-{environmentName} --yes --no-wait
```

## 📝 Configuration

### Environment Variables

Set in `manifests/configmap.yaml`:
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_COSMOS_ENDPOINT`: Cosmos DB endpoint URL

Set in Kubernetes Secret `openai-secret`:
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key

Set in deployment:
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Model deployment name (gpt-4o-mini)
- `AZURE_OPENAI_API_VERSION`: API version (2024-08-01-preview)

## 🎓 KubeCon 2025 Demo

This project demonstrates:
- ✅ Multi-Agent AI systems on Kubernetes
- ✅ Azure Developer CLI (AZD) for simplified deployment
- ✅ Infrastructure as Code with Bicep
- ✅ Container orchestration with AKS
- ✅ AI integration with Azure OpenAI
- ✅ Modern web applications with FastAPI
- ✅ A2A and MCP protocol integration

## 📚 Resources

- [Azure Kubernetes Service](https://azure.microsoft.com/en-us/services/kubernetes-service/)
- [Semantic Kernel](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Azure Developer CLI](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/)
- [A2A Protocol](https://github.com/a2aproject)

## 🤝 Contributing

For demo purposes at KubeCon 2025. Feel free to fork and adapt for your needs!

## 📄 License

MIT License
