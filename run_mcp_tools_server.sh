#!/bin/bash
# Run the TrueNAS MCP Tools Server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set production mode for MCP server
export MCP_SERVER_MODE="production"

# Run the tools server
exec python "$SCRIPT_DIR/truenas_mcp_tools_server.py"