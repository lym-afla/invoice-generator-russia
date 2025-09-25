# 📖 Usage Guide

## 🎯 **Overview**

This guide covers detailed usage of the Invoice Generator system, including Telegram bot commands, configuration options, and advanced features.

## 🤖 **Telegram Bot Usage**

### **Starting the Bot**

1. **Run the bot application**:
   ```bash
   python telegram_bot.py
   ```

2. **Send `/start` command** in your authorized Telegram chat

3. **Use the keyboard buttons** that appear:
   - **📋 Создать документы** - Generate documents
   - **📊 Статистика** - View statistics
   - **❓ Помощь** - Get help

### **Document Generation Process**

#### **Step 1: Initiate Generation**
- Click **📋 Создать документы** button
- Bot will show your previous services (if any)

#### **Step 2: Service Input**
Format options for entering services:

**Simple format** (description only):
```
Website development
System maintenance
Technical support
Consulting services
```

**Detailed format** (with dates):
```
Website development | 2025-08-26 | 2025-09-26
System maintenance | 2025-08-26 | 2025-09-26
```

**Mixed format**:
```
Website development
System maintenance | 2025-08-26 | 2025-09-26
Technical support
```

#### **Step 3: Date Confirmation**
- Bot suggests today's date
- Type new date if needed: `2025-09-25`
- Or confirm with "Подтвердить"

#### **Step 4: Document Delivery**
- Bot generates both invoice and service act
- PDF files are sent directly to chat
- Generation typically takes 5-10 seconds

### **Bot Commands Reference**

| Command | Description | Usage |
|---------|-------------|-------|
| `/start` | Initialize bot and show main menu | `/start` |
| `/help` | Show help information | `/help` |
| `/status` | View generation statistics | `/status` |
| `/generate` | Start document generation | `/generate` |

### **Bot Responses**

**Success Messages:**
- ✅ Document generation completed
- 📄 Files delivered to chat
- 💾 Services saved for next time

**Error Messages:**
- ❌ CBRF rate fetch failed
- ⚠️ Missing required configuration
- 🔧 PDF generation issues

## ⚙️ **Configuration**

### **Environment Variables (`.env`)**

#### **Required Settings**

**Telegram Configuration:**
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**Company Information:**
```env
COMPANY_NAME=ИП Иванов Иван Иванович
COMPANY_INN=1234567890
COMPANY_OGRNIP=123456789012345
```

**Bank Details:**
```env
BANK_NAME=АО "ТБанк"
BANK_PERSONAL_ACC=40702810900076433520
BANK_BIC=044525974
BANK_CORRESP_ACC=30101810145250000974
```

**Client Information:**
```env
CLIENT_NAME=ООО "Клиент"
CLIENT_CONTRACT_DATE=2025-05-26
```

**Financial Settings:**
```env
BASE_RATE=16667
CURRENCY=USD
```

#### **Optional Settings**

**PDF Configuration:**
```env
PDF_GENERATE_HTML=false  # Set to true for debugging
```

### **Configuration Validation**

Test your configuration:
```bash
python -c "
from config import *
print('Company:', COMPANY_INFO['name'])
print('Client:', CLIENT_INFO['name'])
print('Bot token configured:', bool(TELEGRAM_CONFIG['bot_token']))
"
```

## 📄 **Document Details**

### **Invoice (Счет)**

**Generated Information:**
- **Invoice Number**: Auto-generated using octal conversion of YYYYMM
- **Invoice Date**: Specified generation date
- **Amount**: Calculated from service act total
- **QR Code**: СПКР-compliant payment QR code
- **Signature**: Embedded signature image

**QR Code Content** (GOST Р 56042-2014 format):
```
ST00012|Name=ИП Иванов И.И.|PersonalAcc=40702810900076433520|BankName=АО "ТБанк"|BIC=044525974|CorrespAcc=30101810145250000974|PayeeINN=1234567890|Sum=1399884|Purpose=Оплата по счету №123456 от 25.09.2025
```

### **Service Act (Акт)**

**Generated Information:**
- **Document Date**: Specified generation date  
- **Service Period**: 26th of previous month to 26th of current month
- **FX Rate**: Live USD/RUB rate from CBRF API
- **Total Amount**: BASE_RATE × FX_RATE × number_of_services
- **Signature**: Same signature as invoice

**Automatic Date Calculation:**
- **Start Date**: 26th of previous month
- **End Date**: 26th of current month
- **Document Date**: User-specified or today

## 🔧 **Advanced Usage**

### **Programmatic Document Generation**

```python
from generate_documents import UnifiedDocumentGenerator
from config import COMPANY_INFO, BANK_INFO, CLIENT_INFO, FINANCIAL_SETTINGS

# Initialize generator
generator = UnifiedDocumentGenerator()

# Define services
services = [
    "Website development",
    "System maintenance", 
    "Technical support"
]

# Generate documents
results = generator.generate_both_documents(
    services_list=services,
    company_info=COMPANY_INFO,
    bank_info=BANK_INFO,
    client_info=CLIENT_INFO,
    financial_settings=FINANCIAL_SETTINGS,
    signature_path="signatures/YL_Signature.png"
)

print("Generated files:", results)
```

### **Custom Service Dates**

```python
# Services with custom dates
services = [
    {
        "description": "Website development",
        "start_date": "2025-08-01", 
        "end_date": "2025-08-31"
    },
    {
        "description": "System maintenance",
        "start_date": "2025-09-01",
        "end_date": "2025-09-30" 
    }
]
```

### **Signature Management**

**Supported formats:**
- PNG (recommended)
- JPG/JPEG
- GIF
- Transparent backgrounds supported

**Recommended specifications:**
- **Size**: 300x100 - 500x200 pixels
- **Format**: PNG with transparency
- **Color**: Black or dark blue
- **Background**: Transparent

**Signature placement:**
- **Invoice**: Bottom right, overlapping signature line
- **Service Act**: In signature table cell

## 📊 **Data Sources**

### **CBRF Currency Rates**

**API Endpoint**: Central Bank of Russia daily rates
**Update Schedule**: Daily around 15:00 Moscow time
**Fallback**: Error if rate unavailable (no fallback rate)

**Rate Calculation:**
```
Total Amount (RUB) = BASE_RATE (USD) × FX_Rate × Number_of_Services
```

### **Invoice Numbering**

**Format**: Octal conversion of YYYYMM
- **2025-09** → **755031** (octal)
- **2025-10** → **755032** (octal)
- **2025-11** → **755033** (octal)

## 🗂️ **File Management**

### **Output Directory Structure**
```
output/
├── invoice_755031.pdf      # Generated invoice
├── Акт_202509.pdf         # Generated service act
└── [timestamp files]      # Historical documents
```

### **Automatic Cleanup**
- **HTML files**: Deleted after PDF generation (if debugging disabled)
- **Old files**: Manual cleanup recommended monthly
- **Bot data**: Stored in `bot_data.json`

### **File Naming Convention**
- **Invoice**: `invoice_{octal_number}.pdf`
- **Service Act**: `Акт_{YYYYMM}.pdf`
- **Timestamp**: Files include timestamp if generated multiple times per month

## 🔍 **Troubleshooting**

### **Common Issues**

#### **CBRF Rate Fetch Fails**
```
Error: Could not fetch USD rate from CBRF
```
**Solutions:**
- Check internet connection
- Wait and retry (CBRF API may be temporarily down)
- CBRF updates rates daily around 15:00 Moscow time

#### **PDF Generation Fails**
```
Error: WeasyPrint failed
```
**Solutions:**
- Verify WeasyPrint 66.0 is installed: `pip list | grep weasyprint`
- Check signature file exists: `ls signatures/`
- Ensure sufficient disk space

#### **Bot Not Responding**
```
Bot doesn't respond to commands
```
**Solutions:**
- Check bot token: `echo $TELEGRAM_BOT_TOKEN`
- Verify chat ID authorization
- Check bot process is running: `ps aux | grep telegram_bot`

#### **Russian Text Issues**
```
Russian characters appear as squares or question marks
```
**Solutions:**
- Ensure UTF-8 encoding in templates
- Update WeasyPrint: `pip install --upgrade weasyprint`
- Check system locale supports UTF-8

### **Debug Mode**

Enable HTML generation for debugging:
```env
PDF_GENERATE_HTML=true
```

This creates HTML files alongside PDFs for template debugging.

### **Log Analysis**

**Bot logs** (if running as service):
```bash
sudo journalctl -u invoice-bot -f
```

**Direct execution logs**:
```bash
python telegram_bot.py
```

Look for:
- ✅ Successful PDF generation
- ❌ Error messages
- 📊 CBRF rate fetch results
- 🤖 Bot initialization status

## 📈 **Performance Tips**

### **Optimization**
- **Signature optimization**: Use optimized PNG files (~50KB)
- **Template caching**: Templates are cached automatically
- **Rate limiting**: CBRF API has built-in rate limiting

### **Resource Usage**
- **Memory**: ~50MB for bot + document generation
- **CPU**: Minimal, peaks during PDF generation
- **Disk**: ~1-2MB per document pair
- **Network**: CBRF API calls (~1KB per request)

## 🛡️ **Security Best Practices**

### **Environment Security**
- **Never commit `.env`** to version control
- **Restrict file permissions**: `chmod 600 .env`
- **Use strong bot tokens**: Regenerate if compromised
- **Limit chat access**: Only authorized chat IDs

### **Data Protection**
- **Client data**: Stored only in configuration
- **Generated documents**: Consider automatic cleanup
- **Bot data**: Contains only service descriptions and statistics

---

**🎯 You're now ready to use the invoice generator system effectively!**

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).  
For system overview, see [README.md](README.md).
