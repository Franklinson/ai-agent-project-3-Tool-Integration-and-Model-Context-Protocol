"""Secrets Manager for secure credential handling."""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class SecretsManager:
    """Manages secrets and sensitive configuration."""
    
    def __init__(self, secrets_file: Optional[str] = None):
        self.secrets_file = Path(secrets_file) if secrets_file else None
        self.secrets = {}
        if self.secrets_file and self.secrets_file.exists():
            self._load_secrets()
    
    def _load_secrets(self):
        """Load secrets from file."""
        with open(self.secrets_file) as f:
            self.secrets = json.load(f)
    
    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret from environment or file."""
        # Try environment first
        value = os.getenv(key)
        if value:
            return value
        
        # Try secrets file
        return self.secrets.get(key, default)
    
    def set_secret(self, key: str, value: Any):
        """Set secret value."""
        self.secrets[key] = value
    
    def save_secrets(self):
        """Save secrets to file."""
        if self.secrets_file:
            self.secrets_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.secrets_file, 'w') as f:
                json.dump(self.secrets, f, indent=2)
    
    def get_all_secrets(self) -> Dict[str, Any]:
        """Get all secrets."""
        return self.secrets.copy()
