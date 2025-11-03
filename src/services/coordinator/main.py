"""Coordinator Microservice - A2A + Web UI + MCP Client.

This service acts as the coordinator in the microservices architecture:
- Exposes A2A endpoints for external agent communication
- Provides Web UI for direct user interaction
- Acts as MCP client to communicate with currency and activity agents
"""

import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Import existing components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from api.chat import router as chat_router
from agent.a2a_server import A2AServer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
httpx_client: httpx.AsyncClient = None
a2a_server: A2AServer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global httpx_client, a2a_server
    
    # Startup
    logger.info("🚀 Starting Coordinator Service (Microservices Architecture)...")
    logger.info("📡 [A2A] Initializing A2A Server for external agents...")
    logger.info("🔌 [MCP] Preparing MCP client connections...")
    
    httpx_client = httpx.AsyncClient(timeout=30)
    
    # Initialize A2A server
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    a2a_server = A2AServer(httpx_client, host=host, port=port)
    
    # Mount A2A endpoints to the main app
    app.mount("/a2a", a2a_server.get_starlette_app(), name="a2a")
    
    logger.info(f"✅ [A2A] A2A server mounted at /a2a")
    logger.info(f"🌐 Agent Card available at http://{host}:{port}/a2a/")
    
    # Log MCP agent URLs
    currency_url = os.getenv("CURRENCY_AGENT_URL", "http://currency-agent:8001")
    activity_url = os.getenv("ACTIVITY_AGENT_URL", "http://activity-agent:8002")
    logger.info(f"🔌 [MCP] Currency Agent: {currency_url}")
    logger.info(f"🔌 [MCP] Activity Agent: {activity_url}")
    
    yield
    
    # Shutdown
    logger.info("⏹️  Shutting down Coordinator Service...")
    if httpx_client:
        await httpx_client.aclose()


# Create FastAPI app
app = FastAPI(
    title="Travel Agent Coordinator",
    description=(
        "Coordinator microservice for A2A Travel Agent - "
        "Handles A2A protocol, Web UI, and MCP client coordination"
    ),
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files
# In container: files are at /app/static and /app/templates
# This file is at /app/src/services/coordinator/main.py
static_path = Path("/app/static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory=static_path), name="static")
else:
    logger.warning(f"⚠️  Static files directory not found: {static_path}")

# Setup templates
templates_path = Path("/app/templates")
if templates_path.exists():
    templates = Jinja2Templates(directory=templates_path)
else:
    logger.warning(f"⚠️  Templates directory not found: {templates_path}")
    templates = None

# Include API routes
app.include_router(chat_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main chat interface"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse("<h1>Travel Agent Coordinator</h1><p>Web UI templates not configured</p>")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "coordinator",
        "architecture": "microservices",
        "protocols": ["A2A", "MCP", "REST"]
    }


@app.get("/agent-card")
async def get_agent_card():
    """Expose the A2A Agent Card for discovery"""
    if a2a_server:
        return a2a_server._get_agent_card()
    return {"error": "A2A server not initialized"}


@app.get("/services/status")
async def services_status():
    """Check status of connected MCP services"""
    currency_url = os.getenv("CURRENCY_AGENT_URL", "http://currency-agent:8001")
    activity_url = os.getenv("ACTIVITY_AGENT_URL", "http://activity-agent:8002")
    
    services = {}
    
    # Check currency service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{currency_url}/health")
            services["currency"] = response.json() if response.status_code == 200 else {"status": "unhealthy"}
    except Exception as e:
        services["currency"] = {"status": "unreachable", "error": str(e)}
    
    # Check activity service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{activity_url}/health")
            services["activity"] = response.json() if response.status_code == 200 else {"status": "unhealthy"}
    except Exception as e:
        services["activity"] = {"status": "unreachable", "error": str(e)}
    
    return {
        "coordinator": {"status": "healthy"},
        "mcp_agents": services
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"🌐 Starting Coordinator on {host}:{port}")
    uvicorn.run(app, host=host, port=port, reload=debug)
