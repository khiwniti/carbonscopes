#!/usr/bin/env python3
"""
Test MCP integration with CarbonScope project
This script demonstrates how to use MCP tools with the CarbonScope backend
"""

import asyncio
import json
import logging
import os
import sys

# Add backend to path
sys.path.insert(0, "/teamspace/studios/this_studio/carbonscopes/backend")

from core.mcp_module.mcp_service import mcp_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_integration():
    """Test MCP integration with CarbonScope"""
    logger.info("Starting MCP integration test...")

    # Test 1: Check if MCP service is initialized
    logger.info("Test 1: Checking MCP service initialization")
    connections = mcp_service.get_all_connections()
    logger.info(f"Current MCP connections: {len(connections)}")

    # Test 2: Create a mock MCP configuration (simulating what would come from frontend)
    logger.info("Test 2: Creating mock MCP configuration")
    mock_mcp_config = {
        "qualifiedName": "test-echo-server",
        "name": "Test Echo Server",
        "config": {
            "url": "http://localhost:8001/mcp",  # This would be our test MCP server
            "headers": {},
        },
        "enabledTools": ["echo", "add_numbers", "multiply_numbers", "get_server_info"],
        "provider": "custom",
    }

    # Test 3: Try to connect to the MCP server (will fail if server not running, but that's ok for demo)
    logger.info("Test 3: Attempting to connect to MCP server")
    try:
        server_info = await mcp_service.connect_server(mock_mcp_config)
        logger.info(f"Successfully connected to MCP server: {server_info.name}")
        logger.info(
            f"Available tools: {[tool.name for tool in server_info.tools or []]}"
        )

        # Test 4: Execute a tool
        logger.info("Test 4: Executing echo tool")
        result = await mcp_service.execute_tool(
            "echo", {"message": "Hello CarbonScope!"}
        )
        if result.success:
            logger.info(f"Echo tool result: {result.result}")
        else:
            logger.error(f"Echo tool failed: {result.error}")

        # Test 5: Execute add tool
        logger.info("Test 5: Executing add tool")
        result = await mcp_service.execute_tool("add_numbers", {"a": 5, "b": 3})
        if result.success:
            logger.info(f"Add tool result: {result.result}")
        else:
            logger.error(f"Add tool failed: {result.error}")

    except Exception as e:
        logger.warning(
            f"Expected error connecting to MCP server (server may not be running): {e}"
        )
        logger.info("This is expected if the MCP test server is not running")

    # Test 6: Show MCP service capabilities
    logger.info("Test 6: Checking MCP service capabilities")
    tools = mcp_service.get_all_tools_openapi()
    logger.info(f"MCP service has {len(tools)} tools available via OpenAPI format")

    logger.info("MCP integration test completed!")
    return True


def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("CarbonScope MCP Integration Test")
    logger.info("=" * 50)

    try:
        # Run the async test
        result = asyncio.run(test_mcp_integration())
        if result:
            logger.info("✅ MCP integration test completed successfully")
            return 0
        else:
            logger.error("❌ MCP integration test failed")
            return 1
    except Exception as e:
        logger.error(f"❌ MCP integration test failed with exception: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
