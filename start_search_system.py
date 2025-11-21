#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品检索系统启动脚本
提供简单的命令行界面来启动不同的检索系统组件
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_requirements():
    """检查必要的依赖包"""
    required_packages = [
        'streamlit',
        'flask',
        'flask_cors',
        'pandas',
        'sqlite3'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'flask_cors':
                import flask_cors
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)

    return missing_packages

def install_package(package):
    """安装缺失的包"""
    print(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {package} 安装失败")
        return False

def check_database():
    """检查数据库文件是否存在"""
    db_path = Path("data/inventory.db")
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        print("请确保数据库文件存在且包含产品数据")
        return False
    print(f"✅ 数据库文件存在: {db_path}")
    return True

def start_streamlit_app():
    """启动Streamlit应用"""
    print("\n🚀 启动Streamlit检索应用...")

    # 切换到src目录
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src目录不存在")
        return False

    os.chdir(src_dir)

    try:
        # 启动streamlit应用
        cmd = [sys.executable, "-m", "streamlit", "run", "product_search_enhanced.py"]
        print(f"执行命令: {' '.join(cmd)}")
        print("⏳ 应用正在启动...")

        # 在新进程中启动
        process = subprocess.Popen(cmd)

        # 等待几秒后自动打开浏览器
        time.sleep(3)
        webbrowser.open("http://localhost:8501")

        print("✅ Streamlit应用已启动")
        print("🌐 访问地址: http://localhost:8501")
        print("💡 按 Ctrl+C 停止应用")

        # 等待进程结束
        process.wait()
        return True

    except KeyboardInterrupt:
        print("\n👋 用户中断，正在停止应用...")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def start_api_server():
    """启动API服务器"""
    print("\n🚀 启动API服务器...")

    # 切换到api目录
    api_dir = Path("src/api")
    if not api_dir.exists():
        print("❌ src/api目录不存在")
        return False

    os.chdir(api_dir)

    try:
        # 启动API服务器
        cmd = [sys.executable, "search_api.py"]
        print(f"执行命令: {' '.join(cmd)}")
        print("⏳ 服务器正在启动...")

        # 在新进程中启动
        process = subprocess.Popen(cmd)

        # 等待几秒后测试API
        time.sleep(2)

        # 测试API是否正常运行
        import requests
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ API服务器已启动")
                print("🌐 API地址: http://localhost:5000")
                print("📖 API文档: http://localhost:5000/api/health")
                print("💡 按 Ctrl+C 停止服务器")
            else:
                print("⚠️ 服务器已启动但健康检查失败")
        except requests.exceptions.RequestException:
            print("⚠️ 无法连接到API服务器，但进程可能仍在启动中")

        # 等待进程结束
        process.wait()
        return True

    except KeyboardInterrupt:
        print("\n👋 用户中断，正在停止服务器...")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def show_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("🔍 产品检索系统启动器")
    print("="*50)
    print("1. 启动Streamlit检索界面")
    print("2. 启动API服务器")
    print("3. 检查系统环境")
    print("4. 查看使用说明")
    print("0. 退出")
    print("="*50)

def check_environment():
    """检查系统环境"""
    print("\n🔍 检查系统环境...")

    # 检查Python版本
    python_version = sys.version
    print(f"Python版本: {python_version}")

    # 检查依赖包
    print("\n📦 检查依赖包...")
    missing_packages = check_requirements()

    if missing_packages:
        print(f"❌ 缺失以下依赖包: {', '.join(missing_packages)}")

        choice = input("\n是否自动安装缺失的包? (y/n): ").lower().strip()
        if choice == 'y':
            for package in missing_packages:
                install_package(package)
        else:
            print("请手动安装缺失的包: pip install " + " ".join(missing_packages))
            return False
    else:
        print("✅ 所有依赖包已安装")

    # 检查数据库
    check_database()

    print("\n✅ 系统环境检查完成")
    return True

def show_help():
    """显示使用说明"""
    help_text = """
🔍 产品检索系统使用说明
========================

启动方式:
1. Streamlit界面 - 提供图形化搜索界面
2. API服务器 - 提供RESTful API接口

文件结构:
src/product_search_enhanced.py  - Streamlit应用主文件
src/api/search_api.py          - API服务器
docs/product_search_guide.md   - 详细使用说明
data/inventory.db             - 产品数据库

快速开始:
1. 选择选项1启动Streamlit界面
2. 在浏览器中访问 http://localhost:8501
3. 输入搜索条件并点击"执行搜索"

更多信息请查看: docs/product_search_guide.md
    """
    print(help_text)

def main():
    """主函数"""
    print("欢迎使用产品检索系统！")

    while True:
        show_menu()

        try:
            choice = input("\n请选择操作 (0-4): ").strip()

            if choice == "0":
                print("👋 退出系统，再见！")
                break

            elif choice == "1":
                start_streamlit_app()

            elif choice == "2":
                start_api_server()

            elif choice == "3":
                check_environment()

            elif choice == "4":
                show_help()

            else:
                print("❌ 无效选择，请输入0-4之间的数字")

        except KeyboardInterrupt:
            print("\n👋 用户中断，退出系统")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    # 检查当前目录
    if not Path("src").exists():
        print("❌ 请在项目根目录运行此脚本")
        print("当前目录应包含src/、data/、docs/等文件夹")
        sys.exit(1)

    main()