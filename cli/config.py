"""
Configuration management for the Gamaliel Prompts CLI tool.
"""

import os
from typing import Dict, Any


class Config:
    """Simple configuration manager that uses environment variables."""
    
    def __init__(self):
        self.config = self._load_from_env()
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "llm": {
                "model": os.getenv("GAMALIEL_MODEL", "gpt-4o-mini"),
                "api_key": os.getenv("OPENAI_API_KEY"),
                "max_tokens": int(os.getenv("GAMALIEL_MAX_TOKENS", "1000"))
            },
            "defaults": {
                "profile": os.getenv("GAMALIEL_PROFILE", "curious_explorer"),
                "theology": os.getenv("GAMALIEL_THEOLOGY", "default"),
                "max_words": int(os.getenv("GAMALIEL_MAX_WORDS", "300"))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.config["llm"]
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default values."""
        return self.config["defaults"]
    
    def validate(self) -> bool:
        """Validate configuration."""
        # Check required environment variables
        api_key = self.config["llm"]["api_key"]
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set")
            return False
        
        return True
