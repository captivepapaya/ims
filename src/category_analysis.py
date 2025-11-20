#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分类系统分析脚本 - 验证新旧分类系统的对应关系
"""

import sqlite3
import pandas as pd
import os

def analyze_categories():
    """分析产品分类系统"""

    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventory.db')
    conn = sqlite3.connect(db_path)

    try:
        print("=== 分类系统分析报告 ===\n")

        # 1. 新分类系统统计 (nCategory, nSubCategory)
        print("1. 新分类系统统计 (nCategory, nSubCategory):")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT nCategory, nSubCategory, COUNT(*) as count
            FROM products
            WHERE nCategory != '' AND nSubCategory != ''
            GROUP BY nCategory, nSubCategory
            ORDER BY nCategory, nSubCategory;
        """)

        new_categories = cursor.fetchall()
        for category, subcat, count in new_categories:
            print(f"   {category} > {subcat}: {count} 条")

        print(f"\n   总计: {len(new_categories)} 个子分类")

        # 2. 旧分类系统统计 (Category, SubCat)
        print("\n2. 旧分类系统统计 (Category, SubCat):")
        cursor.execute("""
            SELECT Category, SubCat, COUNT(*) as count
            FROM products
            WHERE Category != '' AND SubCat != ''
            GROUP BY Category, SubCat
            ORDER BY Category, SubCat;
        """)

        old_categories = cursor.fetchall()
        print(f"   总计: {len(old_categories)} 个子分类")

        # 3. 验证 SubCat 与 nSubCategory 的一致性
        print("\n3. 验证 SubCat 与 nSubCategory 一致性:")
        cursor.execute("""
            SELECT COUNT(*)
            FROM products
            WHERE SubCat != nSubCategory
            AND SubCat != '' AND nSubCategory != '';
        """)

        inconsistent_count = cursor.fetchone()[0]
        if inconsistent_count == 0:
            print("   SubCat 与 nSubCategory 完全一致")
        else:
            print(f"   有 {inconsistent_count} 条记录 SubCat 与 nSubCategory 不一致")

        # 4. CatCode 分布分析
        print("\n4. CatCode 分布分析:")
        cursor.execute("""
            SELECT nCategory, nSubCategory, CatCode, COUNT(*) as count
            FROM products
            WHERE CatCode != '' AND nCategory != ''
            GROUP BY nCategory, nSubCategory, CatCode
            ORDER BY nCategory, CatCode;
        """)

        catcode_distribution = cursor.fetchall()
        current_cat = None
        for category, subcat, catcode, count in catcode_distribution:
            if category != current_cat:
                print(f"\n   {category}:")
                current_cat = category
            print(f"     {subcat} (CatCode: {catcode}): {count} 条")

        # 5. 找出没有 CatCode 的产品
        cursor.execute("SELECT COUNT(*) FROM products WHERE CatCode = '' OR CatCode IS NULL;")
        no_catcode_count = cursor.fetchone()[0]
        if no_catcode_count > 0:
            print(f"\n警告: 有 {no_catcode_count} 条产品缺少 CatCode")

        # 6. 空值统计
        print("\n6. 分类字段空值统计:")
        cursor.execute("""
            SELECT
                SUM(CASE WHEN Category IS NULL OR Category = '' THEN 1 ELSE 0 END) as null_category,
                SUM(CASE WHEN nCategory IS NULL OR nCategory = '' THEN 1 ELSE 0 END) as null_ncategory,
                SUM(CASE WHEN SubCat IS NULL OR SubCat = '' THEN 1 ELSE 0 END) as null_subcat,
                SUM(CASE WHEN nSubCategory IS NULL OR nSubCategory = '' THEN 1 ELSE 0 END) as null_nsubcat,
                SUM(CASE WHEN CatCode IS NULL OR CatCode = '' THEN 1 ELSE 0 END) as null_catcode
            FROM products;
        """)

        null_stats = cursor.fetchone()
        print(f"   空旧分类 (Category): {null_stats[0]}")
        print(f"   空新分类 (nCategory): {null_stats[1]}")
        print(f"   空旧子分类 (SubCat): {null_stats[2]}")
        print(f"   空新子分类 (nSubCategory): {null_stats[3]}")
        print(f"   空分类代码 (CatCode): {null_stats[4]}")

        # 7. 生成新分类到CatCode的映射表
        print("\n7. 新分类到CatCode的映射表:")
        cursor.execute("""
            SELECT DISTINCT nCategory, nSubCategory, CatCode
            FROM products
            WHERE nCategory != '' AND nSubCategory != '' AND CatCode != ''
            ORDER BY nCategory, nSubCategory;
        """)

        mappings = cursor.fetchall()
        print("   nCategory,nSubCategory,CatCode")
        for category, subcat, catcode in mappings:
            print(f"   {category},{subcat},{catcode}")

        print(f"\n=== 分析完成 ===")

    except Exception as e:
        print(f"分析过程中出现错误: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    analyze_categories()