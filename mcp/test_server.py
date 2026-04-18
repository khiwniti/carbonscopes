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
async def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b


@mcp.tool
async def get_server_info() -> dict:
    """Get information about this MCP server"""
    return {
        "name": "TestMCPServer",
        "version": "1.0.0",
        "description": "A test MCP server for CarbonScope",
        "tools": ["echo", "add_numbers", "multiply_numbers", "get_server_info"],
    }


@mcp.resource("greeting://{name}")
async def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! Welcome to the Test MCP Server."


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
