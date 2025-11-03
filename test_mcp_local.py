"""
Local test script for MCP integration.

This script demonstrates how to:
1. Start MCP servers for Currency and Activity agents
2. Connect the MCP coordinator to both servers
3. Discover available tools
4. Execute tools and see results
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.mcp_coordinator import MCPCoordinator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_mcp_integration():
    """Test the MCP integration locally."""
    
    print("\n" + "="*70)
    print("🧪 Testing MCP Integration - Phase 1")
    print("="*70 + "\n")
    
    coordinator = MCPCoordinator()
    
    # Get the correct Python executable path
    import sys
    coordinator.python_exe = sys.executable
    
    try:
        # Step 1: Register Currency Agent
        print("📝 Step 1: Registering Currency Exchange Agent...")
        await coordinator.register_agent(
            agent_name="currency",
            server_script="src/agent/mcp_currency_server.py"
        )
        print("✅ Currency Agent registered\n")
        
        # Step 2: Register Activity Agent
        print("📝 Step 2: Registering Activity Planner Agent...")
        await coordinator.register_agent(
            agent_name="activity",
            server_script="src/agent/mcp_activity_server.py"
        )
        print("✅ Activity Agent registered\n")
        
        # Step 3: Discover all available tools
        print("📝 Step 3: Discovering available tools from all agents...")
        all_tools = await coordinator.discover_tools()
        
        for agent_name, tools in all_tools.items():
            print(f"\n🔧 {agent_name.upper()} Agent Tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        print()
        
        # Step 4: Test Currency Exchange
        print("📝 Step 4: Testing Currency Exchange Tool...")
        print("   Query: USD to KRW exchange rate")
        currency_result = await coordinator.call_tool(
            agent_name="currency",
            tool_name="get_exchange_rate",
            arguments={
                "currency_from": "USD",
                "currency_to": "KRW"
            }
        )
        print(f"   Result: {currency_result.content[0].text}")
        print()
        
        # Step 5: Test Currency Conversion
        print("📝 Step 5: Testing Currency Conversion Tool...")
        print("   Query: Convert 100 USD to KRW")
        conversion_result = await coordinator.call_tool(
            agent_name="currency",
            tool_name="convert_amount",
            arguments={
                "amount": 100,
                "currency_from": "USD",
                "currency_to": "KRW"
            }
        )
        print(f"   Result: {conversion_result.content[0].text}")
        print()
        
        # Step 6: Test Activity Planning
        print("📝 Step 6: Testing Activity Planning Tool...")
        print("   Query: Plan 2-day trip to Seoul with $100/day budget")
        activity_result = await coordinator.call_tool(
            agent_name="activity",
            tool_name="plan_activities",
            arguments={
                "location": "Seoul, South Korea",
                "duration_days": 2,
                "budget_per_day": 100,
                "interests": ["food", "culture", "shopping"]
            }
        )
        print(f"   Result:\n{activity_result.content[0].text}")
        print()
        
        # Step 7: Test Restaurant Suggestions
        print("📝 Step 7: Testing Restaurant Suggestion Tool...")
        print("   Query: Korean restaurants in Seoul (moderate budget)")
        restaurant_result = await coordinator.call_tool(
            agent_name="activity",
            tool_name="suggest_restaurants",
            arguments={
                "location": "Seoul",
                "cuisine_type": "Korean",
                "budget": "moderate"
            }
        )
        print(f"   Result:\n{restaurant_result.content[0].text}")
        print()
        
        # Step 8: Test Attraction Suggestions
        print("📝 Step 8: Testing Attraction Suggestion Tool...")
        print("   Query: Cultural attractions in Seoul")
        attraction_result = await coordinator.call_tool(
            agent_name="activity",
            tool_name="suggest_attractions",
            arguments={
                "location": "Seoul",
                "category": "cultural"
            }
        )
        print(f"   Result:\n{attraction_result.content[0].text}")
        print()
        
        print("="*70)
        print("✅ All MCP Integration Tests Passed!")
        print("="*70)
        print("\n📊 Summary:")
        print(f"   - Agents Registered: 2 (Currency, Activity)")
        print(f"   - Tools Discovered: {sum(len(tools) for tools in all_tools.values())}")
        print(f"   - Tool Calls Executed: 6")
        print(f"   - Status: SUCCESS ✅")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        logger.exception("Test failed")
        return False
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        await coordinator.shutdown()
        print("✅ Cleanup complete\n")
    
    return True


async def test_individual_server(server_name: str, server_script: str):
    """Test an individual MCP server in isolation.
    
    Args:
        server_name: Name of the server (e.g., 'currency', 'activity')
        server_script: Path to the server script
    """
    print(f"\n🧪 Testing {server_name.upper()} MCP Server individually...\n")
    
    coordinator = MCPCoordinator()
    coordinator.python_exe = sys.executable
    
    try:
        await coordinator.register_agent(server_name, server_script)
        tools = await coordinator.discover_tools()
        
        print(f"✅ {server_name.upper()} Server is running")
        print(f"   Available tools: {[t['name'] for t in tools[server_name]]}")
        
        await coordinator.shutdown()
        return True
    except Exception as e:
        print(f"❌ {server_name.upper()} Server failed: {e}")
        return False


async def main():
    """Main test runner."""
    print("\n🚀 MCP Integration Test Suite")
    print("=" * 70)
    
    # Option 1: Run full integration test
    print("\nRunning full integration test...\n")
    success = await test_mcp_integration()
    
    if not success:
        print("\n⚠️  Full test failed. Testing servers individually...\n")
        
        # Test Currency Server
        await test_individual_server("currency", "src/agent/mcp_currency_server.py")
        
        # Test Activity Server
        await test_individual_server("activity", "src/agent/mcp_activity_server.py")
    
    print("\n" + "="*70)
    print("🏁 Test Suite Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
