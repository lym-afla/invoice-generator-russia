#!/usr/bin/env python3
"""
Windows installation helper for WeasyPrint
Downloads and installs GTK3 runtime for Windows
"""

import os
import sys
import urllib.request
import zipfile
import subprocess
from pathlib import Path

def download_gtk_runtime():
    """Download and extract GTK3 runtime for Windows"""
    print("Setting up WeasyPrint for Windows...")
    
    # For Windows, we'll use an alternative approach with reportlab
    print("\nWeasyPrint requires GTK3 runtime on Windows.")
    print("For easier setup, we can use an alternative PDF library.")
    print("\nOptions:")
    print("1. Install GTK3 runtime manually (recommended for production)")
    print("2. Use ReportLab as alternative (simpler setup)")
    
    choice = input("\nChoose option (1 or 2): ").strip()
    
    if choice == "1":
        print("\nTo install GTK3 runtime:")
        print("1. Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
        print("2. Install the latest release")
        print("3. Add GTK bin directory to PATH")
        print("4. Restart your terminal and run: python invoice_generator.py")
    elif choice == "2":
        print("\nInstalling ReportLab alternative...")
        subprocess.run([sys.executable, "-m", "pip", "install", "reportlab==4.0.8"])
        print("ReportLab installed! Use invoice_generator_reportlab.py instead.")
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    download_gtk_runtime()
