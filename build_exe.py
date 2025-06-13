#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建可执行文件的脚本
使用PyInstaller将Streamlit应用打包成可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功!")
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller安装失败: {e}")
        return False
    return True

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.env', '.'),
        ('.env.example', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.state',
        'streamlit.runtime.caching',
        'streamlit.components.v1',
        'pandas',
        'plotly',
        'plotly.express',
        'plotly.graph_objects',
        'PyPDF2',
        'requests',
        'python-dotenv',
        'streamlit_aggrid',
        'streamlit_option_menu',
        'reportlab',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.lib.colors',
        'reportlab.pdfbase',
        'reportlab.pdfbase.ttfonts',
        'altair',
        'altair.vegalite.v4',
        'altair.vegalite.v4.api',
        'altair.vegalite.v4.schema',
        'altair.vegalite.v4.schema.channels',
        'altair.vegalite.v4.schema.core',
        'altair.vegalite.v4.schema.mixins',
        'tornado',
        'tornado.web',
        'tornado.websocket',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'click',
        'toml',
        'validators',
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'packaging.requirements',
        'pyarrow',
        'PIL',
        'PIL.Image',
        'numpy',
        'scipy',
        'matplotlib',
        'matplotlib.pyplot',
        'seaborn',
        'openpyxl',
        'xlsxwriter',
    ],
    hookspath=[],
    hooksconfig={},
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
    name='AI简历分析系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已创建 app.spec 文件")

def create_launcher_script():
    """创建启动脚本"""
    launcher_content = '''
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
        print("\n正在停止应用...")
        process.terminate()
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
'''
    
    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    print("已创建 launcher.py 启动脚本")

def build_executable():
    """构建可执行文件"""
    print("正在构建可执行文件...")
    try:
        # 使用spec文件构建
        subprocess.check_call(["pyinstaller", "app.spec", "--clean"])
        print("构建成功!")
        
        # 检查输出目录
        dist_dir = Path("dist")
        if dist_dir.exists():
            print(f"可执行文件位置: {dist_dir.absolute()}")
            
            # 复制必要文件到dist目录
            exe_dir = dist_dir / "AI简历分析系统"
            if exe_dir.exists():
                # 复制.env文件
                if Path(".env").exists():
                    shutil.copy2(".env", exe_dir)
                    print("已复制 .env 文件")
                
                # 复制README
                if Path("README.md").exists():
                    shutil.copy2("README.md", exe_dir)
                    print("已复制 README.md 文件")
                
                print(f"\n构建完成! 可执行文件位于: {exe_dir.absolute()}")
                print("运行可执行文件即可启动应用")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False

def main():
    """主函数"""
    print("AI简历分析系统 - 可执行文件构建工具")
    print("="*50)
    
    # 检查是否安装了PyInstaller
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        if not install_pyinstaller():
            return
    
    # 创建spec文件
    create_spec_file()
    
    # 创建启动脚本
    create_launcher_script()
    
    # 构建可执行文件
    if build_executable():
        print("\n构建完成!")
        print("\n使用说明:")
        print("1. 进入 dist/AI简历分析系统/ 目录")
        print("2. 运行 AI简历分析系统.exe")
        print("3. 应用将自动在浏览器中打开")
    else:
        print("\n构建失败，请检查错误信息")

if __name__ == "__main__":
    main()