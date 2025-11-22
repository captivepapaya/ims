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
    /* 调整缩放和布局 */
    body {
        zoom: 0.95;
    }

    /* 增大整体字体大小 */
    .stMarkdown, .stText {
        font-size: 18px !important;
        line-height: 1.5 !important;
    }

    .stSubheader {
        font-size: 20px !important;
        font-weight: 600 !important;
    }

    .stHeader {
        font-size: 24px !important;
        font-weight: 700 !important;
    }

    /* 增大输入框字体 */
    input, select, textarea {
        font-size: 16px !important;
    }

    /* 调整主容器高度，撑满显示屏 */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        min-height: 95vh !important;
    }

    /* 限制使用帮助框在左栏内 */
    div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:first-child .stExpander {
        max-width: 100% !important;
    }

    .search-container {
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
        width: 100%;
        box-sizing: border-box;
    }

    /* 限制使用帮助在左栏范围内 */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:first-child {
        width: 100% !important;
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
            event.preventDefault();

            // 清空搜索输入框
            const searchInput = document.querySelector('input[placeholder="例如: rose +red, flower -white, big or large"]');
            if (searchInput) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
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
        SELECT DISTINCT nSubCategory
        FROM products
        WHERE nCategory = ? AND nSubCategory IS NOT NULL AND nSubCategory != ''
        ORDER BY nSubCategory
        """
        cursor = conn.cursor()
        cursor.execute(query, (category,))
        return [row[0] for row in cursor.fetchall()]

    def parse_search_query(self, query: str) -> Tuple[str, List[str], List[str]]:
        """解析搜索查询语句"""
        query = query.lower().strip()

        # 提取包含的词汇（+ 开头的词）
        include_words = re.findall(r'\+([^\s+]+)', query)

        # 提排除的词汇（- 开头的词）
        exclude_words = re.findall(r'-([^\s+]+)', query)

        # 移除操作符，得到纯文本查询
        clean_query = re.sub(r'[+-]', '', query).strip()

        return clean_query, include_words, exclude_words

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
            base_query += " AND CAST(COALESCE(NULLIF(HL, ''), '0') AS REAL) <= ?"
            params.append(max_height)

        # 价格筛选
        if min_price is not None:
            base_query += " AND CAST(COALESCE(NULLIF(Price, ''), '0') AS REAL) >= ?"
            params.append(min_price)

        if max_price is not None:
            base_query += " AND CAST(COALESCE(NULLIF(Price, ''), '0') AS REAL) <= ?"
            params.append(max_price)

        # 分类筛选
        if category:
            base_query += " AND nCategory = ?"
            params.append(category)

        # 子分类筛选
        if subcategories:
            placeholders = ','.join(['?' for _ in subcategories])
            base_query += f" AND nSubCategory IN ({placeholders})"
            params.extend(subcategories)

        # 文本搜索
        if search_query:
            clean_query, include_words, exclude_words = self.parse_search_query(search_query)

            # 构建搜索条件
            search_conditions = []

            if clean_query:
                search_conditions.append("(LOWER(Description) LIKE ? OR LOWER(SKU) LIKE ? OR LOWER(Code) LIKE ?)")
                search_term = f"%{clean_query}%"
                params.extend([search_term, search_term, search_term])

            # 包含词汇
            for word in include_words:
                search_conditions.append("LOWER(Description) LIKE ?")
                params.append(f"%{word}%")

            # 排除词汇
            for word in exclude_words:
                search_conditions.append("(LOWER(Description) NOT LIKE ? AND LOWER(SKU) NOT LIKE ? AND LOWER(Code) NOT LIKE ?)")
                exclude_term = f"%{word}%"
                params.extend([exclude_term, exclude_term, exclude_term])

            if search_conditions:
                base_query += " AND " + " AND ".join(search_conditions)

        # 计算总数
        count_query = f"SELECT COUNT(*) FROM ({base_query})"
        cursor = conn.cursor()
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # 添加排序和分页
        base_query += " ORDER BY Code LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])

        # 执行查询
        df = pd.read_sql_query(base_query, conn, params=params)
        conn.close()

        return df, total_count

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

        # 使用帮助
        with st.expander("📖 使用帮助", expanded=False):
            st.markdown("""
            ### 搜索语法：
            - **基本搜索**：如 `rose`
            - **包含搜索**：如 `+red`（必须包含red）
            - **排除搜索**：如 `-white`（不包含white）
            - **组合搜索**：如 `rose +red -white`
            - **或搜索**：如 `red or pink`

            ### 筛选条件：
            - **供应商**：选择特定供应商或"ALL"
            - **高度/长度**：设置数值范围
            - **价格**：设置价格范围
            - **分类**：选择主分类和子分类

            ### 快捷键：
            - **Ctrl + Enter**：执行搜索
            - **ESC**：清空搜索框
            """)

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

        # 5. 分类筛选
        st.subheader("5. 分类筛选")
        categories = search_engine.get_categories()
        selected_category = st.selectbox(
            "选择主分类",
            ["全部"] + categories,
            key="category_select"
        )

        # 6. 子分类筛选（动态加载）
        if selected_category != "全部":
            subcategories = search_engine.get_subcategories(selected_category)
            if subcategories:
                selected_subcategories = st.multiselect(
                    "选择子分类（可选）",
                    subcategories,
                    key="subcategory_select"
                )
            else:
                st.info("该分类下暂无子分类")
                selected_subcategories = []
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
                        if total_pages > 0:
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
            # 不显示任何内容
            pass

if __name__ == "__main__":
    main()