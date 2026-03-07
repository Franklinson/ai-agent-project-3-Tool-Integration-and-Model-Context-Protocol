"""Configuration Manager for MCP Server."""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages configuration for different environments."""
    
    ENVIRONMENTS = ['local', 'development', 'staging', 'production', 'cloud']
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or self._get_default_config_dir())
        self.environment = self._detect_environment()
        self.config = {}
        self.secrets = {}
    
    def _get_default_config_dir(self) -> str:
        """Get default config directory."""
        return str(Path(__file__).parent.parent / 'config')
    
    def _detect_environment(self) -> str:
        """Detect current environment."""
        env = os.getenv('MCP_ENV', os.getenv('ENVIRONMENT', 'local')).lower()
        return env if env in self.ENVIRONMENTS else 'local'
    
    def load_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration for environment."""
        env = environment or self.environment
        config_file = self.config_dir / f'config.{env}.json'
        
        if not config_file.exists():
            config_file = self.config_dir / 'config.json'
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file) as f:
            self.config = json.load(f)
        
        self._load_secrets()
        self._substitute_env_vars()
        return self.config
    
    def _load_secrets(self):
        """Load secrets from environment or file."""
        secrets_file = self.config_dir / '.secrets.json'
        if secrets_file.exists():
            with open(secrets_file) as f:
                self.secrets = json.load(f)
    
    def _substitute_env_vars(self):
        """Replace ${VAR} with environment variables."""
        self.config = self._recursive_substitute(self.config)
    
    def _recursive_substitute(self, obj):
        """Recursively substitute environment variables."""
        if isinstance(obj, dict):
            return {k: self._recursive_substitute(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._recursive_substitute(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            var_name = obj[2:-1]
            return os.getenv(var_name, self.secrets.get(var_name, obj))
        return obj
    
    def validate_config(self) -> bool:
        """Validate configuration."""
        required = ['server', 'logging', 'tools', 'security']
        for key in required:
            if key not in self.config:
                raise ValueError(f"Missing required config section: {key}")
        
        if 'name' not in self.config['server']:
            raise ValueError("Missing server.name in config")
        
        if 'port' not in self.config['server']:
            raise ValueError("Missing server.port in config")
        
        return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot notation."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set config value by dot notation."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
    
    def save_config(self, environment: Optional[str] = None):
        """Save current config to file."""
        env = environment or self.environment
        config_file = self.config_dir / f'config.{env}.json'
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
