"""Configuration Validator."""

from typing import Dict, Any, List


class ConfigValidator:
    """Validates configuration against schema."""
    
    REQUIRED_FIELDS = {
        'server': ['name', 'version', 'port'],
        'logging': ['level'],
        'tools': ['enabled', 'timeout'],
        'security': ['sandbox_enabled', 'validate_inputs']
    }
    
    @staticmethod
    def validate(config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return errors."""
        errors = []
        
        # Check required sections
        for section in ConfigValidator.REQUIRED_FIELDS:
            if section not in config:
                errors.append(f"Missing required section: {section}")
                continue
            
            # Check required fields in section
            for field in ConfigValidator.REQUIRED_FIELDS[section]:
                if field not in config[section]:
                    errors.append(f"Missing required field: {section}.{field}")
        
        # Validate types
        if 'server' in config:
            if 'port' in config['server']:
                port = config['server']['port']
                if not isinstance(port, int) or port < 1 or port > 65535:
                    errors.append("server.port must be integer between 1-65535")
        
        if 'logging' in config:
            if 'level' in config['logging']:
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if config['logging']['level'] not in valid_levels:
                    errors.append(f"logging.level must be one of {valid_levels}")
        
        if 'tools' in config:
            if 'timeout' in config['tools']:
                if not isinstance(config['tools']['timeout'], (int, float)):
                    errors.append("tools.timeout must be a number")
        
        return errors
    
    @staticmethod
    def is_valid(config: Dict[str, Any]) -> bool:
        """Check if configuration is valid."""
        return len(ConfigValidator.validate(config)) == 0
