#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple dependency installer for Product Search System
"""

import subprocess
import sys

def install_package(package_name):
    """Install a single package"""
    print(f"Installing {package_name}...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package_name],
                      check=True, capture_output=True)
        print(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}: {e}")
        return False

def main():
    print("Product Search System - Dependency Installer")
    print("=" * 50)

    packages = [
        "streamlit",
        "flask",
        "flask-cors",
        "pandas",
        "requests"
    ]

    print(f"Installing {len(packages)} packages...")

    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1

    print(f"\nInstallation complete!")
    print(f"Success: {success_count}/{len(packages)}")

    if success_count == len(packages):
        print("All packages installed successfully!")
        print("You can now run the search system.")
    else:
        print("Some packages failed to install.")
        print("Please try manual installation:")
        for package in packages:
            print(f"  pip install {package}")

if __name__ == "__main__":
    main()