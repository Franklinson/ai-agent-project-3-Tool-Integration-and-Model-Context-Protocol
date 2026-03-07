# Configuration Management System

Complete configuration management for the MCP Server with environment-specific configs, secrets management, validation, and dynamic loading.

## Overview

The configuration management system provides:
- **Environment Detection**: Automatic detection of deployment environment
- **Config Loading**: Dynamic loading of environment-specific configurations
- **Secrets Management**: Secure handling of sensitive credentials
- **Validation**: Schema-based configuration validation
- **Variable Substitution**: Environment variable replacement

## Components

### ConfigManager
Main configuration manager with environment detection and loading.

### SecretsManager
Secure secrets handling with environment variable priority.

### ConfigValidator
Schema-based validation for configuration files.

## Supported Environments

- **local**: Local development (default)
- **development**: Development environment
- **staging**: Staging/pre-production
- **production**: Production deployment
- **cloud**: Cloud-specific configuration

## Usage

### Basic Usage

```python
from day_44.config_manager import ConfigManager

# Initialize (auto-detects environment)
cm = ConfigManager()

# Load configuration
config = cm.load_config()

# Validate configuration
cm.validate_config()

# Get values
server_name = cm.get('server.name')
port = cm.get('server.port', 8080)

# Set values
cm.set('server.debug', True)
```

### Environment-Specific Loading

```python
# Load specific environment
config = cm.load_config('production')

# Or set environment variable
import os
os.environ['MCP_ENV'] = 'staging'
cm = ConfigManager()
config = cm.load_config()  # Loads staging config
```

### Secrets Management

```python
from day_44.config_manager import SecretsManager

# Initialize with secrets file
sm = SecretsManager('config/.secrets.json')

# Get secret (checks env vars first)
db_password = sm.get_secret('DB_PASSWORD')
api_key = sm.get_secret('API_KEY', 'default_key')

# Set secret
sm.set_secret('NEW_SECRET', 'value')
sm.save_secrets()
```

### Configuration Validation

```python
from day_44.config_manager import ConfigValidator

# Validate configuration
errors = ConfigValidator.validate(config)

if errors:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Configuration is valid")

# Quick validation
is_valid = ConfigValidator.is_valid(config)
```

## Configuration Files

### File Naming Convention
```
config/
├── config.local.json          # Local development
├── config.development.json    # Development environment
├── config.staging.json        # Staging environment
├── config.production.json     # Production environment
├── config.cloud.json          # Cloud deployment
└── .secrets.json              # Secrets (gitignored)
```

### Configuration Structure

```json
{
  "server": {
    "name": "mcp-server",
    "version": "1.0.0",
    "host": "localhost",
    "port": 8080,
    "environment": "local"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(message)s",
    "file": "logs/server.log",
    "console": true
  },
  "tools": {
    "enabled": ["calculator", "web_search"],
    "timeout": 30,
    "max_concurrent": 5
  },
  "security": {
    "sandbox_enabled": true,
    "validate_inputs": true,
    "allowed_hosts": ["localhost"]
  },
  "resources": {
    "max_memory_mb": 512,
    "max_cpu_percent": 50
  },
  "database": {
    "host": "${DB_HOST}",
    "password": "${DB_PASSWORD}"
  }
}
```

## Environment Variables

### Setting Environment

```bash
# Set environment
export MCP_ENV=production

# Or use ENVIRONMENT
export ENVIRONMENT=staging
```

### Variable Substitution

Configuration values with `${VAR_NAME}` are replaced with environment variables:

```json
{
  "database": {
    "host": "${DB_HOST}",
    "password": "${DB_PASSWORD}"
  }
}
```

```bash
# Set environment variables
export DB_HOST=localhost
export DB_PASSWORD=secret123

# Variables are automatically substituted when config loads
```

## Required Configuration Fields

### Server Section
- `name`: Server name (string)
- `version`: Server version (string)
- `port`: Port number (integer, 1-65535)

### Logging Section
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Tools Section
- `enabled`: List of enabled tools (array)
- `timeout`: Tool timeout in seconds (number)

### Security Section
- `sandbox_enabled`: Enable sandboxing (boolean)
- `validate_inputs`: Enable input validation (boolean)

## Environment Comparison

| Feature | Local | Development | Staging | Production |
|---------|-------|-------------|---------|------------|
| Log Level | INFO | DEBUG | INFO | WARNING |
| Console Logs | Yes | Yes | Yes | No |
| Sandbox | Yes | Yes | Yes | Yes |
| Max Concurrent | 5 | 5 | 10 | 20 |
| Memory Limit | 512MB | 512MB | 768MB | 1GB |
| Auto-scaling | No | No | No | Yes |
| Monitoring | Basic | Basic | Full | Full |

## Secrets Management

### Secrets File Format

```json
{
  "DB_PASSWORD": "secret123",
  "API_KEY": "key456",
  "REDIS_PASSWORD": "redis789"
}
```

### Priority Order

1. **Environment Variables** (highest priority)
2. **Secrets File** (.secrets.json)
3. **Default Value** (lowest priority)

### Best Practices

1. **Never commit secrets** - Add `.secrets.json` to `.gitignore`
2. **Use environment variables** in production
3. **Rotate secrets regularly**
4. **Use cloud secret managers** (AWS Secrets Manager, GCP Secret Manager)
5. **Encrypt secrets at rest**

## Validation Rules

### Port Validation
- Must be integer
- Range: 1-65535

### Log Level Validation
- Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Timeout Validation
- Must be a number (int or float)
- Should be positive

### Required Sections
- server
- logging
- tools
- security

## Examples

### Example 1: Load and Use Config

```python
from day_44.config_manager import ConfigManager

# Initialize
cm = ConfigManager()
config = cm.load_config('production')

# Validate
if cm.validate_config():
    print("Config valid!")
    
    # Use configuration
    server_name = cm.get('server.name')
    port = cm.get('server.port')
    log_level = cm.get('logging.level')
    
    print(f"Starting {server_name} on port {port}")
```

### Example 2: Environment-Specific Behavior

```python
from day_44.config_manager import ConfigManager

cm = ConfigManager()
config = cm.load_config()

if cm.environment == 'production':
    # Production-specific setup
    enable_monitoring()
    disable_debug_mode()
elif cm.environment == 'development':
    # Development-specific setup
    enable_debug_mode()
    enable_hot_reload()
```

### Example 3: Dynamic Configuration

```python
from day_44.config_manager import ConfigManager

cm = ConfigManager()
cm.load_config()

# Modify configuration at runtime
if high_load_detected():
    cm.set('tools.max_concurrent', 30)
    cm.set('resources.max_memory_mb', 2048)

# Save modified config
cm.save_config('production')
```

### Example 4: Secrets with Fallback

```python
from day_44.config_manager import SecretsManager

sm = SecretsManager('config/.secrets.json')

# Get with fallback
db_password = sm.get_secret('DB_PASSWORD', 'default_password')
api_key = sm.get_secret('API_KEY', 'test_key')

# Use in application
connect_to_database(password=db_password)
```

## Testing

### Run Tests

```bash
# Run all tests
python day_44/config_manager/test_config_manager.py

# With specific environment
MCP_ENV=staging python day_44/config_manager/test_config_manager.py
```

### Test Coverage

- Environment detection
- Configuration loading (all environments)
- Configuration validation
- Get/Set operations
- Secrets management
- Environment variable substitution
- All environment configs validation

## Integration with MCP Server

```python
from day_43.mcp_server import MCPServer
from day_44.config_manager import ConfigManager

# Load configuration
cm = ConfigManager()
config = cm.load_config()

# Validate
cm.validate_config()

# Initialize server with config
server = MCPServer(
    server_name=cm.get('server.name'),
    version=cm.get('server.version')
)

# Start server
server.start()
```

## Troubleshooting

### Config File Not Found
```
FileNotFoundError: Config file not found
```
**Solution**: Ensure config file exists for the environment, or create `config.json` as fallback.

### Validation Errors
```
ValueError: Missing required field: server.port
```
**Solution**: Add missing fields to configuration file.

### Environment Variable Not Substituted
```
Database host is still ${DB_HOST}
```
**Solution**: Set environment variable before loading config:
```bash
export DB_HOST=localhost
```

### Secrets Not Loading
```
Secret returns None
```
**Solution**: 
1. Check `.secrets.json` exists
2. Verify secret key name
3. Set environment variable as fallback

## Security Considerations

1. **Never commit secrets** to version control
2. **Use environment variables** in production
3. **Restrict file permissions** on secrets files (chmod 600)
4. **Rotate secrets regularly**
5. **Use cloud secret managers** for production
6. **Audit secret access**
7. **Encrypt secrets at rest**

## Best Practices

1. **Use environment-specific configs** for different deployments
2. **Validate configuration** before starting server
3. **Use environment variables** for secrets
4. **Document all configuration options**
5. **Test configuration changes** before deployment
6. **Version control configs** (except secrets)
7. **Use defaults** for optional settings
8. **Monitor configuration changes**

## API Reference

### ConfigManager

#### Methods
- `__init__(config_dir)`: Initialize manager
- `load_config(environment)`: Load configuration
- `validate_config()`: Validate configuration
- `get(key, default)`: Get config value
- `set(key, value)`: Set config value
- `save_config(environment)`: Save configuration

#### Properties
- `environment`: Current environment
- `config`: Loaded configuration
- `config_dir`: Configuration directory

### SecretsManager

#### Methods
- `__init__(secrets_file)`: Initialize manager
- `get_secret(key, default)`: Get secret value
- `set_secret(key, value)`: Set secret value
- `save_secrets()`: Save secrets to file
- `get_all_secrets()`: Get all secrets

### ConfigValidator

#### Methods
- `validate(config)`: Validate and return errors
- `is_valid(config)`: Check if valid

## Additional Resources

- [Local Setup Guide](../deployment/local_setup.md)
- [Cloud Setup Guide](../deployment/cloud_setup.md)
- [MCP Server Documentation](../../day_43/README.md)
