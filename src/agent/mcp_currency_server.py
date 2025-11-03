"""MCP Server for Currency Exchange Agent.

This module exposes the Currency Exchange functionality as an MCP server,
allowing other agents to discover and invoke currency conversion tools.
"""

import logging
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)


class CurrencyMCPServer:
    """MCP Server that exposes currency exchange tools."""

    def __init__(self):
        """Initialize the Currency MCP Server."""
        self.server = Server("currency-exchange-agent")
        self._register_tools()

    def _register_tools(self):
        """Register all currency-related tools with the MCP server."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available currency exchange tools."""
            return [
                Tool(
                    name="get_exchange_rate",
                    description="Retrieves exchange rate between two currencies using Frankfurter API",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "currency_from": {
                                "type": "string",
                                "description": "Currency code to convert from (e.g., USD)"
                            },
                            "currency_to": {
                                "type": "string",
                                "description": "Currency code to convert to (e.g., EUR, KRW)"
                            },
                            "date": {
                                "type": "string",
                                "description": "Date in YYYY-MM-DD format or 'latest'",
                                "default": "latest"
                            }
                        },
                        "required": ["currency_from", "currency_to"]
                    }
                ),
                Tool(
                    name="convert_amount",
                    description="Convert a specific amount from one currency to another",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "Amount to convert"
                            },
                            "currency_from": {
                                "type": "string",
                                "description": "Currency code to convert from"
                            },
                            "currency_to": {
                                "type": "string",
                                "description": "Currency code to convert to"
                            }
                        },
                        "required": ["amount", "currency_from", "currency_to"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Execute a currency exchange tool."""
            if name == "get_exchange_rate":
                return await self._get_exchange_rate(
                    arguments.get("currency_from"),
                    arguments.get("currency_to"),
                    arguments.get("date", "latest")
                )
            elif name == "convert_amount":
                return await self._convert_amount(
                    arguments.get("amount"),
                    arguments.get("currency_from"),
                    arguments.get("currency_to")
                )
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _get_exchange_rate(
        self,
        currency_from: str,
        currency_to: str,
        date: str = "latest"
    ) -> list[TextContent]:
        """Get exchange rate between two currencies."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'https://api.frankfurter.app/{date}',
                    params={'from': currency_from, 'to': currency_to},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                
                if 'rates' not in data or currency_to not in data['rates']:
                    return [TextContent(
                        type="text",
                        text=f'Could not retrieve rate for {currency_from} to {currency_to}'
                    )]
                
                rate = data['rates'][currency_to]
                return [TextContent(
                    type="text",
                    text=f'Exchange rate: 1 {currency_from} = {rate} {currency_to}'
                )]
        except Exception as e:
            logger.error(f"Currency API error: {e}")
            return [TextContent(
                type="text",
                text=f'Currency API call failed: {str(e)}'
            )]

    async def _convert_amount(
        self,
        amount: float,
        currency_from: str,
        currency_to: str
    ) -> list[TextContent]:
        """Convert a specific amount between currencies."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'https://api.frankfurter.app/latest',
                    params={
                        'amount': amount,
                        'from': currency_from,
                        'to': currency_to
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                
                if 'rates' not in data or currency_to not in data['rates']:
                    return [TextContent(
                        type="text",
                        text=f'Could not convert {amount} {currency_from} to {currency_to}'
                    )]
                
                converted_amount = data['rates'][currency_to]
                return [TextContent(
                    type="text",
                    text=f'{amount} {currency_from} = {converted_amount} {currency_to}'
                )]
        except Exception as e:
            logger.error(f"Currency conversion error: {e}")
            return [TextContent(
                type="text",
                text=f'Currency conversion failed: {str(e)}'
            )]

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
    server = CurrencyMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
