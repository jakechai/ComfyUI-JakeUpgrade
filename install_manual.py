#!/usr/bin/env python3
"""
JakeUpgrade Nodes Auto-Install Script
JakeUpgrade 节点自动安装脚本
用于安装 ComfyUI 自定义节点所需的依赖包
For installing dependencies required by ComfyUI custom nodes
"""

import sys
import subprocess
import os
import platform
import re
from pathlib import Path

def get_comfyui_path():
    """获取 ComfyUI 根目录路径 / Get ComfyUI root path"""
    current_dir = Path(__file__).parent
    
    # 尝试多种可能的目录结构
    possible_paths = [
        current_dir.parent.parent,                  # root\ComfyUI\custom_nodes\
        current_dir.parent.parent.parent,           # root\ComfyUI\custom_nodes\node_name
        current_dir.parent.parent.parent.parent,    # root\ComfyUI\custom_nodes\node_name\subfolder
    ]
    
    for comfy_path in possible_paths:
        # 检查是否是 ComfyUI 目录
        if (comfy_path / "ComfyUI").exists():
            return comfy_path
    
    # 如果找不到，返回当前目录的父目录的父目录
    return current_dir.parent.parent

def get_python_executable():
    """获取 Python 可执行文件路径 / Get Python executable path"""
    comfy_path = get_comfyui_path()
    
    # 优先使用嵌入式 Python / Prefer embedded Python
    embedded_python = comfy_path / "python_embeded" / "python.exe"
    if embedded_python.exists():
        print(f"✅ Using embedded Python: {embedded_python}")
        return str(embedded_python)
    
    # 检查 ComfyUI 目录下的嵌入式 Python
    embedded_python2 = comfy_path / "ComfyUI" / "python_embeded" / "python.exe"
    if embedded_python2.exists():
        print(f"✅ Using embedded Python: {embedded_python2}")
        return str(embedded_python2)
    
    # 使用系统 Python / Use system Python
    system_python = sys.executable
    print(f"✅ Using system Python: {system_python}")
    return system_python

def check_python_version(python_exec):
    """检查 Python 版本 / Check Python version"""
    print("🔍 Checking Python version...")
    try:
        result = subprocess.run(
            [python_exec, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version_output = result.stdout.strip()
            print(f"✅ Python version: {version_output}")
            
            # 解析版本号 / Parse version number
            version_match = re.search(r"Python (\d+)\.(\d+)", version_output)
            if version_match:
                major, minor = int(version_match.group(1)), int(version_match.group(2))
                if major < 3 or (major == 3 and minor < 8):
                    print(f"❌ Unsupported Python version: {version_output}")
                    print("✅ Requires Python 3.8 or higher")
                    return False
            return True
    except Exception as e:
        print(f"❌ Failed to check Python version: {e}")
        return False
    
    return True

def check_existing_dependencies(python_exec):
    """检查已安装的依赖 / Check existing dependencies"""
    print("\n🔍 Checking existing dependencies...")
    
    try:
        # 获取已安装的包列表
        result = subprocess.run(
            [python_exec, "-s", "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            installed_packages = set()
            for line in result.stdout.strip().split('\n'):
                if line and '==' in line:
                    pkg = line.split('==', 1)[0].strip().lower()
                    installed_packages.add(pkg)
            
            # 读取 requirements.txt
            current_dir = Path(__file__).parent
            requirements_file = current_dir / "requirements.txt"
            
            with open(requirements_file, 'r', encoding='utf-8') as f:
                requirements = f.readlines()
            
            missing_packages = []
            for req in requirements:
                req = req.strip()
                if not req or req.startswith('#'):
                    continue
                
                # 只检查包名，不考虑版本
                pkg_name = req.strip().lower()
                
                if pkg_name not in installed_packages:
                    missing_packages.append(req)
                    print(f"❌ {req} - Not installed")
                else:
                    print(f"✅ {req} - Already installed")
            
            return missing_packages
        else:
            print(f"❌ Cannot get installed packages: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return None

def install_missing_only(python_exec, missing_packages):
    """只安装缺失的包 / Install only missing packages"""
    if not missing_packages:
        print("✅ All dependencies already installed")
        return True
    
    print(f"\n📦 Packages to install: {', '.join(missing_packages)}")
    
    try:
        # 为所有缺失的包一次性安装
        print("⏳ Installing missing dependencies...")
        result = subprocess.run(
            [python_exec, "-s", "-m", "pip", "install"] + missing_packages,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ Missing dependencies installed")
            return True
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during installation: {e}")
        return False

def install_requirements(python_exec):
    """安装 requirements.txt 中的依赖 / Install dependencies from requirements.txt"""
    print("\n📦 Starting dependency check...")
    
    current_dir = Path(__file__).parent
    requirements_file = current_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ requirements.txt not found: {requirements_file}")
        return False
    
    try:
        # 首先检查已安装的依赖
        missing_packages = check_existing_dependencies(python_exec)
        
        if missing_packages is None:
            # 如果检查失败，回退到传统安装方式
            print("⚠️ Dependency check failed, using traditional installation")
            return install_traditional(python_exec, requirements_file)
        
        # 只安装缺失的包
        return install_missing_only(python_exec, missing_packages)
            
    except Exception as e:
        print(f"❌ Exception during installation: {e}")
        return install_traditional(python_exec, requirements_file)

def install_traditional(python_exec, requirements_file):
    """传统安装方式（备用） / Traditional installation (fallback)"""
    print("🔄 Using traditional installation method")
    
    try:
        result = subprocess.run(
            [python_exec, "-s", "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ Dependencies installation completed!")
            return True
        else:
            print(f"❌ Error during installation:")
            if result.stdout:
                print(f"Stdout: {result.stdout}")
            if result.stderr:
                print(f"Stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Installation timeout, check network connection or install manually")
        return False

def check_installation(python_exec):
    """检查安装结果 / Check installation results"""
    print("\n🔍 Checking installation results...")
    
    packages_to_check = [
        ("cv2", "opencv-python"),
        ("piexif", "piexif"),
        ("torch", "torch"),
        ("torchvision", "torchvision"),
        ("numpy", "numpy"),
        ("PIL", "pillow"),
        ("simpleeval", "simpleeval"),
        ("functools", "functools"),
        ("yaml", "PyYAML"),
        ("toml", "toml"),
        
    ]
    
    all_installed = True
    for import_name, package_name in packages_to_check:
        try:
            # 使用指定的 Python 执行器检查
            check_script = f"import {import_name}" if import_name != "PIL" else "import PIL"
            result = subprocess.run(
                [python_exec, "-c", check_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ {package_name} installed correctly")
            else:
                print(f"❌ {package_name} installation failed: {result.stderr}")
                all_installed = False
        except Exception as e:
            print(f"❌ Error checking {package_name}: {e}")
            all_installed = False
    
    return all_installed

def main():
    """主函数 / Main function"""
    print("=" * 60)
    print("🛠️  JakeUpgrade Nodes Installer")
    print("=" * 60)
    
    # 检查系统信息
    print(f"💻 OS: {platform.system()} {platform.release()}")
    print(f"📁 Working directory: {Path(__file__).parent}")
    
    # 获取 Python 执行器
    python_exec = get_python_executable()
    
    # 执行安装步骤
    if not check_python_version(python_exec):
        sys.exit(1)
    
    if not install_requirements(python_exec):
        print("\n❌ Dependency installation failed, try manual installation:")
        print("   1. Open command prompt or terminal")
        print("   2. Change to current directory")
        print(f"   3. Run: {python_exec} -m pip install -r requirements.txt")
        sys.exit(1)
    
    # 验证安装
    if check_installation(python_exec):
        print("\n🎉 Installation complete! JakeUpgrade Nodes ready!")
        print("🔧 You can now start ComfyUI and use JakeUpgrade nodes")
    else:
        print("\n⚠️  Some dependencies may not be installed correctly")
        print("💡 Recommended to restart ComfyUI and check if nodes work properly")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    import re
    main()