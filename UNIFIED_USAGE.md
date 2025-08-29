# 🚀 Unified Document Generator

## ✨ **Simple Usage**

Generate both **Invoice** and **Act** PDFs with a single command:

```bash
python generate.py
```

That's it! 🎉

## 📋 **What You Get**

- **Invoice PDF** - Professional invoice with QR code for payment
- **Act PDF** - Service act with live FX rates from Central Bank of Russia
- **PDF Only** - No HTML files generated (configurable)
- **Auto-calculated amounts** - Uses real FX rates × base rate
- **Auto-generated dates** - Services get 26th-to-26th periods

## ⚙️ **Configuration**

All fixed data is stored in **`config.py`**:

### 🏢 Company Info
```python
COMPANY_INFO = {
    'legal_form': 'Индивидуальный предприниматель',
    'name': 'Линик Ярослав Михайлович',
    'inn': '890305332590',
    'ogrn': '325774600140091',
    # ... etc
}
```

### 👤 Client Info
```python
CLIENT_INFO = {
    'name': 'Гуринов Вадим Александрович',
    'contract_date': '2025-05-26',  # YYYY-MM-DD
}
```

### 💰 Financial Settings
```python
FINANCIAL_SETTINGS = {
    'base_rate': 16667,  # Base rate in USD
    'currency': 'USD',       # Currency for FX rates
}
```

## 🎯 **Input Required**

**Only one thing**: List of services

```python
services = [
    'Service description 1',
    'Service description 2', 
    'Service description 3'
]
```

## 📊 **Advanced Usage**

### Custom Services with Different Periods
```python
from generate_documents import UnifiedDocumentGenerator

# Mix of strings and custom periods
services = [
    'Auto-dated service',  # Gets 26th-26th dates
    {
        'description': 'Custom period service',
        'start_date': '01/01/2025',
        'end_date': '31/01/2025'
    }
]

generator = UnifiedDocumentGenerator()
results = generator.generate_both_documents(services)
```

### Generate Individual Documents
```python
# Act only
act_path = generator.generate_act_only(services)

# Invoice only (specify amount)
invoice_path = generator.generate_invoice_only(services, 1500000)
```

## 📁 **Project Structure**

```
Invoice generator/
├── generate.py              ⭐ Simple interface
├── generate_documents.py    🔧 Unified generator class
├── config.py               ⚙️  All configuration data
├── templates/
│   ├── invoice.html        📄 Invoice template
│   └── act.html           📄 Act template
├── output/                📂 Generated PDFs
└── signatures/            🖋️  Signature images
```

## 🔧 **Configuration Options**

### PDF Settings
```python
PDF_CONFIG = {
    'generate_html': False,  # PDF only, no HTML files
}
```

### Bank Details (for QR codes)
```python
BANK_INFO = {
    'personal_acc': '42301810900076433520',
    'bank_name': 'АО "Банк"',
    'bic': '044525974',
    # ... etc
}
```

## 📈 **How It Works**

1. **Act Generation**: 
   - Gets live USD→RUB rate from CBR
   - Calculates: `base_rate × fx_rate`
   - Generates service periods (26th to 26th)

2. **Invoice Generation**:
   - Uses same amount as Act
   - Generates QR code with payment details
   - Creates unique invoice number (octal date format)

3. **PDF Output**:
   - WeasyPrint generates professional PDFs
   - Includes signatures, proper formatting
   - No HTML files saved (configurable)

## 🛠️ **Customization**

To modify for different clients/projects:

1. **Edit `config.py`** - Update company, client, financial settings
2. **Run `python generate.py`** - Generate documents
3. **Check `output/`** - Your PDFs are ready!

## 📋 **Dependencies**

- **WeasyPrint** - PDF generation (with GTK3 on Windows)  
- **CBR API** - Live FX rates
- **Jinja2** - Template rendering
- **QR Code** - Payment QR generation

---

## 🎯 **TL;DR**

1. Put your services in `generate.py`
2. Run `python generate.py`  
3. Get both Invoice and Act PDFs in `output/`

**Maximum simplicity for maximum productivity!** 🚀
