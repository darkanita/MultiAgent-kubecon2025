# Development Container for Multi-Agent KubeCon 2025

This devcontainer provides a fully configured development environment for the Multi-Agent AI System on Azure Kubernetes Service.

## 🚀 Quick Start with GitHub Codespaces

### Option 1: Using GitHub Web Interface

1. Navigate to the repository on GitHub
2. Click the **Code** button (green button)
3. Select the **Codespaces** tab
4. Click **Create codespace on main**
5. Wait for the container to build and start (3-5 minutes)

### Option 2: Using GitHub CLI

```bash
gh codespace create --repo darkanita/MultiAgent-kubecon2025
```

### Option 3: Using VS Code Desktop

1. Install the [GitHub Codespaces extension](https://marketplace.visualstudio.com/items?itemName=GitHub.codespaces)
2. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Type: `Codespaces: Create New Codespace`
4. Select the repository: `darkanita/MultiAgent-kubecon2025`

## 📦 What's Included

### Tools & CLIs
- **Python 3.11** - Latest stable Python version
- **Azure CLI** - Azure resource management
- **Azure Developer CLI (azd)** - Infrastructure deployment automation
- **kubectl** - Kubernetes cluster management
- **Helm** - Kubernetes package manager
- **Docker** - Container operations (Docker-in-Docker)
- **Node.js LTS** - For any frontend tooling needs

### VS Code Extensions
- Python & Pylance - Python development
- Azure Tools - Azure resource management
- Kubernetes Tools - K8s manifest editing and cluster management
- Docker - Container management
- GitHub Copilot - AI-assisted coding
- YAML - Manifest file editing

### Python Packages
- **semantic-kernel** - AI agent framework
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **azure-cosmos** - Cosmos DB client
- **azure-identity** - Azure authentication
- **Development tools**: black, pylint, pytest

## 🔧 Initial Setup in Codespace

Once your Codespace is running, authenticate with Azure:

```bash
# 1. Login to Azure CLI (use device code for Codespaces)
az login --use-device-code

# 2. Set your Azure subscription
az account set --subscription "<your-subscription-id>"

# 3. Login to Azure Developer CLI
azd auth login --use-device-code

# 4. Verify authentication
az account show
```

## 🚢 Deploy to Azure

```bash
# Deploy infrastructure and application
azd up

# The deployment will:
# - Create Azure resources (AKS, ACR, OpenAI, Cosmos DB)
# - Build and push Docker image
# - Deploy to Kubernetes
# - Output the application URL
```

## 💻 Local Development in Codespace

Run the application locally for development:

```bash
# Install dependencies (already done by post-create script)
pip install -e .

# Set environment variables
export AZURE_OPENAI_ENDPOINT="<your-endpoint>"
export AZURE_OPENAI_API_KEY="<your-api-key>"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
export AZURE_COSMOS_ENDPOINT="<your-cosmos-endpoint>"
export AZURE_COSMOS_KEY="<your-cosmos-key>"

# Run the FastAPI application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at the forwarded port (automatically opened by Codespaces).

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src tests/

# Lint code
pylint src/

# Format code
black src/
```

## 🔍 Working with AKS from Codespace

```bash
# Get AKS credentials
az aks get-credentials --resource-group rg-kubeconagent --name <aks-cluster-name>

# View pods
kubectl get pods -n multiagent-kubecon-simple

# View logs
kubectl logs -n multiagent-kubecon-simple deployment/multiagent-app --tail=50 -f

# Port forward to access app
kubectl port-forward -n multiagent-kubecon-simple service/multiagent-service 8080:80
```

## 📁 Persistent Storage

The devcontainer automatically mounts your local `.azure` directory to persist:
- Azure CLI credentials
- Azure Developer CLI configuration
- Kubernetes config files

This means you won't need to re-authenticate every time you restart the Codespace (if you're using VS Code Desktop with Codespaces).

## 🔄 Rebuilding the Container

If you modify the devcontainer configuration:

1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type: `Codespaces: Rebuild Container`
3. Select the option and wait for rebuild

## 🌐 Port Forwarding

The following ports are automatically forwarded:
- **8000** - FastAPI application (main app)
- **8080** - Alternative port for port-forward operations

You can access these through the "Ports" tab in VS Code or via the Codespaces web interface.

## 💡 Tips for Codespaces

1. **Pause when not using** - Codespaces auto-pause after 30 minutes of inactivity
2. **Use secrets** - Store API keys in GitHub Codespaces secrets (Settings → Secrets → Codespaces)
3. **Commit often** - Your work is in the cloud; commit to save progress
4. **Use .env files** - Create a `.env` file for local environment variables (add to .gitignore)

## 🐛 Troubleshooting

### Azure CLI login issues
```bash
# Clear cached credentials
rm -rf ~/.azure

# Try login again with device code
az login --use-device-code
```

### Docker permission issues
```bash
# Add user to docker group (may require container rebuild)
sudo usermod -aG docker $USER
```

### kubectl connection issues
```bash
# Re-fetch AKS credentials
az aks get-credentials --resource-group <rg-name> --name <aks-name> --overwrite-existing
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

## 📚 Additional Resources

- [DEPLOYMENT.md](../DEPLOYMENT.md) - Complete deployment guide
- [DEPLOYMENT_SUMMARY.md](../DEPLOYMENT_SUMMARY.md) - Deployment session summary
- [README.md](../README.md) - Project overview and architecture
- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

## 🎯 KubeCon 2025 Demo Setup

For the KubeCon demo, follow these steps:

1. **Create a fresh Codespace** from the repository
2. **Authenticate** with Azure (both `az` and `azd`)
3. **Deploy infrastructure**: `azd up`
4. **Get LoadBalancer IP**: `kubectl get svc -n multiagent-kubecon-simple`
5. **Test the application**: Open the LoadBalancer IP in browser
6. **Demo the agents**: Try currency conversion and trip planning queries

The entire setup from Codespace creation to running application takes approximately 10-15 minutes.
