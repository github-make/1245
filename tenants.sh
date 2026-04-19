#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }
success() { echo -e "${GREEN}[OK] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }

TENANTS_DIR="$HOME/.openclaw/tenants"

mkdir -p "$TENANTS_DIR"

list_tenants() {
    echo ""
    echo "=========================================="
    echo "       Tenant List"
    echo "=========================================="
    echo ""

    if [[ ! -d "$TENANTS_DIR" ]] || [[ -z "$(ls -A "$TENANTS_DIR" 2>/dev/null)" ]]; then
        warn "No tenants found"
        return
    fi

    printf "${CYAN}%-20s %-15s %-10s %s${NC}\n" "Tenant ID" "Name" "Status" "Deployed"
    echo "----------------------------------------"

    for tenant_dir in "$TENANTS_DIR"/*/; do
        [[ -d "$tenant_dir" ]] || continue

        local tenant_id=$(basename "$tenant_dir")
        local config_file="$tenant_dir/config.json"

        if [[ -f "$config_file" ]]; then
            local name=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$config_file" 2>/dev/null | cut -d'"' -f4 || echo "N/A")
            local status=$(grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' "$config_file" 2>/dev/null | cut -d'"' -f4 || echo "unknown")
            local date=$(grep -o '"deployed"[[:space:]]*:[[:space:]]*"[^"]*"' "$config_file" 2>/dev/null | cut -d'"' -f4 || echo "N/A")

            printf "%-20s %-15s %-10s %s\n" "$tenant_id" "$name" "$status" "$date"
        fi
    done

    echo ""
}

add_tenant() {
    echo ""
    echo "=========================================="
    echo "       Add New Tenant"
    echo "=========================================="
    echo ""

    read -p "Tenant ID (e.g., company_a): " tenant_id

    if [[ -z "$tenant_id" ]]; then
        error "Tenant ID cannot be empty"
        return 1
    fi

    if [[ -d "$TENANTS_DIR/$tenant_id" ]]; then
        error "Tenant $tenant_id already exists"
        return 1
    fi

    read -p "Customer name: " customer_name
    read -p "Email: " email
    read -p "Server (IP/domain): " server_host
    read -p "Notes (optional): " notes

    local deploy_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    mkdir -p "$TENANTS_DIR/$tenant_id"

    cat > "$TENANTS_DIR/$tenant_id/config.json" << EOF
{
  "tenant_id": "$tenant_id",
  "name": "$customer_name",
  "email": "$email",
  "server_host": "$server_host",
  "notes": "$notes",
  "status": "deployed",
  "deployed": "$deploy_time",
  "last_updated": "$deploy_time"
}
EOF

    success "Tenant $tenant_id added successfully"
    info "Config file: $TENANTS_DIR/$tenant_id/config.json"
}

remove_tenant() {
    echo ""
    echo "=========================================="
    echo "       Remove Tenant"
    echo "=========================================="
    echo ""

    read -p "Enter tenant ID to remove: " tenant_id

    if [[ ! -d "$TENANTS_DIR/$tenant_id" ]]; then
        error "Tenant $tenant_id does not exist"
        return 1
    fi

    read -p "WARNING: This cannot be undone! Confirm? (yes/no): " confirm

    if [[ "$confirm" == "yes" ]]; then
        rm -rf "$TENANTS_DIR/$tenant_id"
        success "Tenant $tenant_id removed"
    else
        warn "Cancelled"
    fi
}

update_tenant() {
    echo ""
    echo "=========================================="
    echo "       Update Tenant Status"
    echo "=========================================="
    echo ""

    read -p "Enter tenant ID: " tenant_id

    if [[ ! -d "$TENANTS_DIR/$tenant_id" ]]; then
        error "Tenant $tenant_id does not exist"
        return 1
    fi

    local config_file="$TENANTS_DIR/$tenant_id/config.json"

    echo "Current config:"
    cat "$config_file"
    echo ""

    read -p "New status (active/suspended/inactive, empty to skip): " new_status

    if [[ -n "$new_status" ]]; then
        sed -i "s/\"status\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"status\": \"$new_status\"/" "$config_file"
    fi

    local update_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    sed -i "s/\"last_updated\"[[:space:]]*:[[:space:]]*\"[^\"]*\"/\"last_updated\": \"$update_time\"/" "$config_file"

    success "Tenant updated"
}

show_details() {
    echo ""
    read -p "Enter tenant ID: " tenant_id

    if [[ ! -d "$TENANTS_DIR/$tenant_id" ]]; then
        error "Tenant $tenant_id does not exist"
        return 1
    fi

    local config_file="$TENANTS_DIR/$tenant_id/config.json"

    echo ""
    echo "=========================================="
    echo "       Tenant Details: $tenant_id"
    echo "=========================================="
    echo ""

    if [[ -f "$config_file" ]]; then
        cat "$config_file"
    else
        error "Config file not found"
    fi

    echo ""
}

usage() {
    cat << 'EOF'
OpenClaw Tenant Management Tool

Usage: ./tenants.sh <command>

Commands:
    list              List all tenants
    add               Add new tenant
    remove            Remove tenant
    update            Update tenant status
    details           Show tenant details

Examples:
    ./tenants.sh list
    ./tenants.sh add
EOF
}

case "${1:-}" in
    list) list_tenants ;;
    add) add_tenant ;;
    remove) remove_tenant ;;
    update) update_tenant ;;
    details) show_details ;;
    *) usage ;;
esac