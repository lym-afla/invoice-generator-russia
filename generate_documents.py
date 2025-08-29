#!/usr/bin/env python3
"""
Unified Document Generator
Generates both Invoice and Act PDFs from a single interface
"""

import base64
import os
from datetime import date, datetime

# Import our generators and config
from config import BANK_INFO, COMPANY_INFO, CLIENT_INFO, FINANCIAL_SETTINGS
from invoice_generator_html import InvoiceGeneratorHTML
from act_generator import ActGenerator


class UnifiedDocumentGenerator:
    """
    Unified generator for both invoices and acts
    """
    
    def __init__(self):
        self.invoice_generator = InvoiceGeneratorHTML()
        self.act_generator = ActGenerator()
        
        # Parse contract date from config
        contract_date_str = CLIENT_INFO['contract_date']
        year, month, day = map(int, contract_date_str.split('-'))
        self.contract_date = date(year, month, day)        
        
    def generate_both_documents(self, services_list, company_info, bank_info, client_info, financial_settings, signature_path):
        """
        Generate both invoice and act for the given services
        
        Args:
            services_list (list): List of service descriptions (strings) or service dicts
            invoice_amount (float, optional): Invoice amount, if None uses calculated amount from act
            
        Returns:
            dict: Paths to generated files or None values on failure
        """
        
        print("🚀 Unified Document Generator")
        print("=" * 50)
        
        results = {
            'invoice_path': None,
            'act_path': None,
            'invoice_amount': None,
            'act_amount': None
        }

        if os.path.exists(signature_path):
            try:
                with open(signature_path, 'rb') as f:
                    self.signature_data = base64.b64encode(f.read()).decode()
                    print("✅ Signature loaded")
            except Exception as e:
                print(f"⚠️  Could not load signature: {e}")
        
        # 1. Generate Act first (to get calculated amount)
        print("\n📋 Generating Service Act...")
        try:
            act_path = self.act_generator.generate_act(
                services_list=services_list,
                company_info=company_info,
                client_info=client_info,
                financial_settings=financial_settings,
                signature_data=self.signature_data
            )
            
            if act_path:
                print(f"✅ Act generated: {os.path.basename(act_path)}")
                results['act_path'] = act_path
                
                # Get the calculated amount from act (same calculation as act generator)
                try:
                    fx_rate = self.act_generator.get_fx_rate(financial_settings['currency'], date.today())
                    if fx_rate:
                        calculated_amount = int(financial_settings['base_rate'] * fx_rate)
                        results['act_amount'] = calculated_amount
                    else:
                        print("⚠️  Could not get FX rate for invoice amount calculation")
                except Exception as e:
                    print(f"⚠️  Error calculating amount: {e}")
                
                # Use calculated amount for invoice if not specified  
                if results.get('act_amount'):
                    print(f"💰 Using calculated amount: {results['act_amount']:,.0f} RUB")
            else:
                print("❌ Act generation failed")
                return results
                
        except Exception as e:
            print(f"❌ Act generation error: {e}")
            return results
        
        # 2. Generate Invoice
        print("\n🧾 Generating Invoice...")
        try:
            # Prepare invoice data
            invoice_data = self._prepare_invoice_data(results['act_amount'], company_info, bank_info, client_info)
            
            invoice_path = self.invoice_generator.generate_invoice(invoice_data)
            
            if invoice_path:
                print(f"✅ Invoice generated: {os.path.basename(invoice_path)}")
                results['invoice_path'] = invoice_path
                results['invoice_amount'] = results['act_amount']
            else:
                print("❌ Invoice generation failed")
                
        except Exception as e:
            print(f"❌ Invoice generation error: {e}")
        
        return results
    
    def _prepare_invoice_data(self, total_amount, company_info, bank_info, client_info):
        """
        Prepare invoice data from services and config
        """
        
        # Convert services to invoice items
        items = []
        
        # Single item
        items.append({
            'name': 'Консультационные услуги',
            'quantity': 1,
            'price': total_amount,
            'vat_rate': 'Без НДС',
            'total': total_amount
        })
        
        # Prepare full invoice data
        invoice_data = {
            'payee': {
                'legal_form': company_info['legal_form'],
                'legal_form_short': company_info['legal_form_short'],
                'name': company_info['name'],
                'inn': company_info['inn'],
                'bank_name': bank_info['bank_name'],
                'bank_bik': bank_info['bic'],
                'bank_corr_account': bank_info['corresp_acc'],
                'account_number': bank_info['personal_acc'],
                'details_string': f"{company_info['name']}, ИНН {company_info['inn']}, р/с {bank_info['personal_acc']}, в банке {bank_info['bank_name']}, БИК {bank_info['bic']}, к/с {bank_info['corresp_acc']}"
            },
            'payer': {
                'name': client_info['name']
            },
            'invoice': {
                'number': '',
                'date': f"{datetime.now().strftime('%d')} {self.act_generator.get_russian_month(datetime.now().month)} {datetime.now().year} г."
            },
            'items': items,
            'totals': {
                'total': total_amount,
                'total_in_words': ''
            },
            'qr_code_data': {
                'name': company_info['name'],
                'personal_acc': bank_info['personal_acc'],
                'bank_name': bank_info['bank_name'],
                'bic': bank_info['bic'],
                'corresp_acc': bank_info['corresp_acc'],
                'payee_inn': company_info['inn'],
                'kpp': '',
                'sum': total_amount
            },
            'qr_code_data_uri': '',
            'signatures': {
                'director': self.signature_data
            }
        }
        
        return invoice_data
    
    def generate_invoice_only(self, services_list, amount):
        """Generate only invoice"""
        print("🧾 Generating Invoice Only...")
        invoice_data = self._prepare_invoice_data(amount, COMPANY_INFO, BANK_INFO, CLIENT_INFO)
        return self.invoice_generator.generate_invoice(invoice_data)
    
    def generate_act_only(self, services_list):
        """Generate only act"""
        print("📋 Generating Act Only...")
        return self.act_generator.generate_act(
            services_list=services_list,
            currency=FINANCIAL_SETTINGS['currency'],
            customer_name=CLIENT_INFO['name'],
            contract_date=self.contract_date,
            base_rate=FINANCIAL_SETTINGS['base_rate']
        )


def main():
    """
    Main function with example usage
    """
    
    # Example services
    services = [
        'Анализ и реализация инвестиционных проектов (Кракен, Citymall)',
        'Ведение проекта редомицилиации MLOne',
        'Актуализация соглашений по существующим инвестициям и анализ перспективных инвестиций в BeOnd',
        'Реализация проекта по аналитике портфельной аллокации'
    ]
    
    # Initialize generator
    generator = UnifiedDocumentGenerator()
    
    # Generate both documents
    results = generator.generate_both_documents(
        services=services,
        company_info=COMPANY_INFO,
        bank_info=BANK_INFO,
        client_info=CLIENT_INFO,
        financial_settings=FINANCIAL_SETTINGS,
        signature_path='signatures/YL_Signature.png'
        )
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Generation Summary:")
    print(f"📋 Act: {'✅ ' + os.path.basename(results['act_path']) if results['act_path'] else '❌ Failed'}")
    print(f"🧾 Invoice: {'✅ ' + os.path.basename(results['invoice_path']) if results['invoice_path'] else '❌ Failed'}")
    
    if results['act_amount']:
        print(f"💰 Amount: {results['act_amount']:,.0f} RUB")
    
    print(f"📂 Output folder: {os.path.abspath('output')}")


if __name__ == "__main__":
    main()
