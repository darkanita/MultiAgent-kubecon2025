# 🚀 Your Next Steps: Deploy Phase 2 with AZD

You're ready to deploy the microservices architecture! Here are the **exact commands** to run.

---

## ✅ What You Have Now

- ✅ Phase 1 deployed: `kubeconagent` environment (monolithic)
- ✅ All azd configuration created
- ✅ Infrastructure templates ready
- ✅ Documentation complete

---

## 🎯 Deploy Phase 2 (3 Steps)

### Step 1: Create New AZD Environment

```bash
cd /c/Users/alopezmoreno/Downloads/Kubecon/MultiAgent-kubecon2025

# Create new environment
azd env new kubecon-micro

# You'll be prompted:
# ? Enter a new environment name: kubecon-micro
# 
# Select your Azure subscription (same as Phase 1)
# Select location: eastus (recommend same as Phase 1)
```

### Step 2: Optional - Share Resources from Phase 1

**Option A: Share ACR and OpenAI (Recommended - Saves ~$30/month)**

```bash
# Get Phase 1 resource names
ACR_NAME=$(az acr list --resource-group rg-kubeconagent --query "[0].name" -o tsv)
OPENAI_ID=$(az cognitiveservices account list --resource-group rg-kubeconagent --query "[0].id" -o tsv)
OPENAI_ENDPOINT=$(az cognitiveservices account list --resource-group rg-kubeconagent --query "[0].properties.endpoint" -o tsv)
OPENAI_KEY=$(az cognitiveservices account keys list --resource-group rg-kubeconagent --name $(az cognitiveservices account list --resource-group rg-kubeconagent --query "[0].name" -o tsv) --query "key1" -o tsv)

echo "ACR: $ACR_NAME"
echo "OpenAI ID: $OPENAI_ID"
echo "OpenAI Endpoint: $OPENAI_ENDPOINT"

# Set in new environment
azd env set SHARED_ACR_NAME $ACR_NAME
azd env set SHARED_OPENAI_ID $OPENAI_ID
azd env set AZURE_OPENAI_ENDPOINT $OPENAI_ENDPOINT
azd env set AZURE_OPENAI_API_KEY $OPENAI_KEY
```

**Option B: Create Everything New (Testing isolation - Higher cost)**

```bash
# Skip the sharing step - azd will create new ACR and OpenAI
# Good for complete isolation, costs ~$80-100/month
```

### Step 3: Provision Infrastructure

```bash
# This creates: AKS cluster, ACR (if not shared), networking, monitoring
azd provision --config azure.microservices.yaml
```

**Expected output:**
```
Provisioning Azure resources (azd provision)
Provisioning Azure resources can take some time

Subscription: [Your Subscription]
Location: eastus

  You can view detailed progress in the Azure Portal:
  [Azure Portal Link]

  (✓) Done: Resource group: rg-kubecon-micro
  (✓) Done: Log Analytics workspace: log-xxxxx
  (✓) Done: Application Insights: appi-xxxxx
  (✓) Done: Container registry: acrmaxxxxx (OR using shared: acrmakubeconagent5h4hjd6w)
  (✓) Done: AKS cluster: aks-xxxxx (8-10 minutes)
  (✓) Done: Role assignments

🔧 Configuring AKS cluster...
  ✅ AKS credentials retrieved
  ✅ Namespace created: multiagent-microservices
  ✅ ConfigMap created
  ✅ Secret created

SUCCESS: Your infrastructure was provisioned in Azure in 10 minutes 45 seconds.
You can view the resources created under the resource group rg-kubecon-micro in Azure Portal:
https://portal.azure.com/#@/resource/subscriptions/[...]/resourceGroups/rg-kubecon-micro
```

---

## ⏸️ STOP HERE - Infrastructure Ready!

**At this point you have:**
- ✅ New resource group: `rg-kubecon-micro`
- ✅ New AKS cluster running
- ✅ Namespace configured
- ✅ ConfigMap and secrets created
- ✅ RBAC permissions set

**But no services deployed yet** because you need to implement the service code first!

---

## 📝 Next: Implement Service Code

Before you can run `azd deploy`, you need to create the service code following **PHASE2_IMPLEMENTATION_PLAN.md**:

1. **Create service structure** (Step 1-3 in PHASE2_IMPLEMENTATION_PLAN.md)
   ```
   src/services/
   ├── coordinator/
   │   └── main.py
   ├── currency_agent/
   │   └── main.py
   └── activity_agent/
       └── main.py
   ```

2. **Create Dockerfiles** (Step 4-6)
   ```
   Dockerfile.coordinator
   Dockerfile.currency
   Dockerfile.activity
   ```

3. **Create K8s manifests** (Step 7)
   ```
   manifests/microservices/
   ├── coordinator/
   ├── currency-agent/
   └── activity-agent/
   ```

---

## 🚀 After Code Implementation: Deploy Services

Once you've implemented the service code (following PHASE2_IMPLEMENTATION_PLAN.md), deploy:

```bash
# Deploy all 3 microservices
azd deploy --config azure.microservices.yaml
```

This will:
1. ✅ Build 3 Docker images
2. ✅ Push to ACR
3. ✅ Deploy to AKS
4. ✅ Create LoadBalancer service
5. ✅ Wait for pods to be ready

---

## 🎯 Quick Command Summary

```bash
# 1. Create environment
azd env new kubecon-micro

# 2. Share resources (optional but recommended)
ACR_NAME=$(az acr list --resource-group rg-kubeconagent --query "[0].name" -o tsv)
OPENAI_ID=$(az cognitiveservices account list --resource-group rg-kubeconagent --query "[0].id" -o tsv)
azd env set SHARED_ACR_NAME $ACR_NAME
azd env set SHARED_OPENAI_ID $OPENAI_ID

# 3. Provision infrastructure
azd provision --config azure.microservices.yaml

# 4. Implement service code (see PHASE2_IMPLEMENTATION_PLAN.md)

# 5. Deploy services
azd deploy --config azure.microservices.yaml
```

---

## 📊 Verify Infrastructure

After `azd provision` completes, verify:

```bash
# Check environment
azd env get-values

# Expected output:
# AZURE_AKS_CLUSTER_NAME="aks-xxxxx"
# AZURE_CONTAINER_REGISTRY_ENDPOINT="acrmaxxxxx.azurecr.io"
# AZURE_OPENAI_ENDPOINT="https://oai-xxxxx.openai.azure.com/"
# CURRENCY_AGENT_URL="http://currency-agent:8001"
# ACTIVITY_AGENT_URL="http://activity-agent:8002"

# Check AKS cluster
kubectl get nodes

# Expected:
# NAME                                STATUS   ROLES   AGE   VERSION
# aks-agentpool-xxxxx                 Ready    agent   5m    v1.XX.XX

# Check namespace
kubectl get all -n multiagent-microservices

# Expected (before deployment):
# No resources found in multiagent-microservices namespace.
```

---

## 🔄 Compare with Phase 1

```bash
# Phase 1 environment
azd env select kubeconagent
azd env get-values

# Phase 2 environment
azd env select kubecon-micro
azd env get-values
```

Both should be running independently!

---

## 💰 Estimated Costs

**Phase 1 (Monolithic):**
- AKS (1 node): ~$50/month
- ACR Basic: ~$5/month
- OpenAI: Pay-per-use
- **Total: ~$60-80/month**

**Phase 2 (Microservices) with Shared Resources:**
- AKS (1 node, autoscale to 3): ~$50-150/month
- ACR: Shared ($0 extra)
- OpenAI: Shared ($0 extra)
- Monitoring: ~$5/month
- **Total: ~$55-155/month**

**Both Running: ~$115-235/month**

---

## 🆘 Troubleshooting

### Issue: `azd provision` fails

```bash
# Check subscription
az account show

# Check quota
az vm list-usage --location eastus --output table
```

### Issue: Can't find Phase 1 resources

```bash
# List all resource groups
az group list --output table

# If Phase 1 is in different RG, update commands:
az acr list --resource-group [YOUR_PHASE1_RG] --query "[0].name" -o tsv
```

### Issue: "No space left on device" during provision

```bash
# AKS needs at least 30GB disk per node
# Default Standard_B2s has 30GB - should be fine
# If issue persists, use Standard_B2ms (60GB)
```

---

## ✅ Success Criteria

After `azd provision`, you should have:

- [ ] New environment: `kubecon-micro` in `azd env list`
- [ ] New resource group: `rg-kubecon-micro` in Azure Portal
- [ ] AKS cluster running: `kubectl get nodes` shows 1 node
- [ ] Namespace created: `kubectl get ns multiagent-microservices`
- [ ] ConfigMap exists: `kubectl get cm -n multiagent-microservices`
- [ ] Secret exists: `kubectl get secret -n multiagent-microservices`
- [ ] Phase 1 still running: `kubectl get pods -n multiagent-kubecon-simple` works

---

## 📚 Documentation

- **[README_AZD_MICROSERVICES.md](./README_AZD_MICROSERVICES.md)**: Quick overview
- **[AZD_DEPLOYMENT_GUIDE.md](./AZD_DEPLOYMENT_GUIDE.md)**: Comprehensive guide
- **[PHASE2_IMPLEMENTATION_PLAN.md](./PHASE2_IMPLEMENTATION_PLAN.md)**: Service code implementation
- **[PHASE2_CHECKLIST.md](./PHASE2_CHECKLIST.md)**: Step-by-step checklist

---

## 🎉 Ready to Start!

Run the first command now:

```bash
azd env new kubecon-micro
```

Then follow the prompts. After that's done, run:

```bash
azd provision --config azure.microservices.yaml
```

Then you'll be ready to implement the service code! 🚀
