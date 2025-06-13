#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历比较工具安装和运行脚本
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version}")
    return True

def install_requirements():
    """安装依赖包"""
    print("\n📦 正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("\n⚠️  未找到.env文件")
            print("请按以下步骤配置:")
            print("1. 复制.env.example为.env")
            print("2. 编辑.env文件，填入你的OpenAI API密钥")
            print("3. 保存后重新运行此脚本")
            
            # 自动复制.env.example到.env
            try:
                import shutil
                shutil.copy(".env.example", ".env")
                print("\n✅ 已自动创建.env文件，请编辑后重新运行")
            except Exception as e:
                print(f"❌ 创建.env文件失败: {e}")
            return False
        else:
            print("❌ 未找到.env.example文件")
            return False
    
    # 检查.env文件内容
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            if "your_openai_api_key_here" in content:
                print("\n⚠️  请在.env文件中设置你的OpenAI API密钥")
                return False
            elif "OPENAI_API_KEY=" in content:
                print("✅ .env文件配置检查通过")
                return True
    except Exception as e:
        print(f"❌ 读取.env文件失败: {e}")
        return False
    
    return True

def run_streamlit():
    """运行Streamlit应用"""
    print("\n🚀 启动简历比较工具...")
    print("应用将在浏览器中自动打开")
    print("如果没有自动打开，请访问: http://localhost:8501")
    print("\n按Ctrl+C停止应用")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\n👋 应用已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        print("\n请尝试手动运行:")
        print("streamlit run app.py")

def main():
    """主函数"""
    print("=" * 50)
    print("📄 简历比较工具 - 安装和运行脚本")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_requirements():
        return
    
    # 检查环境变量配置
    if not check_env_file():
        return
    
    # 运行应用
    run_streamlit()

if __name__ == "__main__":
    main()