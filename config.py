"""
Configuration file for Invoice Generator
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Company information (Contractor/Payee)
COMPANY_INFO = {
    'legal_form': 'Индивидуальный предприниматель',
    'legal_form_short': 'ИП',
    'name': os.getenv('COMPANY_NAME'),
    'inn': os.getenv('COMPANY_INN'),
    'ogrnip': os.getenv('COMPANY_OGRNIP'),
    'signature_name': 'Я.М. Линик'
}

# Bank details for QR code generation
BANK_INFO = {
    'name': os.getenv('COMPANY_NAME'),
    'personal_acc': os.getenv('BANK_PERSONAL_ACC'),
    'bank_name': os.getenv('BANK_NAME'),
    'bic': os.getenv('BANK_BIC', '044525974'),
    'corresp_acc': os.getenv('BANK_CORRESP_ACC')
}

# Default client information
CLIENT_INFO = {
    'name': os.getenv('CLIENT_NAME'),
    'contract_date': os.getenv('CLIENT_CONTRACT_DATE'),  # Format: YYYY-MM-DD
}

# Financial settings
FINANCIAL_SETTINGS = {
    'base_rate': int(os.getenv('BASE_RATE')),  # Base rate in USD
    'currency': os.getenv('CURRENCY'),           # Default currency for FX rate
}

# Telegram Bot Configuration
TELEGRAM_CONFIG = {
    'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
}

# File paths
TEMPLATES_DIR = 'templates'
OUTPUT_DIR = 'output'
SIGNATURES_DIR = 'signatures'

# PDF settings
PDF_CONFIG = {
    'page_size': 'A4',
    'margin': '2cm',
    'encoding': 'utf-8',
    'generate_html': False,  # Only generate PDFs, no HTML files
}

# QR Code settings
QR_CONFIG = {
    'version': 1,
    'error_correction': 'L',  # Low error correction for faster scanning
    'box_size': 10,
    'border': 4
}
