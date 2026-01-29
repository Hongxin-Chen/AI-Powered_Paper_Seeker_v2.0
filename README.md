# 🔬 AI-powered Paper Seeker

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-API-blue?style=for-the-badge)](https://www.deepseek.com/)
[![arXiv](https://img.shields.io/badge/arXiv-Data-B31B1B?style=for-the-badge)](https://arxiv.org/)

基于 AI 的学术论文智能搜索与分析工具，整合 arXiv 预印本库与 Semantic Scholar API，结合 DeepSeek V3 大语言模型，为学术研究人员提供三种智能化检索模式。(deployed at "https://paperseekerchx.streamlit.app/")

## ✨ 核心功能

### 🔥 arXiv 今日速递
- 📡 自动获取过去 24 小时的最新论文
- 🤖 AI 智能分类，自动识别研究方向
- 📊 可视化饼图展示方向分布
- 💡 一句话总结论文核心工作
- 🎯 **个性化精选**：根据您的研究领域智能推荐高度相关论文

### 🏆 顶刊近一周
- 📚 追踪 Nature、Science、Nature Photonics 等顶级期刊
- ⏰ 实时监控过去 7 天内的最新发表
- 🔍 按研究方向筛选顶刊论文
- 🎯 **AI 精选**：优先展示与您研究方向相关的顶刊论文

### 🔍 自定义深度搜索
- 📋 预设领域选择或自定义关键词输入
- ⏱️ 灵活设置时间范围（1-30 天）
- 🔢 自定义检索数量（10-500 篇）
- 📝 AI 生成中文摘要
- 🎯 **智能推荐**：识别与您研究背景高度匹配的论文

## 🎯 个性化 AI 精选

在所有三个模块中，您可以设置自己的研究领域，系统将：
- 自动识别与您研究方向高度相关的论文
- 给出 1-10 分的相关度评分
- 提供简短的关联要点说明
- 优先展示精选论文，节省您的时间

## 🌟 支持的研究领域

### 🔬 光学
非线性光学 | 超快光学 | 紫外激光 | 量子光学 | 光学频率梳 | 光纤激光 | 超连续谱 | 太赫兹光学 | 光参量过程 | 高次谐波

### 💻 计算机科学
人工智能 | 机器学习 | 计算机视觉 | 自然语言处理 | 强化学习 | 生成模型 | 多模态学习 | 图神经网络 | 联邦学习 | AI安全

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在 `PaperAgent.py` 文件中替换你的 DeepSeek API Key：

```python
client_ai = OpenAI(
    api_key="YOUR_DEEPSEEK_API_KEY",  # 替换为你的 API Key
    base_url="https://api.deepseek.com"
)
```

获取 API Key：访问 [DeepSeek Platform](https://platform.deepseek.com)

### 3. 运行应用

```bash
streamlit run PaperAgent.py
```

应用将自动在浏览器中打开（默认地址：http://localhost:8501）

## 📖 使用指南

### 第一步：设置研究领域（可选）
展开"设置您的研究领域"，输入您的研究方向和技术背景，AI 将为您精选最相关的论文。

示例：
```
我是一名从事紫外固体激光器的激光工程师，主要从事发355nm、266nm、193nm紫外激光器，
同时在半导体行业，我还从事设计litho四波长定位激光器设计。
```

### Tab 1: arXiv 今日速递
1. 选择学科领域（光学/计算机科学）
2. 选择最大论文篇数（无限制或 10-100 篇）
3. 点击"刷新今日速递"
4. 查看：
   - 📊 研究方向分布饼图
   - 🎯 为您精选的高相关度论文
   - 📚 全部论文列表（带星标标记精选论文）

### Tab 2: 顶刊近一周
1. 选择学科领域
2. 选择具体研究方向（可多选）
3. 点击"搜索顶刊论文"
4. 查看近 7 天内顶刊的最新发表

**监控期刊**：
- 光学：Nature、Science、Nature Photonics、Optica、Physical Review Letters 等
- 计算机：Nature、Science、NeurIPS、ICML、CVPR、ICCV 等

### Tab 3: 自定义搜索
**模式 1：从预设领域选择**
1. 选择学科 → 选择研究方向
2. 设置时间范围和检索数量
3. 点击"开始搜索"

**模式 2：自定义输入关键词**
1. 选择学科分类（用于限定 arXiv 类别）
2. 输入关键词（逗号或空格分隔）
   - 例如：`ultraviolet laser, 355nm, 266nm, solid-state laser, lithography`
3. 设置时间范围和检索数量
4. 点击"开始搜索"

## 🛠️ 技术栈

- **前端框架**: Streamlit
- **数据源**: 
  - arXiv API（预印本论文）
  - Semantic Scholar API（顶刊论文）
- **AI 模型**: DeepSeek V3 API
- **可视化**: Plotly（饼图）
- **编程语言**: Python 3.8+

## 📋 依赖项

```
streamlit>=1.28.0
arxiv>=2.0.0
openai>=1.0.0
urllib3>=2.0.0
requests>=2.28.0
plotly>=5.0.0
```
## 🔍 工作原理

### arXiv 今日速递
1. 从 arXiv 获取过去 24 小时的论文
2. AI 自动分类到 10 个研究方向
3. 生成一句话总结和完整英文摘要
4. 根据用户研究领域进行个性化精选
5. 饼图可视化展示方向分布

### 顶刊近一周
1. 通过 Semantic Scholar API 搜索关键词
2. 筛选 Nature、Science 等顶级期刊
3. 过滤近 7 天内的最新论文
4. AI 生成一句话总结
5. 根据用户领域智能推荐

### 自定义搜索
1. 根据预设方向或自定义关键词构建查询
2. 从 arXiv 检索指定时间范围内的论文
3. AI 判断相关性并生成中文摘要
4. 个性化精选高相关度论文
5. 展示完整英文摘要供深入阅读

### AI 精选算法
- 分析论文标题和摘要与用户研究领域的匹配度
- 给出 1-10 分的相关度评分（6 分以上认为相关）
- 提取关键关联点（不超过 30 字）
- 优先展示高相关度论文

## ⚙️ 配置说明

### 功能参数

**今日速递**：
- 最大论文数：无限制 / 10-100 篇
- 时间范围：固定 24 小时

**顶刊监控**：
- 时间范围：固定 7 天
- 搜索年份：当前年份（2026）
- API 超时：30 秒，最多重试 3 次

**自定义搜索**：
- 时间范围：1-30 天（默认 7 天）
- 最大检索数量：10-500 篇（默认 100 篇）
- AI 超时：30 秒
- 重试次数：最多 3 次

### arXiv 分类映射

- **光学**: `physics.optics`, `eess.IV`, `physics.app-ph`, `cond-mat.mtrl-sci`, `quant-ph`
- **计算机科学**: `cs.AI`, `cs.LG`, `cs.CV`, `cs.CL`, `cs.NE`, `stat.ML`

### 顶刊白名单

**光学领域**：
- Nature、Science
- Nature Photonics、Nature Communications
- Optica、Physical Review Letters
- Advanced Photonics、Laser & Photonics Reviews
- Light: Science & Applications

**计算机科学**：
- Nature、Science、Nature Machine Intelligence
- NeurIPS、ICML、ICLR
- CVPR、ICCV

## 🎨 界面截图

<img width="2800" height="1496" alt="image" src="https://github.com/user-attachments/assets/dd5d609e-b33d-445d-8a62-b03abe60063b" />
<img width="2818" height="1226" alt="image" src="https://github.com/user-attachments/assets/e5e8b698-f924-4d15-bedb-081b50a78eee" />
<img width="2866" height="1486" alt="image" src="https://github.com/user-attachments/assets/74dfd443-8504-4d7f-a1b3-4ac64aeffc5e" />



*界面包含三个主要 Tab：*
- 🔥 arXiv 今日速递（带饼图和精选）
- 🏆 顶刊近一周（实时监控）
- 🔍 自定义搜索（灵活配置）

## ⚠️ 注意事项

1. **API Key**: 需要有效的 DeepSeek API Key
2. **网络连接**: Semantic Scholar API 可能需要稳定的网络环境
3. **SSL 问题**: 代码已禁用 SSL 验证以适应某些网络环境
4. **请求频率**: arXiv API 设置了 2 秒延迟，避免请求过快
5. **论文数量**: 顶刊监控可能返回较少结果（因为顶刊发表周期较长）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，欢迎通过 bjackchen955@gmail.com 联系。

---

**开发说明**: 
- 主文件：`PaperAgent.py`
- 三个 Tab 各自独立，无侧边栏
- 所有 Tab 都支持个性化 AI 精选功能
- 使用 Plotly 进行数据可视化

**使用提示**: 
1. 首次使用建议设置研究领域，获得更精准的推荐
2. 今日速递每天运行一次即可
3. 顶刊监控建议每周运行，关注最新发表
4. 自定义搜索适合深度挖掘特定方向论文
