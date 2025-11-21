# 产品检索系统

一个功能强大的库存产品检索系统，支持多条件筛选和复杂搜索语法。

## ✨ 功能特点

- 🔍 **智能搜索**: 支持SKU、产品代码、描述的模糊匹配
- 🔧 **高级语法**: 支持 `+` (AND)、`-` (NOT)、`or` 操作符
- 🏷️ **多维度筛选**: 供应商、价格、高度、类别等多条件组合
- 📊 **分页显示**: 每页10条记录，支持快速翻页
- ⌨️ **快捷键**: Ctrl+Enter 执行搜索，ESC 清空输入
- 🌐 **API支持**: 提供RESTful API接口

## 🚀 快速开始

### 方法1: 使用启动脚本（推荐）

**Windows用户**:
双击运行 `启动检索系统.bat`

**命令行**:
```bash
python start_search_system.py
```

### 方法2: 直接启动

**Streamlit界面**:
```bash
cd src
streamlit run product_search_enhanced.py
```

**API服务器**:
```bash
cd src/api
python search_api.py
```

## 📦 依赖要求

- Python 3.7+
- 自动安装所需包: streamlit, flask, pandas, requests

## 📁 项目结构

```
ims/
├── src/
│   ├── product_search_enhanced.py    # Streamlit主应用
│   └── api/
│       └── search_api.py             # API服务器
├── data/
│   └── inventory.db                  # 产品数据库
├── docs/
│   └── product_search_guide.md       # 详细说明文档
├── 启动检索系统.bat                   # Windows启动脚本
├── start_search_system.py            # Python启动脚本
└── install_deps_simple.py            # 依赖安装脚本
```

## 🔍 搜索语法

### 基本搜索
- `rose` - 搜索包含"rose"的产品
- `ABC123` - 搜索包含"ABC123"的产品

### 高级语法
- `rose +red` - 同时包含"rose"和"red"
- `flower -white` - 包含"flower"但不包含"white"
- `red or blue` - 包含"red"或"blue"

## 🌐 访问地址

- **Streamlit界面**: http://localhost:8501
- **API服务**: http://localhost:5000
- **API文档**: http://localhost:5000/api/health

## 📖 详细文档

查看 `docs/product_search_guide.md` 获取完整的使用说明和API文档。

## ⚠️ 故障排除

### 依赖包安装问题
如果遇到包安装失败，请运行：
```bash
python install_deps_simple.py
```

### 字符编码问题
如果批处理文件显示乱码，请使用PowerShell运行：
```powershell
python start_search_system.py
```

### 数据库问题
确保 `data/inventory.db` 文件存在且包含产品数据。

## 📞 技术支持

如需帮助，请检查：
1. Python版本是否 >= 3.7
2. 所有依赖包是否正确安装
3. 数据库文件是否存在
4. 防火墙是否阻止端口访问

---

**版本**: 1.0
**更新**: 2025-11-21