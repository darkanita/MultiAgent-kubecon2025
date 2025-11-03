# Phase 2: Microservices Deployment with AZD

## 🎯 Quick Start

You're ready to deploy Phase 2 (microservices) using Azure Developer CLI while keeping Phase 1 (monolithic) running!

### Current Status
- ✅ Phase 1 deployed: Environment `kubeconagent` (monolithic)
- 🚧 Phase 2 ready to deploy: New environment (microservices)

---

## 📋 What Changed for AZD

### New Files Created

1. **`azure.microservices.yaml`**
   - New azd configuration for microservices
   - Defines 3 services: coordinator, currency-agent, activity-agent
   - Includes hooks for automatic setup

2. **`infra/main.microservices.bicep`**
   - Microservices-specific infrastructure template
   - Supports sharing ACR and OpenAI from Phase 1
   - Creates new AKS cluster optimized for microservices

3. **`infra/modules/microservices-aks.bicep`**
   - Module for AKS with autoscaling
   - Conditional resource creation (shared vs new)
   - Monitoring integration

4. **`docs/AZD_DEPLOYMENT_GUIDE.md`**
   - Complete azd-specific deployment guide
   - Commands for managing both environments
   - Troubleshooting and testing procedures

---

## 🚀 Deploy Now (3 Commands)

```bash
# 1. Create new azd environment
azd env new kubecon-micro

# 2. Provision infrastructure (creates AKS, ACR, etc.)
azd provision --config azure.microservices.yaml

# 3. Deploy services (builds and deploys 3 microservices)
azd deploy --config azure.microservices.yaml
```

**That's it!** Your microservices are deployed.

---

## 🔄 Two Environments in Parallel

```
Phase 1 (Monolithic) ✅              Phase 2 (Microservices) 🚀
├─ Environment: kubeconagent         ├─ Environment: kubecon-micro
├─ Config: azure.yaml                ├─ Config: azure.microservices.yaml
├─ Pods: 1 (all-in-one)              ├─ Pods: 3 (coordinator + agents)
├─ Namespace: ...kubecon-simple      ├─ Namespace: ...microservices
├─ Status: PRODUCTION                └─ Status: TESTING
└─ External IP: 172.168.108.4
```

---

## 📝 Next Steps After Deploy

### 1. Get External IP

```bash
kubectl get svc coordinator-service -n multiagent-microservices
```

### 2. Test A2A Endpoint

```bash
EXTERNAL_IP=$(kubectl get svc coordinator-service -n multiagent-microservices -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$EXTERNAL_IP/a2a/
```

### 3. Check MCP Communication

```bash
# Send test message
curl -X POST http://$EXTERNAL_IP/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"Convert 100 USD to EUR","session_id":"test"}'

# Check logs for MCP activity
kubectl logs -n multiagent-microservices -l app=coordinator --tail=100 | grep "🚀 \[MCP\]"
```

**Expected logs:**
```
🔌 [MCP] Connecting to currency-agent MCP server...
✅ [MCP] Connected to currency-agent
🚀 [MCP] Calling tool 'convert_currency' on currency-agent
✅ [MCP] Tool executed successfully
```

---

## 🎛️ Managing Both Environments

### Switch Between Environments

```bash
# Work with Phase 1
azd env select kubeconagent
kubectl config set-context --current --namespace=multiagent-kubecon-simple

# Work with Phase 2
azd env select kubecon-micro
kubectl config set-context --current --namespace=multiagent-microservices
```

### Update Phase 2 Services

```bash
# Make code changes, then:
azd env select kubecon-micro
azd deploy --config azure.microservices.yaml

# Or update single service:
azd deploy coordinator --config azure.microservices.yaml
```

### Compare Performance

```bash
# Test Phase 1
curl -X POST http://172.168.108.4/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"Convert 100 USD to EUR","session_id":"test1"}'

# Test Phase 2
curl -X POST http://$EXTERNAL_IP/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"Convert 100 USD to EUR","session_id":"test2"}'
```

---

## 💰 Cost Optimization

### Option 1: Share Resources (Recommended)

```bash
# Share ACR from Phase 1
ACR_NAME=$(az acr list --resource-group rg-kubeconagent --query "[0].name" -o tsv)
azd env set SHARED_ACR_NAME $ACR_NAME

# Share OpenAI from Phase 1
OPENAI_ID=$(az cognitiveservices account list --resource-group rg-kubeconagent --query "[0].id" -o tsv)
azd env set SHARED_OPENAI_ID $OPENAI_ID

# Re-provision
azd provision --config azure.microservices.yaml
```

**Savings:** ~30% cost reduction

### Option 2: Stop AKS When Not Testing

```bash
# Stop Phase 2 AKS (no compute charges)
az aks stop --resource-group rg-kubecon-micro --name $(az aks list --resource-group rg-kubecon-micro --query "[0].name" -o tsv)

# Start when needed
az aks start --resource-group rg-kubecon-micro --name $(az aks list --resource-group rg-kubecon-micro --query "[0].name" -o tsv)
```

---

## 📊 Success Criteria

Phase 2 is successful when:

- [ ] `azd env list` shows both `kubeconagent` and `kubecon-micro`
- [ ] `kubectl get pods -n multiagent-microservices` shows 3 pods running
- [ ] External IP assigned to coordinator-service
- [ ] `curl http://$EXTERNAL_IP/a2a/` returns Agent Card
- [ ] Logs show `🚀 [MCP]` when using currency/activity agents
- [ ] Phase 1 still accessible and working

---

## 🆘 Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod -n multiagent-microservices [POD_NAME]
kubectl logs -n multiagent-microservices [POD_NAME]
```

### Can't Pull Images

```bash
# Verify ACR attachment
az aks show --resource-group rg-kubecon-micro --name [AKS_NAME] --query "servicePrincipalProfile"

# Re-attach ACR
az aks update --resource-group rg-kubecon-micro --name [AKS_NAME] --attach-acr [ACR_NAME]
```

### MCP Connection Failed

```bash
# Test DNS inside coordinator pod
kubectl exec -n multiagent-microservices [COORDINATOR_POD] -- nslookup currency-agent

# Test HTTP connectivity
kubectl exec -n multiagent-microservices [COORDINATOR_POD] -- curl http://currency-agent:8001/health
```

---

## 📚 Full Documentation

- **[AZD_DEPLOYMENT_GUIDE.md](./AZD_DEPLOYMENT_GUIDE.md)**: Complete azd deployment guide
- **[PHASE2_IMPLEMENTATION_PLAN.md](./PHASE2_IMPLEMENTATION_PLAN.md)**: Step-by-step implementation
- **[PHASE2_CHECKLIST.md](./PHASE2_CHECKLIST.md)**: Quick checkbox workflow
- **[PHASE2_ARCHITECTURE.md](./PHASE2_ARCHITECTURE.md)**: Architecture diagrams

---

## 🎉 You're Ready!

**Before implementing service code**, just run:

```bash
azd env new kubecon-micro
azd provision --config azure.microservices.yaml
```

This will create your infrastructure. Then follow **PHASE2_IMPLEMENTATION_PLAN.md** to create the service code, and finally:

```bash
azd deploy --config azure.microservices.yaml
```

**Your microservices will be live!** 🚀
