import streamlit as st
import pandas as pd
import os
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="库存管理系统",
    page_icon="📦",
    layout="wide"
)

# 应用标题
st.title("📦 库存管理系统")
st.markdown("---")

# 定义数据路径
DATA_RAW_PATH = Path("../data/raw")
DATA_DB_PATH = Path("../data/db")

def load_csv_files():
    """加载 data/raw 目录下的所有 CSV 文件"""
    csv_files = []
    if DATA_RAW_PATH.exists():
        for file in DATA_RAW_PATH.glob("*.csv"):
            csv_files.append(file.name)
    return csv_files

def read_csv_file(filename):
    """读取指定的 CSV 文件"""
    try:
        file_path = DATA_RAW_PATH / filename
        df = pd.read_csv(file_path, encoding='utf-8')
        return df, None
    except Exception as e:
        return None, str(e)

# 侧边栏 - 文件选择
st.sidebar.header("📁 文件选择")

# 检查目录是否存在
if not DATA_RAW_PATH.exists():
    st.sidebar.error(f"目录不存在: {DATA_RAW_PATH}")
    st.sidebar.info("请将 CSV 文件放置在 data/raw/ 目录下")
else:
    # 获取 CSV 文件列表
    csv_files = load_csv_files()

    if not csv_files:
        st.sidebar.warning("未找到 CSV 文件")
        st.sidebar.info(f"请将 CSV 文件放置在: {DATA_RAW_PATH}")
    else:
        selected_file = st.sidebar.selectbox("选择 CSV 文件", csv_files)

        # 读取并显示选中的文件
        if selected_file:
            st.sidebar.success(f"已选择: {selected_file}")

            # 读取文件
            df, error = read_csv_file(selected_file)

            if error:
                st.error(f"读取文件失败: {error}")
            else:
                # 显示文件信息
                st.header(f"📊 {selected_file}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("行数", len(df))
                with col2:
                    st.metric("列数", len(df.columns))
                with col3:
                    st.metric("文件大小", f"{os.path.getsize(DATA_RAW_PATH / selected_file)} bytes")

                # 显示数据预览
                st.subheader("数据预览")

                # 显示列信息
                st.subheader("📋 列信息")
                col_info = pd.DataFrame({
                    '列名': df.columns,
                    '数据类型': df.dtypes.astype(str),
                    '非空值数量': df.count(),
                    '空值数量': df.isnull().sum()
                })
                st.dataframe(col_info, use_container_width=True)

                # 显示数据内容
                st.subheader("📄 数据内容")

                # 添加显示行数选择
                show_rows = st.selectbox("显示行数", [10, 50, 100, "全部"], key="show_rows")

                if show_rows == "全部":
                    st.dataframe(df, use_container_width=True)
                else:
                    st.dataframe(df.head(show_rows), use_container_width=True)

                # 下载功能
                st.subheader("⬇️ 下载处理后的数据")
                csv = df.to_csv(index=False)
                st.download_button(
                    label="下载 CSV 文件",
                    data=csv,
                    file_name=f"processed_{selected_file}",
                    mime="text/csv"
                )

# 文件上传功能
st.sidebar.header("📤 上传新文件")
uploaded_file = st.sidebar.file_uploader(
    "上传 CSV 文件",
    type=['csv'],
    help="上传新的 CSV 文件到 data/raw 目录"
)

if uploaded_file is not None:
    try:
        # 确保目录存在
        DATA_RAW_PATH.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = DATA_RAW_PATH / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.sidebar.success(f"文件已保存: {uploaded_file.name}")
        st.experimental_rerun()

    except Exception as e:
        st.sidebar.error(f"保存文件失败: {e}")

# 底部信息
st.markdown("---")
st.markdown("💡 提示: 将 CSV 文件放置在 `data/raw/` 目录下，或使用侧边栏上传功能")