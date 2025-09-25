# Invoice Generator Management Script for Windows
# Manages the invoice bot application on Windows

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "update", "help")]
    [string]$Command = "help",
    
    [switch]$Follow,
    [int]$Lines = 50,
    [string]$LogType = "app"
)

# Configuration
$ServiceName = "InvoiceBot"
$AppDir = "C:\invoice-generator"
$ProcessName = "python"
$ScriptName = "telegram_bot.py"
$GitRepoUrl = "https://github.com/lym-afla/invoice-generator.git"  # Update this

# Colors for output
function Write-Info { 
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green 
}

function Write-Warning { 
    param($Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow 
}

function Write-Error { 
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red 
}

function Write-Header { 
    param($Message)
    Write-Host "[INVOICE-BOT] $Message" -ForegroundColor Blue 
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Get process information
function Get-BotProcess {
    Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like "*$ScriptName*" } |
    Select-Object -First 1
}

# Check if service exists (for NSSM-managed service)
function Test-ServiceExists {
    return (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) -ne $null
}

# Start the application
function Start-BotService {
    Write-Header "Starting application..."
    
    # Check if running as Windows service
    if (Test-ServiceExists) {
        Write-Info "Starting Windows service..."
        try {
            Start-Service -Name $ServiceName
            Write-Info "Service started successfully"
            Show-Status
        }
        catch {
            Write-Error "Failed to start service: $($_.Exception.Message)"
        }
        return
    }
    
    # Check if already running
    $process = Get-BotProcess
    if ($process) {
        Write-Warning "Application is already running (PID: $($process.Id))"
        Show-Status
        return
    }
    
    # Start as regular process
    Write-Info "Starting application as process..."
    
    if (-not (Test-Path $AppDir)) {
        Write-Error "Application directory not found: $AppDir"
        return
    }
    
    Set-Location $AppDir
    
    # Activate virtual environment and start
    if (Test-Path "venv\Scripts\activate.ps1") {
        Write-Info "Activating virtual environment..."
        & "venv\Scripts\activate.ps1"
    }
    
    # Start the bot in background
    Start-Process -FilePath "python" -ArgumentList $ScriptName -WorkingDirectory $AppDir -WindowStyle Hidden
    
    Start-Sleep -Seconds 2
    
    $process = Get-BotProcess
    if ($process) {
        Write-Info "Application started successfully (PID: $($process.Id))"
        Show-Status
    } else {
        Write-Error "Failed to start application"
    }
}

# Stop the application
function Stop-BotService {
    Write-Header "Stopping application..."
    
    # Check if running as Windows service
    if (Test-ServiceExists) {
        Write-Info "Stopping Windows service..."
        try {
            Stop-Service -Name $ServiceName -Force
            Write-Info "Service stopped successfully"
        }
        catch {
            Write-Error "Failed to stop service: $($_.Exception.Message)"
        }
        Show-Status
        return
    }
    
    # Stop process
    $process = Get-BotProcess
    if ($process) {
        Write-Info "Stopping process (PID: $($process.Id))..."
        try {
            Stop-Process -Id $process.Id -Force
            Write-Info "Application stopped successfully"
        }
        catch {
            Write-Error "Failed to stop application: $($_.Exception.Message)"
        }
    } else {
        Write-Warning "Application was not running"
    }
    
    Show-Status
}

# Restart the application
function Restart-BotService {
    Write-Header "Restarting application..."
    Stop-BotService
    Start-Sleep -Seconds 2
    Start-BotService
}

# Show application status
function Show-Status {
    Write-Header "Application status..."
    
    # Check Windows service
    if (Test-ServiceExists) {
        $service = Get-Service -Name $ServiceName
        Write-Info "Service Status: $($service.Status)"
        
        if ($service.Status -eq "Running") {
            Write-Host "Service is " -NoNewline
            Write-Host "RUNNING" -ForegroundColor Green
        } else {
            Write-Host "Service is " -NoNewline
            Write-Host "STOPPED" -ForegroundColor Red
        }
        return
    }
    
    # Check process
    $process = Get-BotProcess
    if ($process) {
        Write-Host "Application is " -NoNewline
        Write-Host "RUNNING" -ForegroundColor Green
        Write-Info "Process ID: $($process.Id)"
        Write-Info "Started: $($process.StartTime)"
        Write-Info "CPU Time: $($process.TotalProcessorTime)"
        Write-Info "Memory: $([math]::Round($process.WorkingSet64/1MB, 2)) MB"
    } else {
        Write-Host "Application is " -NoNewline
        Write-Host "STOPPED" -ForegroundColor Red
    }
}

# Show logs
function Show-Logs {
    Write-Header "Showing logs..."
    
    # For Windows, we'll check common log locations
    $logPaths = @(
        "$AppDir\logs\*.log",
        "$AppDir\*.log",
        "$env:TEMP\invoice-bot*.log"
    )
    
    $foundLogs = $false
    
    foreach ($path in $logPaths) {
        if (Test-Path $path) {
            $logFiles = Get-ChildItem $path | Sort-Object LastWriteTime -Descending
            foreach ($logFile in $logFiles) {
                Write-Info "Log file: $($logFile.FullName)"
                if ($Follow) {
                    Write-Info "Following log file (Ctrl+C to stop)..."
                    Get-Content $logFile.FullName -Tail $Lines -Wait
                } else {
                    Get-Content $logFile.FullName -Tail $Lines
                }
                $foundLogs = $true
                break
            }
            if ($foundLogs) { break }
        }
    }
    
    if (-not $foundLogs) {
        # If no log files found, show Windows Event Log
        Write-Info "No application log files found, checking Windows Event Log..."
        try {
            Get-WinEvent -FilterHashtable @{LogName='Application'; ID=1000,1001} -MaxEvents $Lines |
            Where-Object { $_.Message -like "*python*" -or $_.Message -like "*invoice*" } |
            Format-Table TimeCreated, Id, LevelDisplayName, Message -Wrap
        }
        catch {
            Write-Warning "No relevant events found in Windows Event Log"
            
            # As fallback, try to run the app and capture output
            Write-Info "Starting application in console mode to show logs..."
            Set-Location $AppDir
            if (Test-Path "venv\Scripts\activate.ps1") {
                & "venv\Scripts\activate.ps1"
            }
            python $ScriptName
        }
    }
}

# Update application
function Update-App {
    Write-Header "Updating application..."
    
    if (-not (Test-Administrator)) {
        Write-Error "Update requires administrator privileges. Run PowerShell as Administrator."
        return
    }
    
    if (-not (Test-Path "$AppDir\.git")) {
        Write-Error "No git repository found in $AppDir"
        Write-Info "This script requires the application to be installed from git"
        return
    }
    
    $originalLocation = Get-Location
    Set-Location $AppDir
    
    # Check if app is running
    $wasRunning = $false
    if (Test-ServiceExists) {
        $service = Get-Service -Name $ServiceName
        $wasRunning = $service.Status -eq "Running"
    } else {
        $process = Get-BotProcess
        $wasRunning = $process -ne $null
    }
    
    if ($wasRunning) {
        Write-Info "Application is running, will restart after update"
    }
    
    # Get current version
    try {
        $currentCommit = & git rev-parse HEAD
        Write-Info "Current version: $($currentCommit.Substring(0,8))"
    }
    catch {
        $currentCommit = "unknown"
        Write-Warning "Could not determine current version"
    }
    
    # Fetch latest changes
    Write-Info "Fetching latest changes from repository..."
    try {
        & git fetch origin
    }
    catch {
        Write-Error "Failed to fetch from repository"
        Set-Location $originalLocation
        return
    }
    
    # Check if there are updates
    try {
        $latestCommit = & git rev-parse origin/main
        if (-not $latestCommit) {
            $latestCommit = & git rev-parse origin/master
        }
    }
    catch {
        Write-Error "Could not determine latest version"
        Set-Location $originalLocation
        return
    }
    
    if ($currentCommit -eq $latestCommit) {
        Write-Info "Already up to date"
        Set-Location $originalLocation
        return
    }
    
    # Stop application if running
    if ($wasRunning) {
        Write-Info "Stopping application for update..."
        Stop-BotService
        Start-Sleep -Seconds 2
    }
    
    # Pull latest changes
    Write-Info "Pulling latest version..."
    try {
        & git pull origin main
        if ($LASTEXITCODE -ne 0) {
            & git pull origin master
        }
    }
    catch {
        Write-Error "Failed to pull latest changes"
        Set-Location $originalLocation
        return
    }
    
    # Show what changed
    try {
        $newCommit = & git rev-parse HEAD
        Write-Info "Updated to version: $($newCommit.Substring(0,8))"
        
        if ($currentCommit -ne "unknown" -and $currentCommit -ne $newCommit) {
            Write-Info "Changes in this update:"
            & git log --oneline "$currentCommit..$newCommit" | Select-Object -First 10
        }
    }
    catch {
        Write-Warning "Could not show update details"
    }
    
    # Update dependencies
    Write-Info "Updating Python dependencies..."
    if (Test-Path "venv\Scripts\activate.ps1") {
        try {
            & "venv\Scripts\activate.ps1"
            & pip install -r requirements.txt --quiet --upgrade
            Write-Info "Dependencies updated successfully"
        }
        catch {
            Write-Warning "Some dependencies may not have updated properly"
        }
    } else {
        Write-Warning "Virtual environment not found, skipping dependency update"
    }
    
    # Restart application if it was running
    if ($wasRunning) {
        Write-Info "Restarting application..."
        Start-BotService
    }
    
    Set-Location $originalLocation
    Write-Info "Update completed successfully!"
}

# Show help
function Show-Help {
    Write-Host "Invoice Generator Management Script for Windows"
    Write-Host ""
    Write-Host "Usage: .\manage-invoice-bot.ps1 <command> [options]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  start                Start the application"
    Write-Host "  stop                 Stop the application"
    Write-Host "  restart              Restart the application"
    Write-Host "  status               Show application status"
    Write-Host "  logs                 Show logs"
    Write-Host "  update               Update application from git and restart"
    Write-Host "  help                 Show this help message"
    Write-Host ""
    Write-Host "Log options:"
    Write-Host "  -Follow              Follow logs in real-time"
    Write-Host "  -Lines N             Number of lines to show (default: $Lines)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\manage-invoice-bot.ps1 start"
    Write-Host "  .\manage-invoice-bot.ps1 logs -Follow"
    Write-Host "  .\manage-invoice-bot.ps1 logs -Lines 100"
    Write-Host "  .\manage-invoice-bot.ps1 update"
    Write-Host ""
    Write-Host "Configuration:"
    Write-Host "  Service name: $ServiceName"
    Write-Host "  App directory: $AppDir"
    Write-Host "  Script name: $ScriptName"
}

# Main script logic
switch ($Command) {
    "start" { Start-BotService }
    "stop" { Stop-BotService }
    "restart" { Restart-BotService }
    "status" { Show-Status }
    "logs" { Show-Logs }
    "update" { Update-App }
    "help" { Show-Help }
    default { 
        Write-Error "Unknown command: $Command"
        Show-Help 
    }
}
