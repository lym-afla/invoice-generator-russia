"""
Configuration file for Invoice Generator
"""

# Company information
COMPANY_INFO = {
    'name': 'ООО "Ромашка"',
    'inn': '7701234567',
    'ogrn': '1234567890123',
    'phone': '+7 (495) 123-45-67',
    'email': 'info@romashka.ru',
    'website': 'www.romashka.ru'
}

# Bank details for QR code generation
BANK_INFO = {
    'name': 'ООО "Ромашка"',
    'personal_acc': '40702810900000000001',
    'bank_name': 'ПАО "Банк"',
    'bic': '044525225',
    'corresp_acc': '30101810400000000225',
    'payee_inn': '1234567890',
}

# VAT settings
DEFAULT_VAT_RATE = 20  # %

# File paths
TEMPLATES_DIR = 'templates'
OUTPUT_DIR = 'output'
SIGNATURES_DIR = 'signatures'

# PDF settings
PDF_CONFIG = {
    'page_size': 'A4',
    'margin': '2cm',
    'encoding': 'utf-8'
}

# QR Code settings
QR_CONFIG = {
    'version': 1,
    'error_correction': 'L',  # Low error correction for faster scanning
    'box_size': 10,
    'border': 4
}
