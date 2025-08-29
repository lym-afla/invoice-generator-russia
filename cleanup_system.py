#!/usr/bin/env python3
"""
Script to uninstall project dependencies from system Python
Run this AFTER setting up virtual environment
"""

import subprocess
import sys

# Dependencies that were installed for this project
DEPENDENCIES_TO_REMOVE = [
    "weasyprint",
    "reportlab", 
    "Jinja2",
    "qrcode",
    "Pillow",
    "babel",
    "num2words",
    "python-dateutil",
    
    # Dependencies of the above
    "pydyf",
    "cffi",
    "html5lib",
    "tinycss2",
    "cssselect2",
    "Pyphen",
    "fonttools",
    "MarkupSafe",
    "typing-extensions",
    "pypng",
    "colorama",
    "docopt",
    "six",
    "chardet",
    "webencodings",
    "brotli",
    "zopfli",
    "pycparser"
]

def uninstall_dependencies():
    """Uninstall dependencies from system Python"""
    print("🧹 Cleaning up system Python dependencies...")
    print("⚠️  This will uninstall packages that were installed for this project")
    print("   from your system Python installation.")
    print()
    
    choice = input("Continue? (y/N): ").strip().lower()
    if choice not in ['y', 'yes']:
        print("❌ Cleanup cancelled.")
        return
    
    for package in DEPENDENCIES_TO_REMOVE:
        try:
            print(f"🗑️  Uninstalling {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'uninstall', package, '-y'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Uninstalled {package}")
            else:
                print(f"ℹ️  {package} not found or already uninstalled")
                
        except Exception as e:
            print(f"⚠️  Error uninstalling {package}: {e}")
    
    print()
    print("✅ System cleanup completed!")
    print("💡 Use the virtual environment from now on:")
    print("   Windows: .\\venv\\Scripts\\activate")
    print("   Linux/Mac: source venv/bin/activate")

if __name__ == "__main__":
    uninstall_dependencies()
