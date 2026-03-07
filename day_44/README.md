# Day 44 - Deployment Setup

Complete deployment configuration and documentation for the MCP Server, covering both local and cloud deployments.

## Contents

### Documentation
- **[local_setup.md](deployment/local_setup.md)** - Local deployment guide
  - System requirements
  - Installation steps
  - Configuration guide
  - Security considerations
  - Maintenance procedures
  - Troubleshooting

- **[cloud_setup.md](deployment/cloud_setup.md)** - Cloud deployment guide
  - Cloud platform setup (AWS, GCP, Azure, DigitalOcean)
  - Containerization with Docker
  - Deployment strategies
  - Scaling configuration
  - Monitoring and alerting

### Configuration
- **[config.local.json](config/config.local.json)** - Local configuration template
  - Server settings
  - Tool configurations
  - Security options
  - Resource limits

- **[config.cloud.json](config/config.cloud.json)** - Cloud configuration template
  - Production settings
  - Cloud-specific options
  - Scaling parameters
  - Monitoring configuration

### Scripts

#### Local Deployment
- **[setup.sh](deployment/setup.sh)** - Automated local setup
- **[verify_setup.py](deployment/verify_setup.py)** - Setup verification
- **[start_server.py](deployment/start_server.py)** - Server launcher

#### Cloud Deployment
- **[Dockerfile](docker/Dockerfile)** - Production container
- **[docker-compose.yml](docker/docker-compose.yml)** - Multi-container setup
- **[kubernetes.yaml](docker/kubernetes.yaml)** - Kubernetes manifests
- **[build.sh](docker/build.sh)** - Docker build script
- **[deploy-aws.sh](docker/deploy-aws.sh)** - AWS deployment
- **[deploy-gcp.sh](docker/deploy-gcp.sh)** - GCP deployment

## Quick Start

### Local Deployment

#### Automated Setup
```bash
cd day_44/deployment
./setup.sh
```

#### Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy configuration
cp day_44/config/config.local.json day_44/config/config.json

# Verify setup
python day_44/deployment/verify_setup.py
```

#### Verify Installation
```bash
source venv/bin/activate
python day_44/deployment/verify_setup.py
```

Expected output:
```
✓ Python 3.x.x
✓ jsonschema
✓ requests
✓ docker
✓ Configuration loaded
✓ MCP Server module
✓ Server start/stop
Results: 5/5 checks passed
```

#### Run Server
```bash
source venv/bin/activate
python day_44/deployment/start_server.py
```

### Cloud Deployment

#### Build Docker Image
```bash
# Build image
docker build -f day_44/docker/Dockerfile -t mcp-server:latest .

# Or use build script
./day_44/docker/build.sh
```

#### Run with Docker
```bash
# Simple run
docker run -p 8080:8080 mcp-server:latest

# With Docker Compose
cd day_44/docker
docker-compose up -d
```

#### Deploy to AWS
```bash
export AWS_REGION=us-east-1
./day_44/docker/deploy-aws.sh
```

#### Deploy to GCP
```bash
export GCP_PROJECT=your-project-id
./day_44/docker/deploy-gcp.sh
```

#### Deploy to Kubernetes
```bash
kubectl apply -f day_44/docker/kubernetes.yaml
```

## Configuration Options

### Local Configuration
Edit `day_44/config/config.local.json`:

```json
{
  "server": {
    "name": "local-mcp-server",
    "port": 8080
  },
  "tools": {
    "enabled": ["calculator", "web_search"],
    "timeout": 30
  },
  "security": {
    "sandbox_enabled": true
  }
}
```

### Cloud Configuration
Edit `day_44/config/config.cloud.json`:

```json
{
  "server": {
    "name": "cloud-mcp-server",
    "host": "0.0.0.0",
    "port": 8080
  },
  "scaling": {
    "auto_scale": true,
    "min_instances": 2,
    "max_instances": 10
  },
  "monitoring": {
    "enabled": true,
    "prometheus_enabled": true
  }
}
```

## Directory Structure

```
day_44/
├── deployment/
│   ├── local_setup.md      # Local deployment docs
│   ├── cloud_setup.md      # Cloud deployment docs
│   ├── setup.sh            # Local setup script
│   ├── verify_setup.py     # Verification tool
│   └── start_server.py     # Server launcher
├── docker/
│   ├── Dockerfile          # Production container
│   ├── docker-compose.yml  # Multi-container setup
│   ├── kubernetes.yaml     # K8s manifests
│   ├── prometheus.yml      # Monitoring config
│   ├── build.sh            # Build script
│   ├── deploy-aws.sh       # AWS deployment
│   ├── deploy-gcp.sh       # GCP deployment
│   ├── github-actions.yml  # CI/CD pipeline
│   └── README.md           # Docker docs
├── config/
│   ├── config.local.json   # Local config
│   └── config.cloud.json   # Cloud config
├── logs/                   # Created on first run
├── data/                   # Created on first run
├── README.md               # This file
└── SUMMARY.md              # Completion summary
```

## Deployment Comparison

| Feature | Local | Docker | AWS ECS | GCP Cloud Run | Kubernetes |
|---------|-------|--------|---------|---------------|------------|
| Setup Time | 5 min | 10 min | 30 min | 20 min | 45 min |
| Scalability | Manual | Limited | Auto | Auto | Auto |
| Cost | Free | Free | Pay-as-go | Pay-as-go | Variable |
| Complexity | Low | Medium | Medium | Low | High |
| Best For | Dev | Testing | Production | Serverless | Enterprise |

## Testing

### Local Testing
```bash
# Test MCP server
python day_43/test_mcp_server.py

# Test with configuration
python -c "
import json
from day_43.mcp_server import MCPServer

with open('day_44/config/config.local.json') as f:
    config = json.load(f)

server = MCPServer(config['server']['name'], config['server']['version'])
print(server.start())
"
```

### Docker Testing
```bash
# Build and test
./day_44/docker/build.sh

# Test with docker-compose
cd day_44/docker
docker-compose up -d
docker-compose logs -f mcp-server
```

## Troubleshooting

### Local Issues
See [local_setup.md](deployment/local_setup.md#troubleshooting) for detailed guide.

Common issues:
- **Import errors**: Activate venv and reinstall dependencies
- **Port in use**: Change port in config or kill existing process
- **Permission denied**: Make scripts executable with `chmod +x`

### Docker Issues
See [cloud_setup.md](deployment/cloud_setup.md#troubleshooting) for detailed guide.

Common issues:
- **Build fails**: Clean cache with `docker builder prune`
- **Container won't start**: Check logs with `docker logs <container-id>`
- **Connection issues**: Verify port mappings and network settings

## Next Steps

### For Local Development
1. Review [local_setup.md](deployment/local_setup.md)
2. Run verification: `python day_44/deployment/verify_setup.py`
3. Start server: `python day_44/deployment/start_server.py`
4. Register tools and test functionality

### For Cloud Deployment
1. Review [cloud_setup.md](deployment/cloud_setup.md)
2. Build Docker image: `./day_44/docker/build.sh`
3. Test locally with Docker
4. Deploy to cloud platform
5. Configure monitoring and alerts

## Resources

- [Local Setup Guide](deployment/local_setup.md)
- [Cloud Setup Guide](deployment/cloud_setup.md)
- [Docker Documentation](docker/README.md)
- [MCP Server Documentation](../day_43/README.md)
- [Quick Start Guide](../day_43/QUICKSTART.md)
- [Tool Integration](../day_31/README.md)
- [Error Handling](../day_33/README.md)


## Configuration Management

### Overview
Complete configuration management system with environment detection, secrets handling, and validation.

### Quick Start
```python
from day_44.config_manager import ConfigManager

# Load configuration
cm = ConfigManager()
config = cm.load_config()
cm.validate_config()

# Get values
server_name = cm.get('server.name')
port = cm.get('server.port')
```

### Features
- **Environment Detection**: Auto-detect from MCP_ENV variable
- **Config Loading**: Dynamic loading per environment
- **Secrets Management**: Secure credential handling
- **Validation**: Schema-based validation
- **Variable Substitution**: ${VAR} replacement

### Environments
- local, development, staging, production, cloud

### Documentation
See [config_manager/README.md](config_manager/README.md) for complete documentation.

### Testing
```bash
python day_44/config_manager/test_config_manager.py
```
