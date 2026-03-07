#!/bin/bash
# Local Setup Script for MCP Server

set -e

echo "=========================================="
echo "MCP Server Local Setup"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python
echo -e "\n[1/6] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo -e "\n[2/6] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment exists"
fi

# Activate virtual environment
echo -e "\n[3/6] Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Install dependencies
echo -e "\n[4/6] Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create directories
echo -e "\n[5/6] Creating directories..."
mkdir -p day_44/logs
mkdir -p day_44/data
echo -e "${GREEN}✓${NC} Directories created"

# Copy config
echo -e "\n[6/6] Setting up configuration..."
if [ ! -f "day_44/config/config.json" ]; then
    cp day_44/config/config.local.json day_44/config/config.json
    echo -e "${GREEN}✓${NC} Configuration file created"
else
    echo -e "${GREEN}✓${NC} Configuration file exists"
fi

# Verify setup
echo -e "\n=========================================="
echo "Running verification..."
echo "=========================================="
python day_44/deployment/verify_setup.py

echo -e "\n=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "To start the server:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Run server: python day_43/mcp_server.py"
echo ""
echo "For more info, see: day_44/deployment/local_setup.md"
