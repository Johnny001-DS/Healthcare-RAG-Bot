#!/usr/bin/env python3
"""
Test Runner Script

This script runs all test files in the tests/ directory.
It provides a comprehensive overview of the system health.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_test_file(test_file_path):
    """Run a single test file and return the result"""
    test_name = os.path.basename(test_file_path)
    print(f"\n{'='*60}")
    print(f"🧪 Running: {test_name}")
    print(f"{'='*60}")
    
    try:
        # Change to project root to ensure relative imports work
        project_root = Path(__file__).parent
        
        # Run the test file
        result = subprocess.run(
            [sys.executable, test_file_path],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per test
        )
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        return success, test_name
        
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name}: TIMEOUT (exceeded 2 minutes)")
        return False, test_name
    except Exception as e:
        print(f"❌ {test_name}: ERROR - {str(e)}")
        return False, test_name

def main():
    """Run all tests in the tests directory"""
    print("🚀 RAG-LLM Healthcare Insurance Test Suite")
    print("=" * 60)
    
    # Get the tests directory
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        sys.exit(1)
    
    # Find all test files
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found in tests/ directory!")
        sys.exit(1)
    
    print(f"Found {len(test_files)} test files:")
    for test_file in sorted(test_files):
        print(f"  - {test_file.name}")
    
    # Run tests with specific order for logical flow
    test_order = [
        "test_s3_connection.py",
        "test_bedrock_simple.py", 
        "test_embedding_regions.py",
        "test_nova_converse.py",
        "test_boto3.py",
        "test_admin_embedding.py",
        "test_user_interface.py",
        "test_bulk_processing.py",
        "test_complete_system.py"
    ]
    
    results = []
    start_time = time.time()
    
    # Run tests in the specified order
    for test_name in test_order:
        test_path = tests_dir / test_name
        if test_path.exists():
            success, name = run_test_file(test_path)
            results.append((name, success))
        else:
            print(f"⚠️  Test file {test_name} not found, skipping...")
    
    # Run any remaining test files not in the order list
    remaining_tests = [f for f in test_files if f.name not in test_order]
    for test_file in remaining_tests:
        success, name = run_test_file(test_file)
        results.append((name, success))
    
    # Print summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Duration: {duration:.2f} seconds")
    print()
    
    # Show detailed results
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name:<35} {status}")
    
    print("\n" + "="*60)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Your RAG system is ready to go!")
        print("\nYou can now run:")
        print("  🔧 Admin Interface: streamlit run Admin/admin.py --server.port 8501")
        print("  👤 User Interface:  streamlit run User/app.py --server.port 8502")
    else:
        print(f"⚠️  {failed} test(s) failed. Please check the output above for details.")
        print("\nTroubleshooting tips:")
        print("1. Ensure your .env file has correct AWS credentials")
        print("2. Check that you have access to required AWS services")
        print("3. Verify your AWS region supports the required services")
        print("4. Make sure all dependencies are installed: pip install -r requirements.txt")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
