import streamlit as st
import arxiv
from datetime import datetime, timezone
from openai import OpenAI
import time
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 页面配置
st.set_page_config(
    page_title="AI-powered Paper Seeker",
    page_icon="🔬",
    layout="wide"
)

# 标题
st.title("🔬 AI-powered Paper Seeker")
st.markdown("**跨学科论文搜索（AI 智能筛选）**")

# 项目介绍
with st.expander("📖 关于本搜索器", expanded=False):
    st.markdown("""
    ### 🎯 功能介绍
    本工具为学术研究人员提供智能化的论文检索服务，帮助您快速发现最新、最相关的学术论文。
    
    ### 🔍 数据来源
    - **arXiv.org**: 全球领先的开放获取预印本库
    - 涵盖物理学、计算机科学、数学等多个学科领域
    - 每日更新，实时追踪学术前沿
    
    ### 🤖 智能分析
    - **DeepSeek V3 API**: 采用 DeepSeek 最新的大语言模型 API
    - 智能理解论文内容，精准判断研究方向相关性
    - 自动生成中文摘要，快速了解论文核心内容

    """)

st.divider()

# 学科领域配置
DISCIPLINES = {
    "光学": {
        "icon": "🔬",
        "arxiv_categories": ["physics.optics", "eess.IV", "physics.app-ph", "cond-mat.mtrl-sci", "quant-ph"],
        "topics": {
            "非线性光学": {
                "keywords": ["nonlinear", "nonlinear optics", "SHG", "THG", "FWM", "frequency conversion"],
                "description": "非线性光学效应、频率转换、和频/差频等"
            },
            "超快光学": {
                "keywords": ["ultrafast", "femtosecond", "picosecond", "attosecond", "pulse"],
                "description": "飞秒/皮秒激光、超短脉冲技术"
            },
            "紫外激光": {
                "keywords": ["ultraviolet", "UV laser", "deep-UV", "DUV"],
                "description": "紫外/深紫外激光技术"
            },
            "量子光学": {
                "keywords": ["quantum optics", "quantum entanglement", "single photon", "quantum state"],
                "description": "量子纠缠、单光子源、量子态操控"
            },
            "光学频率梳": {
                "keywords": ["optical frequency comb", "frequency comb", "mode-locked", "comb"],
                "description": "光频梳、锁模激光"
            },
            "光纤激光": {
                "keywords": ["fiber laser", "fiber optics", "optical fiber"],
                "description": "光纤激光器、光纤光学"
            },
            "超连续谱": {
                "keywords": ["supercontinuum", "SC generation", "broadband"],
                "description": "超连续谱产生、宽带光源"
            },
            "太赫兹光学": {
                "keywords": ["terahertz", "THz", "terahertz generation"],
                "description": "太赫兹产生与应用"
            },
            "光参量过程": {
                "keywords": ["OPO", "OPA", "optical parametric", "parametric amplifier"],
                "description": "光参量振荡器/放大器"
            },
            "高次谐波": {
                "keywords": ["high harmonic generation", "HHG", "attosecond pulse"],
                "description": "高次谐波产生、阿秒脉冲"
            }
        }
    },
    "计算机科学": {
        "icon": "💻",
        "arxiv_categories": ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.NE", "stat.ML"],
        "topics": {
            "人工智能": {
                "keywords": ["artificial intelligence", "AI", "machine intelligence", "intelligent systems"],
                "description": "通用人工智能、智能系统"
            },
            "机器学习": {
                "keywords": ["machine learning", "deep learning", "neural network", "CNN", "RNN", "transformer"],
                "description": "深度学习、神经网络、模型训练"
            },
            "计算机视觉": {
                "keywords": ["computer vision", "image processing", "object detection", "segmentation", "visual recognition"],
                "description": "图像识别、目标检测、图像分割"
            },
            "自然语言处理": {
                "keywords": ["natural language processing", "NLP", "language model", "LLM", "GPT", "BERT", "text generation"],
                "description": "语言模型、文本生成、对话系统"
            },
            "强化学习": {
                "keywords": ["reinforcement learning", "RL", "Q-learning", "policy gradient", "deep RL"],
                "description": "强化学习、策略优化、智能决策"
            },
            "生成模型": {
                "keywords": ["generative model", "GAN", "VAE", "diffusion model", "stable diffusion", "image generation"],
                "description": "生成对抗网络、扩散模型、图像生成"
            },
            "多模态学习": {
                "keywords": ["multimodal", "vision-language", "CLIP", "cross-modal", "audio-visual"],
                "description": "视觉-语言、跨模态学习"
            },
            "图神经网络": {
                "keywords": ["graph neural network", "GNN", "graph learning", "node classification"],
                "description": "图神经网络、图表示学习"
            },
            "联邦学习": {
                "keywords": ["federated learning", "distributed learning", "privacy-preserving"],
                "description": "联邦学习、隐私保护学习"
            },
            "AI安全": {
                "keywords": ["adversarial", "robust", "trustworthy AI", "AI safety", "explainable AI"],
                "description": "对抗攻击、模型鲁棒性、可解释AI"
            }
        }
    }
}

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 搜索设置")
    
    # 学科领域选择
    st.subheader("📚 学科领域")
    selected_discipline = st.selectbox(
        "选择学科领域",
        options=list(DISCIPLINES.keys()),
        format_func=lambda x: f"{DISCIPLINES[x]['icon']} {x}",
        help="选择您感兴趣的学科领域"
    )
    
    st.divider()
    
    # 根据学科显示研究方向
    st.subheader("🔍 研究方向")
    available_topics = DISCIPLINES[selected_discipline]["topics"]
    selected_topics = st.multiselect(
        f"选择{selected_discipline}研究方向",
        options=list(available_topics.keys()),
        default=[list(available_topics.keys())[0]],
        help="可多选，系统会根据您的选择智能筛选论文"
    )
    
    # 显示选中方向的描述
    if selected_topics:
        with st.expander("📖 查看选中方向说明"):
            for topic in selected_topics:
                st.caption(f"**{topic}**: {available_topics[topic]['description']}")
    
    st.divider()
    
    # 时间范围选择
    days_range = st.slider(
        "📅 时间范围（天）",
        min_value=1,
        max_value=30,
        value=7,
        help="搜索过去 N 天内发布的论文"
    )
    
    # 最大结果数
    max_results = st.number_input(
        "📊 最大搜索数量",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
        help="从 arXiv 获取的最大论文数量"
    )
    
    st.divider()
    st.caption("💡 提示：搜索数量越多，耗时越长")

# 初始化 DeepSeek API
@st.cache_resource
def init_deepseek():
    return OpenAI(
        api_key="sk-7b13af61c56140dd80595921a087bd27",
        base_url="https://api.deepseek.com",
        timeout=30.0,  # 设置 30 秒超时
        max_retries=2   # 最多重试 2 次
    )

client_ai = init_deepseek()

# 生成中文摘要（带重试机制）
def generate_summary(title, abstract, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            response = client_ai.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个光学领域的专家。请用中文简明扼要地总结论文的核心内容和创新点。"},
                    {"role": "user", "content": f"论文标题：{title}\n\n摘要：{abstract}\n\n请用2-3句话总结这篇论文的核心内容："}
                ],
                max_tokens=200,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2)  # 等待 2 秒后重试
                continue
            return f"摘要生成失败（已重试 {max_attempts} 次）：{str(e)[:100]}"

# 判断是否相关并标注具体方向（带重试机制）
def is_relevant_with_tags(title, abstract, topics_list, max_attempts=3):
    # 构建动态的判断提示词
    topics_desc = "、".join(topics_list)
    
    for attempt in range(max_attempts):
        try:
            response = client_ai.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"你是一个学术领域的专家助手。请判断论文与哪些研究方向相关。"},
                    {"role": "user", "content": f"论文标题：{title}\n\n摘要：{abstract}\n\n候选研究方向：{topics_desc}\n\n请判断这篇论文与哪些研究方向相关。如果相关，请列出具体的方向名称（用逗号分隔）；如果都不相关，请回答'无关'。"}
                ],
                max_tokens=50,
                temperature=0.1
            )
            answer = response.choices[0].message.content.strip()
            
            # 判断是否相关
            if "无关" in answer or "不相关" in answer or answer.lower() == "none":
                return False, []
            
            # 提取相关的具体方向
            related_topics = []
            for topic in topics_list:
                if topic in answer:
                    related_topics.append(topic)
            
            # 如果有匹配的方向，返回 True 和方向列表
            if related_topics:
                return True, related_topics
            else:
                # 如果没有明确匹配但回答不是"无关"，可能是相关的，返回所有候选方向
                return True, [topics_list[0]]  # 默认返回第一个
                
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2)  # 等待 2 秒后重试
                continue
            st.warning(f"DeepSeek 判断失败（已重试 {max_attempts} 次）：{str(e)[:100]}")
            return False, []

# 开始搜索按钮
if st.button("🚀 开始搜索", type="primary"):
    # 检查是否选择了研究方向
    if not selected_topics:
        st.error("❌ 请至少选择一个研究方向！")
        st.stop()
    
    # 获取当前学科的配置
    discipline_config = DISCIPLINES[selected_discipline]
    available_topics = discipline_config["topics"]
    
    # 根据选择的研究方向构建搜索关键词
    all_keywords = []
    for topic in selected_topics:
        all_keywords.extend(available_topics[topic]["keywords"])
    
    # 构建搜索查询（用 OR 连接所有关键词）
    keyword_query = " OR ".join([f'"{kw}"' if " " in kw else kw for kw in all_keywords])
    
    # 根据学科构建 arXiv 分类查询
    category_query = " OR ".join([f"cat:{cat}" for cat in discipline_config["arxiv_categories"]])
    full_query = f"({category_query}) AND ({keyword_query})"
    
    # 配置 arXiv 客户端
    client = arxiv.Client(page_size=10, delay_seconds=3, num_retries=5)
    search = arxiv.Search(
        query=full_query,
        max_results=max_results,  # 使用用户设置的值
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    today = datetime.now(timezone.utc)
    
    # 进度显示
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    count = 0
    filtered_count = 0
    relevant_papers = []
    
    try:
        results_list = list(client.results(search))
        total = len(results_list)
        
        for idx, result in enumerate(results_list):
            count += 1
            time_diff = (today - result.published).days
            
            # 更新进度
            progress_bar.progress((idx + 1) / total)
            status_text.text(f"正在检查第 {count} 篇论文... ({time_diff} 天前)")
            
            if time_diff > days_range:  # 使用用户设置的时间范围
                continue
            
            filtered_count += 1
            
            # 判断相关性并获取具体相关方向
            is_related, related_topics = is_relevant_with_tags(result.title, result.summary, selected_topics)
            
            if is_related:
                # 生成中文摘要
                summary_cn = generate_summary(result.title, result.summary)
                
                relevant_papers.append({
                    'title': result.title,
                    'pdf_url': result.pdf_url,
                    'published': result.published,
                    'summary': summary_cn,
                    'related_topics': related_topics  # 保存相关的具体方向
                })
            
            time.sleep(0.5)  # 避免请求过快
        
        progress_bar.empty()
        status_text.empty()
        
        # 显示结果
        st.success(f"✅ 搜索完成！共检查 {count} 篇论文，{filtered_count} 篇在时间范围内，找到 {len(relevant_papers)} 篇相关论文。")
        
        if relevant_papers:
            st.markdown("---")
            st.header(f"📚 找到 {len(relevant_papers)} 篇相关论文")
            
            for i, paper in enumerate(relevant_papers, 1):
                with st.expander(f"**{i}. {paper['title']}**", expanded=(i==1)):
                    st.markdown(f"**📅 发布时间：** {paper['published'].strftime('%Y-%m-%d')}")
                    
                    # 显示 AI 判定的相关方向标签
                    if paper.get('related_topics'):
                        tags_html = " ".join([f"<span style='background-color: #e8f4f8; padding: 4px 12px; border-radius: 12px; margin-right: 8px; font-size: 14px;'>🏷️ {topic}</span>" for topic in paper['related_topics']])
                        st.markdown(f" {tags_html}", unsafe_allow_html=True)
                    
                    st.markdown(f"**🔗 PDF 链接：** [{paper['pdf_url']}]({paper['pdf_url']})")
                    st.markdown("**📝 AI 生成摘要（中文）：**")
                    st.info(paper['summary'])
        else:
            st.warning("未找到相关论文。")
    
    except Exception as e:
        st.error(f"❌ 搜索出错：{e}")
        st.info("**可能的解决方案：**\n1. 检查网络连接\n2. 检查 DeepSeek API Key 是否有效\n3. 稍后重试")
else:
    # 显示当前设置
    if selected_topics:
        topics_display = "、".join(selected_topics)
        st.info(f"👆 点击上方按钮开始搜索{selected_discipline}论文\n\n**当前设置：**\n- 学科领域：{DISCIPLINES[selected_discipline]['icon']} {selected_discipline}\n- 研究方向：{topics_display}\n- 时间范围：过去 **{days_range}** 天\n- 最多检索：**{max_results}** 篇")
    else:
        st.warning("⚠️ 请在左侧侧边栏选择至少一个研究方向")
