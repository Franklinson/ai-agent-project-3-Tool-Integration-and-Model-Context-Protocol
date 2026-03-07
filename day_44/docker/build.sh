#!/bin/bash
# Docker Build and Test Script

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "Docker Build and Test"
echo "=========================================="

# Configuration
IMAGE_NAME="mcp-server"
IMAGE_TAG="${1:-latest}"
DOCKERFILE="day_44/docker/Dockerfile"
CONTAINER_NAME="mcp-server-test"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗${NC} Docker not found. Please install Docker."
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker found"

# Build image
echo -e "\n[1/5] Building Docker image..."
if docker build -f "$DOCKERFILE" -t "$IMAGE_NAME:$IMAGE_TAG" .; then
    echo -e "${GREEN}✓${NC} Image built successfully"
else
    echo -e "${RED}✗${NC} Build failed"
    exit 1
fi

# Check image size
echo -e "\n[2/5] Checking image size..."
IMAGE_SIZE=$(docker images "$IMAGE_NAME:$IMAGE_TAG" --format "{{.Size}}")
echo -e "${GREEN}✓${NC} Image size: $IMAGE_SIZE"

# Scan for vulnerabilities (if trivy is installed)
echo -e "\n[3/5] Security scan..."
if command -v trivy &> /dev/null; then
    trivy image --severity HIGH,CRITICAL "$IMAGE_NAME:$IMAGE_TAG"
else
    echo -e "${YELLOW}⚠${NC} Trivy not installed, skipping security scan"
fi

# Run container
echo -e "\n[4/5] Starting container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
if docker run -d --name "$CONTAINER_NAME" -p 8080:8080 "$IMAGE_NAME:$IMAGE_TAG"; then
    echo -e "${GREEN}✓${NC} Container started"
else
    echo -e "${RED}✗${NC} Failed to start container"
    exit 1
fi

# Wait for container to be ready
echo "Waiting for container to be ready..."
sleep 5

# Test container
echo -e "\n[5/5] Testing container..."
CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME")
if [ "$CONTAINER_STATUS" = "running" ]; then
    echo -e "${GREEN}✓${NC} Container is running"
else
    echo -e "${RED}✗${NC} Container is not running"
    docker logs "$CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME"
    exit 1
fi

# Check logs
echo -e "\nContainer logs:"
docker logs "$CONTAINER_NAME" | head -20

# Test health (if health endpoint exists)
echo -e "\nTesting connectivity..."
if curl -f http://localhost:8080 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Server is responding"
else
    echo -e "${YELLOW}⚠${NC} Server not responding (may be expected)"
fi

# Cleanup
echo -e "\nCleaning up..."
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null
echo -e "${GREEN}✓${NC} Cleanup complete"

# Summary
echo -e "\n=========================================="
echo -e "${GREEN}Build and Test Complete!${NC}"
echo "=========================================="
echo ""
echo "Image: $IMAGE_NAME:$IMAGE_TAG"
echo "Size: $IMAGE_SIZE"
echo ""
echo "To run the container:"
echo "  docker run -d -p 8080:8080 $IMAGE_NAME:$IMAGE_TAG"
echo ""
echo "To push to registry:"
echo "  docker tag $IMAGE_NAME:$IMAGE_TAG <registry>/$IMAGE_NAME:$IMAGE_TAG"
echo "  docker push <registry>/$IMAGE_NAME:$IMAGE_TAG"
