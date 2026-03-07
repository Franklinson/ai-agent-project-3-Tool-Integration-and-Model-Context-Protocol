#!/usr/bin/env python3
"""Verify local setup is correctly configured."""

import sys
import os
import json
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    print(f"✗ Python {version.major}.{version.minor} (3.8+ required)")
    return False

def check_dependencies():
    """Check required dependencies."""
    required = ['jsonschema', 'requests', 'docker', 'click']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing.append(package)
    
    return len(missing) == 0

def check_config():
    """Check configuration file."""
    config_path = Path(__file__).parent.parent / 'config' / 'config.local.json'
    
    if not config_path.exists():
        print(f"✗ Config file not found: {config_path}")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        print(f"✓ Configuration loaded")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def check_mcp_server():
    """Check MCP server can be imported."""
    try:
        # Add day_43 to path for relative imports
        day_43_path = str(Path(__file__).parent.parent.parent / 'day_43')
        if day_43_path not in sys.path:
            sys.path.insert(0, day_43_path)
        
        from mcp_server import MCPServer
        print("✓ MCP Server module")
        return True
    except ImportError as e:
        print(f"✗ MCP Server import failed: {e}")
        return False

def test_server():
    """Test server initialization."""
    try:
        # Add day_43 to path for relative imports
        day_43_path = str(Path(__file__).parent.parent.parent / 'day_43')
        if day_43_path not in sys.path:
            sys.path.insert(0, day_43_path)
        
        from mcp_server import MCPServer
        
        server = MCPServer("test-server", "1.0.0")
        response = server.start()
        
        if response['result']['status'] == 'success':
            print("✓ Server start/stop")
            server.stop()
            return True
        else:
            print("✗ Server failed to start")
            return False
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 50)
    print("Local Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("MCP Server Module", check_mcp_server),
        ("Server Functionality", test_server)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        results.append(check_func())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ Setup verified successfully!")
        return 0
    else:
        print("✗ Setup incomplete. Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
