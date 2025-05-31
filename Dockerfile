# TrueNAS MCP Server Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY truenas_mcp_server.py .
COPY test_server.py .

# Copy docs directory (will be overridden by volume mount in most cases)
COPY docs/ ./docs/

# Set Python to run in unbuffered mode for better stdio handling
ENV PYTHONUNBUFFERED=1

# MCP servers communicate via stdio
CMD ["python", "truenas_mcp_server.py"]