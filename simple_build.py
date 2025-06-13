
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
        print("
构建成功!")
        print("可执行文件位于 dist/ 目录中")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

if __name__ == "__main__":
    build()
