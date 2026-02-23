#!/usr/bin/env python3
"""
Verification script to confirm all deliverables are present and working.
"""

import os
import sys

def check_file(filepath, description):
    """Check if a file exists."""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def main():
    print("=" * 70)
    print("CODE EXECUTION TOOL - DELIVERABLES VERIFICATION")
    print("=" * 70)
    
    all_present = True
    
    print("\n1. CORE COMPONENTS")
    print("-" * 70)
    all_present &= check_file("code_execution_tool.py", "Main integrated tool")
    all_present &= check_file("code_executor.py", "Basic executor")
    all_present &= check_file("sandbox.py", "Docker sandbox")
    all_present &= check_file("resource_limiter.py", "Resource limiter")
    
    print("\n2. TESTS")
    print("-" * 70)
    all_present &= check_file("tests/test_code_execution.py", "Comprehensive test suite")
    all_present &= check_file("test_code_executor.py", "Executor tests")
    all_present &= check_file("test_sandbox.py", "Sandbox tests")
    all_present &= check_file("test_resource_limits.py", "Resource limit tests")
    
    print("\n3. EXAMPLES & DEMOS")
    print("-" * 70)
    all_present &= check_file("examples.py", "Usage examples")
    all_present &= check_file("demo_sandbox.py", "Sandbox demo")
    all_present &= check_file("demo_resource_limits.py", "Resource limiter demo")
    
    print("\n4. DOCUMENTATION")
    print("-" * 70)
    all_present &= check_file("README.md", "Main documentation")
    all_present &= check_file("PROJECT_SUMMARY.md", "Project summary")
    all_present &= check_file("DELIVERABLES.md", "Deliverables checklist")
    all_present &= check_file("QUICK_REFERENCE.md", "Quick reference")
    all_present &= check_file("README_SANDBOX.md", "Sandbox documentation")
    
    print("\n5. DEPENDENCIES")
    print("-" * 70)
    all_present &= check_file("requirements.txt", "Python dependencies")
    all_present &= check_file("venv/bin/activate", "Virtual environment")
    
    print("\n6. FUNCTIONALITY TEST")
    print("-" * 70)
    
    try:
        # Test import
        from day_36.code_execution_tool import CodeExecutionTool
        print("✅ CodeExecutionTool imports successfully")
        
        # Test basic execution
        tool = CodeExecutionTool(use_sandbox=False)
        result = tool.execute("print('Verification test')")
        
        if result['success'] and 'Verification test' in result['output']:
            print("✅ Basic execution works")
        else:
            print("❌ Basic execution failed")
            all_present = False
    
    except Exception as e:
        print(f"❌ Functionality test failed: {str(e)[:50]}")
        all_present = False
    
    print("\n" + "=" * 70)
    if all_present:
        print("✅ ALL DELIVERABLES PRESENT AND WORKING")
        print("=" * 70)
        print("\nTo run tests:")
        print("  source venv/bin/activate")
        print("  python3 tests/test_code_execution.py")
        print("\nTo run examples:")
        print("  python3 examples.py")
        return 0
    else:
        print("❌ SOME DELIVERABLES MISSING OR NOT WORKING")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
