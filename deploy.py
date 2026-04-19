#!/usr/bin/env python3
# OpenClaw Deploy Tool - 跨平台版本

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

TENANTS_DIR = Path.home() / ".openclaw" / "tenants"

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

    @staticmethod
    def disable():
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.NC = ''

def is_windows():
    return sys.platform.startswith('win')

def get_os_display():
    os_map = {
        'linux': 'Linux',
        'macos': 'macOS',
        'windows': 'Windows'
    }
    os_type = detect_os()
    return os_map.get(os_type, 'Unknown')

def print_banner():
    os_name = get_os_display()
    banner = r"""
   _   _                      _ _
   | \ | |                    | (_)
   |  \| | _____      _____  __| |_  ____
   | . ` |/ _ \ \ /\ / / __|/ _` | |/ / /
   | |\  |  __/\ V  V /\__ \ (_| |   <|
   |_| \_|\___| \_/\_/ |___/\__,_|_|\_\ \_|
   OpenClaw Deploy Tool v1.0.0
   [{os_name}] 跨平台版本
    """.format(os_name=os_name)
    print(f"{Colors.CYAN}{banner}{Colors.NC}")

def log(msg):
    print(f"[{get_timestamp()}] {msg}")

def success(msg):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.NC}")

def error(msg):
    print(f"{Colors.RED}[ERROR] {msg}{Colors.NC}")

def warn(msg):
    print(f"{Colors.YELLOW}[WARN] {msg}{Colors.NC}")

def info(msg):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.NC}")

def get_timestamp():
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def detect_os():
    platform = sys.platform
    if platform.startswith('linux'):
        return 'linux'
    elif platform.startswith('darwin'):
        return 'macos'
    elif platform.startswith('win'):
        return 'windows'
    else:
        return 'unknown'

def check_installed():
    return shutil.which('openclaw') is not None

def get_version():
    try:
        result = subprocess.run(['openclaw', '--version'],
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.stdout else 'unknown'
    except:
        return 'unknown'

def check_node():
    node = shutil.which('node')
    if node:
        try:
            result = subprocess.run(['node', '--version'],
                                  capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.stdout else 'unknown'
        except:
            pass
    return None

def get_powershell_cmd():
    pwsh = shutil.which('pwsh')
    if pwsh:
        return pwsh
    return None

def install_openclaw():
    os_type = detect_os()
    pwsh_cmd = get_powershell_cmd()

    if check_installed():
        version = get_version()
        warn(f"OpenClaw 已安装: {version}")
        confirm = input("是否重新安装? (y/N): ").strip().lower()
        if confirm != 'y':
            return

    log(f"检测到系统: {os_type}")
    log("开始安装 OpenClaw...")

    if os_type in ('linux', 'macos'):
        log("执行官方安装脚本...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://openclaw.ai/install.sh'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run('curl -fsSL https://openclaw.ai/install.sh | bash',
                         shell=True, check=True)
        except subprocess.CalledProcessError as e:
            error(f"安装失败: {e}")
            info("备选方案: npm install -g openclaw@latest")

    elif os_type == 'windows':
        warn("Windows 环境检测到")
        print("\n安装选项:")
        print(f"  {Colors.CYAN}1){Colors.NC} 在 WSL2 Ubuntu 中安装 (推荐)")
        print(f"  {Colors.CYAN}2){Colors.NC} 直接在 Windows 安装")
        print(f"  {Colors.CYAN}3){Colors.NC} 跳过安装")

        choice = input("请选择 [1-3]: ").strip()

        if choice == '1':
            log("请在 WSL2 Ubuntu 终端中运行:")
            print(f"  {Colors.YELLOW}curl -fsSL https://openclaw.ai/install.sh | bash{Colors.NC}")
        elif choice == '2':
            log("执行官方安装脚本 (PowerShell)...")
            try:
                subprocess.run('powershell.exe -NoExit -Command "irm https://openclaw.ai/install.ps1 | iex"',
                             shell=True, timeout=180)
                success("安装完成")
            except subprocess.TimeoutExpired:
                success("安装完成")
            except subprocess.CalledProcessError:
                warn("官方脚本失败，尝试 npm...")
                try:
                    subprocess.run(['npm', 'install', '-g', 'openclaw@latest'],
                                 shell=True, check=True, timeout=180)
                    success("npm 安装完成")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    error("安装失败")
        else:
            warn("跳过安装")

def verify_installation():
    log("验证安装...")

    if check_installed():
        version = get_version()
        success("OpenClaw 安装成功!")
        log(f"版本: {version}")
        print()
        info("后续步骤:")
        info("  1. 运行 openclaw onboard 配置账号")
        info("  2. 运行 openclaw dashboard 查看控制台")
        info("  3. 运行 openclaw status 查看状态")
        print()
        info("或使用自动配置脚本:")
        info(f"  {Colors.CYAN}python post-deploy.py all{Colors.NC}  一键完整配置")
        info(f"  {Colors.CYAN}python post-deploy.py tutorial{Colors.NC}  查看详细教程")
    else:
        error("安装验证失败，请手动检查")

def ensure_tenants_dir():
    TENANTS_DIR.mkdir(parents=True, exist_ok=True)

def list_tenants():
    print()
    print(f"{Colors.CYAN}{'='*45}")
    print("       已部署的租户列表")
    print(f"{'='*45}{Colors.NC}")
    print()

    ensure_tenants_dir()

    if not TENANTS_DIR.exists() or not any(TENANTS_DIR.iterdir()):
        warn("暂无租户")
        return

    print(f"{Colors.CYAN}{'租户ID':<20} {'客户名称':<15} {'状态':<10} {'部署时间':<20}{Colors.NC}")
    print("-" * 70)

    for tenant_dir in sorted(TENANTS_DIR.iterdir()):
        if tenant_dir.is_dir():
            config_file = tenant_dir / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    tenant_id = config.get('tenant_id', tenant_dir.name)
                    name = config.get('name', 'N/A')
                    status = config.get('status', 'unknown')
                    deployed = config.get('deployed', 'N/A')
                    print(f"{tenant_id:<20} {name:<15} {status:<10} {deployed:<20}")
                except Exception:
                    print(f"{tenant_dir.name:<20} {'N/A':<15} {'error':<10} {'N/A':<20}")

    print()

def add_tenant():
    print()
    print(f"{Colors.CYAN}{'='*45}")
    print("       添加新租户")
    print(f"{'='*45}{Colors.NC}")
    print()

    tenant_id = input("租户 ID (如 company_a): ").strip()
    if not tenant_id:
        error("租户 ID 不能为空")
        return

    ensure_tenants_dir()
    tenant_path = TENANTS_DIR / tenant_id

    if tenant_path.exists():
        error(f"租户 {tenant_id} 已存在")
        return

    customer_name = input("客户名称: ").strip()
    email = input("联系邮箱: ").strip()
    server_host = input("服务器地址 (IP/域名): ").strip()
    notes = input("备注 (可选): ").strip()

    from datetime import datetime
    deploy_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    tenant_path.mkdir(parents=True)

    config = {
        "tenant_id": tenant_id,
        "name": customer_name,
        "email": email,
        "server_host": server_host,
        "notes": notes,
        "status": "deployed",
        "deployed": deploy_time,
        "last_updated": deploy_time
    }

    with open(tenant_path / "config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    success(f"租户 {tenant_id} 添加成功")
    info(f"配置文件: {tenant_path / 'config.json'}")

def remove_tenant():
    print()
    print(f"{Colors.CYAN}{'='*45}")
    print("       删除租户")
    print(f"{'='*45}{Colors.NC}")
    print()

    tenant_id = input("输入要删除的租户 ID: ").strip()
    tenant_path = TENANTS_DIR / tenant_id

    if not tenant_path.exists():
        error(f"租户 {tenant_id} 不存在")
        return

    confirm = input("警告：此操作不可恢复！确认删除? (yes/no): ").strip()
    if confirm == 'yes':
        shutil.rmtree(tenant_path)
        success(f"租户 {tenant_id} 已删除")
    else:
        warn("已取消")

def update_tenant():
    print()
    print(f"{Colors.CYAN}{'='*45}")
    print("       更新租户状态")
    print(f"{'='*45}{Colors.CYAN}")
    print()

    tenant_id = input("输入租户 ID: ").strip()
    tenant_path = TENANTS_DIR / tenant_id

    if not tenant_path.exists():
        error(f"租户 {tenant_id} 不存在")
        return

    config_file = tenant_path / "config.json"

    print("\n当前配置:")
    with open(config_file, 'r', encoding='utf-8') as f:
        print(f.read())

    new_status = input("\n新状态 (active/suspended/inactive, 回车跳过): ").strip()

    if new_status:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        config['status'] = new_status
        config['last_updated'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        success("租户已更新")
    else:
        warn("跳过更新")

def show_details():
    print()
    tenant_id = input("输入租户 ID: ").strip()
    tenant_path = TENANTS_DIR / tenant_id

    if not tenant_path.exists():
        error(f"租户 {tenant_id} 不存在")
        return

    config_file = tenant_path / "config.json"

    print()
    print(f"{Colors.CYAN}{'='*45}")
    print(f"       租户详情: {tenant_id}")
    print(f"{'='*45}{Colors.CYAN}")
    print()

    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        error("配置文件不存在")

    print()

def show_usage():
    print(f"""
{Colors.CYAN}OpenClaw 部署工具 (Python 跨平台版){Colors.NC}

{Colors.GREEN}部署命令:{Colors.NC}
    python deploy.py deploy          一键安装 OpenClaw

{Colors.GREEN}租户管理命令:{Colors.NC}
    python deploy.py list            列出所有租户
    python deploy.py add             添加新租户
    python deploy.py remove          删除租户
    python deploy.py update          更新租户状态
    python deploy.py details         查看租户详情

{Colors.GREEN}示例:{Colors.NC}
    python deploy.py deploy
    python deploy.py list
    python deploy.py add
""")

def main():
    if len(sys.argv) >= 2:
        action = sys.argv[1].lower()
        run_action(action)
    elif is_bundled():
        interactive_menu()
    else:
        print_banner()
        print(f"{Colors.YELLOW}请指定操作命令，输入 python deploy.py help 查看帮助{Colors.NC}\n")
        sys.exit(1)

    if is_bundled():
        input("\n按回车键退出...")

def is_bundled():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def interactive_menu():
    print_banner()
    while True:
        print(f"\n{Colors.CYAN}{'='*45}")
        print("       请选择操作")
        print(f"{'='*45}{Colors.NC}")
        print(f"  {Colors.GREEN}1.{Colors.NC} 一键部署 OpenClaw")
        print(f"  {Colors.GREEN}2.{Colors.NC} 查看租户列表")
        print(f"  {Colors.GREEN}3.{Colors.NC} 添加租户")
        print(f"  {Colors.GREEN}4.{Colors.NC} 删除租户")
        print(f"  {Colors.GREEN}5.{Colors.NC} 更新租户状态")
        print(f"  {Colors.GREEN}6.{Colors.NC} 查看租户详情")
        print(f"  {Colors.RED}0.{Colors.NC} 退出")
        print()

        choice = input("请输入选项 [0-6]: ").strip()

        action_map = {
            '1': 'deploy',
            '2': 'list',
            '3': 'add',
            '4': 'remove',
            '5': 'update',
            '6': 'details',
            '0': 'exit'
        }

        action = action_map.get(choice)
        if not action:
            warn("无效选项，请重新输入")
            continue

        if action == 'exit':
            break

        run_action(action)

def run_action(action):
    if action == 'help':
        show_usage()
    elif action == 'deploy':
        print_banner()
        log("")
        log("=" * 45)
        log("OpenClaw 一键部署工具")
        log("=" * 45)
        log("")

        node_version = check_node()
        if node_version:
            success(f"Node.js 已安装: {node_version}")
        else:
            warn("Node.js 未安装")
            print()
            info("请先安装 Node.js 22 LTS:")
            print(f"  {Colors.CYAN}https://nodejs.org/{Colors.NC}")
            print()
            cont = input("是否继续? (y/N): ").strip().lower()
            if cont != 'y':
                return

        install_openclaw()
        verify_installation()
        print()
        success("完成!")
    elif action == 'list':
        list_tenants()
    elif action == 'add':
        add_tenant()
    elif action == 'remove':
        remove_tenant()
    elif action == 'update':
        update_tenant()
    elif action == 'details':
        show_details()
    else:
        error(f"未知命令: {action}")
        info("输入 python deploy.py help 查看帮助")

if __name__ == '__main__':
    main()
