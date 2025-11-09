#!/usr/bin/env python3
"""
Complete A2A Protocol Test Suite
Tests all A2A endpoints and methods to identify what's working
"""

import httpx
import json
import asyncio
from typing import Dict, Any

# Configuration
BASE_URL = "http://<YOUR-PUBLIC-IP>"
A2A_ENDPOINT = f"{BASE_URL}/a2a/"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.YELLOW}ℹ️  {msg}{Colors.END}")

async def test_basic_endpoints():
    """Test basic HTTP endpoints"""
    print_test("Basic HTTP Endpoints")
    
    async with httpx.AsyncClient(timeout=10) as client:
        # Test 1: GET /a2a/
        try:
            response = await client.get(A2A_ENDPOINT)
            print_info(f"GET /a2a/ -> Status: {response.status_code}")
            if response.status_code == 307:
                print_info(f"  Redirects to: {response.headers.get('location')}")
            elif response.status_code == 405:
                print_info(f"  Method not allowed. Allowed: {response.headers.get('allow')}")
            else:
                print_info(f"  Response: {response.text[:200]}")
        except Exception as e:
            print_error(f"GET /a2a/ failed: {e}")
        
        # Test 2: POST /a2a/ (empty)
        try:
            response = await client.post(A2A_ENDPOINT, json={})
            print_info(f"POST /a2a/ (empty) -> Status: {response.status_code}")
            print_info(f"  Response: {response.json()}")
        except Exception as e:
            print_error(f"POST /a2a/ failed: {e}")
        
        # Test 3: GET /agent-card endpoint
        try:
            response = await client.get(f"{BASE_URL}/agent-card")
            print_info(f"GET /agent-card -> Status: {response.status_code}")
            if response.status_code == 200:
                card = response.json()
                print_success(f"Agent Card retrieved!")
                print_info(f"  Name: {card.get('name')}")
                print_info(f"  Skills: {len(card.get('skills', []))}")
        except Exception as e:
            print_error(f"GET /agent-card failed: {e}")

async def test_jsonrpc_methods():
    """Test JSON-RPC 2.0 methods"""
    print_test("JSON-RPC 2.0 Methods")
    
    # Common JSON-RPC methods to try
    methods_to_test = [
        ("agent.get", {}),
        ("agent.card", {}),
        ("agent.info", {}),
        ("task.send", {"input_text": "Hello"}),
        ("task.create", {"input_text": "Hello"}),
        ("tasks.send", {"input_text": "Hello"}),
    ]
    
    async with httpx.AsyncClient(timeout=10) as client:
        for method, params in methods_to_test:
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": 1
            }
            
            try:
                response = await client.post(A2A_ENDPOINT, json=payload)
                result = response.json()
                
                if "error" in result:
                    error_code = result["error"].get("code")
                    error_msg = result["error"].get("message")
                    
                    if error_code == -32601:
                        print_error(f"Method '{method}': Not Found")
                    else:
                        print_info(f"Method '{method}': Error {error_code} - {error_msg}")
                else:
                    print_success(f"Method '{method}': SUCCESS!")
                    print_info(f"  Result: {json.dumps(result.get('result', {}), indent=2)[:200]}")
                    
            except Exception as e:
                print_error(f"Method '{method}' failed: {e}")

async def test_a2a_task_submission():
    """Test A2A task submission with proper payload"""
    print_test("A2A Task Submission")
    
    # Try different task submission formats
    task_payloads = [
        {
            "name": "Standard task format",
            "payload": {
                "jsonrpc": "2.0",
                "method": "task.send",
                "params": {
                    "task": {
                        "input_text": "Convert 100 USD to EUR",
                        "skill_id": "trip_planning_sk"
                    }
                },
                "id": 1
            }
        },
        {
            "name": "Simple input_text",
            "payload": {
                "jsonrpc": "2.0",
                "method": "task.send",
                "params": {
                    "input_text": "Convert 100 USD to EUR"
                },
                "id": 2
            }
        },
        {
            "name": "Tasks endpoint format",
            "payload": {
                "jsonrpc": "2.0",
                "method": "tasks.send",
                "params": {
                    "task": {
                        "inputText": "Convert 100 USD to EUR"
                    }
                },
                "id": 3
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=30) as client:
        for test_case in task_payloads:
            print_info(f"\nTesting: {test_case['name']}")
            try:
                response = await client.post(A2A_ENDPOINT, json=test_case['payload'])
                result = response.json()
                
                if "error" in result:
                    print_error(f"  Error: {result['error'].get('message')}")
                else:
                    print_success(f"  Task accepted!")
                    if "result" in result:
                        print_info(f"  Result: {json.dumps(result['result'], indent=2)[:300]}")
                        
            except Exception as e:
                print_error(f"  Failed: {e}")

async def test_rest_api_comparison():
    """Test REST API for comparison"""
    print_test("REST API (for comparison)")
    
    async with httpx.AsyncClient(timeout=30) as client:
        # Test REST API
        try:
            response = await client.post(
                f"{BASE_URL}/api/chat/message",
                json={
                    "message": "Convert 100 USD to EUR",
                    "session_id": "test-a2a-comparison"
                }
            )
            
            if response.status_code == 200:
                print_success("REST API working!")
                result = response.json()
                print_info(f"  Response: {result.get('response', '')[:200]}")
            else:
                print_error(f"REST API failed: {response.status_code}")
                
        except Exception as e:
            print_error(f"REST API test failed: {e}")

async def inspect_a2a_server_logs():
    """Check what the server logs show"""
    print_test("Server Configuration Check")
    
    async with httpx.AsyncClient(timeout=10) as client:
        # Check health endpoint
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                health = response.json()
                print_success("Health check passed")
                print_info(f"  Service: {health.get('service')}")
                print_info(f"  Architecture: {health.get('architecture')}")
                print_info(f"  Protocols: {health.get('protocols')}")
        except Exception as e:
            print_error(f"Health check failed: {e}")
        
        # Check services status
        try:
            response = await client.get(f"{BASE_URL}/services/status")
            if response.status_code == 200:
                status = response.json()
                print_success("Services status retrieved")
                print_info(f"  Coordinator: {status.get('coordinator', {}).get('status')}")
                print_info(f"  MCP Agents: {json.dumps(status.get('mcp_agents', {}), indent=2)}")
        except Exception as e:
            print_info(f"Services status not available: {e}")

async def main():
    print(f"\n{Colors.BLUE}{'#'*60}{Colors.END}")
    print(f"{Colors.BLUE}# A2A PROTOCOL COMPREHENSIVE TEST SUITE{Colors.END}")
    print(f"{Colors.BLUE}# Target: {BASE_URL}{Colors.END}")
    print(f"{Colors.BLUE}{'#'*60}{Colors.END}")
    
    # Run all tests
    await inspect_a2a_server_logs()
    await test_basic_endpoints()
    await test_jsonrpc_methods()
    await test_a2a_task_submission()
    await test_rest_api_comparison()
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST SUITE COMPLETED{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    print_info("\n📊 Summary:")
    print_info("  • Check which methods returned SUCCESS (✅)")
    print_info("  • Monitor kubectl logs for A2A activity")
    print_info("  • Compare REST API vs A2A protocol behavior")

if __name__ == "__main__":
    asyncio.run(main())
