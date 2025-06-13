
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
