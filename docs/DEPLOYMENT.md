# 🚀 Production Deployment Guide

## 🎯 **Deployment Options**

The invoice generator works on both **Windows** and **Linux** with WeasyPrint 66.0. Choose based on your infrastructure:

- **Windows Server** - Direct deployment, works out of the box
- **Linux Server** - Recommended for production (Ubuntu 20.04+ LTS)
- **Cloud VPS** - Cost-effective option (~$5-10/month)

## 👤 **User Configuration**

### **Recommended: Dedicated User**
The setup script creates a dedicated `invoice-bot` user for security:
- ✅ **Isolated permissions** - Cannot access other system files
- ✅ **Process isolation** - Separate from other applications
- ✅ **Clear ownership** - All app files owned by app user
- ✅ **Systemd integration** - Clean service management

### **Alternative: Existing User**
If you prefer to use an existing user (like `user1`):

1. **Edit the setup script**:
   ```bash
   # In scripts/setup-service.sh
   APP_USER="user1"  # Change from "invoice-bot"
   ```

2. **Run setup**:
   ```bash
   sudo ./scripts/setup-service.sh
   ```

The script will adapt to use your existing user instead of creating a new one.

## 🐧 **Ubuntu Server Deployment (Recommended)**

### **System Requirements**
- **Ubuntu 20.04+ LTS**
- **2GB RAM minimum** (4GB recommended)
- **Python 3.8+**
- **500MB disk space**

### **1. System Setup**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install WeasyPrint system dependencies
sudo apt install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libgtk-3-0

# Install Git for deployment
sudo apt install -y git
```

### **2. Deploy Application**

```bash
# Create application directory
sudo mkdir -p /opt/invoice-generator
sudo chown $USER:$USER /opt/invoice-generator

# Clone repository
cd /opt/invoice-generator
git clone [your-repo-url] .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Configuration**

```bash
# Copy environment template
cp env.template .env

# Edit configuration
nano .env
```

**Production `.env` configuration:**
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyZ
TELEGRAM_CHAT_ID=123456789

# Company Information
COMPANY_NAME=Your Company Name
COMPANY_INN=1234567890
COMPANY_OGRNIP=123456789012345

# Bank Details
BANK_NAME=Your Bank Name
BANK_PERSONAL_ACC=40702810900076433520
BANK_BIC=044525225
BANK_CORRESP_ACC=30101810400000000225

# Client Information
CLIENT_NAME=Client Company Name
CLIENT_CONTRACT_DATE=2025-01-01

# Financial Settings
BASE_RATE=16667
CURRENCY=USD
```

### **4. Upload Signature**

```bash
# Create signatures directory if not exists
mkdir -p signatures

# Upload your signature file (use scp, sftp, or direct copy)
# Example with scp:
# scp YL_Signature.png user@server:/opt/invoice-generator/signatures/
```

### **5. Test Installation**

```bash
# Test document generation
python3 -c "
from generate_documents import UnifiedDocumentGenerator
from config import COMPANY_INFO, BANK_INFO, CLIENT_INFO, FINANCIAL_SETTINGS

generator = UnifiedDocumentGenerator()
results = generator.generate_both_documents(
    ['Test service deployment'],
    COMPANY_INFO, BANK_INFO, CLIENT_INFO, FINANCIAL_SETTINGS,
    'signatures/YL_Signature.png'
)
print('✅ Test successful:', bool(results))
"

# Test bot initialization
python3 -c "
from telegram_bot import DocumentBot
bot = DocumentBot()
print('✅ Bot initialized successfully')
"
```

### **6. Setup Service and Management**

**Automated setup (Recommended):**
```bash
# Run the comprehensive setup script
sudo ./scripts/setup-service.sh
```

This script will:
- ✅ Create dedicated `invoice-bot` user (recommended for security)
- ✅ Set up proper file permissions
- ✅ Create systemd service with security hardening
- ✅ Create management symlink: `sudo invoice-bot <command>`
- ✅ Enable service for automatic startup

**Manual setup (Alternative):**
```bash
# Create service file
sudo nano /etc/systemd/system/invoice-bot.service
```

**Service configuration:**
```ini
[Unit]
Description=Invoice Generator Telegram Bot
After=network.target

[Service]
Type=simple
User=invoice-bot
Group=invoice-bot
WorkingDirectory=/opt/invoice-generator
Environment=PATH=/opt/invoice-generator/venv/bin
ExecStart=/opt/invoice-generator/venv/bin/python telegram_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/invoice-generator

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable invoice-bot

# Start service
sudo systemctl start invoice-bot

# Check status
sudo systemctl status invoice-bot
```

### **7. Service Management**

**Using the management script (Recommended):**
```bash
# Start the service
sudo invoice-bot start

# Stop the service
sudo invoice-bot stop

# Restart the service
sudo invoice-bot restart

# Check detailed status
sudo invoice-bot status

# View logs (various options)
sudo invoice-bot logs                     # Service logs
sudo invoice-bot logs -f                  # Follow logs in real-time
sudo invoice-bot logs -t python -n 100   # Python logs, 100 lines
sudo invoice-bot logs -t error            # Error logs only

# Update from git and restart
sudo invoice-bot update
```

**Traditional systemd commands:**
```bash
# View real-time logs
sudo journalctl -u invoice-bot -f

# Restart service
sudo systemctl restart invoice-bot

# Stop service
sudo systemctl stop invoice-bot

# Check service status
sudo systemctl status invoice-bot
```

## 🖥️ **Windows Server Deployment**

### **1. System Requirements**
- **Windows Server 2019+** or **Windows 10/11**
- **Python 3.8+** installed
- **2GB RAM minimum**

### **2. Installation**

```powershell
# Clone repository
git clone [your-repo-url] C:\invoice-generator
cd C:\invoice-generator

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Configuration**
- Copy `env.template` to `.env`
- Edit `.env` with your settings
- Place signature in `signatures\` folder

### **4. Run as Windows Service**

Use tools like **NSSM** (Non-Sucking Service Manager):

```powershell
# Download NSSM and install service
nssm install InvoiceBot "C:\invoice-generator\venv\Scripts\python.exe"
nssm set InvoiceBot Parameters "telegram_bot.py"
nssm set InvoiceBot AppDirectory "C:\invoice-generator"
nssm start InvoiceBot
```

## ☁️ **Cloud Deployment Options**

### **DigitalOcean Droplet**
- **$6/month** - 1GB RAM, 25GB SSD
- **Ubuntu 20.04** pre-configured
- **Easy deployment** with SSH access

### **AWS EC2**
- **t3.micro** - Free tier eligible
- **Amazon Linux 2** or **Ubuntu**
- **Elastic IP** for static address

### **Google Cloud Platform**
- **e2-micro** - Free tier
- **Ubuntu 20.04 LTS**
- **Preemptible instances** for cost savings

### **VPS Providers**
- **Hetzner** - €3-5/month
- **Linode** - $5/month
- **Vultr** - $6/month

## 🔐 **Security Considerations**

### **Server Security**
```bash
# Basic firewall setup
sudo ufw allow ssh
sudo ufw allow 22/tcp
sudo ufw --force enable

# Disable root login (recommended)
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Keep system updated
sudo apt update && sudo apt upgrade -y
```

### **Application Security**
- **Environment variables** - Never commit `.env` to version control
- **File permissions** - Restrict access to configuration files
- **Bot token security** - Keep Telegram bot token secure
- **Chat authorization** - Bot only responds to authorized chat ID

### **Backup Strategy**
```bash
# Backup script example
#!/bin/bash
tar -czf backup-$(date +%Y%m%d).tar.gz \
    .env \
    signatures/ \
    bot_data.json \
    output/

# Upload to cloud storage or remote location
```

## 📊 **Performance Optimization**

### **System Optimization**
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize Python performance
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
```

### **Memory Management**
- **Monitor usage**: `htop` or `top`
- **Set swap**: Add swap file if RAM is limited
- **Process limits**: Configure systemd service limits if needed

## 🔄 **Updates and Maintenance**

### **Code Updates**

**Automated update (Recommended):**
```bash
# Single command to update everything
sudo invoice-bot update
```

This command will:
- ✅ Fetch latest changes from git repository
- ✅ Stop service gracefully
- ✅ Pull latest code
- ✅ Update Python dependencies
- ✅ Maintain proper file permissions
- ✅ Restart service
- ✅ Verify successful startup

**Manual update:**
```bash
# Pull latest changes
cd /opt/invoice-generator
sudo -u invoice-bot git pull origin main

# Update dependencies if needed
sudo -u invoice-bot bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Restart service
sudo invoice-bot restart
```

### **Regular Maintenance**
```bash
# Clean old output files (monthly)
find output/ -name "*.pdf" -mtime +30 -delete
find output/ -name "*.html" -mtime +7 -delete

# Rotate logs
sudo journalctl --vacuum-time=7d

# System updates
sudo apt update && sudo apt upgrade -y
```

## 📈 **Monitoring**

### **Service Health**
```bash
# Check if service is running
systemctl is-active invoice-bot

# Check service uptime
systemctl show invoice-bot --property=ActiveEnterTimestamp

# Monitor resource usage
sudo systemctl status invoice-bot
```

### **Log Analysis**
```bash
# Recent errors
sudo journalctl -u invoice-bot --since "1 hour ago" -p err

# Bot activity
sudo journalctl -u invoice-bot --since "today" | grep "Document generated"

# Performance metrics
sudo journalctl -u invoice-bot --since "today" | grep "PDF generated"
```

## 🆘 **Troubleshooting**

### **Service Issues**
```bash
# Service won't start
sudo journalctl -u invoice-bot --since "10 minutes ago"

# WeasyPrint issues
python3 -c "import weasyprint; print('WeasyPrint OK')"

# Network connectivity
curl -s https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe
```

### **Common Solutions**
- **Permission issues**: Check file ownership and permissions
- **Memory issues**: Add swap space or upgrade RAM
- **Network issues**: Check firewall and DNS settings
- **Python issues**: Verify virtual environment activation

## ✅ **Deployment Checklist**

### **Pre-deployment**
- [ ] Server provisioned with required specs
- [ ] Domain/IP address configured
- [ ] SSH access configured
- [ ] Backup strategy planned

### **During deployment**
- [ ] System dependencies installed
- [ ] Application deployed and configured
- [ ] Environment variables set
- [ ] Signature file uploaded
- [ ] Service configured and started

### **Post-deployment**
- [ ] Service running and accessible
- [ ] Test document generation works
- [ ] Bot responds to Telegram commands
- [ ] Monitoring and logging configured
- [ ] Security hardening applied

### **Ongoing maintenance**
- [ ] Regular updates scheduled
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Performance monitoring active

---

**🎯 Your invoice generator is now ready for production use!**
