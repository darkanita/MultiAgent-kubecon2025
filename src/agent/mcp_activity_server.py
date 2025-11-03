"""MCP Server for Activity Planner Agent.

This module exposes the Activity Planning functionality as an MCP server,
allowing other agents to discover and invoke activity planning tools.
"""

import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)


class ActivityMCPServer:
    """MCP Server that exposes activity planning tools."""

    def __init__(self):
        """Initialize the Activity MCP Server."""
        self.server = Server("activity-planner-agent")
        self._register_tools()

    def _register_tools(self):
        """Register all activity planning tools with the MCP server."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available activity planning tools."""
            return [
                Tool(
                    name="plan_activities",
                    description="Generate activity recommendations for travelers based on location, duration, and preferences",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Destination city or location"
                            },
                            "duration_days": {
                                "type": "integer",
                                "description": "Number of days for the trip"
                            },
                            "budget_per_day": {
                                "type": "number",
                                "description": "Daily budget in the destination currency",
                                "default": 0
                            },
                            "interests": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of traveler interests (e.g., food, culture, adventure)",
                                "default": []
                            }
                        },
                        "required": ["location", "duration_days"]
                    }
                ),
                Tool(
                    name="suggest_restaurants",
                    description="Suggest restaurants and local food experiences",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City or area for restaurant recommendations"
                            },
                            "cuisine_type": {
                                "type": "string",
                                "description": "Preferred cuisine type (e.g., local, international, vegetarian)"
                            },
                            "budget": {
                                "type": "string",
                                "description": "Budget level: budget, moderate, or luxury",
                                "default": "moderate"
                            }
                        },
                        "required": ["location"]
                    }
                ),
                Tool(
                    name="suggest_attractions",
                    description="Recommend tourist attractions and sightseeing spots",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City or area"
                            },
                            "category": {
                                "type": "string",
                                "description": "Category: cultural, historical, nature, entertainment, shopping",
                                "default": "cultural"
                            }
                        },
                        "required": ["location"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Execute an activity planning tool."""
            if name == "plan_activities":
                return await self._plan_activities(arguments)
            elif name == "suggest_restaurants":
                return await self._suggest_restaurants(arguments)
            elif name == "suggest_attractions":
                return await self._suggest_attractions(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _plan_activities(self, args: dict[str, Any]) -> list[TextContent]:
        """Generate a comprehensive activity plan."""
        location = args.get("location")
        duration = args.get("duration_days")
        budget = args.get("budget_per_day", 0)
        interests = args.get("interests", [])

        # In a real implementation, this would call external APIs or use AI
        # For now, we'll return a structured plan
        plan = f"""
Activity Plan for {location} ({duration} days)

Budget: ${budget} per day
Interests: {', '.join(interests) if interests else 'General tourism'}

Day-by-day itinerary:
"""
        for day in range(1, duration + 1):
            plan += f"\nDay {day}:\n"
            plan += "  Morning: Explore local markets and breakfast spots\n"
            plan += "  Afternoon: Visit main attractions and cultural sites\n"
            plan += "  Evening: Dinner and local entertainment\n"

        plan += "\nNote: This is a sample itinerary. Specific recommendations can be obtained using other tools."

        return [TextContent(type="text", text=plan)]

    async def _suggest_restaurants(self, args: dict[str, Any]) -> list[TextContent]:
        """Suggest restaurants based on criteria."""
        location = args.get("location")
        cuisine = args.get("cuisine_type", "local")
        budget = args.get("budget", "moderate")

        suggestions = f"""
Restaurant Recommendations for {location}

Cuisine: {cuisine}
Budget Level: {budget}

1. Local favorite - Traditional dishes and authentic atmosphere
2. Popular spot - Known for quality and service
3. Hidden gem - Off-the-beaten-path local experience
4. Modern fusion - Contemporary take on local cuisine
5. Street food areas - Budget-friendly authentic experience

Note: These are general categories. For specific restaurant names and locations, 
please consult local travel guides or review platforms.
"""
        return [TextContent(type="text", text=suggestions)]

    async def _suggest_attractions(self, args: dict[str, Any]) -> list[TextContent]:
        """Suggest tourist attractions."""
        location = args.get("location")
        category = args.get("category", "cultural")

        suggestions = f"""
{category.title()} Attractions in {location}

Top recommendations:
1. Major landmark or monument
2. Museums and galleries
3. Historical sites
4. Parks and outdoor spaces
5. Local neighborhoods worth exploring

Tips:
- Check opening hours and booking requirements
- Consider purchasing city passes for savings
- Plan visits during off-peak hours when possible

Note: For specific attraction details, hours, and pricing, 
please check official tourism websites or local guides.
"""
        return [TextContent(type="text", text=suggestions)]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# For running as standalone MCP server
async def main():
    """Main entry point for the MCP server."""
    server = ActivityMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
