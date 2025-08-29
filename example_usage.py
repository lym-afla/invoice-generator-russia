#!/usr/bin/env python3
"""
Example usage of the Invoice Generator
Shows different ways to use the system
"""

from invoice_generator_reportlab import InvoiceGeneratorReportLab
from datetime import datetime
import json

def create_sample_invoice():
    """Create a sample invoice with typical Russian business data"""
    
    generator = InvoiceGeneratorReportLab()
    
    # Sample invoice data
    invoice_data = {
        'company_name': 'ООО "ТехноСервис"',
        'company_address': 'г. Москва, ул. Тверская, д. 10, офис 205',
        'company_inn': '7701234567',
        'company_kpp': '770101001',
        
        'client_name': 'ИП Петров Петр Петрович',
        'client_address': 'г. Санкт-Петербург, пр. Невский, д. 25',
        
        'items': [
            {
                'description': 'Настройка сервера',
                'unit': 'услуга',
                'quantity': 1,
                'price': 25000.00,
                'total': 25000.00
            },
            {
                'description': 'Техническая поддержка (месяц)',
                'unit': 'мес.',
                'quantity': 3,
                'price': 15000.00,
                'total': 45000.00
            },
            {
                'description': 'Резервное копирование',
                'unit': 'шт.',
                'quantity': 1,
                'price': 10000.00,
                'total': 10000.00
            }
        ],
        
        'subtotal': 80000.00,
        'vat_rate': 20,
        'vat_amount': 16000.00,
        'total_amount': 96000.00,
        
        'payment_data': {
            'name': 'ООО "ТехноСервис"',
            'personal_acc': '40702810900000000001',
            'bank_name': 'ПАО "Сбербанк"',
            'bic': '044525225',
            'corresp_acc': '30101810400000000225',
            'payee_inn': '7701234567',
            'kpp': '770101001',
            'sum': '96000',
            'purpose': f'Оплата по счету от {datetime.now().strftime("%d.%m.%Y")}'
        }
    }
    
    return generator.generate_invoice(invoice_data)

def create_invoice_from_json():
    """Load invoice data from JSON file"""
    
    # Sample JSON structure
    sample_json = {
        "client": {
            "name": "ООО \"Клиент\"",
            "address": "г. Москва, ул. Примерная, д. 123",
            "inn": "1234567890"
        },
        "items": [
            {
                "description": "Консультация",
                "quantity": 2,
                "price": 5000,
                "total": 10000
            }
        ],
        "payment": {
            "bank_name": "ПАО \"Банк\"",
            "bic": "044525225",
            "account": "40702810900000000001"
        }
    }
    
    # Save sample JSON
    with open('sample_invoice.json', 'w', encoding='utf-8') as f:
        json.dump(sample_json, f, ensure_ascii=False, indent=2)
    
    print("Sample JSON created: sample_invoice.json")
    
    # You can load and process JSON like this:
    # with open('sample_invoice.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    #     # Process and generate invoice...

def batch_generate_invoices():
    """Generate multiple invoices for different clients"""
    
    generator = InvoiceGeneratorReportLab()
    
    clients = [
        {
            'name': 'ООО "Альфа"',
            'address': 'г. Москва, ул. Арбат, д. 1',
            'services': [('Web-разработка', 1, 50000)]
        },
        {
            'name': 'ИП Иванов И.И.',
            'address': 'г. СПб, ул. Ленина, д. 2',
            'services': [('Консультация', 3, 5000), ('Аудит', 1, 15000)]
        }
    ]
    
    generated_files = []
    
    for client in clients:
        items = []
        subtotal = 0
        
        for desc, qty, price in client['services']:
            total = qty * price
            items.append({
                'description': desc,
                'quantity': qty,
                'price': price,
                'total': total
            })
            subtotal += total
        
        vat_amount = subtotal * 0.20
        total_amount = subtotal + vat_amount
        
        invoice_data = {
            'client_name': client['name'],
            'client_address': client['address'],
            'items': items,
            'subtotal': subtotal,
            'vat_rate': 20,
            'vat_amount': vat_amount,
            'total_amount': total_amount,
            'payment_data': {
                'name': 'ООО "Ваша Компания"',
                'personal_acc': '40702810900000000001',
                'bank_name': 'ПАО "Банк"',
                'bic': '044525225',
                'corresp_acc': '30101810400000000225',
                'payee_inn': '1234567890',
                'kpp': '123456789',
                'sum': str(int(total_amount)),
                'purpose': f'Оплата по счету'
            }
        }
        
        pdf_path = generator.generate_invoice(invoice_data)
        generated_files.append(pdf_path)
        print(f"Generated: {pdf_path}")
    
    return generated_files

if __name__ == "__main__":
    print("=== Invoice Generator Examples ===\n")
    
    # Example 1: Simple invoice
    print("1. Generating sample invoice...")
    pdf_path = create_sample_invoice()
    print(f"✓ Created: {pdf_path}\n")
    
    # Example 2: JSON structure
    print("2. Creating JSON template...")
    create_invoice_from_json()
    print("✓ JSON template created\n")
    
    # Example 3: Batch generation
    print("3. Batch generating invoices...")
    batch_files = batch_generate_invoices()
    print(f"✓ Generated {len(batch_files)} invoices\n")
    
    print("All examples completed successfully!")
