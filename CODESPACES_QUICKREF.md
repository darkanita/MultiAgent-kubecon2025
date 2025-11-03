# GitHub Codespaces Quick Reference

## 🚀 Launch Codespace

### From GitHub Web
```
1. Go to https://github.com/darkanita/MultiAgent-kubecon2025
2. Click "Code" → "Codespaces" → "Create codespace on main"
3. Wait 3-5 minutes for container build
```

### From VS Code
```
1. Install GitHub Codespaces extension
2. Ctrl+Shift+P → "Codespaces: Create New Codespace"
3. Select: darkanita/MultiAgent-kubecon2025
```

### From CLI
```bash
gh codespace create --repo darkanita/MultiAgent-kubecon2025
```

## 🔐 Initial Authentication

Once Codespace is running:

```bash
# 1. Azure CLI Login
az login --use-device-code

# 2. Set Subscription
az account set --subscription "<your-subscription-id>"

# 3. Azure Developer CLI Login
azd auth login --use-device-code

# 4. Verify
az account show
```

## 🚢 Deploy to Azure

```bash
# One-command deployment
azd up

# Follow prompts:
# - Environment name: kubeconagent (or your choice)
# - Location: eastus (or your preferred region)
# - Confirm deployment: Y

# Deployment creates:
# ✅ Resource Group (rg-kubeconagent)
# ✅ AKS Cluster
# ✅ Azure Container Registry
# ✅ Azure OpenAI (gpt-4o-mini)
# ✅ Cosmos DB
# ✅ Virtual Network
# ✅ Log Analytics
```

## 🧪 Test Deployment

```bash
# Get LoadBalancer IP
kubectl get svc -n multiagent-kubecon-simple multiagent-service

# Test the application
curl http://<EXTERNAL-IP>

# View logs
kubectl logs -n multiagent-kubecon-simple deployment/multiagent-app --tail=50 -f
```

## 💻 Run Locally in Codespace

```bash
# Set environment variables
export AZURE_OPENAI_ENDPOINT="<from azd output>"
export AZURE_OPENAI_API_KEY="<from Azure Portal>"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
export AZURE_COSMOS_ENDPOINT="<from azd output>"
export AZURE_COSMOS_KEY="<from Azure Portal>"

# Run FastAPI
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Access via forwarded port (automatically opens)
```

## 📝 Environment Variables

Create `.env` from template:
```bash
cp .env.template .env
nano .env  # or code .env
```

## 🔍 Common Commands

### Kubernetes
```bash
# Get AKS credentials
az aks get-credentials --resource-group rg-kubeconagent --name <aks-name>

# View all resources
kubectl get all -n multiagent-kubecon-simple

# View pods
kubectl get pods -n multiagent-kubecon-simple

# Describe pod
kubectl describe pod <pod-name> -n multiagent-kubecon-simple

# View logs (streaming)
kubectl logs -n multiagent-kubecon-simple deployment/multiagent-app --tail=50 -f

# Port forward (for local access)
kubectl port-forward -n multiagent-kubecon-simple service/multiagent-service 8080:80
```

### Azure Resources
```bash
# List resource groups
az group list --output table

# List AKS clusters
az aks list --output table

# List container registries
az acr list --output table

# View OpenAI deployments
az cognitiveservices account deployment list --resource-group rg-kubeconagent --name <openai-name>
```

### Docker/ACR
```bash
# Login to ACR
az acr login --name <acr-name>

# List images
az acr repository list --name <acr-name>

# Show tags
az acr repository show-tags --name <acr-name> --repository multiagent-kubecon-simple/app-kubeconagent
```

### AZD Commands
```bash
# Show environment
azd env list

# Get output values
azd env get-values

# Refresh deployment
azd deploy

# Clean up resources
azd down

# Monitor deployment
azd monitor
```

## 🐛 Troubleshooting

### Pod not starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n multiagent-kubecon-simple

# Check events
kubectl get events -n multiagent-kubecon-simple --sort-by='.lastTimestamp'
```

### Image pull errors
```bash
# Verify ACR authentication
az aks check-acr --resource-group rg-kubeconagent --name <aks-name> --acr <acr-name>

# Re-attach ACR to AKS
az aks update --resource-group rg-kubeconagent --name <aks-name> --attach-acr <acr-name>
```

### Application errors
```bash
# Check logs
kubectl logs -n multiagent-kubecon-simple deployment/multiagent-app

# Check environment variables
kubectl get configmap app-config -n multiagent-kubecon-simple -o yaml
kubectl get secret openai-secret -n multiagent-kubecon-simple -o yaml
```

### Port already in use (local)
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Alternative: use different port
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Azure authentication issues
```bash
# Clear Azure cache
rm -rf ~/.azure

# Re-login
az login --use-device-code
azd auth login --use-device-code
```

## 💡 Codespaces Tips

1. **Auto-pause**: Codespaces pause after 30 min inactivity (saves costs)
2. **Resume**: Reopening the Codespace resumes it automatically
3. **Secrets**: Store API keys in GitHub Settings → Secrets → Codespaces
4. **Ports**: View forwarded ports in "Ports" tab (bottom panel)
5. **Terminal**: Open multiple terminals with Ctrl+Shift+` (or Ctrl+`)
6. **Extensions**: All required extensions are pre-installed
7. **Persistence**: Files in `/workspaces` persist across rebuilds
8. **Rebuild**: Ctrl+Shift+P → "Codespaces: Rebuild Container" after config changes

## 📊 Resource Costs

**Codespaces**: ~$0.18/hour (2-core machine)
**Azure Resources** (after deployment):
- AKS: ~$73/month (1 x Standard_B2s node)
- ACR: ~$5/month (Basic tier)
- Azure OpenAI: Pay-per-use (~$0.15-0.60 per 1M tokens for gpt-4o-mini)
- Cosmos DB: Pay-per-use (Serverless, minimal for demo)
- VNet: Free
- Log Analytics: ~$2.76/GB ingested

**Cost Saving Tips**:
- Stop AKS when not in use: `az aks stop --resource-group rg-kubeconagent --name <aks-name>`
- Delete resources after demo: `azd down`
- Use Codespaces only when needed (auto-pauses)

## 🎯 KubeCon Demo Checklist

- [ ] Create Codespace
- [ ] Authenticate (`az login`, `azd auth login`)
- [ ] Deploy infrastructure (`azd up`)
- [ ] Verify pods running (`kubectl get pods -n multiagent-kubecon-simple`)
- [ ] Get LoadBalancer IP (`kubectl get svc -n multiagent-kubecon-simple`)
- [ ] Test currency conversion: "Convert 100 USD to EUR"
- [ ] Test trip planning: "Plan a 3-day trip to Paris with $1000 budget"
- [ ] Show logs (`kubectl logs ...`)
- [ ] Demonstrate architecture (README diagrams)
- [ ] Clean up (`azd down`)

## 📚 Documentation

- `.devcontainer/README.md` - Comprehensive Codespaces guide
- `DEPLOYMENT.md` - Detailed deployment instructions
- `DEPLOYMENT_SUMMARY.md` - Complete deployment session summary
- `README.md` - Project overview and architecture

## 🆘 Need Help?

1. Check `kubectl logs` for application errors
2. Review `DEPLOYMENT.md` for troubleshooting steps
3. Verify all environment variables are set correctly
4. Ensure Azure subscription has sufficient quota
5. Check AKS and ACR are in the same region

## ⏱️ Estimated Times

- Codespace creation: 3-5 minutes
- `azd up` deployment: 15-20 minutes
- Local app startup: 30 seconds
- Pod deployment (after infra): 2-3 minutes
- Total demo setup: ~20-25 minutes
