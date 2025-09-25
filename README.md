# 🧾 Invoice Generator

**Professional Russian invoice and service act generator with Telegram bot integration**

## 📚 **Documentation**

Complete documentation is available in the `docs/` folder:

- **[📖 README](docs/README.md)** - Overview, features, and quick start guide
- **[🚀 DEPLOYMENT](docs/DEPLOYMENT.md)** - Production deployment guide for Windows and Linux
- **[📖 USAGE](docs/USAGE.md)** - Detailed usage instructions and troubleshooting

## 🚀 **Quick Start**

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure environment**: Copy `env.template` to `.env` and edit with your settings
3. **Add signature**: Place signature image in `signatures/` folder
4. **Run bot**: `python telegram_bot.py`

## 🤖 **Features**

- ✅ **Telegram Bot Interface** - Generate documents via chat commands
- ✅ **Professional PDFs** - Invoice and service act with signatures, QR codes  
- ✅ **Live Currency Rates** - Real-time USD/RUB exchange rates from CBRF
- ✅ **Russian Localization** - Full Russian language support
- ✅ **Cross-Platform** - Works on Windows and Linux with WeasyPrint 66.0

## 📄 **Generated Documents**

- **Invoice (Счет)** - Professional invoice with QR payment codes
- **Service Act (Акт)** - Service documentation with FX calculations

## 🔧 **Technical Stack**

- **Python 3.8+** with WeasyPrint 66.0 for PDF generation
- **Telegram Bot API** for user interaction
- **CBRF API** for live currency rates
- **Jinja2 templates** for document layout

---

**📚 For complete setup and usage instructions, see the [documentation](docs/) folder.**
