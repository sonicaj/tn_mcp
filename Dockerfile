# TrueNAS MCP Server Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY truenas_mcp_server.py .
COPY truenas_mcp_tools_server.py .
COPY run_middleware_tests.sh .
RUN chmod +x run_middleware_tests.sh

# Copy test files
COPY tests/ ./tests/
COPY pytest.ini .

# Copy docs directory (will be overridden by volume mount in most cases)
COPY docs/ ./docs/

# Set Python to run in unbuffered mode for better stdio handling
ENV PYTHONUNBUFFERED=1

# MCP servers communicate via stdio
CMD ["python", "truenas_mcp_server.py"]