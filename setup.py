#!/usr/bin/env python3
"""
Setup script for Invoice Generator
Handles installation and configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    
    # Determine which requirements file to use
    if sys.platform.startswith('win'):
        requirements_file = 'requirements_windows.txt'
        print("Detected Windows - using ReportLab backend")
    else:
        requirements_file = 'requirements.txt'
        print("Detected Unix/Linux - using WeasyPrint backend")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', requirements_file
        ], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("Setting up directories...")
    
    directories = ['templates', 'output', 'signatures']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_config():
    """Create configuration file if it doesn't exist"""
    print("Setting up configuration...")
    
    if not Path('local_config.py').exists():
        config_content = """# Local configuration overrides
# Copy and modify values from config.py

COMPANY_INFO = {
    'name': 'Ваша Компания',
    'address': 'Ваш адрес',
    'inn': 'Ваш ИНН',
    'kpp': 'Ваш КПП',
    'phone': 'Ваш телефон',
    'email': 'Ваш email'
}

BANK_INFO = {
    'name': 'Ваша Компания',
    'personal_acc': 'Ваш расчетный счет',
    'bank_name': 'Ваш банк',
    'bic': 'БИК банка',
    'corresp_acc': 'Корреспондентский счет',
    'payee_inn': 'Ваш ИНН',
    'kpp': 'Ваш КПП'
}
"""
        with open('local_config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✓ Created local_config.py template")
    else:
        print("✓ local_config.py already exists")

def test_installation():
    """Test if the installation works"""
    print("Testing installation...")
    
    try:
        if sys.platform.startswith('win'):
            from invoice_generator_reportlab import InvoiceGeneratorReportLab
            generator = InvoiceGeneratorReportLab()
        else:
            from invoice_generator import InvoiceGenerator
            generator = InvoiceGenerator()
        
        print("✓ Invoice generator imports successfully")
        
        # Test QR code generation
        test_data = {
            'name': 'Test',
            'sum': '1000',
            'purpose': 'Test payment'
        }
        
        if sys.platform.startswith('win'):
            qr_buffer = generator.generate_qr_code(test_data)
            if qr_buffer:
                print("✓ QR code generation works")
        else:
            qr_code = generator.generate_qr_code(test_data)
            if qr_code:
                print("✓ QR code generation works")
        
        # Test number conversion
        amount_words = generator.sum_to_words_russian(1500.50)
        if amount_words:
            print("✓ Russian number-to-words conversion works")
        
        return True
        
    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=== Invoice Generator Setup ===\n")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Setup steps
    success = True
    success &= install_dependencies()
    
    setup_directories()
    setup_config()
    
    if success:
        success &= test_installation()
    
    print("\n=== Setup Complete ===")
    
    if success:
        print("✓ Invoice Generator is ready to use!")
        print("\nNext steps:")
        print("1. Edit local_config.py with your company details")
        print("2. Run example_usage.py to test the system")
        if sys.platform.startswith('win'):
            print("3. Use invoice_generator_reportlab.py for your invoices")
        else:
            print("3. Use invoice_generator.py for your invoices")
    else:
        print("✗ Setup encountered errors. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
