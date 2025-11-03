# Phase 2: Creating New Azure Environment for Microservices

## 🎯 Goal

Create a **separate Azure environment** for Phase 2 (microservices) while keeping Phase 1 (monolithic) running.

---

## 🏗️ Deployment Strategy

### **Blue-Green Deployment**

```
┌────────────────────────────────────────────────────────────┐
│                    Azure Subscription                      │
│                                                            │
│  ┌──────────────────────────┐  ┌──────────────────────┐  │
│  │  BLUE (Phase 1)          │  │  GREEN (Phase 2)     │  │
│  │  Monolithic              │  │  Microservices       │  │
│  │  ─────────────           │  │  ────────────        │  │
│  │                          │  │                      │  │
│  │  rg-multiagent-mono      │  │  rg-multiagent-micro │  │
│  │                          │  │                      │  │
│  │  • AKS (1 node)          │  │  • AKS (1-3 nodes)   │  │
│  │  • ACR (shared)          │  │  • ACR (same/new)    │  │
│  │  • OpenAI (shared)       │  │  • OpenAI (same/new) │  │
│  │  • 1 Pod                 │  │  • 3+ Pods           │  │
│  │                          │  │                      │  │
│  │  IP: 172.168.108.4       │  │  IP: [NEW-IP]        │  │
│  │  Status: PRODUCTION ✅   │  │  Status: TESTING 🧪  │  │
│  └──────────────────────────┘  └──────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

**Benefits**:
- ✅ Zero downtime - monolithic stays running
- ✅ Safe testing - new environment isolated
- ✅ Easy rollback - just delete new resource group
- ✅ Cost control - know exact microservices cost

---

## 📋 Options for New Environment

### **Option 1: Completely Separate (Recommended for Testing)**

**What's created**:
- New Resource Group
- New AKS cluster
- New ACR (or reuse existing)
- New Azure OpenAI (or reuse existing)
- New Virtual Network
- New Log Analytics

**Pros**:
- ✅ Complete isolation
- ✅ Can test without affecting production
- ✅ Easy to delete everything when done
- ✅ Clear cost separation

**Cons**:
- ❌ Higher cost (duplicate resources)
- ❌ Need to configure everything again

**Cost Estimate**: ~2x Phase 1 cost

---

### **Option 2: Shared Resources (Recommended for Production)**

**What's created**:
- New Resource Group
- New AKS cluster
- **Reuse** existing ACR
- **Reuse** existing Azure OpenAI
- New Virtual Network (can peer with existing)
- **Reuse** Log Analytics

**Pros**:
- ✅ Lower cost (share expensive resources)
- ✅ Same OpenAI model, consistent responses
- ✅ Same container registry
- ✅ Still isolated AKS for testing

**Cons**:
- ❌ Some shared dependencies
- ❌ ACR might need capacity increase

**Cost Estimate**: ~1.3x Phase 1 cost

---

## 🚀 Implementation: Option 2 (Shared Resources)

Let's use **Option 2** as it's the most practical for real-world scenarios.

---

## **Step 1: Get Existing Resource Information**

### 1.1 Find Current Resources

```bash
# List all resource groups
az group list --query "[].{Name:name, Location:location}" -o table

# Get current resource group name (your Phase 1)
CURRENT_RG="rg-multiagent-kubecon-simple"  # Replace with actual name

# List resources in current group
az resource list --resource-group $CURRENT_RG --query "[].{Name:name, Type:type}" -o table
```

### 1.2 Get Shared Resource IDs

```bash
# Get ACR name
ACR_NAME=$(az acr list --resource-group $CURRENT_RG --query "[0].name" -o tsv)
echo "ACR Name: $ACR_NAME"

# Get OpenAI endpoint
OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --resource-group $CURRENT_RG \
  --name $(az cognitiveservices account list --resource-group $CURRENT_RG --query "[0].name" -o tsv) \
  --query "properties.endpoint" -o tsv)
echo "OpenAI Endpoint: $OPENAI_ENDPOINT"

# Get OpenAI resource ID (for RBAC)
OPENAI_ID=$(az cognitiveservices account list --resource-group $CURRENT_RG --query "[0].id" -o tsv)
echo "OpenAI ID: $OPENAI_ID"
```

---

## **Step 2: Create New Resource Group**

```bash
# Set variables
LOCATION="eastus"  # Or your preferred region
NEW_RG="rg-multiagent-microservices"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create resource group
az group create \
  --name $NEW_RG \
  --location $LOCATION \
  --tags "Environment=Microservices" "Phase=2" "Project=KubeCon2025"

echo "✅ Resource Group created: $NEW_RG"
```

---

## **Step 3: Create New AKS Cluster**

### 3.1 Create AKS with Managed Identity

```bash
# Set cluster name
AKS_NAME="aks-multiagent-micro"

# Create AKS cluster
az aks create \
  --resource-group $NEW_RG \
  --name $AKS_NAME \
  --node-count 1 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys \
  --network-plugin azure \
  --enable-addons monitoring \
  --tags "Environment=Microservices" "Phase=2"

echo "✅ AKS Cluster created: $AKS_NAME"
echo "⏳ This takes 5-10 minutes..."
```

### 3.2 Get AKS Credentials

```bash
# Get credentials
az aks get-credentials \
  --resource-group $NEW_RG \
  --name $AKS_NAME \
  --overwrite-existing

# Verify connection
kubectl config current-context
kubectl get nodes

# Create namespace
kubectl create namespace multiagent-microservices

echo "✅ AKS connected and namespace created"
```

---

## **Step 4: Connect to Existing ACR**

### 4.1 Attach ACR to New AKS

```bash
# Attach existing ACR to new AKS
az aks update \
  --resource-group $NEW_RG \
  --name $AKS_NAME \
  --attach-acr $ACR_NAME

echo "✅ ACR attached to new AKS cluster"
```

### 4.2 Verify ACR Access

```bash
# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Test pull access from AKS
kubectl run test-acr \
  --image=$ACR_LOGIN_SERVER/multiagent-kubecon-simple/app-kubeconagent:mcp-logging \
  --restart=Never \
  -n multiagent-microservices

# Check if pod can pull image
kubectl get pod test-acr -n multiagent-microservices

# Clean up test
kubectl delete pod test-acr -n multiagent-microservices

echo "✅ ACR access verified"
```

---

## **Step 5: Configure Azure OpenAI Access**

### 5.1 Get AKS Managed Identity

```bash
# Get AKS kubelet managed identity
KUBELET_IDENTITY=$(az aks show \
  --resource-group $NEW_RG \
  --name $AKS_NAME \
  --query identityProfile.kubeletidentity.clientId -o tsv)

echo "AKS Managed Identity: $KUBELET_IDENTITY"
```

### 5.2 Grant OpenAI Access

```bash
# Assign "Cognitive Services OpenAI User" role to AKS identity
az role assignment create \
  --assignee $KUBELET_IDENTITY \
  --role "Cognitive Services OpenAI User" \
  --scope $OPENAI_ID

echo "✅ OpenAI access granted to new AKS cluster"
```

---

## **Step 6: Create ConfigMap and Secrets**

### 6.1 Get OpenAI Details

```bash
# Get OpenAI deployment name (model)
OPENAI_DEPLOYMENT="gpt-4o-mini"  # Or your actual deployment name

# Get OpenAI API key (if needed for local testing)
OPENAI_KEY=$(az cognitiveservices account keys list \
  --resource-group $CURRENT_RG \
  --name $(az cognitiveservices account list --resource-group $CURRENT_RG --query "[0].name" -o tsv) \
  --query "key1" -o tsv)
```

### 6.2 Create ConfigMap

```bash
# Create ConfigMap
kubectl create configmap app-config \
  --from-literal=AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT \
  --namespace=multiagent-microservices

echo "✅ ConfigMap created"
```

### 6.3 Create Secret

```bash
# Create Secret (for API key - optional if using Managed Identity)
kubectl create secret generic openai-secret \
  --from-literal=AZURE_OPENAI_API_KEY=$OPENAI_KEY \
  --namespace=multiagent-microservices

echo "✅ Secret created"
```

---

## **Step 7: Prepare Manifests for New Environment**

### 7.1 Create Microservices Manifest Directory

```bash
# Create directory for microservices manifests
mkdir -p manifests/microservices

# Copy base manifests as templates
cp manifests/deployment.yaml manifests/microservices/coordinator-deployment.yaml.template
```

### 7.2 Update Image References

All manifests should reference your existing ACR:

```yaml
# coordinator-deployment.yaml
image: acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/coordinator:latest

# currency-agent-deployment.yaml
image: acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/currency-agent:latest

# activity-agent-deployment.yaml
image: acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/activity-agent:latest
```

---

## **Step 8: Build and Push Microservices Images**

### 8.1 Prepare Source Code

Follow the Phase 2 implementation plan to create the service files:

```bash
# Create service directories
mkdir -p src/services/coordinator
mkdir -p src/services/currency-agent
mkdir -p src/services/activity-agent

# Create service files (see PHASE2_IMPLEMENTATION_PLAN.md)
# - coordinator/main.py
# - coordinator/Dockerfile
# - currency-agent/main.py
# - currency-agent/http_wrapper.py
# - currency-agent/Dockerfile
# - activity-agent/main.py
# - activity-agent/http_wrapper.py
# - activity-agent/Dockerfile
```

### 8.2 Build Images

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build coordinator
docker build -f src/services/coordinator/Dockerfile \
  -t $ACR_LOGIN_SERVER/multiagent-kubecon-simple/coordinator:latest .

# Build currency agent
docker build -f src/services/currency-agent/Dockerfile \
  -t $ACR_LOGIN_SERVER/multiagent-kubecon-simple/currency-agent:latest .

# Build activity agent
docker build -f src/services/activity-agent/Dockerfile \
  -t $ACR_LOGIN_SERVER/multiagent-kubecon-simple/activity-agent:latest .
```

### 8.3 Push Images

```bash
# Push all images
docker push $ACR_LOGIN_SERVER/multiagent-kubecon-simple/coordinator:latest
docker push $ACR_LOGIN_SERVER/multiagent-kubecon-simple/currency-agent:latest
docker push $ACR_LOGIN_SERVER/multiagent-kubecon-simple/activity-agent:latest

echo "✅ All images pushed to ACR"
```

---

## **Step 9: Deploy Microservices**

### 9.1 Deploy in Order

```bash
# Deploy Currency Agent first
kubectl apply -f manifests/microservices/currency-agent-deployment.yaml -n multiagent-microservices

# Wait for currency agent to be ready
kubectl wait --for=condition=ready pod -l app=currency-agent -n multiagent-microservices --timeout=120s

# Deploy Activity Agent
kubectl apply -f manifests/microservices/activity-agent-deployment.yaml -n multiagent-microservices

# Wait for activity agent to be ready
kubectl wait --for=condition=ready pod -l app=activity-agent -n multiagent-microservices --timeout=120s

# Deploy Coordinator (depends on agents)
kubectl apply -f manifests/microservices/coordinator-deployment.yaml -n multiagent-microservices

# Wait for coordinator to be ready
kubectl wait --for=condition=ready pod -l app=coordinator -n multiagent-microservices --timeout=120s

echo "✅ All services deployed"
```

### 9.2 Verify Deployment

```bash
# Check all pods
kubectl get pods -n multiagent-microservices

# Expected output:
# NAME                                READY   STATUS    RESTARTS   AGE
# coordinator-xxxxx                   1/1     Running   0          2m
# currency-agent-xxxxx                1/1     Running   0          3m
# activity-agent-xxxxx                1/1     Running   0          3m

# Check services
kubectl get svc -n multiagent-microservices

# Get external IP
kubectl get svc coordinator-service -n multiagent-microservices -w
```

---

## **Step 10: Test New Environment**

### 10.1 Get New External IP

```bash
# Get new microservices external IP
NEW_EXTERNAL_IP=$(kubectl get svc coordinator-service -n multiagent-microservices -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "🎉 New Microservices Endpoint: http://${NEW_EXTERNAL_IP}"
```

### 10.2 Test Endpoints

```bash
# Test health
curl http://${NEW_EXTERNAL_IP}/health

# Test A2A discovery
curl http://${NEW_EXTERNAL_IP}/a2a/

# Test chat API
curl -X POST "http://${NEW_EXTERNAL_IP}/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Convert 100 USD to EUR",
    "session_id": "test-microservices"
  }'
```

### 10.3 Check MCP Logs

```bash
# Watch coordinator logs for MCP activity
kubectl logs -f deployment/coordinator-service -n multiagent-microservices | grep -E "MCP|A2A"

# Expected:
# 🔌 [MCP] Connected to currency-agent
# 🔌 [MCP] Connected to activity-agent
# 🚀 [MCP] Calling tool 'convert_amount'
# ✅ [MCP] Tool executed successfully
```

---

## **Step 11: Compare Both Environments**

### 11.1 Side-by-Side Status

```bash
echo "=== PHASE 1 (Monolithic) ==="
kubectl config use-context [your-phase1-context]
kubectl get pods -n multiagent-kubecon-simple
kubectl get svc multiagent-service -n multiagent-kubecon-simple

echo ""
echo "=== PHASE 2 (Microservices) ==="
kubectl config use-context [your-phase2-context]
kubectl get pods -n multiagent-microservices
kubectl get svc coordinator-service -n multiagent-microservices
```

### 11.2 Cost Comparison

```bash
# Get Phase 1 resource costs
az consumption usage list \
  --start-date $(date -d '7 days ago' +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  | jq -r '.[] | select(.instanceName | contains("'$CURRENT_RG'")) | [.instanceName, .pretaxCost, .currency] | @tsv'

# Get Phase 2 resource costs  
az consumption usage list \
  --start-date $(date -d '7 days ago' +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  | jq -r '.[] | select(.instanceName | contains("'$NEW_RG'")) | [.instanceName, .pretaxCost, .currency] | @tsv'
```

---

## **Step 12: DNS and Traffic Management (Optional)**

### 12.1 Option A: Keep Both IPs

```
Phase 1 (Monolithic): http://172.168.108.4
Phase 2 (Microservices): http://[NEW-IP]

Users/Clients choose which to use
```

### 12.2 Option B: Use Azure Front Door

```bash
# Create Front Door for A/B testing or gradual rollout
az network front-door create \
  --resource-group $NEW_RG \
  --name fd-multiagent \
  --backend-address $NEW_EXTERNAL_IP

# Can route traffic:
# - 100% to Phase 1 (safe)
# - 50/50 split (gradual rollout)
# - 100% to Phase 2 (full cutover)
```

---

## **Step 13: Monitoring and Observability**

### 13.1 Enable Container Insights

```bash
# Enable monitoring on new AKS
az aks enable-addons \
  --resource-group $NEW_RG \
  --name $AKS_NAME \
  --addons monitoring
```

### 13.2 View Logs in Azure Portal

```
1. Go to Azure Portal
2. Navigate to new AKS cluster
3. Select "Logs" in left menu
4. Query:
   ContainerLog
   | where Namespace == "multiagent-microservices"
   | where LogEntry contains "MCP" or LogEntry contains "A2A"
   | project TimeGenerated, LogEntry
   | order by TimeGenerated desc
```

---

## **Step 14: Cleanup Strategy**

### 14.1 If Phase 2 Successful - Delete Phase 1

```bash
# After thorough testing, if Phase 2 is working perfectly:

# Delete Phase 1 resource group (CAREFUL!)
az group delete --name $CURRENT_RG --yes --no-wait

# This removes:
# - Old AKS cluster
# - Old deployments
# - Old Virtual Network
# (Keeps shared ACR and OpenAI if in different RG)
```

### 14.2 If Phase 2 Fails - Delete Phase 2

```bash
# If Phase 2 has issues, easy rollback:

# Delete Phase 2 resource group
az group delete --name $NEW_RG --yes --no-wait

# Phase 1 continues running unaffected
```

---

## 📊 Resource Comparison

| Resource | Phase 1 (Mono) | Phase 2 (Micro) | Shared? |
|----------|----------------|-----------------|---------|
| **Resource Group** | rg-multiagent-mono | rg-multiagent-micro | ❌ |
| **AKS Cluster** | aks-5h4hjd6w | aks-multiagent-micro | ❌ |
| **Node Count** | 1 | 1-3 | ❌ |
| **Pods** | 1 | 3+ | ❌ |
| **ACR** | acr... | (reuse) | ✅ |
| **Azure OpenAI** | oai-... | (reuse) | ✅ |
| **VNet** | vnet-mono | vnet-micro | ❌ |
| **Namespace** | multiagent-kubecon-simple | multiagent-microservices | ❌ |
| **External IP** | 172.168.108.4 | [NEW-IP] | ❌ |

---

## ✅ Final Checklist

- [ ] New resource group created
- [ ] New AKS cluster created and connected
- [ ] Existing ACR attached to new AKS
- [ ] Existing OpenAI access granted
- [ ] ConfigMap and Secrets created in new namespace
- [ ] Microservices source code ready
- [ ] Docker images built and pushed
- [ ] All 3 services deployed (coordinator, currency, activity)
- [ ] All pods showing 1/1 Ready
- [ ] External IP assigned to coordinator service
- [ ] Health endpoint responding
- [ ] A2A endpoint responding
- [ ] Chat API working
- [ ] MCP logs showing in coordinator
- [ ] Both environments working independently

---

## 🎯 Summary Commands

```bash
# Quick deployment script
# Save this as: deploy-microservices-env.sh

#!/bin/bash
set -e

# Variables
CURRENT_RG="rg-multiagent-kubecon-simple"
NEW_RG="rg-multiagent-microservices"
LOCATION="eastus"
AKS_NAME="aks-multiagent-micro"

# Get existing resources
ACR_NAME=$(az acr list --resource-group $CURRENT_RG --query "[0].name" -o tsv)
OPENAI_ID=$(az cognitiveservices account list --resource-group $CURRENT_RG --query "[0].id" -o tsv)
OPENAI_ENDPOINT=$(az cognitiveservices account list --resource-group $CURRENT_RG --query "[0].properties.endpoint" -o tsv)

# Create new RG
az group create --name $NEW_RG --location $LOCATION

# Create AKS
az aks create \
  --resource-group $NEW_RG \
  --name $AKS_NAME \
  --node-count 1 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group $NEW_RG --name $AKS_NAME --overwrite-existing

# Create namespace
kubectl create namespace multiagent-microservices

# Attach ACR
az aks update --resource-group $NEW_RG --name $AKS_NAME --attach-acr $ACR_NAME

# Grant OpenAI access
KUBELET_IDENTITY=$(az aks show --resource-group $NEW_RG --name $AKS_NAME --query identityProfile.kubeletidentity.clientId -o tsv)
az role assignment create --assignee $KUBELET_IDENTITY --role "Cognitive Services OpenAI User" --scope $OPENAI_ID

# Create ConfigMap
kubectl create configmap app-config \
  --from-literal=AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT \
  --namespace=multiagent-microservices

echo "✅ Environment ready for microservices deployment!"
echo "Next: Build and push Docker images, then deploy manifests"
```

---

**Your new microservices environment is ready!** 🚀

**Next Steps**:
1. Follow `PHASE2_IMPLEMENTATION_PLAN.md` to create service code
2. Build and push Docker images
3. Deploy microservices to new environment
4. Test thoroughly
5. When confident, migrate traffic or keep both running

**Current Status**:
- ✅ Phase 1 (Monolithic): PRODUCTION at 172.168.108.4
- 🚧 Phase 2 (Microservices): TESTING at [NEW-IP]
