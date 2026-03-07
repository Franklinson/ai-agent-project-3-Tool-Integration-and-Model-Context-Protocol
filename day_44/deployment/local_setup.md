# Local Deployment Setup

Complete guide for deploying the AI Agent MCP Server on your local desktop environment.

## System Requirements

### Hardware
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Network**: Internet connection for package installation

### Software
- **OS**: macOS, Linux, or Windows 10+
- **Python**: 3.8 or higher
- **pip**: Latest version
- **Git**: For cloning repository

## Installation Steps

### 1. Clone Repository
```bash
cd ~/Desktop
git clone <repository-url>
cd "ai-agent-project-3-Tool Integration and Model Context Protocol"
```

### 2. Create Virtual Environment
```bash
# Create venv
python3 -m venv venv

# Activate venv
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import jsonschema, requests, docker; print('Dependencies OK')"
```

## Configuration

### Local Configuration File
Copy and customize the local configuration:

```bash
cp day_44/config/config.local.json day_44/config/config.json
```

Edit `config.json` with your settings:
- Server name and version
- Port and host settings
- Tool configurations
- Logging preferences

### Environment Variables (Optional)
```bash
export MCP_SERVER_NAME="local-mcp-server"
export MCP_SERVER_PORT=8080
export MCP_LOG_LEVEL="INFO"
```

## Running the Agent

### Start MCP Server
```bash
# Ensure venv is activated
source venv/bin/activate

# Run server
python day_43/mcp_server.py
```

### Interactive Mode
```python
from day_43.mcp_server import MCPServer

# Initialize
server = MCPServer("local-agent", "1.0.0")
server.start()

# Register tools
server.handle_request({
    "method": "tools/register",
    "params": {
        "tool": {
            "name": "calculator",
            "description": "Basic calculator",
            "parameters": {"expression": "string"}
        }
    }
})

# Check status
server.handle_request({"method": "status", "params": {}})
```

### Run with Custom Config
```bash
python -c "
from day_43.mcp_server import MCPServer
import json

with open('day_44/config/config.json') as f:
    config = json.load(f)

server = MCPServer(config['server']['name'], config['server']['version'])
server.start()
print('Server running...')
"
```

## Security Considerations

### Local Development
- **Network**: Server binds to localhost only by default
- **Authentication**: Not required for local development
- **File Access**: Sandbox enabled for code execution tools
- **Resource Limits**: Memory and CPU limits enforced

### Best Practices
1. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
2. **Use virtual environment**: Isolate project dependencies
3. **Validate inputs**: All tool parameters are validated
4. **Monitor resources**: Check CPU/memory usage during operation
5. **Backup data**: Regular backups of tool configurations

### Security Checklist
- [ ] Virtual environment activated
- [ ] Dependencies from requirements.txt only
- [ ] No hardcoded credentials in config
- [ ] Sandbox enabled for code execution
- [ ] Resource limits configured
- [ ] Logs reviewed for errors

## Maintenance Procedures

### Daily
- Check server logs for errors
- Monitor resource usage
- Verify tool availability

### Weekly
- Update dependencies: `pip list --outdated`
- Review and rotate logs
- Test critical tools

### Monthly
- Full dependency update
- Security audit of configurations
- Backup tool registry and configs

### Update Dependencies
```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade <package-name>

# Update all
pip install --upgrade -r requirements.txt
```

### Clear Cache
```bash
# Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# pip cache
pip cache purge
```

### Restart Server
```bash
# Stop current process (Ctrl+C)
# Reactivate venv
source venv/bin/activate
# Restart
python day_43/mcp_server.py
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Port Already in Use
**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port
lsof -i :8080
# Kill process
kill -9 <PID>
```

#### 3. Permission Denied
**Problem**: Cannot write to directory

**Solution**:
```bash
chmod +x day_43/mcp_server.py
# Or run with appropriate permissions
```

#### 4. Virtual Environment Not Found
**Problem**: `venv/bin/activate: No such file or directory`

**Solution**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Tool Registration Fails
**Problem**: Tool registration returns error

**Solution**:
- Verify tool schema matches requirements
- Check server is started
- Review error message in response

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check
```bash
python -c "
from day_43.mcp_server import MCPServer
server = MCPServer('test', '1.0.0')
response = server.start()
print('Status:', response['result']['status'])
server.stop()
"
```

## Testing Local Setup

### Run Test Suite
```bash
# Test MCP server
python day_43/test_mcp_server.py

# Test tool registry
python day_43/test_tool_registry.py

# Test request handler
python day_43/test_request_handler.py
```

### Verify Tools
```bash
python day_43/request_handler_demo.py
```

### Integration Test
```bash
python day_44/deployment/verify_setup.py
```

## Performance Optimization

### For Low-Resource Systems
- Reduce concurrent tool executions
- Increase timeout values
- Disable unused tools
- Limit log verbosity

### For High-Performance Systems
- Enable parallel tool execution
- Increase worker threads
- Enable caching
- Optimize database connections

## Uninstallation

```bash
# Deactivate venv
deactivate

# Remove virtual environment
rm -rf venv

# Remove cache
find . -type d -name "__pycache__" -exec rm -r {} +

# Optional: Remove entire project
cd ..
rm -rf "ai-agent-project-3-Tool Integration and Model Context Protocol"
```

## Additional Resources

- [MCP Server README](../day_43/README.md)
- [Tool Integration Guide](../day_31/README.md)
- [Error Handling](../day_33/README.md)
- [Quick Start Guide](../day_43/QUICKSTART.md)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test files for examples
3. Check server logs for detailed errors
4. Verify configuration matches schema
