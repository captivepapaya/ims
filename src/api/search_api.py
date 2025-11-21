"""
产品检索API接口
提供RESTful API来支持产品检索功能
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 数据库路径
DB_PATH = Path("../data/inventory.db")

class ProductSearchAPI:
    """产品检索API类"""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def connect(self):
        """连接数据库"""
        return sqlite3.connect(self.db_path)

    def get_suppliers(self) -> List[str]:
        """获取所有供应商列表"""
        conn = self.connect()
        query = "SELECT DISTINCT SU FROM products WHERE SU IS NOT NULL AND SU != '' ORDER BY SU"
        cursor = conn.cursor()
        cursor.execute(query)
        suppliers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ["ALL"] + suppliers

    def get_categories(self) -> List[str]:
        """获取所有主分类列表"""
        conn = self.connect()
        query = "SELECT DISTINCT nCategory FROM products WHERE nCategory IS NOT NULL AND nCategory != '' ORDER BY nCategory"
        cursor = conn.cursor()
        cursor.execute(query)
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    def get_subcategories(self, category: str) -> List[str]:
        """根据主分类获取子分类列表"""
        conn = self.connect()
        query = """
        SELECT DISTINCT nSubCategory FROM products
        WHERE nCategory = ? AND nSubCategory IS NOT NULL AND nSubCategory != ''
        ORDER BY nSubCategory
        """
        cursor = conn.cursor()
        cursor.execute(query, (category,))
        subcategories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return subcategories

    def normalize_text(self, text: str) -> str:
        """标准化文本：移除标点符号、空格，转为小写"""
        if not text or pd.isna(text):
            return ""
        # 移除所有非字母数字字符，转为小写
        return re.sub(r'[^\w]', '', str(text).lower())

    def parse_search_query(self, query: str) -> Dict:
        """解析搜索查询字符串"""
        if not query or not query.strip():
            return {"type": "simple", "terms": []}

        query = query.strip()

        # 检查 OR 操作符
        if re.search(r'\bor\b', query, flags=re.IGNORECASE):
            parts = re.split(r'\s+or\s+', query, flags=re.IGNORECASE)
            return {
                "type": "or",
                "terms": [part.strip() for part in parts if part.strip()]
            }

        # 检查 AND 操作符 (+)
        if '+' in query:
            parts = query.split('+')
            return {
                "type": "and",
                "terms": [part.strip() for part in parts if part.strip()]
            }

        # 检查 NOT 操作符 (-)
        if '-' in query:
            parts = query.split('-', 1)  # 只分割第一个-
            include = parts[0].strip()
            exclude = parts[1].strip() if len(parts) > 1 else ""
            return {
                "type": "not",
                "include": include,
                "exclude": exclude
            }

        # 简单搜索
        return {
            "type": "simple",
            "terms": [query]
        }

    def matches_search_terms(self, product_data: Dict, search_info: Dict) -> bool:
        """检查产品是否匹配搜索条件"""
        # 要搜索的文本字段
        searchable_fields = [
            product_data.get('SKU', ''),
            product_data.get('Code', ''),
            product_data.get('Description', ''),
            product_data.get('nSubCategory', '')
        ]

        # 将所有搜索文本合并为一个字符串
        combined_text = ' '.join(searchable_fields)
        normalized_text = self.normalize_text(combined_text)

        search_type = search_info["type"]

        if search_type == "simple":
            # 简单搜索：任何匹配即可
            for term in search_info["terms"]:
                normalized_term = self.normalize_text(term)
                if normalized_term and normalized_term in normalized_text:
                    return True
            return len(search_info["terms"]) == 0

        elif search_type == "or":
            # OR搜索：任何条件匹配即可
            for term in search_info["terms"]:
                normalized_term = self.normalize_text(term)
                if normalized_term and normalized_term in normalized_text:
                    return True
            return False

        elif search_type == "and":
            # AND搜索：所有条件都必须匹配
            for term in search_info["terms"]:
                normalized_term = self.normalize_text(term)
                if not normalized_term or normalized_term not in normalized_text:
                    return False
            return True

        elif search_type == "not":
            # NOT搜索：包含include但不包含exclude
            include_term = self.normalize_text(search_info["include"])
            exclude_term = self.normalize_text(search_info["exclude"])

            if include_term and include_term in normalized_text:
                if exclude_term and exclude_term in normalized_text:
                    return False
                return True
            return False

        return False

    def search_products(self, search_query: str = "", suppliers: List[str] = None,
                       min_height: float = None, max_height: float = None,
                       min_price: float = None, max_price: float = None,
                       category: str = None, subcategories: List[str] = None,
                       page: int = 1, per_page: int = 10) -> Dict:
        """搜索产品"""

        conn = self.connect()

        try:
            # 构建基础查询
            base_query = """
            SELECT Code, SKU, Description, ListPrice, HL, Qty, Stock, Sold, StockStatus,
                   nCategory, nSubCategory, Comment, SU
            FROM products
            WHERE 1=1
            """

            params = []

            # 供应商筛选
            if suppliers and "ALL" not in suppliers and len(suppliers) > 0:
                placeholders = ','.join(['?' for _ in suppliers])
                base_query += f" AND SU IN ({placeholders})"
                params.extend(suppliers)

            # 高度/长度筛选
            if min_height is not None:
                base_query += " AND CAST(COALESCE(NULLIF(HL, ''), '0') AS REAL) >= ?"
                params.append(min_height)

            if max_height is not None:
                base_query += " AND CAST(COALESCE(NULLIF(HL, ''), '999999') AS REAL) <= ?"
                params.append(max_height)

            # 价格筛选
            if min_price is not None:
                base_query += " AND COALESCE(ListPrice, 0) >= ?"
                params.append(min_price)

            if max_price is not None:
                base_query += " AND COALESCE(ListPrice, 999999) <= ?"
                params.append(max_price)

            # 类别筛选
            if category:
                base_query += " AND nCategory = ?"
                params.append(category)

                if subcategories and len(subcategories) > 0:
                    placeholders = ','.join(['?' for _ in subcategories])
                    base_query += f" AND nSubCategory IN ({placeholders})"
                    params.extend(subcategories)

            # 执行查询获取所有匹配的记录
            df = pd.read_sql_query(base_query, conn, params=params)

            # 应用关键词搜索筛选
            if search_query and search_query.strip():
                search_info = self.parse_search_query(search_query)

                def search_filter(row):
                    product_data = row.to_dict()
                    return self.matches_search_terms(product_data, search_info)

                df = df[df.apply(search_filter, axis=1)]

            # 计算总记录数
            total_count = len(df)

            # 分页
            if per_page > 0:
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                df_page = df.iloc[start_idx:end_idx]
            else:
                df_page = df

            # 转换为字典列表
            products = df_page.to_dict('records')

            return {
                "products": products,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 1
            }

        except Exception as e:
            logger.error(f"搜索产品时出错: {e}")
            return {
                "products": [],
                "total_count": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0,
                "error": str(e)
            }
        finally:
            conn.close()

# 创建API实例
search_api = ProductSearchAPI(DB_PATH)

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "healthy", "message": "Product Search API is running"})

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """获取供应商列表"""
    try:
        suppliers = search_api.get_suppliers()
        return jsonify({"suppliers": suppliers})
    except Exception as e:
        logger.error(f"获取供应商列表时出错: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取主分类列表"""
    try:
        categories = search_api.get_categories()
        return jsonify({"categories": categories})
    except Exception as e:
        logger.error(f"获取分类列表时出错: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/subcategories', methods=['GET'])
def get_subcategories():
    """获取子分类列表"""
    category = request.args.get('category')
    if not category:
        return jsonify({"error": "Category parameter is required"}), 400

    try:
        subcategories = search_api.get_subcategories(category)
        return jsonify({"subcategories": subcategories})
    except Exception as e:
        logger.error(f"获取子分类列表时出错: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/search', methods=['GET'])
def search_products():
    """搜索产品接口"""
    try:
        # 获取查询参数
        search_query = request.args.get('q', '')
        suppliers = request.args.getlist('suppliers')
        min_height = request.args.get('min_height', type=float)
        max_height = request.args.get('max_height', type=float)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        category = request.args.get('category')
        subcategories = request.args.getlist('subcategories')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 验证分页参数
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10

        # 执行搜索
        result = search_api.search_products(
            search_query=search_query,
            suppliers=suppliers,
            min_height=min_height,
            max_height=max_height,
            min_price=min_price,
            max_price=max_price,
            category=category,
            subcategories=subcategories,
            page=page,
            per_page=per_page
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"搜索产品时出错: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/search', methods=['POST'])
def search_products_post():
    """搜索产品接口 (POST方式，支持复杂查询)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # 获取JSON参数
        search_query = data.get('q', '')
        suppliers = data.get('suppliers', [])
        min_height = data.get('min_height')
        max_height = data.get('max_height')
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        category = data.get('category')
        subcategories = data.get('subcategories', [])
        page = data.get('page', 1)
        per_page = data.get('per_page', 10)

        # 验证分页参数
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10

        # 执行搜索
        result = search_api.search_products(
            search_query=search_query,
            suppliers=suppliers,
            min_height=min_height,
            max_height=max_height,
            min_price=min_price,
            max_price=max_price,
            category=category,
            subcategories=subcategories,
            page=page,
            per_page=per_page
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"搜索产品时出错: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/suggestions', methods=['GET'])
def get_search_suggestions():
    """获取搜索建议"""
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify({"suggestions": []})

        conn = search_api.connect()

        # 获取SKU建议
        sku_query = """
        SELECT DISTINCT SKU FROM products
        WHERE SKU IS NOT NULL AND SKU != '' AND SKU LIKE ?
        LIMIT 5
        """

        # 获取Description建议
        desc_query = """
        SELECT DISTINCT Description FROM products
        WHERE Description IS NOT NULL AND Description != '' AND Description LIKE ?
        LIMIT 5
        """

        # 获取子分类建议
        subcat_query = """
        SELECT DISTINCT nSubCategory FROM products
        WHERE nSubCategory IS NOT NULL AND nSubCategory != '' AND nSubCategory LIKE ?
        LIMIT 5
        """

        like_pattern = f'%{query}%'

        suggestions = []

        # 获取建议
        for q in [sku_query, desc_query, subcat_query]:
            cursor = conn.cursor()
            cursor.execute(q, (like_pattern,))
            results = [row[0] for row in cursor.fetchall()]
            suggestions.extend(results)

        # 去重并限制数量
        unique_suggestions = list(set(suggestions))[:10]

        conn.close()

        return jsonify({"suggestions": unique_suggestions})

    except Exception as e:
        logger.error(f"获取搜索建议时出错: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    if not DB_PATH.exists():
        logger.error(f"数据库文件不存在: {DB_PATH}")
        print(f"错误: 数据库文件不存在: {DB_PATH}")
    else:
        logger.info("启动产品检索API服务...")
        app.run(host='0.0.0.0', port=5000, debug=True)