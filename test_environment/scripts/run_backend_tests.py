#!/usr/bin/env python3
"""
Backend Test Runner
Runs all backend component tests (parser, embedder, ranker) with mock services.
"""

import os
import sys
import time
import traceback
from pathlib import Path

# Add project paths
script_dir = Path(__file__).parent
test_env_dir = script_dir.parent
project_root = test_env_dir.parent

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(test_env_dir))

def print_header(title):
    """Print a formatted header."""
    print("\\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section header."""
    print(f"\\n🧪 {title}")
    print("-" * 40)

def run_parser_test():
    """Run parser component test."""
    print_section("Testing Parser Component")
    try:
        # Import and run parser test
        from backend_tests.test_parser import main as test_parser_main
        
        start_time = time.time()
        results = test_parser_main()
        duration = time.time() - start_time
        
        print(f"✅ Parser test completed in {duration:.2f} seconds")
        return {"status": "success", "duration": duration, "results": results}
        
    except Exception as e:
        print(f"❌ Parser test failed: {str(e)}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

def run_embedder_test():
    """Run embedder component test."""
    print_section("Testing Embedder Component")
    try:
        # Import and run embedder test
        from backend_tests.test_embedder import main as test_embedder_main
        
        start_time = time.time()
        results = test_embedder_main()
        duration = time.time() - start_time
        
        print(f"✅ Embedder test completed in {duration:.2f} seconds")
        return {"status": "success", "duration": duration, "results": results}
        
    except Exception as e:
        print(f"❌ Embedder test failed: {str(e)}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

def run_ranker_test():
    """Run ranker component test."""
    print_section("Testing Ranker Component")
    try:
        # Import and run ranker test
        from backend_tests.test_ranker import main as test_ranker_main
        
        start_time = time.time()
        results = test_ranker_main()
        duration = time.time() - start_time
        
        print(f"✅ Ranker test completed in {duration:.2f} seconds")
        return {"status": "success", "duration": duration, "results": results}
        
    except Exception as e:
        print(f"❌ Ranker test failed: {str(e)}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

def run_integrated_test():
    """Run an integrated test using all components together."""
    print_section("Running Integrated Test")
    try:
        from backend_tests.test_parser import TestParser
        from backend_tests.test_ranker import TestRanker
        import json
        
        start_time = time.time()
        
        # Initialize components
        parser = TestParser()
        ranker = TestRanker()
        
        print("📄 Parsing sample resumes...")
        parsed_resumes = parser.test_sample_resumes()
        
        print("📊 Loading job descriptions...")
        job_desc_file = test_env_dir / "mock_data" / "job_descriptions.json"
        with open(job_desc_file, 'r') as f:
            job_descriptions = json.load(f)
        
        print("🎯 Ranking resumes for all job descriptions...")
        integrated_results = {}
        
        for job_key, job_data in job_descriptions.items():
            print(f"  - Testing: {job_data['title']}")
            ranked_results = ranker.rank_resumes(
                parsed_resumes, 
                job_data['description']
            )
            
            integrated_results[job_key] = {
                "job_title": job_data['title'],
                "top_resume": ranked_results[0] if ranked_results else None,
                "total_ranked": len([r for r in ranked_results if "error" not in r])
            }
        
        duration = time.time() - start_time
        
        print(f"✅ Integrated test completed in {duration:.2f} seconds")
        print("\\n📋 Integrated Test Summary:")
        for job_key, result in integrated_results.items():
            if result["top_resume"] and "error" not in result["top_resume"]:
                print(f"  - {result['job_title']}: {result['top_resume']['file']} " +
                      f"(Score: {result['top_resume'].get('hybrid_score', 'N/A')})")
            else:
                print(f"  - {result['job_title']}: No valid results")
        
        return {
            "status": "success", 
            "duration": duration, 
            "results": integrated_results
        }
        
    except Exception as e:
        print(f"❌ Integrated test failed: {str(e)}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

def check_dependencies():
    """Check if required dependencies are available."""
    print_section("Checking Dependencies")
    
    required_packages = [
        "spacy", "sklearn", "numpy", "re"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - Available")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    # Special check for spacy model
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ en_core_web_sm - Available")
    except Exception:
        print("❌ en_core_web_sm - Missing (run: python -m spacy download en_core_web_sm)")
        missing_packages.append("en_core_web_sm")
    
    if missing_packages:
        print(f"\\n⚠️  Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("\\n✅ All dependencies are available!")
        return True

def main():
    """Run all backend tests."""
    print_header("Resume Screener Backend Test Suite")
    
    # Check dependencies first
    if not check_dependencies():
        print("\\n❌ Please install missing dependencies before running tests.")
        return
    
    # Test results storage
    test_results = {
        "parser": None,
        "embedder": None,
        "ranker": None,
        "integrated": None
    }
    
    # Run individual component tests
    test_results["parser"] = run_parser_test()
    test_results["embedder"] = run_embedder_test()
    test_results["ranker"] = run_ranker_test()
    
    # Run integrated test if individual tests passed
    individual_tests_passed = all(
        result and result.get("status") == "success" 
        for result in [test_results["parser"], test_results["embedder"], test_results["ranker"]]
    )
    
    if individual_tests_passed:
        test_results["integrated"] = run_integrated_test()
    else:
        print_section("Skipping Integrated Test")
        print("⚠️  Some individual tests failed. Skipping integrated test.")
    
    # Print final summary
    print_header("Test Results Summary")
    
    total_duration = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_name, result in test_results.items():
        if result:
            status_icon = "✅" if result.get("status") == "success" else "❌"
            duration = result.get("duration", 0)
            total_duration += duration
            
            if result.get("status") == "success":
                passed_tests += 1
            else:
                failed_tests += 1
            
            print(f"{status_icon} {test_name.capitalize()} Test: " +
                  f"{result.get('status', 'unknown')} ({duration:.2f}s)")
        else:
            print(f"⚠️  {test_name.capitalize()} Test: Skipped")
    
    print(f"\\n📊 Overall Results:")
    print(f"   • Tests Passed: {passed_tests}")
    print(f"   • Tests Failed: {failed_tests}")
    print(f"   • Total Duration: {total_duration:.2f} seconds")
    
    success_rate = (passed_tests / (passed_tests + failed_tests)) * 100 if (passed_tests + failed_tests) > 0 else 0
    print(f"   • Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\\n🎉 All tests passed! Your ML components are working correctly with mock services.")
    elif success_rate >= 75:
        print("\\n✅ Most tests passed! Check the failed tests for any issues.")
    else:
        print("\\n⚠️  Several tests failed. Please review the error messages above.")
    
    return test_results

if __name__ == "__main__":
    main()