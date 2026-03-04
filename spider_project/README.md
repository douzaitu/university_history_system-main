# 爬虫项目说明
本项目用于爬取 [成都理工大学计算机与网络安全学院师资页面](http://cist.cdut.edu.cn/szdw/bssds.htm) 的相关信息。

## 项目结构
spider_project/
├── src/ # 核心代码
│ ├── crawlers/ # 爬虫脚本
│ ├── utils/ # 工具函数（请求、解析、日志等）
│ ├── config/ # 配置文件（URL、参数等）
│ └── main.py # 程序入口（启动爬虫）
├── data/ # 数据存储（原始 / 清洗后的数据）
├── logs/ # 日志文件
├── requirements.txt # 依赖清单
└── README.md # 项目说明

## 环境准备
1. 安装Python 3.10+
2. 安装依赖：`pip install -r requirements.txt`

## 运行方式
1. 打开PyCharm，设置项目Python解释器（使用项目虚拟环境）
2. 运行 `src/main.py` 文件，启动爬虫

## 数据说明
- 爬取目标：导师姓名、职称、研究方向、联系方式等
- 数据存储路径：`data/raw/`（原始数据）、`data/processed/`（清洗后数据）
- 数据格式：JSON/CSV（可根据协作需求调整）

## 协作说明
- 爬虫输出数据格式：{
    "name": "导师姓名",
    "title": "职称",
    "research_area": "研究方向",
    "contact": "联系方式"
  }
- 若需修改爬取字段/频率，修改 `src/config/settings.py`
- 遇到问题查看 `logs/` 目录下的日志文件