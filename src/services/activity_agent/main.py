"""Activity Agent Microservice - MCP Server over HTTP.

This service exposes the Activity Planning MCP server over HTTP,
allowing the coordinator to communicate with it via MCP protocol over HTTP.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn

# Import the existing MCP server
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from agent.mcp_activity_server import ActivityMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global MCP server instance
mcp_server: ActivityMCPServer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    global mcp_server
    logger.info("🚀 [MCP] Starting Activity Planner MCP Server...")
    
    # Initialize MCP server
    mcp_server = ActivityMCPServer()
    logger.info("✅ [MCP] Activity Planner MCP Server initialized")
    logger.info("🔧 [MCP] Available tools: plan_activities, suggest_restaurants, suggest_attractions")
    
    yield
    
    logger.info("⏹️  [MCP] Shutting down Activity Planner MCP Server...")


# Create FastAPI app
app = FastAPI(
    title="Activity Planner MCP Server",
    description="Microservice exposing activity planning tools via MCP over HTTP",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "activity-agent",
        "protocol": "MCP over HTTP"
    }


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP communication endpoint.
    
    This endpoint receives MCP JSON-RPC messages over HTTP and
    processes them through the MCP server.
    """
    try:
        # Get JSON-RPC message from request body
        message = await request.json()
        logger.info(f"🚀 [MCP] Received request: {message.get('method', 'unknown')}")
        
        if not mcp_server:
            return JSONResponse(
                status_code=503,
                content={"error": "MCP server not initialized"}
            )
        
        # Handle MCP methods
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        if method == "tools/list":
            # List available tools
            tools = await mcp_server.server.list_tools()
            result = {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools
                ]
            }
            logger.info(f"🔧 [MCP] Listed {len(result['tools'])} tools")
            return {"jsonrpc": "2.0", "id": msg_id, "result": result}
        
        elif method == "tools/call":
            # Execute a tool
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            logger.info(f"🚀 [MCP] Calling tool '{tool_name}' with args: {arguments}")
            
            # Call the tool through the MCP server
            result_content = await mcp_server.server.call_tool(tool_name, arguments)
            
            # Convert TextContent to dict
            result = {
                "content": [
                    {"type": content.type, "text": content.text}
                    for content in result_content
                ]
            }
            
            logger.info(f"✅ [MCP] Tool '{tool_name}' executed successfully")
            return {"jsonrpc": "2.0", "id": msg_id, "result": result}
        
        elif method == "initialize":
            # MCP initialization
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "activity-agent",
                    "version": "1.0.0"
                }
            }
            logger.info("🔌 [MCP] Client initialized")
            return {"jsonrpc": "2.0", "id": msg_id, "result": result}
        
        else:
            logger.warning(f"⚠️  [MCP] Unknown method: {method}")
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            )
    
    except Exception as e:
        logger.error(f"❌ [MCP] Error processing request: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": message.get("id") if 'message' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    logger.info(f"🌐 Starting Activity Planner Agent on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
