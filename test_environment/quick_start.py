#!/usr/bin/env python3
"""
Quick Start Script for Resume Screener Test Environment
Checks dependencies and runs a basic test to get you started.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("🧪 RESUME SCREENER TEST ENVIRONMENT")
    print("   Quick Start & Dependency Check")
    print("=" * 60)

def check_python_version():
    """Check Python version."""
    print("\n🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_and_install_packages():
    """Check and optionally install required packages."""
    print("\n📦 Checking Python packages...")
    
    required_packages = {
        'spacy': 'spacy',
        'sklearn': 'scikit-learn',
        'numpy': 'numpy'
    }
    
    missing_packages = []
    
    for import_name, pip_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {pip_name} - Installed")
        except ImportError:
            print(f"❌ {pip_name} - Missing")
            missing_packages.append(pip_name)
    
    # Check spaCy model separately
    spacy_model_available = True
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ en_core_web_sm - Available")
    except:
        print("❌ en_core_web_sm - Missing")
        spacy_model_available = False
    
    if missing_packages or not spacy_model_available:
        print(f"\n⚠️  Missing dependencies detected!")
        
        if missing_packages:
            install_cmd = f"pip install {' '.join(missing_packages)}"
            print(f"\n📥 To install missing packages, run:")
            print(f"   {install_cmd}")
        
        if not spacy_model_available:
            print(f"\n📥 To install spaCy model, run:")
            print(f"   python -m spacy download en_core_web_sm")
        
        response = input("\n❓ Would you like to install them automatically? (y/n): ").lower()
        
        if response == 'y':
            print("\n🔄 Installing packages...")
            try:
                if missing_packages:
                    subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
                
                if not spacy_model_available:
                    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
                
                print("✅ Installation completed!")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Installation failed: {e}")
                return False
        else:
            print("\n⚠️  Please install missing dependencies manually and run this script again.")
            return False
    
    return True

def check_test_data():
    """Check if test data files exist."""
    print("\n📁 Checking test data files...")
    
    base_path = Path(__file__).parent
    mock_data_path = base_path / "mock_data"
    
    required_files = [
        "sample_resume_1.txt",
        "sample_resume_2.txt", 
        "sample_resume_3.txt",
        "job_descriptions.json"
    ]
    
    missing_files = []
    
    for file_name in required_files:
        file_path = mock_data_path / file_name
        if file_path.exists():
            print(f"✅ {file_name} - Found")
        else:
            print(f"❌ {file_name} - Missing")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"⚠️  Missing test files: {', '.join(missing_files)}")
        return False
    
    return True

def run_quick_test():
    """Run a quick test to verify everything works."""
    print("\n🧪 Running quick test...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Import and run a simple parser test
        from backend_tests.test_parser import TestParser
        
        parser = TestParser()
        
        # Test with just one resume
        test_file = Path(__file__).parent / "mock_data" / "sample_resume_1.txt"
        
        if test_file.exists():
            result = parser.parse_resume(str(test_file))
            
            print("✅ Quick test completed!")
            print(f"   📄 Parsed: {result['file']}")
            print(f"   👤 Name: {result['parsed'].get('name', 'N/A')}")
            print(f"   📧 Email: {result['parsed'].get('email', 'N/A')}")
            print(f"   🔧 Skills found: {len(result['parsed'].get('skills', []))}")
            
            return True
        else:
            print("❌ Test file not found")
            return False
            
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def show_next_steps():
    """Show next steps to user."""
    print("\n🎉 SETUP COMPLETE!")
    print("\n🚀 Next Steps:")
    print("   1. Run full test suite:")
    print("      python scripts/run_backend_tests.py")
    print("")
    print("   2. Or run individual tests:")
    print("      python backend_tests/test_parser.py")
    print("      python backend_tests/test_embedder.py") 
    print("      python backend_tests/test_ranker.py")
    print("")
    print("   3. For Windows users:")
    print("      Double-click: scripts/run_tests.bat")
    print("")
    print("   4. Read the full documentation:")
    print("      Open: README.md")
    print("")
    print("Happy testing! 🧪✨")

def main():
    """Main setup flow."""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Incompatible Python version")
        input("Press Enter to exit...")
        return
    
    # Step 2: Check and install packages
    if not check_and_install_packages():
        print("\n❌ Setup failed: Missing dependencies")
        input("Press Enter to exit...")
        return
    
    # Step 3: Check test data
    if not check_test_data():
        print("\n❌ Setup failed: Missing test data files")
        print("   This might indicate the test environment wasn't set up correctly.")
        input("Press Enter to exit...")
        return
    
    # Step 4: Run quick test
    if not run_quick_test():
        print("\n⚠️  Quick test failed, but setup appears complete.")
        print("   Try running the full test suite manually.")
    
    # Step 5: Show next steps
    show_next_steps()
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()