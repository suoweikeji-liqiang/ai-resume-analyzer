
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI简历分析系统启动器
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    """主函数"""
    print("="*50)
    print("    AI简历智能分析系统")
    print("="*50)
    print("正在启动应用...")
    
    # 获取当前目录
    current_dir = Path(__file__).parent.absolute()
    app_path = current_dir / "app.py"
    
    if not app_path.exists():
        print(f"错误: 找不到应用文件 {app_path}")
        input("按回车键退出...")
        return
    
    try:
        # 启动Streamlit应用
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", "8501"]
        print(f"执行命令: {' '.join(cmd)}")
        
        # 启动应用
        process = subprocess.Popen(cmd, cwd=current_dir)
        
        # 等待几秒后打开浏览器
        time.sleep(3)
        print("正在打开浏览器...")
        webbrowser.open("http://localhost:8501")
        
        print("应用已启动!")
        print("浏览器地址: http://localhost:8501")
        print("按 Ctrl+C 停止应用")
        
        # 等待进程结束
        process.wait()
        
    except KeyboardInterrupt:
        print("
正在停止应用...")
        process.terminate()
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
