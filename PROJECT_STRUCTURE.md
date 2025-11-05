# Project Structure - Phase 2 Microservices

This document describes the clean, production-ready structure after Phase 2 deployment.

---

## 📁 Repository Structure

```
MultiAgent-kubecon2025/
├── README.md                          # Main project documentation
├── PROTOCOL_FLOWS.md                  # Visual A2A vs MCP flow diagrams
├── MONITORING_GUIDE.md                # How to monitor logs and protocols
├── PROJECT_STRUCTURE.md               # This file
│
├── azure.yaml                         # Azure Developer CLI configuration
├── pyproject.toml                     # Python project metadata
├── requirements.txt                   # Production dependencies
├── requirements-minimal.txt           # Docker build dependencies
├── .env.template                      # Environment variables template
├── .gitignore                         # Git ignore rules
│
├── Dockerfile.coordinator             # Coordinator service container
├── Dockerfile.currency                # Currency agent container
│
├── src/                               # Source code
│   ├── __init__.py
│   ├── agents/                        # AI agent implementations
│   │   ├── __init__.py
│   │   ├── coordinator_agent.py       # Main travel coordinator
│   │   ├── worker_agent.py            # Specialized agents
│   │   ├── mcp_currency_server.py     # Currency MCP server
│   │   └── mcp_activity_server.py     # Activity MCP server
│   │
│   ├── config/                        # Configuration
│   │   ├── __init__.py
│   │   └── azure_config.py            # Azure settings
│   │
│   ├── protocols/                     # Protocol implementations
│   │   ├── __init__.py
│   │   ├── a2a_handler.py             # A2A protocol
│   │   └── mcp_handler.py             # MCP protocol
│   │
│   └── services/                      # Microservices (Phase 2)
│       ├── coordinator/
│       │   └── main.py                # Coordinator FastAPI app
│       ├── currency_agent/
│       │   └── main.py                # Currency agent HTTP wrapper
│       └── activity_agent/
│           └── main.py                # Activity agent HTTP wrapper
│
├── static/                            # Web UI static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── chat.js
│
├── templates/                         # HTML templates
│   └── index.html                     # Chat interface
│
├── manifests/                         # Kubernetes manifests
│   ├── monolithic/                    # Phase 1 (main branch)
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── secret.yaml
│   │
│   └── microservices/                 # Phase 2 (microservices branch)
│       ├── namespace.yaml
│       ├── configmap.yaml
│       ├── coordinator/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       ├── currency-agent/
│       │   ├── deployment.yaml
│       │   └── service.yaml
│       └── activity-agent/
│           ├── deployment.yaml
│           └── service.yaml
│
├── infra/                             # Infrastructure as Code (Bicep)
│   ├── main.bicep                     # Main infrastructure template
│   ├── main.parameters.json           # Parameters
│   └── modules/
│       ├── aks.bicep                  # AKS cluster
│       ├── acr.bicep                  # Container registry
│       ├── openai.bicep               # Azure OpenAI
│       ├── vnet.bicep                 # Virtual network
│       ├── log-analytics.bicep        # Monitoring
│       └── rbac/                      # Role assignments
│           ├── aks-acr-pull.bicep
│           └── openai-user.bicep
│
├── docs/                              # Additional documentation
│   ├── A2A_AND_MCP_EXPLAINED.md       # Protocol comparison
│   ├── MCP_INTEGRATION.md             # MCP implementation details
│   └── PHASE1_TEST_RESULTS.md         # Testing history
│
├── .devcontainer/                     # GitHub Codespaces config
│   ├── devcontainer.json
│   └── Dockerfile
│
├── .github/                           # GitHub workflows
│   ├── copilot-instructions.md        # Copilot customization
│   └── workflows/
│       └── azure-deploy.yml           # CI/CD (if used)
│
├── test_mcp_simple.py                 # MCP integration tests
└── test_mcp_local.py                  # Full MCP test suite

```

---

## 🔑 Key Files Explained

### Configuration Files

| File | Purpose |
|------|---------|
| `azure.yaml` | Azure Developer CLI main config for deployment |
| `pyproject.toml` | Python dependencies and project metadata |
| `requirements.txt` | Full dependency list with versions |
| `requirements-minimal.txt` | Minimal deps for Docker (avoids editable install issues) |

### Dockerfiles

| File | Service | Base Image | Purpose |
|------|---------|------------|---------|
| `Dockerfile.coordinator` | Coordinator | python:3.11-slim | Web UI + A2A + MCP client |
| `Dockerfile.currency` | Currency Agent | python:3.11-slim | MCP server for currency tools |

**Note**: Activity agent reuses `Dockerfile.currency` with different context in azure.yaml

### Source Code

| Directory | Contents |
|-----------|----------|
| `src/agents/` | AI agent logic (Semantic Kernel) |
| `src/config/` | Azure OpenAI configuration |
| `src/protocols/` | A2A and MCP protocol handlers |
| `src/services/` | **Phase 2**: Microservice FastAPI apps |

### Manifests

| Directory | Deployment |
|-----------|------------|
| `manifests/monolithic/` | **Phase 1**: Single pod deployment |
| `manifests/microservices/` | **Phase 2**: 3 separate services |

### Infrastructure

| Directory | Purpose |
|-----------|---------|
| `infra/modules/` | Reusable Bicep modules |
| `infra/modules/rbac/` | Role-based access control |

---

## 🚀 Deployments

### Phase 1 (main branch)
- **Branch**: `main`
- **Namespace**: `multiagent-kubecon-simple`
- **External IP**: http://172.168.108.4
- **Architecture**: Monolithic (single pod)
- **Resource Group**: `rg-kubeconagent`
- **Status**: ✅ Deployed and working

### Phase 2 (microservices branch)
- **Branch**: `microservices`
- **Namespace**: `multiagent-microservices`
- **External IP**: http://172.169.51.14
- **Architecture**: 3 microservices
  - Coordinator (Port 8000, LoadBalancer)
  - Currency Agent (Port 8001, ClusterIP)
  - Activity Agent (Port 8002, ClusterIP)
- **Resource Group**: `rg-kubecon-micro`
- **Status**: ✅ Deployed and working

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main documentation with quick start |
| `PROTOCOL_FLOWS.md` | Visual diagrams showing A2A vs MCP flows |
| `MONITORING_GUIDE.md` | How to monitor logs, test protocols |
| `docs/A2A_AND_MCP_EXPLAINED.md` | Protocol concepts and differences |
| `docs/MCP_INTEGRATION.md` | MCP implementation technical details |

---

## 🧹 Removed Files

The following files were removed as they were outdated or redundant:

### Removed from Root:
- ❌ `azure.microservices.yaml` (merged into azure.yaml)
- ❌ `Dockerfile` (replaced by service-specific Dockerfiles)
- ❌ `main.py` (moved to src/services/)
- ❌ `deploy.log` (temporary file)
- ❌ `check-deployment.sh` (obsolete script)
- ❌ `DEPLOYMENT.md` (outdated, replaced by README)
- ❌ `DEPLOYMENT_SUMMARY.md` (Phase 1 only, outdated)
- ❌ `NEXT_STEPS_AZD.md` (completed tasks)
- ❌ `PHASE2_STATUS.md` (deployment complete)
- ❌ `CODESPACES_CHECKLIST.md` (redundant)
- ❌ `CODESPACES_QUICKREF.md` (redundant)
- ❌ `Dockerfile.activity` (not used, uses Dockerfile.currency)

### Removed from docs/:
- ❌ `PHASE2_CHECKLIST.md` (completed)
- ❌ `PHASE2_IMPLEMENTATION_PLAN.md` (completed)
- ❌ `PHASE2_NEW_RESOURCE_GROUP.md` (completed)
- ❌ `PHASE2_ARCHITECTURE.md` (merged into README)
- ❌ `AZD_DEPLOYMENT_GUIDE.md` (merged into README)
- ❌ `NEW_ENVIRONMENT_SETUP.md` (completed)
- ❌ `QUICK_REFERENCE_DUAL_ENV.md` (info in README)
- ❌ `README_AZD_MICROSERVICES.md` (merged into README)
- ❌ `LOGGING_GUIDE.md` (replaced by MONITORING_GUIDE.md)
- ❌ `LOG_EXAMPLES.md` (merged into MONITORING_GUIDE.md)

---

## ✅ Current Clean State

The repository now contains:
- **3 markdown files in root** (README, PROTOCOL_FLOWS, MONITORING_GUIDE, PROJECT_STRUCTURE)
- **3 documentation files in docs/** (A2A explained, MCP integration, Phase 1 tests)
- **1 azure.yaml** for deployment
- **2 Dockerfiles** (coordinator, currency)
- **Clean source tree** with logical separation
- **Complete manifests** for both phases
- **Complete infrastructure** as code

All files serve a clear purpose and are up-to-date with Phase 2 deployment! 🎯
