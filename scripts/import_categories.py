#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品分类数据导入脚本
从CSNEW.csv文件导入数据到product_categories表
"""

import sqlite3
import csv
import os
from datetime import datetime

def import_categories():
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventory.db')
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'CSNEW.csv')

    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"连接到数据库: {db_path}")
        print(f"CSV文件路径: {csv_path}")

        # 检查CSV文件是否存在
        if not os.path.exists(csv_path):
            print(f"错误: CSV文件不存在 {csv_path}")
            return False

        # 首先创建product_categories表（如果不存在）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS product_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_code TEXT(3) NOT NULL UNIQUE,
            ncategory TEXT NOT NULL,
            nsubcategory TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_sql)

        # 创建索引
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_cat_code ON product_categories(cat_code);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ncategory ON product_categories(ncategory);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nsubcategory ON product_categories(nsubcategory);")

        # 清空现有数据（可选，根据需求选择是否保留现有数据）
        print("正在清空现有分类数据...")
        cursor.execute("DELETE FROM product_categories;")

        # 读取CSV文件并导入数据
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            imported_count = 0
            skipped_count = 0

            for row in csv_reader:
                try:
                    cat_code = row['CatCode'].strip()
                    ncategory = row['nCategory'].strip()
                    nsubcategory = row['nSubCategory'].strip()

                    # 验证数据
                    if not cat_code or not ncategory or not nsubcategory:
                        print(f"跳过无效行: {row}")
                        skipped_count += 1
                        continue

                    # 插入数据
                    insert_sql = """
                    INSERT INTO product_categories (cat_code, ncategory, nsubcategory, updated_at)
                    VALUES (?, ?, ?, ?)
                    """
                    cursor.execute(insert_sql, (cat_code, ncategory, nsubcategory, datetime.now()))
                    imported_count += 1

                except Exception as e:
                    print(f"处理行时出错 {row}: {e}")
                    skipped_count += 1
                    continue

        # 提交事务
        conn.commit()

        # 验证导入结果
        cursor.execute("SELECT COUNT(*) FROM product_categories")
        total_count = cursor.fetchone()[0]

        print(f"\n导入完成!")
        print(f"成功导入: {imported_count} 条记录")
        print(f"跳过记录: {skipped_count} 条")
        print(f"数据库中总记录数: {total_count}")

        # 显示前几条记录作为验证
        print("\n前5条记录预览:")
        cursor.execute("SELECT cat_code, ncategory, nsubcategory FROM product_categories LIMIT 5")
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[1]} - {row[2]}")

        return True

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return False

    except Exception as e:
        print(f"导入过程中发生错误: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("开始导入产品分类数据...")
    success = import_categories()
    if success:
        print("导入成功完成!")
    else:
        print("导入失败!")