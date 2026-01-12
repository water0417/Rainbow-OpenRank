# Open-Source Project Social Graph System

🌐 **基于 IoTDB + OpenDigger 的开源项目社交图系统**

本项目旨在构建一套**面向 GitHub 开源项目的智能、可交互社交关系分析系统**。  
不同于仅依赖 Star、Fork 等静态指标的传统分析方式，我们引入**时序数据存储、关系网络建模与多维影响力指标**，从更动态、更结构化的视角刻画开源项目的真实生态。

---

## 👥 Team Roles | 小组分工

本项目由 **Rainbow 队** 协作完成，成员分工如下：

### 鲍鑫宇
- **项目方案与文档**：PPT 初稿设计，数据科学与工程作品报告撰写，README.md 编写  
- **算法与系统梳理**：完成项目整体实现流程与技术路线梳理  
- **网页设计**：参与可视化网页功能设计与实现  

### 李昕芮
- **项目展示相关工作**：PPT 制作，项目演示视频录制与剪辑  
- **数据工作**：负责 OpenDigger / GitHub 数据的获取与处理  
- **前端与可视化**：开源项目社交图的可视化网页制作与交互设计  

---

## ✨ Project Highlights | 项目亮点

### 🚀 1. 时序化的数据存储与分析（IoTDB）

- 采用 **Apache IoTDB** 作为核心数据存储引擎  
- 将开发者行为（提交、Issue、PR、互动等）建模为**时间序列数据**  
- 支持：
  - 长周期趋势分析  
  - 活跃度变化检测  
  - 指标的准实时更新  

👉 相比传统关系型数据库，更适合**开源生态的动态演化分析**

---

### 🧠 2. 基于 OpenDigger 的影响力指标体系

引入 **OpenDigger** 标准化指标作为核心分析维度，包括：

- 活跃度（Activity）  
- 社区影响力（Community OpenRank）  
- 全局影响力（Global OpenRank）  

优势在于：

- 避免仅以 Star / Fork 评价项目或开发者的片面性  
- 支持对以下问题进行更精细刻画：
  - 项目生命周期  
  - 核心贡献者角色  
  - 社区结构演化  

---

### 🕸️ 3. 多维关系网络构建（EasyGraph）

- 使用 **EasyGraph** 构建复杂的开源协作网络  
- 支持多种关系类型：
  - Developer – Developer  
  - Developer – Project  
  - Issue / PR – Contributor  

- 可灵活扩展图算法：
  - 影响力传播  
  - 社区发现  
  - 关键节点识别  

---

### 📊 4. 可交互的开源生态可视化

通过可视化方式直观呈现：

- 项目协作结构  
- 贡献者关系网络  
- 指标随时间变化趋势  

面向以下用户群体：

- 研究者  
- 社区维护者  
- 开源学习者  

提供友好、直观的分析入口。

---

## 📁 Project Structure | 项目结构（OpenSource-SocialGraph）

```text
OpenSource-SocialGraph
├── data_collection/            # GitHub / OpenDigger 数据采集
│   ├── github_fetch.py         # GitHub 原始数据获取
│   └── opendigger_fetch.py     # OpenDigger 指标数据获取
├── storage/                    # 数据存储模块
│   ├── iotdb_writer.py         # IoTDB 写入接口
│   └── schema_define.py        # 时序数据结构定义
├── data_processing/            # 数据清洗与特征构建
│   ├── preprocess.py           # 数据预处理
│   └── feature_engineering.py  # 特征工程
├── graph_construction/         # 关系网络构建与分析
│   ├── build_graph.py          # 社交图构建
│   └── graph_analysis.py       # 图分析与指标计算
├── visualization/              # 可视化与展示模块
│   └── dashboard/              # 图可视化与交互界面
├── config/                     # 配置文件
│   └── config.yaml
├── main.py                     # 项目主入口
├── requirements.txt            # Python 依赖
└── README.md                   # 项目说明文档
```

## ⚙️ Getting Started | 快速开始

### 1️⃣ 环境依赖
- Python ≥ 3.9
- Apache IoTDB ≥ 1.1
- Neo4j（可选，用于复杂关系分析）
- Git 
安装 Python 依赖：
pip install -r requirements.txt

### 2️⃣ 配置数据源
在 config/config.yaml 中配置以下信息：
- GitHub Token
- OpenDigger 数据源
- IoTDB 连接信息

### 3️⃣ 数据采集与存储
bash
python data_collection/github_fetch.py
python data_collection/opendigger_fetch.py
采集的数据将被统一写入 IoTDB，形成可持续更新的时序数据集。

### 4️⃣ 构建关系网络
python graph_construction/build_graph.py
生成多维开源协作关系网络，用于后续分析与可视化。

### 5️⃣ 启动系统
python main.py

---
### 🎯 Application Scenarios | 应用场景
- 📌 开源项目生态研究  
- 📌 社区治理与维护者决策支持
- 📌 开源贡献行为分析
- 📌 数据科学 / 社交网络分析教学示例

---
### 🧩 Future Work | 后续计划
- 引入更多图算法与影响力模型
- 支持多项目、跨社区对比分析
- 提供 Web 化交互界面
- 探索 AI 驱动的生态趋势预测

---
### 🤝 Contributing
欢迎通过 Issue 或 Pull Request 参与项目改进 🙌

---
### 📄 License
This project is licensed under the Apache-2.0 License.
Please comply with the license when using or modifying this project.


