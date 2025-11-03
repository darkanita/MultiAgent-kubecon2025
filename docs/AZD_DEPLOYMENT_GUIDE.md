# AZD Deployment Guide for Phase 2 Microservices

This guide shows how to deploy the **Phase 2 Microservices architecture** using Azure Developer CLI (`azd`), running in parallel with your existing **Phase 1 Monolithic** deployment.

---

## 📋 Prerequisites

✅ You already have:
- Azure Developer CLI installed (`azd version`)
- Azure CLI installed and authenticated (`az login`)
- Phase 1 deployed with environment `kubeconagent`
- kubectl installed

---

## 🎯 Two AZD Environments Strategy

You'll maintain **two separate azd environments**:

```
┌─────────────────────────────────────────────┐
│  Environment 1: kubeconagent (Phase 1)      │
│  ─────────────────────────────────          │
│  Config: azure.yaml                         │
│  Bicep: infra/main.bicep                    │
│  RG: rg-kubeconagent                        │
│  Architecture: Monolithic (1 pod)           │
│  Status: PRODUCTION ✅                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Environment 2: kubecon-micro (Phase 2)     │
│  ─────────────────────────────────          │
│  Config: azure.microservices.yaml           │
│  Bicep: infra/main.microservices.bicep      │
│  RG: rg-kubecon-micro                       │
│  Architecture: Microservices (3+ pods)      │
│  Status: TESTING 🚧                          │
└─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start: Deploy Phase 2

### Step 1: Create New Environment

```bash
cd /c/Users/alopezmoreno/Downloads/Kubecon/MultiAgent-kubecon2025

# Create new azd environment for microservices
azd env new kubecon-micro

# Select your subscription (same as Phase 1)
azd auth login

# Set the location (recommend same as Phase 1)
azd env set AZURE_LOCATION eastus
```

### Step 2: Configure Environment Variables

```bash
# Get OpenAI details from Phase 1
OPENAI_KEY=$(az cognitiveservices account keys list \
  --resource-group rg-kubeconagent \
  --name $(az cognitiveservices account list --resource-group rg-kubeconagent --query "[0].name" -o tsv) \
  --query "key1" -o tsv)

# Set in new environment
azd env set AZURE_OPENAI_API_KEY $OPENAI_KEY

# Optional: Share ACR (if you want to use existing one)
ACR_NAME=$(az acr list --resource-group rg-kubeconagent --query "[0].name" -o tsv)
azd env set SHARED_ACR_NAME $ACR_NAME
```

### Step 3: Provision Infrastructure

```bash
# Use microservices-specific configuration
azd provision --config azure.microservices.yaml

# This will:
# ✅ Create new resource group: rg-kubecon-micro
# ✅ Create new AKS cluster with 3 nodes
# ✅ Create new ACR (or use shared)
# ✅ Create new OpenAI (or use shared)
# ✅ Configure networking and RBAC
# ✅ Run postprovision hooks
```

**Expected output:**
```
Provisioning Azure resources (azd provision)
Provisioning Azure resources can take some time

  You can view detailed progress in the Azure Portal:
  https://portal.azure.com/#blade/HubsExtension/DeploymentDetailsBlade/...

  (✓) Done: Resource group: rg-kubecon-micro
  (✓) Done: Container registry: acrkubeconmicro...
  (✓) Done: AKS cluster: aks-kubecon-micro
  (✓) Done: Log Analytics workspace
  (✓) Done: Application Insights

SUCCESS: Your application was provisioned in Azure in 8 minutes 32 seconds.
```

### Step 4: Deploy Services

```bash
# Deploy all 3 microservices
azd deploy --config azure.microservices.yaml

# This will:
# ✅ Build 3 Docker images (coordinator, currency, activity)
# ✅ Push to ACR
# ✅ Deploy to AKS namespace: multiagent-microservices
# ✅ Create LoadBalancer for coordinator
# ✅ Wait for pods to be ready
```

**Expected output:**
```
Deploying services (azd deploy)

  (✓) Done: Building coordinator (1m 23s)
  (✓) Done: Building currency-agent (45s)
  (✓) Done: Building activity-agent (42s)
  (✓) Done: Pushing coordinator to ACR (34s)
  (✓) Done: Pushing currency-agent to ACR (28s)
  (✓) Done: Pushing activity-agent to ACR (26s)
  (✓) Done: Deploying to AKS (1m 12s)

🎉 Microservices deployment completed!

📊 Deployment Summary:
  Environment: kubecon-micro
  Resource Group: rg-kubecon-micro
  AKS Cluster: aks-kubecon-micro-xxxxx
  Namespace: multiagent-microservices

🌐 Getting external IP...
NAME                  TYPE           EXTERNAL-IP      PORT(S)        AGE
coordinator-service   LoadBalancer   20.85.123.45     80:30123/TCP   2m
```

### Step 5: Verify Deployment

```bash
# Check pods
kubectl get pods -n multiagent-microservices

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# coordinator-xxxxxx                1/1     Running   0          2m
# currency-agent-xxxxxx             1/1     Running   0          2m
# activity-agent-xxxxxx             1/1     Running   0          2m

# Get external IP
EXTERNAL_IP=$(kubectl get svc coordinator-service -n multiagent-microservices -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: $EXTERNAL_IP"

# Test A2A endpoint
curl http://$EXTERNAL_IP/a2a/

# Test Web UI
curl http://$EXTERNAL_IP/health
```

---

## 🔄 Managing Both Environments

### Switch Between Environments

```bash
# Work with Phase 1 (Monolithic)
azd env select kubeconagent
azd deploy --config azure.yaml

# Work with Phase 2 (Microservices)
azd env select kubecon-micro
azd deploy --config azure.microservices.yaml
```

### View Both Environments

```bash
# List all environments
azd env list

# Output:
# NAME           DEFAULT   LOCAL   REMOTE
# kubeconagent   false     true    false
# kubecon-micro  true      true    false

# View Phase 1 details
azd env select kubeconagent
azd env get-values

# View Phase 2 details
azd env select kubecon-micro
azd env get-values
```

### Compare Deployments

```bash
# Phase 1 pods
kubectl get pods -n multiagent-kubecon-simple

# Phase 2 pods
kubectl get pods -n multiagent-microservices

# Phase 1 services
kubectl get svc -n multiagent-kubecon-simple

# Phase 2 services
kubectl get svc -n multiagent-microservices
```

---

## 📁 File Structure for AZD

After implementing Phase 2, your structure will be:

```
MultiAgent-kubecon2025/
├── azure.yaml                           # Phase 1 config
├── azure.microservices.yaml             # Phase 2 config (NEW)
├── infra/
│   ├── main.bicep                       # Phase 1 infrastructure
│   ├── main.microservices.bicep         # Phase 2 infrastructure (NEW)
│   └── modules/
│       ├── core-resources.bicep         # Shared module
│       └── microservices-aks.bicep      # Microservices-specific (NEW)
├── Dockerfile                           # Phase 1 monolithic
├── Dockerfile.coordinator               # Phase 2 coordinator (NEW)
├── Dockerfile.currency                  # Phase 2 currency agent (NEW)
├── Dockerfile.activity                  # Phase 2 activity agent (NEW)
├── manifests/
│   ├── deployment.yaml                  # Phase 1
│   └── microservices/                   # Phase 2 (NEW)
│       ├── coordinator/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── currency-agent/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       └── activity-agent/
│           ├── deployment.yaml
│           └── service.yaml
└── src/
    ├── main.py                          # Phase 1 entry point
    └── services/                        # Phase 2 (NEW)
        ├── coordinator/
        │   └── main.py
        ├── currency_agent/
        │   └── main.py
        └── activity_agent/
            └── main.py
```

---

## 🛠️ Common AZD Commands

### Provision Only (Create Infrastructure)

```bash
azd provision --config azure.microservices.yaml
```

### Deploy Only (Update Services)

```bash
azd deploy --config azure.microservices.yaml
```

### Full Pipeline (Provision + Deploy)

```bash
azd up --config azure.microservices.yaml
```

### View Logs

```bash
# AZD logs
azd monitor --config azure.microservices.yaml

# Direct kubectl logs
kubectl logs -n multiagent-microservices -l app=coordinator -f --tail=50
```

### Update Single Service

```bash
# Rebuild and deploy just coordinator
azd deploy coordinator --config azure.microservices.yaml

# Rebuild and deploy just currency agent
azd deploy currency-agent --config azure.microservices.yaml
```

### Tear Down

```bash
# Delete Phase 2 (keeps Phase 1 running)
azd env select kubecon-micro
azd down --config azure.microservices.yaml --purge

# This will DELETE:
# ❌ Resource group: rg-kubecon-micro
# ❌ All resources in it (AKS, ACR, etc.)
# ✅ Phase 1 remains untouched
```

---

## 🔐 Sharing Resources Between Environments

### Option 1: Share ACR (Recommended)

```bash
# Use Phase 1's ACR in Phase 2
ACR_NAME=$(az acr list --resource-group rg-kubeconagent --query "[0].name" -o tsv)

# Set in Phase 2 environment
azd env select kubecon-micro
azd env set SHARED_ACR_NAME $ACR_NAME

# Update main.microservices.bicep to use existing ACR
```

### Option 2: Share OpenAI (Recommended)

```bash
# Get Phase 1 OpenAI details
OPENAI_ID=$(az cognitiveservices account list --resource-group rg-kubeconagent --query "[0].id" -o tsv)
OPENAI_ENDPOINT=$(az cognitiveservices account list --resource-group rg-kubeconagent --query "[0].properties.endpoint" -o tsv)

# Set in Phase 2 environment
azd env select kubecon-micro
azd env set SHARED_OPENAI_ID $OPENAI_ID
azd env set AZURE_OPENAI_ENDPOINT $OPENAI_ENDPOINT

# Update main.microservices.bicep to use existing OpenAI
```

### Option 3: Separate Everything (Testing)

```bash
# Each environment gets its own ACR and OpenAI
# Good for complete isolation
# Higher cost (~2x)
```

---

## 📊 Cost Management

### View Costs by Environment

```bash
# Phase 1 costs
az consumption usage list --resource-group rg-kubeconagent

# Phase 2 costs
az consumption usage list --resource-group rg-kubecon-micro
```

### Stop/Start AKS to Save Costs

```bash
# Stop Phase 2 AKS (keeps resources, stops compute)
az aks stop --resource-group rg-kubecon-micro --name $(az aks list --resource-group rg-kubecon-micro --query "[0].name" -o tsv)

# Start again
az aks start --resource-group rg-kubecon-micro --name $(az aks list --resource-group rg-kubecon-micro --query "[0].name" -o tsv)
```

---

## 🧪 Testing Workflow

### 1. Deploy Phase 2

```bash
azd env select kubecon-micro
azd up --config azure.microservices.yaml
```

### 2. Test Both Environments

```bash
# Test Phase 1 (Monolithic)
PHASE1_IP=$(kubectl get svc multiagent-service -n multiagent-kubecon-simple -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$PHASE1_IP/a2a/

# Test Phase 2 (Microservices)
PHASE2_IP=$(kubectl get svc coordinator-service -n multiagent-microservices -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$PHASE2_IP/a2a/
```

### 3. Compare Logs

```bash
# Phase 1 logs (no MCP - monolithic)
kubectl logs -n multiagent-kubecon-simple -l app=multiagent-kubecon-simple --tail=100

# Phase 2 logs (with MCP - microservices)
kubectl logs -n multiagent-microservices -l app=coordinator --tail=100 | grep "🚀 \[MCP\]"
```

### 4. Load Test (Optional)

```bash
# Test Phase 2
for i in {1..10}; do
  curl -X POST http://$PHASE2_IP/api/chat/message \
    -H "Content-Type: application/json" \
    -d '{"message":"Convert 100 USD to EUR","session_id":"test-'$i'"}' &
done
wait

# Check pod scaling
kubectl get pods -n multiagent-microservices -w
```

### 5. Validate MCP Communication

```bash
# Should see MCP logs
kubectl logs -n multiagent-microservices -l app=coordinator | grep "🚀 \[MCP\]"

# Expected:
# 🔌 [MCP] Connecting to currency-agent MCP server...
# ✅ [MCP] Connected to currency-agent
# 🚀 [MCP] Calling tool 'convert_currency' on currency-agent
# ✅ [MCP] Tool executed successfully
```

---

## 🆘 Troubleshooting

### Issue: `azd provision` fails

```bash
# Check Azure quota
az vm list-usage --location eastus --query "[?name.value=='cores'].{Name:name.localizedValue, Current:currentValue, Limit:limit}"

# If quota exceeded, request increase or use smaller VMs
```

### Issue: Pods not starting

```bash
# Check pod status
kubectl describe pod -n multiagent-microservices [POD_NAME]

# Check events
kubectl get events -n multiagent-microservices --sort-by='.lastTimestamp'

# Check image pull
az acr repository show-tags --name $ACR_NAME --repository coordinator --output table
```

### Issue: External IP stuck in `<pending>`

```bash
# Check service
kubectl describe svc coordinator-service -n multiagent-microservices

# Usually takes 2-3 minutes, if longer:
# 1. Check Azure quota for LoadBalancers
# 2. Check AKS networking configuration
```

### Issue: Can't connect to MCP servers

```bash
# Test DNS resolution inside coordinator pod
kubectl exec -n multiagent-microservices [COORDINATOR_POD] -- nslookup currency-agent

# Test HTTP connectivity
kubectl exec -n multiagent-microservices [COORDINATOR_POD] -- curl http://currency-agent:8001/health

# Check MCP server logs
kubectl logs -n multiagent-microservices -l app=currency-agent
```

---

## ✅ Success Criteria

**Phase 2 is successfully deployed when:**

- [ ] `azd env list` shows both `kubeconagent` and `kubecon-micro`
- [ ] `kubectl get pods -n multiagent-microservices` shows 3 pods running
- [ ] `kubectl get svc coordinator-service -n multiagent-microservices` shows external IP
- [ ] `curl http://<EXTERNAL-IP>/a2a/` returns Agent Card
- [ ] Logs show `🚀 [MCP]` entries when using currency/activity tools
- [ ] Both Phase 1 and Phase 2 are accessible simultaneously
- [ ] Phase 1 still works (no disruption)

---

## 🎯 Quick Command Reference

```bash
# Create new environment
azd env new kubecon-micro

# Deploy everything
azd up --config azure.microservices.yaml

# Update just code (no infra changes)
azd deploy --config azure.microservices.yaml

# View logs
azd monitor --config azure.microservices.yaml

# Get external IP
kubectl get svc coordinator-service -n multiagent-microservices

# Delete everything
azd down --config azure.microservices.yaml --purge

# Switch environments
azd env select kubecon-micro
azd env select kubeconagent
```

---

## 📚 Next Steps

1. ✅ **Setup**: Create new azd environment
2. ✅ **Implement**: Create service code (see PHASE2_IMPLEMENTATION_PLAN.md)
3. ✅ **Deploy**: Run `azd up`
4. ✅ **Verify**: Test both environments
5. ✅ **Monitor**: Compare metrics
6. ✅ **Scale**: Add more agents (Phase 3)

**You're ready to deploy with azd!** 🚀
