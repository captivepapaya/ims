# 产品检索系统使用说明

## 概述

产品检索系统是为库存管理系统设计的高级搜索功能，支持多条件筛选和复杂的搜索语法。

## 功能特性

### 🔍 搜索功能
- **关键词搜索**: 支持SKU、供应商代码(Chrisy Code)、产品描述、子分类的模糊匹配
- **操作符支持**:
  - `+` (AND): 同时匹配多个条件
  - `-` (NOT): 排除特定关键词
  - `or`: 匹配任意一个条件
- **大小写不敏感**: 自动忽略大小写差异
- **标点符号忽略**: 自动忽略所有标点符号和空格

### 🏷️ 筛选功能
1. **供应商筛选**: 支持多选，"ALL"选项表示选择所有供应商
2. **高度/长度筛选**: 数值范围筛选，包含最小值和最大值
3. **价格筛选**: 基于List Price的数值范围筛选
4. **类别筛选**: 主分类单选 + 子分类多选(最多5个)

### 📊 结果显示
- **显示字段**: Code, SKU, Description, List Price, HL, Qty, Stock, Sold, Stock Status, nCategory, nSubCategory, Comment
- **分页显示**: 每页10条记录，支持翻页
- **统计信息**: 显示总记录数、当前显示范围、总页数

## 使用方法

### 启动方式

#### 方式1: Streamlit界面
```bash
cd src
streamlit run product_search_enhanced.py
```

#### 方式2: API服务 + 前端
```bash
# 启动API服务
cd src/api
python search_api.py

# API服务将在 http://localhost:5000 启动
```

### 搜索语法示例

#### 基本搜索
- `rose` - 搜索包含"rose"的产品
- `red` - 搜索包含"red"的产品
- `ABC123` - 搜索包含"ABC123"的产品

#### 组合搜索
- `rose +red` - 搜索同时包含"rose"和"red"的产品
- `flower -white` - 搜索包含"flower"但不包含"white"的产品
- `red or blue` - 搜索包含"red"或"blue"的产品

#### 复杂组合
- `rose +red -white` - 搜索包含"rose"和"red"但不包含"white"的产品
- `(big or large) +red` - 搜索包含"big"或"large"且包含"red"的产品

### 筛选条件设置

#### 供应商筛选
- 默认选择"ALL"表示搜索所有供应商的产品
- 取消"ALL"后可选择特定供应商，支持多选

#### 高度/长度筛选
- 输入最小值和最大值来设定范围
- 留空表示不限制该条件
- 例如: 最小值10，最大值50，搜索高度/长度在10-50之间的产品

#### 价格筛选
- 基于产品的List Price字段
- 输入最低价和最高价
- 支持小数点后两位

#### 类别筛选
- **主分类**: 必须选择一个主分类（或选择"全部"）
- **子分类**: 基于选择的主分类，可选择最多5个子分类
- 只有同时满足主分类和子分类条件的产品才会显示

### 快捷键操作
- `Ctrl + Enter`: 执行搜索
- `ESC`: 清空搜索框

## API接口文档

### 基础信息
- **基础URL**: `http://localhost:5000/api`
- **数据格式**: JSON
- **字符编码**: UTF-8

### 接口列表

#### 1. 健康检查
```http
GET /api/health
```
**响应示例**:
```json
{
  "status": "healthy",
  "message": "Product Search API is running"
}
```

#### 2. 获取供应商列表
```http
GET /api/suppliers
```
**响应示例**:
```json
{
  "suppliers": ["ALL", "Supplier1", "Supplier2", "Supplier3"]
}
```

#### 3. 获取主分类列表
```http
GET /api/categories
```
**响应示例**:
```json
{
  "categories": ["Artificial Flowers", "Artificial Plants", "Artificial Trees"]
}
```

#### 4. 获取子分类列表
```http
GET /api/subcategories?category=Artificial%20Flowers
```
**响应示例**:
```json
{
  "subcategories": ["Rose", "Lily", "Tulip", "Orchid"]
}
```

#### 5. 搜索产品 (GET)
```http
GET /api/products/search?q=rose+red&suppliers=Supplier1&min_price=10&max_price=100&page=1&per_page=10
```

**查询参数**:
- `q`: 搜索关键词
- `suppliers`: 供应商列表（可重复）
- `min_height`: 最小高度/长度
- `max_height`: 最大高度/长度
- `min_price`: 最低价格
- `max_price`: 最高价格
- `category`: 主分类
- `subcategories`: 子分类列表（可重复）
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认10，最大100）

**响应示例**:
```json
{
  "products": [
    {
      "Code": "CHR001",
      "SKU": "RED-ROSE-001",
      "Description": "Red Artificial Rose",
      "ListPrice": 15.99,
      "HL": "30",
      "Qty": 100,
      "Stock": 85,
      "Sold": 15,
      "StockStatus": "In Stock",
      "nCategory": "Artificial Flowers",
      "nSubCategory": "Rose",
      "Comment": "High quality red rose",
      "SU": "Supplier1"
    }
  ],
  "total_count": 1,
  "page": 1,
  "per_page": 10,
  "total_pages": 1
}
```

#### 6. 搜索产品 (POST)
```http
POST /api/products/search
Content-Type: application/json

{
  "q": "rose +red",
  "suppliers": ["Supplier1"],
  "min_price": 10,
  "max_price": 100,
  "category": "Artificial Flowers",
  "subcategories": ["Rose"],
  "page": 1,
  "per_page": 10
}
```

#### 7. 搜索建议
```http
GET /api/products/suggestions?q=ro
```
**响应示例**:
```json
{
  "suggestions": ["Rose", "Royal", "Romantic"]
}
```

## 技术架构

### 前端技术栈
- **Streamlit**: Web应用框架
- **HTML/CSS/JavaScript**: 界面增强和交互
- **Pandas**: 数据处理

### 后端技术栈
- **Flask**: Web框架
- **SQLite**: 数据库
- **Python**: 核心逻辑

### 数据库结构
系统使用现有的`products`表，主要字段：
- `Code`: 供应商产品代码
- `SKU`: 产品SKU
- `Description`: 产品描述
- `ListPrice`: 标价
- `HL`: 高度/长度
- `Qty`: 数量
- `Stock`: 库存
- `Sold`: 已售数量
- `StockStatus`: 库存状态
- `nCategory`: 主分类
- `nSubCategory`: 子分类
- `Comment`: 备注
- `SU`: 供应商

## 性能优化

### 数据库索引建议
```sql
-- 为搜索字段创建索引
CREATE INDEX idx_products_sku ON products(SKU);
CREATE INDEX idx_products_code ON products(Code);
CREATE INDEX idx_products_description ON products(Description);
CREATE INDEX idx_products_ncategory ON products(nCategory);
CREATE INDEX idx_products_nsubcategory ON products(nSubCategory);
CREATE INDEX idx_products_su ON products(SU);
CREATE INDEX idx_products_listprice ON products(ListPrice);
```

### 搜索优化
- 使用数据库索引提高查询速度
- 分页显示减少内存使用
- 智能缓存常用查询结果

## 故障排除

### 常见问题

#### 1. 数据库连接失败
- 检查数据库文件路径是否正确
- 确认数据库文件存在且可访问

#### 2. 搜索结果为空
- 检查搜索条件是否过于严格
- 尝试使用更宽泛的关键词
- 确认数据库中存在相关数据

#### 3. API服务无法启动
- 检查端口5000是否被占用
- 确认已安装所需依赖包

### 日志查看
- Streamlit应用: 查看终端输出
- API服务: 查看控制台日志，级别设为INFO

## 扩展功能建议

### 短期改进
1. **搜索历史**: 记录用户搜索历史
2. **收藏功能**: 允许收藏常用搜索条件
3. **导出功能**: 支持将搜索结果导出为CSV/Excel
4. **高级筛选**: 增加更多筛选条件

### 长期规划
1. **全文搜索**: 使用Elasticsearch等搜索引擎
2. **智能推荐**: 基于用户行为的智能推荐
3. **数据分析**: 搜索数据分析和可视化
4. **移动端适配**: 响应式设计和移动端优化

---

**文档版本**: 1.0
**创建日期**: 2025-11-21
**最后更新**: 2025-11-21
**维护者**: 系统管理员