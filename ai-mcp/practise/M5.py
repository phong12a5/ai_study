"""M5: MCP client connects to local server.py via stdio."""

import asyncio
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_PATH = Path(__file__).with_name("server.py")

server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(SERVER_PATH)],
)


async def run() -> None:
    """Start local MCP server, list tools, and call tra_cuu."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}")

            result = await session.call_tool("tra_cuu", {"country": "Việt Nam"})
            print("\nKết quả tra_cuu('Việt Nam'):")
            for item in result.content:
                text = getattr(item, "text", None)
                if text is not None:
                    print(f"  {text}")


def main() -> None:
    """Entry point for the M5 client."""
    asyncio.run(run())


if __name__ == "__main__":
    main()