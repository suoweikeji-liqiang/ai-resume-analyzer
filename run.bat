@echo off
echo 启动简历比较工具...
echo.
echo 请确保已安装所需依赖:
echo pip install -r requirements.txt
echo.
echo 请确保已配置.env文件中的OPENAI_API_KEY
echo.
pause
streamlit run app.py
pause