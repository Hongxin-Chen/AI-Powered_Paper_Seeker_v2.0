# 🔬 AI-Powered Paper Seeker

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-API-blue?style=for-the-badge)](https://www.deepseek.com/)

基于 AI 的学术论文智能搜索与分析工具，帮助研究人员快速发现最新、最相关的学术论文。

## ✨ 主要特性

- 📚 **多学科支持**: 光学、计算机科学等多个领域
- 🔍 **细分方向**: 每个学科下有 10+ 个细分研究方向
- 🤖 **AI 智能筛选**: 使用 DeepSeek V3 API 智能判断论文相关性
- 📝 **自动摘要**: AI 生成中文论文摘要，快速了解核心内容
- 🏷️ **智能标注**: 自动标注论文所属的具体研究方向
- ⚡ **实时搜索**: 自定义时间范围（1-30天），追踪最新论文
- 🎨 **可视化界面**: 基于 Streamlit 的友好交互界面

## 🌟 支持的研究领域

### 🔬 光学
- 非线性光学
- 超快光学
- 紫外激光
- 量子光学
- 光学频率梳
- 光纤激光
- 超连续谱
- 太赫兹光学
- 光参量过程
- 高次谐波

### 💻 计算机科学
- 人工智能
- 机器学习
- 计算机视觉
- 自然语言处理
- 强化学习
- 生成模型
- 多模态学习
- 图神经网络
- 联邦学习
- AI 安全

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在 `PaperSearcher.py` 文件中替换你的 DeepSeek API Key：

```python
client_ai = OpenAI(
    api_key="YOUR_DEEPSEEK_API_KEY",  # 替换为你的 API Key
    base_url="https://api.deepseek.com"
)
```

获取 API Key：访问 [DeepSeek Platform](https://platform.deepseek.com)

### 3. 运行应用

```bash
streamlit run PaperSearcher.py
```

应用将自动在浏览器中打开（默认地址：http://localhost:8501）

## 📖 使用指南

1. **选择学科领域**：在左侧边栏选择感兴趣的学科（光学或计算机科学）
2. **选择研究方向**：根据学科选择一个或多个具体的研究方向
3. **设置搜索参数**：
   - 时间范围：1-30 天
   - 最大搜索数量：10-500 篇
4. **点击搜索**：点击"开始搜索"按钮
5. **查看结果**：浏览 AI 筛选后的论文列表，包含：
   - 论文标题
   - 发布时间
   - AI 判定的相关方向标签
   - PDF 下载链接
   - AI 生成的中文摘要

## 🛠️ 技术栈

- **前端框架**: Streamlit
- **数据源**: arXiv API
- **AI 模型**: DeepSeek V3 API
- **编程语言**: Python 3.8+

## 📋 依赖项

```
streamlit>=1.28.0
arxiv>=2.0.0
openai>=1.0.0
urllib3>=2.0.0
```

## 🔍 工作原理

1. **论文获取**: 从 arXiv 按关键词和分类获取最新论文
2. **时间筛选**: 根据用户设定的时间范围过滤论文
3. **AI 判断**: DeepSeek 分析论文标题和摘要，判断相关性
4. **方向标注**: AI 标注论文属于哪些具体研究方向
5. **摘要生成**: AI 生成易懂的中文摘要
6. **结果展示**: 可视化展示所有相关论文

## ⚙️ 配置说明

### 搜索参数

- **时间范围**: 默认 7 天，可调整为 1-30 天
- **最大搜索数量**: 默认 100 篇，可调整为 10-500 篇
- **AI 超时**: 30 秒
- **重试次数**: 最多 3 次

### arXiv 分类映射

- **光学**: physics.optics, eess.IV, physics.app-ph, cond-mat.mtrl-sci, quant-ph
- **计算机科学**: cs.AI, cs.LG, cs.CV, cs.CL, cs.NE, stat.ML



