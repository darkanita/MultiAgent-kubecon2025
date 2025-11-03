# Quick Reference: Dual Environment Setup

## 🎯 Two Parallel Environments

```
┌─────────────────────────────────────────────────────┐
│         Your Azure Subscription                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Environment 1: MONOLITHIC (Phase 1) ✅             │
│  ─────────────────────────────────────             │
│  RG: rg-multiagent-kubecon-simple                  │
│  AKS: aks-XXXXX                                    │
│  Namespace: multiagent-kubecon-simple              │
│  IP: 172.168.108.4                                 │
│  Pods: 1 (all-in-one)                              │
│  Status: PRODUCTION                                │
│                                                     │
│  Environment 2: MICROSERVICES (Phase 2) 🚧          │
│  ──────────────────────────────────────            │
│  RG: rg-multiagent-microservices                   │
│  AKS: aks-multiagent-micro                         │
│  Namespace: multiagent-microservices               │
│  IP: [TO BE ASSIGNED]                              │
│  Pods: 3+ (coordinator + agents)                   │
│  Status: TESTING                                   │
│                                                     │
│  Shared Resources:                                 │
│  ─────────────────                                 │
│  ACR: acrmakubeconagent5h4hjd6w (shared)          │
│  OpenAI: oai-5h4hjd6wjnu74 (shared)               │
└─────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Commands

### Switch Between Environments

```bash
# Switch to Phase 1 (Monolithic)
kubectl config use-context [phase1-aks-context]
kubectl config set-context --current --namespace=multiagent-kubecon-simple

# Switch to Phase 2 (Microservices)
kubectl config use-context [phase2-aks-context]
kubectl config set-context --current --namespace=multiagent-microservices
```

### View Both Environments

```bash
# Phase 1 status
kubectl get pods -n multiagent-kubecon-simple --context=[phase1-context]

# Phase 2 status
kubectl get pods -n multiagent-microservices --context=[phase2-context]
```

### Get External IPs

```bash
# Phase 1 IP
kubectl get svc multiagent-service -n multiagent-kubecon-simple -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Phase 2 IP
kubectl get svc coordinator-service -n multiagent-microservices -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

---

## 📝 Setup Script

Save as `setup-new-environment.sh`:

```bash
#!/bin/bash
set -e

# Configuration
CURRENT_RG="rg-multiagent-kubecon-simple"  # Your Phase 1 RG
NEW_RG="rg-multiagent-microservices"
LOCATION="eastus"
AKS_NAME="aks-multiagent-micro"

echo "🚀 Setting up new microservices environment..."

# Step 1: Get existing resources
echo "📋 Getting existing resources..."
ACR_NAME=$(az acr list --resource-group $CURRENT_RG --query "[0].name" -o tsv)
OPENAI_ID=$(az cognitiveservices account list --resource-group $CURRENT_RG --query "[0].id" -o tsv)
OPENAI_ENDPOINT=$(az cognitiveservices account list --resource-group $CURRENT_RG --query "[0].properties.endpoint" -o tsv)
OPENAI_KEY=$(az cognitiveservices account keys list --resource-group $CURRENT_RG --name $(az cognitiveservices account list --resource-group $CURRENT_RG --query "[0].name" -o tsv) --query "key1" -o tsv)

echo "  ACR: $ACR_NAME"
echo "  OpenAI: $OPENAI_ENDPOINT"

# Step 2: Create new resource group
echo "🏗️  Creating new resource group..."
az group create --name $NEW_RG --location $LOCATION --tags "Environment=Microservices" "Phase=2"

# Step 3: Create AKS cluster
echo "☸️  Creating AKS cluster (this takes 5-10 minutes)..."
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

# Step 4: Get credentials
echo "🔑 Getting AKS credentials..."
az aks get-credentials --resource-group $NEW_RG --name $AKS_NAME --overwrite-existing

# Step 5: Create namespace
echo "📦 Creating namespace..."
kubectl create namespace multiagent-microservices

# Step 6: Attach ACR
echo "🐳 Attaching ACR to AKS..."
az aks update --resource-group $NEW_RG --name $AKS_NAME --attach-acr $ACR_NAME

# Step 7: Grant OpenAI access
echo "🤖 Granting OpenAI access..."
KUBELET_IDENTITY=$(az aks show --resource-group $NEW_RG --name $AKS_NAME --query identityProfile.kubeletidentity.clientId -o tsv)
az role assignment create \
  --assignee $KUBELET_IDENTITY \
  --role "Cognitive Services OpenAI User" \
  --scope $OPENAI_ID

# Step 8: Create ConfigMap
echo "⚙️  Creating ConfigMap..."
kubectl create configmap app-config \
  --from-literal=AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT \
  --namespace=multiagent-microservices

# Step 9: Create Secret
echo "🔐 Creating Secret..."
kubectl create secret generic openai-secret \
  --from-literal=AZURE_OPENAI_API_KEY=$OPENAI_KEY \
  --namespace=multiagent-microservices

# Step 10: Summary
echo ""
echo "✅ New environment setup complete!"
echo ""
echo "📊 Environment Details:"
echo "  Resource Group: $NEW_RG"
echo "  AKS Cluster: $AKS_NAME"
echo "  Namespace: multiagent-microservices"
echo "  Shared ACR: $ACR_NAME"
echo "  Shared OpenAI: $OPENAI_ENDPOINT"
echo ""
echo "🎯 Next Steps:"
echo "  1. Build microservices Docker images"
echo "  2. Push images to ACR: az acr login --name $ACR_NAME"
echo "  3. Deploy manifests: kubectl apply -f manifests/microservices/"
echo "  4. Get external IP: kubectl get svc coordinator-service -n multiagent-microservices"
echo ""
echo "📖 Full guide: docs/NEW_ENVIRONMENT_SETUP.md"
```

Make it executable:
```bash
chmod +x setup-new-environment.sh
```

Run it:
```bash
./setup-new-environment.sh
```

---

## 🧪 Testing Both Environments

```bash
# Test Phase 1 (Monolithic)
PHASE1_IP="172.168.108.4"
curl http://${PHASE1_IP}/health
curl http://${PHASE1_IP}/a2a/

# Test Phase 2 (Microservices) - after deployment
PHASE2_IP=$(kubectl get svc coordinator-service -n multiagent-microservices -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://${PHASE2_IP}/health
curl http://${PHASE2_IP}/a2a/
```

---

## 💰 Cost Management

### View Costs by Environment

```bash
# Phase 1 costs
az consumption usage list --resource-group rg-multiagent-kubecon-simple

# Phase 2 costs
az consumption usage list --resource-group rg-multiagent-microservices

# Total
az consumption usage list | grep multiagent
```

### Shutdown Phase 2 (Save Costs)

```bash
# Stop Phase 2 AKS (keeps everything but stops compute)
az aks stop --resource-group rg-multiagent-microservices --name aks-multiagent-micro

# Start again when needed
az aks start --resource-group rg-multiagent-microservices --name aks-multiagent-micro
```

---

## 🔄 Migration Path

### Safe Migration Strategy

```
Week 1: Setup
├─ Day 1-2: Create new environment
├─ Day 3-5: Deploy microservices
└─ Day 6-7: Test thoroughly

Week 2: Validation
├─ Day 1-3: Load testing
├─ Day 4-5: Compare metrics
└─ Day 6-7: Fix issues

Week 3: Cutover
├─ Day 1: 10% traffic to Phase 2
├─ Day 2: 50% traffic split
├─ Day 3: 100% to Phase 2
└─ Day 4-7: Monitor

Week 4: Cleanup
└─ Delete Phase 1 resources
```

---

## 📊 Comparison Dashboard

| Metric | Phase 1 (Mono) | Phase 2 (Micro) |
|--------|---------------|-----------------|
| **Pods** | 1 | 3+ |
| **Scalability** | Limited | Per-service |
| **Deployment** | All-or-nothing | Independent |
| **Protocols** | Internal | MCP active |
| **Cost** | $X/month | $1.3X/month |
| **Downtime Risk** | High | Low |

---

## 🆘 Troubleshooting

### Issue: Can't switch contexts

```bash
# List all contexts
kubectl config get-contexts

# Rename for clarity
kubectl config rename-context [old-name] phase1-mono
kubectl config rename-context [old-name] phase2-micro
```

### Issue: ACR access denied

```bash
# Re-attach ACR
az aks update \
  --resource-group rg-multiagent-microservices \
  --name aks-multiagent-micro \
  --attach-acr acrmakubeconagent5h4hjd6w
```

### Issue: OpenAI access denied

```bash
# Check role assignment
az role assignment list --assignee [KUBELET_IDENTITY] --scope [OPENAI_ID]

# Re-assign if needed
az role assignment create \
  --assignee [KUBELET_IDENTITY] \
  --role "Cognitive Services OpenAI User" \
  --scope [OPENAI_ID]
```

---

## ✅ Final Checklist

**Environment Setup**:
- [ ] New resource group created
- [ ] New AKS cluster running
- [ ] kubectl can connect to new AKS
- [ ] Namespace `multiagent-microservices` created
- [ ] ACR attached to new AKS
- [ ] OpenAI access granted
- [ ] ConfigMap created
- [ ] Secret created

**Deployment Ready**:
- [ ] Service code created (see PHASE2_IMPLEMENTATION_PLAN.md)
- [ ] Docker images built
- [ ] Images pushed to ACR
- [ ] Manifests created in `manifests/microservices/`

**Validation**:
- [ ] Both environments accessible
- [ ] Can switch between contexts
- [ ] Both have different external IPs
- [ ] Phase 1 still working (no disruption)

---

**You're ready to deploy microservices!** 🚀

**Next**: Follow `PHASE2_CHECKLIST.md` to deploy the microservices architecture.
