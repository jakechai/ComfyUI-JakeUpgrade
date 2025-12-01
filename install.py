#!/usr/bin/env python3
"""
JakeUpgrade Nodes Auto-Install Script for ComfyUI
ComfyUI 自动安装脚本 - 简化版，无用户交互
"""

import sys
import subprocess
import os
from pathlib import Path

def run_installation():
    """执行安装流程"""
    try:
        # 使用当前 Python 解释器
        python_exec = sys.executable
        
        # requirements.txt 路径
        current_dir = Path(__file__).parent
        requirements_file = current_dir / "requirements.txt"
        
        if not requirements_file.exists():
            print(f"Requirements file not found: {requirements_file}")
            return False
        
        # 直接安装依赖
        print("Installing dependencies...")
        result = subprocess.run(
            [python_exec, "-s", "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("Dependencies installed successfully")
            return True
        else:
            print(f"Installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Installation error: {e}")
        return False

def main():
    """主函数 - 简化版，无用户交互"""
    print("JakeUpgrade Nodes Installer - ComfyUI Mode")
    
    success = run_installation()
    
    if success:
        print("Installation completed successfully")
    else:
        print("Installation failed")
    
    # 不等待用户输入，直接退出
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()