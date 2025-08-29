#!/usr/bin/env python3
"""
Act Generator - Generate service completion acts with FX rates
"""

import os
import base64
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from jinja2 import Environment, FileSystemLoader
from cbr_simple import CBRClient
from config import COMPANY_INFO, FINANCIAL_SETTINGS

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)


class ActGenerator:
    def __init__(self, output_dir="output", templates_dir="templates"):
        """
        Initialize the act generator
        
        Args:
            output_dir (str): Directory for generated PDFs
            templates_dir (str): Directory containing HTML templates
        """
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
        # Initialize CBR client
        self.cbr_client = CBRClient()
        
        if not WEASYPRINT_AVAILABLE:
            print("⚠️  WeasyPrint not available. Only HTML output will be generated.")
            if 'WEASYPRINT_ERROR' in globals():
                print(f"   Error: {WEASYPRINT_ERROR}")
    
    def get_default_periods(self):
        """
        Generate default service periods (26th of prev month to 26th of current month)
        
        Returns:
            list: List of 4 periods with start and end dates
        """
        today = date.today()
        
        # Current period: 26th of prev month to 26th of current month
        current_start = (today.replace(day=1) - relativedelta(months=1)).replace(day=26)
        current_end = today.replace(day=26)
        
        periods = []
        
        # Generate 4 periods going backwards
        for i in range(4):
            period_end = current_end - relativedelta(months=i)
            period_start = current_start - relativedelta(months=i)
            
            periods.append({
                'start_date': period_start.strftime("%d.%m.%Y"),
                'end_date': period_end.strftime("%d.%m.%Y"),
                'start_date_obj': period_start,
                'end_date_obj': period_end
            })
        
        # Reverse to get chronological order
        return list(reversed(periods))
    
    def get_fx_rate(self, currency='USD', date_req=None):
        """
        Get FX rate from CBR
        
        Args:
            currency (str): Currency code (default: 'USD')
            date_req (date): Date for rate (default: today)
            
        Returns:
            Decimal: Exchange rate or None if failed
        """
        if date_req is None:
            date_req = date.today()
        
        try:
            rate = self.cbr_client.get_rate(currency, date_req)
            if rate:
                return rate
            else:
                print(f"❌ Could not get {currency} rate for {date_req}")
                return None
        except Exception as e:
            print(f"❌ Error getting FX rate: {e}")
            return None
    
    def generate_act_number(self):
        """Generate act number based on current date"""
        today = date.today()
        return f"{today.strftime('%d%m')}"
    
    def load_signature(self, signature_path='signatures/YL_Signature.png'):
        """Load signature image if available"""
        if os.path.exists(signature_path):
            try:
                with open(signature_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            except Exception as e:
                print(f"⚠️  Could not load signature from {signature_path}: {e}")
        return None
    
    def process_services_with_dates(self, services_input):
        """
        Process services input to ensure all have start_date and end_date
        
        Args:
            services_input (list): Either list of strings (descriptions) or 
                                 list of dicts with description, start_date, end_date
                                 
        Returns:
            list: List of service dicts with description, start_date, end_date
        """
        if not services_input:
            return []
        
        result_services = []
        
        for i, service in enumerate(services_input):
            if isinstance(service, str):
                # Service is just a description string              
                today = date.today()
                result_services.append({
                    'description': service,
                    'start_date': (today.replace(day=1) - relativedelta(months=1)).replace(day=26).strftime("%d/%m/%Y"),
                    'end_date': today.replace(day=26).strftime("%d/%m/%Y")
                })
                
            elif isinstance(service, dict):
                # Service is already a dictionary
                if 'start_date' in service and 'end_date' in service:
                    # Already has dates, use as-is
                    result_services.append(service)
                else:
                    # Has description but missing dates, add them                    
                    today = date.today()
                    result_services.append({
                        'description': service.get('description', ''),
                        'start_date': (today.replace(day=1) - relativedelta(months=1)).replace(day=26).strftime("%d/%m/%Y"),
                        'end_date': today.replace(day=26).strftime("%d/%m/%Y")
                    })
            else:
                print(f"⚠️  Invalid service format at index {i}: {service}")
                continue
        
        return result_services
    
    def generate_act(self, 
                     services_list,
                     company_info,
                     client_info,
                     financial_settings,
                     signature_data):
        """
        Generate act document
        
        Args:
            services_list (list): List of service dictionaries with description, start_date, end_date
            client_info (dict): Client information
            company_info (dict): Company information
            financial_settings (dict): Financial settings
            signature_data (str): Signature data (REQUIRED - cannot be None)
            
        Returns:
            str: Path to generated PDF or HTML
            
        Raises:
            ValueError: If contract_date or customer_name is None
        """
        
        # Generate act data
        today = date.today()
        
        # Process services to ensure they have dates
        if services_list is None:
            # Default services
            periods = self.get_default_periods()
            services_list = []
            for i, period in enumerate(periods):
                services_list.append({
                    'description': "Анализ и реализация инвестиционных проектов (Кракен, Citymall)",
                    'start_date': period['start_date'],
                    'end_date': period['end_date']
                })
        else:
            # Process provided services to add dates if needed
            services_list = self.process_services_with_dates(services_list)
        
        # Get current FX rate - MUST succeed or return None
        fx_rate = self.get_fx_rate(financial_settings['currency'], today)
        if fx_rate is None:
            print(f"❌ Cannot generate act: Failed to get {financial_settings['currency']} exchange rate from CBR")
            return None
        
        # Calculate total value (base rate * fx_rate)
        total_value = int(financial_settings['base_rate'] * fx_rate)
        
        # Required parameters validation
        if client_info['contract_date'] is None:
            raise ValueError("contract_date is required and cannot be None")
        if client_info['name'] is None:
            raise ValueError("customer_name is required and cannot be None")
        
        year, month, day = map(int, client_info['contract_date'].split('-'))
        contract_date = date(year, month, day)
        
        # Prepare template data matching new template
        template_data = {
            'document': {
                'day': today.strftime("%d"),
                'month_name': self.get_russian_month(today.month),
                'year': today.year
            },
            'customer': {
                'name': client_info['name'],
                # Convert "LASTNAME FIRSTNAME THIRDNAME" to "F. T. LASTNAME"
                # If only one name is present, use as is
                'signature_name': (
                    f"{name_parts[1][0]}.{name_parts[2][0]}. {name_parts[0]}"
                    if (len((name_parts := client_info['name'].split())) == 3)
                    else client_info['name']
                )
            },
            'contractor': {
                'legal_form': company_info['legal_form'],
                'legal_form_short': company_info['legal_form_short'],
                'name': company_info['name'],
                'ogrnip': company_info['ogrnip'],
                'inn': company_info['inn'],
                'signature_name': company_info['signature_name']
            },
            'contract': {
                'day': contract_date.strftime("%d"),
                'month_name': self.get_russian_month(contract_date.month),
                'year': contract_date.year
            },
            'services': services_list,
            'totals': {
                'value': total_value,
                'fx_rate': fx_rate
            },
            'signatures': {
                'director': signature_data
            }
        }
        
        # Load and render template
        template = self.env.get_template('act.html')
        html_content = template.render(**template_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m")
        filename = f"Акт_{timestamp}"
        
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
                weasyprint.HTML(string=html_content, base_url=self.templates_dir).write_pdf(pdf_path)
                print(f"✅ PDF generated with WeasyPrint: {pdf_path}")
                return pdf_path
            except Exception as e:
                print(f"❌ WeasyPrint error: {e}")
        
        # Fallback - if HTML is disabled and PDF failed, return None
        if html_path:
            print(f"📄 HTML generated: {html_path}")
            print("💡 To create PDF manually:")
            print("   1. Open the HTML file in a web browser")
            print("   2. Press Ctrl+P (Print)")
            print("   3. Choose 'Save as PDF' as destination")
            return html_path
        else:
            print("❌ PDF generation failed and HTML generation is disabled")
            return None
    
    def get_russian_month(self, month_num):
        """Convert month number to Russian month name"""
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        return months.get(month_num, 'января')


def main():
    """Test the act generator"""
    generator = ActGenerator()
    
    print("🧾 Act Generator")
    print("=" * 50)
    
    # Generate act with default settings
    print("\n📋 Generating act...")
    result_path = generator.generate_act(base_rate=FINANCIAL_SETTINGS['base_rate'])
    print(f"✅ Act generated: {result_path}")


if __name__ == "__main__":
    main()
