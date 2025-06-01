#!/bin/bash
# Run the TrueNAS MCP Tools Server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set production mode for MCP server
export MCP_SERVER_MODE="production"

# Path to the virtual environment
VENV_PATH="/Users/waqar/Desktop/work/ixsystems/codes/venv_tn_mcp"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH" >&2
    exit 1
fi

# Ensure Python path includes the script directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the tools server with the virtual environment Python
exec "$VENV_PATH/bin/python3" truenas_mcp_tools_server.py