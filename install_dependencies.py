#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖包安装脚本
自动安装产品检索系统所需的所有依赖包
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n🔄 {description}...")
    print(f"执行: {command}")

    try:
        result = subprocess.run(command, shell=True, check=True,
                              capture_output=True, text=True, encoding='utf-8')
        print(f"✅ {description} 成功")
        if result.stdout:
            print(f"输出: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ {description} 执行出错: {e}")
        return False

def check_package_import(package_name, import_name=None):
    """检查包是否可以导入"""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"❌ {package_name} 未安装")
        return False

def install_package(package_name):
    """安装单个包"""
    print(f"\n📦 安装 {package_name}...")

    # 升级pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip")

    # 安装包
    success = run_command(f"{sys.executable} -m pip install {package_name}", f"安装 {package_name}")

    if success:
        # 验证安装
        import_name = package_name.replace('-', '_')
        if check_package_import(package_name, import_name):
            print(f"✅ {package_name} 安装并验证成功")
            return True
        else:
            print(f"⚠️ {package_name} 安装完成但验证失败")
            return False
    else:
        print(f"❌ {package_name} 安装失败")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 产品检索系统依赖包安装器")
    print("=" * 60)

    # 检查Python版本
    print(f"\n🐍 Python版本: {sys.version}")

    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        input("按回车键退出...")
        return False

    # 需要安装的包列表
    required_packages = [
        {
            "name": "streamlit",
            "import_name": "streamlit",
            "description": "Web应用框架"
        },
        {
            "name": "flask",
            "import_name": "flask",
            "description": "API服务器框架"
        },
        {
            "name": "flask-cors",
            "import_name": "flask_cors",
            "description": "跨域支持"
        },
        {
            "name": "pandas",
            "import_name": "pandas",
            "description": "数据处理库"
        },
        {
            "name": "requests",
            "import_name": "requests",
            "description": "HTTP请求库"
        }
    ]

    print(f"\n📋 需要安装 {len(required_packages)} 个依赖包:")
    for pkg in required_packages:
        print(f"  - {pkg['name']}: {pkg['description']}")

    # 询问是否继续
    choice = input("\n是否继续安装? (y/n): ").lower().strip()
    if choice != 'y':
        print("安装已取消")
        return False

    # 检查每个包的状态
    print("\n🔍 检查依赖包状态...")
    missing_packages = []

    for pkg in required_packages:
        if not check_package_import(pkg['name'], pkg['import_name']):
            missing_packages.append(pkg)

    if not missing_packages:
        print("\n🎉 所有依赖包都已安装!")
        input("按回车键继续...")
        return True

    print(f"\n📦 需要安装 {len(missing_packages)} 个缺失的包:")
    for pkg in missing_packages:
        print(f"  - {pkg['name']}")

    # 安装缺失的包
    success_count = 0
    total_count = len(missing_packages)

    for i, pkg in enumerate(missing_packages, 1):
        print(f"\n[{i}/{total_count}] 安装 {pkg['name']}...")

        if install_package(pkg['name']):
            success_count += 1
        else:
            print(f"⚠️ {pkg['name']} 安装失败，将跳过...")

    # 安装结果
    print(f"\n📊 安装结果:")
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失败: {total_count - success_count}/{total_count}")

    if success_count == total_count:
        print("\n🎉 所有依赖包安装成功!")
    else:
        print("\n⚠️ 部分依赖包安装失败")
        print("您可能需要手动安装失败的包:")
        for pkg in missing_packages:
            if not check_package_import(pkg['name'], pkg['import_name']):
                print(f"  pip install {pkg['name']}")

    # 验证所有包
    print("\n🔍 最终验证...")
    all_good = True
    for pkg in required_packages:
        if not check_package_import(pkg['name'], pkg['import_name']):
            all_good = False

    if all_good:
        print("\n✅ 所有依赖包验证通过!")
        print("\n🚀 您现在可以启动产品检索系统了!")
        print("   方法1: 双击运行 '启动检索系统.bat'")
        print("   方法2: 运行 'python start_search_system.py'")
    else:
        print("\n❌ 仍有依赖包未正确安装")
        print("请检查错误信息并重试")

    input("\n按回车键退出...")
    return all_good

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断安装")
    except Exception as e:
        print(f"\n❌ 安装过程出错: {e}")
        input("按回车键退出...")