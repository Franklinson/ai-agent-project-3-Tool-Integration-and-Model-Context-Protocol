#!/bin/bash
# GCP Cloud Run Deployment Script

set -e

# Configuration
GCP_PROJECT="${GCP_PROJECT:-your-project-id}"
GCP_REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="mcp-server"
IMAGE_TAG="${1:-latest}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "GCP Cloud Run Deployment"
echo "=========================================="

# Check gcloud CLI
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}✗${NC} gcloud CLI not found"
    exit 1
fi
echo -e "${GREEN}✓${NC} gcloud CLI found"

# Set project
gcloud config set project "$GCP_PROJECT"
echo "Project: $GCP_PROJECT"
echo "Region: $GCP_REGION"

# GCR image URL
GCR_URL="gcr.io/$GCP_PROJECT/$SERVICE_NAME"

# Step 1: Configure Docker for GCR
echo -e "\n[1/4] Configuring Docker for GCR..."
gcloud auth configure-docker
echo -e "${GREEN}✓${NC} Docker configured"

# Step 2: Build and tag image
echo -e "\n[2/4] Building Docker image..."
docker build -f day_44/docker/Dockerfile -t "$SERVICE_NAME:$IMAGE_TAG" .
docker tag "$SERVICE_NAME:$IMAGE_TAG" "$GCR_URL:$IMAGE_TAG"
docker tag "$SERVICE_NAME:$IMAGE_TAG" "$GCR_URL:latest"
echo -e "${GREEN}✓${NC} Image built and tagged"

# Step 3: Push to GCR
echo -e "\n[3/4] Pushing to GCR..."
docker push "$GCR_URL:$IMAGE_TAG"
docker push "$GCR_URL:latest"
echo -e "${GREEN}✓${NC} Image pushed"

# Step 4: Deploy to Cloud Run
echo -e "\n[4/4] Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$GCR_URL:$IMAGE_TAG" \
    --platform managed \
    --region "$GCP_REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 1 \
    --max-instances 10 \
    --set-env-vars "MCP_SERVER_NAME=gcp-server,MCP_LOG_LEVEL=INFO" \
    --timeout 300

echo -e "${GREEN}✓${NC} Deployed to Cloud Run"

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform managed \
    --region "$GCP_REGION" \
    --format 'value(status.url)')

echo -e "\n=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Image: $GCR_URL:$IMAGE_TAG"
echo "Service: $SERVICE_NAME"
echo "URL: $SERVICE_URL"
echo ""
echo "To test the service:"
echo "  curl $SERVICE_URL/health"
