# 📜 Management Scripts

This folder contains management scripts for the Invoice Generator application.

## 🐧 **Linux Scripts**

### **`manage-invoice-bot.sh`** - Main Management Script
Comprehensive service management for Linux/Ubuntu systems.

**Features:**
- ✅ **Service control**: start, stop, restart, status
- ✅ **Log viewing**: service logs, Python logs, error logs with follow option
- ✅ **Auto-update**: git pull, dependency install, restart
- ✅ **Permission management**: maintains proper user permissions
- ✅ **Resource monitoring**: shows CPU, memory, uptime

**Usage after setup:**
```bash
sudo invoice-bot start                    # Start the service
sudo invoice-bot stop                     # Stop the service
sudo invoice-bot restart                  # Restart the service
sudo invoice-bot status                   # Show detailed status
sudo invoice-bot logs                     # Show service logs
sudo invoice-bot logs -f                  # Follow logs in real-time
sudo invoice-bot logs -t python -n 100   # Show 100 lines of Python logs
sudo invoice-bot logs -t error            # Show only error logs
sudo invoice-bot update                   # Update from git and restart
```

### **`setup-service.sh`** - Initial Service Setup
One-time setup script that configures everything needed for production.

**What it does:**
- ✅ **Creates dedicated user**: `invoice-bot` (recommended for security)
- ✅ **Sets up permissions**: proper file ownership and security
- ✅ **Creates systemd service**: with security hardening
- ✅ **Creates symlink**: `/usr/local/bin/invoice-bot` → management script
- ✅ **Enables service**: for automatic startup on boot

**Usage:**
```bash
sudo ./scripts/setup-service.sh
```

## 🖥️ **Windows Scripts**

### **`manage-invoice-bot.ps1`** - Windows Management Script
PowerShell script for Windows service management.

**Features:**
- ✅ **Process/Service control**: start, stop, restart, status
- ✅ **Log viewing**: application logs and Windows Event Log
- ✅ **Auto-update**: git pull and dependency install
- ✅ **NSSM service support**: if installed as Windows service

**Usage:**
```powershell
.\scripts\manage-invoice-bot.ps1 start     # Start application
.\scripts\manage-invoice-bot.ps1 stop      # Stop application
.\scripts\manage-invoice-bot.ps1 status    # Show status
.\scripts\manage-invoice-bot.ps1 logs      # Show logs
.\scripts\manage-invoice-bot.ps1 update    # Update and restart
```

## 🚀 **Quick Setup Guide**

### **For Linux Production:**

1. **Deploy application** to `/opt/invoice-generator`
2. **Run setup script**:
   ```bash
   cd /opt/invoice-generator
   sudo ./scripts/setup-service.sh
   ```
3. **Start service**:
   ```bash
   sudo invoice-bot start
   ```
4. **Check status**:
   ```bash
   sudo invoice-bot status
   ```

### **For Windows:**

1. **Deploy application** to `C:\invoice-generator`
2. **Use management script**:
   ```powershell
   .\scripts\manage-invoice-bot.ps1 start
   ```

## 👤 **User Recommendations**

### **Linux: Use `invoice-bot` User (Recommended)**

**Why create a dedicated user?**
- ✅ **Security**: Isolated permissions, can't access other system files
- ✅ **Systemd integration**: Clean service management
- ✅ **File ownership**: Clear ownership boundaries
- ✅ **Process isolation**: Separate from other applications

**Alternative: Use existing user (like `user1`)**
If you prefer to use your existing `user1`:

1. **Edit setup script variables**:
   ```bash
   # In scripts/setup-service.sh
   APP_USER="user1"
   ```

2. **Edit service file template**:
   ```bash
   # In scripts/setup-service.sh, update the service file section
   User=user1
   Group=user1
   ```

3. **Run setup**:
   ```bash
   sudo ./scripts/setup-service.sh
   ```

### **Security Considerations**

**Dedicated User (Recommended):**
```bash
# The setup script creates:
User: invoice-bot
Home: /home/invoice-bot  
Groups: invoice-bot, systemd-journal
Permissions: Limited to app directory only
```

**Existing User:**
```bash
# If using user1:
User: user1
Home: /home/user1
Groups: user1 + existing groups
Permissions: Broader system access
```

## 🔧 **Configuration Files**

### **Systemd Service File** (`/etc/systemd/system/invoice-bot.service`)
```ini
[Unit]
Description=Invoice Generator Telegram Bot
After=network.target

[Service]
Type=simple
User=invoice-bot                    # <-- Change this for different user
Group=invoice-bot                   # <-- Change this too
WorkingDirectory=/opt/invoice-generator
Environment=PATH=/opt/invoice-generator/venv/bin
ExecStart=/opt/invoice-generator/venv/bin/python telegram_bot.py
Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/invoice-generator

[Install]
WantedBy=multi-user.target
```

### **Management Script Configuration**
```bash
# In scripts/manage-invoice-bot.sh
SERVICE_NAME="invoice-bot"
APP_DIR="/opt/invoice-generator"
APP_USER="invoice-bot"              # <-- Change this for different user
GITHUB_REPO_URL="https://github.com/your-username/invoice-generator.git"
```

## 📊 **Update Process**

The update command performs these steps:

1. **Check git repository** - Ensures app was installed from git
2. **Fetch latest changes** - Downloads latest commits
3. **Compare versions** - Shows what will be updated
4. **Stop service** - Gracefully stops if running
5. **Pull changes** - Updates code to latest version
6. **Update permissions** - Maintains proper file ownership
7. **Update dependencies** - Installs new Python packages (quietly)
8. **Restart service** - Starts updated version
9. **Verify startup** - Confirms service started successfully

**Example update output:**
```bash
$ sudo invoice-bot update
[INVOICE-BOT] Updating application...
[INFO] Service is running, will restart after update
[INFO] Current version: a1b2c3d4
[INFO] Fetching latest changes from repository...
[INFO] Stopping service for update...
[INFO] Pulling latest version...
[INFO] Updated to version: e5f6g7h8
[INFO] Changes in this update:
e5f6g7h8 Fix currency rate display
d4c3b2a1 Add new document template
[INFO] Updating file permissions...
[INFO] Updating Python dependencies...
[INFO] Dependencies updated successfully
[INFO] Restarting service...
[INFO] Service restarted successfully
[INFO] Update completed successfully!
```

## 📋 **Log Types**

The management script supports different log views:

| Type | Description | Usage |
|------|-------------|-------|
| `service` | Systemd service logs | `sudo invoice-bot logs` |
| `python` | Application output only | `sudo invoice-bot logs -t python` |
| `error` | Error messages only | `sudo invoice-bot logs -t error` |
| `all` | Complete logs | `sudo invoice-bot logs -t all` |

**Log options:**
- `-f, --follow` - Follow logs in real-time
- `-n, --lines N` - Show N lines (default: 50)

## 🔍 **Troubleshooting**

### **Service won't start:**
```bash
sudo invoice-bot status
sudo invoice-bot logs -t error
```

### **Update fails:**
```bash
# Check git status
cd /opt/invoice-generator
sudo -u invoice-bot git status

# Manual update
sudo -u invoice-bot git pull
sudo -u invoice-bot bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo invoice-bot restart
```

### **Permission issues:**
```bash
# Reset permissions
sudo ./scripts/setup-service.sh
```

### **Symlink issues:**
```bash
# Recreate symlink
sudo ln -sf /opt/invoice-generator/scripts/manage-invoice-bot.sh /usr/local/bin/invoice-bot
```

---

**🎯 These scripts provide production-ready management for the Invoice Generator system!**
