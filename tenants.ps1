# OpenClaw Tenant Management Tool - Windows PowerShell

param(
    [Parameter(Position=0)]
    [ValidateSet("list", "add", "remove", "update", "details")]
    [string]$Action = ""
)

$GREEN = "`e[0;32m"
$RED = "`e[0;31m"
$YELLOW = "`e[1;33m"
$BLUE = "`e[0;34m"
$CYAN = "`e[0;36m"
$NC = "`e[0m"

function Write-Success { param([string]$Message) Write-Host "${GREEN}[OK] $Message${NC}" }
function Write-Error { param([string]$Message) Write-Host "${RED}[ERROR] $Message${NC}" }
function Write-Warn { param([string]$Message) Write-Host "${YELLOW}[WARN] $Message${NC}" }
function Write-Info { param([string]$Message) Write-Host "${BLUE}[INFO] $Message${NC}" }

$TENANTS_DIR = "$env:USERPROFILE\.openclaw\tenants"

if (-not (Test-Path $TENANTS_DIR)) {
    New-Item -Path $TENANTS_DIR -ItemType Directory -Force | Out-Null
}

function List-Tenants {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "       Tenant List" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""

    $tenants = Get-ChildItem -Path $TENANTS_DIR -Directory -ErrorAction SilentlyContinue

    if (-not $tenants -or $tenants.Count -eq 0) {
        Write-Warn "No tenants found"
        return
    }

    $header = "{0,-20} {1,-15} {2,-12} {3}" -f "Tenant ID", "Name", "Status", "Deployed"
    Write-Host $header -ForegroundColor Magenta
    Write-Host ("-" * 70)

    foreach ($tenant in $tenants) {
        $configFile = Join-Path $tenant.FullName "config.json"

        if (Test-Path $configFile) {
            try {
                $config = Get-Content $configFile | ConvertFrom-Json

                $tenantId = if ($config.tenant_id) { $config.tenant_id } else { $tenant.Name }
                $name = if ($config.name) { $config.name } else { "N/A" }
                $status = if ($config.status) { $config.status } else { "unknown" }
                $deployed = if ($config.deployed) { $config.deployed } else { "N/A" }

                $line = "{0,-20} {1,-15} {2,-12} {3}" -f $tenantId, $name, $status, $deployed
                Write-Host $line
            }
            catch {
                Write-Host ("{0,-20} {1,-15} {2,-12} {3}" -f $tenant.Name, "N/A", "error", "N/A")
            }
        }
        else {
            Write-Host ("{0,-20} {1,-15} {2,-12} {3}" -f $tenant.Name, "N/A", "N/A", "N/A")
        }
    }

    Write-Host ""
}

function Add-Tenant {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "       Add New Tenant" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""

    $tenantId = Read-Host "Tenant ID (e.g., company_a)"

    if (-not $tenantId) {
        Write-Error "Tenant ID cannot be empty"
        return
    }

    $tenantPath = Join-Path $TENANTS_DIR $tenantId
    if (Test-Path $tenantPath) {
        Write-Error "Tenant $tenantId already exists"
        return
    }

    $customerName = Read-Host "Customer name"
    $email = Read-Host "Email"
    $serverHost = Read-Host "Server (IP/domain)"
    $notes = Read-Host "Notes (optional)"

    $deployTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

    New-Item -Path $tenantPath -ItemType Directory -Force | Out-Null

    $config = @{
        tenant_id = $tenantId
        name = $customerName
        email = $email
        server_host = $serverHost
        notes = $notes
        status = "deployed"
        deployed = $deployTime
        last_updated = $deployTime
    }

    $config | ConvertTo-Json | Set-Content (Join-Path $tenantPath "config.json")

    Write-Success "Tenant $tenantId added successfully"
    Write-Info "Config file: $tenantPath\config.json"
}

function Remove-Tenant {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "       Remove Tenant" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""

    $tenantId = Read-Host "Enter tenant ID to remove"

    $tenantPath = Join-Path $TENANTS_DIR $tenantId
    if (-not (Test-Path $tenantPath)) {
        Write-Error "Tenant $tenantId does not exist"
        return
    }

    $confirm = Read-Host "WARNING: This cannot be undone! Confirm? (yes/no)"
    if ($confirm -eq "yes") {
        Remove-Item -Path $tenantPath -Recurse -Force
        Write-Success "Tenant $tenantId removed"
    }
    else {
        Write-Warn "Cancelled"
    }
}

function Update-Tenant {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "       Update Tenant Status" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""

    $tenantId = Read-Host "Enter tenant ID"

    $tenantPath = Join-Path $TENANTS_DIR $tenantId
    if (-not (Test-Path $tenantPath)) {
        Write-Error "Tenant $tenantId does not exist"
        return
    }

    $configFile = Join-Path $tenantPath "config.json"

    Write-Host "Current config:"
    Get-Content $configFile | Format-List

    $newStatus = Read-Host "New status (active/suspended/inactive, empty to skip)"

    if ($newStatus) {
        $config = Get-Content $configFile | ConvertFrom-Json
        $config.status = $newStatus
        $config.last_updated = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        $config | ConvertTo-Json | Set-Content $configFile
        Write-Success "Tenant updated"
    }
}

function Show-Details {
    Write-Host ""
    $tenantId = Read-Host "Enter tenant ID"

    $tenantPath = Join-Path $TENANTS_DIR $tenantId
    if (-not (Test-Path $tenantPath)) {
        Write-Error "Tenant $tenantId does not exist"
        return
    }

    $configFile = Join-Path $tenantPath "config.json"

    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "       Tenant Details: $tenantId" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""

    if (Test-Path $configFile) {
        try {
            $config = Get-Content $configFile | ConvertFrom-Json
            $config | Format-List
        }
        catch {
            Get-Content $configFile
        }
    }
    else {
        Write-Error "Config file not found"
    }

    Write-Host ""
}

function Show-Usage {
    Write-Host @"
OpenClaw Tenant Management Tool (Windows)

Usage: .\tenants.ps1 <command>

Commands:
    list              List all tenants
    add               Add new tenant
    remove            Remove tenant
    update            Update tenant status
    details           Show tenant details

Examples:
    .\tenants.ps1 list
    .\tenants.ps1 add
"@
}

switch ($Action) {
    "list" { List-Tenants }
    "add" { Add-Tenant }
    "remove" { Remove-Tenant }
    "update" { Update-Tenant }
    "details" { Show-Details }
    default { Show-Usage }
}