# GitHub Repository Setup Instructions

## Create Repository Manually

Since GitHub authentication isn't configured, create the repository manually:

### 1. Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `invoice-generator-russia`
3. Description: `Russian Invoice Generator with QR codes (СПКР ГОСТ Р 56042-2014), automatic numbering, and PDF export. Supports both WeasyPrint and ReportLab backends.`
4. Set to **Public**
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

### 2. Initialize Local Repository

```bash
git init
git add .
git commit -m "Initial commit: Russian Invoice Generator with QR codes and signatures"
git branch -M main
git remote add origin https://github.com/YOURUSERNAME/invoice-generator-russia.git
git push -u origin main
```

### 3. Repository Structure

Your repository will contain:

```
invoice-generator-russia/
├── README.md                          # Comprehensive documentation
├── requirements.txt                   # WeasyPrint dependencies (Linux/macOS)
├── requirements_windows.txt           # ReportLab dependencies (Windows)
├── setup.py                          # Automated setup script
├── config.py                         # Default configuration
├── .gitignore                        # Git ignore rules
├── invoice_generator.py              # Main WeasyPrint version
├── invoice_generator_reportlab.py    # ReportLab version (Windows)
├── signature_utils.py                # Signature management utilities
├── example_usage.py                  # Usage examples
├── install_windows.py               # Windows installation helper
├── templates/
│   └── invoice.html                  # HTML invoice template
├── output/                           # Generated PDFs (ignored by git)
├── signatures/                       # Signature images (ignored by git)
└── sample_invoice.json              # Example JSON data structure
```

### 4. Repository Topics (Tags)

Add these topics in GitHub repository settings:

- `invoice-generator`
- `pdf-generation`
- `qr-codes`
- `russian-localization`
- `business-automation`
- `reportlab`
- `weasyprint`
- `python`

### 5. Repository Features

Enable in Settings:
- ✅ Issues
- ✅ Wiki
- ✅ Discussions (optional)
- ✅ Actions (for future CI/CD)

## Post-Creation Setup

### Create Releases

1. Go to repository → Releases → Create a new release
2. Tag version: `v1.0.0`
3. Release title: `Russian Invoice Generator v1.0.0`
4. Description:
```markdown
## ✨ Features

- 📄 Professional PDF invoice generation
- 📱 QR codes compliant with Russian СПКР standard (ГОСТ Р 56042-2014)
- 🔢 Automatic invoice numbering (octal yyyymm format)
- 🔤 Russian number-to-words conversion
- 🖊️ Digital signature support
- 💰 VAT calculations
- 🖥️ Cross-platform (Windows/Linux/macOS)

## 🔧 Technical Details

- **Windows**: Uses ReportLab backend (easier setup)
- **Linux/macOS**: Uses WeasyPrint backend (better HTML/CSS support)
- **Dependencies**: Minimal external dependencies
- **Language**: Pure Python 3.7+

## 📋 Requirements

- Python 3.7+
- See `requirements.txt` or `requirements_windows.txt`

## 🚀 Quick Start

```bash
git clone https://github.com/yourusername/invoice-generator-russia.git
cd invoice-generator-russia
python setup.py
python example_usage.py
```
```

### Add Screenshots

Take screenshots of:
1. Generated PDF invoice
2. QR code scanning result
3. Terminal output showing generation

Upload to repository as `screenshots/invoice_example.png`, etc.

## Marketing Description

Use this for README and repository description:

**English:**
> Professional Russian invoice generator with QR payment codes (GOST R 56042-2014), automatic numbering, VAT calculations, and digital signatures. Supports both WeasyPrint and ReportLab backends for maximum compatibility.

**Russian:**
> Профессиональный генератор российских счетов-фактур с QR-кодами для оплаты (ГОСТ Р 56042-2014), автоматической нумерацией, расчетом НДС и цифровыми подписями. Поддерживает WeasyPrint и ReportLab для максимальной совместимости.
