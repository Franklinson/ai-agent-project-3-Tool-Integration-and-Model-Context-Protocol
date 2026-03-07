# Multi-stage Dockerfile for MCP Server
# Optimized for production cloud deployment

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Metadata
LABEL maintainer="MCP Server Team"
LABEL description="AI Agent MCP Server for cloud deployment"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    MCP_SERVER_NAME="cloud-mcp-server" \
    MCP_SERVER_PORT=8080 \
    MCP_LOG_LEVEL="INFO"

# Create non-root user
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/mcpuser/.local

# Copy application code
COPY day_43/ /app/day_43/
COPY day_44/config/ /app/config/
COPY day_31/ /app/day_31/
COPY day_33/ /app/day_33/

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Add local bin to PATH
ENV PATH=/home/mcpuser/.local/bin:$PATH

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/day_43'); from mcp_server import MCPServer; server = MCPServer(); response = server.start(); sys.exit(0 if response['result']['status'] == 'success' else 1); server.stop()"

# Run the application
CMD ["python", "-c", "import sys; sys.path.insert(0, '/app/day_43'); from mcp_server import MCPServer; import json; server = MCPServer('cloud-mcp-server', '1.0.0'); server.start(); print('Server running on port 8080...'); import time; [time.sleep(1) for _ in iter(int, 1)]"]
