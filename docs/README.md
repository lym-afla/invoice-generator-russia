# 🧾 Invoice Generator

**Professional invoice and service act generator with Telegram bot integration**

## 📋 **Overview**

This system automatically generates professional Russian invoices and service acts in PDF format, featuring:

- 🤖 **Telegram Bot Interface** - Generate documents via chat commands
- 📄 **Professional PDFs** - Invoice and service act with signatures, QR codes
- 💱 **Live Currency Rates** - Real-time USD/RUB exchange rates from CBRF
- 🔢 **Smart Numbering** - Automatic invoice numbering with octal date conversion
- 📱 **QR Payment Codes** - СПКР-compliant QR codes for payments
- 🖊️ **Digital Signatures** - Embedded signature images
- 🇷🇺 **Russian Localization** - Full Russian language support

## 🚀 **Quick Start**

### **1. Installation**

```bash
# Clone the repository
git clone [your-repo-url]
cd invoice-generator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Configuration**

```bash
# Copy environment template
cp env.template .env

# Edit with your credentials
nano .env  # or use any text editor
```

**Required environment variables:**
```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Company Data
COMPANY_NAME=Your Company Name
COMPANY_INN=1234567890
COMPANY_OGRNIP=123456789012345

# Bank Details
BANK_NAME=Your Bank Name
BANK_PERSONAL_ACC=12345678901234567890
BANK_BIC=123456789
BANK_CORRESP_ACC=12345678901234567890

# Client Data
CLIENT_NAME=Client Name
CLIENT_CONTRACT_DATE=2025-01-01

# Financial Settings
BASE_RATE=16667
CURRENCY=USD
```

### **3. Add Signature**

Place your signature image in the `signatures/` folder:
```
signatures/YL_Signature.png
```

### **4. Run the Bot**

```bash
python telegram_bot.py
```

## 💬 **Telegram Bot Commands**

- **📋 Создать документы** - Generate invoice and service act
- **📊 Статистика** - View generation statistics  
- **❓ Помощь** - Get help and instructions

### **Document Generation Flow**

1. **Start generation** - Use "📋 Создать документы" button
2. **Review previous services** - Bot shows last used services
3. **Update services** - Enter new services (one per line)
4. **Confirm date** - Confirm or change document date
5. **Receive documents** - Get PDF files delivered to chat

## 📄 **Generated Documents**

### **Invoice (Счет)**
- Professional invoice layout
- QR code for payment (СПКР-compliant)
- Automatic sum-to-words conversion
- Digital signature integration
- Unique invoice numbering

### **Service Act (Акт)**
- Service period documentation
- Live FX rate from CBRF
- Total calculation in RUB
- Same professional styling
- Monthly numbering

## 🔧 **Technical Stack**

- **Python 3.8+** - Core language
- **WeasyPrint 66.0** - PDF generation (works on Windows & Linux)
- **Jinja2** - HTML templating
- **python-telegram-bot** - Bot framework
- **qrcode** - QR code generation
- **num2words** - Number to words conversion
- **requests** - CBRF API integration

## 📁 **Project Structure**

```
invoice-generator/
├── docs/                    # Documentation
├── templates/               # HTML templates
│   ├── invoice.html         # Invoice template
│   └── act.html            # Service act template
├── signatures/              # Signature images
├── output/                  # Generated PDFs
├── telegram_bot.py          # Main bot application
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```

## 🌟 **Features**

### **Document Features**
- ✅ **Professional layout** - Pixel-perfect design
- ✅ **Russian language** - Full localization
- ✅ **QR payments** - GOST-compliant QR codes
- ✅ **Digital signatures** - Embedded signature images
- ✅ **Live rates** - Real-time CBRF exchange rates
- ✅ **Smart numbering** - Automatic invoice numbering

### **Bot Features**
- ✅ **Persistent keyboard** - Always-available buttons
- ✅ **Service memory** - Remembers previous services
- ✅ **Date confirmation** - Flexible document dating
- ✅ **Error handling** - Graceful failure management
- ✅ **File delivery** - Direct PDF delivery to chat

### **Technical Features**
- ✅ **Cross-platform** - Works on Windows and Linux
- ✅ **Lightweight** - Minimal dependencies
- ✅ **Secure config** - Environment variable management
- ✅ **Production ready** - Service deployment support

## 🔐 **Security**

- **Environment variables** - Sensitive data in `.env` file
- **Chat authorization** - Bot restricted to authorized chat ID
- **Input validation** - Secure data handling
- **Error logging** - Comprehensive error tracking

## 📊 **Usage Statistics**

The bot tracks:
- Total documents generated
- Generation history
- Last used services
- Error rates

## 🆘 **Troubleshooting**

### **Common Issues**

**Bot not responding:**
- Check `TELEGRAM_BOT_TOKEN` in `.env`
- Verify bot is running: `python telegram_bot.py`

**PDF generation fails:**
- Ensure WeasyPrint 66.0 is installed: `pip install weasyprint==66.0`
- Check signature file exists in `signatures/` folder

**CBRF rate fetch fails:**
- Check internet connection
- CBRF API may be temporarily unavailable

**Russian text issues:**
- Ensure UTF-8 encoding in templates
- WeasyPrint 66.0 handles Russian text correctly

## 📚 **Documentation**

- **README.md** - This overview and quick start
- **DEPLOYMENT.md** - Production deployment guide
- **USAGE.md** - Detailed usage instructions

## 🤝 **Support**

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review the detailed usage documentation
3. Check bot logs for error messages

## 📄 **License**

This project is for internal business use. Modify according to your needs.

---

**🎯 Ready to generate professional Russian invoices and service acts with just a few Telegram messages!**
