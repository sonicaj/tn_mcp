#!/bin/bash
# Startup script for TrueNAS MCP Server

# Activate virtual environment
source /Users/waqar/Desktop/work/ixsystems/codes/venv_tn_mcp/bin/activate

# Run the server
exec python truenas_mcp_server.py