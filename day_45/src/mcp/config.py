"""
Cache Configuration
Defines configurable TTL, size limits, and eviction policies.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class CacheConfig:
    """Cache configuration settings"""
    
    # TTL settings (in seconds)
    tool_metadata_ttl: float = 600  # 10 minutes
    discovery_ttl: float = 300       # 5 minutes
    response_ttl: float = 60         # 1 minute
    
    # Size limits
    max_size: int = 1000
    max_metadata_size: int = 1000
    max_discovery_size: int = 500
    max_response_size: int = 2000
    
    # Eviction policy
    eviction_policy: str = "lru"  # lru, lfu, fifo
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tool_metadata_ttl": self.tool_metadata_ttl,
            "discovery_ttl": self.discovery_ttl,
            "response_ttl": self.response_ttl,
            "max_size": self.max_size
        }


# Predefined configurations
CACHE_CONFIGS = {
    "default": CacheConfig(),
    
    "aggressive": CacheConfig(
        tool_metadata_ttl=1800,  # 30 minutes
        discovery_ttl=900,       # 15 minutes
        response_ttl=300,        # 5 minutes
        max_size=5000
    ),
    
    "minimal": CacheConfig(
        tool_metadata_ttl=60,    # 1 minute
        discovery_ttl=30,        # 30 seconds
        response_ttl=10,         # 10 seconds
        max_size=100
    ),
    
    "no_response_cache": CacheConfig(
        tool_metadata_ttl=600,
        discovery_ttl=300,
        response_ttl=0,          # No response caching
        max_size=1000
    )
}


def get_cache_config(profile: str = "default") -> Dict[str, Any]:
    """Get cache configuration by profile name"""
    config = CACHE_CONFIGS.get(profile, CACHE_CONFIGS["default"])
    return config.to_dict()
