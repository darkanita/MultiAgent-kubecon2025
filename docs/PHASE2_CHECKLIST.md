# Phase 2: Quick Start Checklist

This is a condensed checklist for implementing Phase 2. See `PHASE2_IMPLEMENTATION_PLAN.md` for detailed explanations.

## ✅ Pre-Flight Checklist

- [ ] Phase 1 deployed and working on AKS
- [ ] kubectl connected to cluster: `kubectl get pods -n multiagent-kubecon-simple`
- [ ] ACR access configured: `az acr login --name acrmakubeconagent5h4hjd6w`
- [ ] Current branch: `microservices`

---

## 📁 Step 1: Create Directory Structure

```bash
mkdir -p src/services/coordinator
mkdir -p src/services/currency-agent
mkdir -p src/services/activity-agent
mkdir -p manifests/microservices
```

---

## 📝 Step 2: Create Service Files

### Files to Create:

1. **Coordinator Service**
   - [ ] `src/services/coordinator/main.py` (FastAPI app with MCP client)
   - [ ] `src/services/coordinator/Dockerfile`

2. **Currency Agent**
   - [ ] `src/services/currency-agent/main.py` (MCP server runner)
   - [ ] `src/services/currency-agent/http_wrapper.py` (HTTP endpoint for MCP)
   - [ ] `src/services/currency-agent/Dockerfile`

3. **Activity Agent**
   - [ ] `src/services/activity-agent/main.py` (MCP server runner)
   - [ ] `src/services/activity-agent/http_wrapper.py` (HTTP endpoint for MCP)
   - [ ] `src/services/activity-agent/Dockerfile`

4. **Kubernetes Manifests**
   - [ ] `manifests/microservices/coordinator-deployment.yaml`
   - [ ] `manifests/microservices/currency-agent-deployment.yaml`
   - [ ] `manifests/microservices/activity-agent-deployment.yaml`

**⚡ Tip**: Copy templates from `PHASE2_IMPLEMENTATION_PLAN.md` sections 1-4

---

## 🔧 Step 3: Update MCP Coordinator

- [ ] Modify `src/agent/mcp_coordinator.py` to support HTTP communication
- [ ] Add `service_url` parameter to `MCPAgentClient.__init__`
- [ ] Add HTTP client logic to `connect()` and `call_tool()` methods

**Key Changes**:
```python
# Add this to MCPAgentClient
self.service_url = service_url
self.http_client = httpx.AsyncClient() if service_url else None

# In connect():
if self.service_url:
    # HTTP mode for K8s services
    response = await self.http_client.get(f"{self.service_url}/mcp/list_tools")
```

---

## 🐳 Step 4: Build Docker Images

```bash
# Build all three services
docker build -f src/services/coordinator/Dockerfile \
  -t acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/coordinator:latest .

docker build -f src/services/currency-agent/Dockerfile \
  -t acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/currency-agent:latest .

docker build -f src/services/activity-agent/Dockerfile \
  -t acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/activity-agent:latest .
```

**Status**:
- [ ] Coordinator image built
- [ ] Currency agent image built
- [ ] Activity agent image built

---

## ☁️ Step 5: Push to Azure Container Registry

```bash
# Login
az acr login --name acrmakubeconagent5h4hjd6w

# Push all images
docker push acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/coordinator:latest
docker push acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/currency-agent:latest
docker push acrmakubeconagent5h4hjd6w.azurecr.io/multiagent-kubecon-simple/activity-agent:latest
```

**Status**:
- [ ] Coordinator pushed to ACR
- [ ] Currency agent pushed to ACR
- [ ] Activity agent pushed to ACR

---

## ☸️ Step 6: Deploy to Kubernetes

### Deploy in Order (agents first, coordinator last):

```bash
# 1. Deploy Currency Agent
kubectl apply -f manifests/microservices/currency-agent-deployment.yaml -n multiagent-kubecon-simple

# 2. Deploy Activity Agent
kubectl apply -f manifests/microservices/activity-agent-deployment.yaml -n multiagent-kubecon-simple

# 3. Wait for agents to be ready
kubectl wait --for=condition=ready pod -l app=currency-agent -n multiagent-kubecon-simple --timeout=120s
kubectl wait --for=condition=ready pod -l app=activity-agent -n multiagent-kubecon-simple --timeout=120s

# 4. Deploy Coordinator
kubectl apply -f manifests/microservices/coordinator-deployment.yaml -n multiagent-kubecon-simple

# 5. Wait for coordinator
kubectl wait --for=condition=ready pod -l app=coordinator -n multiagent-kubecon-simple --timeout=120s
```

**Status**:
- [ ] Currency agent deployed and running
- [ ] Activity agent deployed and running
- [ ] Coordinator deployed and running

---

## 🔍 Step 7: Verify Deployment

### Check Pods

```bash
kubectl get pods -n multiagent-kubecon-simple
```

**Expected**:
```
NAME                                   READY   STATUS    RESTARTS   AGE
coordinator-service-xxxxx              1/1     Running   0          2m
currency-agent-xxxxx                   1/1     Running   0          3m
activity-agent-xxxxx                   1/1     Running   0          3m
```

**Status**:
- [ ] All pods showing 1/1 Ready
- [ ] All pods in Running status
- [ ] No restarts or errors

### Check Services

```bash
kubectl get svc -n multiagent-kubecon-simple
```

**Expected**:
```
NAME                  TYPE           CLUSTER-IP      EXTERNAL-IP       PORT(S)
coordinator-service   LoadBalancer   10.0.x.x        172.168.x.x       80:xxxxx/TCP
currency-agent        ClusterIP      10.0.x.x        <none>            8001/TCP
activity-agent        ClusterIP      10.0.x.x        <none>            8002/TCP
```

**Status**:
- [ ] Coordinator has external IP assigned
- [ ] Currency agent has ClusterIP
- [ ] Activity agent has ClusterIP

---

## 📊 Step 8: Check MCP Connectivity

### View Coordinator Startup Logs

```bash
kubectl logs deployment/coordinator-service -n multiagent-kubecon-simple | grep "MCP"
```

**Expected Output**:
```
🔌 [MCP] Connecting to currency-agent via HTTP: http://currency-agent:8001
🔌 [MCP] Connected to currency-agent MCP server. Available tools: ['get_exchange_rate', 'convert_amount']
🔌 [MCP] Connecting to activity-agent via HTTP: http://activity-agent:8002
🔌 [MCP] Connected to activity-agent MCP server. Available tools: ['plan_activities', 'suggest_restaurants', 'suggest_attractions']
✅ All MCP agents registered
```

**Status**:
- [ ] Coordinator connected to currency-agent
- [ ] Coordinator connected to activity-agent
- [ ] All tools discovered successfully

---

## 🧪 Step 9: Test End-to-End

### Get External IP

```bash
EXTERNAL_IP=$(kubectl get svc coordinator-service -n multiagent-kubecon-simple -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: http://${EXTERNAL_IP}"
```

### Send Test Request

```bash
curl -X POST "http://${EXTERNAL_IP}/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Convert 100 USD to EUR and suggest activities in Paris",
    "session_id": "phase2-test"
  }'
```

**Status**:
- [ ] Request completed successfully
- [ ] Response includes currency conversion
- [ ] Response includes activity suggestions

---

## 📝 Step 10: Watch Live Logs

Open 3 terminal windows:

**Terminal 1 - Coordinator**:
```bash
kubectl logs -f deployment/coordinator-service -n multiagent-kubecon-simple | grep -E "MCP|CHAT"
```

**Terminal 2 - Currency Agent**:
```bash
kubectl logs -f deployment/currency-agent -n multiagent-kubecon-simple
```

**Terminal 3 - Activity Agent**:
```bash
kubectl logs -f deployment/activity-agent -n multiagent-kubecon-simple
```

### Send Another Request and Watch

```bash
curl -X POST "http://${EXTERNAL_IP}/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "How much is 500 USD in Japanese Yen?", "session_id": "test2"}'
```

**Expected in Logs**:
- **Coordinator**: `🚀 [MCP] Calling tool 'convert_amount' on currency-agent`
- **Currency Agent**: `📥 Received tool call: convert_amount`
- **Coordinator**: `✅ [MCP] Tool executed successfully`

**Status**:
- [ ] Saw MCP call in coordinator logs
- [ ] Saw tool execution in agent logs
- [ ] Request completed successfully

---

## ✅ Final Validation

### Functionality Checklist

- [ ] Currency conversion works
- [ ] Activity planning works
- [ ] Web UI accessible at external IP
- [ ] A2A endpoint works: `curl http://${EXTERNAL_IP}/a2a/`
- [ ] Health endpoints respond: `curl http://${EXTERNAL_IP}/health`

### Performance Checklist

- [ ] Response time < 3 seconds
- [ ] No errors in logs
- [ ] All pods stable (no restarts)

### MCP Checklist

- [ ] MCP connection logs visible
- [ ] MCP tool call logs visible
- [ ] MCP success logs visible
- [ ] All 5 tools accessible (2 currency + 3 activity)

---

## 🎉 Success!

If all checkboxes are marked, **Phase 2 is complete!** You now have:

✅ Microservices architecture  
✅ MCP protocol active and visible in logs  
✅ Independent agent services  
✅ Scalable deployment  

---

## 🚨 Rollback (If Needed)

If something goes wrong:

```bash
# Delete microservices
kubectl delete -f manifests/microservices/ -n multiagent-kubecon-simple

# Restore Phase 1 monolithic deployment
kubectl apply -f manifests/deployment.yaml -n multiagent-kubecon-simple
```

---

## 📚 Next Steps

After successful Phase 2:

1. **Scale agents**: `kubectl scale deployment currency-agent --replicas=2`
2. **Add monitoring**: Prometheus + Grafana
3. **Start Phase 3**: Add HR Agent as new microservice
4. **Dynamic registration**: Agents auto-register with coordinator

---

## 🆘 Common Issues

### Issue: Pods stuck in CrashLoopBackOff

**Fix**: Check logs for errors
```bash
kubectl logs deployment/[service-name] -n multiagent-kubecon-simple --previous
```

### Issue: Coordinator can't connect to agents

**Fix**: Check service DNS resolution
```bash
kubectl exec -it deployment/coordinator-service -n multiagent-kubecon-simple -- \
  nslookup currency-agent
```

### Issue: No MCP logs

**Fix**: Ensure HTTP wrapper is running
```bash
kubectl logs deployment/currency-agent -n multiagent-kubecon-simple | grep "Starting"
```

---

## 📞 Need Help?

- Review detailed plan: `docs/PHASE2_IMPLEMENTATION_PLAN.md`
- Check logging guide: `docs/LOGGING_GUIDE.md`
- View log examples: `docs/LOG_EXAMPLES.md`

---

**Estimated Time**: 4-6 hours  
**Difficulty**: ⭐⭐⭐⭐ (Intermediate-Advanced)  
**Prerequisites**: Docker, Kubernetes, Python, Azure

Good luck! 🚀
