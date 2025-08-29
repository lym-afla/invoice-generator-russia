#!/usr/bin/env python3
"""
Main Invoice Generator Script
Simplified interface for generating invoices
"""

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
        'company_name': 'ИП Линик Ярослав Михайлович',
        'company_inn': '890305332590',
        'company_kpp': '',
        
        'client_name': client_name,
        'client_address': '',
        
        'items': [
            {
                'description': service_description,
                'unit': 'шт.',
                'quantity': 1,
                'price': amount,
                'total': amount
            }
        ],
        
        'subtotal': amount,
        'total_amount': amount,
        
        'payment_data': {
            'name': 'Линик Ярослав Михайлович',
            'personal_acc': '42301810900076433520',
            'bank_name': 'АО "ТБанк"',
            'bic': '044525974',
            'corresp_acc': '30101810145250000974',
            'payee_inn': '890305332590',
            'kpp': '',
            'sum': str(int(amount))
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
