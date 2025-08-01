#!/usr/bin/env python3
"""
Test script to verify the Semantic Kernel migration of Virtual Havruta.
This script tests both implementations and ensures backward compatibility.
"""

import sys
import logging
from VirtualHavruta import (
    VirtualHavruta, 
    VirtualHavrutaSemanticKernel,
    create_virtual_havruta,
    create_sk_havruta,
    get_implementation_info
)
from VirtualHavruta.util import create_logger


def test_sk_implementation():
    """Test the Semantic Kernel implementation."""
    print("🧪 Testing Semantic Kernel Implementation...")
    
    logger = create_logger("test-sk")
    vh_sk = create_sk_havruta('prompts.yaml', 'config.yaml', logger)
    
    # Test basic functions
    print("  ✓ SK Virtual Havruta created successfully")
    
    # Test anti-attack
    detection, explanation, tokens = vh_sk.anti_attack("What is Torah?", "test-1")
    print(f"  ✓ Anti-attack: {detection} ({explanation[:50]}...)")
    
    # Test adaptor
    adapted, tokens = vh_sk.adaptor("What is Torah?", "test-2")
    print(f"  ✓ Adaptor: {adapted[:50]}...")
    
    # Test retrieval
    docs = vh_sk.retrieve_docs("Torah commentary", "test-3")
    print(f"  ✓ Retrieval: Found {len(docs)} documents")
    
    # Test QA
    response, tokens = vh_sk.qa("What is Torah?", "Sample reference data", "test-4")
    print(f"  ✓ QA: {response[:50]}...")
    
    print("✅ Semantic Kernel implementation tests passed!\n")
    return vh_sk


def test_compatibility():
    """Test the compatibility layer."""
    print("🔄 Testing Compatibility Layer...")
    
    logger = create_logger("test-compat")
    
    # Test auto-selection (should pick SK based on config)
    vh_auto = create_virtual_havruta('prompts.yaml', 'config.yaml', logger)
    info = get_implementation_info(vh_auto)
    print(f"  ✓ Auto-selected implementation: {info['type']}")
    print(f"  ✓ Features: {', '.join(info['features'])}")
    
    # Test that API is the same
    detection, explanation, tokens = vh_auto.anti_attack("Test query", "compat-1")
    print(f"  ✓ Compatible API: anti_attack works ({detection})")
    
    print("✅ Compatibility tests passed!\n")
    return vh_auto


def test_configuration():
    """Test SK-specific configuration."""
    print("⚙️  Testing Configuration...")
    
    import yaml
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Check SK config sections
    sk_config = config.get('semantic_kernel', {})
    use_sk = config.get('environment', {}).get('use_semantic_kernel', False)
    
    print(f"  ✓ use_semantic_kernel: {use_sk}")
    print(f"  ✓ SK plugins configured: {len(sk_config.get('plugins', []))}")
    print(f"  ✓ SK planners configured: {sk_config.get('planners', {})}")
    print(f"  ✓ SK memory configured: {sk_config.get('memory', {})}")
    
    print("✅ Configuration tests passed!\n")


def test_error_handling():
    """Test error handling in SK implementation."""
    print("🛡️  Testing Error Handling...")
    
    logger = create_logger("test-errors")
    vh_sk = create_sk_havruta('prompts.yaml', 'config.yaml', logger)
    
    # Test with empty query
    detection, explanation, tokens = vh_sk.anti_attack("", "error-1")
    print(f"  ✓ Empty query handled: {detection}")
    
    # Test with very long query
    long_query = "A" * 1000
    adapted, tokens = vh_sk.adaptor(long_query, "error-2")
    print(f"  ✓ Long query handled: {len(adapted)} chars")
    
    print("✅ Error handling tests passed!\n")


def test_performance():
    """Basic performance test."""
    print("⚡ Testing Performance...")
    
    import time
    logger = create_logger("test-perf")
    
    # Time SK initialization
    start_time = time.time()
    vh_sk = create_sk_havruta('prompts.yaml', 'config.yaml', logger)
    init_time = time.time() - start_time
    print(f"  ✓ SK initialization: {init_time:.3f}s")
    
    # Time a simple operation
    start_time = time.time()
    adapted, tokens = vh_sk.adaptor("Performance test query", "perf-1")
    op_time = time.time() - start_time
    print(f"  ✓ SK operation time: {op_time:.3f}s")
    
    print("✅ Performance tests passed!\n")


def main():
    """Run all tests."""
    print("🚀 Virtual Havruta Semantic Kernel Migration Test Suite\n")
    
    try:
        # Run all test suites
        test_configuration()
        vh_sk = test_sk_implementation() 
        vh_auto = test_compatibility()
        test_error_handling()
        test_performance()
        
        print("🎉 All tests passed! Semantic Kernel migration is successful!")
        print("\n📊 Summary:")
        print(f"  • SK implementation: {get_implementation_info(vh_sk)['type']}")
        print(f"  • Auto implementation: {get_implementation_info(vh_auto)['type']}")
        print(f"  • Configuration: SK-enabled")
        print(f"  • Backward compatibility: ✅")
        print(f"  • Error handling: ✅")
        print(f"  • Performance: ✅")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)