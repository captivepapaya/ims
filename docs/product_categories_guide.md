# 产品分类系统说明文档

## 概述

本文档描述了库存管理系统中的产品分类系统，该系统基于CSNEW.csv文件中的分类数据构建，用于支持SKU生成和产品管理。

## 数据结构

### 源数据文件

- **文件位置**: `data/raw/CSNEW.csv`
- **格式**: CSV格式，UTF-8编码
- **列定义**:
  - `CatCode`: 三位数字分类代码 (如: 101, 501, 901)
  - `nCategory`: 主分类名称 (如: Artificial Flower Arrangements, Artificial Flowers)
  - `nSubCategory`: 子分类名称 (如: Banksia Series, Akebia, Acacia Tree)

### 数据库表结构

#### product_categories 表

```sql
CREATE TABLE product_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cat_code TEXT(3) NOT NULL UNIQUE,      -- 三位分类代码
    ncategory TEXT NOT NULL,               -- 主分类名称
    nsubcategory TEXT NOT NULL,            -- 子分类名称
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**索引**:
- `idx_cat_code`: 分类代码唯一索引
- `idx_ncategory`: 主分类索引
- `idx_nsubcategory`: 子分类索引

## 分类体系

### 主分类 (nCategory)

系统包含以下主分类：

1. **Artificial Flower Arrangements** (CatCode: 101-115, 100)
   - 人造花艺 arrangements 系列
   - 包含 Banksia, Cymbidium, Eucalyptus 等系列

2. **Artificial Flowers** (CatCode: 500-661, 503-660)
   - 单支人造花
   - 涵盖各种花卉类型：玫瑰、兰花、向日葵等

3. **Artificial Plants** (CatCode: 700-793)
   - 人造植物和绿植
   - 包括多肉植物、蕨类、棕榈等

4. **Artificial Planter Plants** (CatCode: 707-846, 800)
   - 盆栽人造植物
   - 包含各种盆栽绿植

5. **Artificial Trees** (CatCode: 900-939)
   - 人造树木
   - 包括竹子、棕榈树、果树等

6. **Hanging Basket** (CatCode: 201-203)
   - 悬挂花篮
   - 分为花卉、绿植和混合花篮

7. **Indoor Landscape** (CatCode: 221-225)
   - 室内景观
   - 包括地面景观、空中景观等

8. **Peripheral** (CatCode: 001-009)
   - 配套产品
   - 花瓶、花盆、蜡烛等装饰品

### 分类代码规则

- **第一位数字**: 表示主分类组别
  - 0xx: 配套产品 (Peripheral)
  - 1xx: 人造花艺 (Artificial Flower Arrangements)
  - 2xx: 悬挂花篮 (Hanging Basket)
  - 5xx: 人造花 (Artificial Flowers)
  - 7xx: 人造植物 (Artificial Plants)
  - 8xx: 人造盆栽 (Artificial Planter Plants)
  - 9xx: 人造树 (Artificial Trees)

- **后两位数字**: 子分类序列号

## SKU生成建议

基于此分类系统，建议的SKU格式：

```
SKU格式: [CatCode][产品编码][颜色代码][尺寸代码]
示例: 101-001-RD-L  (Banksia Series产品，红色，大号)
```

### SKU生成规则

1. **CatCode部分** (3位): 直接使用分类代码
2. **产品编码** (3位): 在分类内的唯一产品编号
3. **颜色代码** (2位): 颜色缩写
4. **尺寸代码** (1-2位): 尺寸标识

## 数据管理

### 导入数据

```bash
# 执行导入脚本
python scripts/import_categories.py
```

### 查询分类

```sql
-- 查询所有主分类
SELECT DISTINCT ncategory FROM product_categories ORDER BY ncategory;

-- 查询特定主分类下的所有子分类
SELECT cat_code, nsubcategory FROM product_categories
WHERE ncategory = 'Artificial Flowers' ORDER BY cat_code;

-- 根据分类代码查询
SELECT * FROM product_categories WHERE cat_code = '101';
```

### 更新分类

```sql
-- 更新分类信息
UPDATE product_categories
SET ncategory = 'New Category Name', nsubcategory = 'New SubCategory'
WHERE cat_code = '101';
```

## 与现有系统的集成

### products表集成

现有的`products`表已包含以下相关字段：
- `CatCode`: 与product_categories.cat_code对应
- `nCategory`: 与product_categories.ncategory对应
- `nSubCategory`: 与product_categories.nsubcategory对应

### 建议的改进

1. **建立外键关系**:
```sql
ALTER TABLE products ADD CONSTRAINT fk_cat_code
FOREIGN KEY (CatCode) REFERENCES product_categories(cat_code);
```

2. **数据一致性检查**:
```sql
-- 检查products表中的CatCode是否在分类表中存在
SELECT DISTINCT p.CatCode FROM products p
LEFT JOIN product_categories pc ON p.CatCode = pc.cat_code
WHERE pc.cat_code IS NULL;
```

## 使用场景

1. **产品管理**: 根据分类组织和查找产品
2. **库存分析**: 按分类统计库存情况
3. **销售报告**: 按分类分析销售数据
4. **网站分类**: 电商网站的产品分类展示
5. **SKU生成**: 自动化SKU编码系统

## 维护说明

1. **新增分类**: 直接在product_categories表中插入新记录
2. **修改分类**: 更新相应的ncategory或nsubcategory字段
3. **删除分类**: 建议使用软删除，标记为不活跃而非物理删除
4. **批量更新**: 使用import_categories.py脚本重新导入完整的分类数据

## 技术支持

如有疑问或需要技术支持，请联系系统管理员。

---

**文档版本**: 1.0
**创建日期**: 2025-11-21
**最后更新**: 2025-11-21