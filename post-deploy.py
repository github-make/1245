#!/usr/bin/env python3
# OpenClaw 部署后自动化配置工具
# 安装完 OpenClaw 后，运行此脚本完成初始化配置

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def is_bundled():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_bundle_dir():
    if is_bundled():
        return Path(sys._MEIPASS)
    return Path(__file__).parent

def is_windows():
    return sys.platform.startswith('win')

def init_colors():
    if is_windows() and not is_bundled():
        os.system('')
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

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

init_colors()

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

def check_openclaw():
    return shutil.which('openclaw') is not None

def run_command(cmd, timeout=30, shell=False, check=False):
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=shell
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def run_openclaw_cmd(args, timeout=30):
    cmd = ['openclaw'] + args
    is_windows = sys.platform.startswith('win')
    return run_command(cmd, timeout=timeout, shell=is_windows)

def print_banner():
    banner = r"""
   _   _                      _ _
   | \ | |                    | (_)
   |  \| | _____      _____  __| |_  ____
   | . ` |/ _ \ \ /\ / / __|/ _` | |/ / /
   | |\  |  __/\ V  V /\__ \ (_| |   <|
   |_| \_|\___| \_/\_/ |___/\__,_|_|\_\ \_|
   OpenClaw 部署后配置工具 v1.0.0
    """
    print(f"{Colors.CYAN}{banner}{Colors.NC}")

def show_dashboard():
    info("正在打开控制台...")
    success("Dashboard 地址: http://127.0.0.1:18789/")
    success("按 Ctrl+C 停止，或关闭终端退出")
    print()
    run_openclaw_cmd(['dashboard'], timeout=300)

def run_onboard():
    print()
    info("=" * 50)
    info("  启动交互式配置向导")
    info("=" * 50)
    info("")
    info("此向导将引导您完成以下配置:")
    info("  1. 选择模型提供商 (Anthropic/OpenAI/Google)")
    info("  2. 设置 API 密钥")
    info("  3. 配置安全设置")
    info("  4. 设置消息通道 (Telegram 等)")
    info("  5. 安装后台服务")
    info("")
    warn("配置过程需要交互输入，请保持网络连接")
    print()

    success, stdout, stderr = run_openclaw_cmd(['onboard', '--install-daemon'], timeout=300)

    if success:
        success("配置完成!")
        return True
    else:
        error(f"配置失败: {stderr}")
        return False

def check_gateway_status():
    print()
    info("检查 Gateway 状态...")
    success, stdout, stderr = run_openclaw_cmd(['gateway', 'status'], timeout=30)

    if success and stdout:
        print(stdout)
        return True
    else:
        warn("Gateway 可能未运行")
        info("尝试启动 Gateway...")
        run_openclaw_cmd(['gateway', 'start'], timeout=30)
        return False

def check_doctor():
    print()
    info("运行健康检查...")
    success, stdout, stderr = run_openclaw_cmd(['doctor'], timeout=60)

    if stdout:
        print(stdout)

    if success:
        success("健康检查通过")
        return True
    else:
        warn("部分检查未通过，请根据提示修复")
        return False

def check_models():
    print()
    info("检查模型配置...")
    success, stdout, stderr = run_openclaw_cmd(['models', 'status'], timeout=30)

    if stdout:
        print(stdout)
        return success
    else:
        warn("模型状态检查失败")
        return False

def show_tutorial():
    print()
    print(f"{Colors.CYAN}{'='*60}")
    print("           OpenClaw 部署后操作指南")
    print(f"{'='*60}{Colors.NC}")
    print()
    print(f"{Colors.GREEN}一、首次配置（必须）{Colors.NC}")
    print()
    print(f"  {Colors.YELLOW}步骤 1: 交互式配置向导{Colors.NC}")
    print(f"    命令: {Colors.CYAN}openclaw onboard --install-daemon{Colors.NC}")
    print(f"    作用: 设置 API 密钥、选择模型、配置安全策略")
    print()
    print(f"  {Colors.YELLOW}步骤 2: 检查 Gateway 状态{Colors.NC}")
    print(f"    命令: {Colors.CYAN}openclaw gateway status{Colors.NC}")
    print(f"    作用: 确认服务运行在端口 18789")
    print()
    print(f"  {Colors.YELLOW}步骤 3: 打开控制台{Colors.CYAN}")
    print(f"    命令: {Colors.CYAN}openclaw dashboard{Colors.NC}")
    print(f"    作用: 在浏览器中打开 Web 控制台")
    print()
    print(f"{Colors.GREEN}二、日常运维命令{Colors.NC}")
    print()
    print(f"  {Colors.CYAN}openclaw status{Colors.NC}          - 查看快速状态摘要")
    print(f"  {Colors.CYAN}openclaw health{Colors.NC}          - 深度健康检查")
    print(f"  {Colors.CYAN}openclaw doctor{Colors.NC}          - 自动修复常见问题")
    print(f"  {Colors.CYAN}openclaw logs --follow{Colors.NC}   - 实时查看日志")
    print()
    print(f"{Colors.GREEN}三、配置消息通道（推荐）{Colors.NC}")
    print()
    print(f"  Telegram 通道配置:")
    print(f"    1. 在 Telegram 搜索 @BotFather")
    print(f"    2. 发送 /newbot 创建机器人")
    print(f"    3. 复制 Bot Token")
    print(f"    4. 运行: {Colors.CYAN}openclaw channels add telegram{Colors.NC}")
    print()
    print(f"{Colors.GREEN}四、技能安装（可选）{Colors.NC}")
    print()
    print(f"  {Colors.CYAN}openclaw skills list{Colors.CYAN}          - 查看可用技能")
    print(f"  {Colors.CYAN}openclaw skills install web-search{Colors.NC} - 安装网页搜索")
    print(f"  {Colors.CYAN}openclaw skills install browser{Colors.NC}    - 安装浏览器控制")
    print()
    print(f"{Colors.GREEN}五、控制台访问{Colors.NC}")
    print()
    print(f"  本地访问: {Colors.CYAN}http://127.0.0.1:18789/{Colors.NC}")
    print(f"  如果要求输入 Token，运行:")
    print(f"    {Colors.CYAN}openclaw config get gateway.auth.token{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}提示: 首次使用建议先运行 'openclaw doctor' 检查配置{Colors.NC}")
    print()

def show_usage():
    print(f"""
{Colors.CYAN}OpenClaw 部署后配置工具{Colors.NC}

{Colors.GREEN}用法:{Colors.NC}
    python post-deploy.py <命令>

{Colors.GREEN}可用命令:{Colors.NC}
    python post-deploy.py onboard     启动交互式配置向导
    python post-deploy.py dashboard   打开 Web 控制台
    python post-deploy.py status      检查 Gateway 状态
    python post-deploy.py doctor      运行健康检查
    python post-deploy.py models      检查模型配置
    python post-deploy.py tutorial     显示操作指南
    python post-deploy.py all         一键完整配置（推荐）

{Colors.GREEN}示例:{Colors.NC}
    python post-deploy.py all         完整自动化配置
    python post-deploy.py tutorial    查看操作指南
""")

def run_all():
    print()
    info("=" * 50)
    info("  OpenClaw 一键完整配置")
    info("=" * 50)
    print()

    if not check_openclaw():
        error("OpenClaw 未安装，请先运行 deploy.py")
        return

    success("OpenClaw 已安装")

    check_gateway_status()
    print()

    if run_onboard():
        print()
        check_doctor()
        print()
        check_models()

    print()
    info("=" * 50)
    info("  配置完成!")
    info("=" * 50)
    print()
    success("Dashboard 地址: http://127.0.0.1:18789/")
    print()
    info("后续操作:")
    info("  python post-deploy.py dashboard  打开控制台")
    info("  python post-deploy.py tutorial   查看详细教程")
    print()

def main():
    if len(sys.argv) < 2:
        print_banner()
        print(f"{Colors.YELLOW}请指定操作命令{Colors.NC}")
        show_usage()
        sys.exit(1)

    action = sys.argv[1].lower()

    if not check_openclaw():
        error("OpenClaw 未安装!")
        info("请先运行: python deploy.py deploy")
        sys.exit(1)

    if action == 'onboard':
        print_banner()
        run_onboard()
    elif action == 'dashboard':
        print_banner()
        show_dashboard()
    elif action == 'status':
        print_banner()
        check_gateway_status()
    elif action == 'doctor':
        print_banner()
        check_doctor()
    elif action == 'models':
        print_banner()
        check_models()
    elif action == 'tutorial':
        print_banner()
        show_tutorial()
    elif action == 'all':
        print_banner()
        run_all()
    else:
        error(f"未知命令: {action}")
        show_usage()
        sys.exit(1)

if __name__ == '__main__':
    main()
