#!/bin/bash
# Invoice Generator Management Script
# Manages the invoice-bot systemd service and application updates

# Configuration
SERVICE_NAME="invoice-bot"
APP_DIR="/opt/invoice-generator"
APP_USER="invoice-bot"
LOG_LINES=50
GITHUB_REPO_URL="https://github.com/lym-afla/invoice-generator.git"  # Update this

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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
    echo -e "${BLUE}[${SERVICE_NAME^^}]${NC} $1"
}

# Check if running as root (needed for service management)
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check if root is needed for specific commands
check_root_for_command() {
    local command="$1"
    case "$command" in
        status|logs|help)
            # These commands can run without root
            return 0
            ;;
        *)
            # Other commands need root - try to escalate automatically
            if [[ $EUID -ne 0 ]]; then
                print_warning "This command requires root privileges"
                print_status "Attempting to escalate with sudo..."
                exec sudo "$0" "$@"
            fi
            ;;
    esac
}

# Check if service exists
check_service_exists() {
    if ! systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
        print_error "Service ${SERVICE_NAME} does not exist"
        print_status "Run the deployment script first to create the service"
        exit 1
    fi
}

# Start the service
start_service() {
    print_header "Starting service..."
    check_root_for_command "start"
    check_service_exists
    
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        print_warning "Service is already running"
        status_service
    else
        systemctl start "${SERVICE_NAME}"
        if systemctl is-active --quiet "${SERVICE_NAME}"; then
            print_status "Service started successfully"
            status_service
        else
            print_error "Failed to start service"
            systemctl status "${SERVICE_NAME}" --no-pager -l
            exit 1
        fi
    fi
}

# Stop the service
stop_service() {
    print_header "Stopping service..."
    check_root_for_command "stop"
    check_service_exists
    
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        systemctl stop "${SERVICE_NAME}"
        print_status "Service stopped successfully"
    else
        print_warning "Service was not running"
    fi
    status_service
}

# Restart the service
restart_service() {
    print_header "Restarting service..."
    check_root_for_command "restart"
    check_service_exists
    
    systemctl restart "${SERVICE_NAME}"
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        print_status "Service restarted successfully"
        status_service
    else
        print_error "Failed to restart service"
        systemctl status "${SERVICE_NAME}" --no-pager -l
        exit 1
    fi
}

# Show service status
status_service() {
    print_header "Service status..."
    check_root_for_command "status"
    check_service_exists
    
    # Service status
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        print_status "Service is ${GREEN}RUNNING${NC}"
    else
        print_error "Service is ${RED}STOPPED${NC}"
    fi
    
    # Detailed status
    echo
    systemctl status "${SERVICE_NAME}" --no-pager -l
    
    # Memory and CPU usage
    echo
    print_status "Resource usage:"
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        systemctl show "${SERVICE_NAME}" --property=MainPID --value | xargs -I {} ps -p {} -o pid,ppid,cmd,%mem,%cpu --no-headers 2>/dev/null || echo "Process information not available"
    fi
    
    # Uptime
    echo
    print_status "Service uptime:"
    systemctl show "${SERVICE_NAME}" --property=ActiveEnterTimestamp --value
}

# Show logs
show_logs() {
    check_root_for_command "logs"
    local follow_logs=false
    local log_type="service"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--follow)
                follow_logs=true
                shift
                ;;
            -t|--type)
                log_type="$2"
                shift 2
                ;;
            -n|--lines)
                LOG_LINES="$2"
                shift 2
                ;;
            *)
                break
                ;;
        esac
    done
    
    print_header "Showing logs (type: $log_type, lines: $LOG_LINES)..."
    
    case $log_type in
        service|systemd)
            if $follow_logs; then
                print_status "Following service logs (Ctrl+C to stop)..."
                journalctl -u "${SERVICE_NAME}" -f
            else
                journalctl -u "${SERVICE_NAME}" -n "${LOG_LINES}" --no-pager
            fi
            ;;
        python|app)
            # Show application logs from journalctl but filter for Python output
            if $follow_logs; then
                print_status "Following application logs (Ctrl+C to stop)..."
                journalctl -u "${SERVICE_NAME}" -f | grep -E "(✅|❌|⚠️|📋|📊|🤖|ERROR|WARNING|INFO)"
            else
                journalctl -u "${SERVICE_NAME}" -n "${LOG_LINES}" --no-pager | grep -E "(✅|❌|⚠️|📋|📊|🤖|ERROR|WARNING|INFO)"
            fi
            ;;
        error|errors)
            print_status "Showing error logs only..."
            journalctl -u "${SERVICE_NAME}" -n "${LOG_LINES}" --no-pager -p err
            ;;
        all)
            print_status "Showing all logs..."
            if $follow_logs; then
                journalctl -u "${SERVICE_NAME}" -f
            else
                journalctl -u "${SERVICE_NAME}" -n "${LOG_LINES}" --no-pager
            fi
            ;;
        *)
            print_error "Unknown log type: $log_type"
            print_status "Available types: service, python, error, all"
            exit 1
            ;;
    esac
}

# Update application
update_app() {
    print_header "Updating application..."
    check_root_for_command "update"
    
    # Check if git repository exists
    if [ ! -d "${APP_DIR}/.git" ]; then
        print_error "No git repository found in ${APP_DIR}"
        print_status "This script requires the application to be installed from git"
        exit 1
    fi
    
    # Store current directory
    ORIGINAL_DIR=$(pwd)
    
    # Change to application directory
    cd "${APP_DIR}" || {
        print_error "Cannot access application directory: ${APP_DIR}"
        exit 1
    }
    
    # Check if service is running (we'll need to restart it)
    local was_running=false
    if systemctl is-active --quiet "${SERVICE_NAME}"; then
        was_running=true
        print_status "Service is running, will restart after update"
    fi
    
    # Backup current version info
    local current_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    print_status "Current version: ${current_commit:0:8}"
    
    # Fetch latest changes
    print_status "Fetching latest changes from repository..."
    if ! git fetch origin; then
        print_error "Failed to fetch from repository"
        cd "${ORIGINAL_DIR}"
        exit 1
    fi
    
    # Check if there are updates
    local latest_commit=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null)
    if [ "$current_commit" = "$latest_commit" ]; then
        print_status "Already up to date"
        cd "${ORIGINAL_DIR}"
        return
    fi
    
    # Stop service if running
    if $was_running; then
        print_status "Stopping service for update..."
        systemctl stop "${SERVICE_NAME}"
    fi
    
    # Pull latest changes
    print_status "Pulling latest version..."
    if ! git pull origin main 2>/dev/null && ! git pull origin master 2>/dev/null; then
        print_error "Failed to pull latest changes"
        cd "${ORIGINAL_DIR}"
        exit 1
    fi
    
    # Show what changed
    local new_commit=$(git rev-parse HEAD)
    print_status "Updated to version: ${new_commit:0:8}"
    
    if [ "$current_commit" != "unknown" ] && [ "$current_commit" != "$new_commit" ]; then
        echo
        print_status "Changes in this update:"
        git log --oneline "${current_commit}..${new_commit}" | head -10
        echo
    fi
    
    # Update file permissions and git config
    print_status "Updating file permissions..."
    chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"
    chmod +x "${APP_DIR}/scripts/"*.sh 2>/dev/null || true
    
    # Ensure management script and symlink remain executable after updates
    chmod +x "${APP_DIR}/scripts/manage-invoice-bot.sh"
    
    # Fix symlink permissions - remove and recreate if needed
    if [ -L "/usr/local/bin/invoice-bot" ]; then
        rm -f "/usr/local/bin/invoice-bot"
    fi
    ln -sf "${APP_DIR}/scripts/manage-invoice-bot.sh" "/usr/local/bin/invoice-bot"
    chmod +x "/usr/local/bin/invoice-bot"
    
    print_status "Symlink recreated and permissions fixed"
    
    # Configure git to ignore file mode changes and reset any phantom changes
    sudo -u "${APP_USER}" bash -c "
        cd '${APP_DIR}'
        git config core.filemode false
        git config core.autocrlf false
        git config --global --add safe.directory '${APP_DIR}'
        git checkout -- . 2>/dev/null || true
    "
    
    # Also add safe.directory for root user (for future updates)
    git config --global --add safe.directory "${APP_DIR}" 2>/dev/null || true
    
    # Activate virtual environment and update dependencies
    print_status "Updating Python dependencies..."
    if [ -f "${APP_DIR}/venv/bin/activate" ]; then
        # Use the app user to update dependencies
        sudo -u "${APP_USER}" bash -c "
            cd '${APP_DIR}'
            source venv/bin/activate
            pip install -r requirements.txt --quiet --upgrade
        " 2>/dev/null
        
        if [ $? -eq 0 ]; then
            print_status "Dependencies updated successfully"
        else
            print_warning "Some dependencies may not have updated properly"
        fi
    else
        print_warning "Virtual environment not found, skipping dependency update"
    fi
    
    # Reload systemd if service files changed
    if git diff --name-only "${current_commit}..${new_commit}" 2>/dev/null | grep -q "\.service$"; then
        print_status "Service file changed, reloading systemd..."
        systemctl daemon-reload
    fi
    
    # Restart service if it was running
    if $was_running; then
        print_status "Restarting service..."
        systemctl start "${SERVICE_NAME}"
        
        # Wait a moment and check status
        sleep 2
        if systemctl is-active --quiet "${SERVICE_NAME}"; then
            print_status "Service restarted successfully"
        else
            print_error "Service failed to start after update"
            print_status "Check logs for details:"
            journalctl -u "${SERVICE_NAME}" -n 20 --no-pager
            cd "${ORIGINAL_DIR}"
            exit 1
        fi
    fi
    
    cd "${ORIGINAL_DIR}"
    
    # Verify symlink is working
    print_status "Verifying symlink functionality..."
    if [ -x "/usr/local/bin/invoice-bot" ]; then
        print_status "Symlink is executable and working"
    else
        print_warning "Symlink may have permission issues"
        print_status "Fixing symlink permissions..."
        chmod +x "/usr/local/bin/invoice-bot"
    fi
    
    print_status "Update completed successfully!"
}

# Show help
show_help() {
    echo "Invoice Generator Management Script"
    echo
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  start                Start the service"
    echo "  stop                 Stop the service"
    echo "  restart              Restart the service"
    echo "  status               Show service status and resource usage"
    echo "  logs [options]       Show logs"
    echo "  update               Update application from git and restart"
    echo "  help                 Show this help message"
    echo
    echo "Log options:"
    echo "  -f, --follow         Follow logs in real-time"
    echo "  -t, --type TYPE      Log type: service, python, error, all (default: service)"
    echo "  -n, --lines N        Number of lines to show (default: $LOG_LINES)"
    echo
    echo "Examples:"
    echo "  $0 start                    # Start the service"
    echo "  $0 logs -f                  # Follow service logs"
    echo "  $0 logs -t python -n 100    # Show 100 lines of Python logs"
    echo "  $0 logs -t error            # Show only error logs"
    echo "  $0 update                   # Update and restart"
    echo
    echo "Configuration:"
    echo "  Service name: $SERVICE_NAME"
    echo "  App directory: $APP_DIR"
    echo "  App user: $APP_USER"
}

# Main script logic
main() {
    case "${1:-help}" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            status_service
            ;;
        logs)
            shift
            show_logs "$@"
            ;;
        update)
            update_app
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
