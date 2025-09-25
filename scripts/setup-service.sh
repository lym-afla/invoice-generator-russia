#!/bin/bash
# Service Setup Script for Invoice Generator
# Creates user, sets permissions, creates symlink, and configures systemd service

# Configuration
SERVICE_NAME="invoice-bot"
APP_DIR="/opt/invoice-generator"
APP_USER="invoice-bot"  # Will be auto-detected if needed
SYMLINK_PATH="/usr/local/bin/invoice-bot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Detect and configure user
detect_and_configure_user() {
    print_header "Configuring application user..."
    
    # If APP_USER is set to a specific existing user, use that
    if [ "$APP_USER" != "invoice-bot" ] && id "$APP_USER" &>/dev/null; then
        print_status "Using existing user: $APP_USER"
        return
    fi
    
    # If invoice-bot user already exists, use it
    if id "invoice-bot" &>/dev/null; then
        APP_USER="invoice-bot"
        print_status "Using existing invoice-bot user"
        return
    fi
    
    # Try to detect the actual user who ran sudo
    if [ -n "$SUDO_USER" ] && id "$SUDO_USER" &>/dev/null; then
        print_status "Detected user who ran sudo: $SUDO_USER"
        echo "Choose user configuration:"
        echo "1) Create dedicated 'invoice-bot' user (recommended for production)"
        echo "2) Use existing user '$SUDO_USER'"
        read -p "Enter choice (1 or 2): " choice
        
        case $choice in
            1)
                create_invoice_bot_user
                ;;
            2)
                APP_USER="$SUDO_USER"
                print_status "Using existing user: $APP_USER"
                ;;
            *)
                print_warning "Invalid choice, creating dedicated user"
                create_invoice_bot_user
                ;;
        esac
    else
        # Default: create invoice-bot user
        create_invoice_bot_user
    fi
}

# Create dedicated invoice-bot user
create_invoice_bot_user() {
    print_status "Creating dedicated 'invoice-bot' user..."
    
    # Create system user with home directory
    useradd --system --create-home --home-dir "/home/invoice-bot" --shell /bin/bash "invoice-bot"
    APP_USER="invoice-bot"
    print_status "User $APP_USER created"
    
    # Add user to necessary groups
    usermod -aG systemd-journal "$APP_USER" 2>/dev/null || true
    print_status "User permissions configured"
}

# Set up directory permissions
setup_permissions() {
    print_header "Setting up directory permissions..."
    
    if [ ! -d "$APP_DIR" ]; then
        print_error "Application directory $APP_DIR does not exist"
        print_status "Please deploy the application first"
        exit 1
    fi
    
    # Change ownership to app user
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    print_status "Directory ownership set to $APP_USER"
    
    # Set proper permissions
    find "$APP_DIR" -type d -exec chmod 755 {} \;
    find "$APP_DIR" -type f -exec chmod 644 {} \;
    
    # Make scripts executable
    chmod +x "$APP_DIR/scripts/"*.sh 2>/dev/null || true
    chmod +x "$APP_DIR/"*.py 2>/dev/null || true
    
    # Secure sensitive files
    chmod 600 "$APP_DIR/.env" 2>/dev/null || true
    chmod 700 "$APP_DIR/signatures" 2>/dev/null || true
    
    print_status "File permissions configured"
}

# Create systemd service file
create_service_file() {
    print_header "Creating systemd service file..."
    
    cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=Invoice Generator Telegram Bot
After=network.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/venv/bin
ExecStart=${APP_DIR}/venv/bin/python telegram_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${APP_DIR}
PrivateDevices=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF

    print_status "Service file created: /etc/systemd/system/${SERVICE_NAME}.service"
    
    # Reload systemd
    systemctl daemon-reload
    print_status "Systemd configuration reloaded"
}

# Create symlink for management script
create_symlink() {
    print_header "Creating management script symlink..."
    
    local script_path="$APP_DIR/scripts/manage-invoice-bot.sh"
    
    if [ ! -f "$script_path" ]; then
        print_error "Management script not found: $script_path"
        return 1
    fi
    
    # Make sure script is executable
    chmod +x "$script_path"
    
    # Remove existing symlink if it exists
    if [ -L "$SYMLINK_PATH" ]; then
        rm "$SYMLINK_PATH"
        print_warning "Removed existing symlink"
    fi
    
    # Create new symlink
    ln -s "$script_path" "$SYMLINK_PATH"
    print_status "Symlink created: $SYMLINK_PATH -> $script_path"
    
    # Test symlink
    if [ -x "$SYMLINK_PATH" ]; then
        print_status "Symlink is working correctly"
        print_status "You can now use: sudo invoice-bot <command>"
    else
        print_error "Symlink test failed"
        return 1
    fi
}

# Enable and start service
enable_service() {
    print_header "Enabling service..."
    
    # Enable service (start on boot)
    systemctl enable "$SERVICE_NAME"
    print_status "Service enabled for automatic startup"
    
    # Don't start automatically, let user start it manually
    print_status "Service is ready but not started"
    print_status "Use: sudo invoice-bot start"
}

# Show setup summary
show_summary() {
    print_header "Setup Summary"
    echo
    print_status "Application user: $APP_USER"
    print_status "Application directory: $APP_DIR"
    print_status "Service name: $SERVICE_NAME"
    print_status "Management command: sudo invoice-bot <command>"
    echo
    print_status "Available commands:"
    echo "  sudo invoice-bot start     # Start the service"
    echo "  sudo invoice-bot stop      # Stop the service"
    echo "  sudo invoice-bot restart   # Restart the service"
    echo "  sudo invoice-bot status    # Show service status"
    echo "  sudo invoice-bot logs      # Show logs"
    echo "  sudo invoice-bot update    # Update from git and restart"
    echo
    print_status "Service status:"
    systemctl is-enabled "$SERVICE_NAME" --quiet && echo "  Enabled: YES" || echo "  Enabled: NO"
    systemctl is-active "$SERVICE_NAME" --quiet && echo "  Running: YES" || echo "  Running: NO"
    echo
    print_status "To start the service now:"
    echo "  sudo invoice-bot start"
}

# Validate environment
validate_environment() {
    print_header "Validating environment..."
    
    # Check for required commands
    local missing_commands=()
    
    for cmd in git python3 pip3 systemctl; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [ ${#missing_commands[@]} -ne 0 ]; then
        print_error "Missing required commands: ${missing_commands[*]}"
        print_status "Please install missing packages and try again"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -f "$APP_DIR/venv/bin/python" ]; then
        print_warning "Virtual environment not found"
        print_status "Make sure you've run the deployment process first"
    fi
    
    # Check if .env file exists
    if [ ! -f "$APP_DIR/.env" ]; then
        print_warning ".env file not found"
        print_status "Make sure to configure .env before starting the service"
    fi
    
    print_status "Environment validation completed"
}

# Main setup function
main() {
    print_header "Invoice Generator Service Setup"
    echo
    
    check_root
    validate_environment
    detect_and_configure_user
    setup_permissions
    create_service_file
    create_symlink
    enable_service
    echo
    show_summary
    
    print_header "Setup completed successfully!"
}

# Show help
show_help() {
    echo "Invoice Generator Service Setup Script"
    echo
    echo "This script sets up the invoice generator as a systemd service with:"
    echo "  - Dedicated application user ($APP_USER)"
    echo "  - Proper file permissions and security"
    echo "  - Systemd service configuration"
    echo "  - Management script symlink"
    echo
    echo "Usage: sudo $0"
    echo
    echo "After running this script, you can manage the service with:"
    echo "  sudo invoice-bot start|stop|restart|status|logs|update"
}

# Parse command line arguments
case "${1:-setup}" in
    setup)
        main
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
