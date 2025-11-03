# Deploy Phase 2 Microservices to New Resource Group

## 🎯 Strategy: Parallel Deployments

Keep **Phase 1 (Monolithic)** running in existing resource group while deploying **Phase 2 (Microservices)** to a new resource group.

### **Current Setup (Phase 1)**
- Resource Group: `rg-makubeconagent` (or similar)
- AKS Cluster: `aks-5h4hjd6wjnu74`
- Deployment: Monolithic application
- Status: ✅ Running and stable

### **New Setup (Phase 2)**
- Resource Group: `rg-makubeconagent-microservices` (new)
- AKS Cluster: New cluster (or use existing with new namespace)
- Deployment: Microservices architecture
- Status: 🚧 To be deployed

---

## 📋 Option 1: New Resource Group + New AKS Cluster (Recommended)

### **Benefits**
- ✅ Complete isolation from Phase 1
- ✅ Can test without affecting production
- ✅ Easy to delete if something goes wrong
- ✅ No namespace conflicts

### **Cost**
- 💰 ~2x cost (two AKS clusters)
- 💰 Can delete after testing

---

## 📋 Option 2: Same AKS Cluster, New Namespace (Cost-Effective)

### **Benefits**
- ✅ Lower cost (one AKS cluster)
- ✅ Share node pool resources
- ✅ Faster deployment

### **Considerations**
- ⚠️ Shares resources with Phase 1
- ⚠️ Need to ensure resource quotas

---

## 🚀 Deployment Steps - Option 1 (New Resource Group)

### **Step 1: Set Environment Variables**

```bash
# New resource group and cluster names
export RG_NAME="rg-makubeconagent-microservices"
export LOCATION="eastus"  # or your preferred location
export AKS_CLUSTER_NAME="aks-multiagent-microservices"
export ACR_NAME="acrmakubeconagent5h4hjd6w"  # Reuse existing ACR
export OPENAI_NAME="oai-5h4hjd6wjnu74"  # Reuse existing OpenAI

# Azure subscription
export SUBSCRIPTION_ID=$(az account show --query id -o tsv)
```

### **Step 2: Create New Resource Group**

```bash
# Create resource group
az group create \
  --name ${RG_NAME} \
  --location ${LOCATION}

echo "✅ Resource group created: ${RG_NAME}"
```

### **Step 3: Create New AKS Cluster**

```bash
# Create AKS cluster for microservices
az aks create \
  --resource-group ${RG_NAME} \
  --name ${AKS_CLUSTER_NAME} \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --enable-managed-identity \
  --generate-ssh-keys \
  --attach-acr ${ACR_NAME}

echo "✅ AKS cluster created: ${AKS_CLUSTER_NAME}"
```

### **Step 4: Get AKS Credentials**

```bash
# Get credentials for new cluster
az aks get-credentials \
  --resource-group ${RG_NAME} \
  --name ${AKS_CLUSTER_NAME} \
  --overwrite-existing

# Verify connection
kubectl get nodes

# Expected output:
# NAME                                STATUS   ROLES   AGE   VERSION
# aks-nodepool1-xxxxx-vmss000000     Ready    agent   5m    v1.28.x
# aks-nodepool1-xxxxx-vmss000001     Ready    agent   5m    v1.28.x
```

### **Step 5: Create Namespace**

```bash
# Create namespace for microservices
kubectl create namespace multiagent-microservices

# Set as default namespace
kubectl config set-context --current --namespace=multiagent-microservices

echo "✅ Namespace created: multiagent-microservices"
```

### **Step 6: Create ConfigMap and Secrets**

```bash
# Get OpenAI endpoint
OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name ${OPENAI_NAME} \
  --resource-group rg-makubeconagent \
  --query properties.endpoint -o tsv)

# Get OpenAI API key
OPENAI_KEY=$(az cognitiveservices account keys list \
  --name ${OPENAI_NAME} \
  --resource-group rg-makubeconagent \
  --query key1 -o tsv)

# Create ConfigMap
kubectl create configmap app-config \
  --from-literal=AZURE_OPENAI_ENDPOINT=${OPENAI_ENDPOINT} \
  -n multiagent-microservices

# Create Secret
kubectl create secret generic openai-secret \
  --from-literal=AZURE_OPENAI_API_KEY=${OPENAI_KEY} \
  -n multiagent-microservices

echo "✅ ConfigMap and Secret created"
```

### **Step 7: Update Kubernetes Manifests**

Update manifests to use the correct ACR and namespace:

```bash
# Update manifests/microservices/*.yaml files
# Replace image names with your ACR
sed -i "s|acrmakubeconagent5h4hjd6w.azurecr.io|${ACR_NAME}.azurecr.io|g" manifests/microservices/*.yaml

echo "✅ Manifests updated"
```

### **Step 8: Build and Push Docker Images**

```bash
# Make sure you're in the project root
cd /path/to/MultiAgent-kubecon2025

# Login to ACR (reusing existing ACR)
az acr login --name ${ACR_NAME}

# Build Coordinator
docker build -f src/services/coordinator/Dockerfile \
  -t ${ACR_NAME}.azurecr.io/multiagent-kubecon-simple/coordinator:v2.0 .

# Build Currency Agent
docker build -f src/services/currency-agent/Dockerfile \
  -t ${ACR_NAME}.azurecr.io/multiagent-kubecon-simple/currency-agent:v2.0 .

# Build Activity Agent
docker build -f src/services/activity-agent/Dockerfile \
  -t ${ACR_NAME}.azurecr.io/multiagent-kubecon-simple/activity-agent:v2.0 .

# Push all images
docker push ${ACR_NAME}.azurecr.io/multiagent-kubecon-simple/coordinator:v2.0
docker push ${ACR_NAME}.azurecr.io/multiagent-kubecon-simple/currency-agent:v2.0
docker push ${ACR_NAME}.azurecr.io/multiagent-kubecon-simple/activity-agent:v2.0

echo "✅ All images built and pushed"
```

### **Step 9: Deploy Microservices**

```bash
# Deploy in order: agents first, then coordinator
kubectl apply -f manifests/microservices/currency-agent-deployment.yaml -n multiagent-microservices
kubectl apply -f manifests/microservices/activity-agent-deployment.yaml -n multiagent-microservices

# Wait for agents to be ready
kubectl wait --for=condition=ready pod -l app=currency-agent -n multiagent-microservices --timeout=120s
kubectl wait --for=condition=ready pod -l app=activity-agent -n multiagent-microservices --timeout=120s

# Deploy coordinator
kubectl apply -f manifests/microservices/coordinator-deployment.yaml -n multiagent-microservices

# Wait for coordinator
kubectl wait --for=condition=ready pod -l app=coordinator -n multiagent-microservices --timeout=120s

echo "✅ All services deployed"
```

### **Step 10: Verify Deployment**

```bash
# Check pods
kubectl get pods -n multiagent-microservices

# Expected:
# NAME                                   READY   STATUS    RESTARTS   AGE
# coordinator-service-xxxxx              1/1     Running   0          2m
# currency-agent-xxxxx                   1/1     Running   0          3m
# activity-agent-xxxxx                   1/1     Running   0          3m

# Check services
kubectl get svc -n multiagent-microservices

# Get external IP
EXTERNAL_IP=$(kubectl get svc coordinator-service -n multiagent-microservices -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "✅ Microservices deployed!"
echo "Access at: http://${EXTERNAL_IP}"
```

### **Step 11: Check Logs for MCP**

```bash
# Check coordinator logs for MCP connections
kubectl logs -f deployment/coordinator-service -n multiagent-microservices | grep MCP

# Expected:
# 🔌 [MCP] Connecting to currency-agent via HTTP: http://currency-agent:8001
# 🔌 [MCP] Connected to currency-agent MCP server
# 🔌 [MCP] Connecting to activity-agent via HTTP: http://activity-agent:8002
# 🔌 [MCP] Connected to activity-agent MCP server
# ✅ All MCP agents registered
```

### **Step 12: Test the System**

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc coordinator-service -n multiagent-microservices -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health
curl http://${EXTERNAL_IP}/health

# Test A2A discovery
curl http://${EXTERNAL_IP}/a2a/

# Test currency conversion
curl -X POST "http://${EXTERNAL_IP}/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Convert 500 USD to EUR and suggest activities in Paris",
    "session_id": "test-microservices"
  }'

echo "✅ System is working!"
```

---

## 🚀 Deployment Steps - Option 2 (Same Cluster, New Namespace)

### **Faster and Cost-Effective**

```bash
# Connect to existing cluster
az aks get-credentials \
  --resource-group rg-makubeconagent \
  --name aks-5h4hjd6wjnu74 \
  --overwrite-existing

# Create new namespace
kubectl create namespace multiagent-microservices

# Create ConfigMap and Secret (reuse from existing namespace or create new)
OPENAI_ENDPOINT=$(kubectl get configmap app-config -n multiagent-kubecon-simple -o jsonpath='{.data.AZURE_OPENAI_ENDPOINT}')
OPENAI_KEY=$(kubectl get secret openai-secret -n multiagent-kubecon-simple -o jsonpath='{.data.AZURE_OPENAI_API_KEY}' | base64 -d)

kubectl create configmap app-config \
  --from-literal=AZURE_OPENAI_ENDPOINT=${OPENAI_ENDPOINT} \
  -n multiagent-microservices

kubectl create secret generic openai-secret \
  --from-literal=AZURE_OPENAI_API_KEY=${OPENAI_KEY} \
  -n multiagent-microservices

# Deploy microservices
kubectl apply -f manifests/microservices/ -n multiagent-microservices

# Get new external IP
kubectl get svc coordinator-service -n multiagent-microservices
```

---

## 📊 Comparison: Both Deployments Running

```
┌─────────────────────────────────────────────────────────┐
│         Azure Subscription                              │
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │ RG: makubeconagent   │  │ RG: makubeconagent-  │   │
│  │                      │  │     microservices    │   │
│  │ ┌─────────────────┐  │  │ ┌─────────────────┐  │   │
│  │ │ AKS Phase 1     │  │  │ │ AKS Phase 2     │  │   │
│  │ │                 │  │  │ │                 │  │   │
│  │ │ • Monolithic    │  │  │ │ • Coordinator   │  │   │
│  │ │   (1 pod)       │  │  │ │ • Currency Agt  │  │   │
│  │ │                 │  │  │ │ • Activity Agt  │  │   │
│  │ │ External IP:    │  │  │ │                 │  │   │
│  │ │ 172.168.108.4   │  │  │ │ External IP:    │  │   │
│  │ │                 │  │  │ │ [NEW-IP]        │  │   │
│  │ └─────────────────┘  │  │ └─────────────────┘  │   │
│  └──────────────────────┘  └──────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Shared Resources:                                │  │
│  │ • ACR: acrmakubeconagent5h4hjd6w                │  │
│  │ • Azure OpenAI: oai-5h4hjd6wjnu74               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Switching Between Deployments

```bash
# List all contexts
kubectl config get-contexts

# Switch to Phase 1 (Monolithic)
kubectl config use-context aks-5h4hjd6wjnu74
kubectl config set-context --current --namespace=multiagent-kubecon-simple

# Switch to Phase 2 (Microservices)
kubectl config use-context aks-multiagent-microservices  # If new cluster
kubectl config set-context --current --namespace=multiagent-microservices

# Or if same cluster:
kubectl config set-context --current --namespace=multiagent-microservices
```

---

## 💰 Cost Considerations

### **Option 1: New Resource Group + New AKS**
```
Monthly Cost Estimate:
- AKS Control Plane: Free (for single cluster)
- Worker Nodes (2x Standard_D2s_v3): ~$140/month
- Load Balancer: ~$20/month
- Storage: ~$10/month
────────────────────────────────────────
Total Additional: ~$170/month

Good for: Production, long-term testing
```

### **Option 2: Same Cluster, New Namespace**
```
Monthly Cost Estimate:
- Additional pods on existing nodes: ~$0 (if capacity available)
- Additional Load Balancer: ~$20/month
────────────────────────────────────────
Total Additional: ~$20/month

Good for: Testing, cost-conscious development
```

---

## 🧹 Cleanup (When Done Testing)

### **Delete New Resource Group (Option 1)**
```bash
# Delete entire resource group (including AKS)
az group delete --name rg-makubeconagent-microservices --yes --no-wait

echo "✅ Phase 2 resources deleted, Phase 1 still running"
```

### **Delete Namespace Only (Option 2)**
```bash
# Delete just the namespace
kubectl delete namespace multiagent-microservices

echo "✅ Phase 2 deleted, Phase 1 still running on same cluster"
```

---

## ✅ Validation Checklist

After deployment, verify:

- [ ] New resource group exists (Option 1) or namespace exists (Option 2)
- [ ] AKS cluster is running
- [ ] 3 pods are running (coordinator, currency-agent, activity-agent)
- [ ] All pods show `1/1 Ready`
- [ ] External IP is assigned to coordinator service
- [ ] Health endpoint responds: `curl http://<external-ip>/health`
- [ ] A2A endpoint works: `curl http://<external-ip>/a2a/`
- [ ] MCP logs visible in coordinator
- [ ] Currency conversion works end-to-end
- [ ] Phase 1 (monolithic) still accessible at old IP

---

## 🎯 Recommended Approach

**For KubeCon Demo/Testing**: Use **Option 1** (New Resource Group)
- Complete isolation
- Can demo both side-by-side
- Easy to delete after demo

**For Development**: Use **Option 2** (Same Cluster)
- Lower cost
- Faster iteration
- Share resources

---

## 📝 Quick Start Script

I can create a complete automation script for you. Would you like me to create:

1. `scripts/deploy-phase2-new-rg.sh` - Automated deployment to new resource group
2. `scripts/deploy-phase2-same-cluster.sh` - Automated deployment to same cluster

Just let me know which option you prefer!

---

**Next Steps**: Choose Option 1 or Option 2, and I'll help you execute the deployment! 🚀
