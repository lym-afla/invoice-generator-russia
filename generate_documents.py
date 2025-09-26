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
        
    def generate_both_documents(
        self,
        services_list,
        company_info,
        bank_info,
        client_info,
        financial_settings,
        signature_path,
        generation_date=None
        ):
        """
        Generate both invoice and act for the given services
        
        Args:
            services_list (list): List of service descriptions (strings) or service dicts
            company_info (dict): Company information
            bank_info (dict): Bank information 
            client_info (dict): Client information
            financial_settings (dict): Financial settings
            signature_path (str): Path to signature image
            generation_date (date): Date for document generation (default: today)
            
        Returns:
            dict: Paths to generated files or None values on failure
        """
        
        print("🚀 Unified Document Generator")
        print("=" * 50)
        
        # Set generation date
        if generation_date is None:
            generation_date = date.today()
        
        print(f"📅 Generation date: {generation_date.strftime('%d.%m.%Y')}")
        
        results = {
            'invoice_path': None,
            'act_path': None,
            'invoice_amount': None,
            'act_amount': None
        }

        # Load signature
        if os.path.exists(signature_path):
            try:
                with open(signature_path, 'rb') as f:
                    self.signature_data = base64.b64encode(f.read()).decode()
                    print("✅ Signature loaded")
            except Exception as e:
                print(f"⚠️  Could not load signature: {e}")
        
        # GET FX RATE ONCE and calculate total amount
        print(f"\n💱 Fetching {financial_settings['currency']} exchange rate...")
        try:
            fx_rate = self.act_generator.get_fx_rate(financial_settings['currency'], generation_date)
            if fx_rate is None:
                print(f"❌ Cannot generate documents: Failed to get {financial_settings['currency']} exchange rate from CBR")
                return results
            
            # Calculate total amount and round to nearest 10
            total_amount_exact = financial_settings['base_rate'] * fx_rate
            total_amount = round(total_amount_exact / 10) * 10  # Round to nearest 10
            
            print(f"💰 Exchange rate: {fx_rate}")
            print(f"💰 Base rate: {financial_settings['base_rate']:,}")
            print(f"💰 Calculated amount: {total_amount:,} RUB (rounded from {total_amount_exact:,.2f})")
            
            results['act_amount'] = total_amount
            results['invoice_amount'] = total_amount
            
        except Exception as e:
            print(f"❌ Error fetching exchange rate: {e}")
            return results
        
        # 1. Generate Act 
        print("\n📋 Generating Service Act...")
        try:
            act_path = self.act_generator.generate_act_with_precalculated(
                services_list=services_list,
                company_info=company_info,
                client_info=client_info,
                signature_data=self.signature_data,
                generation_date=generation_date,
                fx_rate=fx_rate,
                total_amount=total_amount
            )
            
            if act_path:
                print(f"✅ Act generated: {os.path.basename(act_path)}")
                results['act_path'] = act_path
            else:
                print("❌ Act generation failed")
                return results
        except Exception as e:
            print(f"❌ Act generation error: {e}")
            return results
        
        # 2. Generate Invoice
        print("\n🧾 Generating Invoice...")
        try:
            # Prepare invoice data with generation date
            invoice_data = self._prepare_invoice_data(total_amount, company_info, bank_info, client_info, generation_date)
            
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
    
    def _prepare_invoice_data(
        self,
        total_amount,
        company_info,
        bank_info,
        client_info,
        generation_date
        ):
        """
        Prepare invoice data from services and config
        
        Args:
            total_amount (float): Total amount for invoice
            company_info (dict): Company information
            bank_info (dict): Bank information
            client_info (dict): Client information  
            generation_date (date): Date for the invoice
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
                'date': (
                    f"{generation_date.strftime('%d')} "
                    f"{self.act_generator.get_russian_month(generation_date.month)} "
                    f"{generation_date.year} г."
                )
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
