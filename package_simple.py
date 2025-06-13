#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版打包脚本
使用auto-py-to-exe提供图形界面打包
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def install_dependencies():
    """安装打包依赖"""
    dependencies = [
        "pyinstaller",
        "auto-py-to-exe"
    ]
    
    print("正在安装打包工具...")
    for dep in dependencies:
        try:
            print(f"安装 {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"{dep} 安装成功!")
        except subprocess.CalledProcessError as e:
            print(f"{dep} 安装失败: {e}")
            return False
    return True

def create_config_json():
    """创建auto-py-to-exe配置文件"""
    config = {
        "version": "auto-py-to-exe-configuration_v1",
        "pyinstallerOptions": [
            {
                "optionDest": "filenames",
                "value": "app.py"
            },
            {
                "optionDest": "onefile",
                "value": True
            },
            {
                "optionDest": "console",
                "value": True
            },
            {
                "optionDest": "name",
                "value": "AI简历分析系统"
            },
            {
                "optionDest": "add_data",
                "value": ".env;."
            },
            {
                "optionDest": "add_data",
                "value": ".env.example;."
            },
            {
                "optionDest": "add_data",
                "value": "README.md;."
            },
            {
                "optionDest": "hidden_import",
                "value": "streamlit"
            },
            {
                "optionDest": "hidden_import",
                "value": "streamlit.web.cli"
            },
            {
                "optionDest": "hidden_import",
                "value": "pandas"
            },
            {
                "optionDest": "hidden_import",
                "value": "plotly"
            },
            {
                "optionDest": "hidden_import",
                "value": "PyPDF2"
            },
            {
                "optionDest": "hidden_import",
                "value": "requests"
            },
            {
                "optionDest": "hidden_import",
                "value": "python-dotenv"
            },
            {
                "optionDest": "hidden_import",
                "value": "streamlit_aggrid"
            },
            {
                "optionDest": "hidden_import",
                "value": "streamlit_option_menu"
            },
            {
                "optionDest": "hidden_import",
                "value": "reportlab"
            }
        ]
    }
    
    with open('auto-py-to-exe-config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("已创建 auto-py-to-exe-config.json 配置文件")

def create_streamlit_launcher():
    """创建Streamlit启动器"""
    launcher_content = '''
import streamlit.web.cli as stcli
import sys
import os
from pathlib import Path

def main():
    # 获取当前目录
    current_dir = Path(__file__).parent.absolute()
    app_path = current_dir / "app.py"
    
    # 设置Streamlit参数
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port=8501",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    
    # 启动Streamlit
    stcli.main()

if __name__ == "__main__":
    main()
'''
    
    with open('streamlit_launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("已创建 streamlit_launcher.py")

def create_simple_build_script():
    """创建简单的PyInstaller构建脚本"""
    build_script = '''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
from pathlib import Path

def build():
    """使用PyInstaller构建可执行文件"""
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",
        "--name=AI简历分析系统",
        "--add-data=.env;.",
        "--add-data=.env.example;.",
        "--add-data=README.md;.",
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=streamlit.runtime.scriptrunner.script_runner",
        "--hidden-import=pandas",
        "--hidden-import=plotly",
        "--hidden-import=plotly.express",
        "--hidden-import=plotly.graph_objects",
        "--hidden-import=PyPDF2",
        "--hidden-import=requests",
        "--hidden-import=python-dotenv",
        "--hidden-import=streamlit_aggrid",
        "--hidden-import=streamlit_option_menu",
        "--hidden-import=reportlab",
        "--hidden-import=reportlab.lib.pagesizes",
        "--hidden-import=reportlab.platypus",
        "--hidden-import=altair",
        "--hidden-import=tornado",
        "--hidden-import=watchdog",
        "--hidden-import=click",
        "--hidden-import=toml",
        "--hidden-import=validators",
        "--hidden-import=packaging",
        "--clean",
        "streamlit_launcher.py"
    ]
    
    print("正在构建可执行文件...")
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\n构建成功!")
        print("可执行文件位于 dist/ 目录中")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

if __name__ == "__main__":
    build()
'''
    
    with open('simple_build.py', 'w', encoding='utf-8') as f:
        f.write(build_script)
    
    print("已创建 simple_build.py")

def main():
    """主函数"""
    print("AI简历分析系统 - 简化打包工具")
    print("="*50)
    
    # 安装依赖
    if not install_dependencies():
        print("依赖安装失败，请手动安装 pyinstaller 和 auto-py-to-exe")
        return
    
    # 创建配置文件
    create_config_json()
    create_streamlit_launcher()
    create_simple_build_script()
    
    print("\n准备工作完成!")
    print("\n打包方式选择:")
    print("1. 图形界面打包 (推荐新手):")
    print("   运行命令: auto-py-to-exe")
    print("   然后导入配置文件: auto-py-to-exe-config.json")
    print("")
    print("2. 命令行打包:")
    print("   运行命令: python simple_build.py")
    print("")
    print("3. 手动PyInstaller打包:")
    print("   运行命令: python build_exe.py")
    
    choice = input("\n请选择打包方式 (1/2/3): ").strip()
    
    if choice == "1":
        print("正在启动图形界面...")
        try:
            subprocess.Popen(["auto-py-to-exe"])
            print("请在图形界面中导入配置文件: auto-py-to-exe-config.json")
        except Exception as e:
            print(f"启动失败: {e}")
            print("请手动运行: auto-py-to-exe")
    
    elif choice == "2":
        print("正在使用命令行打包...")
        exec(open('simple_build.py').read())
    
    elif choice == "3":
        print("正在使用高级打包...")
        exec(open('build_exe.py').read())
    
    else:
        print("无效选择")

if __name__ == "__main__":
    main()