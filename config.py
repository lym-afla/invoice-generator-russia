"""
Configuration file for Invoice Generator
"""

# Company information (Contractor/Payee)
COMPANY_INFO = {
    'legal_form': 'Индивидуальный предприниматель',
    'legal_form_short': 'ИП',
    'name': 'Линик Ярослав Михайлович',
    'inn': '890305332590',
    'ogrnip': '325774600140091',
    'signature_name': 'Я.М. Линик'
}

# Bank details for QR code generation
BANK_INFO = {
    'name': 'Линик Ярослав Михайлович',
    'personal_acc': '42301810900076433520',
    'bank_name': 'АО "ТБанк"',
    'bic': '044525974',
    'corresp_acc': '30101810145250000974'
}

# Default client information
CLIENT_INFO = {
    'name': 'Гуринов Вадим Александрович',
    'contract_date': '2025-05-26',  # Format: YYYY-MM-DD
}

# Financial settings
FINANCIAL_SETTINGS = {
    'base_rate': 16667,  # Base rate in USD
    'currency': 'USD',       # Default currency for FX rate
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
