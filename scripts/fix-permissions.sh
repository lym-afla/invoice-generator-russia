#!/bin/bash
# Fix Permissions Script for Invoice Generator
# Fixes ownership and permission issues

# Configuration
APP_DIR="/opt/invoice-generator"
APP_USER="user1"  # Change this to your desired user

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
    echo -e "${BLUE}[FIX-PERMISSIONS]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Detect current user if APP_USER is not set properly
detect_user() {
    if [ "$APP_USER" = "user1" ] && ! id "user1" &>/dev/null; then
        # Try to detect the actual user
        REAL_USER=$(who am i | awk '{print $1}')
        if [ -n "$REAL_USER" ] && id "$REAL_USER" &>/dev/null; then
            APP_USER="$REAL_USER"
            print_status "Detected user: $APP_USER"
        else
            print_error "Cannot detect user. Please edit this script and set APP_USER manually."
            exit 1
        fi
    fi
}

# Fix directory permissions
fix_permissions() {
    print_header "Fixing permissions for $APP_DIR"
    
    if [ ! -d "$APP_DIR" ]; then
        print_error "Application directory $APP_DIR does not exist"
        exit 1
    fi
    
    print_status "Current ownership:"
    ls -la "$APP_DIR" | head -5
    
    print_status "Changing ownership to $APP_USER:$APP_USER..."
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    
    print_status "Setting directory permissions..."
    find "$APP_DIR" -type d -exec chmod 755 {} \;
    
    print_status "Setting file permissions..."
    find "$APP_DIR" -type f -exec chmod 644 {} \;
    
    # Make scripts executable
    chmod +x "$APP_DIR/scripts/"*.sh 2>/dev/null || true
    chmod +x "$APP_DIR/"*.py 2>/dev/null || true
    
    # Secure sensitive files
    chmod 600 "$APP_DIR/.env" 2>/dev/null || true
    chmod 700 "$APP_DIR/signatures" 2>/dev/null || true
    
    # Fix virtual environment permissions specifically
    if [ -d "$APP_DIR/venv" ]; then
        print_status "Fixing virtual environment permissions..."
        chown -R "$APP_USER:$APP_USER" "$APP_DIR/venv"
        chmod -R u+w "$APP_DIR/venv"
    fi
    
    print_status "Permissions fixed successfully"
    
    print_status "New ownership:"
    ls -la "$APP_DIR" | head -5
}

# Test virtual environment
test_venv() {
    print_header "Testing virtual environment..."
    
    # Switch to app user and test pip install
    sudo -u "$APP_USER" bash -c "
        cd '$APP_DIR'
        source venv/bin/activate
        pip list | head -5
        echo 'Testing pip install...'
        pip install --dry-run requests 2>/dev/null && echo 'Pip install test: SUCCESS' || echo 'Pip install test: FAILED'
    "
}

# Reinstall dependencies
reinstall_deps() {
    print_header "Reinstalling Python dependencies..."
    
    sudo -u "$APP_USER" bash -c "
        cd '$APP_DIR'
        source venv/bin/activate
        echo 'Installing dependencies...'
        pip install -r requirements.txt --upgrade
    "
    
    if [ $? -eq 0 ]; then
        print_status "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        return 1
    fi
}

# Show usage
show_help() {
    echo "Fix Permissions Script for Invoice Generator"
    echo
    echo "Usage: sudo $0 [options]"
    echo
    echo "Options:"
    echo "  fix                  Fix permissions only"
    echo "  test                 Test virtual environment after fixing"
    echo "  install              Fix permissions and reinstall dependencies"
    echo "  help                 Show this help"
    echo
    echo "Examples:"
    echo "  sudo $0 fix          # Fix permissions only"
    echo "  sudo $0 install      # Fix permissions and install dependencies"
    echo
    echo "Configuration:"
    echo "  APP_DIR: $APP_DIR"
    echo "  APP_USER: $APP_USER"
    echo
    echo "To change the user, edit this script and modify APP_USER variable."
}

# Main function
main() {
    check_root
    detect_user
    
    case "${1:-install}" in
        fix)
            fix_permissions
            ;;
        test)
            fix_permissions
            test_venv
            ;;
        install)
            fix_permissions
            test_venv
            reinstall_deps
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
