#!/usr/bin/env python3
"""
Alternative Invoice Generator using ReportLab (Windows-friendly)
Generates invoices without external dependencies
"""

import os
import qrcode
import base64
from datetime import datetime
from io import BytesIO
from num2words import num2words

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class InvoiceGeneratorReportLab:
    def __init__(self, output_dir="output"):
        """
        Initialize the invoice generator with ReportLab
        
        Args:
            output_dir (str): Directory for generated PDFs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Try to register Russian-compatible fonts
        self.setup_fonts()
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_fonts(self):
        """Try to setup fonts that support Russian characters"""
        try:
            # These fonts should support Cyrillic if available on system
            from reportlab.lib.fonts import addMapping
            self.font_name = 'Times-Roman'  # Fallback
            self.font_bold = 'Times-Bold'
        except Exception:
            # Use default fonts
            self.font_name = 'Times-Roman'
            self.font_bold = 'Times-Bold'
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=0
        ))
        
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.black,
            backColor=colors.yellow,
            leftIndent=6,
            rightIndent=6,
            spaceAfter=6,
            spaceBefore=6
        ))
    
    def generate_invoice_number(self, date=None):
        """Generate invoice number using octal conversion of yyyymm"""
        if date is None:
            date = datetime.now()
        
        yyyymm = int(f"{date.year}{date.month:02d}")
        octal_number = oct(yyyymm)[2:]
        return f"INV-{octal_number}"
    
    def generate_qr_code(self, payment_data):
        """Generate QR code compliant with СПКР (ГОСТ Р 56042-2014)"""
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
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO for ReportLab
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    def create_signature_image(self, signature_base64):
        """
        Create ReportLab Image from base64 signature data
        
        Args:
            signature_base64 (str): Base64 encoded image data
            
        Returns:
            Image: ReportLab Image object or None
        """
        try:
            if signature_base64.startswith('data:image'):
                # Remove data URL prefix
                _, base64_data = signature_base64.split(',', 1)
            else:
                base64_data = signature_base64
            
            # Decode base64
            img_data = base64.b64decode(base64_data)
            img_buffer = BytesIO(img_data)
            
            # Create ReportLab Image
            img = Image(img_buffer, width=4*cm, height=1.5*cm)
            return img
            
        except Exception as e:
            print(f"Error creating signature image: {e}")
            return None

    def sum_to_words_russian(self, amount):
        """Convert numeric amount to words in Russian"""
        try:
            rubles = int(amount)
            kopecks = int((amount - rubles) * 100)
            
            rubles_words = num2words(rubles, lang='ru')
            kopecks_words = num2words(kopecks, lang='ru') if kopecks > 0 else "ноль"
            
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
    
    def generate_invoice(self, invoice_data):
        """Generate invoice PDF using ReportLab"""
        current_date = datetime.now()
        invoice_number = self.generate_invoice_number(current_date)
        
        # Create PDF
        pdf_filename = f"{invoice_number}_{current_date.strftime('%Y%m%d')}.pdf"
        pdf_path = os.path.join(self.output_dir, pdf_filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2*cm)
        
        # Story (content) list
        story = []
        
        # Title
        title = Paragraph(f"СЧЕТ № {invoice_number}", self.styles['CustomTitle'])
        story.append(title)
        
        date_para = Paragraph(f"от {current_date.strftime('%d.%m.%Y')}", self.styles['Normal'])
        date_para.alignment = TA_CENTER
        story.append(date_para)
        story.append(Spacer(1, 20))
        
        # Company info table
        company_data = [
            ['Поставщик:', invoice_data.get('company_name', 'ООО "Ваша Компания"')],
            ['', invoice_data.get('company_address', 'г. Москва, ул. Примерная, д. 1')],
            ['', f"ИНН: {invoice_data.get('company_inn', '1234567890')}"],
            ['', f"КПП: {invoice_data.get('company_kpp', '123456789')}"],
            ['', ''],
            ['Покупатель:', invoice_data.get('client_name', '')],
            ['', invoice_data.get('client_address', '')],
        ]
        
        company_table = Table(company_data, colWidths=[3*cm, 12*cm])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(company_table)
        story.append(Spacer(1, 20))
        
        # Items table
        items_data = [['№', 'Наименование товара, работ, услуг', 'Кол-во', 'Цена', 'Сумма']]
        
        for i, item in enumerate(invoice_data.get('items', []), 1):
            items_data.append([
                str(i),
                item.get('description', ''),
                str(item.get('quantity', '')),
                f"{item.get('price', 0):,.2f}",
                f"{item.get('total', 0):,.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[1*cm, 8*cm, 2*cm, 3*cm, 3*cm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (4, 1), (4, -1), colors.yellow),  # Highlight totals
        ]))
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Totals
        totals_data = [
            ['Итого без НДС:', f"{invoice_data.get('subtotal', 0):,.2f} руб."],
            [f"НДС {invoice_data.get('vat_rate', 20)}%:", f"{invoice_data.get('vat_amount', 0):,.2f} руб."],
            ['Всего к оплате:', f"{invoice_data.get('total_amount', 0):,.2f} руб."],
        ]
        
        totals_table = Table(totals_data, colWidths=[8*cm, 4*cm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.yellow),  # Highlight amounts
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 20))
        
        # Amount in words
        amount_in_words = self.sum_to_words_russian(invoice_data.get('total_amount', 0))
        words_para = Paragraph(f"<b>Сумма прописью:</b> {amount_in_words}", self.styles['Highlight'])
        story.append(words_para)
        story.append(Spacer(1, 20))
        
        # QR Code and payment details
        qr_buffer = self.generate_qr_code(invoice_data.get('payment_data', {}))
        qr_image = Image(qr_buffer, width=4*cm, height=4*cm)
        
        payment_data = invoice_data.get('payment_data', {})
        payment_text = f"""
        <b>Банковские реквизиты:</b><br/>
        Получатель: {payment_data.get('name', '')}<br/>
        Расчетный счет: {payment_data.get('personal_acc', '')}<br/>
        Банк: {payment_data.get('bank_name', '')}<br/>
        БИК: {payment_data.get('bic', '')}<br/>
        Корр. счет: {payment_data.get('corresp_acc', '')}<br/>
        ИНН: {payment_data.get('payee_inn', '')}<br/>
        КПП: {payment_data.get('kpp', '')}<br/>
        Назначение платежа: {payment_data.get('purpose', '')}
        """
        
        payment_para = Paragraph(payment_text, self.styles['Normal'])
        
        payment_table = Table([[payment_para, qr_image]], colWidths=[12*cm, 5*cm])
        payment_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ]))
        story.append(payment_table)
        story.append(Spacer(1, 30))
        
        # Signatures
        signatures = invoice_data.get('signatures', {})
        
        if signatures.get('director') or signatures.get('accountant'):
            # Signatures with images
            director_sig = signatures.get('director')
            accountant_sig = signatures.get('accountant')
            
            sig_elements = []
            
            if director_sig:
                director_img = self.create_signature_image(director_sig)
                sig_elements.extend([
                    Paragraph('Руководитель', self.styles['Normal']),
                    director_img if director_img else Paragraph('_' * 30, self.styles['Normal'])
                ])
            else:
                sig_elements.extend([
                    Paragraph('Руководитель', self.styles['Normal']),
                    Paragraph('_' * 30, self.styles['Normal'])
                ])
            
            if accountant_sig:
                accountant_img = self.create_signature_image(accountant_sig)
                sig_elements.extend([
                    Paragraph('Главный бухгалтер', self.styles['Normal']),
                    accountant_img if accountant_img else Paragraph('_' * 30, self.styles['Normal'])
                ])
            else:
                sig_elements.extend([
                    Paragraph('Главный бухгалтер', self.styles['Normal']),
                    Paragraph('_' * 30, self.styles['Normal'])
                ])
            
            signature_table = Table([sig_elements], colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
        else:
            # Default signatures without images
            signature_data = [['Руководитель', '_' * 30, 'Главный бухгалтер', '_' * 30]]
            signature_table = Table(signature_data, colWidths=[3*cm, 5*cm, 3*cm, 5*cm])
        
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ]))
        story.append(signature_table)
        
        # Build PDF
        doc.build(story)
        return pdf_path


if __name__ == "__main__":
    # Example usage
    generator = InvoiceGeneratorReportLab()
    
    sample_data = {
        'client_name': 'ООО "Клиент"',
        'items': [
            {'description': 'Услуга 1', 'quantity': 1, 'price': 50000, 'total': 50000},
        ],
        'subtotal': 50000,
        'total_amount': 50000,
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
