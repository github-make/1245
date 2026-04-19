# OpenClaw Deploy Tool - Windows PowerShell
# One-click deploy OpenClaw

param(
    [switch]$SkipCheck
)

$GREEN = "`e[0;32m"
$RED = "`e[0;31m"
$YELLOW = "`e[1;33m"
$CYAN = "`e[0;36m"
$NC = "`e[0m"

function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
}

function Write-Success {
    param([string]$Message)
    Write-Host "${GREEN}[OK] $Message${NC}"
}

function Write-Error {
    param([string]$Message)
    Write-Host "${RED}[ERROR] $Message${NC}"
}

function Write-Warn {
    param([string]$Message)
    Write-Host "${YELLOW}[WARN] $Message${NC}"
}

function Show-Banner {
    Write-Host ""
    Write-Host "   _   _                      _ _  "
    Write-Host "  | \ | |                    | (_) "
    Write-Host "  |  \| | _____      _____  __| |_  ____ "
    Write-Host "  | . \` |/ _ \ \ /\ / / __|/ _\` | |/ / /  "
    Write-Host "  | |\  |  __/\ V  V /\__ \ (_| |   <| |  "
    Write-Host "  |_| \_|\___| \_/\_/ |___/\__,_|_|\_\ \_| "
    Write-Host ""
    Write-Host "   OpenClaw Deploy Tool v1.0.0 (Windows)"
    Write-Host ""
}

function Test-OpenClawInstalled {
    $cmd = Get-Command openclaw -ErrorAction SilentlyContinue
    return ($null -ne $cmd)
}

function Get-OpenClawVersion {
    try {
        return openclaw --version 2>$null
    }
    catch {
        return "unknown"
    }
}

function Install-OpenClaw {
    if (Test-OpenClawInstalled) {
        $version = Get-OpenClawVersion
        Write-Warn "OpenClaw installed: $version"
        $confirm = Read-Host "Reinstall? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            return
        }
    }

    Write-Log "Detected Windows environment"
    Write-Log "Recommended: Use WSL2 + Ubuntu for OpenClaw (more stable)"
    Write-Host ""

    Write-Host "Install options:" -ForegroundColor Cyan
    Write-Host "  1) Install in WSL2 Ubuntu (Recommended)"
    Write-Host "  2) Install directly in Windows PowerShell"
    Write-Host "  3) Skip install"
    $choice = Read-Host "Select [1-3]"

    switch ($choice) {
        "1" {
            Write-Log "Please run in WSL2 Ubuntu terminal:"
            Write-Host "  curl -fsSL https://openclaw.ai/install.sh | bash" -ForegroundColor Yellow
        }
        "2" {
            Write-Log "Running official PowerShell install script..."
            try {
                iwr -useb https://openclaw.ai/install.ps1 | iex
                Write-Success "Install complete"
            }
            catch {
                Write-Error "Install failed: $_"
                Write-Host ""
                Write-Host "Fallback - Install via npm:" -ForegroundColor Cyan
                Write-Host "  npm install -g openclaw@latest" -ForegroundColor Yellow
            }
        }
        "3" {
            Write-Warn "Skipped install"
        }
        default {
            Write-Warn "Invalid option, skipping"
        }
    }
}

function Verify-Installation {
    Write-Log "Verifying install..."

    if (Test-OpenClawInstalled) {
        $version = Get-OpenClawVersion
        Write-Success "OpenClaw installed successfully!"
        Write-Log "Version: $version"
        Write-Host ""
        Write-Log "Next steps:"
        Write-Log "  1. Run openclaw onboard to configure"
        Write-Log "  2. Run openclaw dashboard to open console"
        Write-Log "  3. Run openclaw status to check status"
    }
    else {
        Write-Warn "OpenClaw not installed"
    }
}

function Main {
    Clear-Host
    Show-Banner
    Write-Log ""
    Write-Log "=========================================="
    Write-Log "OpenClaw Deploy Tool (Windows)"
    Write-Log "=========================================="
    Write-Log ""

    if (-not $SkipCheck) {
        Write-Log "Checking Node.js..."
        $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
        if ($nodeCmd) {
            $nodeVersion = node --version
            Write-Success "Node.js installed: $nodeVersion"
        }
        else {
            Write-Warn "Node.js not installed"
            Write-Host ""
            Write-Host "Please install Node.js 22 LTS first:" -ForegroundColor Cyan
            Write-Host "  https://nodejs.org/" -ForegroundColor Yellow
            Write-Host ""
            $continue = Read-Host "Continue anyway? (y/N)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                exit
            }
        }
    }

    Install-OpenClaw
    Verify-Installation

    Write-Host ""
    Write-Success "Done!"
}

Main