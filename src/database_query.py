#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库查询工具 - 用于验证和查询库存数据
"""

import sqlite3
import pandas as pd
import os

def query_database():
    """查询数据库基本信息和统计"""

    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventory.db')
    conn = sqlite3.connect(db_path)

    try:
        cursor = conn.cursor()

        print("=== 数据库统计信息 ===")

        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM products;")
        total_count = cursor.fetchone()[0]
        print(f"总产品数量: {total_count}")

        # 库存状态统计
        cursor.execute("""
            SELECT StockStatus, COUNT(*) as count
            FROM products
            GROUP BY StockStatus
            ORDER BY count DESC;
        """)
        stock_status = cursor.fetchall()
        print("\n库存状态分布:")
        for status, count in stock_status:
            print(f"  {status}: {count}")

        # 分类统计
        cursor.execute("""
            SELECT nCategory, COUNT(*) as count
            FROM products
            WHERE nCategory != ''
            GROUP BY nCategory
            ORDER BY count DESC;
        """)
        categories = cursor.fetchall()
        print("\n产品分类分布:")
        for category, count in categories:
            print(f"  {category}: {count}")

        # 库存统计
        cursor.execute("""
            SELECT
                SUM(Stock) as total_stock,
                AVG(Stock) as avg_stock,
                MIN(Stock) as min_stock,
                MAX(Stock) as max_stock
            FROM products;
        """)
        stock_stats = cursor.fetchone()
        print(f"\n库存统计:")
        print(f"  总库存: {stock_stats[0]}")
        print(f"  平均库存: {stock_stats[1]:.1f}")
        print(f"  最小库存: {stock_stats[2]}")
        print(f"  最大库存: {stock_stats[3]}")

        # 价格统计
        cursor.execute("""
            SELECT
                AVG(Price) as avg_price,
                MIN(Price) as min_price,
                MAX(Price) as max_price
            FROM products
            WHERE Price > 0;
        """)
        price_stats = cursor.fetchone()
        print(f"\n价格统计:")
        print(f"  平均价格: ${price_stats[0]:.2f}")
        print(f"  最低价格: ${price_stats[1]:.2f}")
        print(f"  最高价格: ${price_stats[2]:.2f}")

        # 缺货产品
        cursor.execute("SELECT COUNT(*) FROM products WHERE StockStatus = 'outofstock';")
        outofstock = cursor.fetchone()[0]
        print(f"\n缺货产品数量: {outofstock}")

        # 库存充足产品（Stock > 0）
        cursor.execute("SELECT COUNT(*) FROM products WHERE Stock > 0;")
        in_stock = cursor.fetchone()[0]
        print(f"有库存产品数量: {in_stock}")

        # 显示一些示例产品
        print("\n=== 示例产品 ===")
        cursor.execute("""
            SELECT SKU, Description, nCategory, Stock, Price
            FROM products
            WHERE Stock > 0
            ORDER BY Price DESC
            LIMIT 10;
        """)

        products = cursor.fetchall()
        print(f"{'SKU':<12} | {'Category':<15} | {'Stock':<6} | {'Price':<8} | Description")
        print("-" * 80)
        for product in products:
            sku, desc, category, stock, price = product
            desc_short = desc[:30] + "..." if len(desc) > 30 else desc
            print(f"{sku:<12} | {category:<15} | {stock:<6} | ${price:<7.2f} | {desc_short}")

    finally:
        conn.close()

if __name__ == "__main__":
    query_database()