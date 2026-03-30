@echo off
chcp 65001 >nul
title 股票分析 AI Agent

echo ============================================
echo   股票分析 AI Agent 启动脚本
echo ============================================
echo.

:: 设置 Python 路径
set PYTHON_PATH=C:\Users\HP\AppData\Local\Programs\Python\Python314
set PYTHON_EXE=%PYTHON_PATH%\python.exe

:: 检查 Python 是否存在
if not exist "%PYTHON_EXE%" (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python: %PYTHON_EXE%
"%PYTHON_EXE%" --version
echo.

:: 切换到项目目录
cd /d "%~dp0"
echo [OK] 项目目录: %cd%
echo.

:: 检查依赖是否已安装
echo 检查依赖...
"%PYTHON_EXE%" -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [安装] 正在安装依赖，请稍候...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
    echo.
)

echo [OK] 依赖已就绪
echo.

:: 检查 .env 文件
if not exist ".env" (
    echo [提示] 未找到 .env 文件
    echo 请在 .env 文件中配置 DASHSCOPE_API_KEY：
    echo.
    echo   DASHSCOPE_API_KEY=你的阿里百炼密钥
    echo   DASHSCOPE_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
    echo   DASHSCOPE_MODEL=glm-5
    echo.
    echo 获取密钥: https://bailian.console.aliyun.com
    echo.
)

:: 启动 Streamlit
echo ============================================
echo   正在启动 Streamlit...
echo ============================================
echo.
echo 本地访问: http://localhost:8501
echo 局域网访问: http://你的IP:8501
echo (按 Ctrl+C 停止服务)
echo.

"%PYTHON_EXE%" -m streamlit run app.py --server.address 0.0.0.0

pause