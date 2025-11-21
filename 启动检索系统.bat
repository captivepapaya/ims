@echo off
chcp 65001 > nul
title Product Search System Launcher

echo ========================================
echo    Product Search System Launcher
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    echo Please install Python 3.7 or higher
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python is installed
python --version

:: 检查当前目录
if not exist "src" (
    echo Error: Please run this script in project root directory
    echo Current directory should contain src/, data/, docs/ folders
    pause
    exit /b 1
)

echo Directory structure is correct

:: 检查数据库
if not exist "data\inventory.db" (
    echo Error: Database file not found
    echo Please ensure data\inventory.db exists
    pause
    exit /b 1
)

echo Database file exists

:: 显示菜单
:menu
echo.
echo ========================================
echo    Select startup option:
echo ========================================
echo 1. Start Streamlit Search Interface (Recommended)
echo 2. Start API Server
echo 3. Check System Environment
echo 4. View User Guide
echo 0. Exit
echo ========================================
set /p choice="Please enter choice (0-4): "

if "%choice%"=="0" goto exit
if "%choice%"=="1" goto streamlit
if "%choice%"=="2" goto api
if "%choice%"=="3" goto check_env
if "%choice%"=="4" goto help
echo Invalid choice, please try again
goto menu

:streamlit
echo.
echo Starting Streamlit Search Interface...
cd /d "%~dp0src"
python -m streamlit run product_search_enhanced.py
if %errorlevel% neq 0 (
    echo Startup failed, please check error message
    pause
)
cd /d "%~dp0"
goto menu

:api
echo.
echo Starting API Server...
cd /d "%~dp0src\api"
python search_api.py
if %errorlevel% neq 0 (
    echo Startup failed, please check error message
    pause
)
cd /d "%~dp0"
goto menu

:check_env
echo.
echo 🔍 检查系统环境...
echo Python版本:
python --version

echo.
echo 检查依赖包...
python -c "
try:
    import streamlit
    print('✅ streamlit 已安装')
except ImportError:
    print('❌ streamlit 未安装')

try:
    import flask
    print('✅ flask 已安装')
except ImportError:
    print('❌ flask 未安装')

try:
    import flask_cors
    print('✅ flask_cors 已安装')
except ImportError:
    print('❌ flask_cors 未安装')

try:
    import pandas
    print('✅ pandas 已安装')
except ImportError:
    print('❌ pandas 未安装')

try:
    import sqlite3
    print('✅ sqlite3 已安装')
except ImportError:
    print('❌ sqlite3 未安装')
"

echo.
echo ✅ 系统环境检查完成
pause
goto menu

:help
echo.
echo 🔍 产品检索系统使用说明
echo ================================
echo.
echo 📁 文件结构:
echo   src\product_search_enhanced.py  - Streamlit应用
echo   src\api\search_api.py          - API服务器
echo   docs\product_search_guide.md   - 详细说明
echo   data\inventory.db             - 产品数据库
echo.
echo 🚀 启动方式:
echo   1. Streamlit界面 - 图形化搜索界面(推荐)
echo   2. API服务器     - RESTful API接口
echo.
echo 🌐 访问地址:
echo   Streamlit: http://localhost:8501
echo   API服务:  http://localhost:5000
echo.
echo 📖 更多信息请查看: docs\product_search_guide.md
echo.
pause
goto menu

:exit
echo.
echo 👋 退出系统，再见！
timeout /t 2 >nul
exit /b 0