from fastmcp import FastMCP

mcp = FastMCP(name="TestMCPServer")


@mcp.tool
async def echo(message: str) -> str:
    """Echo back the provided message"""
    return f"Echo: {message}"


@mcp.tool
async def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


@mcp.tool
async def get_server_info() -> dict:
    """Get information about this MCP server"""
    return {
        "name": "TestMCPServer",
        "version": "1.0.0",
        "description": "A test MCP server for CarbonScope",
    }


if __name__ == "__main__":
    mcp.run()
