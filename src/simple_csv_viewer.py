import csv
import os
import json
from pathlib import Path

# 简单的 CSV 查看器
class SimpleCSVViewer:
    def __init__(self):
        self.data_raw_path = Path("../data/raw")
        self.ensure_directory_exists()

    def ensure_directory_exists(self):
        """确保目录存在"""
        if not self.data_raw_path.exists():
            print(f"创建目录: {self.data_raw_path}")
            self.data_raw_path.mkdir(parents=True, exist_ok=True)

    def get_csv_files(self):
        """获取所有 CSV 文件"""
        csv_files = []
        if self.data_raw_path.exists():
            for file in self.data_raw_path.glob("*.csv"):
                csv_files.append(file.name)
        return csv_files

    def read_csv(self, filename):
        """读取 CSV 文件"""
        try:
            file_path = self.data_raw_path / filename
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
                return data, None
        except Exception as e:
            return None, str(e)

    def display_csv_info(self, filename):
        """显示 CSV 文件信息"""
        data, error = self.read_csv(filename)
        if error:
            print(f"读取文件失败: {error}")
            return

        if not data:
            print("文件为空")
            return

        print(f"\n文件: {filename}")
        print("=" * 50)
        print(f"行数: {len(data)}")

        if data:
            print(f"列名: {', '.join(data[0].keys())}")
            print(f"列数: {len(data[0].keys())}")

            # 显示前几行数据
            print("\n数据预览 (前5行):")
            print("-" * 50)
            for i, row in enumerate(data[:5]):
                print(f"第 {i+1} 行:")
                for key, value in row.items():
                    print(f"  {key}: {value}")
                print()

def main():
    """主函数"""
    viewer = SimpleCSVViewer()

    print("简单库存管理系统 - CSV 查看器")
    print("=" * 50)

    # 获取 CSV 文件列表
    csv_files = viewer.get_csv_files()

    if not csv_files:
        print("未找到 CSV 文件")
        print(f"请将 CSV 文件放置在: {viewer.data_raw_path}")
        return

    print(f"找到 {len(csv_files)} 个 CSV 文件:")
    for i, file in enumerate(csv_files, 1):
        print(f"  {i}. {file}")

    # 显示每个文件的信息
    for filename in csv_files:
        viewer.display_csv_info(filename)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()