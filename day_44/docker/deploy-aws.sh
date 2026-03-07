#!/bin/bash
# AWS ECS Deployment Script

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPOSITORY="mcp-server"
ECS_CLUSTER="mcp-cluster"
ECS_SERVICE="mcp-server"
IMAGE_TAG="${1:-latest}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "AWS ECS Deployment"
echo "=========================================="

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}✗${NC} AWS CLI not found"
    exit 1
fi
echo -e "${GREEN}✓${NC} AWS CLI found"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "Region: $AWS_REGION"

# ECR repository URL
ECR_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"

# Step 1: Authenticate Docker to ECR
echo -e "\n[1/5] Authenticating to ECR..."
aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
echo -e "${GREEN}✓${NC} Authenticated"

# Step 2: Create ECR repository if it doesn't exist
echo -e "\n[2/5] Checking ECR repository..."
if ! aws ecr describe-repositories --repository-names "$ECR_REPOSITORY" --region "$AWS_REGION" &>/dev/null; then
    echo "Creating repository..."
    aws ecr create-repository \
        --repository-name "$ECR_REPOSITORY" \
        --region "$AWS_REGION" \
        --image-scanning-configuration scanOnPush=true
    echo -e "${GREEN}✓${NC} Repository created"
else
    echo -e "${GREEN}✓${NC} Repository exists"
fi

# Step 3: Build and tag image
echo -e "\n[3/5] Building Docker image..."
docker build -f day_44/docker/Dockerfile -t "$ECR_REPOSITORY:$IMAGE_TAG" .
docker tag "$ECR_REPOSITORY:$IMAGE_TAG" "$ECR_URL:$IMAGE_TAG"
docker tag "$ECR_REPOSITORY:$IMAGE_TAG" "$ECR_URL:latest"
echo -e "${GREEN}✓${NC} Image built and tagged"

# Step 4: Push to ECR
echo -e "\n[4/5] Pushing to ECR..."
docker push "$ECR_URL:$IMAGE_TAG"
docker push "$ECR_URL:latest"
echo -e "${GREEN}✓${NC} Image pushed"

# Step 5: Update ECS service
echo -e "\n[5/5] Updating ECS service..."
if aws ecs describe-services --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE" --region "$AWS_REGION" &>/dev/null; then
    aws ecs update-service \
        --cluster "$ECS_CLUSTER" \
        --service "$ECS_SERVICE" \
        --force-new-deployment \
        --region "$AWS_REGION" >/dev/null
    echo -e "${GREEN}✓${NC} Service updated"
else
    echo -e "${YELLOW}⚠${NC} Service not found. Create it manually or use CloudFormation."
fi

echo -e "\n=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Image: $ECR_URL:$IMAGE_TAG"
echo "Cluster: $ECS_CLUSTER"
echo "Service: $ECS_SERVICE"
echo ""
echo "To check deployment status:"
echo "  aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE"
