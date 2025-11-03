# 🚀 Codespaces Setup Checklist

Use this checklist when setting up your GitHub Codespace for the first time.

## Pre-Flight Check ✈️

- [ ] GitHub account with access to the repository
- [ ] Azure subscription with sufficient credits/quota
- [ ] Azure subscription ID handy

## Launch Codespace 🎯

- [ ] Navigate to https://github.com/darkanita/MultiAgent-kubecon2025
- [ ] Click **Code** button → **Codespaces** tab
- [ ] Click **Create codespace on main**
- [ ] Wait 3-5 minutes for container to build
- [ ] Verify terminal shows "🎉 Development environment is ready!"

## Authentication Setup 🔐

### Azure CLI
- [ ] Run: `az login --use-device-code`
- [ ] Open the displayed URL in browser
- [ ] Enter the provided code
- [ ] Sign in with Azure credentials
- [ ] Return to Codespace terminal

### Set Azure Subscription
- [ ] Run: `az account list --output table`
- [ ] Copy your subscription ID
- [ ] Run: `az account set --subscription "<your-subscription-id>"`
- [ ] Verify: `az account show --output table`

### Azure Developer CLI
- [ ] Run: `azd auth login --use-device-code`
- [ ] Open the displayed URL in browser
- [ ] Enter the provided code
- [ ] Sign in with Azure credentials
- [ ] Return to Codespace terminal

### Verification
- [ ] Run: `az account show`
- [ ] Confirm correct subscription is selected
- [ ] Run: `azd version`
- [ ] Confirm azd is authenticated

## Deploy Infrastructure 🏗️

### Initial Deployment
- [ ] Run: `azd up`
- [ ] Enter environment name (e.g., `kubeconagent`)
- [ ] Select Azure location (e.g., `eastus`)
- [ ] Confirm deployment by typing `Y`
- [ ] Wait 15-20 minutes for deployment to complete

### Post-Deployment Verification
- [ ] Note the resource group name (e.g., `rg-kubeconagent`)
- [ ] Note the AKS cluster name
- [ ] Note the ACR name
- [ ] Note the Azure OpenAI endpoint
- [ ] Note the Cosmos DB endpoint

## Kubernetes Setup ☸️

### Get AKS Credentials
- [ ] Run: `az aks get-credentials --resource-group rg-kubeconagent --name <aks-cluster-name>`
- [ ] Verify: `kubectl config current-context`

### Check Deployment
- [ ] Run: `kubectl get pods -n multiagent-kubecon-simple`
- [ ] Verify pod status is `Running` (1/1)
- [ ] Run: `kubectl get svc -n multiagent-kubecon-simple`
- [ ] Note the LoadBalancer EXTERNAL-IP

### View Application Logs
- [ ] Run: `kubectl logs -n multiagent-kubecon-simple deployment/multiagent-app --tail=50`
- [ ] Verify no errors in logs

## Test Application 🧪

### Access Application
- [ ] Open browser to `http://<EXTERNAL-IP>`
- [ ] Verify web UI loads correctly
- [ ] Check chat interface is visible

### Test Agent Functionality
- [ ] Test currency conversion: "Convert 100 USD to EUR"
- [ ] Verify response with current exchange rate
- [ ] Test trip planning: "Plan a 3-day trip to Paris with $1000 budget"
- [ ] Verify detailed itinerary response

### Monitor Performance
- [ ] Run: `kubectl top pods -n multiagent-kubecon-simple`
- [ ] Check CPU and memory usage
- [ ] Run: `kubectl get events -n multiagent-kubecon-simple --sort-by='.lastTimestamp'`
- [ ] Review recent events

## Local Development (Optional) 💻

### Set Environment Variables
- [ ] Copy `.env.template` to `.env`
- [ ] Fill in Azure OpenAI endpoint
- [ ] Fill in Azure OpenAI API key
- [ ] Fill in Cosmos DB endpoint
- [ ] Fill in Cosmos DB key

### Run Application Locally
- [ ] Run: `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
- [ ] Access via forwarded port (Ports tab)
- [ ] Test locally before deploying changes

## Cleanup 🧹 (After Demo)

### Delete Azure Resources
- [ ] Run: `azd down`
- [ ] Confirm deletion by typing `Y`
- [ ] Wait for resources to be deleted
- [ ] Verify in Azure Portal

### Stop Codespace
- [ ] Save and commit any changes
- [ ] Close Codespace browser tab (auto-pauses after 30 min)
- [ ] Or manually stop from GitHub Codespaces page

## Troubleshooting Checklist 🔧

### If authentication fails:
- [ ] Clear Azure cache: `rm -rf ~/.azure`
- [ ] Re-login: `az login --use-device-code`
- [ ] Re-authenticate azd: `azd auth login --use-device-code`

### If deployment fails:
- [ ] Check Azure subscription has sufficient quota
- [ ] Verify region supports all required services
- [ ] Check `azd` logs for error messages
- [ ] Try: `azd down` then `azd up` again

### If pods won't start:
- [ ] Check pod status: `kubectl describe pod <pod-name> -n multiagent-kubecon-simple`
- [ ] Check events: `kubectl get events -n multiagent-kubecon-simple --sort-by='.lastTimestamp'`
- [ ] Check ACR connection: `az aks check-acr --resource-group rg-kubeconagent --name <aks-name> --acr <acr-name>`

### If application returns errors:
- [ ] Check logs: `kubectl logs -n multiagent-kubecon-simple deployment/multiagent-app --tail=100`
- [ ] Verify ConfigMap: `kubectl get configmap app-config -n multiagent-kubecon-simple -o yaml`
- [ ] Verify Secret: `kubectl get secret openai-secret -n multiagent-kubecon-simple -o yaml`
- [ ] Check OpenAI API key is valid

### If LoadBalancer has no external IP:
- [ ] Wait 2-3 minutes (Azure provisioning time)
- [ ] Check service: `kubectl describe svc multiagent-service -n multiagent-kubecon-simple`
- [ ] Verify AKS can create LoadBalancers in subscription

## Quick Commands Reference 📖

```bash
# Status checks
kubectl get all -n multiagent-kubecon-simple
kubectl top pods -n multiagent-kubecon-simple
kubectl logs -n multiagent-kubecon-simple deployment/multiagent-app --tail=50 -f

# Azure resources
az aks list --output table
az acr list --output table
az group list --output table

# AZD commands
azd env list
azd env get-values
azd deploy
azd down
azd monitor

# Port forwarding (alternative access)
kubectl port-forward -n multiagent-kubecon-simple service/multiagent-service 8080:80
```

## Success Criteria ✅

You're ready for the demo when:
- [ ] Codespace is running smoothly
- [ ] All Azure resources are deployed
- [ ] Pod is in Running state (1/1)
- [ ] LoadBalancer has external IP
- [ ] Web UI loads in browser
- [ ] Currency conversion works
- [ ] Trip planning works
- [ ] Logs show no errors
- [ ] Response times are acceptable

## Time Estimates ⏱️

- Codespace creation: 3-5 minutes
- Azure authentication: 2-3 minutes
- Infrastructure deployment (`azd up`): 15-20 minutes
- Application verification: 2-3 minutes
- **Total setup time: ~20-30 minutes**

## Notes 📝

- Codespaces auto-pause after 30 minutes of inactivity
- Azure resources incur costs while running
- Always run `azd down` after demos to save costs
- Commit changes before closing Codespace
- Environment persists across Codespace restarts

---

**Need more help?** See:
- `.devcontainer/README.md` - Comprehensive guide
- `CODESPACES_QUICKREF.md` - Quick command reference
- `DEPLOYMENT.md` - Detailed deployment guide
- `DEPLOYMENT_SUMMARY.md` - Complete resource list
