"""
Model Adapter Factory

Factory for creating model adapters from configuration.
"""

import os
from typing import Optional, Dict, Any

from modelfang.adapters.base import ModelAdapter
from modelfang.adapters.groq_adapter import GroqAdapter
from modelfang.adapters.gemini_adapter import GeminiAdapter
from modelfang.config.loader import ModelConfig


class AdapterFactory:
    """Factory for creating model adapters."""
    
    @staticmethod
    def create(config: ModelConfig) -> ModelAdapter:
        """
        Create an adapter instance from a model configuration.
        
        Args:
            config: Model configuration object
            
        Returns:
            Configured ModelAdapter instance
            
        Raises:
            ValueError: If provider is not supported
        """
        api_key = None
        if config.api_key_env:
            api_key = os.environ.get(config.api_key_env)
            
        if not api_key:
            # Try to infer default env var logic if not explicitly set
            if config.provider == "groq":
                api_key = os.environ.get("GROQ_API_KEY")
            elif config.provider == "google":
                api_key = os.environ.get("GEMINI_API_KEY")
        
        # Determine provider class
        provider = config.provider.lower()
        
        if provider == "groq":
            return GroqAdapter(
                model_name=config.model_name,
                api_key=api_key,
                timeout_seconds=config.timeout_seconds,
                **config.extra_params
            )
        elif provider == "google" or provider == "gemini":
            return GeminiAdapter(
                model_name=config.model_name,
                api_key=api_key,
                timeout_seconds=config.timeout_seconds,
                **config.extra_params
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
