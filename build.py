#!/usr/bin/env python3
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

    @staticmethod
    def disable():
        global Colors
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.CYAN = ''
        Colors.NC = ''

def get_os():
    p = sys.platform
    if p.startswith('linux'):
        return 'linux'
    elif p.startswith('darwin'):
        return 'macos'
    elif p.startswith('win'):
        return 'windows'
    return 'unknown'

def get_arch():
    return platform.machine().lower()

def check_pyinstaller():
    try:
        result = subprocess.run(['pyinstaller', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def ensure_pyinstaller():
    if not check_pyinstaller():
        print(f"{Colors.YELLOW}正在安装 PyInstaller...{Colors.NC}")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)

def build_spec_file(target_os=None, output_dir=None):
    if target_os is None:
        target_os = get_os()

    if output_dir is None:
        output_dir = Path('dist')

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    script_name = 'post-deploy.py'
    app_name = 'OpenClawPostDeploy'

    if target_os == 'windows':
        ext = '.exe'
    else:
        ext = ''

    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{script_name}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['ctypes', 'subprocess', 'json', 'shutil', 'pathlib', 'datetime', 'platform'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{app_name}{ext}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    spec_file = Path(f'build_{target_os}.spec')
    spec_file.write_text(spec_content, encoding='utf-8')
    return spec_file

def build(target_os=None, output_dir=None):
    print(f"{Colors.CYAN}")
    print("=" * 50)
    print("  OpenClaw 跨平台打包工具")
    print("=" * 50)
    print(f"{Colors.NC}")

    current_os = get_os()

    if target_os is None:
        target_os = current_os

    print(f"当前平台: {current_os}")
    print(f"目标平台: {target_os}")
    print(f"输出目录: {output_dir or 'dist'}")
    print()

    if target_os not in ['linux', 'macos', 'windows']:
        print(f"{Colors.RED}错误: 不支持的平台 {target_os}{Colors.NC}")
        print(f"支持的平台: linux, macos, windows")
        sys.exit(1)

    ensure_pyinstaller()

    print(f"{Colors.GREEN}正在为 {target_os} 构建可执行文件...{Colors.NC}")

    spec_file = build_spec_file(target_os, output_dir)

    pyinstaller_cmd = ['pyinstaller', str(spec_file), '--workpath', 'build/wtemp', '--distpath', output_dir or 'dist']

    result = subprocess.run(pyinstaller_cmd)

    if result.returncode == 0:
        print(f"{Colors.GREEN}构建成功!{Colors.NC}")
    else:
        print(f"{Colors.RED}构建失败{Colors.NC}")
        sys.exit(1)

def build_all():
    print(f"{Colors.CYAN}")
    print("=" * 50)
    print("  OpenClaw 全平台打包")
    print("=" * 50)
    print(f"{Colors.NC}")

    ensure_pyinstaller()

    platforms = ['linux', 'macos', 'windows']

    for target_os in platforms:
        print(f"{Colors.YELLOW}{'='*50}{Colors.NC}")
        print(f"{Colors.YELLOW}正在构建 {target_os} 版本...{Colors.NC}")
        print(f"{Colors.YELLOW}{'='*50}{Colors.NC}")

        output_dir = f'dist/{target_os}'
        build(target_os, output_dir)
        print()

    print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
    print(f"{Colors.GREEN}全部平台构建完成!{Colors.NC}")
    print(f"{Colors.GREEN}{'='*50}{Colors.NC}")
    print()
    print(f"输出目录: dist/")
    print(f"  dist/linux/    - Linux 版本")
    print(f"  dist/macos/    - macOS 版本")
    print(f"  dist/windows/  - Windows 版本")

def clean():
    print(f"{Colors.YELLOW}清理构建文件...{Colors.NC}")
    dirs_to_remove = ['build', 'dist', '__pycache__', '.pytest_cache']
    for d in dirs_to_remove:
        if Path(d).exists():
            shutil.rmtree(d)
            print(f"  删除 {d}/")

    for f in Path('.').glob('*.spec'):
        if f.name.startswith('build_'):
            f.unlink()
            print(f"  删除 {f}")

    print(f"{Colors.GREEN}清理完成{Colors.NC}")

def main():
    if len(sys.argv) < 2:
        print(f"""
{Colors.CYAN}OpenClaw 跨平台打包工具{Colors.NC}

{Colors.GREEN}用法:{Colors.NC}
    python build.py <命令> [选项]

{Colors.GREEN}命令:{Colors.NC}
    python build.py build          构建当前平台版本
    python build.py build linux    构建 Linux 版本
    python build.py build macos    构建 macOS 版本
    python build.py build windows  构建 Windows 版本
    python build.py all            构建所有平台版本
    python build.py clean          清理构建文件

{Colors.GREEN}示例:{Colors.NC}
    python build.py build          构建当前平台
    python build.py all            一次性构建所有平台
    python build.py clean          清理
""")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == 'build':
        target = sys.argv[2].lower() if len(sys.argv) > 2 else None
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        build(target, output_dir)
    elif cmd == 'all':
        build_all()
    elif cmd == 'clean':
        clean()
    else:
        print(f"{Colors.RED}未知命令: {cmd}{Colors.NC}")
        main()

if __name__ == '__main__':
    main()
