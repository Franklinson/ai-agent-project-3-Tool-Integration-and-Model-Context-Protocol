# Cloud Deployment Setup

Complete guide for deploying the AI Agent MCP Server to cloud platforms with containerization, scaling, and monitoring.

## Cloud Platform Options

### AWS (Amazon Web Services)
- **Services**: ECS/EKS, EC2, Lambda
- **Best for**: Enterprise, scalability, AWS ecosystem
- **Cost**: Pay-as-you-go, reserved instances available

### Google Cloud Platform (GCP)
- **Services**: Cloud Run, GKE, Compute Engine
- **Best for**: Kubernetes, ML integration, cost efficiency
- **Cost**: Sustained use discounts, preemptible instances

### Azure
- **Services**: Container Instances, AKS, App Service
- **Best for**: Microsoft ecosystem, hybrid cloud
- **Cost**: Reserved instances, spot instances

### DigitalOcean
- **Services**: App Platform, Kubernetes, Droplets
- **Best for**: Simplicity, startups, predictable pricing
- **Cost**: Fixed monthly pricing

## Containerization with Docker

### Dockerfile Overview
Our Docker setup includes:
- Multi-stage build for optimization
- Python 3.11 slim base image
- Non-root user for security
- Health checks
- Minimal attack surface

### Build Docker Image
```bash
# Build image
docker build -f day_44/docker/Dockerfile -t mcp-server:latest .

# Build with version tag
docker build -f day_44/docker/Dockerfile -t mcp-server:1.0.0 .

# Build for specific platform
docker build --platform linux/amd64 -f day_44/docker/Dockerfile -t mcp-server:latest .
```

### Run Container Locally
```bash
# Run with default config
docker run -p 8080:8080 mcp-server:latest

# Run with custom config
docker run -p 8080:8080 -v $(pwd)/day_44/config:/app/config mcp-server:latest

# Run with environment variables
docker run -p 8080:8080 \
  -e MCP_SERVER_NAME="cloud-server" \
  -e MCP_LOG_LEVEL="DEBUG" \
  mcp-server:latest

# Run in detached mode
docker run -d -p 8080:8080 --name mcp-server mcp-server:latest
```

### Docker Compose (Optional)
```yaml
version: '3.8'
services:
  mcp-server:
    build:
      context: .
      dockerfile: day_44/docker/Dockerfile
    ports:
      - "8080:8080"
    environment:
      - MCP_SERVER_NAME=cloud-server
      - MCP_LOG_LEVEL=INFO
    volumes:
      - ./day_44/config:/app/config
      - ./day_44/logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## AWS Deployment

### Prerequisites
```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
```

### Deploy to AWS ECS (Elastic Container Service)

#### 1. Push to ECR (Elastic Container Registry)
```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name mcp-server --region us-east-1

# Tag image
docker tag mcp-server:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-server:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-server:latest
```

#### 2. Create ECS Task Definition
```json
{
  "family": "mcp-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [{
    "name": "mcp-server",
    "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-server:latest",
    "portMappings": [{
      "containerPort": 8080,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "MCP_SERVER_NAME", "value": "aws-mcp-server"},
      {"name": "MCP_LOG_LEVEL", "value": "INFO"}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/mcp-server",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
```

#### 3. Create ECS Service
```bash
aws ecs create-service \
  --cluster mcp-cluster \
  --service-name mcp-server \
  --task-definition mcp-server \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Deploy to AWS Lambda (Serverless)
```bash
# Package application
zip -r mcp-server.zip day_43/ day_44/config/ requirements.txt

# Create Lambda function
aws lambda create-function \
  --function-name mcp-server \
  --runtime python3.11 \
  --role arn:aws:iam::<account-id>:role/lambda-execution-role \
  --handler lambda_handler.handler \
  --zip-file fileb://mcp-server.zip \
  --timeout 60 \
  --memory-size 512
```

## GCP Deployment

### Prerequisites
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login
gcloud config set project <project-id>
```

### Deploy to Cloud Run

#### 1. Push to Container Registry
```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Tag image
docker tag mcp-server:latest gcr.io/<project-id>/mcp-server:latest

# Push image
docker push gcr.io/<project-id>/mcp-server:latest
```

#### 2. Deploy to Cloud Run
```bash
gcloud run deploy mcp-server \
  --image gcr.io/<project-id>/mcp-server:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars MCP_SERVER_NAME=gcp-server,MCP_LOG_LEVEL=INFO
```

### Deploy to GKE (Google Kubernetes Engine)

#### 1. Create Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: gcr.io/<project-id>/mcp-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: MCP_SERVER_NAME
          value: "gke-server"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

#### 2. Create Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mcp-server
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: mcp-server
```

## Azure Deployment

### Deploy to Azure Container Instances
```bash
# Login
az login

# Create resource group
az group create --name mcp-rg --location eastus

# Create container instance
az container create \
  --resource-group mcp-rg \
  --name mcp-server \
  --image <registry>.azurecr.io/mcp-server:latest \
  --cpu 1 \
  --memory 1 \
  --ports 8080 \
  --environment-variables MCP_SERVER_NAME=azure-server \
  --restart-policy Always
```

## DigitalOcean Deployment

### Deploy to App Platform
```bash
# Install doctl
brew install doctl  # macOS

# Authenticate
doctl auth init

# Create app
doctl apps create --spec app-spec.yaml
```

**app-spec.yaml**:
```yaml
name: mcp-server
services:
- name: mcp-server
  image:
    registry_type: DOCKER_HUB
    repository: mcp-server
    tag: latest
  instance_count: 2
  instance_size_slug: basic-xs
  http_port: 8080
  envs:
  - key: MCP_SERVER_NAME
    value: do-server
  health_check:
    http_path: /health
```

## Scaling Configuration

### Horizontal Scaling

#### AWS ECS Auto Scaling
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/mcp-cluster/mcp-server \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/mcp-cluster/mcp-server \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

**scaling-policy.json**:
```json
{
  "TargetValue": 70.0,
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
  },
  "ScaleInCooldown": 300,
  "ScaleOutCooldown": 60
}
```

#### Kubernetes HPA (Horizontal Pod Autoscaler)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Scaling
- Increase CPU/memory in task definition
- Update instance size in cloud provider
- Adjust resource limits in Kubernetes

## Monitoring Setup

### CloudWatch (AWS)

#### Create Log Group
```bash
aws logs create-log-group --log-group-name /ecs/mcp-server
```

#### Create Alarms
```bash
# CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name mcp-server-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Memory alarm
aws cloudwatch put-metric-alarm \
  --alarm-name mcp-server-high-memory \
  --alarm-description "Alert when memory exceeds 80%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### Google Cloud Monitoring

#### Create Alert Policy
```bash
gcloud alpha monitoring policies create \
  --notification-channels=<channel-id> \
  --display-name="MCP Server High CPU" \
  --condition-display-name="CPU > 80%" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s
```

### Prometheus + Grafana (Self-hosted)

#### Prometheus Configuration
```yaml
scrape_configs:
  - job_name: 'mcp-server'
    static_configs:
      - targets: ['mcp-server:8080']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

#### Grafana Dashboard
- Import dashboard for container metrics
- Create custom panels for tool invocations
- Set up alerts for error rates

### Application Performance Monitoring

#### New Relic
```python
# Add to requirements.txt
newrelic

# Initialize in application
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')
```

#### Datadog
```bash
# Add Datadog agent to Dockerfile
RUN pip install ddtrace

# Run with tracing
ddtrace-run python day_43/mcp_server.py
```

## Security Best Practices

### Container Security
- Use non-root user
- Scan images for vulnerabilities
- Keep base images updated
- Minimize image layers
- Use secrets management

### Network Security
- Use VPC/private networks
- Configure security groups
- Enable HTTPS/TLS
- Implement rate limiting
- Use API gateway

### Secrets Management

#### AWS Secrets Manager
```bash
# Store secret
aws secretsmanager create-secret \
  --name mcp-server/db-password \
  --secret-string "your-password"

# Reference in ECS task definition
"secrets": [{
  "name": "DB_PASSWORD",
  "valueFrom": "arn:aws:secretsmanager:region:account:secret:mcp-server/db-password"
}]
```

#### GCP Secret Manager
```bash
# Create secret
echo -n "your-password" | gcloud secrets create db-password --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:<service-account>" \
  --role="roles/secretmanager.secretAccessor"
```

## CI/CD Pipeline

### GitHub Actions
```yaml
name: Deploy to Cloud
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -f day_44/docker/Dockerfile -t mcp-server:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker tag mcp-server:${{ github.sha }} <registry>/mcp-server:latest
          docker push <registry>/mcp-server:latest
      
      - name: Deploy to cloud
        run: |
          # Cloud-specific deployment commands
```

## Cost Optimization

### Strategies
1. **Right-sizing**: Match resources to actual usage
2. **Auto-scaling**: Scale down during low traffic
3. **Reserved instances**: Commit for discounts
4. **Spot instances**: Use for non-critical workloads
5. **Resource limits**: Prevent runaway costs

### Monitoring Costs
- Set up billing alerts
- Use cost explorer tools
- Tag resources for tracking
- Review usage regularly

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs <container-id>

# Inspect container
docker inspect <container-id>

# Run interactively
docker run -it mcp-server:latest /bin/bash
```

### High Memory Usage
- Check for memory leaks
- Increase container memory
- Optimize code
- Enable garbage collection

### Connection Issues
- Verify security groups
- Check network configuration
- Validate DNS settings
- Test with curl/telnet

## Testing Cloud Deployment

### Load Testing
```bash
# Install Apache Bench
apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 http://<server-url>/status
```

### Health Checks
```bash
# Test health endpoint
curl http://<server-url>/health

# Test with timeout
curl --max-time 5 http://<server-url>/status
```

## Rollback Procedures

### AWS ECS
```bash
# Update service to previous task definition
aws ecs update-service \
  --cluster mcp-cluster \
  --service mcp-server \
  --task-definition mcp-server:1
```

### Kubernetes
```bash
# Rollback deployment
kubectl rollout undo deployment/mcp-server

# Check rollout status
kubectl rollout status deployment/mcp-server
```

## Backup and Disaster Recovery

### Database Backups
- Automated daily backups
- Point-in-time recovery
- Cross-region replication
- Test restore procedures

### Configuration Backups
- Version control all configs
- Store in secure location
- Document restore process
- Regular backup testing

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [AWS ECS Guide](https://docs.aws.amazon.com/ecs/)
- [GCP Cloud Run](https://cloud.google.com/run/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Local Setup Guide](local_setup.md)

## Support Checklist

- [ ] Docker image builds successfully
- [ ] Container runs locally
- [ ] Cloud credentials configured
- [ ] Image pushed to registry
- [ ] Service deployed to cloud
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Auto-scaling enabled
- [ ] Backup strategy implemented
