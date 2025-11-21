-- 创建产品分类表
CREATE TABLE IF NOT EXISTS product_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cat_code TEXT(3) NOT NULL UNIQUE,
    ncategory TEXT NOT NULL,
    nsubcategory TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE UNIQUE INDEX IF NOT EXISTS idx_cat_code ON product_categories(cat_code);
CREATE INDEX IF NOT EXISTS idx_ncategory ON product_categories(ncategory);
CREATE INDEX IF NOT EXISTS idx_nsubcategory ON product_categories(nsubcategory);

-- 插入CSV数据的预处理语句
-- 这个脚本将从CSV文件导入数据到product_categories表