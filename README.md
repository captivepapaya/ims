# 库存管理系统

基于 Python 的库存管理系统，支持从 CSV 文件导入数据并转换为 SQLite 数据库，提供 Web 界面进行库存管理。

## 功能特性

- 支持 Retool 和 Google Sheets CSV 文件导入
- CSV 文件转换为 SQLite 数据库
- Web 界面进行库存管理
- 数据持久化存储

## 项目结构

```
inventory-management/
├── data/
│   ├── raw/          # 存放 Retool 和 Gsheet 的 CSV 文件
│   └── db/           # SQLite 数据库文件
├── src/              # 源代码
├── requirements.txt  # 项目依赖
└── README.md        # 项目说明
```

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
streamlit run src/app.py
```

## 数据导入

1. 将 CSV 文件放置在 `data/raw/` 目录下
2. 运行数据转换脚本导入到数据库
3. 通过 Web 界面管理库存数据