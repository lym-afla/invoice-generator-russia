#!/usr/bin/env python3
"""
Invoice Generator Script
Generates invoices from HTML template with QR codes and Russian localization
"""

import os
import qrcode
import base64
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from num2words import num2words
from io import BytesIO
import calendar


class InvoiceGenerator:
    def __init__(self, template_dir="templates", output_dir="output"):
        """
        Initialize the invoice generator
        
        Args:
            template_dir (str): Directory containing HTML templates
            output_dir (str): Directory for generated PDFs
        """
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_invoice_number(self, date=None):
        """
        Generate invoice number using octal conversion of yyyymm
        
        Args:
            date (datetime, optional): Date for invoice. Defaults to current date.
            
        Returns:
            str: Invoice number in octal format
        """
        if date is None:
            date = datetime.now()
        
        yyyymm = int(f"{date.year}{date.month:02d}")
        octal_number = oct(yyyymm)[2:]  # Remove '0o' prefix
        return f"INV-{octal_number}"
    
    def generate_qr_code(self, payment_data):
        """
        Generate QR code compliant with СПКР (ГОСТ Р 56042-2014)
        
        Args:
            payment_data (dict): Payment information containing required fields
            
        Returns:
            str: Base64 encoded QR code image
        """
        # Format QR data according to СПКР standard
        qr_data = (
            f"ST00012|"
            f"Name={payment_data.get('name', '')}|"
            f"PersonalAcc={payment_data.get('personal_acc', '')}|"
            f"BankName={payment_data.get('bank_name', '')}|"
            f"BIC={payment_data.get('bic', '')}|"
            f"CorrespAcc={payment_data.get('corresp_acc', '')}|"
            f"PayeeINN={payment_data.get('payee_inn', '')}|"
            f"KPP={payment_data.get('kpp', '')}|"
            f"Sum={payment_data.get('sum', '')}|"
            f"Purpose={payment_data.get('purpose', '')}"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for HTML embedding
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{qr_base64}"
    
    def sum_to_words_russian(self, amount):
        """
        Convert numeric amount to words in Russian
        
        Args:
            amount (float): Amount to convert
            
        Returns:
            str: Amount in Russian words
        """
        try:
            # Split into rubles and kopecks
            rubles = int(amount)
            kopecks = int((amount - rubles) * 100)
            
            # Convert to words
            rubles_words = num2words(rubles, lang='ru')
            kopecks_words = num2words(kopecks, lang='ru') if kopecks > 0 else "ноль"
            
            # Add currency units with proper declension
            if rubles % 10 == 1 and rubles % 100 != 11:
                ruble_unit = "рубль"
            elif rubles % 10 in [2, 3, 4] and rubles % 100 not in [12, 13, 14]:
                ruble_unit = "рубля"
            else:
                ruble_unit = "рублей"
            
            if kopecks % 10 == 1 and kopecks % 100 != 11:
                kopeck_unit = "копейка"
            elif kopecks % 10 in [2, 3, 4] and kopecks % 100 not in [12, 13, 14]:
                kopeck_unit = "копейки"
            else:
                kopeck_unit = "копеек"
            
            result = f"{rubles_words.capitalize()} {ruble_unit}"
            if kopecks > 0:
                result += f" {kopecks_words} {kopeck_unit}"
            else:
                result += f" ноль {kopeck_unit}"
                
            return result
            
        except Exception as e:
            return f"Ошибка конвертации: {str(e)}"
    
    def generate_invoice(self, invoice_data, template_name="invoice.html"):
        """
        Generate invoice PDF from template and data
        
        Args:
            invoice_data (dict): Invoice information
            template_name (str): Template filename
            
        Returns:
            str: Path to generated PDF file
        """
        # Load template
        template = self.jinja_env.get_template(template_name)
        
        # Prepare template data
        current_date = datetime.now()
        invoice_number = self.generate_invoice_number(current_date)
        
        # Generate QR code
        qr_code_image = self.generate_qr_code(invoice_data.get('payment_data', {}))
        
        # Convert sum to words
        total_amount = invoice_data.get('total_amount', 0)
        amount_in_words = self.sum_to_words_russian(total_amount)
        
        # Prepare context for template
        context = {
            'invoice_number': invoice_number,
            'invoice_date': current_date.strftime('%d.%m.%Y'),
            'current_month': calendar.month_name[current_date.month],
            'current_year': current_date.year,
            'qr_code': qr_code_image,
            'amount_in_words': amount_in_words,
            **invoice_data  # Merge with provided data
        }
        
        # Render HTML
        html_content = template.render(context)
        
        # Generate PDF
        pdf_filename = f"{invoice_number}_{current_date.strftime('%Y%m%d')}.pdf"
        pdf_path = os.path.join(self.output_dir, pdf_filename)
        
        HTML(string=html_content).write_pdf(pdf_path)
        
        return pdf_path


if __name__ == "__main__":
    # Example usage
    generator = InvoiceGenerator()
    
    # Sample invoice data
    sample_data = {
        'client_name': 'ООО "Клиент"',
        'client_address': 'г. Москва, ул. Примерная, д. 123',
        'items': [
            {'description': 'Услуга 1', 'quantity': 1, 'price': 50000, 'total': 50000},
            {'description': 'Услуга 2', 'quantity': 2, 'price': 25000, 'total': 50000},
        ],
        'subtotal': 100000,
        'vat_rate': 20,
        'vat_amount': 20000,
        'total_amount': 120000,
        'payment_data': {
            'name': 'ООО "Ромашка"',
            'personal_acc': '40702810900000000001',
            'bank_name': 'АО "БАНК"',
            'bic': '044525225',
            'corresp_acc': '30101810400000000225',
            'payee_inn': '7701234567',
            'kpp': '770101001',
            'sum': '120000',
            'purpose': 'Оплата по счету'
        }
    }
    
    try:
        pdf_path = generator.generate_invoice(sample_data)
        print(f"Invoice generated successfully: {pdf_path}")
    except Exception as e:
        print(f"Error generating invoice: {str(e)}")
