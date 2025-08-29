# Invoice Generator - Usage Guide

## ✅ Current Status

The invoice generator is now fully functional with recent improvements:
- ✅ **GTK3 + WeasyPrint** working perfectly on Windows
- ✅ **Professional template design** with modern Aptos/Calibri fonts
- ✅ **Enhanced layout** with improved margins and typography  
- ✅ **Signature integration** from YL_Signature (black).jpg
- ✅ **QR codes** compliant with СПКР ГОСТ Р 56042-2014
- ✅ **Improved Russian text rendering** with proper currency formatting

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
.\venv\Scripts\activate
```

### 2. Generate Invoice
```bash
python generate_invoice.py
```

This will create:
- `output/INV-613414_YYYYMMDD_HHMMSS.pdf` - Professional invoice in PDF format
- `output/INV-613414_YYYYMMDD_HHMMSS.html` - HTML version for debugging

## 🏆 **Recommended Generator: `invoice_generator_html.py`**

**Why this is the best choice for Windows with GTK3:**
- ✅ **Modern design** with Aptos/Calibri fonts (12pt)
- ✅ **Perfect Russian text** rendering with proper currency formatting
- ✅ **Professional layout** with optimized margins and spacing
- ✅ **Signature integration** working flawlessly  
- ✅ **QR codes** with dynamic invoice numbering in payment purpose
- ✅ **Clean table borders** with light grey styling
- ✅ **Enhanced typography** for better readability

## 📊 **Available Generators Comparison**

| Generator | Status | Best For | Russian Support | Dependencies |
|-----------|--------|----------|-----------------|--------------|
| **`invoice_generator_html.py`** | ⭐ **RECOMMENDED** | Windows + GTK3 | ✅ Perfect | WeasyPrint + GTK3 |
| `invoice_generator_reportlab.py` | 🥈 Backup | No GTK3 systems | ⚠️ Limited | ReportLab only |
| `invoice_generator.py` | 🥉 Legacy | Not recommended | ⚠️ Basic | WeasyPrint (old) |

## 🎯 Customization

### Create Custom Invoice
```python
from generate_invoice import create_invoice

# Custom invoice
create_invoice(
    service_description="Web Development",
    amount=85000.00,
    client_name="ООО \"Клиент\"",
    purpose="Payment for contract №123"
)
```

### Invoice Data Structure
The system uses your personal business data:
- **Company**: ИП Линик Ярослав Михайлович
- **INN**: 890305332590
- **Bank**: АО "Банк"
- **Account**: 42301810900076433520
- **BIC**: 044525974

## 📁 Project Structure

```
Invoice generator/
├── venv/                           # Virtual environment
├── templates/
│   ├── invoice_old.html               # Old template (not used)
│   └── invoice.html              # Current professional template ✅
├── signatures/
│   └── YL_Signature (black).jpg   # Your signature ✅
├── output/                        # Generated PDFs and HTML
├── generate_invoice.py            # Main script ✅
├── invoice_generator_html.py      # Core generator
├── config.py                     # Business configuration
└── requirements_windows.txt       # Dependencies
```

## 🔧 Advanced Usage

### Direct Generator Usage
```python
from invoice_generator_html import InvoiceGeneratorHTML

generator = InvoiceGeneratorHTML()
pdf_path = generator.generate_invoice(invoice_data)
```

### Template Features (invoice2.html)
The current template provides:
- **Modern typography**: Aptos/Calibri fonts (12pt) for professional appearance
- **Optimized layout**: 3cm top margin, 1.5cm sides for perfect A4 formatting  
- **Enhanced bank details**: Clean borders with light grey styling
- **Professional table design**: Subtle borders and improved spacing
- **Signature integration**: Automatic signature placement with proper positioning
- **Dynamic QR codes**: Invoice number automatically included in payment purpose
- **Russian compliance**: Meets Russian accounting and invoice standards

## 📋 Key Features

- ✅ **Modern design**: Aptos/Calibri fonts with optimized typography (12pt)
- ✅ **Professional layout**: Perfect A4 margins (3cm top, 1.5cm sides)
- ✅ **Automatic invoice numbering** (octal conversion of YYYYMM)
- ✅ **Dynamic QR codes** (СПКР compliant with invoice number in purpose)
- ✅ **Enhanced Russian formatting** (proper currency amount in words)
- ✅ **Digital signature integration** (automatic YL_Signature placement)
- ✅ **Clean table design** (light grey borders, improved spacing)
- ✅ **Perfect UTF-8 support** (flawless Russian text rendering)
- ✅ **Production ready** (GTK3 + WeasyPrint optimized for Windows)

## 🎉 Production Ready!

**Your system is now optimized and production-ready!**

### Quick Generate:
```bash
python generate_invoice.py
```

### What You Get:
- **Professional invoices** with modern Aptos/Calibri typography
- **Perfect Russian text** rendering with enhanced currency formatting  
- **Automatic signatures** properly positioned on the signature line
- **Dynamic QR codes** with invoice number in payment purpose
- **Clean, modern design** meeting Russian accounting standards

**Recommended workflow**: Use `invoice_generator_html.py` via `generate_invoice.py` for best results on Windows with GTK3!
