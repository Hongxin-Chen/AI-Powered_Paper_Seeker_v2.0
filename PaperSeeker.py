import streamlit as st
import arxiv
from datetime import datetime, timezone, timedelta
from openai import OpenAI
import time
import urllib3
import requests

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 页面配置
st.set_page_config(
    page_title="AI-powered Paper Seeker",
    page_icon="🔍",
    layout="wide"
)

# 标题和时间
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🔍 AI-powered Paper Seeker")
with col2:
    st.markdown(f"### 📅 {datetime.now().strftime('%Y-%m-%d')}")
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# 用户研究领域设置
with st.expander("👤 设置您的研究领域（AI 将优先为您精选相关论文）", expanded=False):
    user_research_field = st.text_area(
        "请描述您的研究方向和技术背景",
        value="我是一名从事紫外固体激光器的激光工程师，主要从事发355nm、266nm、193nm紫外激光器，同时在半导体行业，我还从事设计litho四波长定位激光器设计。",
        height=100,
        help="详细描述您的研究方向、关注的技术领域和应用场景，AI 将根据此信息为您精选最相关的论文"
    )
    st.session_state['user_research_field'] = user_research_field
    if user_research_field:
        st.success("✅ 已设置研究领域，搜索时将为您精选相关论文")

# 项目介绍
with st.expander("📖 关于本搜索器", expanded=False):
    st.markdown("""
    ### 🎯 功能特色
    本工具整合 arXiv 预印本库与 Semantic Scholar API，结合 DeepSeek V3 大语言模型，为学术研究人员提供三种智能化检索模式：
    - **今日速递**：自动获取过去24小时的最新论文，AI 智能分类并生成中文摘要
    - **顶刊周论文**：追踪光学与计算机领域的顶级期刊最新发表（Nature Photonics、Science、CVPR等）
    - **自定义搜索**：灵活设置时间范围和检索数量，深度挖掘特定方向论文
    
    ### 🔍 数据来源
    - **arXiv.org**: 全球最大的开放获取预印本库，涵盖光学、计算机科学等前沿领域
    - **Semantic Scholar**: 微软学术图谱，提供顶刊论文的引用数据和影响力分析
    
    ### 🤖 AI 智能分析
    - **DeepSeek V3 API**: 自动判断论文研究方向、生成中文摘要、筛选相关论文
    - 智能理解论文内容，精准判断研究方向相关性
    - 自动生成中文摘要，快速了解论文核心内容

    """)

st.divider()

# 顶刊白名单配置
TOP_JOURNALS = {
    "光学": [
        "Nature",  # Nature 主刊
        "Science",  # Science 主刊
        "Nature Photonics",
        "Nature Communications",
        "Light: Science & Applications",
        "Optica",
        "Physical Review Letters",
        "Advanced Photonics",
        "Laser & Photonics Reviews"
    ],
    "计算机科学": [
        "Nature",
        "Science",
        "Nature Machine Intelligence",
        "NeurIPS",
        "ICML",
        "ICLR",
        "CVPR",
        "ICCV"
    ]
}

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

# 生成一句话总结（用于今日速递）
def generate_one_sentence_summary(title, abstract, max_attempts=3):
    client_ai = init_deepseek()
    for attempt in range(max_attempts):
        try:
            response = client_ai.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个学术论文分析专家。请用一句话（不超过30个汉字）概括论文的核心工作。"},
                    {"role": "user", "content": f"论文标题：{title}\n\n摘要：{abstract}\n\n请用一句话说明这篇论文做了什么："}
                ],
                max_tokens=100,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2)
                continue
            return "总结生成失败"

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

# AI 精选论文（判断与用户研究领域的相关性）
def ai_filter_for_user(title, abstract, user_field, max_attempts=2):
    """
    让 DeepSeek 判断论文是否与用户研究领域高度相关，并提取关键关联点
    返回: (是否相关, 相关度评分1-10, 关联要点)
    """
    if not user_field or user_field.strip() == "":
        return False, 0, ""
    
    client_ai = init_deepseek()
    for attempt in range(max_attempts):
        try:
            response = client_ai.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个学术文献分析专家。请判断论文是否与用户的研究领域相关，并提取关键关联点。"},
                    {"role": "user", "content": f"用户研究领域：{user_field}\n\n论文标题：{title}\n\n论文摘要：{abstract}\n\n请判断这篇论文是否与用户研究领域高度相关。如果相关，请给出相关度评分（1-10分）和简短的关联要点（不超过30字）。格式：评分|关联要点。如果不相关，只回答：不相关"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            answer = response.choices[0].message.content.strip()
            
            if "不相关" in answer:
                return False, 0, ""
            
            # 解析评分和关联要点
            if "|" in answer:
                parts = answer.split("|")
                try:
                    score = int(parts[0].strip())
                    relevance = parts[1].strip() if len(parts) > 1 else ""
                    return score >= 6, score, relevance  # 6分以上认为相关
                except:
                    return False, 0, ""
            
            return False, 0, ""
            
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2)
                continue
            return False, 0, ""

# AI 分类论文研究方向（用于今日速递）
def classify_paper_region(title, abstract, discipline, max_attempts=2):
    """
    让 DeepSeek 分析论文属于哪个研究方向
    """
    topics_list = list(DISCIPLINES[discipline]["topics"].keys())
    topics_desc = "、".join(topics_list)
    
    for attempt in range(max_attempts):
        try:
            response = client_ai.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": f"你是一个学术分类专家。请判断论文最贴合以下哪个研究方向。"},
                    {"role": "user", "content": f"论文标题：{title}\n\n摘要：{abstract}\n\n候选方向：{topics_desc}\n\n请从候选方向中选择一个最贴合的方向，只回答方向名称。"}
                ],
                max_tokens=20,
                temperature=0.1
            )
            answer = response.choices[0].message.content.strip()
            
            # 匹配具体方向
            for topic in topics_list:
                if topic in answer:
                    return topic
            
            # 如果没匹配到，返回第一个作为默认
            return topics_list[0] if topics_list else "未分类"
                
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(1)
                continue
            return "未分类"
    
    return "未分类"

# Semantic Scholar API - 顶刊监控
def fetch_top_journal_updates(discipline, topic_keywords, days=7):
    """
    从 Semantic Scholar 获取顶刊最新论文（默认近7天）
    """
    target_venues = TOP_JOURNALS.get(discipline, [])
    current_year = datetime.now().year
    
    # 构建关键词查询
    keyword_query = " ".join(topic_keywords[:5])  # 使用前5个关键词
    
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": keyword_query,
        "year": f"{current_year}",  # 只搜当前年份
        "limit": 100,
        "fields": "title,abstract,venue,year,publicationDate,citationCount,url,authors"
    }
    
    # 添加重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 增加超时时间并禁用 SSL 验证（在某些网络环境下需要）
            response = requests.get(
                url, 
                params=params, 
                timeout=30,
                verify=False  # 禁用 SSL 验证（可能解决 SSL 错误）
            )
            
            # 调试信息
            st.info(f"📡 API 请求状态码: {response.status_code}")
            
            if response.status_code != 200:
                if attempt < max_retries - 1:
                    st.warning(f"API 请求失败（状态码 {response.status_code}），正在重试 {attempt + 2}/{max_retries}...")
                    time.sleep(2)
                    continue
                else:
                    st.error(f"API 返回错误: {response.status_code} - {response.text[:200]}")
                    return []
            
            data = response.json()
            st.info(f"📊 API 返回论文总数: {len(data.get('data', []))}")
            
            cleaned_papers = []
            filtered_count = 0
            venue_debug = {}  # 调试：记录所有出现的期刊名
            
            if 'data' in data:
                for paper in data['data']:
                    venue_name = paper.get('venue', '')
                    pub_date = paper.get('publicationDate', '')
                    
                    # 记录期刊出现次数
                    if venue_name:
                        venue_debug[venue_name] = venue_debug.get(venue_name, 0) + 1
                    
                    # 期刊过滤 - 放宽匹配条件
                    if not venue_name:
                        filtered_count += 1
                        continue
                    
                    # 检查是否在目标期刊列表中（更宽松的模糊匹配）
                    is_target_venue = False
                    venue_lower = venue_name.lower()
                    for target in target_venues:
                        target_lower = target.lower()
                        # 只要包含关键词就认为匹配（比如 "Nature" 匹配 "Nature Photonics" 和 "Nature Communications"）
                        target_key = target_lower.split()[0]  # 取第一个单词作为关键词
                        if target_key in venue_lower or venue_lower in target_lower or target_lower in venue_lower:
                            is_target_venue = True
                            break
                    
                    if not is_target_venue:
                        filtered_count += 1
                        continue
                    
                    # 时间过滤（如果有发表日期）
                    if pub_date:
                        try:
                            pub_datetime = datetime.strptime(pub_date, '%Y-%m-%d')
                            if (datetime.now() - pub_datetime).days > days:
                                continue
                        except:
                            pass
                    
                    abstract_text = paper.get('abstract', '')
                    
                    # 生成一句话总结
                    one_sentence = ""
                    if abstract_text:
                        one_sentence = generate_one_sentence_summary(paper['title'], abstract_text)
                    
                    cleaned_papers.append({
                        "title": paper['title'],
                        "venue": venue_name,
                        "year": paper['year'],
                        "link": paper.get('url', ''),
                        "abstract": abstract_text,
                        "one_sentence": one_sentence,
                        "date": pub_date
                    })
            
            # 显示期刊调试信息
            if venue_debug:
                st.info(f"📚 检测到的期刊（前10）: {', '.join(list(venue_debug.keys())[:10])}")
            st.info(f"🎯 期刊过滤: 剔除 {filtered_count} 篇非目标期刊，保留 {len(cleaned_papers)} 篇")
            return cleaned_papers
            
        except requests.exceptions.SSLError as e:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ SSL 连接错误，正在重试 {attempt + 2}/{max_retries}... (可能是网络问题)")
                time.sleep(3)
                continue
            else:
                st.error(f"❌ SSL 连接失败（已重试 {max_retries} 次）。请检查：\n1. 网络连接是否正常\n2. 是否使用了代理或防火墙\n3. 稍后再试")
                return []
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ 网络连接错误，正在重试 {attempt + 2}/{max_retries}...")
                time.sleep(3)
                continue
            else:
                st.error(f"❌ 网络连接失败（已重试 {max_retries} 次）。请检查网络连接。")
                return []
        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ 请求出错，正在重试 {attempt + 2}/{max_retries}...")
                time.sleep(3)
                continue
            else:
                st.error(f"❌ Semantic Scholar API 调用失败：{str(e)[:200]}")
                return []
    
    return []

# arXiv 今日速递
def fetch_arxiv_daily_updates(discipline_config, hours=24):
    """
    获取过去 N 小时的 arXiv 新论文
    """
    category_query = " OR ".join([f"cat:{cat}" for cat in discipline_config["arxiv_categories"]])
    
    client = arxiv.Client(page_size=10, delay_seconds=2, num_retries=3)
    search = arxiv.Search(
        query=category_query,
        max_results=50,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent_papers = []
    
    try:
        for result in client.results(search):
            if result.published >= cutoff_time:
                recent_papers.append({
                    "title": result.title,
                    "pdf_url": result.pdf_url,
                    "published": result.published,
                    "summary": result.summary,
                    "authors": [author.name for author in result.authors]
                })
            else:
                break  # 已经按时间排序，后面的更早
        
        return recent_papers
    except Exception as e:
        st.error(f"arXiv API 调用失败：{e}")
        return []

# 开始主界面 - Tab 模式
tab1, tab2, tab3 = st.tabs(["🔥 arXiv 今日速递", "🏆 顶刊周论文", "🔍 自定义搜索"])

# Tab 1: arXiv 今日速递
with tab1:
    st.subheader("📡 arXiv 今日速递 (Paper in 24hours)")
    
    # 学科选择和限制设置
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        daily_discipline = st.selectbox(
            "选择学科",
            options=list(DISCIPLINES.keys()),
            key="daily_discipline"
        )
    with col2:
        daily_limit_option = st.selectbox(
            "最大论文篇数",
            options=["无限制", "10篇", "20篇", "30篇", "50篇", "100篇"],
            index=3,
            key="daily_limit"
        )
        # 解析限制数量
        if daily_limit_option == "无限制":
            daily_max_papers = None
        else:
            daily_max_papers = int(daily_limit_option.replace("篇", ""))
    with col3:
        st.caption(f"监控分类：{', '.join(DISCIPLINES[daily_discipline]['arxiv_categories'])}")
    
    if st.button("🔄 刷新今日速递", key="refresh_daily", type="primary"):
        with st.spinner("正在扫描 arXiv 最新论文并分析分类..."):
            discipline_config = DISCIPLINES[daily_discipline]
            daily_papers = fetch_arxiv_daily_updates(discipline_config, hours=24)
            
            if daily_papers:
                # 应用篇数限制
                if daily_max_papers is not None and len(daily_papers) > daily_max_papers:
                    daily_papers = daily_papers[:daily_max_papers]
                
                # 使用 AI 分类每篇论文并生成一句话总结
                region_counts = {}
                user_field = st.session_state.get('user_research_field', '')
                user_relevant_papers = []  # 与用户研究领域高度相关的论文
                
                for paper in daily_papers:
                    region = classify_paper_region(
                        paper['title'], 
                        paper['summary'], 
                        daily_discipline
                    )
                    paper['region'] = region
                    # 生成一句话总结
                    paper['one_sentence'] = generate_one_sentence_summary(paper['title'], paper['summary'])
                    region_counts[region] = region_counts.get(region, 0) + 1
                    
                    # AI 精选：判断是否与用户研究领域相关
                    if user_field:
                        is_user_relevant, relevance_score, relevance_point = ai_filter_for_user(
                            paper['title'], 
                            paper['summary'], 
                            user_field
                        )
                        if is_user_relevant:
                            paper['user_relevant'] = True
                            paper['relevance_score'] = relevance_score
                            paper['relevance_point'] = relevance_point
                            user_relevant_papers.append(paper)
                
                st.success(f"✅ 找到 {len(daily_papers)} 篇新论文！" + (f" 其中 **{len(user_relevant_papers)}** 篇与您的研究领域高度相关 🎯" if user_relevant_papers else ""))
                
                # 显示饼图
                if region_counts:
                    st.subheader("📊 研究方向分布")
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        import plotly.graph_objects as go
                        fig = go.Figure(data=[go.Pie(
                            labels=list(region_counts.keys()),
                            values=list(region_counts.values()),
                            hole=0.3,
                            textposition='inside',
                            textinfo='percent',
                            hovertemplate='<b>%{label}</b><br>论文数：%{value}<br>占比：%{percent}<extra></extra>'
                        )])
                        fig.update_layout(
                            showlegend=True,
                            height=400,
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.02,
                                font=dict(size=11)
                            ),
                            margin=dict(l=20, r=120, t=20, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("**统计数据**")
                        for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
                            percentage = (count / len(daily_papers)) * 100
                            st.metric(region, f"{count} 篇", f"{percentage:.1f}%")
                
                st.divider()
                
                # 如果有精选论文，优先显示
                if user_relevant_papers:
                    st.subheader(f"🎯 为您精选 ({len(user_relevant_papers)} 篇)")
                    st.caption("AI 识别出与您研究领域高度相关的论文")
                    
                    for i, paper in enumerate(user_relevant_papers, 1):
                        hours_ago = int((datetime.now(timezone.utc) - paper['published']).total_seconds() / 3600)
                        with st.expander(f"⭐ **{i}. {paper['title']}** 🕐 {hours_ago}小时前", expanded=(i==1)):
                            # 显示相关度评分和关联要点
                            if paper.get('relevance_score'):
                                st.markdown(f"**🎯 相关度评分：** {paper['relevance_score']}/10")
                            if paper.get('relevance_point'):
                                st.info(f"💡 **与您的关联：** {paper['relevance_point']}")
                            
                            # 显示分类标签
                            region_tag = paper.get('region', '未分类')
                            st.markdown(f"**🏷️ 研究方向：** `{region_tag}`")
                            st.markdown(f"**👥 作者：** {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
                            st.markdown(f"**🔗 PDF：** [{paper['pdf_url']}]({paper['pdf_url']})")
                            
                            # 显示一句话总结
                            if paper.get('one_sentence'):
                                st.markdown(f"**💡 核心工作：** {paper['one_sentence']}")
                            
                            # 显示完整英文摘要
                            st.markdown("**📝 完整摘要（英文）：**")
                            with st.expander("展开查看完整摘要"):
                                st.caption(paper['summary'])
                    
                    st.divider()
                
                st.subheader("📚 全部论文列表")
                
                for i, paper in enumerate(daily_papers, 1):
                    hours_ago = int((datetime.now(timezone.utc) - paper['published']).total_seconds() / 3600)
                    # 如果论文已在精选中显示，添加标记
                    title_prefix = "⭐ " if paper.get('user_relevant') else ""
                    with st.expander(f"{title_prefix}**{i}. {paper['title']}** 🕐 {hours_ago}小时前"):
                        # 显示分类标签
                        region_tag = paper.get('region', '未分类')
                        st.markdown(f"**🏷️ 研究方向：** `{region_tag}`")
                        st.markdown(f"**👥 作者：** {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
                        st.markdown(f"**🔗 PDF：** [{paper['pdf_url']}]({paper['pdf_url']})")
                        
                        # 显示一句话总结
                        if paper.get('one_sentence'):
                            st.markdown(f"**💡 核心工作：** {paper['one_sentence']}")
                        
                        # 显示完整英文摘要
                        st.markdown("**📝 完整摘要（英文）：**")
                        with st.expander("展开查看完整摘要"):
                            st.caption(paper['summary'])
            else:
                st.info("暂无新论文，稍后再试")
    else:
        st.info("👆 点击按钮获取今日最新论文")

# Tab 2: 顶刊近一周论文
with tab2:
    st.subheader("🏆 顶刊近一周 - 最新发表（过去7天）")
    
    # 学科和方向选择
    col1, col2 = st.columns(2)
    with col1:
        journal_discipline = st.selectbox(
            "选择学科",
            options=list(DISCIPLINES.keys()),
            key="journal_discipline"
        )
    
    with col2:
        journal_available_topics = DISCIPLINES[journal_discipline]["topics"]
        journal_selected_topics = st.multiselect(
            "选择研究方向",
            options=list(journal_available_topics.keys()),
            default=[list(journal_available_topics.keys())[0]],
            key="journal_topics"
        )
    
    st.caption(f"📚 监控期刊：{', '.join(TOP_JOURNALS[journal_discipline])}")
    
    if journal_selected_topics and st.button("🔍 搜索顶刊论文", key="search_journals", type="primary"):
        with st.spinner("正在扫描顶级期刊近一周论文..."):
            all_keywords = []
            for topic in journal_selected_topics:
                all_keywords.extend(journal_available_topics[topic]["keywords"])
            
            journal_papers = fetch_top_journal_updates(journal_discipline, all_keywords, days=7)
            
            if journal_papers:
                # AI 精选：判断与用户研究领域的相关性
                user_field = st.session_state.get('user_research_field', '')
                user_relevant_papers = []
                
                if user_field:
                    for paper in journal_papers:
                        is_user_relevant, relevance_score, relevance_point = ai_filter_for_user(
                            paper['title'], 
                            paper['abstract'], 
                            user_field
                        )
                        if is_user_relevant:
                            paper['user_relevant'] = True
                            paper['relevance_score'] = relevance_score
                            paper['relevance_point'] = relevance_point
                            user_relevant_papers.append(paper)
                
                st.success(f"✅ 找到 {len(journal_papers)} 篇顶刊论文！" + (f" 其中 **{len(user_relevant_papers)}** 篇与您的研究领域高度相关 🎯" if user_relevant_papers else ""))
                
                # 如果有精选论文，优先显示
                if user_relevant_papers:
                    st.subheader(f"🎯 为您精选 ({len(user_relevant_papers)} 篇)")
                    st.caption("AI 识别出与您研究领域高度相关的顶刊论文")
                    
                    for i, paper in enumerate(user_relevant_papers, 1):
                        with st.expander(f"⭐ **{i}. {paper['title']}**", expanded=(i==1)):
                            # 显示相关度评分和关联要点
                            if paper.get('relevance_score'):
                                st.markdown(f"**🎯 相关度评分：** {paper['relevance_score']}/10")
                            if paper.get('relevance_point'):
                                st.info(f"💡 **与您的关联：** {paper['relevance_point']}")
                            
                            st.markdown(f"**📚 期刊：** {paper['venue']} ({paper['year']})")
                            st.markdown(f"**📅 发表时间：** {paper['date']}")
                            st.markdown(f"**🔗 链接：** [{paper['link']}]({paper['link']})")
                            
                            # 显示一句话总结
                            if paper.get('one_sentence'):
                                st.markdown(f"**💡 核心工作：** {paper['one_sentence']}")
                            
                            # 显示完整英文摘要
                            if paper['abstract']:
                                st.markdown("**📝 完整摘要（英文）：**")
                                with st.expander("展开查看完整摘要"):
                                    st.caption(paper['abstract'])
                    
                    st.divider()
                
                st.subheader("📚 全部顶刊论文列表")
                
                for i, paper in enumerate(journal_papers, 1):
                    # 如果论文已在精选中显示，添加标记
                    title_prefix = "⭐ " if paper.get('user_relevant') else ""
                    with st.expander(f"{title_prefix}**{i}. {paper['title']}**"):
                        st.markdown(f"**📚 期刊：** {paper['venue']} ({paper['year']})")
                        st.markdown(f"**📅 发表时间：** {paper['date']}")
                        st.markdown(f"**� 链接：** [{paper['link']}]({paper['link']})")
                        
                        # 显示一句话总结
                        if paper.get('one_sentence'):
                            st.markdown(f"**💡 核心工作：** {paper['one_sentence']}")
                        
                        # 显示完整英文摘要
                        if paper['abstract']:
                            st.markdown("**📝 完整摘要（英文）：**")
                            with st.expander("展开查看完整摘要"):
                                st.caption(paper['abstract'])
            else:
                st.warning("未找到相关论文，尝试调整研究方向")
    else:
        if not journal_selected_topics:
            st.warning("⚠️ 请先选择研究方向")
        else:
            st.info("👆 点击按钮搜索顶刊最新论文")

# Tab 3: 自定义搜索（原有功能）
with tab3:
    st.subheader("🔍 自定义深度搜索")
    st.caption("使用 AI 智能筛选，生成中文摘要")
    
    # 搜索模式选择
    search_mode = st.radio(
        "搜索模式",
        options=["📋 从预设领域选择", "✍️ 自定义输入关键词"],
        horizontal=True,
        key="search_mode"
    )
    
    st.markdown("---")
    
    if search_mode == "📋 从预设领域选择":
        # 原有的预设领域选择
        col1, col2 = st.columns(2)
        with col1:
            custom_discipline = st.selectbox(
                "选择学科",
                options=list(DISCIPLINES.keys()),
                key="custom_discipline"
            )
        
        with col2:
            custom_available_topics = DISCIPLINES[custom_discipline]["topics"]
            custom_selected_topics = st.multiselect(
                "选择研究方向",
                options=list(custom_available_topics.keys()),
                default=list(custom_available_topics.keys())[:2],
                key="custom_topics"
            )
    else:
        # 自定义输入模式
        col1, col2 = st.columns(2)
        with col1:
            custom_discipline = st.selectbox(
                "选择学科分类（用于限定arXiv类别）",
                options=list(DISCIPLINES.keys()),
                key="custom_discipline_manual"
            )
        
        with col2:
            st.caption("💡 提示：可输入多个关键词，用逗号或空格分隔")
        
        custom_keywords_input = st.text_area(
            "输入搜索关键词",
            placeholder="例如：ultraviolet laser, 355nm, 266nm, solid-state laser, lithography",
            height=100,
            key="custom_keywords"
        )
        
        # 将用户输入转换为关键词列表
        if custom_keywords_input:
            # 支持逗号或空格分隔
            custom_keywords_list = [kw.strip() for kw in custom_keywords_input.replace(',', ' ').split() if kw.strip()]
        else:
            custom_keywords_list = []
    
    # 时间和数量设置
    col3, col4 = st.columns(2)
    with col3:
        custom_days_range = st.slider(
            "时间范围（天）",
            min_value=1,
            max_value=30,
            value=7,
            key="custom_days"
        )
    
    with col4:
        custom_max_results = st.number_input(
            "最大检索数量",
            min_value=10,
            max_value=500,
            value=100,
            step=10,
            key="custom_max"
        )
    
    st.markdown("---")
    
    # 开始搜索按钮
    if st.button("🚀 开始搜索", type="primary", key="custom_search"):
        # 根据搜索模式构建关键词
        if search_mode == "📋 从预设领域选择":
            # 检查是否选择了研究方向
            if not custom_selected_topics:
                st.error("❌ 请至少选择一个研究方向！")
                st.stop()
            
            # 获取当前学科的配置
            discipline_config = DISCIPLINES[custom_discipline]
            available_topics = discipline_config["topics"]
            
            # 根据选择的研究方向构建搜索关键词
            all_keywords = []
            for topic in custom_selected_topics:
                all_keywords.extend(available_topics[topic]["keywords"])
        else:
            # 自定义关键词模式
            if not custom_keywords_list:
                st.error("❌ 请至少输入一个搜索关键词！")
                st.stop()
            
            # 使用用户输入的关键词
            all_keywords = custom_keywords_list
            discipline_config = DISCIPLINES[custom_discipline]
        
        # 构建搜索查询（用 OR 连接所有关键词）
        keyword_query = " OR ".join([f'"{kw}"' if " " in kw else kw for kw in all_keywords])
        
        # 根据学科构建 arXiv 分类查询
        category_query = " OR ".join([f"cat:{cat}" for cat in discipline_config["arxiv_categories"]])
        full_query = f"({category_query}) AND ({keyword_query})"
        
        # 配置 arXiv 客户端
        client = arxiv.Client(page_size=10, delay_seconds=3, num_retries=5)
        search = arxiv.Search(
            query=full_query,
            max_results=custom_max_results,
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
                
                if time_diff > custom_days_range:
                    continue
                
                filtered_count += 1
                
                # 判断相关性
                if search_mode == "📋 从预设领域选择":
                    # 使用原有的相关性判断
                    is_related, related_topics = is_relevant_with_tags(result.title, result.summary, custom_selected_topics)
                else:
                    # 自定义关键词模式：只要检索到就认为相关
                    is_related = True
                    related_topics = [f"匹配关键词: {', '.join(all_keywords[:3])}"]
                
                if is_related:
                    # 生成中文摘要
                    summary_cn = generate_summary(result.title, result.summary)
                    
                    relevant_papers.append({
                        'title': result.title,
                        'pdf_url': result.pdf_url,
                        'published': result.published,
                        'summary': summary_cn,
                        'summary_en': result.summary,
                        'related_topics': related_topics
                    })
                
                time.sleep(0.5)
            
            progress_bar.empty()
            status_text.empty()
            
            # 显示结果
            st.success(f"✅ 搜索完成！共检查 {count} 篇论文，{filtered_count} 篇在时间范围内，找到 {len(relevant_papers)} 篇相关论文。")
            
            if relevant_papers:
                # AI 精选：判断与用户研究领域的相关性
                user_field = st.session_state.get('user_research_field', '')
                user_relevant_papers = []
                
                if user_field:
                    for paper in relevant_papers:
                        is_user_relevant, relevance_score, relevance_point = ai_filter_for_user(
                            paper['title'], 
                            paper['summary_en'], 
                            user_field
                        )
                        if is_user_relevant:
                            paper['user_relevant'] = True
                            paper['relevance_score'] = relevance_score
                            paper['relevance_point'] = relevance_point
                            user_relevant_papers.append(paper)
                
                if user_relevant_papers:
                    st.success(f"🎯 其中 **{len(user_relevant_papers)}** 篇与您的研究领域高度相关")
                
                st.markdown("---")
                
                # 如果有精选论文，优先显示
                if user_relevant_papers:
                    st.subheader(f"🎯 为您精选 ({len(user_relevant_papers)} 篇)")
                    st.caption("AI 识别出与您研究领域高度相关的论文")
                    
                    for i, paper in enumerate(user_relevant_papers, 1):
                        with st.expander(f"⭐ **{i}. {paper['title']}**", expanded=(i==1)):
                            # 显示相关度评分和关联要点
                            if paper.get('relevance_score'):
                                st.markdown(f"**🎯 相关度评分：** {paper['relevance_score']}/10")
                            if paper.get('relevance_point'):
                                st.info(f"💡 **与您的关联：** {paper['relevance_point']}")
                            
                            st.markdown(f"**📅 发布时间：** {paper['published'].strftime('%Y-%m-%d')}")
                            
                            # 显示 AI 判定的相关方向标签
                            if paper.get('related_topics'):
                                tags_html = " ".join([f"<span style='background-color: #e8f4f8; padding: 4px 12px; border-radius: 12px; margin-right: 8px; font-size: 14px;'>🏷️ {topic}</span>" for topic in paper['related_topics']])
                                st.markdown(f" {tags_html}", unsafe_allow_html=True)
                            
                            st.markdown(f"**🔗 PDF 链接：** [{paper['pdf_url']}]({paper['pdf_url']})")
                            st.markdown("**📝 AI 生成摘要（中文）：**")
                            st.info(paper['summary'])
                            
                            # 显示完整英文摘要
                            st.markdown("**📄 完整摘要（英文）：**")
                            with st.expander("展开查看完整摘要"):
                                st.caption(paper.get('summary_en', ''))
                    
                    st.divider()
                
                st.header(f"📚 找到 {len(relevant_papers)} 篇相关论文")
                
                for i, paper in enumerate(relevant_papers, 1):
                    # 如果论文已在精选中显示，添加标记
                    title_prefix = "⭐ " if paper.get('user_relevant') else ""
                    with st.expander(f"{title_prefix}**{i}. {paper['title']}**", expanded=(i==1 and not user_relevant_papers)):
                        st.markdown(f"**📅 发布时间：** {paper['published'].strftime('%Y-%m-%d')}")
                        
                        # 显示 AI 判定的相关方向标签
                        if paper.get('related_topics'):
                            tags_html = " ".join([f"<span style='background-color: #e8f4f8; padding: 4px 12px; border-radius: 12px; margin-right: 8px; font-size: 14px;'>🏷️ {topic}</span>" for topic in paper['related_topics']])
                            st.markdown(f" {tags_html}", unsafe_allow_html=True)
                        
                        st.markdown(f"**🔗 PDF 链接：** [{paper['pdf_url']}]({paper['pdf_url']})")
                        st.markdown("**📝 AI 生成摘要（中文）：**")
                        st.info(paper['summary'])
                        
                        # 显示完整英文摘要
                        st.markdown("**📄 完整摘要（英文）：**")
                        with st.expander("展开查看完整摘要"):
                            st.caption(paper.get('summary_en', ''))
            else:
                st.warning("未找到相关论文。")
        
        except Exception as e:
            st.error(f"❌ 搜索出错：{e}")
            st.info("**可能的解决方案：**\n1. 检查网络连接\n2. 检查 DeepSeek API Key 是否有效\n3. 稍后重试")
    else:
        # 显示当前设置
        if search_mode == "📋 从预设领域选择":
            if custom_selected_topics:
                topics_display = "、".join(custom_selected_topics)
                st.info(f"👆 点击上方按钮开始搜索{custom_discipline}论文\n\n**当前设置：**\n- 学科领域：{DISCIPLINES[custom_discipline]['icon']} {custom_discipline}\n- 研究方向：{topics_display}\n- 时间范围：过去 **{custom_days_range}** 天\n- 最多检索：**{custom_max_results}** 篇")
            else:
                st.warning("⚠️ 请选择至少一个研究方向")
        else:
            if custom_keywords_list:
                keywords_display = "、".join(custom_keywords_list[:5]) + ("..." if len(custom_keywords_list) > 5 else "")
                st.info(f"👆 点击上方按钮开始搜索\n\n**当前设置：**\n- 学科分类：{DISCIPLINES[custom_discipline]['icon']} {custom_discipline}\n- 搜索关键词：{keywords_display}\n- 关键词数量：**{len(custom_keywords_list)}** 个\n- 时间范围：过去 **{custom_days_range}** 天\n- 最多检索：**{custom_max_results}** 篇")
            else:
                st.warning("⚠️ 请至少输入一个搜索关键词")
