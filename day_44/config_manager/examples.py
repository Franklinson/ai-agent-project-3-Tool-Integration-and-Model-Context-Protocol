"""Example usage of Configuration Management System."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from day_44.config_manager import ConfigManager, SecretsManager, ConfigValidator


def example_basic_usage():
    """Example 1: Basic configuration loading."""
    print("\n" + "=" * 50)
    print("Example 1: Basic Configuration Loading")
    print("=" * 50)
    
    # Initialize config manager
    cm = ConfigManager()
    
    # Load configuration (auto-detects environment)
    config = cm.load_config()
    
    print(f"Environment: {cm.environment}")
    print(f"Server Name: {cm.get('server.name')}")
    print(f"Server Port: {cm.get('server.port')}")
    print(f"Log Level: {cm.get('logging.level')}")
    print(f"Enabled Tools: {cm.get('tools.enabled')}")


def example_environment_specific():
    """Example 2: Environment-specific configuration."""
    print("\n" + "=" * 50)
    print("Example 2: Environment-Specific Configuration")
    print("=" * 50)
    
    environments = ['local', 'development', 'staging', 'production']
    
    for env in environments:
        cm = ConfigManager()
        config = cm.load_config(env)
        
        print(f"\n{env.upper()}:")
        print(f"  Server: {cm.get('server.name')}")
        print(f"  Log Level: {cm.get('logging.level')}")
        print(f"  Max Concurrent: {cm.get('tools.max_concurrent')}")
        print(f"  Memory Limit: {cm.get('resources.max_memory_mb')}MB")


def example_validation():
    """Example 3: Configuration validation."""
    print("\n" + "=" * 50)
    print("Example 3: Configuration Validation")
    print("=" * 50)
    
    cm = ConfigManager()
    config = cm.load_config('production')
    
    # Validate configuration
    errors = ConfigValidator.validate(config)
    
    if errors:
        print("❌ Configuration has errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration is valid!")
        print(f"  Server: {cm.get('server.name')}")
        print(f"  Environment: {cm.get('server.environment')}")


def example_secrets():
    """Example 4: Secrets management."""
    print("\n" + "=" * 50)
    print("Example 4: Secrets Management")
    print("=" * 50)
    
    import os
    
    # Set some test environment variables
    os.environ['DB_PASSWORD'] = 'prod_password_123'
    os.environ['API_KEY'] = 'api_key_456'
    
    sm = SecretsManager()
    
    # Get secrets (from environment)
    db_password = sm.get_secret('DB_PASSWORD', 'default')
    api_key = sm.get_secret('API_KEY', 'default')
    
    print(f"DB Password: {db_password}")
    print(f"API Key: {api_key}")
    print("\n✅ Secrets loaded from environment variables")
    
    # Cleanup
    del os.environ['DB_PASSWORD']
    del os.environ['API_KEY']


def example_dynamic_config():
    """Example 5: Dynamic configuration changes."""
    print("\n" + "=" * 50)
    print("Example 5: Dynamic Configuration")
    print("=" * 50)
    
    cm = ConfigManager()
    cm.load_config('local')
    
    print("Original Configuration:")
    print(f"  Max Concurrent: {cm.get('tools.max_concurrent')}")
    print(f"  Memory Limit: {cm.get('resources.max_memory_mb')}MB")
    
    # Modify configuration
    cm.set('tools.max_concurrent', 20)
    cm.set('resources.max_memory_mb', 2048)
    
    print("\nModified Configuration:")
    print(f"  Max Concurrent: {cm.get('tools.max_concurrent')}")
    print(f"  Memory Limit: {cm.get('resources.max_memory_mb')}MB")
    
    print("\n✅ Configuration modified dynamically")


def example_integration():
    """Example 6: Integration with MCP Server."""
    print("\n" + "=" * 50)
    print("Example 6: MCP Server Integration")
    print("=" * 50)
    
    # Load configuration
    cm = ConfigManager()
    config = cm.load_config('development')
    
    # Validate
    if cm.validate_config():
        print("✅ Configuration validated")
        
        # Extract server settings
        server_config = {
            'name': cm.get('server.name'),
            'version': cm.get('server.version'),
            'port': cm.get('server.port'),
            'host': cm.get('server.host')
        }
        
        print("\nServer Configuration:")
        for key, value in server_config.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Ready to initialize MCP Server")


def main():
    """Run all examples."""
    print("=" * 50)
    print("Configuration Management System Examples")
    print("=" * 50)
    
    examples = [
        example_basic_usage,
        example_environment_specific,
        example_validation,
        example_secrets,
        example_dynamic_config,
        example_integration
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
    
    print("\n" + "=" * 50)
    print("All Examples Complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()
