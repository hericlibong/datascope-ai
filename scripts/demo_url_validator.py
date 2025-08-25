#!/usr/bin/env python3
"""
Demo script to show URL validation functionality.
This script can be run to demonstrate the URL validator in action.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from the module to avoid ai_engine init issues
from ai_engine.url_validator import URLValidator, ValidationStatus

def demo_url_validation():
    """Demonstrate URL validation with various types of URLs."""
    print("=== DataScope AI - URL Validator Demo ===\n")
    
    validator = URLValidator(timeout=5)
    
    test_urls = [
        "https://www.eurostat.eu/",  # Should work (real EU statistics site)
        "https://httpbin.org/status/200",  # Should work (test service)
        "https://httpbin.org/status/404",  # Should return 404
        "https://httpbin.org/redirect/3",  # Should redirect
        "https://nonexistent-site-for-testing-12345.com",  # Should fail to connect
        "invalid-url",  # Invalid format
        "",  # Empty URL
        "http://httpbin.org/status/500",  # Server error
    ]
    
    print("Testing various URLs:\n")
    
    for i, url in enumerate(test_urls, 1):
        print(f"{i}. Testing: {url[:50]}{'...' if len(url) > 50 else ''}")
        
        try:
            result = validator.validate_url(url)
            print(f"   Status: {result.status.value}")
            
            if result.final_url and result.final_url != url:
                print(f"   Final URL: {result.final_url}")
            
            if result.status_code:
                print(f"   HTTP Code: {result.status_code}")
            
            if result.error_message:
                print(f"   Error: {result.error_message}")
            
            if result.redirected_from:
                print(f"   Redirected from: {result.redirected_from}")
                
        except Exception as e:
            print(f"   Unexpected error: {e}")
        
        print()
    
    print("=== Accessibility Check Demo ===\n")
    
    accessible_count = 0
    for url in test_urls[:4]:  # Test first 4 URLs for accessibility
        is_accessible = validator.is_url_accessible(url)
        status = "✓ Accessible" if is_accessible else "✗ Not accessible"
        print(f"{status}: {url}")
        if is_accessible:
            accessible_count += 1
    
    print(f"\nSummary: {accessible_count} out of 4 URLs are accessible")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo_url_validation()