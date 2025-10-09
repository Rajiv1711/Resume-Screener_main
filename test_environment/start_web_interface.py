#!/usr/bin/env python3
"""
Resume Screener Test Web Interface Launcher
Easy startup script for the web-based testing interface.
"""

import os
import sys
import webbrowser
import time
from pathlib import Path

def main():
    """Launch the web interface."""
    print("🚀 Starting Resume Screener Test Web Interface")
    print("=" * 60)
    
    # Check if we're in the right directory
    current_dir = Path(__file__).parent
    web_interface_dir = current_dir / "web_interface"
    
    if not web_interface_dir.exists():
        print("❌ Error: web_interface directory not found")
        print("   Make sure you're running this from the test_environment directory")
        return
    
    # Check Flask installation
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Error: Flask is not installed")
        print("   Run: pip install flask")
        return
    
    # Check dependencies
    missing_deps = []
    try:
        import spacy
        print("✅ spaCy is available")
    except ImportError:
        missing_deps.append("spacy")
    
    try:
        import sklearn
        print("✅ scikit-learn is available")
    except ImportError:
        missing_deps.append("scikit-learn")
    
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("   The interface may not work properly without these packages")
    
    # Set working directory
    os.chdir(web_interface_dir)
    
    print("\\n📂 Working directory:", web_interface_dir)
    print("🌐 Starting Flask server...")
    print("=" * 60)
    
    print("\\n🎉 Web interface will open automatically!")
    print("\\n📋 Features available:")
    print("   • Upload resumes (PDF, DOCX, TXT)")
    print("   • Select from 3 job descriptions")
    print("   • Real-time processing with progress")
    print("   • Intelligent ranking with hybrid scoring")
    print("   • Detailed analysis and insights")
    print("   • Export results as CSV or JSON")
    print("   • No external API calls required!")
    
    print("\\n🔧 Controls:")
    print("   • Press Ctrl+C to stop the server")
    print("   • Interface runs at http://localhost:5000")
    
    print("\\n" + "=" * 60)
    
    # Start Flask app
    try:
        # Wait a moment then open browser
        import threading
        def open_browser():
            time.sleep(1.5)  # Give Flask time to start
            webbrowser.open('http://localhost:5000')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Import and run the Flask app
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\\n\\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\\n❌ Error starting server: {e}")
        print("\\nTroubleshooting:")
        print("   • Make sure port 5000 is available")
        print("   • Check that all files are in place")
        print("   • Try running: python web_interface/app.py")
    
    print("\\n👋 Thanks for using Resume Screener Test Interface!")

if __name__ == "__main__":
    main()