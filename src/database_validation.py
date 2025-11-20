#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库验证脚本 - 验证数据完整性和一致性
"""

import sqlite3
import pandas as pd
import os

def validate_database():
    """验证数据库数据完整性"""

    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventory.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("=== 数据库验证报告 ===\n")

        # 1. 基本数据验证
        cursor.execute("SELECT COUNT(*) FROM products;")
        total_count = cursor.fetchone()[0]
        print(f"1. 总记录数: {total_count}")

        # 2. SKU唯一性验证
        cursor.execute("SELECT COUNT(DISTINCT SKU) FROM products;")
        unique_sku = cursor.fetchone()[0]
        print(f"2. 唯一SKU数量: {unique_sku}")
        if total_count != unique_sku:
            print(f"   警告: 存在重复的SKU")
        else:
            print(f"   SKU唯一性验证通过")

        # 3. 必填字段验证
        required_fields = ['SKU', 'Description', 'nCategory']
        for field in required_fields:
            cursor.execute(f"SELECT COUNT(*) FROM products WHERE {field} IS NULL OR {field} = '';")
            missing_count = cursor.fetchone()[0]
            if missing_count > 0:
                print(f"   警告: {field} 字段有 {missing_count} 条空记录")
            else:
                print(f"   {field} 字段验证通过")

        # 4. 数值字段合理性验证
        numeric_checks = [
            ("Stock >= 0", "Stock >= 0"),
            ("Price >= 0", "Price >= 0"),
            ("Qty >= 0", "Qty >= 0")
        ]

        for check_desc, condition in numeric_checks:
            cursor.execute(f"SELECT COUNT(*) FROM products WHERE NOT ({condition});")
            invalid_count = cursor.fetchone()[0]
            if invalid_count > 0:
                print(f"   警告: {check_desc} 有 {invalid_count} 条不合理记录")
            else:
                print(f"   {check_desc} 验证通过")

        # 5. 数据类型一致性验证
        print(f"\n3. 数据类型验证:")
        cursor.execute("SELECT COUNT(*) FROM products WHERE Stock != CAST(Stock AS INTEGER);")
        invalid_stock_type = cursor.fetchone()[0]
        if invalid_stock_type > 0:
            print(f"   警告: Stock字段有 {invalid_stock_type} 条非整数记录")
        else:
            print(f"   Stock字段类型验证通过")

        # 6. 业务逻辑验证
        print(f"\n4. 业务逻辑验证:")

        # 库存状态一致性
        cursor.execute("""
            SELECT COUNT(*) FROM products
            WHERE StockStatus = 'outofstock' AND Stock > 0;
        """)
        inconsistent_stock = cursor.fetchone()[0]
        if inconsistent_stock > 0:
            print(f"   警告: {inconsistent_stock} 条记录库存状态为'outofstock'但库存>0")
        else:
            print(f"   库存状态一致性验证通过")

        # 7. 数据分布统计
        print(f"\n5. 数据分布统计:")

        # 空值统计
        cursor.execute("""
            SELECT
                SUM(CASE WHEN Barcode IS NULL OR Barcode = '' THEN 1 ELSE 0 END) as null_barcode,
                SUM(CASE WHEN Location IS NULL OR Location = '' THEN 1 ELSE 0 END) as null_location,
                SUM(CASE WHEN Color IS NULL OR Color = '' THEN 1 ELSE 0 END) as null_color,
                SUM(CASE WHEN Image IS NULL OR Image = '' THEN 1 ELSE 0 END) as null_image
            FROM products;
        """)
        null_stats = cursor.fetchone()
        print(f"   空值统计:")
        print(f"   - 空条码: {null_stats[0]}")
        print(f"   - 空位置: {null_stats[1]}")
        print(f"   - 空颜色: {null_stats[2]}")
        print(f"   - 空图片: {null_stats[3]}")

        # 8. 示例数据检查
        print(f"\n6. 数据质量样本检查:")
        cursor.execute("""
            SELECT SKU, Description, Stock, Price, nCategory
            FROM products
            WHERE SKU IS NOT NULL AND Description IS NOT NULL
            ORDER BY RANDOM()
            LIMIT 5;
        """)
        samples = cursor.fetchall()

        for i, (sku, desc, stock, price, category) in enumerate(samples, 1):
            print(f"   样本{i}: SKU={sku}, Stock={stock}, Price=${price}, Category={category}")
            print(f"          Description: {desc[:50]}...")

        print(f"\n=== 验证完成 ===")
        print(f"数据库文件大小: {os.path.getsize(db_path) / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"验证过程中出现错误: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    validate_database()