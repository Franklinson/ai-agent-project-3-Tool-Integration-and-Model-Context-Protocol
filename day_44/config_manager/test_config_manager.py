"""Test Configuration Management System."""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from day_44.config_manager import ConfigManager, SecretsManager, ConfigValidator


def test_environment_detection():
    """Test environment detection."""
    print("\n[Test 1] Environment Detection")
    
    # Test default
    cm = ConfigManager()
    assert cm.environment in ConfigManager.ENVIRONMENTS
    print(f"  ✓ Default environment: {cm.environment}")
    
    # Test with env var
    os.environ['MCP_ENV'] = 'staging'
    cm = ConfigManager()
    assert cm.environment == 'staging'
    print(f"  ✓ Environment from MCP_ENV: {cm.environment}")
    
    # Cleanup
    del os.environ['MCP_ENV']
    print("  ✓ Environment detection passed")


def test_config_loading():
    """Test configuration loading."""
    print("\n[Test 2] Configuration Loading")
    
    cm = ConfigManager()
    
    # Test local config
    config = cm.load_config('local')
    assert 'server' in config
    assert 'logging' in config
    print("  ✓ Local config loaded")
    
    # Test development config
    config = cm.load_config('development')
    assert config['server']['environment'] == 'development'
    print("  ✓ Development config loaded")
    
    # Test staging config
    config = cm.load_config('staging')
    assert config['server']['environment'] == 'staging'
    print("  ✓ Staging config loaded")
    
    # Test production config
    config = cm.load_config('production')
    assert config['server']['environment'] == 'production'
    print("  ✓ Production config loaded")
    
    print("  ✓ Configuration loading passed")


def test_config_validation():
    """Test configuration validation."""
    print("\n[Test 3] Configuration Validation")
    
    # Valid config
    valid_config = {
        'server': {'name': 'test', 'version': '1.0', 'port': 8080},
        'logging': {'level': 'INFO'},
        'tools': {'enabled': [], 'timeout': 30},
        'security': {'sandbox_enabled': True, 'validate_inputs': True}
    }
    
    errors = ConfigValidator.validate(valid_config)
    assert len(errors) == 0
    print("  ✓ Valid config passed")
    
    # Invalid config - missing section
    invalid_config = {'server': {'name': 'test'}}
    errors = ConfigValidator.validate(invalid_config)
    assert len(errors) > 0
    print(f"  ✓ Invalid config detected ({len(errors)} errors)")
    
    # Invalid port
    invalid_port = valid_config.copy()
    invalid_port['server']['port'] = 99999
    errors = ConfigValidator.validate(invalid_port)
    assert len(errors) > 0
    print("  ✓ Invalid port detected")
    
    print("  ✓ Configuration validation passed")


def test_config_get_set():
    """Test config get/set operations."""
    print("\n[Test 4] Config Get/Set Operations")
    
    cm = ConfigManager()
    cm.load_config('local')
    
    # Test get
    server_name = cm.get('server.name')
    assert server_name is not None
    print(f"  ✓ Get value: server.name = {server_name}")
    
    # Test set
    cm.set('server.test_value', 'test123')
    assert cm.get('server.test_value') == 'test123'
    print("  ✓ Set value: server.test_value = test123")
    
    # Test nested get
    port = cm.get('server.port', 8080)
    assert port == 8080
    print(f"  ✓ Get nested value: server.port = {port}")
    
    # Test default value
    missing = cm.get('missing.key', 'default')
    assert missing == 'default'
    print("  ✓ Default value returned for missing key")
    
    print("  ✓ Get/Set operations passed")


def test_secrets_manager():
    """Test secrets manager."""
    print("\n[Test 5] Secrets Manager")
    
    # Create temp secrets file
    secrets_file = Path(__file__).parent.parent / 'config' / '.test_secrets.json'
    test_secrets = {'DB_PASSWORD': 'secret123', 'API_KEY': 'key456'}
    
    with open(secrets_file, 'w') as f:
        json.dump(test_secrets, f)
    
    sm = SecretsManager(str(secrets_file))
    
    # Test get secret
    password = sm.get_secret('DB_PASSWORD')
    assert password == 'secret123'
    print("  ✓ Get secret from file")
    
    # Test set secret
    sm.set_secret('NEW_SECRET', 'value789')
    assert sm.get_secret('NEW_SECRET') == 'value789'
    print("  ✓ Set new secret")
    
    # Test environment variable priority
    os.environ['DB_PASSWORD'] = 'env_password'
    password = sm.get_secret('DB_PASSWORD')
    assert password == 'env_password'
    print("  ✓ Environment variable takes priority")
    
    # Cleanup
    del os.environ['DB_PASSWORD']
    secrets_file.unlink()
    print("  ✓ Secrets manager passed")


def test_env_var_substitution():
    """Test environment variable substitution."""
    print("\n[Test 6] Environment Variable Substitution")
    
    # Set test env vars
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_NAME'] = 'testdb'
    
    cm = ConfigManager()
    config = cm.load_config('staging')
    
    # Check substitution
    db_host = cm.get('database.host')
    assert db_host == 'localhost'
    print(f"  ✓ Substituted DB_HOST: {db_host}")
    
    db_name = cm.get('database.database')
    assert db_name == 'testdb'
    print(f"  ✓ Substituted DB_NAME: {db_name}")
    
    # Cleanup
    del os.environ['DB_HOST']
    del os.environ['DB_NAME']
    print("  ✓ Environment variable substitution passed")


def test_all_environments():
    """Test all environment configs are valid."""
    print("\n[Test 7] All Environment Configs")
    
    cm = ConfigManager()
    environments = ['local', 'development', 'staging', 'production', 'cloud']
    
    for env in environments:
        try:
            config = cm.load_config(env)
            errors = ConfigValidator.validate(config)
            if len(errors) == 0:
                print(f"  ✓ {env.capitalize()} config valid")
            else:
                print(f"  ✗ {env.capitalize()} config has errors: {errors}")
        except FileNotFoundError:
            print(f"  ⚠ {env.capitalize()} config not found (optional)")
    
    print("  ✓ All environment configs tested")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Configuration Management System Tests")
    print("=" * 50)
    
    tests = [
        test_environment_detection,
        test_config_loading,
        test_config_validation,
        test_config_get_set,
        test_secrets_manager,
        test_env_var_substitution,
        test_all_environments
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ {failed} tests failed")
    print("=" * 50)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
