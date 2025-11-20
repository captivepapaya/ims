#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
库存管理系统数据库初始化脚本
从CSV文件读取数据并创建SQLite数据库
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

def create_database():
    """创建SQLite数据库并导入数据"""

    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventory.db')
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'LT.csv')
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'LTreadme.csv')

    print("正在初始化数据库...")
    print(f"数据库路径: {db_path}")
    print(f"数据文件: {csv_path}")

    # 创建数据目录（如果不存在）
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 读取字段定义
        print("正在读取字段定义...")
        field_definitions = pd.read_csv(readme_path)

        # 筛选需要导入数据库的字段
        import_fields = field_definitions[field_definitions['是否导入数据库'] == 'Yes']

        print(f"总共 {len(field_definitions)} 个字段，需要导入 {len(import_fields)} 个字段")

        # 创建产品表
        print("正在创建产品表...")

        # 定义字段类型映射
        field_types = {
            'Code': 'TEXT',
            'SU': 'TEXT',
            'SKU': 'TEXT UNIQUE',
            'Barcode': 'TEXT',
            'Description': 'TEXT',
            'NetCost': 'REAL',
            'DiscRate': 'REAL',
            'FinalCost': 'REAL',
            'RefPrice': 'REAL',
            'ListPrice': 'REAL',
            'RegularPrice': 'REAL',
            'SalePrice': 'REAL',
            'HL': 'TEXT',
            'Location': 'TEXT',
            'Color': 'TEXT',
            'Cluster': 'TEXT',
            'Qty': 'INTEGER',
            'Stock': 'INTEGER',
            'Sold': 'INTEGER',
            'StockStatus': 'TEXT',
            'CatCode': 'TEXT',
            'AppliedModel': 'TEXT',
            'ModelCode': 'TEXT',
            'Category': 'TEXT',
            'SubCat': 'TEXT',
            'PostID': 'INTEGER',
            'PostTitle': 'TEXT',
            'PostSlug': 'TEXT',
            'PostContent': 'TEXT',
            'PostShortDesc': 'TEXT',
            'PostStatus': 'TEXT',
            'ProductCat': 'TEXT',
            'ProductTag': 'TEXT',
            'ProductStyle': 'TEXT',
            'FocusKW': 'TEXT',
            'MetaTitle': 'TEXT',
            'MetaDesc': 'TEXT',
            'ProductPage': 'TEXT',
            'Images': 'TEXT',
            'Image': 'TEXT',
            'Comment': 'TEXT',
            'nCategory': 'TEXT',
            'nSubCategory': 'TEXT',
            'Index': 'INTEGER',  # 保留关键字，需要引号
            'Price': 'REAL',
            'Name': 'TEXT',
            'PNDesc': 'TEXT',
            'PNLen': 'INTEGER',
            'Per': 'INTEGER',
            'PC': 'TEXT'
        }

        # 构建CREATE TABLE语句
        create_table_sql = "CREATE TABLE IF NOT EXISTS products (\n"
        create_table_sql += "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"

        fields_to_import = []
        for _, row in import_fields.iterrows():
            field_name = row['列名']
            if field_name in field_types:
                fields_to_import.append(field_name)
                # 处理保留关键字
                if field_name == 'Index':
                    create_table_sql += f"    \"{field_name}\" {field_types[field_name]},\n"
                else:
                    create_table_sql += f"    {field_name} {field_types[field_name]},\n"

        create_table_sql += "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n"
        create_table_sql += "    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
        create_table_sql += ");"

        print(f"SQL建表语句:\n{create_table_sql}")
        cursor.execute(create_table_sql)

        # 读取CSV数据
        print("正在读取CSV数据...")
        df = pd.read_csv(csv_path)

        print(f"CSV数据总行数: {len(df)}")
        print(f"CSV列数: {len(df.columns)}")

        # 只导入需要的字段
        import_data = df[fields_to_import].copy()

        # 处理缺失值
        import_data = import_data.fillna('')

        # 处理数值字段
        numeric_fields = ['NetCost', 'DiscRate', 'FinalCost', 'RefPrice', 'ListPrice',
                         'RegularPrice', 'SalePrice', 'Qty', 'Stock', 'Sold', 'PostID',
                         'Index', 'Price', 'PNLen', 'Per']

        for field in numeric_fields:
            if field in import_data.columns:
                import_data[field] = pd.to_numeric(import_data[field], errors='coerce').fillna(0)

        print(f"准备导入 {len(import_data)} 条记录...")

        # 批量插入数据
        batch_size = 1000
        total_imported = 0

        for i in range(0, len(import_data), batch_size):
            batch = import_data.iloc[i:i+batch_size]

            # 构建插入SQL，需要处理Index字段名
            field_names_sql = []
            for field in fields_to_import:
                if field == 'Index':
                    field_names_sql.append(f'"{field}"')
                else:
                    field_names_sql.append(field)

            placeholders = ', '.join(['?' for _ in range(len(fields_to_import))])
            insert_sql = f"INSERT INTO products ({', '.join(field_names_sql)}) VALUES ({placeholders})"

            # 转换数据为tuple列表
            data_tuples = [tuple(row) for row in batch.values]

            cursor.executemany(insert_sql, data_tuples)
            total_imported += len(batch)

            print(f"已导入 {total_imported}/{len(import_data)} 条记录...")

        # 提交事务
        conn.commit()

        # 创建索引
        print("正在创建索引...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_sku ON products(SKU);",
            "CREATE INDEX IF NOT EXISTS idx_code ON products(Code);",
            "CREATE INDEX IF NOT EXISTS idx_category ON products(Category);",
            "CREATE INDEX IF NOT EXISTS idx_subcat ON products(SubCat);",
            "CREATE INDEX IF NOT EXISTS idx_stock_status ON products(StockStatus);"
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        conn.commit()

        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM products;")
        count = cursor.fetchone()[0]

        print("\n数据库创建成功！")
        print(f"数据库路径: {db_path}")
        print(f"总记录数: {count}")
        print(f"字段数: {len(fields_to_import)}")

        # 显示前几条记录
        cursor.execute("SELECT SKU, Description, Category, Stock, Price FROM products LIMIT 5;")
        sample_data = cursor.fetchall()
        print("\n样本数据:")
        print("SKU\t|\tDescription\t|\tCategory\t|\tStock\t|\tPrice")
        print("-" * 80)
        for row in sample_data:
            print(f"{row[0]}\t|\t{row[1][:30]}\t|\t{row[2]}\t|\t{row[3]}\t|\t{row[4]}")

    except Exception as e:
        print(f"错误: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

    return db_path

if __name__ == "__main__":
    create_database()