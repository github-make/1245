#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }
success() { echo -e "${GREEN}[OK] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }

show_banner() {
    cat << 'EOF'
    _   _                      _ _
   | \ | |                    | (_)
   |  \| | _____      _____  __| |_  ____
   | . ` |/ _ \ \ /\ / / __|/ _` | |/ / /
   | |\  |  __/\ V  V /\__ \ (_| |   <| |
   |_| \_|\___| \_/\_/ |___/\__,_|_|\_\ \_|

   OpenClaw Deploy Tool v1.0.0
   One-click deploy OpenClaw
EOF
}

detect_os() {
    case "$OSTYPE" in
        linux-gnu*) echo "linux" ;;
        darwin*) echo "macos" ;;
        *msys*|*cygwin*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

check_installed() {
    if command -v openclaw &> /dev/null; then
        return 0
    fi
    return 1
}

install_openclaw() {
    local os_type=$(detect_os)

    if check_installed; then
        warn "OpenClaw installed: $(openclaw --version 2>/dev/null || echo 'unknown')"
        read -p "Reinstall? (y/N): " confirm
        if [[ "$confirm" != "y" ]] && [[ "$confirm" != "Y" ]]; then
            return 0
        fi
    fi

    log "Detected OS: $os_type"
    log "Installing OpenClaw..."

    case $os_type in
        linux|macos)
            log "Running official install script..."
            curl -fsSL https://openclaw.ai/install.sh | bash
            ;;
        windows)
            warn "Windows detected"
            warn "Please use PowerShell: iwr -useb https://openclaw.ai/install.ps1 | iex"
            log "Or run in WSL2/Ubuntu: curl -fsSL https://openclaw.ai/install.sh | bash"
            ;;
        *)
            error "Unsupported OS: $os_type"
            exit 1
            ;;
    esac
}

verify_installation() {
    log "Verifying installation..."

    if check_installed; then
        success "OpenClaw installed successfully!"
        log "Version: $(openclaw --version 2>/dev/null || echo 'unknown')"
        log ""
        log "Next steps:"
        log "  1. Run openclaw onboard to configure"
        log "  2. Run openclaw dashboard to open console"
        log "  3. Run openclaw status to check status"
    else
        error "Install verification failed"
    fi
}

main() {
    show_banner
    log ""
    log "=========================================="
    log "OpenClaw Deploy Tool"
    log "=========================================="
    log ""

    install_openclaw
    verify_installation

    log ""
    success "Done!"
}

main "$@"