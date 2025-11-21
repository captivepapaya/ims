import streamlit as st
import pandas as pd
import sqlite3
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 设置页面配置
st.set_page_config(
    page_title="产品检索系统",
    page_icon="🔍",
    layout="wide"
)

# 自定义CSS和JavaScript
def inject_custom_code():
    """注入自定义CSS和JavaScript"""
    st.markdown("""
    <style>
    .search-container {
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
    }

    .search-input {
        font-size: 16px;
        padding: 10px;
        border: 2px solid #ccc;
        border-radius: 5px;
    }

    .search-input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
    }

    .metric-container {
        background-color: #e8f5e8;
        border-left: 4px solid #4CAF50;
        padding: 10px;
        margin: 5px 0;
    }

    .help-text {
        font-size: 12px;
        color: #666;
        font-style: italic;
    }

    .result-table {
        font-size: 14px;
    }

    .page-navigation {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin: 20px 0;
    }
    </style>

    <script>
    // 键盘快捷键支持
    document.addEventListener('keydown', function(event) {
        // Ctrl+Enter 执行搜索
        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault();

            // 触发搜索按钮点击
            const searchButton = document.querySelector('button[kind="primary"]');
            if (searchButton) {
                searchButton.click();
            }
        }

        // ESC 清空搜索
        if (event.key === 'Escape') {
            const searchInput = document.querySelector('input[placeholder*="输入搜索关键词"]');
            if (searchInput) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    });

    // 页面加载完成后提示键盘快捷键
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            console.log('💡 快捷键: Ctrl+Enter 执行搜索, ESC 清空搜索');
        }, 1000);
    });
    </script>
    """, unsafe_allow_html=True)

# 数据库路径
DB_PATH = Path("../data/inventory.db")

class ProductSearchEngine:
    """产品搜索引擎类"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """连接数据库"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def get_suppliers(self) -> List[str]:
        """获取所有供应商列表"""
        conn = self.connect()
        query = "SELECT DISTINCT SU FROM products WHERE SU IS NOT NULL AND SU != '' ORDER BY SU"
        cursor = conn.cursor()
        cursor.execute(query)
        suppliers = [row[0] for row in cursor.fetchall()]
        return ["ALL"] + suppliers

    def get_categories(self) -> List[str]:
        """获取所有主分类列表"""
        conn = self.connect()
        query = "SELECT DISTINCT nCategory FROM products WHERE nCategory IS NOT NULL AND nCategory != '' ORDER BY nCategory"
        cursor = conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

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
        return [row[0] for row in cursor.fetchall()]

    def normalize_text(self, text: str) -> str:
        """标准化文本：移除标点符号、空格，转为小写"""
        if pd.isna(text) or text is None:
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
            return len(search_info["terms"]) == 0  # 如果没有搜索条件，返回True

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
                       page: int = 1, per_page: int = 10) -> Tuple[pd.DataFrame, int]:
        """搜索产品"""

        conn = self.connect()

        # 构建基础查询
        base_query = """
        SELECT Code, SKU, Description, Price, HL, Qty, Stock, Sold, StockStatus,
               nCategory, nSubCategory, Comment, SU
        FROM products
        WHERE 1=1
        """

        params = []

        # 供应商筛选
        if suppliers and "ALL" not in suppliers:
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
            base_query += " AND COALESCE(Price, 0) >= ?"
            params.append(min_price)

        if max_price is not None:
            base_query += " AND COALESCE(Price, 999999) <= ?"
            params.append(max_price)

        # 类别筛选
        if category:
            base_query += " AND nCategory = ?"
            params.append(category)

            if subcategories:
                placeholders = ','.join(['?' for _ in subcategories])
                base_query += f" AND nSubCategory IN ({placeholders})"
                params.extend(subcategories)

        # 执行查询获取所有匹配的记录
        try:
            df = pd.read_sql_query(base_query, conn, params=params)
        except Exception as e:
            st.error(f"查询数据库时出错: {e}")
            return pd.DataFrame(), 0

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
            df = df.iloc[start_idx:end_idx]

        return df, total_count

def display_search_help():
    """显示搜索帮助信息"""
    with st.expander("📖 搜索语法帮助", expanded=False):
        st.markdown("""
        ### 搜索操作符说明：

        **简单搜索**:
        - 直接输入关键词，如: `rose`, `red`, `flower`
        - 在SKU、Code、Description、SubCategory中查找匹配项

        **AND操作符 (+)**:
        - `red +rose` - 同时包含red和rose的结果
        - 所有加号前后的条件都必须匹配

        **OR操作符 (or)**:
        - `red or blue` - 包含red或blue的结果
        - 任意一个条件匹配即可

        **NOT操作符 (-)**:
        - `rose -white` - 包含rose但不包含white的结果
        - 排除特定关键词

        **注意事项**:
        - 搜索不区分大小写
        - 忽略所有标点符号和空格
        - 可以组合使用多个操作符
        """)

def main():
    """主函数"""
    # 注入自定义代码
    inject_custom_code()

    st.title("🔍 产品检索系统")
    st.markdown("---")

    
    # 初始化搜索引擎
    if not DB_PATH.exists():
        st.error(f"数据库文件不存在: {DB_PATH}")
        st.info("请确保数据库文件存在并尝试刷新页面")
        return

    search_engine = ProductSearchEngine(DB_PATH)

    # 主要内容区域 - 使用两列布局
    col_search, col_results = st.columns([2, 5])

    with col_search:
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        st.header("🔍 搜索条件")

        # 1. 关键词搜索框
        st.subheader("1. 关键词搜索")
        search_query = st.text_input(
            "输入搜索关键词",
            placeholder="例如: rose +red, flower -white, big or large",
            help="支持 + (AND), - (NOT), or (OR) 操作符",
            key="main_search_input"
        )

        # 2. 供应商选择
        st.subheader("2. 供应商筛选")
        suppliers = search_engine.get_suppliers()
        selected_suppliers = st.multiselect(
            "选择供应商",
            suppliers,
            default=["ALL"],
            key="supplier_select"
        )

        # 3. 高度/长度筛选
        st.subheader("3. 高度/长度筛选")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            min_height = st.number_input("最小值", value=0.0, placeholder="最小", key="min_height", format="%.2f")
        with col_h2:
            max_height = st.number_input("最大值", value=0.0, placeholder="最大", key="max_height", format="%.2f")

        # 4. 价格筛选
        st.subheader("4. 价格筛选")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            min_price = st.number_input("最低价", value=0.0, placeholder="最低", key="min_price", format="%.2f")
        with col_p2:
            max_price = st.number_input("最高价", value=0.0, placeholder="最高", key="max_price", format="%.2f")

        # 5. 类别筛选
        st.subheader("5. 类别筛选")
        categories = search_engine.get_categories()
        if categories:
            selected_category = st.selectbox(
                "选择主分类",
                ["全部"] + categories,
                key="category_select"
            )

            subcategories = []
            if selected_category != "全部":
                available_subcategories = search_engine.get_subcategories(selected_category)
                if available_subcategories:
                    subcategories = st.multiselect(
                        "选择子分类 (最多5个)",
                        available_subcategories,
                        max_selections=5,
                        key="subcategory_select"
                    )
        else:
            selected_category = "全部"
            subcategories = []

        # 搜索按钮
        st.markdown("---")
        search_button = st.button("🔍 执行搜索", type="primary", key="execute_search", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_results:
        # 初始化session状态
        if 'search_page' not in st.session_state:
            st.session_state.search_page = 1
        if 'last_search_params' not in st.session_state:
            st.session_state.last_search_params = {}
        if 'should_search' not in st.session_state:
            st.session_state.should_search = False

        # 检查是否需要执行搜索
        execute_search = search_button

        if execute_search:
            # 重置页码并标记需要搜索
            st.session_state.search_page = 1
            st.session_state.should_search = True
            # 保存搜索参数
            st.session_state.last_search_params = {
                'search_query': search_query,
                'selected_suppliers': selected_suppliers if "ALL" not in selected_suppliers else None,
                'min_height': min_height if min_height > 0 else None,
                'max_height': max_height if max_height > 0 else None,
                'min_price': min_price if min_price > 0 else None,
                'max_price': max_price if max_price > 0 else None,
                'selected_category': selected_category if selected_category != "全部" else None,
                'subcategories': subcategories if subcategories else None
            }

        # 执行搜索（如果是搜索按钮点击或页面切换）
        if st.session_state.should_search or st.session_state.get('last_search_params'):
            with st.spinner("正在搜索..."):
                params = st.session_state.get('last_search_params', {})
                df, total_count = search_engine.search_products(
                    search_query=params.get('search_query', ''),
                    suppliers=params.get('selected_suppliers'),
                    min_height=params.get('min_height'),
                    max_height=params.get('max_height'),
                    min_price=params.get('min_price'),
                    max_price=params.get('max_price'),
                    category=params.get('selected_category'),
                    subcategories=params.get('subcategories'),
                    page=st.session_state.search_page,
                    per_page=10
                )
            st.session_state.should_search = False

            # 显示搜索结果
            st.header("📊 搜索结果")

            # 结果统计
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总记录数", total_count)
            with col2:
                current_start = (st.session_state.search_page - 1) * 10 + 1
                current_end = min(st.session_state.search_page * 10, total_count)
                st.metric("当前显示", f"{current_start}-{current_end}" if total_count > 0 else "0-0")
            with col3:
                total_pages = (total_count + 9) // 10 if total_count > 0 else 0
                st.metric("总页数", total_pages)

            # 显示数据表格
            if not df.empty:
                # 重命名列以便更好显示
                display_columns = {
                    'Code': '供应商代码',
                    'SKU': 'SKU',
                    'Description': '产品描述',
                    'Price': '标价',
                    'HL': '高度/长度',
                    'Qty': '数量',
                    'Stock': '库存',
                    'Sold': '已售',
                    'StockStatus': '库存状态',
                    'nCategory': '主分类',
                    'nSubCategory': '子分类',
                    'Comment': '备注'
                }

                df_display = df.rename(columns=display_columns)

                # 格式化价格列
                if '标价' in df_display.columns:
                    df_display['标价'] = df_display['标价'].apply(lambda x: f"${x:.2f}" if pd.notna(x) and x > 0 else "")

                # 格式化数值列
                if '高度/长度' in df_display.columns:
                    df_display['高度/长度'] = df_display['高度/长度'].apply(lambda x: f"{x}" if pd.notna(x) and x != "" else "")

                st.dataframe(df_display, use_container_width=True, height=400)

                # 分页控制
                if total_count > 10:
                    st.markdown("---")
                    st.subheader("📄 分页导航")

                    col_prev, col_page, col_next = st.columns([1, 2, 1])

                    with col_prev:
                        if st.button("⬅️ 上一页", disabled=st.session_state.search_page <= 1, key="prev_page"):
                            st.session_state.search_page -= 1
                            st.session_state.should_search = True
                            st.experimental_rerun()

                    with col_page:
                        # 页码输入
                        page_input = st.number_input(
                            "页码",
                            min_value=1,
                            max_value=total_pages,
                            value=st.session_state.search_page,
                            key="page_input"
                        )
                        if page_input != st.session_state.search_page:
                            st.session_state.search_page = page_input
                            st.session_state.should_search = True
                            st.experimental_rerun()

                    with col_next:
                        if st.button("下一页 ➡️", disabled=st.session_state.search_page >= total_pages, key="next_page"):
                            st.session_state.search_page += 1
                            st.session_state.should_search = True
                            st.experimental_rerun()

            else:
                st.info("🔍 未找到匹配的产品，请尝试调整搜索条件")

        else:
            # 显示搜索提示
            st.info("👈 请在左侧设置搜索条件，然后点击执行搜索按钮")

if __name__ == "__main__":
    main()