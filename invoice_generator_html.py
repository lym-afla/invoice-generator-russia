#!/usr/bin/env python3
"""
HTML-based Invoice Generator that works with updated template
Uses WeasyPrint for PDF generation with proper Unicode support
"""

import os
import qrcode
import base64
from datetime import datetime
from io import BytesIO
from num2words import num2words
from jinja2 import Environment, FileSystemLoader

from act_generator import ActGenerator
from config import BANK_INFO, COMPANY_INFO

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)


class InvoiceGeneratorHTML:
    def __init__(self, output_dir="output", templates_dir="templates"):
        """
        Initialize the HTML invoice generator
        
        Args:
            output_dir (str): Directory for generated PDFs
            templates_dir (str): Directory containing HTML templates
        """
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
        if not WEASYPRINT_AVAILABLE:
            print("⚠️  WeasyPrint not available. Only HTML output will be generated.")
            if 'WEASYPRINT_ERROR' in globals():
                print(f"   Error: {WEASYPRINT_ERROR}")
    
    def generate_qr_code(self, qr_data, invoice_number):
        """
        Generate QR code according to СПКР standard
        
        Args:
            qr_data (dict): Payment data for QR generation
            
        Returns:
            str: Base64 encoded QR code image
        """
        # Format according to СПКР (ГОСТ Р 56042-2014)
        qr_data['sum'] = int(qr_data.get('sum', '')) * 100
        qr_string = (
            f"ST00012|"
            f'Name={qr_data.get('name', '')}|'
            f"PersonalAcc={qr_data.get('personal_acc', '')}|"
            f"BankName={qr_data.get('bank_name', '')}|"
            f"BIC={qr_data.get('bic', '')}|"
            f"CorrespAcc={qr_data.get('corresp_acc', '')}|"
            f"PayeeINN={qr_data.get('payee_inn', '')}|"
            f"KPP={qr_data.get('kpp', '')}|"
            f"Sum={qr_data.get('sum', '')}|"
            f"Purpose=Оплата по счету №{invoice_number} от {datetime.now().strftime("%d.%m.%Y")}"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def convert_sum_to_words(self, amount):
        """
        Convert sum to Russian words
        
        Args:
            amount (float): Amount to convert
            
        Returns:
            str: Amount in Russian words
        """
        try:
            # Convert to Russian words
            amount_int = int(amount * 100) # because num2words expects cents
            words = num2words(amount_int, lang='ru', to='currency', currency='RUB')
            words = words.replace(',', '').replace('ноль', '00')
            
            # Capitalize first letter
            return words
        except Exception as e:
            print(f"Error converting sum to words: {e}")
            return f"{int(amount)} рублей"
    
    # def transform_data_for_template(self, invoice_data):
    #     """
    #     Transform invoice data to match invoice.html template structure
        
    #     Args:
    #         invoice_data (dict): Original invoice data
            
    #     Returns:
    #         dict: Transformed data for template
    #     """

    #     # Build template data structure
    #     template_data = {
    #         'payee': invoice_data.get('payee', {}),
    #         'payer': invoice_data.get('payer', {}),
    #         'invoice': {
    #             'number': invoice_data.get('invoice_number', ''),
    #             'date': invoice_data.get('invoice_date', '')
    #         },
    #         'items': [],
    #         'totals': {
    #             'total': invoice_data.get('total_amount', 0),
    #             'total_in_words': invoice_data.get('amount_in_words', '')
    #         },
    #         'qr_code_data_uri': invoice_data.get('qr_code', ''),
    #         'signatures': invoice_data.get('signatures', {})
    #     }
        
    #     # Transform items
    #     for item in invoice_data.get('items', []):
    #         template_data['items'].append({
    #             'name': item.get('description', ''),
    #             'quantity': item.get('quantity', 1),
    #             'price': item.get('price', 0),
    #             'vat_rate': 'Без НДС',
    #             'total': item.get('total', 0)
    #         })
        
    #     return template_data
    

    def generate_octal_invoice_number(self, year, month):
        """
        Generate invoice number using octal conversion of yyyymm
        
        Args:
            year (int): Year
            month (int): Month
            
        Returns:
            str: Octal-based invoice number
        """
        # Create yyyymm format
        yyyymm = year * 100 + month
        
        # Convert to octal (remove '0o' prefix)
        octal_number = oct(yyyymm)[2:]
        
        return octal_number
    
    def generate_invoice(self, invoice_data):
        """
        Generate invoice from data
        
        Args:
            invoice_data (dict): Invoice data
            
        Returns:
            str: Path to generated PDF
        """
        # Generate invoice number if not provided
        now = datetime.now()
        invoice_data['invoice']['number'] = self.generate_octal_invoice_number(now.year, now.month)
        
        # Generate QR code
        if 'qr_code_data' in invoice_data:
            invoice_data['qr_code_data_uri'] = self.generate_qr_code(invoice_data['qr_code_data'], invoice_data['invoice']['number'])
        
        # Convert amount to words
        if 'total' in invoice_data['totals']:
            invoice_data['totals']['total_in_words'] = self.convert_sum_to_words(invoice_data['totals']['total'])
        
        # Remove qr_code_data from invoice_data to match invoice.html structure
        invoice_data.pop('qr_code_data')
        
        # Load and render template
        template = self.env.get_template('invoice.html')
        html_content = template.render(**invoice_data)
        
        # Generate filename with timestamp to avoid conflicts
        invoice_num = invoice_data['invoice']['number']
        filename = f"invoice_{invoice_num}"
        
        # Save HTML only if configured to do so
        from config import PDF_CONFIG
        html_path = None
        if PDF_CONFIG.get('generate_html', True):
            html_path = os.path.join(self.output_dir, f"{filename}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        # Try to generate PDF
        pdf_path = os.path.join(self.output_dir, f"{filename}.pdf")
        
        if WEASYPRINT_AVAILABLE:
            try:
                # Use WeasyPrint to generate PDF
                weasyprint.HTML(string=html_content, base_url=self.templates_dir).write_pdf(pdf_path)
                print(f"✅ PDF generated with WeasyPrint: {pdf_path}")
                return pdf_path
            except Exception as e:
                print(f"❌ WeasyPrint error: {e}")
        
        # Try alternative PDF generation
        try:
            from html_to_pdf_converter import HTMLToPDFConverter
            converter = HTMLToPDFConverter()
            if converter.convert_html_to_pdf(html_content, pdf_path):
                return pdf_path
        except Exception as e:
            print(f"⚠️  Alternative PDF conversion failed: {e}")
        
        # Fallback - if HTML is disabled and PDF failed, return None
        if html_path:
            print(f"📄 HTML generated: {html_path}")
            print("💡 To create PDF manually:")
            print("   1. Open the HTML file in a web browser")
            print("   2. Press Ctrl+P (Print)")
            print("   3. Choose 'Save as PDF' as destination")
            print("   4. Set margins to 'Custom' with 0.75 inches on all sides")
            print("   5. Save the PDF")
            return html_path
        else:
            print("❌ PDF generation failed and HTML generation is disabled")
            return None


def main():
    """Test the invoice generator"""
    generator = InvoiceGeneratorHTML()
    
    # Sample data matching the template
    invoice_data = {
        'company_name': 'ИП Линик Ярослав Михайлович',
        'company_inn': '890305332590',
        'total_amount': 150000.00,
        'items': [
            {
                'description': 'Консультационные услуги',
                'quantity': 1,
                'price': 150000.00,
                'total': 150000.00
            }
        ],
        'payment_data': {
            'name': 'Линик Ярослав Михайлович',
            'personal_acc': '42301810900076433520',
            'bank_name': 'АО "Банк"',
            'bic': '044525974',
            'corresp_acc': '30101810145250000974',
            'payee_inn': '890305332590',
            'kpp': '',
            'sum': '150000',
            'purpose': 'Оплата по счету №7455108 от 28.08.2025'
        },
        'signatures': {
            'director': ''  # Will be populated if signature file exists
        }
    }
    
    # Check for signature file
    sig_path = 'signatures/YL_Signature.png'
    if os.path.exists(sig_path):
        try:
            with open(sig_path, 'rb') as f:
                sig_data = base64.b64encode(f.read()).decode()
                invoice_data['signatures']['director'] = sig_data
                print("✅ Signature loaded")
        except Exception as e:
            print(f"⚠️  Could not load signature: {e}")
    
    # Generate invoice
    result = generator.generate_invoice(invoice_data)
    print(f"📋 Generated: {result}")


if __name__ == "__main__":
    main()
