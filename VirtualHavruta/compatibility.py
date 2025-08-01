"""
Compatibility layer for smooth transition between LangChain and Semantic Kernel implementations.
This module provides factory functions and compatibility utilities.
"""

import logging
import yaml
from typing import Union

# Import both implementations
from VirtualHavruta.vh import VirtualHavruta
from VirtualHavruta.sk_orchestrator import VirtualHavrutaSemanticKernel, create_sk_havruta


def create_virtual_havruta(
    prompts_file: str, 
    config_file: str, 
    logger: logging.Logger,
    force_implementation: str = None
) -> Union[VirtualHavruta, VirtualHavrutaSemanticKernel]:
    """
    Factory function to create Virtual Havruta instance based on configuration.
    
    Args:
        prompts_file: Path to prompts YAML file
        config_file: Path to configuration YAML file
        logger: Logger instance
        force_implementation: Force specific implementation ('langchain' or 'semantic_kernel')
        
    Returns:
        Virtual Havruta instance (either LangChain or SK-based)
    """
    # Load configuration to check which implementation to use
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Determine which implementation to use
    use_sk = config.get("environment", {}).get("use_semantic_kernel", True)
    
    if force_implementation:
        use_sk = force_implementation.lower() == "semantic_kernel"
    
    if use_sk:
        logger.info("[FACTORY] Creating Semantic Kernel-based Virtual Havruta")
        return create_sk_havruta(prompts_file, config_file, logger)
    else:
        logger.info("[FACTORY] Creating LangChain-based Virtual Havruta")
        return VirtualHavruta(prompts_file, config_file, logger)


class VirtualHavrutaAdapter:
    """
    Adapter class that provides a unified interface for both implementations.
    This ensures complete API compatibility regardless of the underlying implementation.
    """
    
    def __init__(self, prompts_file: str, config_file: str, logger: logging.Logger):
        """Initialize the adapter with auto-detection of implementation."""
        self._impl = create_virtual_havruta(prompts_file, config_file, logger)
        self._is_sk = isinstance(self._impl, VirtualHavrutaSemanticKernel)
        
    def __getattr__(self, name):
        """Delegate all method calls to the underlying implementation."""
        return getattr(self._impl, name)
    
    @property
    def implementation_type(self) -> str:
        """Return the type of implementation being used."""
        return "semantic_kernel" if self._is_sk else "langchain"
    
    def switch_implementation(self, target: str):
        """
        Switch between implementations at runtime.
        
        Args:
            target: Target implementation ('langchain' or 'semantic_kernel')
        """
        if target.lower() not in ['langchain', 'semantic_kernel']:
            raise ValueError("Target must be 'langchain' or 'semantic_kernel'")
        
        current_type = self.implementation_type
        if current_type != target.lower():
            # Re-initialize with target implementation
            # Note: This would need the original constructor parameters
            # For now, just log the request
            self._impl.logger.info(f"[ADAPTER] Switch requested from {current_type} to {target}")


def get_implementation_info(vh_instance) -> dict:
    """
    Get information about the Virtual Havruta implementation.
    
    Args:
        vh_instance: Virtual Havruta instance
        
    Returns:
        Dictionary with implementation information
    """
    is_sk = isinstance(vh_instance, VirtualHavrutaSemanticKernel)
    is_adapter = isinstance(vh_instance, VirtualHavrutaAdapter)
    
    info = {
        "type": "semantic_kernel" if is_sk else "langchain",
        "is_adapter": is_adapter,
        "class_name": vh_instance.__class__.__name__,
        "features": []
    }
    
    if is_sk:
        info["features"].extend([
            "SK Plugins",
            "SK Memory Stores", 
            "SK Planners",
            "Enhanced Orchestration"
        ])
    else:
        info["features"].extend([
            "LangChain Chains",
            "Neo4j Vector Search",
            "Traditional RAG Pipeline"
        ])
    
    return info


# Backward compatibility aliases
VH = VirtualHavruta  # Original implementation
VHSK = VirtualHavrutaSemanticKernel  # SK implementation
VHAdapter = VirtualHavrutaAdapter  # Adaptive implementation

# Factory functions for convenience
create_langchain_vh = lambda p, c, l: VirtualHavruta(p, c, l)
create_sk_vh = create_sk_havruta
create_adaptive_vh = lambda p, c, l: VirtualHavrutaAdapter(p, c, l)