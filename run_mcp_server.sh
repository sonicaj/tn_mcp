#!/bin/bash
# Wrapper script for running the TrueNAS MCP server with proper environment

# Set environment variables
export PYTHONPATH="/Users/waqar/Desktop/work/ixsystems/codes/tn_mcp"
export MCP_SERVER_MODE="production"

# Use the virtual environment Python
exec /Users/waqar/Desktop/work/ixsystems/codes/venv_tn_mcp/bin/python3 \
    /Users/waqar/Desktop/work/ixsystems/codes/tn_mcp/truenas_mcp_server.py