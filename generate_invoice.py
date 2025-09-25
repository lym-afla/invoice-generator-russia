#!/usr/bin/env python3
"""
Main Invoice Generator Script
Simplified interface for generating invoices
"""

import datetime
import os
import base64
from invoice_generator_html import InvoiceGeneratorHTML


def load_signature(signature_path):
    """Load signature image if available"""
    if os.path.exists(signature_path):
        try:
            with open(signature_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except Exception as e:
            print(f"⚠️  Could not load signature from {signature_path}: {e}")
    return None


def create_invoice(
    service_description="Консультационные услуги",
    amount=150000.00,
    client_name="[Плательщик]"
):
    """
    Create a single invoice with given parameters
    
    Args:
        service_description (str): Description of service/product
        amount (float): Amount in rubles
        client_name (str): Client name
        purpose (str): Payment purpose
    
    Returns:
        str: Path to generated PDF
    """
    
    generator = InvoiceGeneratorHTML()
    
    # Load signature if available
    signature_data = load_signature('signatures/YL_Signature.png')
    
    # Prepare invoice data
    invoice_data = {
        'payee': {
                'legal_form': "Индивидуальный предприниматель",
                'legal_form_short': "ИП",
                'name': "Название компании",
                'inn': "ИНН компании",
                'bank_name': "Название банка",
                'bank_bik': "БИК банка",
                'bank_corr_account': "Корреспондентский счет банка",
                'account_number': "Расчетный счет банка",
                'details_string': f"Название компании, ИНН 'ИНН компании', р/с 'Расчетный счет банка', в банке 'Название банка', БИК 'БИК банка', к/с 'Корреспондентский счет банка'"
            },
            'payer': {
                'name': "Имя клиента"
            },
            'invoice': {
                'number': '',
                'date': "Дата счета"
            },
            'items': [
                {
                    'description': service_description,
                    'unit': 'шт.',
                    'quantity': 1,
                    'price': amount,
                    'total': amount
                }
            ],
            'totals': {
                'total': amount,
                'total_in_words': ''
            },
            'qr_code_data': {
                'name': "Название компании",
                'personal_acc': "Расчетный счет банка",
                'bank_name': "Название банка",
                'bic': "БИК банка",
                'corresp_acc': "Корреспондентский счет банка",
                'payee_inn': "ИНН компании",
                'kpp': '',
                'sum': amount
            },
            'qr_code_data_uri': '',
            'signatures': {
                'director': "Data"
            }
    }
    
    # Add signature if available
    if signature_data:
        invoice_data['signatures'] = {'director': signature_data}
        print("✅ Signature included")
    
    # Generate invoice
    result_path = generator.generate_invoice(invoice_data)
    print(f"✅ Invoice generated: {result_path}")
    
    return result_path


def main():
    """Main function with examples"""
    print("🧾 Invoice Generator")
    print("=" * 50)
    
    # # Example 1: Default invoice
    # print("\n📋 Generating default invoice...")
    # create_invoice()
    
    # Example 2: Custom invoice
    print("\n📋 Generating custom invoice...")
    create_invoice(
        service_description="Консультационные услуги",
        amount=1345128.00,
        client_name="Гуринов Вадим Александрович"
    )
    
    print("\n✅ All invoices generated successfully!")
    print("📂 Check the 'output' folder for your PDFs")


if __name__ == "__main__":
    main()
